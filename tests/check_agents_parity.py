#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kaynak ile hedef AGENTS.md'nin GLOBAL bolumunu (proje blogu oncesi) karsilastirir."""
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import delivery  # noqa: E402

SRC = ROOT / ".agent" / "AGENTS.md"
config = delivery.load_config(ROOT / "delivery.md")
PROJECTS = {p["id"]: Path(p["path"]) for p in config.get("projects", []) if p.get("enabled", True)}

HEAD = re.compile(r"^## Proje Bazl\u0131 Ek Kurallar[ \t]*\r?$", re.MULTILINE)


def split(text: str):
    m = HEAD.search(text)
    if not m:
        return text, ""
    return text[:m.start()], text[m.start():]


def run_check():
    src_text = SRC.read_text(encoding="utf-8")
    src_global, src_block = split(src_text)
    print(f"KAYNAK: global {len(src_global)} / proje blogu {len(src_block)} karakter")
    print(f"Kaynagin proje blogu skillSetWorks'a ait mi: "
          f"{'EVET' if 'Depo ne yapar, ne yapmaz' in src_block else 'HAYIR'}")
    print()

    stale = []
    for name, path in PROJECTS.items():
        f = Path(path) / ".agent" / "AGENTS.md"
        if not f.is_file():
            print(f"=== {name} ===")
            print(f"  DOSYA BULUNAMADI: {f}")
            stale.append(name)
            continue

        g, b = split(f.read_text(encoding="utf-8"))
        same = g == src_global
        leaked = "Depo ne yapar, ne yapmaz" in b
        print(f"=== {name} ===")
        print(f"  global bolum kaynakla ayni : {same}")
        print(f"  skillSetWorks kurali sizmis : {leaked}")
        print(f"  proje blogu                 : {len(b)} karakter")
        if not same or leaked:
            stale.append(name)

    print()
    print("SONUC:", "YENIDEN DAGITIM GEREKMIYOR" if not stale
          else f"YENIDEN DAGITIM GEREKIYOR: {stale}")
    return len(stale) == 0


if __name__ == "__main__":
    success = run_check()
    sys.exit(0 if success else 1)
