#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Toplu Python Tasarım ve Anti-Slop Kalite Kapısı (test_py_design_audit.py).

[GSW]-PY-AUDIT-001 gereksinimi:
Depo içindeki tüm *.py dosyalarında HTML/CSS/DOM/şablon üreten kodların
DESIGN.md ve Anti-Slop (E8, E9, E14, E15, E16, W5) standartlarına tam uyumunu
mekanik olarak garanti altına alır.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent

# check_design_slop modülünü içe aktar
sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"))
import check_design_slop as cds


class TestPythonDesignAudit(unittest.TestCase):
    """Depodaki tüm python scriptlerinin anti-slop uyumluluğunu denetler."""

    @classmethod
    def setUpClass(cls):
        # Git ile takip edilen tüm .py dosyalarını listele
        out = subprocess.check_output(["git", "ls-files", "*.py"], cwd=PROJECT_ROOT, text=True)
        all_py = [PROJECT_ROOT / f for f in out.strip().splitlines()]
        
        # Test ve test verisi dosyalarını tarama dışı bırak
        cls.source_py_files = [
            p for p in all_py
            if not any(part in ("tests", "test", "__pycache__", ".venv", "venv", "yedekler") for part in p.parts)
            and not p.stem.startswith("test_")
            and not p.stem.endswith("_test")
            and not p.stem.startswith("test-")
        ]

    def test_minimum_source_files_discovered(self):
        """En az 100 kaynak python dosyası keşfedildiğini doğrular."""
        self.assertGreaterEqual(len(self.source_py_files), 100)

    def test_all_python_files_free_of_design_slop(self):
        """Python dosyalarındaki gömülü HTML/CSS şablonlarında zanaat tabanı ihlali olmadığını doğrular."""
        violations = []

        for p in self.source_py_files:
            if not p.is_file():
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:
                violations.append((str(p), 1, "E0", f"Okuma hatası: {exc}"))
                continue

            lines = content.splitlines()

            # E14: Rogue Dark Modal Header Slop
            for m in cds.ROGUE_DARK_MODAL_RE.finditer(content):
                line_no = content[:m.start()].count("\n") + 1
                violations.append((str(p), line_no, "E14", m.group(0)[:80]))

            # E16: Semantic Token Drift / Ham Koyu Input
            m = cds.DARK_INPUT_MODAL_RE.search(content)
            if m:
                line_no = content[:m.start()].count("\n") + 1
                violations.append((str(p), line_no, "E16", m.group(0)[:80]))

            # E8: Şablon veya HTML üretirken buton/rozet içinde ham emoji kullanımı
            for idx, line in enumerate(lines, start=1):
                if any(tag in line for tag in ("<button", "<div", "<span", "<h", "<a", "<li", "badge", "icon", "pill", "btn")):
                    # Regex tanımları veya yorumları hariç tut
                    if any(kw in line for kw in ("_RE", "re.compile", "pattern", "Pattern", "test")):
                        continue
                    if line.strip().startswith("#"):
                        continue
                    m = cds.EMOJI_STANDALONE_TAG_RE.search(line)
                    if m:
                        violations.append((str(p), idx, "E8", m.group(0).strip()))

            # E9: Inline style içinde token dışı ham hex renk kullanımı
            for idx, line in enumerate(lines, start=1):
                if any(kw in line for kw in ("_RE", "re.compile", "pattern", "Pattern", "HEX_")):
                    continue
                if line.strip().startswith("#"):
                    continue
                m = cds.INLINE_HEX_STYLE_RE.search(line)
                if m:
                    # var(--..., #hex) fallback istisnası
                    val = m.group(0)
                    if "var(" in line and ", #" in line:
                        continue
                    violations.append((str(p), idx, "E9", val[:80]))

            # W5: Modal/drawer scroll alanında overscroll-contain bulunmalı
            for pattern in (cds.MODAL_SCROLL_TW_RE, cds.MODAL_TAG_SCROLL_RE1, cds.MODAL_TAG_SCROLL_RE2):
                for m in pattern.finditer(content):
                    matched_tag = m.group(0)
                    if not re.search(r"\b(?:overscroll-contain|overscroll-none|overscroll-behavior)\b", matched_tag):
                        line_no = content[:m.start()].count("\n") + 1
                        violations.append((str(p), line_no, "W5", matched_tag[:80]))

        if violations:
            msg_lines = [f"{len(violations)} tasarım ihlali tespit edildi:"]
            for f, l, code, detail in violations[:10]:
                msg_lines.append(f"  {f}:{l} [{code}] -> {detail}")
            if len(violations) > 10:
                msg_lines.append(f"  ... and {len(violations)-10} more")
            self.fail("\n".join(msg_lines))

    def test_skills_catalog_html_passes_anti_slop(self):
        """.agent/skills-catalog.html dosyasının check_design_slop kapısından sıfır hatayla geçtiğini doğrular."""
        catalog_path = PROJECT_ROOT / ".agent" / "skills-catalog.html"
        self.assertTrue(catalog_path.is_file(), ".agent/skills-catalog.html mevcut olmalı")

        res = cds.run_checks(PROJECT_ROOT, specific_files=[catalog_path], include_agent=True)
        self.assertEqual(res["exit"], 0, f"skills-catalog.html hatalar içeriyor: {res.get('errors')}")
        self.assertEqual(len(res["errors"]), 0, f"0 hata bekleniyordu, {len(res['errors'])} bulundu")


if __name__ == "__main__":
    unittest.main()

