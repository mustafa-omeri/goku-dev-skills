#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for check_db_migrations.py gate script."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# musgoku/scripts dizinini sys.path'e ekle
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parents[4]
SCRIPTS_DIR = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import check_db_migrations


class TestCheckDbMigrations(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_db_migrations_"))
        self.orig_env = os.environ.get("AGENTS_PROJECT_ROOT")
        os.environ["AGENTS_PROJECT_ROOT"] = str(self.tmp_dir)

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["AGENTS_PROJECT_ROOT"] = self.orig_env
        else:
            os.environ.pop("AGENTS_PROJECT_ROOT", None)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_out_of_scope_when_no_db_assets(self):
        """Frontend veya düz projede kapsam dışı dönmeli (exit 0)."""
        ret = check_db_migrations.main(["--json"])
        self.assertEqual(ret, 0)

    def test_fails_when_entity_exists_but_no_db_migrations_file(self):
        """Entity varken DB_MIGRATIONS.md yoksa E1 hatası dönmeli (exit 1)."""
        entity_file = self.tmp_dir / "src" / "main" / "java" / "com" / "example" / "User.java"
        entity_file.parent.mkdir(parents=True, exist_ok=True)
        entity_file.write_text("@Entity\npublic class User { private Long id; }", encoding="utf-8")

        ret = check_db_migrations.main(["--json"])
        self.assertEqual(ret, 1)

    def test_fails_when_db_migrations_file_is_empty(self):
        """DB_MIGRATIONS.md boşsa E3 hatası dönmeli."""
        entity_file = self.tmp_dir / "src" / "main" / "java" / "com" / "example" / "User.java"
        entity_file.parent.mkdir(parents=True, exist_ok=True)
        entity_file.write_text("@Entity\npublic class User { private Long id; }", encoding="utf-8")

        doc_file = self.tmp_dir / "DB_MIGRATIONS.md"
        doc_file.write_text("# DB\nToo short", encoding="utf-8")

        ret = check_db_migrations.main(["--json"])
        self.assertEqual(ret, 1)

    def test_fails_when_migration_script_not_documented(self):
        """Migration SQL dosyası diskte var ama dokümanda geçmiyorsa E2 hatası dönmeli."""
        mig_dir = self.tmp_dir / "src" / "main" / "resources" / "db" / "migration"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1__init_schema.sql").write_text("CREATE TABLE test (id INT);", encoding="utf-8")

        doc_file = self.tmp_dir / "DB_MIGRATIONS.md"
        doc_file.write_text(
            "# DB_MIGRATIONS.md\n\n"
            "## 1. Özet\nSon Revizyon: REV-1\n\n"
            "## 2. Revizyon Geçmişi\n\n"
            "### [REV-20261016-01] Init\n"
            "- Tarih: 2026-10-16\n"
            "Farklı bir metin var ama aranan sql migration dosyası kesinlikle yok.\n",
            encoding="utf-8"
        )

        ret = check_db_migrations.main(["--json"])
        self.assertEqual(ret, 1)

    def test_passes_when_migration_and_entity_properly_documented(self):
        """Her şey kurallara uygun belgelendiğinde exit 0 dönmeli."""
        entity_file = self.tmp_dir / "src" / "main" / "java" / "com" / "example" / "User.java"
        entity_file.parent.mkdir(parents=True, exist_ok=True)
        entity_file.write_text("@Entity\n@Table(name='users')\npublic class User { private Long id; }", encoding="utf-8")

        mig_dir = self.tmp_dir / "src" / "main" / "resources" / "db" / "migration"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1__init_schema.sql").write_text("CREATE TABLE users (id INT PRIMARY KEY);", encoding="utf-8")

        doc_file = self.tmp_dir / "DB_MIGRATIONS.md"
        doc_file.write_text(
            "# DB_MIGRATIONS.md\n\n"
            "## 1. Proje Veritabanı Özeti\n"
            "- Motor: MySQL\n"
            "- Son Revizyon: REV-20261016-01\n\n"
            "## 2. Revizyon Geçmişi\n\n"
            "### [REV-20261016-01] Kullanıcı Tablosu Oluşturuldu\n"
            "- Tarih: 2026-10-16\n"
            "- İşlem Türü: CREATE_TABLE\n"
            "- İlgili Tablo: users\n"
            "- Etkilenen Entity: User\n"
            "- Migration Dosyası: V1__init_schema.sql\n\n"
            "#### Değişiklik Detay Tablosu\n"
            "| Tablo | Kolon | İşlem | Eski | Yeni | Null | Def | Açıklama |\n"
            "| users | id | ADD | - | INT | Hayır | - | PK |\n\n"
            "#### Rollback Planı\n"
            "```sql\nDROP TABLE users;\n```\n",
            encoding="utf-8"
        )

        ret = check_db_migrations.main(["--json"])
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
