#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for idea_manager.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from idea_manager import parse_ideas, init_idea_file


SAMPLE_MARKDOWN = """# 💡 PROJE FİKİR HAVUZU (myidea.md)

### IDEA-101: Test Idea One
- **Durum:** 🎯 `[RECOMMENDED]`
- **Rating:** `9.5/10`
- **Açıklama:** Quick explanation.
- **Değer / Gerekçe:** High value.
- **Ajan Değerlendirmesi:** Immediate win.

### IDEA-102: Obsolete Idea Two
- **Durum:** ⛔ `[DROPPED - Replaced by modern stack]`
- **Rating:** `3.0/10`
- **Açıklama:** Old stuff.
- **Değer / Gerekçe:** Low value.
- **Ajan Değerlendirmesi:** Do not proceed.

### IDEA-103: Completed Idea Three
- **Durum:** ✅ `[SHIPPED - Sprint 2]`
- **Rating:** `8.0/10`
- **Açıklama:** Already done.
- **Değer / Gerekçe:** Useful.
- **Ajan Değerlendirmesi:** Successfully shipped.
"""


class TestIdeaManager(unittest.TestCase):
    def test_parse_ideas(self):
        ideas = parse_ideas(SAMPLE_MARKDOWN)
        self.assertEqual(len(ideas), 3)

        # Idea 101
        self.assertEqual(ideas[0]["id"], "IDEA-101")
        self.assertEqual(ideas[0]["score"], 9.5)
        self.assertTrue(ideas[0]["is_active"])
        self.assertFalse(ideas[0]["is_eliminated"])

        # Idea 102
        self.assertEqual(ideas[1]["id"], "IDEA-102")
        self.assertTrue(ideas[1]["is_eliminated"])
        self.assertFalse(ideas[1]["is_active"])

        # Idea 103
        self.assertEqual(ideas[2]["id"], "IDEA-103")
        self.assertTrue(ideas[2]["is_done"])
        self.assertFalse(ideas[2]["is_active"])

    def test_init_idea_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "docs" / "idea" / "myidea.md"
            tpl = Path(tmpdir) / "template.md"
            tpl.write_text("# Template Content\n", encoding="utf-8")

            res = init_idea_file(target, tpl)
            self.assertTrue(res)
            self.assertTrue(target.is_file())
            self.assertIn("# Template Content", target.read_text(encoding="utf-8"))

            # Calling again should return False (already exists)
            res2 = init_idea_file(target, tpl)
            self.assertFalse(res2)


if __name__ == "__main__":
    unittest.main()
