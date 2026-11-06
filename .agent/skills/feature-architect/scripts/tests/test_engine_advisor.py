#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit & CLI contract tests for `engine_advisor.py` (Single vs Multi-Agent advisor)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
ADVISOR_SCRIPT = SCRIPTS_DIR / "engine_advisor.py"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import engine_advisor  # noqa: E402


class EngineAdvisorUnitTests(unittest.TestCase):
    def test_advisor_small_project_single(self) -> None:
        metrics = {"source_files": 42, "loc": 4800, "routes": 8, "peers": 0, "gaps": 5}
        advice = engine_advisor.advise(metrics, subagents=True)
        self.assertEqual(advice["total"], 0)
        self.assertEqual(advice["size_class"], "small")
        self.assertEqual(advice["recommendation"], "single")
        self.assertTrue(advice["ask_user"])

    def test_advisor_large_project_recommends_multi_and_asks(self) -> None:
        metrics = {"source_files": 512, "loc": 61230, "routes": 74, "peers": 1, "gaps": 33}
        advice = engine_advisor.advise(metrics, subagents="yes")
        self.assertEqual(advice["total"], 8)
        self.assertEqual(advice["size_class"], "large")
        self.assertEqual(advice["recommendation"], "multi")
        self.assertTrue(advice["ask_user"])
        self.assertIn("Önerilen", advice["question_prompt"])

    def test_advisor_no_subagents_never_asks(self) -> None:
        metrics = {"source_files": 600, "loc": 80000, "routes": 90, "peers": 2, "gaps": 50}
        advice = engine_advisor.advise(metrics, subagents="no")
        self.assertEqual(advice["size_class"], "large")
        self.assertEqual(advice["recommendation"], "single")
        self.assertFalse(advice["ask_user"])

    def test_advisor_medium_boundaries(self) -> None:
        # Exact lower boundaries for 1 point each on files (150), loc (15000), routes (20) => total 3 => medium
        m_med = {"source_files": 150, "loc": 15000, "routes": 20, "peers": 0, "gaps": 14}
        adv_med = engine_advisor.advise(m_med, subagents=True)
        self.assertEqual(adv_med["points"], {"source_files": 1, "loc": 1, "routes": 1, "peers": 0, "gaps": 0})
        self.assertEqual(adv_med["total"], 3)
        self.assertEqual(adv_med["size_class"], "medium")
        self.assertEqual(adv_med["recommendation"], "single")

        # Just below boundaries: 149 files, 14999 loc, 19 routes => total 0 => small
        m_low = {"source_files": 149, "loc": 14999, "routes": 19, "peers": 0, "gaps": 14}
        adv_low = engine_advisor.advise(m_low, subagents=True)
        self.assertEqual(adv_low["total"], 0)
        self.assertEqual(adv_low["size_class"], "small")

        # Upper boundaries: 401 files (2), 50001 loc (2), 61 routes (2) => total 6 => large => multi
        m_high = {"source_files": 401, "loc": 50001, "routes": 61, "peers": 0, "gaps": 0}
        adv_high = engine_advisor.advise(m_high, subagents=True)
        self.assertEqual(adv_high["total"], 6)
        self.assertEqual(adv_high["size_class"], "large")
        self.assertEqual(adv_high["recommendation"], "multi")

    def test_collect_metrics_excludes_vendor_dirs_and_cli_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src"
            src.mkdir()
            (src / "App.tsx").write_text("export const App = () => <div>Hello</div>;\n" * 10, encoding="utf-8")
            (src / "api.ts").write_text("export function fetchItems() { return []; }\n" * 5, encoding="utf-8")

            nm = root / "node_modules" / "pkg"
            nm.mkdir(parents=True)
            (nm / "index.js").write_text("console.log('ignored');\n" * 500, encoding="utf-8")

            dist = root / "dist"
            dist.mkdir()
            (dist / "bundle.js").write_text("console.log('ignored');\n" * 500, encoding="utf-8")

            gap_stub = {
                "roots": {"root": str(root), "peers": []},
                "routes": {"declared": [{"path": "/"}, {"path": "/settings"}], "links": []},
                "summary": {
                    "stub_pages": 2,
                    "stub_actions": 1,
                    "broken_routes": 1,
                    "orphan_endpoints": 3,
                    "orphan_fields": 0,
                    "todo_markers": 99,
                },
            }
            metrics = engine_advisor.collect_metrics(root, peers=[], gap_data=gap_stub)
            self.assertEqual(metrics["source_files"], 2)
            self.assertEqual(metrics["loc"], 15)
            self.assertEqual(metrics["routes"], 2)
            self.assertEqual(metrics["peers"], 0)
            self.assertEqual(metrics["gaps"], 7)

            gap_file = root / "gap.json"
            gap_file.write_text(json.dumps(gap_stub), encoding="utf-8")
            res = subprocess.run(
                [
                    sys.executable,
                    str(ADVISOR_SCRIPT),
                    "--root",
                    str(root),
                    "--gap-json",
                    str(gap_file),
                    "--subagents",
                    "yes",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            payload = json.loads(res.stdout)
            self.assertEqual(payload["schema"], "feature-architect/engine-advice@1")
            self.assertEqual(payload["metrics"]["source_files"], 2)


if __name__ == "__main__":
    unittest.main()
