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
        installed_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()}
        self.assertEqual(len(installed_skills), 21)


if __name__ == "__main__":
    unittest.main()
