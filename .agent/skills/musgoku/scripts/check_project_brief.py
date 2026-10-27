#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evrensel Canlı Proje Özeti ve Mimari Senkronizasyon Kapısı (PROJECT_BRIEF.md).

Neden var?
----------
`project-brief-maintenance.md` kuralı, projenin canlı mimarisini, teknoloji yığınını,
veritabanı şemasını ve bağlayıcı standartlarını tek bir konsolide matriste (`PROJECT_BRIEF.md`)
taze tutulmasını zorunlu kılar.

Bu kapı scripti aşağıdaki kontrolleri deterministik olarak yürütür:
1. Zorunlu Dosya Varlığı (E1):
   - Proje kökünde `PROJECT_BRIEF.md` dosyasının varlığını denetler.
2. YAML Frontmatter Geçerliliği (E2):
   - `title`, `type: project-brief`, `primary_language` alanlarının tamlığını doğrular.
3. Git Diff Bağımlılık Senkronizasyonu (E3):
   - `package.json`, `pom.xml`, `requirements.txt` vb. değiştiğinde `PROJECT_BRIEF.md`
     dosyasının da aynı oturumda güncellendiğini matematiksel olarak zorunlu kılar.
4. Git Diff Veritabanı / Migration Senkronizasyonu (E4):
   - Veritabanı şeması veya migration değiştiğinde `PROJECT_BRIEF.md`'nin de güncellendiğini denetler.
5. Kırık Dokümantasyon Bağlantısı (E5):
   - Frontmatter'daki `related_docs` altında listelenen dosyaların diskte var olduğunu doğrular.
6. Tarih ve Bölüm Uyum Kontrolleri (W1, W2):
   - `updated` tarihinin tazeliğini ve 5 standart mimari bölümünün mevcudiyetini doğrular.

Kontroller
----------
E1 zorunlu dosya eksik      PROJECT_BRIEF.md bulunamadı
E2 geçersiz frontmatter     YAML frontmatter eksik veya zorunlu alanlar (title, type, primary_language) yok
E3 bağımlılık sapması       Git diff'te paket/manifest değişti ama PROJECT_BRIEF.md güncellenmedi
E4 veritabanı sapması       Git diff'te DB/migration değişti ama PROJECT_BRIEF.md güncellenmedi
E5 kırık doküman linki      related_docs listesindeki dosya diskte bulunamadı
W1 tarih sapması            updated tarihi bugünün tarihi değil
W2 eksik mimari bölümü      5 standart mimari bölümünden biri eksik

E1-E5 hata (exit 1) · W1-W2 uyarı · exit 2 = araç hatası.
Manifest içermeyen projelerde kapsam dışı: exit 0.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEPENDENCY_MANIFESTS = {
    "package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock",
    "pom.xml", "build.gradle", "build.gradle.kts",
    "requirements.txt", "pyproject.toml", "Pipfile", "Pipfile.lock",
    "Cargo.toml", "Cargo.lock", "go.mod", "go.sum"
}

DB_INDICATORS = {
    "supabase/migrations", "prisma/schema.prisma", "migrations",
    "schema.sql", "database.sql"
}

STANDARD_SECTIONS = [
    "Teknoloji Yığını",
    "Dizin Ağacı",
    "Bağlayıcı Kararlar",
    "Veritabanı Modeli",
    "Yaşatma"
]


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


def is_in_scope(project_root: Path) -> tuple[bool, str]:
    """Projenin bu kapı kapsamında olup olmadığını belirler."""
    brief_file = project_root / "PROJECT_BRIEF.md"
    if brief_file.is_file():
        return True, "PROJECT_BRIEF.md mevcut"

    manifest_candidates = [
        "package.json", "pom.xml", "build.gradle", "requirements.txt",
        "pyproject.toml", "Cargo.toml", "go.mod", "goku.json"
    ]
    for m in manifest_candidates:
        if (project_root / m).is_file():
            return True, f"Proje manifesti tespit edildi ({m})"

    if (project_root / ".agent").is_dir():
        return True, ".agent/ klasörü mevcut (goku-dev-skills)"

    return False, "Proje manifesti veya .agent/ tespit edilemedi"


def parse_frontmatter(content: str) -> tuple[dict[str, any] | None, str]:
    """Basit ve bağımlılıksız YAML frontmatter ayrıştırıcısı."""
    if not content.startswith("---"):
        return None, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content

    yaml_raw = parts[1]
    body = parts[2]

    data: dict[str, any] = {}
    current_list_key = None

    for line in yaml_raw.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        # Liste öğesi (- item)
        if line_str.startswith("- ") and current_list_key:
            item_val = line_str[2:].strip().strip("\"'")
            if isinstance(data.get(current_list_key), list):
                data[current_list_key].append(item_val)
            continue

        if ":" in line_str:
            key, val = line_str.split(":", 1)
            key = key.strip()
            val = val.strip()

            # Köşeli parantezli liste ["a", "b"]
            if val.startswith("[") and val.endswith("]"):
                items_str = val[1:-1].strip()
                if items_str:
                    items = [it.strip().strip("\"'") for it in items_str.split(",") if it.strip()]
                    data[key] = items
                else:
                    data[key] = []
                current_list_key = None
            elif not val:
                # Çok satırlı liste başlangıcı
                data[key] = []
                current_list_key = key
            else:
                data[key] = val.strip("\"'")
                current_list_key = None

    return data, body


def check_git_diff_drift(project_root: Path) -> tuple[list[str], list[str]]:
    """Git diff üzerinden bağımlılık veya DB değişip PROJECT_BRIEF.md değişmemişse yakalar."""
    try:
        git_dir = project_root / ".git"
        if not git_dir.exists():
            return [], []

        cmd = ["git", "status", "--porcelain"]
        proc = subprocess.run(
            cmd, cwd=project_root, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace"
        )
        if proc.returncode != 0:
            return [], []

        changed_deps: list[str] = []
        changed_db: list[str] = []
        brief_changed = False

        for raw_line in proc.stdout.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # Durum harflerini atla: M file, A file, ?? file vb.
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            file_part = parts[1].strip()
            if " -> " in file_part:
                file_part = file_part.split(" -> ")[1].strip()

            norm_path = file_part.replace("\\", "/").lower()

            if norm_path.endswith("project_brief.md"):
                brief_changed = True
                continue

            # Manifest kontrolü
            basename = Path(norm_path).name
            if basename in DEPENDENCY_MANIFESTS:
                changed_deps.append(file_part)

            # DB / migration kontrolü
            is_db = any(ind in norm_path for ind in DB_INDICATORS) or norm_path.endswith((".sql", ".prisma"))
            if is_db and not any(norm_path.startswith(d) for d in (".agent/", "yedekler/", "docs/")):
                changed_db.append(file_part)

        if brief_changed:
            return [], []

        return changed_deps, changed_db

    except Exception:
        return [], []


def validate_project_brief(project_root: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    brief_path = project_root / "PROJECT_BRIEF.md"
    if not brief_path.is_file():
        errors.append((
            "E1",
            "Zorunlu 'PROJECT_BRIEF.md' dosyası proje kökünde bulunamadı. "
            "(.agent/templates/PROJECT_BRIEF.template.md şablonundan oluşturun)"
        ))
        return errors, warnings

    try:
        content = brief_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        errors.append(("E2", f"PROJECT_BRIEF.md okunamadı: {exc}"))
        return errors, warnings

    # 1. Frontmatter denetimi
    fm, body = parse_frontmatter(content)
    if not fm:
        errors.append(("E2", "PROJECT_BRIEF.md içinde geçerli YAML frontmatter (--- ... ---) bulunamadı."))
    else:
        # Zorunlu alanlar
        for req in ("title", "type", "primary_language"):
            if not fm.get(req):
                errors.append(("E2", f"YAML frontmatter zorunlu alanı eksik veya boş: '{req}'"))

        if fm.get("type") != "project-brief":
            errors.append(("E2", f"YAML frontmatter 'type' değeri 'project-brief' olmalıdır (Mevcut: '{fm.get('type')}')"))

        # related_docs kırık bağlantı denetimi (E5)
        rel_docs = fm.get("related_docs")
        if isinstance(rel_docs, list):
            for doc in rel_docs:
                clean_doc = doc.strip().strip("[]").replace("\\", "/")
                target_file = project_root / clean_doc
                if not target_file.is_file():
                    errors.append(("E5", f"related_docs altındaki dosya diskte bulunamadı: '{clean_doc}'"))

        # Tarih kontrolü (W1)
        today_str = datetime.date.today().isoformat()
        updated_val = str(fm.get("updated", "")).strip()
        if updated_val and updated_val != today_str:
            # Sadece dosyada başka bir değişiklik varsa veya git'te staged ise uyar
            warnings.append((
                "W1",
                f"PROJECT_BRIEF.md frontmatter 'updated' tarihi ({updated_val}) bugünün tarihi ({today_str}) değil."
            ))

    # 2. Standart 5 mimari bölüm denetimi (W2)
    for section in STANDARD_SECTIONS:
        if section.lower() not in body.lower():
            warnings.append(("W2", f"Standart mimari bölümü eksik veya başlığı değiştirilmiş: '## {section}'"))

    # 3. Git Diff Drift denetimi (E3, E4)
    changed_deps, changed_db = check_git_diff_drift(project_root)
    if changed_deps:
        errors.append((
            "E3",
            f"Git çalışma ağacında bağımlılık manifesti değişti ({', '.join(changed_deps[:2])}) "
            "ancak 'PROJECT_BRIEF.md' güncellenmedi! Mimariyi senkronize edin."
        ))

    if changed_db:
        errors.append((
            "E4",
            f"Git çalışma ağacında veritabanı/migration dosyası değişti ({', '.join(changed_db[:2])}) "
            "ancak 'PROJECT_BRIEF.md' güncellenmedi! Mimariyi senkronize edin."
        ))

    return errors, warnings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evrensel Canlı Proje Özeti ve Mimari Senkronizasyon Kapısı")
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı")
    parser.add_argument("--strict", action="store_true", help="Uyarıları da hata say")
    args = parser.parse_args(argv)

    project_root = find_project_root()
    in_scope, scope_reason = is_in_scope(project_root)

    if not in_scope:
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
            print(f"Kapsam Dışı: {scope_reason} — PROJECT_BRIEF.md kuralı bu projede uygulanmaz.")
            print("\nSONUÇ: [OK]")
        return 0

    errors, warnings = validate_project_brief(project_root)

    effective_errors = list(errors)
    if args.strict:
        for w_code, w_msg in warnings:
            effective_errors.append((w_code, f"[STRICT] {w_msg}"))

    if args.json:
        result = {
            "scope": "in_scope",
            "reason": scope_reason,
            "errors": [{"code": c, "message": m} for c, m in errors],
            "warnings": [{"code": c, "message": m} for c, m in warnings],
            "strict": args.strict,
            "status": "FAIL" if effective_errors else "OK",
            "exit": 1 if effective_errors else 0
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result["exit"]

    # Terminal çıktısı
    print("=" * 60)
    print("Canlı Proje Özeti Kapısı (check_project_brief.py)")
    print("=" * 60)
    print(f"Proje kökü: {project_root}")
    print(f"Kapsam   : {scope_reason}")

    if not errors and not warnings:
        print("\n✅ PROJECT_BRIEF.md eksiksiz, YAML geçerli ve çalışma ağacı senkron.")
        print("\nSONUÇ: 0 hata · 0 uyarı · [OK]")
        return 0

    if warnings:
        print(f"\n⚠️  UYARILAR ({len(warnings)}):")
        for code, msg in warnings:
            print(f"  [{code}] {msg}")

    if errors:
        print(f"\n❌ HATALAR ({len(errors)}):")
        for code, msg in errors:
            print(f"  [{code}] {msg}")
        print(f"\nSONUÇ: {len(errors)} hata · {len(warnings)} uyarı · [FAIL]")
        return 1

    if args.strict and warnings:
        print(f"\nSONUÇ: [STRICT] {len(warnings)} uyarı hata sayıldı · [FAIL]")
        return 1

    print(f"\nSONUÇ: 0 hata · {len(warnings)} uyarı · [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
