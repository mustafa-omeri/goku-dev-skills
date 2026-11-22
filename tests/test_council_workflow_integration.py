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

    def test_council_requires_physical_md_plan_file_and_sibling_question(self):
        """/council planı sohbet çıktısı olarak değil ayrı .md plan dosyasında üretmeli ve kardeş projeyi sormalı."""
        content = self.council_skill_file.read_text(encoding="utf-8")
        self.assertIn(".md", content)
        self.assertIn("PLAN.template.md", content)
        self.assertIn("FAA AC 121-24C", content)
        self.assertTrue(
            "kardeş" in content.lower() and "sor" in content.lower(),
            "council/SKILL.md içinde kardeş proje sorusu zorunluluğu yok"
        )

    def test_plan_must_be_physical_md_file_and_faa_ac_121_24c_compliant(self):
        """/plan çıktıları sohbete ham metin olarak basılmamalı, .md dosyası ve FAA AC 121-24C olmalı."""
        import subprocess
        import tempfile

        dev_txt = self.dev_workflow_file.read_text(encoding="utf-8")
        self.assertIn("FAA AC 121-24C", dev_txt)
        self.assertTrue(
            "sohbet çıktısı" in dev_txt.lower() or "chat-only" in dev_txt.lower(),
            "development-workflow.md içinde sohbet çıktısı yasağı yok"
        )

        # check_aviation_docs.py PLAN.template.md üzerinde geçmeli; E2'siz bozuk planı reddetmeli
        gate_script = REPO_ROOT / ".agent" / "skills" / "musgoku" / "scripts" / "check_aviation_docs.py"
        with tempfile.TemporaryDirectory() as tmp:
            tmppath = Path(tmp)
            plans_dir = tmppath / ".agent" / "plans"
            plans_dir.mkdir(parents=True)
            bad_plan = plans_dir / "bad_plan.md"
            bad_plan.write_text("# Kötü Plan\n1. Sadece adım yazıldı çıktı yok\n", encoding="utf-8")
            env = dict(**__import__("os").environ, AGENTS_PROJECT_ROOT=str(tmppath))
            res_bad = subprocess.run(
                [sys.executable, str(gate_script), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
            )
            self.assertNotEqual(res_bad.returncode, 0, "check_aviation_docs.py FAA AC 121-24C eksik planı reddetmeli")
            payload = __import__("json").loads(res_bad.stdout)
            codes = {e["code"] for e in payload.get("errors", [])}
            self.assertTrue({"E1", "E2"}.intersection(codes), f"Beklenen E1/E2 bulunamadı: {codes}")

    def test_main_screen_caveman_faa_and_sprint_end_verify_sprint_prompt(self):
        """Ana ekrana /caveman + FAA AC 121-24C yanıtı ve sprint bitiminde otomatik /verify-sprint sorusu."""
        agents_txt = (REPO_ROOT / ".agent" / "AGENTS.md").read_text(encoding="utf-8")
        aviation_txt = (REPO_ROOT / ".agent" / "rules" / "aviation-documentation-standard.md").read_text(encoding="utf-8")
        verify_sprint_txt = (REPO_ROOT / ".agent" / "skills" / "verify-sprint" / "SKILL.md").read_text(encoding="utf-8")
        routing_txt = (REPO_ROOT / ".agent" / "rules" / "skill-trigger-routing.md").read_text(encoding="utf-8")

        self.assertIn("/caveman", agents_txt)
        self.assertIn("FAA AC 121-24C", agents_txt)
        self.assertIn("/caveman", aviation_txt)
        self.assertIn("`/caveman`", routing_txt)
        self.assertTrue(
            "sorar" in verify_sprint_txt.lower() or "sorulur" in verify_sprint_txt.lower(),
            "verify-sprint/SKILL.md sprint bitiminde kullanıcıya sorma protokolü içermeli"
        )


if __name__ == "__main__":
    unittest.main()
