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

from idea_manager import parse_ideas, init_idea_file, convert_idea_to_card, format_kanban_card


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

    def test_convert_idea_to_card(self):
        ideas = parse_ideas(SAMPLE_MARKDOWN)
        card = convert_idea_to_card("IDEA-101", ideas, sprint="S3")
        self.assertIsNotNone(card)
        self.assertIn("### S3-101 · Test Idea One", card)
        self.assertIn("| durum | Bekliyor |", card)
        self.assertIn("| oncelik | P1 |", card)
        self.assertIn("| sprint | S3 |", card)
        self.assertIn("| gherkin | specs/S3-101.feature#test-idea-one |", card)
        self.assertIn("| kapi | python tests/run_all.py |", card)
        self.assertIn("| test | (yazılacak) |", card)
        self.assertIn("| risk | orta |", card)

        # Non-existent idea returns None
        self.assertIsNone(convert_idea_to_card("IDEA-999", ideas))

    def test_convert_idea_to_card_append(self):
        ideas = parse_ideas(SAMPLE_MARKDOWN)
        with tempfile.TemporaryDirectory() as tmpdir:
            kanban = Path(tmpdir) / "KANBAN.md"
            kanban.write_text("# KANBAN\n\n## Bekliyor\n\n### Existing\n\n## Yapılıyor\n", encoding="utf-8")
            card = convert_idea_to_card("IDEA-101", ideas, sprint="S2", append_target=kanban)
            self.assertIsNotNone(card)
            content = kanban.read_text(encoding="utf-8")
            self.assertIn("### S2-101 · Test Idea One", content)
            self.assertTrue(content.index("### S2-101") < content.index("## Yapılıyor"))


if __name__ == "__main__":
    unittest.main()
