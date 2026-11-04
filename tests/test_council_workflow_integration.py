#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_council_workflow_integration.py
LLM Council & Kör Hakemlik Mekanizmasının Tüm Geliştirme Süreçlerine
Kademeli Entegrasyonunu Doğrulayan Regresyon Test Paketi.
"""

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


class TestCouncilWorkflowIntegration(unittest.TestCase):

    def setUp(self):
        self.dev_workflow_file = REPO_ROOT / ".agent" / "rules" / "development-workflow.md"
        self.plan_template_file = REPO_ROOT / ".agent" / "templates" / "PLAN.template.md"
        self.council_skill_file = REPO_ROOT / ".agent" / "skills" / "council" / "SKILL.md"
        self.diagnosing_bugs_file = REPO_ROOT / ".agent" / "skills" / "diagnosing-bugs" / "SKILL.md"
        self.code_review_file = REPO_ROOT / ".agent" / "skills" / "code-review" / "SKILL.md"
        self.sprint_workflow_file = REPO_ROOT / ".agent" / "rules" / "sprint-delivery-workflow.md"

    def test_development_workflow_has_council_in_step_2_table(self):
        """Adım 2 Best Practice tablosunda 2+ mimari alternatif için council bulunmalı."""
        self.assertTrue(self.dev_workflow_file.exists(), "development-workflow.md bulunamadı")
        content = self.dev_workflow_file.read_text(encoding="utf-8")
        self.assertIn("council", content.lower(), "development-workflow.md içinde 'council' geçmiyor")
        self.assertTrue(
            "council" in content and ("alternatif" in content.lower() or "kör hakemlik" in content.lower()),
            "Adım 2 veya Adım 2.1 altında council ve alternatif seçimi eşleşmedi"
        )

    def test_development_workflow_has_council_deliberation_threshold_in_step_2_1(self):
        """Adım 2.1 Uygulama Planı altında Kademeli Konsey Eşiği (Council Deliberation Threshold) yer almalı."""
        content = self.dev_workflow_file.read_text(encoding="utf-8")
        self.assertIn("Council Deliberation Threshold", content, "Adım 2.1 altında Council Deliberation Threshold başlığı yok")
        self.assertIn("Option A", content, "Adım 2.1 altında Option A alternatifi şart koşulmamış")
        self.assertIn("Option B", content, "Adım 2.1 altında Option B alternatifi şart koşulmamış")

    def test_plan_template_has_council_deliberation_section(self):
        """PLAN.template.md içinde Council Deliberation ve Alternatif Yaklaşımlar bölümü olmalı."""
        self.assertTrue(self.plan_template_file.exists(), "PLAN.template.md bulunamadı")
        content = self.plan_template_file.read_text(encoding="utf-8")
        self.assertIn("Council Deliberation", content, "PLAN.template.md içinde Council Deliberation bölümü yok")
        self.assertIn("Option A", content, "PLAN.template.md içinde Option A satırı yok")
        self.assertIn("Option B", content, "PLAN.template.md içinde Option B satırı yok")
        self.assertIn("Borda", content, "PLAN.template.md içinde Borda puanı sütunu/alanı yok")

    def test_plan_template_links_unified_planning_ecosystem(self):
        """PLAN.template.md birleşik planlama ekosistemini (PRD, gap_scanner, KANBAN, TDD) bağlamalı."""
        content = self.plan_template_file.read_text(encoding="utf-8")
        self.assertIn("KANBAN", content, "PLAN.template.md içinde KANBAN kartı bağlantısı yok")
        self.assertIn("TDD", content, "PLAN.template.md içinde TDD dikiş noktası bağlantısı yok")
        self.assertIn("Dikey Dilim", content, "PLAN.template.md içinde Dikey Dilim bağlantısı yok")

    def test_council_skill_documents_5_sdlc_touchpoints(self):
        """council/SKILL.md 5 SDLC temas noktasını belgelemeli."""
        self.assertTrue(self.council_skill_file.exists(), "council/SKILL.md bulunamadı")
        content = self.council_skill_file.read_text(encoding="utf-8")
        self.assertIn("5 SDLC", content, "council/SKILL.md içinde 5 SDLC temas noktası belgelenmemiş")
        self.assertIn("Planlama", content, "council/SKILL.md içinde Planlama (/plan) temas noktası yok")
        self.assertIn("Refactoring", content, "council/SKILL.md içinde Refactoring temas noktası yok")

    def test_diagnosing_bugs_integrates_council_for_conflicting_hypotheses(self):
        """diagnosing-bugs/SKILL.md çelişen hipotezlerde Council deliberation bağlantısı içermeli."""
        self.assertTrue(self.diagnosing_bugs_file.exists(), "diagnosing-bugs/SKILL.md bulunamadı")
        content = self.diagnosing_bugs_file.read_text(encoding="utf-8")
        self.assertTrue(
            "council" in content.lower() or "karpathy-guidelines" in content.lower(),
            "diagnosing-bugs/SKILL.md içinde council/karpathy köprüsü yok"
        )

    def test_code_review_integrates_council_for_standard_vs_spec_disputes(self):
        """code-review/SKILL.md standartlar vs şartname uyuşmazlığında Council hakemliği içermeli."""
        self.assertTrue(self.code_review_file.exists(), "code-review/SKILL.md bulunamadı")
        content = self.code_review_file.read_text(encoding="utf-8")
        self.assertTrue(
            "council" in content.lower() or "hakemlik" in content.lower(),
            "code-review/SKILL.md içinde council/hakemlik köprüsü yok"
        )


if __name__ == "__main__":
    unittest.main()
