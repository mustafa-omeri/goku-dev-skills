#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Global Antigravity CLI Plugin Sync (scripts/sync_agy_global.py & bin/cli.js)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYNC_SCRIPT = ROOT / "scripts" / "sync_agy_global.py"
CLI_PATH = ROOT / "bin" / "cli.js"


class TestAgyGlobalPlugin(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="goku_agy_plugin_"))
        self.plugin_dir = self.temp_dir / "plugins" / "goku-dev-skills"
        self.global_skills_dir = self.temp_dir / "skills"

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_sync_creates_valid_plugin_within_rule_budget(self):
        self.assertTrue(SYNC_SCRIPT.is_file(), f"Missing sync script: {SYNC_SCRIPT}")
        res = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), "--dest", str(self.plugin_dir)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res.returncode, 0, f"Sync failed: {res.stderr}\n{res.stdout}")

        # 1. plugin.json contract
        manifest_path = self.plugin_dir / "plugin.json"
        self.assertTrue(manifest_path.is_file(), "plugin.json must exist")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("name"), "goku-dev-skills")
        self.assertTrue(manifest.get("version"))

        # 2. All 50 skills synced
        src_skills = {d.name for d in (ROOT / ".agent" / "skills").iterdir() if d.is_dir()}
        dst_skills = {d.name for d in (self.plugin_dir / "skills").iterdir() if d.is_dir()}
        self.assertEqual(dst_skills, src_skills)

        # Full package includes component-themes
        self.assertTrue((self.plugin_dir / "skills" / "frontend-design" / "component-themes").is_dir())

        # 3. All 20 templates synced
        src_templates = {f.name for f in (ROOT / ".agent" / "templates").iterdir() if f.is_file()}
        dst_templates = {f.name for f in (self.plugin_dir / "templates").iterdir() if f.is_file()}
        self.assertEqual(dst_templates, src_templates)

        # 4. Rules budget guard: rules/ MUST contain ONLY AGENTS.md and be < 24,000 bytes
        rules_dir = self.plugin_dir / "rules"
        self.assertTrue(rules_dir.is_dir())
        rule_files = list(rules_dir.iterdir())
        self.assertEqual([f.name for f in rule_files], ["AGENTS.md"])
        agents_bytes = (rules_dir / "AGENTS.md").stat().st_size
        self.assertLess(agents_bytes, 24000, f"rules/AGENTS.md exceeds 24KB cap: {agents_bytes}")
        agents_text = (rules_dir / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("goku-dev-skills", agents_text)
        self.assertIn("Scope Guard", agents_text)

        # 5. Full 22 rules preserved on-demand under references/rules/
        src_rules = {f.name for f in (ROOT / ".agent" / "rules").glob("*.md")}
        ref_rules = {f.name for f in (self.plugin_dir / "references" / "rules").glob("*.md")}
        self.assertEqual(ref_rules, src_rules)

    def test_check_mode_does_not_write_and_minimal_excludes_themes(self):
        res_check = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), "--dest", str(self.plugin_dir), "--check"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res_check.returncode, 0, res_check.stderr)
        self.assertFalse(self.plugin_dir.exists(), "--check must not create target directory")

        res_min = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), "--dest", str(self.plugin_dir), "--minimal"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res_min.returncode, 0, res_min.stderr)
        self.assertFalse((self.plugin_dir / "skills" / "frontend-design" / "component-themes").exists())

    def test_dedupe_global_skills_backs_up_and_removes_duplicates(self):
        dup_skill = self.global_skills_dir / "git-release-workflow"
        dup_skill.mkdir(parents=True, exist_ok=True)
        (dup_skill / "SKILL.md").write_text("old copy", encoding="utf-8")
        backup_dir = self.temp_dir / "backups"

        res = subprocess.run(
            [
                sys.executable,
                str(SYNC_SCRIPT),
                "--dest",
                str(self.plugin_dir),
                "--global-skills-dir",
                str(self.global_skills_dir),
                "--backup-dir",
                str(backup_dir),
                "--dedupe-global-skills",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertFalse(dup_skill.exists(), "Duplicate global skill should be removed")
        self.assertTrue(any(backup_dir.glob("global-skills-git-release-workflow-*")))

    def test_cli_help_documents_sync_agy_and_dry_run_works(self):
        help_res = subprocess.run(
            ["node", str(CLI_PATH), "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(help_res.returncode, 0)
        self.assertIn("sync-agy", help_res.stdout)

        cli_res = subprocess.run(
            ["node", str(CLI_PATH), "sync-agy", "--check", "--dest", str(self.plugin_dir)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(cli_res.returncode, 0, f"CLI sync-agy failed: {cli_res.stderr}\n{cli_res.stdout}")
        self.assertFalse(self.plugin_dir.exists())


if __name__ == "__main__":
    unittest.main()
