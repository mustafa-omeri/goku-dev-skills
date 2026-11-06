#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression & ecosystem contract tests for the global `feature-architect` skill."""
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
SCANNER_TESTS = SKILL_DIR / "scripts" / "tests" / "test_gap_scanner.py"
DASHBOARD_DIR = ROOT / ".agent" / "skills" / "frontend-design" / "dashboard-theme"
TRIGGER_RULE = ROOT / ".agent" / "rules" / "skill-trigger-routing.md"
AGENTS_MD = ROOT / ".agent" / "AGENTS.md"
CLI_JS = ROOT / "bin" / "cli.js"
GEN_CATALOG = ROOT / "scripts" / "generate_skills_catalog.py"
CATALOG_HTML = ROOT / ".agent" / "skills-catalog.html"

FORBIDDEN_PROJECT_RE = re.compile(
    r"\bocai\b|FEProjectv1|FEProject\b|bookmarkManagerProject|bookmarkManager|\bkalansure\b",
    re.IGNORECASE,
)


class FeatureArchitectContractTests(unittest.TestCase):
    """Verifies unit tests, global purity, dashboard catalog, and registration points."""

    def test_01_gap_scanner_unit_suite_passes(self):
        self.assertTrue(SCANNER_TESTS.is_file(), f"Missing unit test file: {SCANNER_TESTS}")
        res = subprocess.run(
            [sys.executable, str(SCANNER_TESTS)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(
            res.returncode,
            0,
            f"gap_scanner unit tests failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}",
        )

    def test_02_skill_files_exist(self):
        required = [
            SKILL_DIR / "SKILL.md",
            SKILL_DIR / "scripts" / "gap_scanner.py",
            SKILL_DIR / "scripts" / "council_merger.py",
            SKILL_DIR / "scripts" / "engine_advisor.py",
            SKILL_DIR / "schemas" / "council-contract.schema.json",
            SKILL_DIR / "references" / "council-protocol.md",
            SKILL_DIR / "references" / "report-template.md",
            SKILL_DIR / "references" / "dashboard-matching.md",
            SKILL_DIR / "references" / "theme-skeleton-matching.md",
            SKILL_DIR / "agents" / "01-snr-product-owner.md",
            SKILL_DIR / "agents" / "02-snr-software-architect.md",
            SKILL_DIR / "agents" / "03-principal-ui-ux-specialist.md",
            SKILL_DIR / "agents" / "04-snr-seo-specialist.md",
            SKILL_DIR / "agents" / "05-snr-growth-marketing.md",
            SKILL_DIR / "agents" / "06-snr-qa-security-auditor.md",
        ]
        missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
        self.assertEqual(missing, [], f"Missing feature-architect files: {missing}")

    def test_03_global_purity_no_project_names_in_skill(self):
        """Enforces user requirement: 100% global, zero hardcoded project names."""
        self.assertTrue((SKILL_DIR / "SKILL.md").is_file(), "SKILL.md missing")
        violations = []
        for path in sorted(SKILL_DIR.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix not in {".md", ".py", ".json"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for m in FORBIDDEN_PROJECT_RE.finditer(text):
                violations.append(f"{path.relative_to(ROOT)}: contains project name {m.group(0)!r}")
        self.assertEqual(violations, [], "\n".join(violations))

    def test_04_dashboard_catalog_has_18_verified_entries(self):
        catalog_path = DASHBOARD_DIR / "catalog.json"
        self.assertTrue(catalog_path.is_file(), f"Missing {catalog_path}")
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        self.assertEqual(data.get("schema"), "dashboard-theme-catalog@1")
        themes = data.get("themes", [])
        self.assertEqual(len(themes), 18, f"Expected 18 dashboard themes, got {len(themes)}")
        required_keys = {"id", "file", "title", "archetype", "density", "surface", "layout", "widgets", "best_for"}
        for entry in themes:
            missing = required_keys - set(entry.keys())
            self.assertEqual(missing, set(), f"{entry.get('id')} missing keys: {missing}")
            webp = DASHBOARD_DIR / entry["file"]
            self.assertTrue(webp.is_file(), f"Referenced image missing: {webp}")

    def test_05_trigger_routing_and_agents_registration(self):
        text = TRIGGER_RULE.read_text(encoding="utf-8")
        self.assertIn("`feature-architect`", text)
        self.assertIn("`/feature-architect`", text)
        self.assertIn("`skills/feature-architect/SKILL.md`", text)
        agents_text = AGENTS_MD.read_text(encoding="utf-8")
        self.assertIn("feature-architect", agents_text)

    def test_06_cli_and_catalog_registration(self):
        cli_text = CLI_JS.read_text(encoding="utf-8")
        self.assertIn("'feature-architect':", cli_text)
        gen_text = GEN_CATALOG.read_text(encoding="utf-8")
        self.assertIn('"/feature-architect"', gen_text)
        self.assertIn('"feature-architect"', gen_text)
        html_text = CATALOG_HTML.read_text(encoding="utf-8")
        self.assertIn("feature-architect", html_text)
        self.assertIn("/feature-architect", html_text)


if __name__ == "__main__":
    unittest.main()
