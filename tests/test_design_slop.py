#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_design_slop.py Birim ve Regresyon Test Paketi."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

# Add scripts to path
import sys
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
SCRIPT_DIR = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from check_design_slop import check_file, run_checks


class TestCheckDesignSlop(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_file(self, filename: str, content: str) -> Path:
        p = self.dir_path / filename
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_e1_nested_cards(self):
        content = """
        <div className="container">
          <Card>
            <CardHeader><CardTitle>Ana Kart</CardTitle></CardHeader>
            <CardContent>
              <Card>
                <CardContent>İç İçe Kart (Yasak)</CardContent>
              </Card>
            </CardContent>
          </Card>
        </div>
        """
        f = self._write_file("TestComponent.tsx", content)
        errors, _ = check_file(f)
        rules = [e["rule"] for e in errors]
        self.assertIn("nested-card", rules)

    def test_e2_gradient_text(self):
        content_tw = """<h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-600">Başlık</h1>"""
        f_tw = self._write_file("GradTw.tsx", content_tw)
        errors, _ = check_file(f_tw)
        self.assertIn("gradient-text", [e["rule"] for e in errors])

        content_css = """.title { -webkit-background-clip: text; -webkit-text-fill-color: transparent; }"""
        f_css = self._write_file("styles.css", content_css)
        errors_css, _ = check_file(f_css)
        self.assertIn("gradient-text", [e["rule"] for e in errors_css])

    def test_e3_side_accent_on_rounded_card(self):
        content = """<div className="card rounded-xl border-l-4 border-blue-500 p-6 bg-slate-900">İçerik</div>"""
        f = self._write_file("SideAccent.tsx", content)
        errors, _ = check_file(f)
        self.assertIn("side-accent", [e["rule"] for e in errors])

    def test_e4_block_shadow(self):
        content_tw = """<div className="p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">Kutu</div>"""
        f_tw = self._write_file("Shadow.tsx", content_tw)
        errors, _ = check_file(f_tw)
        self.assertIn("block-shadow", [e["rule"] for e in errors])

    def test_e5_gray_on_chromatic_bg(self):
        content = """<div className="bg-indigo-600 text-slate-400 p-4">Çiğ Metin</div>"""
        f = self._write_file("GrayOnColor.tsx", content)
        errors, _ = check_file(f)
        self.assertIn("gray-on-color", [e["rule"] for e in errors])

    def test_e6_banned_fonts(self):
        content = """.banner { font-family: Impact, sans-serif; }"""
        f = self._write_file("font.css", content)
        errors, _ = check_file(f)
        self.assertIn("display-fallback", [e["rule"] for e in errors])

    def test_e7_eyebrow_kicker_spam(self):
        content = """
        <span className="uppercase tracking-widest text-xs text-blue-500">YENİ ÖZELLİK</span>
        <h2>Gerçek Başlık</h2>
        """
        f = self._write_file("Eyebrow.tsx", content)
        errors, _ = check_file(f)
        self.assertIn("eyebrow-spam", [e["rule"] for e in errors])

    def test_e8_emoji_used_as_icon(self):
        # 1. Standalone tag with emoji
        content1 = """<span class="icon">🚀</span>"""
        f1 = self._write_file("Emoji1.html", content1)
        errors1, _ = check_file(f1)
        self.assertIn("emoji-icon", [e["rule"] for e in errors1])

        # 2. Button with emoji prefix
        content2 = """<button class="btn">⚡ Çalıştır</button>"""
        f2 = self._write_file("Emoji2.html", content2)
        errors2, _ = check_file(f2)
        self.assertIn("emoji-icon", [e["rule"] for e in errors2])

        # 3. Badge class with emoji
        content3 = """<div class="status-badge">✓ Tamamlandı</div>"""
        f3 = self._write_file("Emoji3.html", content3)
        errors3, _ = check_file(f3)
        self.assertIn("emoji-icon", [e["rule"] for e in errors3])

    def test_e9_hardcoded_inline_hex(self):
        content = """<div style="color: #38bdf8; font-weight: bold;">Renkli Metin</div>"""
        f = self._write_file("InlineHex.html", content)
        errors, _ = check_file(f)
        self.assertIn("hardcoded-palette", [e["rule"] for e in errors])

    def test_e9_hardcoded_css_rule_hex_but_exempts_root_tokens(self):
        content = """
        <style>
          :root {
            --bg-primary: #0f172a;
            --accent: #38bdf8;
          }
          .active-btn {
            background: var(--accent);
            color: #090d16;
          }
        </style>
        <button class="active-btn">Aktif</button>
        """
        f = self._write_file("CssRuleHex.html", content)
        errors, _ = check_file(f)
        e9_hits = [e for e in errors if e["rule"] == "hardcoded-palette"]
        self.assertEqual(len(e9_hits), 1, f"Beklenen 1 E9 hatası (#090d16), gelen: {e9_hits}")
        self.assertIn("#090d16", e9_hits[0]["message"])

    def test_e10_mono_font_outside_code_selectors(self):
        content = """
        <style>
          :root { --font-mono: 'JetBrains Mono', monospace; }
          pre code, kbd { font-family: var(--font-mono); }
          .card-badge { font-family: var(--font-mono); }
        </style>
        """
        f = self._write_file("MonoLeak.html", content)
        errors, _ = check_file(f)
        e10_hits = [e for e in errors if e["rule"] == "mono-outside-code"]
        self.assertEqual(len(e10_hits), 1, f"Beklenen 1 E10 hatası (.card-badge), gelen: {e10_hits}")
        self.assertIn(".card-badge", e10_hits[0]["message"])

    def test_w2_uppercase_label_spam(self):
        content = """
        <style>
          .lbl-1 { text-transform: uppercase; letter-spacing: 0.08em; }
          .lbl-2 { text-transform: uppercase; letter-spacing: 0.06em; }
          .lbl-3 { text-transform: uppercase; letter-spacing: 0.05em; }
          .lbl-4 { text-transform: uppercase; letter-spacing: 0.1em; }
        </style>
        """
        f = self._write_file("UppercaseSpam.html", content)
        _, warnings = check_file(f)
        self.assertIn("label-uppercase-spam", [w["rule"] for w in warnings])

    def test_w1_missing_tabular_nums_on_table(self):
        content = """<table><thead><tr><th>Fiyat</th></tr></thead><tbody><tr><td>120 TL</td></tr></tbody></table>"""
        f = self._write_file("Table.html", content)
        _, warnings = check_file(f)
        self.assertIn("missing-tabular-nums", [w["rule"] for w in warnings])

    def test_w3_horizontal_scroll_slop_detected_in_css(self):
        content = """
        <style>
          .quick-slash-ribbon {
            display: flex;
            overflow-x: auto;
            white-space: nowrap;
          }
        </style>
        """
        f = self._write_file("Ribbon.html", content)
        _, warnings = check_file(f)
        rules = [w["rule"] for w in warnings]
        self.assertIn("horizontal-scroll-slop", rules)

    def test_w3_horizontal_scroll_slop_exemptions(self):
        content = """
        <style>
          .table-card { overflow-x: auto; white-space: nowrap; }
          pre.code-block { overflow-x: auto; white-space: nowrap; }
        </style>
        """
        f = self._write_file("Exemptions.html", content)
        _, warnings = check_file(f)
        w3_warnings = [w for w in warnings if w["rule"] == "horizontal-scroll-slop"]
        self.assertEqual(len(w3_warnings), 0, f"İstisnalar muaf tutulmalıydı: {w3_warnings}")

    def test_w3_horizontal_scroll_slop_tailwind(self):
        # 1. Violated
        bad_tw = '<div className="chip-list overflow-x-auto whitespace-nowrap"><span>Item</span></div>'
        f_bad = self._write_file("BadTw.tsx", bad_tw)
        _, warnings = check_file(f_bad)
        self.assertIn("horizontal-scroll-slop", [w["rule"] for w in warnings])

        # 2. Exempted (table container)
        good_tw = '<div className="table-wrap overflow-x-auto whitespace-nowrap"><table className="tabular-nums"><tbody><tr><td>Data</td></tr></tbody></table></div>'
        f_good = self._write_file("GoodTw.tsx", good_tw)
        _, warnings_good = check_file(f_good)
        w3_good = [w for w in warnings_good if w["rule"] == "horizontal-scroll-slop"]
        self.assertEqual(len(w3_good), 0)

    def test_accepts_clean_craft_code(self):
        clean_content = """
        <div class="card p-6 border border-slate-800 rounded-lg bg-slate-900">
          <div class="flex items-center gap-2">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle></svg>
            <h2 class="text-xl font-bold text-slate-100">Temiz Zanaat Başlığı</h2>
          </div>
          <p class="text-slate-300 mt-2">Düzgün tokenlandırılmış ve SVG ikonlu bileşen.</p>
          <table class="w-full mt-4 tabular-nums">
            <thead><tr><th>Adet</th></tr></thead>
            <tbody><tr><td>42</td></tr></tbody>
          </table>
        </div>
        """
        f = self._write_file("CleanComponent.tsx", clean_content)
        errors, warnings = check_file(f)
        self.assertEqual(len(errors), 0, f"Temiz kodda beklenmeyen hatalar: {errors}")
        self.assertEqual(len(warnings), 0, f"Temiz kodda beklenmeyen uyarılar: {warnings}")


if __name__ == "__main__":
    unittest.main()
