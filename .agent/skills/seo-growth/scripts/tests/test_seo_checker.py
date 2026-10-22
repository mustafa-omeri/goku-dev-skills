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

from seo_checker import analyze_html_content, scan_path


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
    <p>İçerik metni burada yer alır.</p>
    <img src="/logo.png" alt="Şirket Logosu">
</body>
</html>"""
        res = analyze_html_content(html_doc, "index.html")
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["warnings"], [])
        self.assertEqual(res["score"], 100)
        self.assertEqual(res["checks"]["h1_count"], 1)

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
