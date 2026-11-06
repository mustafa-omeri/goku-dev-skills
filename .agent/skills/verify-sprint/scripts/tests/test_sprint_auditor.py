#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for verify-sprint sprint_auditor.py at its public seam."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
SCRIPTS_DIR = HERE.parent
sys.path.insert(0, str(SCRIPTS_DIR))


def _load_auditor():
    import sprint_auditor  # noqa: E402
    return sprint_auditor


class SprintAuditorSeamTests(unittest.TestCase):
    """Tests sprint_auditor audit logic, findings generation, and audit trail formatting."""

    def test_01_no_sprint_board_returns_skipped(self):
        auditor = _load_auditor()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            res = auditor.audit_sprint(root)
            self.assertEqual(res["status"], "SKIPPED")
            self.assertFalse(res["has_findings"])
            self.assertEqual(len(res["findings"]), 0)

    def test_02_detects_missing_gherkin_and_missing_user_test_findings(self):
        auditor = _load_auditor()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SPRINT_PLAN.md").write_text(
                "## Sprint 12\n**Hedef**: Test Hedef\n**MVP Kapsam**: S12-28\n**Kapsam Dışı**: Yok\n",
                encoding="utf-8",
            )
            (root / "docs").mkdir(parents=True)
            (root / "docs" / "KULLANICI_TEST_REHBERI.md").write_text("# Test Rehberi\n", encoding="utf-8")
            # KANBAN has S12-28 in Yapıldı, but specs/S12-28.feature is missing, and test is placeholder
            (root / "KANBAN.md").write_text(
                "## Bekliyor\n\n## Yapılıyor\n\n## Sınırdı\n\n## Yapıldı\n\n"
                "### S12-28 · Bildirim Gönderimi\n"
                "| alan | değer |\n"
                "|---|---|\n"
                "| durum | Yapıldı |\n"
                "| oncelik | P1 |\n"
                "| sprint | S12 |\n"
                "| gherkin | specs/S12-28.feature#bildirim |\n"
                "| kapi | pytest tests/test_notifications.py |\n"
                "| test | todo |\n"
                "| risk | orta |\n",
                encoding="utf-8",
            )
            res = auditor.audit_sprint(root)
            self.assertEqual(res["status"], "FAILED")
            self.assertTrue(res["has_findings"])
            self.assertGreaterEqual(len(res["findings"]), 1)
            f = res["findings"][0]
            self.assertEqual(f["card_id"], "S12-28")
            # Should flag missing gherkin and placeholder user test
            finding_types = [issue["type"] for issue in f["issues"]]
            self.assertIn("MISSING_GHERKIN", finding_types)
            self.assertIn("INVALID_USER_TEST", finding_types)

    def test_03_passes_clean_sprint_with_zero_findings(self):
        auditor = _load_auditor()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SPRINT_PLAN.md").write_text(
                "## Sprint 12\n**Hedef**: Test Hedef\n**MVP Kapsam**: S12-28\n**Kapsam Dışı**: Yok\n",
                encoding="utf-8",
            )
            (root / "specs").mkdir(parents=True)
            (root / "specs" / "S12-28.feature").write_text(
                "# language: tr\n"
                "Feature: Bildirim\n\n"
                "  Scenario: Bildirim basarili\n"
                "    Given kullanici sisteme giris yapar\n"
                "    When bildirim gonderir\n"
                "    Then bildirim basariyla iletilir\n",
                encoding="utf-8",
            )
            (root / "docs").mkdir(parents=True)
            (root / "docs" / "KULLANICI_TEST_REHBERI.md").write_text(
                "# Test Rehberi\n## S12-28 Bildirim Testi\n1. Bildirim butonuna bas.\n2. Toast mesajını gözle doğrula.\n",
                encoding="utf-8",
            )
            (root / "KANBAN.md").write_text(
                "## Bekliyor\n\n## Yapılıyor\n\n## Sınırdı\n\n## Yapıldı\n\n"
                "### S12-28 · Bildirim Gönderimi\n"
                "| alan | değer |\n"
                "|---|---|\n"
                "| durum | Yapıldı |\n"
                "| oncelik | P1 |\n"
                "| sprint | S12 |\n"
                "| gherkin | specs/S12-28.feature#bildirim-basarili |\n"
                "| kapi | pytest tests/test_notifications.py |\n"
                "| test | Kullanıcı bildirim butonuna basar ve toast mesajını görür |\n"
                "| risk | orta |\n",
                encoding="utf-8",
            )
            res = auditor.audit_sprint(root)
            self.assertEqual(res["status"], "PASSED")
            self.assertFalse(res["has_findings"])
            self.assertEqual(len(res["findings"]), 0)

    def test_04_format_audit_trail_entry(self):
        auditor = _load_auditor()
        entry = auditor.format_audit_trail_entry(
            card_id="S12-28",
            title="Bildirim Gönderimi",
            sprint="12",
            initial_status="Geliştirme tamamlandı, ilk birim testleri yeşil (PASS)",
            findings="specs/S12-28.feature eksik, kullanıcı test adımı placeholder idi",
            fix_applied="Gherkin senaryosu yazıldı ve kullanıcı test adımı somutlaştırıldı",
            tests_run="pytest tests/test_notifications.py",
            recheck_status="Sıfır bulgu (Zero Findings), kart Yapıldı sütununa taşındı ve sprint onaylandı",
        )
        self.assertIn("S12-28", entry)
        self.assertIn("Sprint Doğrulama & Cerrahi Onarım İzlenebilirlik Kaydı", entry)
        self.assertIn("İlk Geliştirme Durumu", entry)
        self.assertIn("/verify-sprint Denetim Bulgusu", entry)
        self.assertIn("Planlanan ve Uygulanan Onarım", entry)
        self.assertIn("Onarım Doğrulama Testleri", entry)
        self.assertIn("İkinci Denetim Sonucu", entry)


if __name__ == "__main__":
    unittest.main()
