#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evrensel veritabanı migration ve revizyon kapısı.

Neden var?
----------
`db-migration-enforcement.md` kuralı, veritabanı revizyonlarında (yeni tablo, kolon,
indeks, entity/model değişikliği, migration scripti) `DB_MIGRATIONS.md` dosyasının
güncel tutulmasını zorunlu kılar.

Bu kapı scripti, çok dilli ve çok yığınlı (multi-ecosystem) evrensel mimariye sahiptir:
1. Ekosistem Tespiti (manifest ve bağımlılık taraması):
   - Node.js / TS (Supabase, Prisma, Drizzle, TypeORM, Sequelize, Mongoose, pg, mysql2 vb.)
   - Java / Kotlin (Spring Data JPA, Hibernate, Flyway, Liquibase, R2DBC vb.)
   - Python (SQLAlchemy, Alembic, Django ORM, Tortoise-ORM, Beanie, Peewee vb.)
   - Go (GORM, sqlx, golang-migrate, Ent, Bun)
   - Rust (Diesel, SQLx, SeaORM)
   - .NET (EF Core, Dapper, FluentMigrator)
2. Evrensel Migration Dizin Tespiti:
   - supabase/migrations, prisma/migrations, drizzle, alembic/versions, hasura/migrations
   - db/migrations, database/migrations, migrations, src/main/resources/db/migration
3. Dinamik Git Çalışma Ağacı Koruması (E4):
   - Git çalışma ağacında (staged / unstaged) veritabanı/migration/şema dosyası
     değiştirilmişse, DB_MIGRATIONS.md dosyasının da aynı oturumda güncellendiğini
     matematiksel olarak zorunlu kılar.
4. Brownfield / Legacy Desteği:
   - Kural öncesi geçmiş (legacy) migration'lar için baseline desteği.

Kontroller
----------
E1 zorunlu dosya eksik      DB_MIGRATIONS.md (veya docs/database/DB_MIGRATIONS.md) yok
E2 migration belgelenmemiş  disk üzerindeki migration scripti DB_MIGRATIONS.md içinde yok
E3 boş veya yetersiz içerik DB_MIGRATIONS.md boş veya revizyon/tablo kaydı içermiyor
E4 git diff eşzamansızlığı  git çalışma ağacında DB/migration değişti ama DB_MIGRATIONS.md güncellenmedi
W1 entity belgelenmemiş     Entity/Model sınıfı var ama DB_MIGRATIONS.md içinde anılmamış
W2 standart başlık eksik    Standart revizyon başlığı (### [REV-...] veya ### [V...]) bulunamadı
W3 legacy migration uyarısı Eski migration'lar baseline olarak belirtilmemiş
W4 çoklu dosya uyarısı      Birden fazla DB_MIGRATIONS.md tespit edildi

E1-E4 hata (exit 1) · W1-W4 uyarı · exit 2 = araç hatası.
Veritabanı varlığı bulunamayan projelerde (frontend-only vb.) kapsam dışı: exit 0.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IGNORE_DIRS = {
    ".git", ".idea", ".vscode", "node_modules", "target", "build", "dist",
    "out", ".pytest_cache", "__pycache__", "yedekler", ".agent", ".next",
    ".nuxt", ".output", "coverage", ".turbo"
}

# Regex kalıpları
JAVA_ENTITY_RE = re.compile(r"@(?:Entity|Table|Document|Node)\b")
PRISMA_MODEL_RE = re.compile(r"\bmodel\s+(\w+)\b")
TYPEORM_ENTITY_RE = re.compile(r"@(?:Entity|EntityRepository)\b")
DRIZZLE_TABLE_RE = re.compile(r"\b(?:pgTable|mysqlTable|sqliteTable)\s*\(\s*['\"](\w+)['\"]")
PYTHON_MODEL_RE = re.compile(r"class\s+(\w+)\s*\((?:models\.Model|Base|SQLModel|Document|db\.Model)\):")
CSHARP_ENTITY_RE = re.compile(r"(?:public\s+DbSet<(\w+)>|class\s+(\w+)\s*:\s*(?:DbContext|BaseEntity))")
GO_STRUCT_DB_RE = re.compile(r"type\s+(\w+)\s+struct\s+\{.*gorm:", re.DOTALL)
REVISION_HEADER_RE = re.compile(r"^###\s+\[?(?:REV|V\d)[\w.-]+\]?", re.MULTILINE | re.IGNORECASE)

# Bilinen migration dizin göreli yolları
KNOWN_MIGRATION_DIRS = [
    ("src", "main", "resources", "db", "migration"),
    ("src", "main", "resources", "db", "changelog"),
    ("supabase", "migrations"),
    ("prisma", "migrations"),
    ("drizzle", "migrations"),
    ("drizzle",),
    ("alembic", "versions"),
    ("hasura", "migrations"),
    ("db", "migrations"),
    ("db", "migration"),
    ("database", "migrations"),
    ("database", "migration"),
    ("migrations",),
    ("migration",),
    ("sql", "migrations"),
]

# Bağımlılık paket anahtar kelimeleri
NODE_DB_PACKAGES = {
    "@supabase/supabase-js", "@supabase/ssr", "firebase", "firebase-admin",
    "appwrite", "pocketbase", "prisma", "@prisma/client", "drizzle-orm",
    "typeorm", "sequelize", "knex", "kysely", "mikro-orm", "@mikro-orm/core",
    "mongoose", "pg", "pg-promise", "mysql", "mysql2", "mariadb", "sqlite3",
    "better-sqlite3", "oracledb", "tedious", "mongodb", "@libsql/client",
    "db-migrate", "node-pg-migrate", "drizzle-kit", "umzug"
}

JVM_DB_PACKAGES = {
    "spring-boot-starter-data-jpa", "spring-boot-starter-data-mongodb",
    "spring-boot-starter-data-r2dbc", "hibernate", "flyway", "liquibase",
    "mybatis", "jooq", "mysql-connector", "postgresql", "ojdbc", "h2"
}

PYTHON_DB_PACKAGES = {
    "sqlalchemy", "alembic", "django", "tortoise-orm", "peewee", "beanie",
    "motor", "pymongo", "sqlmodel", "psycopg2", "psycopg", "asyncpg",
    "pymysql", "mysqlclient", "aiosqlite"
}

GO_DB_PACKAGES = {
    "gorm.io", "github.com/jmoiron/sqlx", "github.com/golang-migrate/migrate",
    "entgo.io/ent", "github.com/uptrace/bun"
}

RUST_DB_PACKAGES = {
    "diesel", "sqlx", "sea-orm", "rusqlite", "tokio-postgres"
}

DOTNET_DB_PACKAGES = {
    "Microsoft.EntityFrameworkCore", "Dapper", "FluentMigrator", "Npgsql",
    "System.Data.SqlClient"
}


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


def locate_db_migrations_files(project_root: Path) -> tuple[Path | None, list[Path]]:
    candidates = [
        project_root / "DB_MIGRATIONS.md",
        project_root / "docs" / "database" / "DB_MIGRATIONS.md",
        project_root / "docs" / "DB_MIGRATIONS.md",
        project_root / "database" / "DB_MIGRATIONS.md",
    ]
    existing = [c for c in candidates if c.is_file()]
    if not existing:
        return None, []
    if len(existing) == 1:
        return existing[0], existing
    # Birden fazla varsa en son değiştirileni (en güncelini) seç
    best = max(existing, key=lambda p: (p.stat().st_mtime, p.stat().st_size))
    return best, existing


def collect_migration_files(project_root: Path) -> list[Path]:
    """Projedeki bilinen tüm migration scriptlerini bulur (Supabase, Flyway, Prisma, Drizzle, Alembic vb.)."""
    migration_files: list[Path] = []
    seen_paths: set[Path] = set()

    for parts in KNOWN_MIGRATION_DIRS:
        target_dir = project_root.joinpath(*parts)
        if target_dir.is_dir():
            for p in target_dir.rglob("*"):
                if p.is_file() and p.suffix.lower() in {".sql", ".xml", ".yaml", ".yml", ".prisma", ".py"}:
                    if p.name.startswith("__"):
                        continue
                    if p not in seen_paths:
                        seen_paths.add(p)
                        migration_files.append(p)

    return sorted(migration_files)


def scan_entities_fast(project_root: Path) -> list[str]:
    """os.walk ile node_modules ve build dizinlerini atlayarak hızlı entity/model taraması yapar."""
    entities: list[str] = []

    for root, dirs, files in os.walk(str(project_root)):
        # IGNORE_DIRS altındaki dizinlere inmeyi kes
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        root_path = Path(root)
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in {".java", ".prisma", ".ts", ".py", ".cs"}:
                continue
            if fname.endswith(".d.ts"):
                continue

            fpath = root_path / fname
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if ext == ".java" and JAVA_ENTITY_RE.search(content):
                entities.append(fpath.stem)
            elif ext == ".prisma":
                for m in PRISMA_MODEL_RE.finditer(content):
                    entities.append(m.group(1))
            elif ext == ".ts":
                if TYPEORM_ENTITY_RE.search(content):
                    entities.append(fpath.stem)
                for m in DRIZZLE_TABLE_RE.finditer(content):
                    entities.append(m.group(1))
            elif ext == ".py":
                for m in PYTHON_MODEL_RE.finditer(content):
                    entities.append(m.group(1))
            elif ext == ".cs":
                for m in CSHARP_ENTITY_RE.finditer(content):
                    entities.append(m.group(1) or m.group(2))

    return sorted(set(e for e in entities if e))


def check_db_scope(project_root: Path, migration_files: list[Path], entities: list[str]) -> tuple[bool, str]:
    """Projede veritabanı veya migration ihtiyacı olup olmadığını çok dilli ekosistemde tespit eder."""
    if migration_files:
        return True, f"{len(migration_files)} adet migration dosyası tespit edildi"

    if entities:
        return True, f"{len(entities)} adet entity/model tanımı tespit edildi"

    # Standalone DB / BaaS config dosyaları
    config_indicators = [
        (project_root / "supabase" / "config.toml", "Supabase projesi"),
        (project_root / "alembic.ini", "Alembic migration konfigürasyonu"),
        (project_root / "flyway.conf", "Flyway konfigürasyonu"),
        (project_root / "drizzle.config.ts", "Drizzle ORM konfigürasyonu"),
        (project_root / "drizzle.config.js", "Drizzle ORM konfigürasyonu"),
        (project_root / "prisma" / "schema.prisma", "Prisma şeması"),
        (project_root / "firestore.rules", "Firebase/Firestore kuralları"),
    ]
    for path, reason in config_indicators:
        if path.is_file():
            return True, reason

    # Node.js: package.json
    pkg_json = project_root / "package.json"
    if pkg_json.is_file():
        try:
            content = pkg_json.read_text(encoding="utf-8", errors="ignore")
            matched = [pkg for pkg in NODE_DB_PACKAGES if f'"{pkg}"' in content]
            if matched:
                return True, f"package.json veritabanı paketleri: {', '.join(matched[:3])}"
        except Exception:
            pass

    # Java / JVM: pom.xml, build.gradle
    pom = project_root / "pom.xml"
    if pom.is_file():
        try:
            content = pom.read_text(encoding="utf-8", errors="ignore")
            matched = [pkg for pkg in JVM_DB_PACKAGES if pkg in content]
            if matched:
                return True, f"pom.xml veritabanı bağımlılıkları: {', '.join(matched[:3])}"
        except Exception:
            pass

    for gradle_name in ("build.gradle", "build.gradle.kts"):
        gradle = project_root / gradle_name
        if gradle.is_file():
            try:
                content = gradle.read_text(encoding="utf-8", errors="ignore")
                matched = [pkg for pkg in JVM_DB_PACKAGES if pkg in content]
                if matched:
                    return True, f"{gradle_name} veritabanı bağımlılıkları: {', '.join(matched[:3])}"
            except Exception:
                pass

    # Python: requirements.txt, pyproject.toml, Pipfile
    py_files = [project_root / "requirements.txt", project_root / "pyproject.toml", project_root / "Pipfile"]
    for py_file in py_files:
        if py_file.is_file():
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore").lower()
                matched = [pkg for pkg in PYTHON_DB_PACKAGES if pkg in content]
                if matched:
                    return True, f"{py_file.name} veritabanı paketleri: {', '.join(matched[:3])}"
            except Exception:
                pass

    # Go: go.mod
    go_mod = project_root / "go.mod"
    if go_mod.is_file():
        try:
            content = go_mod.read_text(encoding="utf-8", errors="ignore")
            matched = [pkg for pkg in GO_DB_PACKAGES if pkg in content]
            if matched:
                return True, f"go.mod veritabanı modülleri: {', '.join(matched[:3])}"
        except Exception:
            pass

    # Rust: Cargo.toml
    cargo = project_root / "Cargo.toml"
    if cargo.is_file():
        try:
            content = cargo.read_text(encoding="utf-8", errors="ignore")
            matched = [pkg for pkg in RUST_DB_PACKAGES if pkg in content]
            if matched:
                return True, f"Cargo.toml veritabanı paketleri: {', '.join(matched[:3])}"
        except Exception:
            pass

    # .NET: *.csproj
    for csproj in project_root.glob("*.csproj"):
        try:
            content = csproj.read_text(encoding="utf-8", errors="ignore")
            matched = [pkg for pkg in DOTNET_DB_PACKAGES if pkg in content]
            if matched:
                return True, f"{csproj.name} veritabanı paketleri: {', '.join(matched[:3])}"
        except Exception:
            pass

    return False, "Veritabanı varlığı veya bağımlılığı bulunamadı"


def check_git_working_tree_changes(project_root: Path, doc_paths: list[Path]) -> list[str]:
    """Git çalışma ağacında DB/migration dosyası değiştiğinde DB_MIGRATIONS.md'nin de değiştiğini doğrular (E4)."""
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=False
        )
        if res.returncode != 0:
            return []
    except Exception:
        return []

    lines = res.stdout.strip().splitlines()
    if not lines:
        return []

    changed_files: list[str] = []
    doc_changed = False

    doc_rel_names = {
        "db_migrations.md",
        "docs/database/db_migrations.md",
        "docs/db_migrations.md",
        "database/db_migrations.md"
    }

    for line in lines:
        if len(line) < 4:
            continue
        file_part = line[3:].strip()
        # Yeniden adlandırma: "R  old -> new"
        if " -> " in file_part:
            file_part = file_part.split(" -> ")[1].strip()

        norm_path = file_part.replace("\\", "/").lower()

        if norm_path in doc_rel_names:
            doc_changed = True
            continue

        # DB / migration dosyası mı?
        is_migration_dir = any(
            norm_path.startswith("/".join(p).lower() + "/") or norm_path == "/".join(p).lower()
            for p in KNOWN_MIGRATION_DIRS
        )
        is_sql = norm_path.endswith((".sql", ".prisma", ".cql"))
        is_schema_or_mig = (
            is_migration_dir or
            is_sql or
            "migration" in norm_path or
            "schema" in norm_path
        )

        # .agent/, docs/, test/, yedekler gibi harici alanları filtrele
        if is_schema_or_mig:
            if not any(norm_path.startswith(d) for d in (".agent/", "yedekler/", "docs/", ".git/")):
                changed_files.append(file_part)

    # Eğer DB/migration dosyası değişmiş ama DB_MIGRATIONS.md değişmemişse E4 ihlali
    if changed_files and not doc_changed:
        return changed_files

    return []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evrensel veritabanı migration ve revizyon kapısı")
    parser.add_argument("--json", action="store_true", help="Makinece okunabilir JSON çıktısı")
    parser.add_argument("--strict", action="store_true", help="Uyarıları da hata say")
    args = parser.parse_args(argv)

    project_root = find_project_root()
    migration_files = collect_migration_files(project_root)
    entities = scan_entities_fast(project_root)

    is_db_project, scope_reason = check_db_scope(project_root, migration_files, entities)
    if not is_db_project:
        if args.json:
            print(json.dumps({
                "scope": "out_of_scope",
                "reason": scope_reason,
                "errors": [],
                "warnings": [],
                "status": "OK",
                "exit": 0
            }, ensure_ascii=False, indent=2))
        else:
            print(f"Kapsam Dışı: {scope_reason} — kural bu projede uygulanmaz")
            print("\nSONUÇ: 0 migration · [OK]")
        return 0

    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    doc_path, all_doc_paths = locate_db_migrations_files(project_root)
    if not doc_path:
        errors.append((
            "E1",
            f"DB_MIGRATIONS.md dosyası bulunamadı ({scope_reason}). "
            "Veritabanı varlığı veya bağımlılığı barındıran tüm projelerde DB_MIGRATIONS.md zorunludur."
        ))
    else:
        if len(all_doc_paths) > 1:
            warnings.append((
                "W4",
                f"Birden fazla DB_MIGRATIONS.md dosyası tespit edildi ({len(all_doc_paths)} adet). "
                f"En güncel olan '{doc_path.relative_to(project_root)}' esas alındı. Lütfen tek konuma indirgeyin."
            ))

        try:
            # Birden fazla dosya varsa tüm içerikleri birleştirerek geriye dönük arama yap
            combined_content = "\n".join(
                p.read_text(encoding="utf-8", errors="replace") for p in all_doc_paths
            )
            doc_content = doc_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            print(f"[ARAÇ HATASI] {doc_path} okunamadı: {exc}", file=sys.stderr)
            return 2

        if len(doc_content.strip()) < 80:
            errors.append(("E3", f"{doc_path.name} dosyası boş veya yetersiz içerik barındırıyor."))
        else:
            # Baseline kontrolü: dökümanda baseline / başlangıç deklarasyonu var mı?
            has_baseline = bool(re.search(r"(?:baseline|başlangıç|initial\s+schema)", combined_content, re.IGNORECASE))

            missing_migrations = []
            for mf in migration_files:
                if mf.name not in combined_content:
                    missing_migrations.append(mf.name)

            if missing_migrations:
                # Eğer projede baseline belirtilmişse veya eski dosyalar varsa
                if has_baseline and len(missing_migrations) < len(migration_files):
                    warnings.append((
                        "W3",
                        f"{len(missing_migrations)} adet migration dosyası DB_MIGRATIONS.md içinde doğrudan listelenmemiş (baseline kapsamında kabul edildi): "
                        f"{', '.join(missing_migrations[:3])}{' (...)' if len(missing_migrations) > 3 else ''}"
                    ))
                else:
                    for mf_name in missing_migrations[:10]:
                        errors.append(("E2", f"Migration dosyası {doc_path.name} içinde belgelenmemiş: {mf_name}"))
                    if len(missing_migrations) > 10:
                        errors.append(("E2", f"... ve {len(missing_migrations) - 10} migration dosyası daha belgelenmemiş."))

            # Entity'ler var ama dokümanda anılmış mı?
            if entities:
                missing_entities = [e for e in entities if e.lower() not in combined_content.lower()]
                if len(missing_entities) == len(entities):
                    warnings.append(("W1", f"Projede {len(entities)} entity/model tespit edildi ancak {doc_path.name} içinde hiçbiri anılmamış."))

            # En az bir revizyon kaydı veya tablo formatı var mı?
            if not REVISION_HEADER_RE.search(combined_content) and "REV-" not in combined_content:
                warnings.append(("W2", f"{doc_path.name} içinde standart revizyon başlığı (### [REV-...] veya ### [V...]) bulunamadı."))

    # Dinamik Git Çalışma Ağacı Koruması (E4)
    touched_db_files = check_git_working_tree_changes(project_root, all_doc_paths)
    if touched_db_files:
        errors.append((
            "E4",
            f"Git çalışma ağacında veritabanı/migration/şema dosyası değiştirildi ancak DB_MIGRATIONS.md güncellenmedi! "
            f"Değişen dosyalar: {', '.join(touched_db_files[:5])}{' (...)' if len(touched_db_files) > 5 else ''}"
        ))

    if args.json:
        out = {
            "scope": "in_scope",
            "scope_reason": scope_reason,
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
    print(f"Veritabanı kapsamı ({scope_reason}): {len(migration_files)} migration dosyası, {len(entities)} entity/model")
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
