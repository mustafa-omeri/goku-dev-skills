#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test CLI Surgical Update (npx goku-dev-skills update).

Verifies:
1. Surgical Scope: Updates only already-installed skills, rules, and templates. Never downloads/copies uninstalled skills.
2. Minimal Mode Protection: Frontend minimal installs exclude component-themes, and update continues to bypass them.
3. Check / Dry-Run: `--check` accurately detects modified files without writing to disk.
4. Content Sync: Modified or outdated installed files are properly updated to match source.
5. Project Block Preservation: `## Proje Bazlı Ek Kurallar` in AGENTS.md is strictly preserved during update.
6. Metadata Maintenance: `.agent/goku.json` tracks versions and timestamps.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = ROOT / "bin" / "cli.js"


class TestCliUpdate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="goku_test_update_"))

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_surgical_update_preserves_installed_scope(self):
        # 1. Initialize backend profile in temp directory
        target_dir = self.temp_dir / "be_proj"
        init_cmd = ["node", str(CLI_PATH), "init", "-p", "backend", "--dest", str(target_dir)]
        res = subprocess.run(init_cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0, f"Init failed: {res.stderr}")

        skills_dir = target_dir / ".agent" / "skills"
        initial_skills = sorted(d.name for d in skills_dir.iterdir() if d.is_dir())
        self.assertIn("musgoku", initial_skills)
        self.assertIn("my-idea", initial_skills)
        self.assertNotIn("frontend-design", initial_skills)
        self.assertNotIn("canvas-design", initial_skills)

        # 2. Modify one installed skill file to simulate outdated content
        test_skill_md = skills_dir / "my-idea" / "SKILL.md"
        self.assertTrue(test_skill_md.is_file())
        test_skill_md.write_text("--- \nname: my-idea\noutdated: true\n---", encoding="utf-8")

        # 3. Add custom project-specific rule to AGENTS.md
        agents_md = target_dir / ".agent" / "AGENTS.md"
        custom_block = "\n\n## Proje Bazlı Ek Kurallar\n\n### Özel Backend Kuralı\nBu kural asla silinmemelidir."
        agents_md.write_text(agents_md.read_text(encoding="utf-8") + custom_block, encoding="utf-8")

        # 4. Run update with --check (Dry-Run)
        check_cmd = ["node", str(CLI_PATH), "update", "--check", "--dest", str(target_dir)]
        check_res = subprocess.run(check_cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(check_res.returncode, 0, f"Check failed: {check_res.stderr}")
        self.assertIn(".agent/skills/my-idea/SKILL.md", check_res.stdout)
        self.assertIn("Check complete", check_res.stdout)

        # Verify dry-run did NOT touch the file
        self.assertIn("outdated: true", test_skill_md.read_text(encoding="utf-8"))

        # 5. Run actual update
        update_cmd = ["node", str(CLI_PATH), "update", "--dest", str(target_dir)]
        update_res = subprocess.run(update_cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(update_res.returncode, 0, f"Update failed: {update_res.stderr}")
        self.assertIn(".agent/skills/my-idea/SKILL.md", update_res.stdout)
        self.assertIn("updated successfully", update_res.stdout)

        # 6. Verify file was properly updated to source
        source_skill_md = ROOT / ".agent" / "skills" / "my-idea" / "SKILL.md"
        self.assertEqual(test_skill_md.read_text(encoding="utf-8"), source_skill_md.read_text(encoding="utf-8"))

        # 7. CRITICAL: Verify NO uninstalled skills were copied/downloaded
        updated_skills = sorted(d.name for d in skills_dir.iterdir() if d.is_dir())
        self.assertEqual(updated_skills, initial_skills, "Update must not add uninstalled skills!")
        self.assertNotIn("frontend-design", updated_skills)
        self.assertNotIn("canvas-design", updated_skills)

        # 8. Verify project-specific rules in AGENTS.md were strictly preserved
        updated_agents_content = agents_md.read_text(encoding="utf-8")
        self.assertIn("## Proje Bazlı Ek Kurallar", updated_agents_content)
        self.assertIn("### Özel Backend Kuralı", updated_agents_content)
        self.assertIn("Bu kural asla silinmemelidir.", updated_agents_content)

        # 9. Verify goku.json metadata exists and was updated
        goku_json_path = target_dir / ".agent" / "goku.json"
        self.assertTrue(goku_json_path.is_file())
        meta = json.loads(goku_json_path.read_text(encoding="utf-8"))
        self.assertEqual(meta["profile"], "backend")
        self.assertIn("lastUpdated", meta)

    def test_minimal_frontend_update_bypasses_heavy_themes(self):
        # 1. Initialize frontend minimal profile
        target_dir = self.temp_dir / "fe_proj"
        init_cmd = ["node", str(CLI_PATH), "init", "-p", "frontend", "-m", "--dest", str(target_dir)]
        res = subprocess.run(init_cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0, f"Init minimal failed: {res.stderr}")

        fe_dir = target_dir / ".agent" / "skills" / "frontend-design"
        self.assertTrue(fe_dir.is_dir())
        self.assertFalse((fe_dir / "component-themes").exists(), "Minimal init must exclude component-themes")

        # 2. Run update on minimal frontend project
        update_cmd = ["node", str(CLI_PATH), "update", "--dest", str(target_dir)]
        update_res = subprocess.run(update_cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(update_res.returncode, 0, f"Update minimal failed: {update_res.stderr}")

        # 3. Verify component-themes was NOT re-introduced during update
        self.assertFalse((fe_dir / "component-themes").exists(), "Update must respect minimal mode and not fetch 55 themes")


if __name__ == "__main__":
    unittest.main()
