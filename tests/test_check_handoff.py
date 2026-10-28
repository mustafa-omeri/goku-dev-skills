#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_handoff.py ve run_all_gates.py kapılarının regresyon testi.

Kapsam:
  1. Gerçek depo temiz mi? (skillSetWorks kendi HANDOFF.md dosyası)
  2. Kapsam dışı tespiti (boş dizin vs proje dizini)
  3. Hata ve uyarı kodlarının tetiklenmesi (E1, E2, E3, E4, W1, W2)
  4. Geçerli proje testi (yanlış pozitif kontrolü)
  5. run_all_gates.py kapsam-duyarlı orkestratör testi
"""
import subprocess
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

import check_handoff as gate  # noqa: E402
import run_all_gates as runner  # noqa: E402

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        failures.append(label)


def codes(entries):
    return {code for code, _message in entries}


VALID_HANDOFF = """# HANDOFF — TestProj

> **Son güncelleme:** 2026-10-28 · `v1.0.0`
> **Güncellik kanıtı:** 12 test · 0 hata

---

## 1. Nerede Kaldık

- Temel kurulum tamamlandı.

---

## 2. Katman Bütünlüğü ve İlerleme

| Özellik | Durum |
|---|---|
| Çekirdek | ✅ TAMAM |

---

## 3. Sıradaki İşler (Canlı Görev Panosu)

| # | Durum | Görev |
|---|---|---|
| 1 | ⏭️ SIRADAKİ | Yeni modül eklenmesi |

---

## 4. Bu Projede Düşülen Hatalar / Tuzaklar

- Tuzak 1: Örnek ders.

---

## 5. Bu Projede Alınan Kararlar

- Karar 1: Örnek karar.

---

## 6. Nasıl Test Edilir (kullanıcı gözüyle)

- `pytest` çalıştırılır.
"""


def test_real_repo():
    print("=== TEST 1: Bu deponun kendi HANDOFF.md'si temiz mi ===")
    errors, warnings = gate.validate_handoff(ROOT)
    check("gerçek depoda hata yok", not errors, "; ".join(f"{c}: {m}" for c, m in errors))
    check("gerçek depoda uyarı yok", not warnings, "; ".join(f"{c}: {m}" for c, m in warnings))


def test_scope():
    print("=== TEST 2: Kapsam tespiti ===")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        in_scope, reason = gate.is_in_scope(tmp_root)
        check("boş dizin kapsam dışı", not in_scope, reason)

        (tmp_root / "package.json").write_text("{}", encoding="utf-8")
        in_scope_pkg, reason_pkg = gate.is_in_scope(tmp_root)
        check("package.json varsa kapsama girer", in_scope_pkg, reason_pkg)


def test_error_scenarios():
    print("=== TEST 3: Hata ve uyarı kodlarının tetiklenmesi (E1, E2, E3, E4, W1, W2) ===")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "package.json").write_text("{}", encoding="utf-8")

        # 1. E2: HANDOFF.md yok
        errors, _ = gate.validate_handoff(tmp_root)
        check("E2 tetikleniyor (HANDOFF.md yok)", "E2" in codes(errors))

        # 2. E1: Yasaklı mükerrer görev dosyası (TASK.md / TODO.md)
        (tmp_root / "HANDOFF.md").write_text(VALID_HANDOFF, encoding="utf-8")
        (tmp_root / "TASK.md").write_text("# Rogue task", encoding="utf-8")
        errors, _ = gate.validate_handoff(tmp_root)
        check("E1 tetikleniyor (TASK.md mevcut)", "E1" in codes(errors))
        (tmp_root / "TASK.md").unlink()

        # 3. E4: Doldurulmamış şablon yer tutucusu
        placeholder_handoff = VALID_HANDOFF.replace("2026-10-28", "[YYYY-MM-DD]")
        (tmp_root / "HANDOFF.md").write_text(placeholder_handoff, encoding="utf-8")
        errors, _ = gate.validate_handoff(tmp_root)
        check("E4 tetikleniyor ([YYYY-MM-DD] yer tutucusu)", "E4" in codes(errors))

        # 4. W1: §3 Sıradaki İşler tablosunda ✅ BİTTİ satırı kalmış
        polluted_handoff = VALID_HANDOFF.replace(
            "| 1 | ⏭️ SIRADAKİ | Yeni modül eklenmesi |",
            "| 1 | ✅ BİTTİ | Eski bitmiş görev |\n| 2 | ⏭️ SIRADAKİ | Yeni modül eklenmesi |",
        )
        (tmp_root / "HANDOFF.md").write_text(polluted_handoff, encoding="utf-8")
        errors, warnings = gate.validate_handoff(tmp_root)
        check("W1 tetikleniyor (§3 içinde ✅ BİTTİ satırı)", "W1" in codes(warnings))


def test_git_diff_e3_and_w2():
    print("=== TEST 4: Git çalışma ağacı E3 (kod değişti HANDOFF güncellenmedi) ve W2 ===")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        subprocess.run(["git", "init"], cwd=str(tmp_root), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(tmp_root), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp_root), capture_output=True, check=True)

        (tmp_root / "package.json").write_text("{}", encoding="utf-8")
        (tmp_root / "HANDOFF.md").write_text(VALID_HANDOFF, encoding="utf-8")
        src_dir = tmp_root / "src" / "components"
        src_dir.mkdir(parents=True)
        app_file = src_dir / "Modal.tsx"
        app_file.write_text("export const Modal = () => null;\n", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=str(tmp_root), capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=str(tmp_root), capture_output=True, check=True)

        # Modify UI component without updating HANDOFF.md or KULLANICI_TEST_REHBERI.md
        app_file.write_text("export const Modal = () => <div>Changed</div>;\n", encoding="utf-8")

        errors, warnings = gate.validate_handoff(tmp_root)
        check("E3 tetikleniyor (src/ değişti ama HANDOFF.md güncellenmedi)", "E3" in codes(errors))
        check("W2 tetikleniyor (UI değişti ama KULLANICI_TEST_REHBERI.md yok)", "W2" in codes(warnings))

        # Now update HANDOFF.md and create KULLANICI_TEST_REHBERI.md
        (tmp_root / "HANDOFF.md").write_text(VALID_HANDOFF + "\n<!-- updated -->\n", encoding="utf-8")
        (tmp_root / "KULLANICI_TEST_REHBERI.md").write_text("# Test Rehberi\n", encoding="utf-8")
        errors2, warnings2 = gate.validate_handoff(tmp_root)
        check("HANDOFF.md ve rehber güncellenince E3/W2 kalkıyor", "E3" not in codes(errors2) and "W2" not in codes(warnings2))


def test_run_all_gates():
    print("=== TEST 5: run_all_gates.py kapsam-duyarlı orkestratör testi ===")
    summary = runner.run_gates(ROOT, include_slow=False)
    check("run_all_gates gerçek depoda 0 başarısız kapı döndürdü", summary["failed_count"] == 0, str(summary.get("failed_gates")))
    check("run_all_gates en az 5 kapı değerlendirdi", len(summary["results"]) >= 5, f"{len(summary['results'])} kapı")


def main():
    print("=" * 60)
    print("test_check_handoff.py Regresyon Test Paketi")
    print("=" * 60)
    test_real_repo()
    test_scope()
    test_error_scenarios()
    test_git_diff_e3_and_w2()
    test_run_all_gates()

    print("\n" + "=" * 60)
    if failures:
        print(f"SONUÇ: {len(failures)} TEST BAŞARISIZ!")
        return 1
    print("SONUÇ: TÜM TESTLER BAŞARIYLA GEÇTİ!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
