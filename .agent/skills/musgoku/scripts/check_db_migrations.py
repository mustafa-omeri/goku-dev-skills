#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veritabanı migration ve revizyon kapısı — şema/entity var, DB_MIGRATIONS.md yok/eksik.

Neden var?
----------
`db-migration-enforcement.md` kuralı, veritabanı revizyonlarında (yeni tablo, kolon,
indeks, entity değişikliği, migration scripti) `DB_MIGRATIONS.md` dosyasının
güncel tutulmasını zorunlu kılar. Bu kapı scripti, kuralın ölçülebilirliğini sağlar:
projede veritabanı varlığı veya migration dosyası varsa `DB_MIGRATIONS.md` dosyasının
varlığını, doluluğunu ve diskteki migration scriptlerinin belgelenip belgelenmediğini
otomatik denetler.

Kontroller
----------
E1 zorunlu dosya eksik      DB_MIGRATIONS.md (veya docs/database/DB_MIGRATIONS.md) yok
E2 migration belgelenmemiş  disk üzerindeki migration scripti DB_MIGRATIONS.md içinde yok
E3 boş veya geçersiz içerik DB_MIGRATIONS.md boş veya revizyon/tablo kaydı içermiyor
W1 entity belgelenmemiş     @Entity sınıfı var ama DB_MIGRATIONS.md içinde anılmamış

E1-E3 hata (exit 1) · W1 uyari · exit 2 = araç hatası.
Veritabanı varlığı bulunamayan projelerde (frontend-only vb.) kapsam dışı: exit 0.

Kullanım
--------
    python .agent/skills/musgoku/scripts/check_db_migrations.py
    python .agent/skills/musgoku/scripts/check_db_migrations.py --json
    python .agent/skills/musgoku/scripts/check_db_migrations.py --strict

Ortam
-----
AGENTS_PROJECT_ROOT   proje kökünü elle verir (yoksa script konumundan aranır)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IGNORE_DIRS = {
    ".git", ".idea", ".vscode", "node_modules", "target", "build", "dist",
    "out", ".pytest_cache", "__pycache__", "yedekler", ".agent"
}

ENTITY_RE = re.compile(r"@(?:Entity|Table)\b")
REVISION_HEADER_RE = re.compile(r"^###\s+\[?(?:REV|V\d)[\w.-]+\]?", re.MULTILINE | re.IGNORECASE)


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


def locate_db_migrations_file(project_root: Path) -> Path | None:
    candidates = [
        project_root / "DB_MIGRATIONS.md",
        project_root / "docs" / "database" / "DB_MIGRATIONS.md",
        project_root / "docs" / "DB_MIGRATIONS.md",
        project_root / "database" / "DB_MIGRATIONS.md",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def collect_migration_files(project_root: Path) -> list[Path]:
    """Projedeki bilinen migration scriptlerini bulur (Flyway, Liquibase, Prisma vb.)."""
    migration_files: list[Path] = []
    search_dirs = [
        project_root / "src" / "main" / "resources" / "db" / "migration",
        project_root / "src" / "main" / "resources" / "db" / "changelog",
        project_root / "migrations",
        project_root / "prisma" / "migrations",
        project_root / "db" / "migrations",
    ]
    for d in search_dirs:
        if d.is_dir():
            for p in d.rglob("*"):
                if p.is_file() and p.suffix.lower() in {".sql", ".xml", ".yaml", ".yml"}:
                    migration_files.append(p)
    return sorted(migration_files)


def scan_entities(project_root: Path) -> list[str]:
    """Java/@Entity sınıflarını veya Prisma modellerini arar."""
    entities: list[str] = []
    # Java entity arama
    for java_file in project_root.rglob("*.java"):
        if any(part in IGNORE_DIRS for part in java_file.parts):
            continue
        try:
            content = java_file.read_text(encoding="utf-8", errors="ignore")
            if ENTITY_RE.search(content):
                entities.append(java_file.stem)
        except Exception:
            continue

    # Prisma schema arama
    for prisma_file in project_root.rglob("*.prisma"):
        if any(part in IGNORE_DIRS for part in prisma_file.parts):
            continue
        try:
            content = prisma_file.read_text(encoding="utf-8", errors="ignore")
            for match in re.finditer(r"\bmodel\s+(\w+)\b", content):
                entities.append(match.group(1))
        except Exception:
            continue

    return sorted(set(entities))


def check_db_scope(project_root: Path, migration_files: list[Path], entities: list[str]) -> bool:
    """Projede veritabanı veya migration ihtiyacı olup olmadığını tespit eder."""
    if migration_files or entities:
        return True

    # pom.xml içinde jpa/hibernate/flyway/liquibase kontrolü
    pom = project_root / "pom.xml"
    if pom.is_file():
        try:
            text = pom.read_text(encoding="utf-8", errors="ignore")
            if any(k in text for k in ("spring-boot-starter-data-jpa", "flyway", "liquibase", "hibernate")):
                return True
        except Exception:
            pass

    return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Veritabanı migration ve revizyon kapısı")
    parser.add_argument("--json", action="store_true", help="Makinece okunabilir JSON çıktısı")
    parser.add_argument("--strict", action="store_true", help="Uyarıları da hata say")
    args = parser.parse_args(argv)

    project_root = find_project_root()
    migration_files = collect_migration_files(project_root)
    entities = scan_entities(project_root)

    is_db_project = check_db_scope(project_root, migration_files, entities)
    if not is_db_project:
        if args.json:
            print(json.dumps({
                "scope": "out_of_scope",
                "errors": [],
                "warnings": [],
                "status": "OK",
                "exit": 0
            }, ensure_ascii=False, indent=2))
        else:
            print("Veritabanı varlığı veya entity bulunamadı — kural bu projede kapsam dışı")
            print("\nSONUÇ: 0 migration · [OK]")
        return 0

    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    doc_path = locate_db_migrations_file(project_root)
    if not doc_path:
        errors.append(("E1", "DB_MIGRATIONS.md dosyası bulunamadı. Veritabanı şeması veya entity barındıran projelerde DB_MIGRATIONS.md zorunludur."))
    else:
        try:
            doc_content = doc_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            print(f"[ARAÇ HATASI] {doc_path} okunamadı: {exc}", file=sys.stderr)
            return 2

        if len(doc_content.strip()) < 80:
            errors.append(("E3", f"{doc_path.name} dosyası boş veya yetersiz içerik barındırıyor."))
        else:
            # Migration dosyaları diskte var ama dokümanda geçiyor mu?
            for mf in migration_files:
                if mf.name not in doc_content:
                    errors.append(("E2", f"Migration dosyası {doc_path.name} içinde belgelenmemiş: {mf.name}"))

            # Entity'ler var ama dokümanda anılmış mı?
            if entities:
                missing_entities = [e for e in entities if e.lower() not in doc_content.lower()]
                if len(missing_entities) == len(entities):
                    warnings.append(("W1", f"Projede {len(entities)} entity tespit edildi ancak {doc_path.name} içinde hiçbir entity adı geçmiyor."))

            # En az bir revizyon kaydı veya tablo formatı var mı?
            if not REVISION_HEADER_RE.search(doc_content) and "REV-" not in doc_content:
                warnings.append(("W2", f"{doc_path.name} içinde standart revizyon başlığı (### [REV-...] veya ### [V...]) bulunamadı."))

    if args.json:
        out = {
            "scope": "in_scope",
            "document": str(doc_path.relative_to(project_root)) if doc_path else None,
            "migrations_count": len(migration_files),
            "entities_count": len(entities),
            "errors": [{"code": c, "message": m} for c, m in errors],
            "warnings": [{"code": c, "message": m} for c, m in warnings],
            "exit": 1 if errors or (args.strict and warnings) else 0
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return out["exit"]

    # Düz metin çıktısı
    print(f"Veritabanı kapsamı: {len(migration_files)} migration dosyası, {len(entities)} entity sınıfı")
    if doc_path:
        print(f"Dokümantasyon: {doc_path.relative_to(project_root)}")

    for code, msg in errors:
        print(f"[HATA] {code}: {msg}")
    for code, msg in warnings:
        print(f"[UYARI] {code}: {msg}")

    failed = bool(errors) or (args.strict and bool(warnings))
    if failed:
        print(f"\nSONUÇ: {len(errors)} hata · {len(warnings)} uyarı · kapı geçersiz")
        return 1

    print(f"\nSONUÇ: {len(migration_files)} migration · {len(entities)} entity · [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
