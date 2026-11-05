#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression & contract tests for Multi-Tool Plan Mode & Unified Theme/Component Skeleton Integration (S2-06)."""
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
PLAN_TEMPLATE = ROOT / ".agent" / "templates" / "PLAN.template.md"
DEV_WORKFLOW = ROOT / ".agent" / "rules" / "development-workflow.md"
SPRINT_WORKFLOW = ROOT / ".agent" / "rules" / "sprint-delivery-workflow.md"
AGENTS_MD = ROOT / ".agent" / "AGENTS.md"
FA_SKILL = ROOT / ".agent" / "skills" / "feature-architect" / "SKILL.md"
FA_REPORT_TEMPLATE = ROOT / ".agent" / "skills" / "feature-architect" / "references" / "report-template.md"
THEME_SKELETON_REF = ROOT / ".agent" / "skills" / "feature-architect" / "references" / "theme-skeleton-matching.md"
GET_COMPONENT_SCRIPT = ROOT / ".agent" / "skills" / "frontend-design" / "scripts" / "get_component.py"

FORBIDDEN_PROJECT_RE = re.compile(
    r"\bocai\b|FEProjectv1|FEProject\b|bookmarkManagerProject|bookmarkManager|\bkalansure\b",
    re.IGNORECASE,
)


class ThemeSkeletonIntegrationTests(unittest.TestCase):
    """Verifies that /plan and /feature-architect connect to the full theme & component skeleton across all tools."""

    def test_01_plan_template_has_theme_skeleton_contract_and_multi_tool_support(self):
        self.assertTrue(PLAN_TEMPLATE.is_file(), f"Missing {PLAN_TEMPLATE}")
        text = PLAN_TEMPLATE.read_text(encoding="utf-8")

        # Multi-tool header support
        for tool_name in ("Antigravity IDE", "Antigravity CLI", "Claude Code", "OpenCode"):
            self.assertIn(tool_name, text, f"PLAN.template.md must support {tool_name}")

        # Theme & Component Skeleton section
        self.assertIn("Tema ve Bileşen İskeleti Sözleşmesi", text)
        self.assertIn("16", text)
        self.assertIn("55+", text)
        self.assertIn("18", text)
        self.assertIn("get_component.py", text)
        self.assertIn("Skeleton", text)

    def test_02_feature_architect_skill_references_unified_theme_skeleton_and_multi_tool(self):
        self.assertTrue(FA_SKILL.is_file(), f"Missing {FA_SKILL}")
        text = FA_SKILL.read_text(encoding="utf-8")

        self.assertIn("theme-skeleton-matching.md", text)
        self.assertIn("get_component.py", text)
        for tool_name in ("Antigravity IDE", "Antigravity CLI", "Claude Code", "OpenCode"):
            self.assertIn(tool_name, text, f"feature-architect/SKILL.md must support {tool_name}")
        self.assertIn(".agent/plans/", text)

    def test_03_theme_skeleton_matching_reference_exists_and_covers_all_8_categories_and_16_themes(self):
        self.assertTrue(
            THEME_SKELETON_REF.is_file(),
            f"Missing unified reference: {THEME_SKELETON_REF}",
        )
        text = THEME_SKELETON_REF.read_text(encoding="utf-8")

        # All 8 component categories
        categories = ("accordions", "cards", "footers", "logins", "menus", "navbars", "parallax", "sidebars")
        for cat in categories:
            self.assertIn(cat, text, f"theme-skeleton-matching.md missing component category: {cat}")

        # 16 Official Themes & Living Surface
        self.assertIn("Obsidian Velvet", text)
        self.assertIn("Warm Alabaster", text)
        self.assertIn("themes.css", text)
        self.assertIn("Living Surface", text)

        # 18 Dashboards & Skeleton Cassettes & CLI Helpers
        self.assertIn("catalog.json", text)
        self.assertIn("get_component.py", text)
        self.assertIn("generate_auth_hero.py", text)
        self.assertIn("Zero-CLS", text)

        # Multi-tool parity
        for tool_name in ("Antigravity IDE", "Antigravity CLI", "Claude Code", "OpenCode"):
            self.assertIn(tool_name, text, f"theme-skeleton-matching.md missing {tool_name}")

    def test_04_workflows_and_agents_enforce_multi_tool_and_theme_skeleton(self):
        dev_text = DEV_WORKFLOW.read_text(encoding="utf-8")
        for item in ("Antigravity IDE", "Antigravity CLI", "Claude Code", "OpenCode", ".agent/plans/", "get_component.py", "theme-skeleton-matching.md"):
            self.assertIn(item, dev_text, f"development-workflow.md missing: {item}")

        sprint_text = SPRINT_WORKFLOW.read_text(encoding="utf-8")
        for tool_name in ("Antigravity IDE", "Antigravity CLI", "Claude Code", "OpenCode"):
            self.assertIn(tool_name, sprint_text, f"sprint-delivery-workflow.md missing: {tool_name}")

        agents_text = AGENTS_MD.read_text(encoding="utf-8")
        for tool_name in ("Antigravity CLI", "Claude Code", "OpenCode"):
            self.assertIn(tool_name, agents_text, f"AGENTS.md missing: {tool_name}")

    def test_05_get_component_cli_operates_agnostically(self):
        self.assertTrue(GET_COMPONENT_SCRIPT.is_file(), f"Missing {GET_COMPONENT_SCRIPT}")
        res = subprocess.run(
            [sys.executable, str(GET_COMPONENT_SCRIPT), "--list"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res.returncode, 0, f"get_component.py --list failed: {res.stderr}")
        for cat in ("logins", "sidebars", "cards", "footers"):
            self.assertIn(cat, res.stdout.lower())

    def test_06_global_purity_no_project_names(self):
        targets = [
            PLAN_TEMPLATE,
            DEV_WORKFLOW,
            FA_SKILL,
            FA_REPORT_TEMPLATE,
            THEME_SKELETON_REF,
        ]
        violations = []
        for path in targets:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for m in FORBIDDEN_PROJECT_RE.finditer(text):
                violations.append(f"{path.relative_to(ROOT)}: contains project name {m.group(0)!r}")
        self.assertEqual(violations, [], "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
