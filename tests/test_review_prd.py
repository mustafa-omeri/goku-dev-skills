#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""review-prd (prd_review_helper.py) dikiş noktası birim ve CLI regresyon testleri."""
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

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / ".agent" / "skills" / "review-prd" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import prd_review_helper as helper  # noqa: E402


SAMPLE_PRD = """# Bildirim Merkezi ve Akıllı Raporlama PRD

## 1. Amaç
Kullanıcı dostu ve hızlı bir bildirim merkezi kurulacaktır.

## 2. Gereksinimler
- FR-001: Kullanıcı bildirim tercihlerini (e-posta vs push veya webhook) seçebilmelidir.
- FR-002: Yönetici raporları uygun şekilde dışa aktarabilmelidir vb.
- US-003: Gerçek zamanlı bildirim akışı için WebSocket veya SSE alternatifi değerlendirilmelidir.
"""

SAMPLE_PRD_WITH_GHERKIN = """# Güvenli Oturum Yönetimi PRD

## 1. Kapsam
- FR-101: Kullanıcı aktif cihaz oturumlarını iptal edebilir.

```gherkin
Feature: Aktif Oturum İptali
  Scenario: Kullanıcı başka bir cihazı sonlandırır
    Given Kullanıcı oturumlarım sayfasındadır
    When "Sonlandır" butonuna tıklar
    Then Oturum token'ı sunucuda iptal edilir ve listeden kalkar
```
"""


class TestReviewPrdHelper(unittest.TestCase):
    def test_analyze_prd_extracts_requirements_ambiguities_and_council_candidates(self):
        analysis = helper.analyze_prd(SAMPLE_PRD)

        self.assertIn("FR-001", analysis["requirements"])
        self.assertIn("FR-002", analysis["requirements"])
        self.assertIn("US-003", analysis["requirements"])
        self.assertFalse(analysis["has_gherkin"])
        self.assertEqual(analysis["gherkin_scenarios"], 0)
        self.assertGreaterEqual(len(analysis["ambiguities"]), 3)
        self.assertGreaterEqual(len(analysis["council_candidates"]), 1)

        gherkin_analysis = helper.analyze_prd(SAMPLE_PRD_WITH_GHERKIN)
        self.assertTrue(gherkin_analysis["has_gherkin"])
        self.assertEqual(gherkin_analysis["gherkin_scenarios"], 1)

    def test_collect_project_context_reads_core_docs_and_stack(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "sampleWebApp"
            proj.mkdir()
            (proj / "package.json").write_text(
                '{"name": "sampleWebApp", "dependencies": {"react": "^18.0.0"}}',
                encoding="utf-8",
            )
            (proj / "PROJECT_BRIEF.md").write_text(
                "---\nprimary_language: TypeScript\n---\n# Brief\nReact SPA\n",
                encoding="utf-8",
            )
            (proj / "DESIGN.md").write_text(
                "# DESIGN\n- Surface: Light (`Living Surface`)\n",
                encoding="utf-8",
            )

            ctx = helper.collect_project_context(proj)
            self.assertEqual(ctx["project_name"], "sampleWebApp")
            self.assertTrue(ctx["docs"]["PROJECT_BRIEF.md"])
            self.assertTrue(ctx["docs"]["DESIGN.md"])
            self.assertFalse(ctx["docs"]["PRODUCT.md"])
            self.assertIn("TypeScript", ctx["primary_language"])

    def test_build_review_bundle_and_archive_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "sampleApp"
            proj.mkdir()
            (proj / "package.json").write_text('{"name": "sampleApp"}', encoding="utf-8")
            prd_file = proj / "docs" / "new-feature-prd.md"
            prd_file.parent.mkdir(parents=True)
            prd_file.write_text(SAMPLE_PRD, encoding="utf-8")

            bundle = helper.build_review_bundle(project_root=proj, prd_path=prd_file)
            self.assertEqual(bundle["prd_source"], "docs/new-feature-prd.md")
            self.assertIn("FR-001", bundle["prd_analysis"]["requirements"])
            self.assertIn("project_context", bundle)

            archived = helper.archive_prd_review(
                report_text="# PRD Review\nKarar: CONDITIONAL GO\n",
                project_root=proj,
                slug="bildirim-prd",
            )
            self.assertTrue(archived.is_file())
            self.assertTrue(archived.name.startswith("prd_review_bildirim_prd_"))
            self.assertEqual(archived.parent, proj / "docs" / "plans")

    def test_cli_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "cliProj"
            proj.mkdir()
            (proj / "pom.xml").write_text("<project/>", encoding="utf-8")
            prd_file = proj / "prd.md"
            prd_file.write_text(SAMPLE_PRD, encoding="utf-8")

            script = SCRIPTS / "prd_review_helper.py"
            res = subprocess.run(
                [sys.executable, str(script), "--root", str(proj), "--prd", str(prd_file), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(res.returncode, 0, res.stderr + res.stdout)
            payload = json.loads(res.stdout)
            self.assertIn("FR-001", payload["prd_analysis"]["requirements"])
            self.assertEqual(payload["project_context"]["project_name"], "cliProj")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestReviewPrdHelper)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
