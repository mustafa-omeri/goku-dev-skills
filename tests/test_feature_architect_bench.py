#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ecosystem & Seam 4 Benchmark Gate Tests for `tests/feature-architect-bench/quality_bench.py`."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / ".agent" / "skills" / "feature-architect"
BENCH_DIR = ROOT / "tests" / "feature-architect-bench"
BENCH_RUNNER = BENCH_DIR / "quality_bench.py"

FORBIDDEN_TRACE_RE = re.compile(
    r"\bocai\b|FEProjectv1|FEProject\b|bookmarkManagerProject|bookmarkManager|\bkalansure\b"
    r"|peopleside|performinds|mocktest\.com|mockuser\d*|\bpassword123\b",
    re.IGNORECASE,
)


class FeatureArchitectBenchmarkGateTests(unittest.TestCase):
    """Enforces Seam 4 KPIs (14 synthetic fixtures, recall, precision, FPR, determinism, purity)."""

    def test_01_golden_benchmark_suite_meets_all_kpis(self) -> None:
        self.assertTrue(BENCH_RUNNER.is_file(), f"Missing benchmark runner: {BENCH_RUNNER}")
        proc = subprocess.run(
            [
                sys.executable,
                str(BENCH_RUNNER),
                "--fixtures",
                "--determinism-runs",
                "3",
                "--json",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"quality_bench.py failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )
        report = json.loads(proc.stdout)
        self.assertGreaterEqual(report["scenarios_count"], 14)
        self.assertGreaterEqual(report["metrics"]["structural_recall"], 0.90)
        self.assertGreaterEqual(report["metrics"]["precision"], 0.80)
        self.assertLessEqual(report["metrics"]["clean_repo_fpr"], 0.02)
        self.assertEqual(report["metrics"]["evidence_integrity"], 1.0)
        self.assertTrue(report["metrics"]["determinism_pass"])

    def test_02_zero_project_or_credential_traces_in_skill_and_bench(self) -> None:
        violations: list[str] = []
        for scan_dir in (SKILL_DIR, BENCH_DIR):
            if not scan_dir.is_dir():
                continue
            for path in sorted(scan_dir.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                if path.suffix.lower() not in {".md", ".py", ".json", ".mjs", ".ts", ".tsx", ".java", ".sql", ".yaml", ".yml"}:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                for m in FORBIDDEN_TRACE_RE.finditer(text):
                    violations.append(f"{path.relative_to(ROOT)}: forbidden trace {m.group(0)!r}")
        self.assertEqual(violations, [], "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
