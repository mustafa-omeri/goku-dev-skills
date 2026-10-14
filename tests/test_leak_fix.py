#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inject_project_block() sizinti duzeltmesini gercek senaryoda dogrular.

Senaryo: skillSetWorks kaynagindaki "Proje Bazli Ek Kurallar" blogu, kendi
kural blogu OLMAYAN yeni bir projeye kopyalanirsa kaynagin proje kurallari
sizar mi?
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import delivery  # noqa: E402

SRC = ROOT / ".agent"
HEAD = re.compile(r"^## Proje Bazl\u0131 Ek Kurallar[ \t]*\r?$", re.MULTILINE)

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        failures.append(label)


def block_of(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = HEAD.search(text)
    return text[m.start():] if m else ""


def run_tests():
    print("=== TEST 1: kaynak kendi proje kurallarini iceriyor mu ===")
    src_block = block_of(SRC / "AGENTS.md")
    check("kaynakta proje blogu dolu", len(src_block) > 500, f"{len(src_block)} karakter")
    check("kaynakta skillSetWorks ozel kurali var",
          "Depo ne yapar, ne yapmaz" in src_block)

    print()
    print("=== TEST 2: yeni proje (kendi blogu YOK) kirletiliyor mu ===")
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / ".agent"
        shutil.copytree(SRC, target, ignore=shutil.ignore_patterns("__pycache__"))
        # yeni proje kendi kural blogunu hic yazmamis
        result = delivery.inject_project_block(target / "AGENTS.md", None)
        out = block_of(target / "AGENTS.md")
        check("islem sonucu 'temizlendi'", result == "temizlendi", result)
        check("kaynak proje kurallari SIZMADI",
              "Depo ne yapar, ne yapmaz" not in out)
        check("placeholder yazildi",
              "Henüz bu projeye özel ek bir kural tanımlanmamıştır" in out)
        check("baslik sayisi 1", len(HEAD.findall(
            (target / "AGENTS.md").read_text(encoding="utf-8"))) == 1)

    print()
    print("=== TEST 3: mevcut proje (kendi blogu VAR) korunuyor mu ===")
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / ".agent"
        shutil.copytree(SRC, target, ignore=shutil.ignore_patterns("__pycache__"))
        own = ("## Proje Bazlı Ek Kurallar\n\n"
               "> Bu bölüm **projeye özeldir**.\n\n"
               "### Bu proje için ek kurallar\n\n"
               "### Kendi kuralım\n\n- **Paket kökü:** `com.ornek.proje`\n")
        delivery.inject_project_block(target / "AGENTS.md", own)
        result = delivery.inject_project_block(target / "AGENTS.md", own)
        out = block_of(target / "AGENTS.md")
        check("islem sonucu 'yazildi'", result == "yazildi", result)
        check("projenin kendi blogu korundu", "com.ornek.proje" in out)
        check("kaynak sizmadi", "Depo ne yapar, ne yapmaz" not in out)
        check("baslik sayisi 1", len(HEAD.findall(
            (target / "AGENTS.md").read_text(encoding="utf-8"))) == 1)

    print()
    print("=== TEST 4: idempotentlik (iki kez calistirma) ===")
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / ".agent"
        shutil.copytree(SRC, target, ignore=shutil.ignore_patterns("__pycache__"))
        own = ("## Proje Bazlı Ek Kurallar\n\n"
               "### Bu proje için ek kurallar\n\n"
               "### Kendi kuralım\n\n- **Paket kökü:** `com.ornek.proje`\n")
        delivery.inject_project_block(target / "AGENTS.md", own)
        first = (target / "AGENTS.md").read_text(encoding="utf-8")
        delivery.inject_project_block(target / "AGENTS.md", own)
        second = (target / "AGENTS.md").read_text(encoding="utf-8")
        check("iki kez calistirma ayni sonucu verir", first == second)
        check("baslik sayisi yine 1", len(HEAD.findall(second)) == 1)

    print()
    print("=" * 58)
    if failures:
        print(f"SONUC: {len(failures)} BASARISIZ -> {failures}")
        return False
    print("SONUC: TUM TESTLER GECTI")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
