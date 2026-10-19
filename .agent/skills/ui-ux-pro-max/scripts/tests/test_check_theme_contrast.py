#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for check_theme_contrast.py gate checker."""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parents[4]
SCRIPTS_DIR = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import check_theme_contrast


class TestCheckThemeContrast(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_theme_contrast_"))
        self.orig_env = os.environ.get("AGENTS_PROJECT_ROOT")
        os.environ["AGENTS_PROJECT_ROOT"] = str(self.tmp_dir)

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["AGENTS_PROJECT_ROOT"] = self.orig_env
        else:
            os.environ.pop("AGENTS_PROJECT_ROOT", None)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_out_of_scope_when_no_css_files(self):
        """CSS dosyası veya tema token'ı olmadığında kapsam dışı dönmeli (exit 0)."""
        errors, warnings, blocks, _ = check_theme_contrast.check(self.tmp_dir)
        self.assertEqual(blocks, 0)
        self.assertEqual(len(errors), 0)

    def test_clean_theme_passes(self):
        """Yüksek kontrastlı, WCAG 4.5:1 uyumlu tema temiz geçmeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "theme.css"
        css.write_text(
            """
            :root {
                --background-color: #FFFFFF;
                --theme-surface: #F8FAFC;
                --theme-ink: #0F172A;
                --theme-ink-muted: #475569;
                --theme-ink-faint: #64748B;
            }
            [data-theme="dark"] {
                --background-color: #09090B;
                --theme-surface: #18181B;
                --theme-ink: #FAFAFA;
                --theme-ink-muted: #A1A1AA;
                --theme-ink-faint: #71717A;
            }
            """,
            encoding="utf-8",
        )
        errors, warnings, blocks, _ = check_theme_contrast.check(self.tmp_dir)
        self.assertGreaterEqual(blocks, 2)
        self.assertEqual(len(errors), 0)

    def test_low_contrast_primary_fails_e1(self):
        """Birincil metin kontrastı < 4.5:1 olduğunda E1 hatası vermeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "bad_theme.css"
        css.write_text(
            """
            [data-theme="dark"] {
                --background-color: #061824;
                --theme-surface: #0B2233;
                --theme-ink: #023047; /* Koyu lacivert zemin üzerinde koyu lacivert metin (1.35:1) */
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        e1_codes = [e.code for e in errors]
        self.assertIn("E1", e1_codes)

    def test_low_contrast_muted_fails_e2(self):
        """İkincil/muted metin kontrastı < 3.0:1 olduğunda E2 hatası vermeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "muted_fail.css"
        css.write_text(
            """
            [data-theme="dark"] {
                --background-color: #0F172A;
                --theme-surface: #1E293B;
                --theme-ink: #F8FAFC;
                --theme-ink-muted: #1E293B; /* Zeminle neredeyse aynı renk (1.1:1) */
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        e2_codes = [e.code for e in errors]
        self.assertIn("E2", e2_codes)

    def test_hardcoded_body_contrast_fails_e3(self):
        """Tema seçicisi içinde body seçicisine koyu zemin üzerinde koyu renk verildiğinde E3 vermeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "body_contrast.css"
        css.write_text(
            """
            [data-theme="dark"] {
                --background-color: #050B10;
                --theme-ink: #F8FAFC;
            }
            [data-theme="dark"] body {
                color: #023047; /* Koyu zeminde koyu lacivert gövde metni */
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        e3_codes = [e.code for e in errors]
        self.assertIn("E3", e3_codes)

    def test_alpha_compositing_calculation(self):
        """Alfa kanalı opaklık içeren renklerin zemin üzerinde doğru harmanlandığını doğrular."""
        bg = check_theme_contrast.ColorRGBA(0, 0, 0, 1.0)  # Siyah
        fg_semi = check_theme_contrast.ColorRGBA(255, 255, 255, 0.5)  # %50 Beyaz
        eff = fg_semi.composite_over(bg)
        # Siyah üzerinde %50 beyaz -> yaklaşık 128 gri
        self.assertAlmostEqual(eff.r, 128, delta=2)
        self.assertAlmostEqual(eff.g, 128, delta=2)
        self.assertAlmostEqual(eff.b, 128, delta=2)

    def test_hsl_and_shadcn_format_parsing(self):
        """HSL ve Tailwind/shadcn boşluklu formatların doğru çözümlendiğini doğrular."""
        c1 = check_theme_contrast.parse_color("hsl(210, 40%, 98%)")
        self.assertIsNotNone(c1)
        self.assertGreater(c1.r, 200)

        c2 = check_theme_contrast.parse_color("222.2 84% 4.9%")
        self.assertIsNotNone(c2)
        self.assertLess(c2.r, 50)

    def test_selection_pair_isolation(self):
        """Selection token'larının normal zeminle karıştırılmayıp kendi çiftiyle ölçüldüğünü doğrular."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "selection.css"
        css.write_text(
            """
            [data-theme="dark"] {
                --background-color: #061824;
                --theme-surface: #0B2233;
                --theme-ink: #F8FAFC;
                --theme-selection-bg: #0284C7;
                --theme-selection-text: #FFFFFF;
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        # Selection-bg normal text ile kıyaslanıp sahte hata vermemeli
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
