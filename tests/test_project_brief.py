#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_project_brief.py kapısının regresyon testi.

Kapsam:
  1. Gerçek depo temiz mi? (skillSetWorks kendi PROJECT_BRIEF.md dosyası)
  2. Kapsam dışı tespiti (manifesti ve brief'i olmayan dizin)
  3. Geçersiz fixture'lar yakalanıyor mu? (E1, E2, E5, W1, W2)
  4. Geçerli fixture yeşil alıyor mu? (yanlış pozitif kontrolü)
"""
import datetime
import os
import sys
import tempfile
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_project_brief as gate  # noqa: E402

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        failures.append(label)


def codes(entries):
    return {code for code, _message in entries}


VALID_BRIEF = f"""---
title: Project Brief — TestProj
type: project-brief
project: testproj
status: active
created: {datetime.date.today().isoformat()}
updated: {datetime.date.today().isoformat()}
primary_language: TypeScript (React 19, Vite 6)
frameworks: ["React 19", "Vite 6"]
database: ["Supabase PostgreSQL"]
depends_on:
  - [[projects/_STANDARTLAR/decisions/kod-ajani-vaulta-yazmaz]]
related_docs:
  - README.md
---

# 🚀 TestProj — Project Brief & Architecture Matrix

## 1. Teknoloji Yığını & Altyapı
- Dil: TypeScript

## 2. Dizin Ağacı & Modül Sorumlulukları
| Dizin | Kapsam | Notlar |
|---|---|---|
| `src/` | Kaynak kod | Modüler |

## 3. Bağlayıcı Kararlar & Dış Referanslar
| Karar | Link |
|---|---|

## 4. Veritabanı Modeli & Migration Politikası
- Model: PostgreSQL

## 5. Yaşatma ve Senkronizasyon Kuralı
Kural kopyası.
"""


def test_real_repo():
    print("=== TEST 1: Bu deponun kendi PROJECT_BRIEF.md'si temiz mi ===")
    errors, warnings = gate.validate_project_brief(ROOT)
    check("gerçek depoda hata yok", not errors, "; ".join(f"{c}: {m}" for c, m in errors))
    check("gerçek depoda uyarı yok", not warnings, "; ".join(f"{c}: {m}" for c, m in warnings))


def test_scope():
    print("=== TEST 2: Kapsam tespiti ===")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        in_scope, reason = gate.is_in_scope(tmp_root)
        check("boş dizin kapsam dışı", not in_scope, reason)

        # manifest eklendiğinde kapsama girmeli
        (tmp_root / "package.json").write_text("{}", encoding="utf-8")
        in_scope_pkg, reason_pkg = gate.is_in_scope(tmp_root)
        check("package.json varsa kapsama girer", in_scope_pkg, reason_pkg)


def test_error_scenarios():
    print("=== TEST 3: Hata kodlarının tetiklenmesi (E1, E2, E5, W1, W2) ===")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "package.json").write_text("{}", encoding="utf-8")

        # 1. E1: Dosya yok
        errors, _ = gate.validate_project_brief(tmp_root)
        check("E1 tetikleniyor (dosya yok)", "E1" in codes(errors))

        # 2. E2: Bozuk frontmatter (--- yok)
        brief_file = tmp_root / "PROJECT_BRIEF.md"
        brief_file.write_text("# Sadece başlık, frontmatter yok", encoding="utf-8")
        errors, _ = gate.validate_project_brief(tmp_root)
        check("E2 tetikleniyor (frontmatter yok)", "E2" in codes(errors))

        # 3. E2: Eksik zorunlu alanlar
        broken_fm = """---
title: Test
---
# Body
"""
        brief_file.write_text(broken_fm, encoding="utf-8")
        errors, _ = gate.validate_project_brief(tmp_root)
        check("E2 tetikleniyor (primary_language ve type eksik)", "E2" in codes(errors))

        # 4. E5: Kırık related_docs
        broken_link_fm = f"""---
title: Test
type: project-brief
primary_language: Python
created: {datetime.date.today().isoformat()}
updated: {datetime.date.today().isoformat()}
related_docs:
  - nonexistent_doc.md
---
## 1. Teknoloji Yığını
## 2. Dizin Ağacı
## 3. Bağlayıcı Kararlar
## 4. Veritabanı Modeli
## 5. Yaşatma
"""
        brief_file.write_text(broken_link_fm, encoding="utf-8")
        errors, _ = gate.validate_project_brief(tmp_root)
        check("E5 tetikleniyor (olmayan related_docs)", "E5" in codes(errors))

        # 5. W1: Eski tarih
        stale_date_fm = f"""---
title: Test
type: project-brief
primary_language: Python
created: 2020-01-01
updated: 2020-01-01
related_docs: []
---
## 1. Teknoloji Yığını
## 2. Dizin Ağacı
## 3. Bağlayıcı Kararlar
## 4. Veritabanı Modeli
## 5. Yaşatma
"""
        brief_file.write_text(stale_date_fm, encoding="utf-8")
        errors, warnings = gate.validate_project_brief(tmp_root)
        check("W1 tetikleniyor (eski tarih)", "W1" in codes(warnings))

        # 6. W2: Eksik mimari bölümü
        missing_section_fm = f"""---
title: Test
type: project-brief
primary_language: Python
created: {datetime.date.today().isoformat()}
updated: {datetime.date.today().isoformat()}
related_docs: []
---
## 1. Teknoloji Yığını
Sadece bir bölüm var.
"""
        brief_file.write_text(missing_section_fm, encoding="utf-8")
        errors, warnings = gate.validate_project_brief(tmp_root)
        check("W2 tetikleniyor (eksik mimari bölüm)", "W2" in codes(warnings))

        # 7. E7: Doldurulmamış şablon yer tutucusu ([PROJE_ADI] / [proje-slug])
        placeholder_fm = VALID_BRIEF.replace("TestProj", "[PROJE_ADI]")
        brief_file.write_text(placeholder_fm, encoding="utf-8")
        (tmp_root / "README.md").write_text("# Readme", encoding="utf-8")
        errors, _ = gate.validate_project_brief(tmp_root)
        check("E7 tetikleniyor ([PROJE_ADI] şablon yer tutucusu)", "E7" in codes(errors))


def test_git_diff_e6_serverless_infra():
    print("=== TEST 3B: Git çalışma ağacında Edge Function / Altyapı değiştiğinde E6 ===")
    import subprocess
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        subprocess.run(["git", "init"], cwd=str(tmp_root), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(tmp_root), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp_root), capture_output=True, check=True)

        (tmp_root / "README.md").write_text("# Readme", encoding="utf-8")
        (tmp_root / "PROJECT_BRIEF.md").write_text(VALID_BRIEF, encoding="utf-8")
        edge_dir = tmp_root / "supabase" / "functions" / "webhook-dispatcher"
        edge_dir.mkdir(parents=True)
        edge_file = edge_dir / "index.ts"
        edge_file.write_text("Deno.serve(() => new Response('ok'));\n", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=str(tmp_root), capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=str(tmp_root), capture_output=True, check=True)

        # Edge Function değişti ama PROJECT_BRIEF.md güncellenmedi -> E6
        edge_file.write_text("Deno.serve(() => new Response('v2'));\n", encoding="utf-8")
        errors, _ = gate.validate_project_brief(tmp_root)
        check("E6 tetikleniyor (Edge Function değişti ama PROJECT_BRIEF.md güncellenmedi)", "E6" in codes(errors))

        # PROJECT_BRIEF.md güncellendiğinde E6 kalkmalı
        (tmp_root / "PROJECT_BRIEF.md").write_text(VALID_BRIEF + "\n<!-- edge updated -->\n", encoding="utf-8")
        errors2, _ = gate.validate_project_brief(tmp_root)
        check("PROJECT_BRIEF.md güncellenince E6 kalkıyor", "E6" not in codes(errors2))


def test_valid_project():
    print("=== TEST 4: Geçerli proje testi (false positive kontrolü) ===")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "README.md").write_text("# Readme", encoding="utf-8")
        (tmp_root / "PROJECT_BRIEF.md").write_text(VALID_BRIEF, encoding="utf-8")

        errors, warnings = gate.validate_project_brief(tmp_root)
        check("geçerli projede 0 hata", not errors, "; ".join(f"{c}: {m}" for c, m in errors))
        check("geçerli projede 0 uyarı", not warnings, "; ".join(f"{c}: {m}" for c, m in warnings))


def main():
    print("=" * 60)
    print("test_project_brief.py Regresyon Test Paketi")
    print("=" * 60)
    test_real_repo()
    test_scope()
    test_error_scenarios()
    test_git_diff_e6_serverless_infra()
    test_valid_project()

    print("\n" + "=" * 60)
    if failures:
        print(f"SONUÇ: {len(failures)} TEST BAŞARISIZ!")
        return 1
    print("SONUÇ: TÜM TESTLER BAŞARIYLA GEÇTİ!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
