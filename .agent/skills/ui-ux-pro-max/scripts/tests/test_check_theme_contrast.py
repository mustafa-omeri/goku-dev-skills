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

    def test_shadcn_tokens_no_false_positives(self):
        """Standart shadcn/ui :root ve .dark token setinde sıfır false-positive üretmeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "index.css"
        css.write_text(
            """
            @layer base {
              :root {
                --background: 0 0% 100%;
                --foreground: 0 0% 3.9%;
                --card: 0 0% 100%;
                --card-foreground: 0 0% 3.9%;
                --popover: 0 0% 100%;
                --popover-foreground: 0 0% 3.9%;
                --primary: 203 73% 38%;
                --primary-foreground: 0 0% 98%;
                --secondary: 0 0% 96.1%;
                --secondary-foreground: 0 0% 9%;
                --muted: 0 0% 96.1%;
                --muted-foreground: 0 0% 45.1%;
                --accent: 203 61% 56%;
                --accent-foreground: 0 0% 9%;
                --destructive: 0 72.2% 50.6%;
                --destructive-foreground: 0 0% 98%;
                --border: 0 0% 89.8%;
                --input: 0 0% 89.8%;
                --ring: 203 73% 38%;
                --chart-1: 203 61% 56%;
                --radius: 0.5rem;
              }
              .dark {
                --background: 0 0% 3.9%;
                --foreground: 0 0% 98%;
                --card: 0 0% 3.9%;
                --card-foreground: 0 0% 98%;
                --popover: 0 0% 3.9%;
                --popover-foreground: 0 0% 98%;
                --primary: 203 61% 56%;
                --primary-foreground: 0 0% 9%;
                --secondary: 0 0% 14.9%;
                --secondary-foreground: 0 0% 98%;
                --muted: 0 0% 14.9%;
                --muted-foreground: 0 0% 63.9%;
                --accent: 203 73% 38%;
                --accent-foreground: 0 0% 98%;
                --destructive: 0 62.8% 30.6%;
                --destructive-foreground: 0 0% 98%;
              }
            }
            """,
            encoding="utf-8",
        )
        errors, _, blocks, _ = check_theme_contrast.check(self.tmp_dir)
        self.assertEqual(blocks, 2)
        self.assertEqual(len(errors), 0, f"Beklenmeyen false-positive: {[e.message for e in errors]}")

    def test_shadcn_paired_foreground_low_contrast_fails_e1(self):
        """Eşleşen --primary ve --primary-foreground çifti < 4.5:1 olduğunda E1 vermeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "bad_primary.css"
        css.write_text(
            """
            :root {
                --background: 0 0% 100%;
                --foreground: 0 0% 3.9%;
                --primary: 200 90% 70%;
                --primary-foreground: 0 0% 98%; /* Açık mavi üstüne beyaz metin -> düşük kontrast */
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        self.assertTrue(
            any(e.code == "E1" and e.bg_name == "--primary" and e.text_name == "--primary-foreground" for e in errors),
            f"--primary/--primary-foreground çifti yakalanmadı: {[e.message for e in errors]}",
        )

    def test_shadcn_accent_and_destructive_pairs_checked(self):
        """--accent/--accent-foreground ve --destructive/--destructive-foreground çiftleri de denetlenmeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "bad_accent_destr.css"
        css.write_text(
            """
            :root {
                --background: 0 0% 100%;
                --foreground: 0 0% 3.9%;
                --accent: 210 100% 85%;
                --accent-foreground: 0 0% 98%;
                --destructive: 0 85% 75%;
                --destructive-foreground: 0 0% 98%;
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        pair_hits = {(e.bg_name, e.text_name) for e in errors if e.code == "E1"}
        self.assertIn(("--accent", "--accent-foreground"), pair_hits)
        self.assertIn(("--destructive", "--destructive-foreground"), pair_hits)

    def test_shadcn_v3_sidebar_background_pair_checked(self):
        """shadcn v3 --sidebar-background ve --sidebar-foreground çifti doğru eşlenmeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "sidebar.css"
        css.write_text(
            """
            :root {
                --background: 0 0% 100%;
                --foreground: 0 0% 3.9%;
                --sidebar-background: 240 5.9% 10%;
                --sidebar-foreground: 240 5.9% 15%; /* Koyu zemin üstünde koyu metin */
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        self.assertTrue(
            any(e.code == "E1" and e.bg_name == "--sidebar-background" and e.text_name == "--sidebar-foreground" for e in errors),
            f"sidebar çifti yakalanmadı: {[e.message for e in errors]}",
        )

    def test_partial_dark_override_inherits_pair_from_root(self):
        """.dark yalnız --primary değiştirirse :root'tan miras alınan --primary-foreground ile test edilmeli."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "partial_dark.css"
        css.write_text(
            """
            :root {
                --background: 0 0% 100%;
                --foreground: 0 0% 3.9%;
                --primary: 222.2 47.4% 11.2%;
                --primary-foreground: 0 0% 98%;
            }
            .dark {
                --background: 0 0% 3.9%;
                --foreground: 0 0% 98%;
                --primary: 0 0% 95%; /* Açık zemin yapılıp --primary-foreground (#FAFAFA) override edilmemiş */
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        self.assertTrue(
            any(
                e.code == "E1"
                and ".dark" in e.theme_selector
                and e.bg_name == "--primary"
                and e.text_name == "--primary-foreground"
                for e in errors
            ),
            f"Kısmi .dark miras hatası yakalanmadı: {[e.message for e in errors]}",
        )

    def test_unpaired_muted_and_text_secondary_still_checked(self):
        """Partneri olmayan tekil --muted ve --text-secondary klasik temalarda hala E2 ile yakalanmalı."""
        styles_dir = self.tmp_dir / "src"
        styles_dir.mkdir()
        css = styles_dir / "legacy_muted.css"
        css.write_text(
            """
            :root {
                --bg: #ffffff;
                --text: #111827;
                --muted: #e5e7eb; /* --muted-foreground yok -> metin token'ı ve çok soluk */
                --text-secondary: #f3f4f6;
            }
            """,
            encoding="utf-8",
        )
        errors, _, _, _ = check_theme_contrast.check(self.tmp_dir)
        hit_texts = {e.text_name for e in errors if e.code == "E2"}
        self.assertIn("--muted", hit_texts)
        self.assertIn("--text-secondary", hit_texts)


if __name__ == "__main__":
    unittest.main()
