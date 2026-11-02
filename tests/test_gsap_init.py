#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_gsap_init.py - TDD Seam Tests for GSAP & ScrollSmoother Integration Engine
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

# Ensure .agent/skills/ui-ux-pro-max/scripts is in python path
ROOT = Path(__file__).resolve().parent.parent
GSAP_SCRIPTS_DIR = ROOT / ".agent" / "skills" / "ui-ux-pro-max" / "scripts"
if str(GSAP_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(GSAP_SCRIPTS_DIR))

try:
    from gsap_init import (
        check_suitability,
        detect_package_manager,
        scaffold_gsap,
        build_install_command,
        get_vite_cache_notice,
    )
except ImportError:
    # Expected in Red Loop before minimal code is written
    check_suitability = None
    detect_package_manager = None
    scaffold_gsap = None
    build_install_command = None
    get_vite_cache_notice = None


class TestGSAPInitEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="gsap_test_"))

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_seam_import(self):
        """Test that gsap_init engine is importable."""
        self.assertIsNotNone(
            check_suitability,
            "gsap_init module could not be imported (RED phase)",
        )

    def test_02_check_suitability_react_vite(self):
        """Test suitability detection for a Vite + React web project."""
        pkg_json = self.test_dir / "package.json"
        pkg_json.write_text(
            json.dumps({
                "name": "my-vite-app",
                "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0"},
                "devDependencies": {"vite": "^5.0.0"}
            }),
            encoding="utf-8"
        )
        is_suitable, reason, meta = check_suitability(self.test_dir)
        self.assertTrue(is_suitable)
        self.assertEqual(meta.get("framework"), "react")
        self.assertTrue(meta.get("is_vite"))

    def test_03_check_suitability_reject_backend(self):
        """Test suitability rejection for a pure backend or empty project."""
        # Empty dir
        is_suitable, reason, meta = check_suitability(self.test_dir)
        self.assertFalse(is_suitable)
        self.assertIn("package.json", reason)

        # Python backend only
        (self.test_dir / "main.py").write_text("print('hello')", encoding="utf-8")
        is_suitable, reason, meta = check_suitability(self.test_dir)
        self.assertFalse(is_suitable)

    def test_04_detect_package_manager(self):
        """Test accurate lockfile detection for pnpm, yarn, bun, and npm."""
        # pnpm
        (self.test_dir / "pnpm-lock.yaml").write_text("", encoding="utf-8")
        self.assertEqual(detect_package_manager(self.test_dir), "pnpm")
        (self.test_dir / "pnpm-lock.yaml").unlink()

        # yarn
        (self.test_dir / "yarn.lock").write_text("", encoding="utf-8")
        self.assertEqual(detect_package_manager(self.test_dir), "yarn")
        (self.test_dir / "yarn.lock").unlink()

        # bun
        (self.test_dir / "bun.lockb").write_text("", encoding="utf-8")
        self.assertEqual(detect_package_manager(self.test_dir), "bun")
        (self.test_dir / "bun.lockb").unlink()

        # fallback to npm
        (self.test_dir / "package-lock.json").write_text("", encoding="utf-8")
        self.assertEqual(detect_package_manager(self.test_dir), "npm")

    def test_05_build_install_command(self):
        """Test building installation command for React and non-React projects."""
        cmd_pnpm_react = build_install_command("pnpm", framework="react")
        self.assertIn("pnpm add gsap @gsap/react", cmd_pnpm_react)

        cmd_npm_vanilla = build_install_command("npm", framework="vanilla")
        self.assertIn("npm install gsap", cmd_npm_vanilla)
        self.assertNotIn("@gsap/react", cmd_npm_vanilla)

    def test_06_scaffold_react_ts_files(self):
        """Test scaffolding src/lib/gsap.ts and src/components/SmoothScroll.tsx."""
        pkg_json = self.test_dir / "package.json"
        pkg_json.write_text(
            json.dumps({"name": "test-app", "dependencies": {"react": "^18.0.0"}}),
            encoding="utf-8"
        )
        (self.test_dir / "src").mkdir(parents=True)

        created_files = scaffold_gsap(self.test_dir, framework="react", is_typescript=True)
        self.assertGreater(len(created_files), 0)

        # Check lib file
        lib_file = self.test_dir / "src" / "lib" / "gsap.ts"
        self.assertTrue(lib_file.exists(), "src/lib/gsap.ts must be created")
        content = lib_file.read_text(encoding="utf-8")
        self.assertIn("gsap.registerPlugin", content)
        self.assertIn("ScrollTrigger", content)
        self.assertIn("prefers-reduced-motion", content)
        self.assertIn("autoScrollTo", content)

        # Check component wrapper
        comp_file = self.test_dir / "src" / "components" / "SmoothScroll.tsx"
        self.assertTrue(comp_file.exists(), "SmoothScroll.tsx must be created")
        comp_content = comp_file.read_text(encoding="utf-8")
        self.assertIn("smooth-wrapper", comp_content)
        self.assertIn("smooth-content", comp_content)
        self.assertIn("useGSAP", comp_content)

    def test_07_vite_cache_notice(self):
        """Test Vite cache notice when vite is in project."""
        (self.test_dir / "vite.config.ts").write_text("export default {}", encoding="utf-8")
        notice = get_vite_cache_notice(self.test_dir)
        self.assertIn("--force", notice)
        self.assertIn(".vite", notice)


if __name__ == "__main__":
    unittest.main()
