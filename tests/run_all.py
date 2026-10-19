#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skillSetWorks tum teslimat ve denetim testlerini kosturur."""
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent

TEST_SCRIPTS = [
    ("Audit Data", HERE / "audit_data.py"),
    ("Audit Font Runtime", HERE / "audit_font_runtime.py"),
    ("Test Leak Fix", HERE / "test_leak_fix.py"),
    ("Test Root Files", HERE / "test_root_files.py"),
    ("Test Rule Gates", HERE / "test_rule_gates.py"),
    ("Test Backup Policy", HERE / "test_backup_policy.py"),
    ("Test Sprint Board", HERE / "test_sprint_board.py"),
    ("Check AGENTS Parity", HERE / "check_agents_parity.py"),
    ("Test Skills Catalog", HERE / "test_skills_catalog.py"),
    ("Test CLI Profiles", HERE / "test_cli_profiles.py"),
]


def main():
    print("=" * 60)
    print("skillSetWorks Denetim ve Regresyon Test Paketi")
    print("=" * 60)

    failed = []
    for name, script in TEST_SCRIPTS:
        print(f"\n>>> Koşuluyor: {name} ({script.name})")
        res = subprocess.run([sys.executable, str(script)], cwd=str(HERE.parent))
        if res.returncode != 0:
            failed.append(name)

    print("\n" + "=" * 60)
    if failed:
        print(f"SONUÇ: {len(failed)}/{len(TEST_SCRIPTS)} TEST BAŞARISIZ: {failed}")
        sys.exit(1)
    else:
        print(f"SONUÇ: {len(TEST_SCRIPTS)}/{len(TEST_SCRIPTS)} TESTİN HEPSİ BAŞARIYLA GEÇTİ!")
        sys.exit(0)


if __name__ == "__main__":
    main()
