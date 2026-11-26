#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test CLI Profile-Based Modular Installation.

Verifies:
1. Backend profile installs only backend skills & rules, drops UI/theme clutter, and passes rules_gates.py.
2. Frontend profile in minimal mode excludes component-themes and passes rules_gates.py.
3. Fullstack profile installs full suite.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = ROOT / "bin" / "cli.js"


class TestCliProfiles(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="goku_test_profile_"))

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_backend_profile_installation(self):
        dest = self.temp_dir / "be_proj"
        cmd = ["node", str(CLI_PATH), "init", "-p", "backend", "--dest", str(dest)]
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0, f"CLI init backend failed: {res.stderr}")

        # Check skills
        skills_dir = dest / ".agent" / "skills"
        self.assertTrue(skills_dir.is_dir())
        installed_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()}
        self.assertIn("musgoku", installed_skills)
        self.assertIn("git-release-workflow", installed_skills)
        self.assertNotIn("frontend-design", installed_skills)
        self.assertNotIn("ui-ux-pro-max", installed_skills)
        self.assertNotIn("canvas-design", installed_skills)

        # Check AGENTS.md gate table
        agents_md = (dest / ".agent" / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Backend / API dokümantasyonu", agents_md)
        self.assertIn("Backend / Veritabanı migration", agents_md)
        self.assertNotIn("Frontend / bundle bütçesi", agents_md)
        self.assertNotIn("Tasarım / zanaat tabanı", agents_md)

        # Run rules_gates.py in target
        gate_script = dest / ".agent" / "skills" / "musgoku" / "scripts" / "rules_gates.py"
        self.assertTrue(gate_script.exists())
        gate_res = subprocess.run([sys.executable, str(gate_script), "--strict"],
                                  cwd=str(dest), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(gate_res.returncode, 0, f"rules_gates failed in backend: {gate_res.stdout}\n{gate_res.stderr}")

    def test_frontend_minimal_profile_installation(self):
        dest = self.temp_dir / "fe_proj"
        cmd = ["node", str(CLI_PATH), "init", "-p", "frontend", "-m", "--dest", str(dest)]
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0, f"CLI init frontend minimal failed: {res.stderr}")

        # Check component-themes is excluded in minimal mode
        fe_skill_dir = dest / ".agent" / "skills" / "frontend-design"
        self.assertTrue(fe_skill_dir.is_dir())
        self.assertFalse((fe_skill_dir / "component-themes").exists())

        # Check skills
        skills_dir = dest / ".agent" / "skills"
        installed_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()}
        self.assertIn("ui-ux-pro-max", installed_skills)
        self.assertIn("react-best-practices", installed_skills)
        self.assertIn("ui-styling", installed_skills)

        # Check AGENTS.md gate table
        agents_md = (dest / ".agent" / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Frontend / bundle bütçesi", agents_md)
        self.assertIn("Tasarım / zanaat tabanı", agents_md)
        self.assertNotIn("Backend / API dokümantasyonu", agents_md)

        # Run rules_gates.py in target
        gate_script = dest / ".agent" / "skills" / "musgoku" / "scripts" / "rules_gates.py"
        self.assertTrue(gate_script.exists())
        gate_res = subprocess.run([sys.executable, str(gate_script), "--strict"],
                                  cwd=str(dest), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(gate_res.returncode, 0, f"rules_gates failed in frontend minimal: {gate_res.stdout}\n{gate_res.stderr}")

    def test_fullstack_profile_installation(self):
        dest = self.temp_dir / "full_proj"
        cmd = ["node", str(CLI_PATH), "init", "-p", "fullstack", "--dest", str(dest)]
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0, f"CLI init fullstack failed: {res.stderr}")

        skills_dir = dest / ".agent" / "skills"
        installed_skills = {d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}
        source_skills = len([d for d in (ROOT / ".agent" / "skills").iterdir() if d.is_dir() and (d / "SKILL.md").is_file()])
        self.assertEqual(len(installed_skills), source_skills)

    def test_opencode_add_skill_and_sync_opencode(self):
        # 1. Single skill via --agent opencode writes to ./.opencode/skills/<skill>
        proj_dir = self.temp_dir / "oc_proj"
        proj_dir.mkdir(parents=True, exist_ok=True)
        add_res = subprocess.run(
            ["node", str(CLI_PATH), "add", "tdd", "--agent", "opencode"],
            cwd=str(proj_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(add_res.returncode, 0, f"add --agent opencode failed: {add_res.stderr}")
        self.assertTrue((proj_dir / ".opencode" / "skills" / "tdd" / "SKILL.md").is_file())

        # 2. sync-opencode --check does not write to disk
        oc_base = self.temp_dir / "oc_global"
        chk_res = subprocess.run(
            ["node", str(CLI_PATH), "sync-opencode", "--dest", str(oc_base), "--check"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(chk_res.returncode, 0, f"sync-opencode --check failed: {chk_res.stderr}")
        self.assertFalse(oc_base.exists())

        # 3. sync-opencode --minimal installs all skills (without component-themes), rules, templates, and AGENTS.md
        sync_res = subprocess.run(
            ["node", str(CLI_PATH), "sync-opencode", "--dest", str(oc_base), "--minimal"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(sync_res.returncode, 0, f"sync-opencode failed: {sync_res.stderr}")
        src_skills = {d.name for d in (ROOT / ".agent" / "skills").iterdir() if d.is_dir()}
        dst_skills = {d.name for d in (oc_base / "skills").iterdir() if d.is_dir()}
        self.assertEqual(dst_skills, src_skills)
        self.assertFalse((oc_base / "skills" / "frontend-design" / "component-themes").exists())
        self.assertTrue((oc_base / "references" / "rules" / "tdd.md").is_file() or (oc_base / "references" / "rules" / "development-workflow.md").is_file())
        self.assertTrue((oc_base / "AGENTS.md").is_file())
        self.assertLess((oc_base / "AGENTS.md").stat().st_size, 24000)

        # 4. Existing custom AGENTS.md is preserved (writes GOKU_AGENTS.md instead)
        custom_oc = self.temp_dir / "oc_custom"
        custom_oc.mkdir(parents=True, exist_ok=True)
        custom_agents = custom_oc / "AGENTS.md"
        custom_agents.write_text("# My Custom OpenCode Rules\nDo not overwrite.", encoding="utf-8")
        preserve_res = subprocess.run(
            ["node", str(CLI_PATH), "sync-opencode", "--dest", str(custom_oc), "--minimal"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(preserve_res.returncode, 0, f"sync-opencode preserve failed: {preserve_res.stderr}")
        self.assertIn("My Custom OpenCode Rules", custom_agents.read_text(encoding="utf-8"))
        self.assertTrue((custom_oc / "GOKU_AGENTS.md").is_file())

    def test_profiles_and_component_themes_parity_with_disk(self):
        import re

        cli_text = CLI_PATH.read_text(encoding="utf-8")
        # 1. COMPONENT_THEMES must match all themes on disk (56 themes)
        disk_themes = {
            p.parent.name
            for p in (ROOT / ".agent" / "skills" / "frontend-design" / "component-themes").rglob("*.html")
        }
        ct_match = re.search(r"const COMPONENT_THEMES = \{(.*?)\n\};", cli_text, re.S)
        self.assertIsNotNone(ct_match)
        cat_keys = set(re.findall(r"^\s+'([a-z0-9-]+)':", ct_match.group(1), re.M))
        cli_themes = set(re.findall(r"'([a-z0-9-]+)'", ct_match.group(1))) - cat_keys
        self.assertEqual(disk_themes - cli_themes, set(), "Diskteki tum component temalari CLI'da bulunmali")

        # 2. Backend & Frontend profiles must include core verification/planning skills, rules & templates
        be_dest = self.temp_dir / "be_parity"
        fe_dest = self.temp_dir / "fe_parity"
        subprocess.run(["node", str(CLI_PATH), "init", "-p", "backend", "--dest", str(be_dest)], cwd=str(ROOT), check=True, capture_output=True)
        subprocess.run(["node", str(CLI_PATH), "init", "-p", "frontend", "-m", "--dest", str(fe_dest)], cwd=str(ROOT), check=True, capture_output=True)

        for dest in (be_dest, fe_dest):
            skills = {d.name for d in (dest / ".agent" / "skills").iterdir() if d.is_dir()}
            rules = {f.name for f in (dest / ".agent" / "rules").glob("*.md")}
            templates = {f.name for f in (dest / ".agent" / "templates").iterdir() if f.is_file()}
            for req_skill in ("verify-last", "verify-sprint", "spec-reconciler"):
                self.assertIn(req_skill, skills)
            for req_rule in ("aviation-documentation-standard.md", "cognitive-counsel-framework.md"):
                self.assertIn(req_rule, rules)
            for req_tpl in ("PLAN.template.md", "ACCEPTANCE_TEST_SPEC.template.md", "DEPLOYMENT_PLAN.template.md", "DEPLOYMENT_TARGET.template.yaml"):
                self.assertIn(req_tpl, templates)

        fe_templates = {f.name for f in (fe_dest / ".agent" / "templates").iterdir() if f.is_file()}
        self.assertIn("KULLANICI_REHBERI.template.html", fe_templates)
        self.assertIn("rehber_design.md", fe_templates)


if __name__ == "__main__":
    unittest.main()
