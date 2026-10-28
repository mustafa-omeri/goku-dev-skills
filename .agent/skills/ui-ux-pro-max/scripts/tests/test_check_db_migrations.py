#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for check_db_migrations.py gate script."""

import json
import os
import shutil
import subprocess
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

    def test_supabase_project_detected_and_verified(self):
        """Supabase migrations dizini ve package.json bağımlılığı evrensel olarak tespit edilmeli."""
        pkg = self.tmp_dir / "package.json"
        pkg.write_text('{"name": "test-app", "dependencies": {"@supabase/supabase-js": "^2.39.0"}}', encoding="utf-8")

        mig_dir = self.tmp_dir / "supabase" / "migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "20261020_001_create_items.sql").write_text("CREATE TABLE items (id uuid primary key);", encoding="utf-8")

        # Önce dokümansızken hata vermeli (E1)
        ret_fail = check_db_migrations.main(["--json"])
        self.assertEqual(ret_fail, 1)

        # Doküman eklendiğinde ve migration belgelendiğinde geçmeli
        doc_file = self.tmp_dir / "docs" / "database" / "DB_MIGRATIONS.md"
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        doc_file.write_text(
            "# DB_MIGRATIONS.md\n\n"
            "## 1. Proje Veritabanı Özeti\n"
            "- Motor: Supabase PostgreSQL\n\n"
            "## 2. Revizyon Geçmişi\n\n"
            "### [REV-20261020-01] Items Tablosu\n"
            "- Migration Dosyası: supabase/migrations/20261020_001_create_items.sql\n"
            "| Tablo | Kolon | İşlem |\n| items | id | ADD |\n",
            encoding="utf-8"
        )

        ret_ok = check_db_migrations.main(["--json"])
        self.assertEqual(ret_ok, 0)

    def test_drizzle_and_python_alembic_detected(self):
        """Drizzle ve Python/Alembic projeleri otomatik algılanmalı."""
        # Drizzle config
        (self.tmp_dir / "drizzle.config.ts").write_text("export default {};", encoding="utf-8")
        ret_drizzle = check_db_migrations.main(["--json"])
        self.assertEqual(ret_drizzle, 1)  # DB_MIGRATIONS.md yok diye E1 vermeli

        # Drizzle sil, Python requirements dene
        (self.tmp_dir / "drizzle.config.ts").unlink()
        (self.tmp_dir / "requirements.txt").write_text("alembic==1.13.0\npsycopg2-binary==2.9.9", encoding="utf-8")
        ret_python = check_db_migrations.main(["--json"])
        self.assertEqual(ret_python, 1)

    def test_baseline_declaration_allows_legacy_migrations(self):
        """Baseline bildirimi yapıldığında eski migration'lar hata vermemeli (W3 uyarısı vermeli)."""
        mig_dir = self.tmp_dir / "supabase" / "migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "001_initial.sql").write_text("CREATE TABLE t1 (id int);", encoding="utf-8")
        (mig_dir / "002_profiles.sql").write_text("CREATE TABLE t2 (id int);", encoding="utf-8")
        (mig_dir / "049_new_feature.sql").write_text("CREATE TABLE t49 (id int);", encoding="utf-8")

        doc_file = self.tmp_dir / "DB_MIGRATIONS.md"
        doc_file.write_text(
            "# DB_MIGRATIONS.md\n\n"
            "## 1. Proje Veritabanı Özeti\n"
            "- Motor: PostgreSQL\n"
            "- Başlangıç / Baseline: 001..048 başlangıç şeması\n"
            "- Son Revizyon: REV-20261020-01\n\n"
            "## 2. Revizyon Geçmişi\n\n"
            "### [REV-20261020-01] New Feature\n"
            "- Migration Dosyası: 049_new_feature.sql\n"
            "| Tablo | Kolon | İşlem |\n| t49 | id | ADD |\n",
            encoding="utf-8"
        )

        ret = check_db_migrations.main(["--json"])
        self.assertEqual(ret, 0)  # Baseline olduğu için exit 0 olmalı

    def test_git_working_tree_e4_guard(self):
        """Git çalışma ağacında SQL değiştirilip DB_MIGRATIONS.md ellenmediğinde E4 vermelidir."""
        # Git deposu oluştur
        subprocess.run(["git", "init"], cwd=str(self.tmp_dir), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=str(self.tmp_dir), check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(self.tmp_dir), check=True)

        doc_file = self.tmp_dir / "DB_MIGRATIONS.md"
        doc_file.write_text(
            "# DB_MIGRATIONS.md\n\n"
            "## 1. Proje Veritabanı Özeti\n"
            "- Motor: MySQL\n"
            "### [REV-20261016-01] Initial\n"
            "- Migration: V1__init.sql\n"
            "| Tablo | Kolon | İşlem |\n| a | b | c |\n",
            encoding="utf-8"
        )
        mig_dir = self.tmp_dir / "migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1__init.sql").write_text("CREATE TABLE a (b INT);", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=str(self.tmp_dir), check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=str(self.tmp_dir), check=True)

        # Şimdi yeni bir migration ekle ama DB_MIGRATIONS.md'ye dokunma
        (mig_dir / "V2__add_status.sql").write_text("ALTER TABLE a ADD COLUMN status VARCHAR;", encoding="utf-8")

        ret = check_db_migrations.main(["--json"])
        self.assertEqual(ret, 1)  # E4 ve E2 nedeniyle hata vermeli


    def test_git_working_tree_e5_project_brief_dual_mapping_guard(self):
        """Git çalışma ağacında SQL eklenip DB_MIGRATIONS.md güncellense bile PROJECT_BRIEF.md ellenmediğinde E5 vermelidir."""
        subprocess.run(["git", "init"], cwd=str(self.tmp_dir), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=str(self.tmp_dir), check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(self.tmp_dir), check=True)

        brief_file = self.tmp_dir / "PROJECT_BRIEF.md"
        brief_file.write_text(
            "---\ntitle: Test Brief\ntype: project-brief\nproject: test\nstatus: active\n"
            "created: 2026-10-28\nupdated: 2026-10-28\nprimary_language: Python\n"
            "frameworks: []\ndatabase: [MySQL]\n---\n# Test Brief\n",
            encoding="utf-8"
        )

        doc_file = self.tmp_dir / "DB_MIGRATIONS.md"
        doc_file.write_text(
            "# DB_MIGRATIONS.md\n\n## 1. Proje Veritabanı Özeti\n- Motor: MySQL\n"
            "### [REV-20261016-01] Initial\n- Migration: V1__init.sql\n| Tablo | Kolon | İşlem |\n| a | b | c |\n",
            encoding="utf-8"
        )
        mig_dir = self.tmp_dir / "migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1__init.sql").write_text("CREATE TABLE a (b INT);", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=str(self.tmp_dir), check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=str(self.tmp_dir), check=True)

        # Yeni migration ekle ve DB_MIGRATIONS.md'ye yaz (E4 çözüldü, E2 çözüldü)
        (mig_dir / "V2__add_status.sql").write_text("ALTER TABLE a ADD COLUMN status VARCHAR;", encoding="utf-8")
        doc_file.write_text(
            "# DB_MIGRATIONS.md\n\n## 1. Proje Veritabanı Özeti\n- Motor: MySQL\n"
            "### [REV-20261016-02] Add Status\n- Migration Dosyası: V2__add_status.sql\n| Tablo | Kolon | İşlem |\n| a | status | ADD |\n"
            "### [REV-20261016-01] Initial\n- Migration: V1__init.sql\n| Tablo | Kolon | İşlem |\n| a | b | c |\n",
            encoding="utf-8"
        )

        # PROJECT_BRIEF.md güncellenmedi! E5 vermeli
        ret_fail = check_db_migrations.main(["--json"])
        self.assertEqual(ret_fail, 1)

        # Şimdi PROJECT_BRIEF.md'yi de güncelle (İkili Eşleme / Dual Mapping sağlandı)
        brief_file.write_text(
            "---\ntitle: Test Brief\ntype: project-brief\nproject: test\nstatus: active\n"
            "created: 2026-10-28\nupdated: 2026-10-28\nprimary_language: Python\n"
            "frameworks: []\ndatabase: [MySQL, 'v2 status']\n---\n# Test Brief (Updated)\n",
            encoding="utf-8"
        )
        ret_pass = check_db_migrations.main(["--json"])
        self.assertEqual(ret_pass, 0)


if __name__ == "__main__":
    unittest.main()
