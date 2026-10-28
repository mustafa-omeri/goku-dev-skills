#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_theme_bridge.py - Verification tests for get_component, get_palette, and search.py bridge."""

import sys
import subprocess
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_SCRIPTS = ROOT_DIR / ".agent" / "skills" / "frontend-design" / "scripts"
UI_UX_SCRIPTS = ROOT_DIR / ".agent" / "skills" / "ui-ux-pro-max" / "scripts"

sys.path.insert(0, str(FRONTEND_SCRIPTS))
sys.path.insert(0, str(UI_UX_SCRIPTS))

import get_component
import get_palette


class TestComponentThemes(unittest.TestCase):
    def test_get_all_themes_count_and_structure(self):
        themes = get_component.get_all_themes()
        self.assertEqual(len(themes), 56, f"Expected 56 themes, found {len(themes)}")

        categories = set()
        for t in themes:
            self.assertIn("name", t)
            self.assertIn("title", t)
            self.assertIn("category", t)
            self.assertIn("path", t)
            self.assertTrue(t["has_html"])
            self.assertTrue(t["has_css"])
            categories.add(t["category"])

        expected_categories = {"accordions", "cards", "footers", "logins", "menus", "navbars", "parallax", "sidebars"}
        self.assertTrue(expected_categories.issubset(categories), f"Missing categories: {expected_categories - categories}")

    def test_find_theme_by_name(self):
        exact = get_component.find_theme_by_name("violet-minimal-sidebar")
        self.assertIsNotNone(exact)
        self.assertEqual(exact["category"], "sidebars")

        partial = get_component.find_theme_by_name("violet-minimal")
        self.assertIsNotNone(partial)
        self.assertEqual(partial["name"], "violet-minimal-sidebar")

        none_match = get_component.find_theme_by_name("non-existent-theme-xyz")
        self.assertIsNone(none_match)

    def test_search_themes(self):
        sidebar_results = get_component.search_themes("sidebar")
        self.assertGreaterEqual(len(sidebar_results), 5)
        for r in sidebar_results[:5]:
            self.assertIn("sidebar", f"{r['name']} {r['category']}".lower())

        login_results = get_component.search_themes("login")
        self.assertGreaterEqual(len(login_results), 3)

        multi_word = get_component.search_themes("saas dual rail sidebar")
        self.assertGreater(len(multi_word), 0)
        self.assertIn("dual-rail", multi_word[0]["name"])


class TestPaletteCatalog(unittest.TestCase):
    def test_parse_catalog(self):
        palettes = get_palette.parse_catalog()
        self.assertEqual(len(palettes), 10, f"Expected 10 palettes, got {len(palettes)}")

        for p in palettes:
            self.assertIn("id", p)
            self.assertIn("title", p)
            self.assertIn("mode", p)
            self.assertIn("roles", p)
            self.assertIn("contrast", p)
            self.assertIn("on_accent", p)
            self.assertIn("zemin", p["roles"])
            self.assertIn("metin", p["roles"])
            self.assertIn("vurgu", p["roles"])

    def test_format_css_variables(self):
        palettes = get_palette.parse_catalog()
        p7 = next(p for p in palettes if p["id"] == 7)
        css = get_palette.format_css_variables(p7)

        self.assertIn(":root {", css)
        self.assertIn("--bg-primary: #EDF1EF;", css)
        self.assertIn("--text-primary: #1B3A2C;", css)
        self.assertIn("--color-accent: #4A6B5C;", css)
        self.assertIn("--text-on-accent: #FFFFFF;", css)

    def test_search_palettes(self):
        palettes = get_palette.parse_catalog()

        orman_res = get_palette.search_palettes(palettes, "orman")
        self.assertEqual(len(orman_res), 1)
        self.assertEqual(orman_res[0]["id"], 7)

        dark_res = get_palette.search_palettes(palettes, "karanlık")
        self.assertGreaterEqual(len(dark_res), 2)
        dark_ids = [p["id"] for p in dark_res]
        self.assertIn(3, dark_ids)
        self.assertIn(4, dark_ids)


class TestSearchBridge(unittest.TestCase):
    def test_search_py_surfaces_components_and_palettes(self):
        search_script = UI_UX_SCRIPTS / "search.py"

        # 1. Search for sidebar
        res = subprocess.run(
            [sys.executable, str(search_script), "sidebar"],
            capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT_DIR)
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Ready-Made Local Assets (from frontend-design)", res.stdout)
        self.assertIn("sidebars/", res.stdout)
        self.assertIn("get_component.py --theme", res.stdout)

        # 2. Search for palette keyword
        res_pal = subprocess.run(
            [sys.executable, str(search_script), "orman"],
            capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT_DIR)
        )
        self.assertEqual(res_pal.returncode, 0)
        self.assertIn("Ready-Made Local Assets (from frontend-design)", res_pal.stdout)
        self.assertIn("Şehir Ormanı", res_pal.stdout)
        self.assertIn("get_palette.py --id 7", res_pal.stdout)

        # 3. Design system query
        res_ds = subprocess.run(
            [sys.executable, str(search_script), "saas dashboard sidebar", "--design-system"],
            capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT_DIR)
        )
        self.assertEqual(res_ds.returncode, 0)
        self.assertIn("Ready-Made Local Assets (from frontend-design)", res_ds.stdout)


if __name__ == "__main__":
    unittest.main()
