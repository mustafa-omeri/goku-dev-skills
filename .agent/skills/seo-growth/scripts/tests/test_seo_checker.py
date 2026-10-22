#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEO Checker Birim Test Paketi."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from seo_checker import analyze_html_content, analyze_robots_txt, scan_path


class TestSeoChecker(unittest.TestCase):

    def test_perfect_seo_page(self):
        html_doc = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Harika Ürün - Modern ve Hızlı Çözümler Sunan Platform</title>
    <meta name="description" content="Harika Ürün ile iş süreçlerinizi dakikalar içinde dijitalleştirin. Güvenli, ölçeklenebilir ve yapay zeka destekli yönetim platformu.">
    <link rel="canonical" href="https://example.com/harika-urun">
    <link rel="alternate" hreflang="tr" href="https://example.com/harika-urun">
    <link rel="alternate" hreflang="en" href="https://example.com/en/great-product">
    <link rel="alternate" hreflang="x-default" href="https://example.com/en/great-product">
    <meta property="og:title" content="Harika Ürün">
    <meta property="og:description" content="Harika Ürün ile iş süreçlerinizi dakikalar içinde dijitalleştirin.">
    <meta property="og:image" content="https://example.com/og.png">
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Harika Ürün"
    }
    </script>
</head>
<body>
    <h1>Harika Ürün ile Tanışın</h1>
    <p>Harika Ürün, kurumsal ekiplerin iş akışlarını otomatikleştirerek manuel operasyon yükünü %60 oranında azaltan yeni nesil bulut tabanlı bir iş yönetim platformudur. Gelişmiş yapay zeka entegrasyonu sayesinde ekipler tek bir ekrandan tüm süreçleri güvenle yönetir ve raporlar.</p>
    <img src="/logo.png" alt="Şirket Logosu">
</body>
</html>"""
        res = analyze_html_content(html_doc, "index.html")
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["warnings"], [])
        self.assertEqual(res["score"], 100)
        self.assertEqual(res["checks"]["h1_count"], 1)
        self.assertIn("SoftwareApplication", res["checks"]["schema_types"])
        self.assertGreaterEqual(res["checks"]["answer_block_candidates"], 1)

    def test_missing_critical_elements(self):
        bad_html = """<!DOCTYPE html>
<html>
<head>
    <title>Kısa</title>
</head>
<body>
    <h2>Başlık Var Ama H1 Yok</h2>
    <img src="/unnamed.jpg">
    <script type="application/ld+json">
    { bu geçersiz bir json }
    </script>
</body>
</html>"""
        res = analyze_html_content(bad_html, "bad.html")
        self.assertEqual(res["status"], "FAIL")
        # Beklenen hatalar: Description eksik (E2), Viewport eksik (E3), H1 eksik (E4), Malformed JSON-LD (E5)
        error_codes = [e.split(":")[0] for e in res["errors"]]
        self.assertIn("E2", error_codes)
        self.assertIn("E3", error_codes)
        self.assertIn("E4", error_codes)
        self.assertIn("E5", error_codes)
        self.assertLess(res["score"], 50)

    def test_stale_year_and_hreflang_warnings(self):
        stale_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Best SEO Practices for 2023 - Complete Guide</title>
    <meta name="description" content="Learn all the best SEO practices and guides that were relevant in the past year for web developers.">
    <link rel="canonical" href="https://example.com/seo-2023">
    <link rel="alternate" hreflang="en" href="https://example.com/en/seo">
    <link rel="alternate" hreflang="tr" href="https://example.com/tr/seo">
    <meta name="robots" content="noindex, follow">
</head>
<body>
    <h1>Best SEO Practices for 2023</h1>
</body>
</html>"""
        res = analyze_html_content(stale_html, "stale.html")
        # Hata yok ama Content Decay (W10), x-default eksik (W11) ve noindex (W12) uyarısı gelmeli
        self.assertEqual(res["status"], "PASS")
        warn_codes = [w.split(":")[0] for w in res["warnings"]]
        self.assertIn("W10", warn_codes)
        self.assertIn("W11", warn_codes)
        self.assertIn("W12", warn_codes)

    def test_robots_txt_analysis(self):
        valid_robots = """User-agent: *
Allow: /
Disallow: /admin/

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

Sitemap: https://example.com/sitemap.xml
"""
        res = analyze_robots_txt(valid_robots, "robots.txt")
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["warnings"], [])
        self.assertEqual(res["score"], 100)
        self.assertTrue(res["checks"]["has_sitemap"])
        self.assertIn("chatgpt-user", res["checks"]["configured_ai_bots"])
        self.assertIn("perplexitybot", res["checks"]["configured_ai_bots"])

    def test_robots_txt_blanket_disallow_and_missing_sitemap(self):
        bad_robots = """User-agent: *
Disallow: /
"""
        res = analyze_robots_txt(bad_robots, "robots.txt")
        warn_codes = [w.split(":")[0] for w in res["warnings"]]
        self.assertIn("W_ROBOTS_1", warn_codes)  # Sitemap eksik
        self.assertIn("W_ROBOTS_2", warn_codes)  # Blanket disallow
        self.assertIn("W_ROBOTS_3", warn_codes)  # AI bot politikası eksik

    def test_scan_path_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir)
            (p / "page1.html").write_text("<!DOCTYPE html><html><head><title>Test Page Title Long Enough 12345</title><meta name=\"viewport\" content=\"width=device-width\"><meta name=\"description\" content=\"This is a sufficiently long description that fits SEO heuristics well.\"></head><body><h1>Heading</h1></body></html>", encoding="utf-8")
            (p / "page2.txt").write_text("not html", encoding="utf-8")

            results = scan_path(p)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
