#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Alt skill pytest paketlerini (brand, design-system, ui-styling) koşar."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
PYTEST_DIRS = [
    ROOT / ".agent" / "skills" / "brand" / "scripts" / "tests",
    ROOT / ".agent" / "skills" / "design-system" / "scripts" / "tests",
    ROOT / ".agent" / "skills" / "ui-styling" / "scripts" / "tests",
    ROOT / ".agent" / "skills" / "test-spec-generator" / "scripts" / "tests",
]


def main() -> int:
    if importlib.util.find_spec("pytest") is None:
        print("[SKIP] pytest kurulu değil — alt skill pytest paketleri atlandı.")
        return 0

    targets = [str(p) for p in PYTEST_DIRS if p.is_dir()]
    if not targets:
        print("[SKIP] Alt skill pytest klasörü bulunamadı.")
        return 0

    proc = subprocess.run([sys.executable, "-m", "pytest", *targets, "-q"], cwd=str(ROOT))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
