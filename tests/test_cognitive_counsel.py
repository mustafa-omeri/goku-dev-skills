#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for Cognitive Counsel Framework & 6-Hat Micro-Focus Commands."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULE_FILE = ROOT / ".agent" / "rules" / "cognitive-counsel-framework.md"
ROUTING_FILE = ROOT / ".agent" / "rules" / "skill-trigger-routing.md"


class TestCognitiveCounselFramework(unittest.TestCase):
    def test_rule_file_exists_and_is_attitude(self):
        self.assertTrue(RULE_FILE.is_file(), "cognitive-counsel-framework.md dosyası mevcut olmalıdır")
        content = RULE_FILE.read_text(encoding="utf-8")
        self.assertIn("sinif: TUTUM", content)
        self.assertIn("cognitive-counsel-framework", content)

    def test_contains_all_six_disciplines(self):
        content = RULE_FILE.read_text(encoding="utf-8")
        for discipline in ("`PO`", "`ARCH`", "`UX`", "`SEO`", "`GRW`", "`QA`"):
            self.assertIn(discipline, content, f"{discipline} şapkası kuralda yer almalıdır")

    def test_contains_anti_sycophancy_and_invisible_filters(self):
        content = RULE_FILE.read_text(encoding="utf-8")
        self.assertIn("Anti-Sycophancy", content)
        self.assertIn("Onaylama, Sına", content)
        for filter_name in ("REDTEAM", "80/20", "KILLCRITIC", "TRUTHMODE", "LINDYMODE", "ELI5"):
            self.assertIn(filter_name, content, f"{filter_name} görünmez düşünme filtresi kuralda yer almalıdır")

    def test_contains_micro_focus_commands(self):
        content = RULE_FILE.read_text(encoding="utf-8")
        commands = [
            "/PO", "/ARCH", "/UX", "/SEO", "/GRW", "/QA",
            "/6HAT", "/TIGHT", "/DIG", "/PUSHBACK"
        ]
        for cmd in commands:
            self.assertIn(cmd, content, f"{cmd} komutu kural dosyasında bulunmalıdır")

    def test_commands_registered_in_routing_dictionary(self):
        self.assertTrue(ROUTING_FILE.is_file())
        routing_content = ROUTING_FILE.read_text(encoding="utf-8")
        for cmd in ("/PO", "/ARCH", "/UX", "/SEO", "/GRW", "/QA", "/6HAT", "/TIGHT", "/DIG", "/PUSHBACK"):
            self.assertIn(cmd, routing_content, f"{cmd} komutu skill-trigger-routing.md içinde kayıtlı olmalıdır")
        self.assertIn("cognitive-counsel-framework", routing_content)

    def test_output_ending_rule_omitted_for_handoff_safety(self):
        content = RULE_FILE.read_text(encoding="utf-8")
        # Kullanıcının direktifi: "planı '7. Çıktı Bitiş Kuralı' olmadan uygulayalım. mevcut handoff sürecimizi riske atmak istemiyorum"
        self.assertNotIn("ÇIKTI BİTİŞ KURALI", content)
        self.assertIn("Pano Sadakati", content)


if __name__ == "__main__":
    unittest.main()
