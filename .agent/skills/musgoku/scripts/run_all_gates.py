#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Birleşik Kapsam-Duyarlı Doğrulama Kapısı Orkestratörü (Unified Gate Runner).

AGENTS.md §3.1 ve §3.3 (Kapsam-Duyarlı Doğrulama İlkesi) uyarınca projedeki
ilgili tüm ölçülebilir doğrulama kapılarını tek komutla koşturur ve özetler.

Kullanım:
  python .agent/skills/musgoku/scripts/run_all_gates.py
  python .agent/skills/musgoku/scripts/run_all_gates.py --include-slow
  python .agent/skills/musgoku/scripts/run_all_gates.py --json
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

FAST_PYTHON_GATES = [
    ("Kural Seti & Tablo Senkronu", ".agent/skills/musgoku/scripts/rules_gates.py", ["--strict"]),
    ("Oturum Devri (HANDOFF.md)", ".agent/skills/musgoku/scripts/check_handoff.py", []),
    ("Canlı Proje Mimarisi (PROJECT_BRIEF.md)", ".agent/skills/musgoku/scripts/check_project_brief.py", []),
    ("Veritabanı Migration (DB_MIGRATIONS.md)", ".agent/skills/musgoku/scripts/check_db_migrations.py", []),
    ("API Dokümantasyonu", ".agent/skills/musgoku/scripts/check_api_docs.py", []),
    ("Tasarım Sözleşmesi (DESIGN.md)", ".agent/skills/musgoku/scripts/check_design_contract.py", []),
    ("Tasarım Skill Sahipliği", ".agent/skills/musgoku/scripts/check_design_skills.py", []),
    ("Tasarım Anti-Slop", ".agent/skills/musgoku/scripts/check_design_slop.py", []),
    ("Tema Kontrastı & WCAG", ".agent/skills/musgoku/scripts/check_theme_contrast.py", []),
    ("Frontend i18n", ".agent/skills/i18n-localization/scripts/i18n_checker.py", []),
    ("Sprint & Kanban Panosu", ".agent/skills/musgoku/scripts/check_sprint_board.py", []),
    ("Vite SPA İzolasyonu", ".agent/skills/musgoku/scripts/check_vite_spa.py", []),
]


def run_gates(root: Path, include_slow: bool = False) -> Dict[str, Any]:
    root = root.resolve()
    results: List[Dict[str, Any]] = []

    for label, rel_script, extra_args in FAST_PYTHON_GATES:
        script_path = root / rel_script
        if not script_path.is_file():
            results.append({
                "name": label,
                "command": rel_script,
                "status": "SKIPPED",
                "reason": "script kurulu değil (profil kapsamı dışı)",
                "exit_code": 0,
            })
            continue

        cmd = [sys.executable, str(script_path)] + extra_args
        res = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        out = (res.stdout + "\n" + res.stderr).strip()
        last_line = out.splitlines()[-1] if out.splitlines() else ""
        status = "PASS" if res.returncode == 0 else "FAIL"
        if res.returncode == 0 and (
            out.startswith("[SKIP]")
            or out.startswith("[Kapsam")
            or "kapsam dışı" in last_line.lower()
            or "kapsam disi" in last_line.lower()
            or "0 migration" in last_line.lower()
            or "0 endpoint" in last_line.lower()
        ):
            status = "SKIPPED"
        elif res.returncode == 2 and ("--locales ile belirt" in out or "sözlük klasörü bulunamadı" in out.lower()):
            status = "SKIPPED"
            last_line = "sözlük klasörü bulunamadı (i18n kapsam dışı)"
        results.append({
            "name": label,
            "command": f"python {rel_script}" + (" " + " ".join(extra_args) if extra_args else ""),
            "status": status,
            "exit_code": 0 if status == "SKIPPED" else res.returncode,
            "summary": last_line[:160],
            "output": out if status == "FAIL" else "",
        })

    # Skill sözleşme testi
    contracts_dir = root / ".agent" / "skills" / "ui-ux-pro-max" / "scripts" / "tests"
    if (contracts_dir / "test_skill_contracts.py").is_file():
        res = subprocess.run(
            [sys.executable, "-m", "unittest", "test_skill_contracts"],
            cwd=str(contracts_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        out = (res.stdout + "\n" + res.stderr).strip()
        results.append({
            "name": "Skill Sözleşmesi & Tetikleyici Sözlüğü",
            "command": "python -m unittest test_skill_contracts",
            "status": "PASS" if res.returncode == 0 else "FAIL",
            "exit_code": res.returncode,
            "summary": "OK" if res.returncode == 0 else out.splitlines()[-1][:160],
            "output": out if res.returncode != 0 else "",
        })

    if include_slow:
        # Bundle limits (only if vite config exists)
        has_vite = any((root / f).is_file() for f in ("vite.config.ts", "vite.config.js", "vite.config.mjs"))
        bundle_script = root / ".agent" / "skills" / "musgoku" / "scripts" / "check_bundle_limits.py"
        if has_vite and bundle_script.is_file():
            res = subprocess.run(
                [sys.executable, str(bundle_script)],
                cwd=str(root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            out = (res.stdout + "\n" + res.stderr).strip()
            results.append({
                "name": "Frontend Bundle Bütçesi",
                "command": "python .agent/skills/musgoku/scripts/check_bundle_limits.py",
                "status": "PASS" if res.returncode == 0 else "FAIL",
                "exit_code": res.returncode,
                "summary": out.splitlines()[-1][:160] if out.splitlines() else "",
                "output": out if res.returncode != 0 else "",
            })

    failed = [r for r in results if r["status"] == "FAIL"]
    passed = [r for r in results if r["status"] == "PASS"]
    skipped = [r for r in results if r["status"] == "SKIPPED"]

    return {
        "root": str(root),
        "total": len(results),
        "passed_count": len(passed),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "failed_gates": [r["name"] for r in failed],
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Birleşik Kapsam-Duyarlı Doğrulama Kapısı Orkestratörü")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Proje kök dizini")
    parser.add_argument("--include-slow", action="store_true", help="Ağır build/bundle kapılarını da dahil et")
    parser.add_argument("--json", action="store_true", help="JSON çıktı üret")
    args = parser.parse_args()

    summary = run_gates(args.root, include_slow=args.include_slow)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1 if summary["failed_count"] > 0 else 0

    print("=" * 68)
    print("Birleşik Doğrulama Kapıları (run_all_gates.py)")
    print("=" * 68)
    for r in summary["results"]:
        badge = {"PASS": "[PASS]", "SKIPPED": "[SKIP]", "FAIL": "[FAIL]"}[r["status"]]
        detail = r.get("summary") or r.get("reason") or ""
        print(f"  {badge:6} {r['name']:40} {detail}")
        if r["status"] == "FAIL" and r.get("output"):
            for line in r["output"].splitlines()[:10]:
                print(f"         | {line}")

    print("-" * 68)
    print(
        f"ÖZET: {summary['passed_count']} geçti · "
        f"{summary['skipped_count']} kapsam dışı/atlandı · "
        f"{summary['failed_count']} başarısız (Toplam {summary['total']} kapı)"
    )
    if summary["failed_count"] > 0:
        print(f"[FAIL] Başarısız kapılar: {', '.join(summary['failed_gates'])}")
        return 1
    print("[OK] Tüm kapsam içi doğrulama kapıları yeşil.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
