#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rootFiles dagitim yolunu gecici bir proje uzerinde dener (uretime dokunmadan)."""
import json
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

SRC = ROOT
AGENT = SRC / ".agent"
failures = []


def check(label, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))
    if not cond:
        failures.append(label)


def run_tests():
    config = delivery.load_config(SRC / "delivery.md")
    print("config rootFiles:", config.get("rootFiles"))
    check("rootFiles tanimli", bool(config.get("rootFiles")))
    check("rootFiles kaynak dosyalari var",
          all((SRC / n).is_file() for n in config.get("rootFiles", [])))

    print()
    print("=== TEST 1: bos projeye yazma ===")
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp)
        (proj / ".agent").mkdir()
        written, skipped = delivery.distribute_root_files(config, AGENT, proj)
        # rootFiles sayisi config'den okunur; listeye dosya eklenince bu
        # kontrol kirilmamalidir (sabit sayi yazmak sessiz bayatlik olurdu).
        expected = len(config.get("rootFiles", []))
        check("tum kok dosyalar yazildi", written == expected,
              f"written={written}, beklenen={expected}")
        check("atlanan yok", skipped == 0)
        for name in config.get("rootFiles", []):
            check(f"{name} hedefte var", (proj / name).is_file())
            check(f"{name} icerigi birebir ayni",
                  (proj / name).read_bytes() == (SRC / name).read_bytes())
        src_bytes = (SRC / "readme-help.md").read_bytes()
        check("icerik birebir ayni", (proj / "readme-help.md").read_bytes() == src_bytes)
        check(".agent/ icine koyulmadi", not (proj / ".agent" / "readme-help.md").exists())
        check("verifier temiz", delivery.verify_root_files(config, AGENT, proj) == [])

    print()
    print("=== TEST 2: bayat / farkli hedef dosyasinin ezilmesi ===")
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp)
        (proj / ".agent").mkdir()
        (proj / "readme-help.md").write_text("BAYAT SURUM", encoding="utf-8")
        delivery.distribute_root_files(config, AGENT, proj)
        check("bayat icerik ezildi",
              (proj / "readme-help.md").read_bytes() == (SRC / "readme-help.md").read_bytes())
        check("verifier temiz", delivery.verify_root_files(config, AGENT, proj) == [])

    print()
    print("=== TEST 3: verifier bozuklugu yakaliyor mu ===")
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp)
        (proj / ".agent").mkdir()
        delivery.distribute_root_files(config, AGENT, proj)
        (proj / "readme-help.md").write_text("BOZULDU", encoding="utf-8")
        problems = delivery.verify_root_files(config, AGENT, proj)
        check("fark yakalandi", bool(problems), str(problems))
        (proj / "readme-help.md").unlink()
        problems = delivery.verify_root_files(config, AGENT, proj)
        check("eksik dosya yakalandi", any("eksik" in p for p in problems), str(problems))

    print()
    print("=== TEST 4: DEV_BRIEF.md yonetilmemis olmali (kritik) ===")
    for name in ("DEV_BRIEF.md", "HANDOFF.md", "knowledge-base.md", "AGENTS.md", "skills-catalog.html"):
        check(f"{name} rootFiles'ta degil", name not in config.get("rootFiles", []))

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
