#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for scaffold_tour.py script in onboarding-tour skill."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import scaffold_tour


class TestScaffoldTour(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_tour_"))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_generates_driverjs_by_default(self):
        """Varsayılan olarak driver.js import ve hook içeren kod üretmeli."""
        code = scaffold_tour.generate_scaffold("driverjs", "dashboard")
        self.assertIn("import { driver, DriveStep, Config } from 'driver.js'", code)
        self.assertIn("useDashboardTour", code)
        self.assertIn("onboarding_completed_dashboard", code)
        self.assertIn("DEFAULT_DASHBOARD_STEPS", code)

    def test_generates_joyride_template(self):
        """joyride seçildiğinde React Joyride bileşeni üretmeli."""
        code = scaffold_tour.generate_scaffold("joyride", "onboarding-wizard")
        self.assertIn("import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride'", code)
        self.assertIn("export function OnboardingWizardTour", code)
        self.assertIn("onboarding_completed_onboarding-wizard", code)

    def test_generates_coachmark_template(self):
        """coachmark seçildiğinde sıfır bağımlılıklı pulsing beacon bileşeni üretmeli."""
        code = scaffold_tour.generate_scaffold("coachmark", "settings-tip")
        self.assertIn("export function CoachmarkBeacon", code)
        self.assertIn("animate-ping", code)

    def test_custom_storage_key(self):
        """Özel storageKey verildiğinde şablona yansımalı."""
        code = scaffold_tour.generate_scaffold(
            "driverjs", "app-tour", storage_key="custom_tour_v2_done"
        )
        self.assertIn("custom_tour_v2_done", code)

    def test_cli_output_file(self):
        """--output parametresi ile dosyaya yazım yapılabilmeli."""
        out_file = self.tmp_dir / "useTour.ts"
        ret = scaffold_tour.main([
            "--engine", "driverjs",
            "--name", "header-nav",
            "--output", str(out_file),
            "--json",
        ])
        self.assertEqual(ret, 0)
        self.assertTrue(out_file.is_file())
        content = out_file.read_text(encoding="utf-8")
        self.assertIn("useHeaderNavTour", content)


if __name__ == "__main__":
    unittest.main()
