#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_design_contract.py Birim ve Regresyon Test Paketi (TDD)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
SCRIPT_DIR = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from check_design_contract import parse_oklch_to_rgba, run_checks  # noqa: E402


VALID_DESIGN_MD = """---
name: "Field Manual Reference"
description: "Yüksek kontrastlı teknik saha kılavuzu ve beceri indeksi"
mode: "crafted"
last_reviewed: "2026-10-27"

colors:
  primary: "oklch(55% 0.18 255)"
  secondary: "oklch(50% 0.14 175)"
  accent: "oklch(58% 0.19 35)"
  surface-ground: "#0b0f17"
  surface-inset: "#070a10"
  surface-raised: "#131a26"
  surface-overlay: "#1b2434"
  text-primary: "#f1f5f9"
  text-body: "#cbd5e1"
  text-muted: "#94a3b8"
  text-faint: "#64748b"
  text-disabled: "#475569"
  border-subtle: "rgba(148, 163, 184, 0.16)"
  border-strong: "rgba(56, 189, 248, 0.55)"

typography:
  scale:
    "12": "0.75rem"
    "14": "0.875rem"
    "16": "1rem"
    "20": "1.25rem"
    "24": "1.5rem"
    "32": "2rem"
  display:
    fontFamily: "'Plus Jakarta Sans', sans-serif"
  body:
    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif"
  code:
    fontFamily: "'JetBrains Mono', monospace"
    allowedSelectors: ["code", "pre", "kbd", "samp", ".trigger-chip", ".slash-cmd-name"]

rounded:
  none: "0"
  sm: "6px"
  md: "8px"
  lg: "12px"
  pill: "999px"

spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "32px"
---

# Design System: Field Manual

## 0. Proje Kanıtı (Project Evidence)
- Ekran görüntüsü: `docs/screenshots/desktop-dark-1440.png`
- Yüzey modu: Operate + Read

## 1. Genel Bakış & Kreatif Kuzey Yıldızı
Endüstriyel saha kılavuzu disiplini.

## 2. Değerlendirilen Yönler
| Yön | Felsefe | Palet & Font | Karar |
|---|---|---|---|
| Yön A | Saha Kılavuzu | Mineral Koyu + Plus Jakarta Sans | Seçildi |
| Yön B | Editoryal İndeks | Kağıt Krem + Instrument Serif | Elendi |
| Yön C | Komut Merkezi | Karbon + IBM Plex Sans | Elendi |

## 3. Reddedilen Varsayılanlar (Rejected Defaults)
| Reddedilen Aday | Kaynak | Neden Reddedildi? | Yerine Ne Seçildi? |
|---|---|---|---|
| Slate + Neon Yeşil | search.py | Jenerik AI terminal klişesi | Mineral zemin + dengeli mavi/indigo |
| Tüm etiketlerde Mono font | Eski kod | Okunabilirliği düşürüyor | Yalnızca komut ve tetikleyicilerde Mono |

## 9. Bileşen Durum Matrisi
| Bileşen | Default | Hover | Loading | Empty |
|---|---|---|---|---|
| Arama | Hazır | Focus halka | Filtreleniyor | Sonuç yok + Sıfırla CTA |

## 10. Responsive Davranış (390 / 834 / 1440)
| Kırılım | Düzen |
|---|---|
| 390px | Tek sütun, 44px dokunma hedefi |
| 834px | 2 sütun ızgara |
| 1440px | 3 sütun ızgara + yapışkan tablo |

## 11. Karar Günlüğü
| Tarih | Karar | Kanıt | Token |
|---|---|---|---|
| 2026-10-27 | İlk sözleşme | F1-F7 | Tümü |
"""


class TestCheckDesignContract(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write(self, rel_path: str, content: str) -> Path:
        p = self.root / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_out_of_scope_when_no_ui_and_no_design_md(self):
        self._write("README.md", "# Backend Only\n")
        res = run_checks(self.root)
        self.assertEqual(res["scope"], "out_of_scope")
        self.assertEqual(res["exit"], 0)

    def test_e1_or_w0_when_ui_exists_without_design_md(self):
        self._write("src/App.tsx", "export const App = () => <div className='p-4'>Hello</div>;\n")
        # Default brownfield grace mode -> W0 warning, exit 0
        res_grace = run_checks(self.root, strict=False)
        self.assertEqual(res_grace["exit"], 0)
        self.assertIn("W0", [w["code"] for w in res_grace["warnings"]])

        # Strict mode -> E1 error, exit 1
        res_strict = run_checks(self.root, strict=True)
        self.assertEqual(res_strict["exit"], 1)
        self.assertIn("E1", [e["code"] for e in res_strict["errors"]])

    def test_e2_missing_required_tokens(self):
        incomplete = """---
name: "Incomplete"
mode: "crafted"
last_reviewed: "2026-10-27"
colors:
  primary: "#2563eb"
---
# Incomplete
"""
        self._write("DESIGN.md", incomplete)
        self._write("src/index.css", ":root { --bg: #000; }")
        res = run_checks(self.root)
        self.assertIn("E2", [e["code"] for e in res["errors"]])

    def test_e3_template_placeholder_or_anchor_fingerprint(self):
        template_copy = Path(PROJECT_ROOT / ".agent" / "templates" / "DESIGN.template.md").read_text(encoding="utf-8")
        self._write("DESIGN.md", template_copy)
        self._write("src/index.css", ":root { --bg: #111; }")
        res = run_checks(self.root)
        self.assertIn("E3", [e["code"] for e in res["errors"]])

        # Also test old anchored oklch fingerprint
        anchored = VALID_DESIGN_MD.replace(
            'primary: "oklch(55% 0.18 255)"',
            'primary: "oklch(84% 0.19 80)"'
        ).replace(
            'surface-ground: "#0b0f17"',
            'surface-ground: "oklch(7% 0.006 95)"'
        )
        self._write("DESIGN.md", anchored)
        res2 = run_checks(self.root)
        self.assertIn("E3", [e["code"] for e in res2["errors"]])

    def test_e4_wcag_token_contrast_failure_and_oklch_math(self):
        # Verify OKLCH parser returns valid RGB
        c_dark = parse_oklch_to_rgba("oklch(15% 0.02 250)")
        c_light = parse_oklch_to_rgba("oklch(92% 0.01 250)")
        self.assertIsNotNone(c_dark)
        self.assertIsNotNone(c_light)
        self.assertLess(c_dark.r, 50)
        self.assertGreater(c_light.r, 200)

        # Low contrast between surface-ground (#0b0f17) and text-body (#1e293b)
        bad_contrast = VALID_DESIGN_MD.replace('text-body: "#cbd5e1"', 'text-body: "#1e293b"')
        self._write("DESIGN.md", bad_contrast)
        self._write("src/index.css", ":root { --bg: #0b0f17; }")
        res = run_checks(self.root)
        self.assertIn("E4", [e["code"] for e in res["errors"]])

    def test_e5_undeclared_font_family_drift(self):
        self._write("DESIGN.md", VALID_DESIGN_MD)
        self._write(
            "src/styles.css",
            ".hero { font-family: 'Papyrus Neue', fantasy; }\n"
        )
        res = run_checks(self.root)
        self.assertIn("E5", [e["code"] for e in res["errors"]])

    def test_e6_mono_font_outside_allowed_selectors(self):
        self._write("DESIGN.md", VALID_DESIGN_MD)
        # Using var(--font-mono) on .card-title (not in allowedSelectors) -> E6
        self._write(
            "src/styles.css",
            ".card-title { font-family: var(--font-mono); }\n"
            ".trigger-chip { font-family: var(--font-mono); }\n"
            "pre code { font-family: 'JetBrains Mono', monospace; }\n"
        )
        res = run_checks(self.root)
        e6_msgs = [e["message"] for e in res["errors"] if e["code"] == "E6"]
        self.assertTrue(any(".card-title" in m for m in e6_msgs), f"Expected .card-title in E6, got {res['errors']}")
        self.assertFalse(any(".trigger-chip" in m for m in e6_msgs))
        self.assertFalse(any("pre code" in m for m in e6_msgs))

    def test_w1_rejected_defaults_exempt_in_baseline_mode(self):
        # Crafted mode without Rejected Defaults section -> W1
        no_rejected = VALID_DESIGN_MD.split("## 3. Reddedilen Varsayılanlar")[0] + "\n## 9. Bileşen Durum Matrisi\n"
        self._write("DESIGN.md", no_rejected)
        self._write("src/styles.css", "body { font-family: 'Plus Jakarta Sans', sans-serif; }\n")
        res_crafted = run_checks(self.root)
        self.assertIn("W1", [w["code"] for w in res_crafted["warnings"]])

        # Baseline mode without Rejected Defaults section -> no W1!
        baseline_md = no_rejected.replace('mode: "crafted"', 'mode: "baseline"')
        self._write("DESIGN.md", baseline_md)
        res_baseline = run_checks(self.root)
        self.assertNotIn("W1", [w["code"] for w in res_baseline["warnings"]])

    def test_clean_valid_contract_passes_zero_errors_zero_warnings(self):
        self._write("DESIGN.md", VALID_DESIGN_MD)
        self._write(
            "src/styles.css",
            ":root { --bg-ground: #0b0f17; --font-sans: 'Plus Jakarta Sans', sans-serif; --font-mono: 'JetBrains Mono', monospace; }\n"
            "body { font-family: var(--font-sans); color: var(--text-body); }\n"
            "pre code, .trigger-chip { font-family: var(--font-mono); }\n"
        )
        res = run_checks(self.root, strict=True)
        self.assertEqual(res["errors"], [], f"Unexpected errors: {res['errors']}")
        self.assertEqual(res["warnings"], [], f"Unexpected warnings: {res['warnings']}")
        self.assertEqual(res["exit"], 0)


if __name__ == "__main__":
    unittest.main()
