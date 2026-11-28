#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TDD dikiş noktası testleri: testsprite_bridge.py ve TestSprite rapor eşleme."""
from __future__ import annotations

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

TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent
FIXTURES_DIR = TESTS_DIR / "fixtures"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import test_spec_scanner as scanner  # noqa: E402
import test_spec_tracker as tracker  # noqa: E402
import testsprite_bridge as bridge  # noqa: E402


SAMPLE_SPEC = """# ACMEPORTAL — Birleşik Kabul Kriterleri & Gherkin Test Spesifikasyonu

## 0. Test Ortamı, Mimari & Auth Sözleşmesi
- **Proje Slug:** `acmePortal`

## 1. Uçtan Uca Kapsam ve İzlenebilirlik Matrisi
| Modül | Kaynak | Route / API Endpoint | AC ID'leri | Scenario ID'leri | Risk | Durum |
|---|---|---|---|---|---|---|
| auth | FR-001 | `/login` | `AC-AUTH-01` | `SC-AUTH-01` | `P0` | `🆕 NEW` |
| projects | US-002 | `/projects`, `POST /api/v1/projects` | `AC-PROJ-01` | `SC-PROJ-01`, `SC-PROJ-02` | `P1` | `🆕 NEW` |

## 2. Modül Bazlı Acceptance Criteria & Gherkin Senaryoları

<!-- TEST-SPEC:MODULE:auth:BEGIN -->
### Modül 1: Auth (`/login`)
- **AC-AUTH-01:** Giriş başarılıdır.

```gherkin
Feature: Auth (/login)

  @p0-critical @smoke
  Scenario: SC-AUTH-01 Gecerli bilgilerle basarili giris
    Given Uygulama /login sayfasindadir
    When Gecerli bilgilerle giris yapilir
    Then Kullanici /projects ekranina yonlendirilir
```
<!-- TEST-SPEC:MODULE:auth:END -->

<!-- TEST-SPEC:MODULE:projects:BEGIN -->
### Modül 2: Projects (`/projects`, `POST /api/v1/projects`)
- **AC-PROJ-01:** Proje listeleme ve oluşturma çalışır.

```gherkin
Feature: Projects (/projects)

  @p1-high @e2e
  Scenario: SC-PROJ-01 Yonetici proje listeler ve yeni proje olusturur
    Given Kullanici ADMIN rolundedir ve /projects sayfasindadir
    When Yeni proje gonderilip POST /api/v1/projects cagrilir
    Then Sunucu 201 doner ve liste guncellenir

  @p2-medium @negative
  Scenario: SC-PROJ-02 Yetkisiz kullanici reddedilir
    Given Kullanici EMPLOYEE rolundedir
    When POST /api/v1/projects cagrilir
    Then Sunucu 403 doner
```
<!-- TEST-SPEC:MODULE:projects:END -->
"""


def _setup_workspace_with_peer(base: Path):
    fe = base / "acme-frontend"
    be = base / "acme-backend"
    (fe / "src" / "pages").mkdir(parents=True)
    (fe / "docs" / "testing").mkdir(parents=True)
    (be / "src" / "main" / "java" / "com" / "acme").mkdir(parents=True)

    (fe / "package.json").write_text(
        json.dumps({"name": "acme-frontend", "dependencies": {"react": "^18.2.0", "react-router-dom": "^6.20.0"}}),
        encoding="utf-8",
    )
    (fe / "src" / "App.tsx").write_text(
        "import { Routes, Route } from 'react-router-dom';\nexport function App(){ return <Routes><Route path=\"/login\" /><Route path=\"/projects\" /></Routes>; }\n",
        encoding="utf-8",
    )
    ctrl = be / "src" / "main" / "java" / "com" / "acme" / "ProjectController.java"
    ctrl.write_text(
        "@RestController\n@RequestMapping(\"/api/v1/projects\")\npublic class ProjectController {\n  @PostMapping(\"\")\n  public String create(){ return \"ok\"; }\n}\n",
        encoding="utf-8",
    )
    spec_path = fe / "docs" / "testing" / "ACME_ACCEPTANCE_TEST_SPEC.md"
    spec_path.write_text(SAMPLE_SPEC, encoding="utf-8")
    inv = scanner.build_test_inventory(fe, peers=[be])
    inv_path = fe / "docs" / "testing" / "test-inventory.json"
    inv_path.write_text(json.dumps(inv, indent=2), encoding="utf-8")
    state_path = fe / "docs" / "testing" / "test-spec-state.json"
    tracker.sync_state_from_spec(spec_path, state_path, inv)
    return fe, be, spec_path, state_path, inv_path


class TestSpriteBridgeTests(unittest.TestCase):
    def test_to_plan_filters_pass_backs_up_existing_plan_and_supports_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            fe, _, spec_path, state_path, _ = _setup_workspace_with_peer(Path(tmp))
            # SC-AUTH-01 PASS olsun, diğer ikisi NEW kalsın
            tracker.record_execution_results(state_path, {"SC-AUTH-01": "PASS"}, runner="testsprite")

            plan_path = fe / "testsprite_tests" / "testsprite_frontend_test_plan.json"
            plan_path.parent.mkdir(parents=True)
            original_plan = (FIXTURES_DIR / "testsprite_plan_sample.json").read_text(encoding="utf-8")
            plan_path.write_text(original_plan, encoding="utf-8")

            res = bridge.export_testsprite_plan(
                spec_path=spec_path,
                state_path=state_path,
                plan_path=plan_path,
                batch_size=1,
                batch_index=0,
            )
            self.assertTrue((plan_path.with_suffix(".json.bak")).is_file())
            self.assertEqual(res["total_delta"], 2)
            self.assertEqual(res["total_batches"], 2)
            self.assertEqual(res["batch_test_ids"], ["TC001"])

            written = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(len(written), 1)
            self.assertTrue(written[0]["title"].startswith("SC-PROJ-01"))
            self.assertEqual(written[0]["priority"], "High")
            self.assertGreaterEqual(len(written[0]["steps"]), 3)
            self.assertEqual(written[0]["steps"][-1]["type"], "assertion")

            sc_map = json.loads((plan_path.parent / "sc_map.json").read_text(encoding="utf-8"))
            self.assertEqual(sc_map["tc_to_sc"]["TC001"], "SC-PROJ-01")
            self.assertEqual(sc_map["tc_to_sc"]["TC002"], "SC-PROJ-02")

    def test_parse_testsprite_report_supports_multiline_markdown_and_json_with_sc_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            sc_map = tmp_p / "sc_map.json"
            sc_map.write_text(
                json.dumps({"tc_to_sc": {"TC001": "SC-AUTH-01", "TC002": "SC-PROJ-01"}}),
                encoding="utf-8",
            )

            # 1. Çok satırlı raw_report.md (başlıkta SC-* olsa bile Status 5+ satır aşağıda)
            md_report = tmp_p / "raw_report.md"
            md_report.write_text((FIXTURES_DIR / "testsprite_raw_report.md.txt").read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual(
                tracker.parse_testsprite_report(md_report, sc_map_path=sc_map),
                {"SC-AUTH-01": "PASS", "SC-PROJ-01": "FAIL"},
            )

            # 2. Başlıkta yalnız TC001/TC002 olan (SC-* yazmayan) rapor da sc_map ile eşleşmeli
            tc_only_md = tmp_p / "tc_only.md"
            tc_only_md.write_text(
                "#### Test TC001 Login\n- **Status:** ✅ Passed\n---\n#### Test TC002 Create\n- **Status:** ❌ Failed\n",
                encoding="utf-8",
            )
            self.assertEqual(
                tracker.parse_testsprite_report(tc_only_md, sc_map_path=sc_map),
                {"SC-AUTH-01": "PASS", "SC-PROJ-01": "FAIL"},
            )

            # 3. TestSprite tmp/test_results.json formatı
            json_report = tmp_p / "test_results.json"
            json_report.write_text((FIXTURES_DIR / "testsprite_results.json").read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual(
                tracker.parse_testsprite_report(json_report, sc_map_path=sc_map),
                {"SC-AUTH-01": "PASS", "SC-PROJ-01": "FAIL"},
            )

    def test_record_cli_exits_nonzero_when_nonempty_report_matches_zero_scenarios(self):
        with tempfile.TemporaryDirectory() as tmp:
            fe, _, _, state_path, _ = _setup_workspace_with_peer(Path(tmp))
            bad_report = fe / "empty_match_report.md"
            bad_report.write_text("# Report\n#### Test TC999 Unknown test\n- **Status:** ✅ Passed\n", encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "test_spec_tracker.py"),
                    "record",
                    "--state",
                    str(state_path),
                    "--import-testsprite",
                    str(bad_report),
                    "--runner",
                    "testsprite",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)

    def test_triage_attributes_endpoint_failure_to_sibling_backend_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            fe, be, _, state_path, inv_path = _setup_workspace_with_peer(Path(tmp))
            tracker.record_execution_results(state_path, {"SC-AUTH-01": "PASS", "SC-PROJ-01": "FAIL"}, runner="testsprite")

            report_json = fe / "testsprite_tests" / "tmp" / "test_results.json"
            report_json.parent.mkdir(parents=True)
            report_json.write_text((FIXTURES_DIR / "testsprite_results.json").read_text(encoding="utf-8"), encoding="utf-8")
            sc_map = fe / "testsprite_tests" / "sc_map.json"
            sc_map.write_text(json.dumps({"tc_to_sc": {"TC001": "SC-AUTH-01", "TC002": "SC-PROJ-01"}}), encoding="utf-8")

            triage_res = bridge.triage_failed_scenarios(
                state_path=state_path,
                inventory_path=inv_path,
                report_path=report_json,
                sc_map_path=sc_map,
            )
            self.assertEqual(triage_res["failed_count"], 1)
            item = triage_res["items"][0]
            self.assertEqual(item["scenario_id"], "SC-PROJ-01")
            self.assertEqual(item["repo_role"], "backend-peer")
            self.assertIn("acme-backend", item["owner_repo"])
            self.assertTrue(any("ProjectController.java" in f for f in item["suspect_files"]))
            self.assertIn("POST /api/v1/projects", item["endpoint_refs"])
            self.assertIn("acme-backend", item["recommended_action"])
            self.assertEqual(item["failure_class"], "BE_PEER_DEFECT")
            self.assertEqual(item["verification_runner"], "testsprite")

    def test_triage_classifies_env_auth_seed_non_ui_observable_and_fe_defect(self):
        with tempfile.TemporaryDirectory() as tmp:
            fe, _, _, state_path, inv_path = _setup_workspace_with_peer(Path(tmp))
            tracker.record_execution_results(
                state_path,
                {"SC-AUTH-01": "FAIL", "SC-PROJ-01": "FAIL", "SC-PROJ-02": "FAIL"},
                runner="testsprite",
            )
            report_json = fe / "testsprite_tests" / "tmp" / "test_results.json"
            report_json.parent.mkdir(parents=True)
            report_json.write_text(
                json.dumps(
                    [
                        {
                            "title": "TC001 SC-AUTH-01 Login",
                            "testStatus": "FAILED",
                            "testError": "TEST FAILURE\nSubmitting blank login form did not display validation feedback.",
                        },
                        {
                            "title": "TC002 SC-PROJ-01 Admin project flow",
                            "testStatus": "FAILED",
                            "testError": "TEST FAILURE\nThe current page displayed “Bu işlemi yapmak için yetkiniz bulunmuyor” while signed in as Goku Admin.",
                        },
                        {
                            "title": "TC003 SC-PROJ-02 Unauthorized check",
                            "testStatus": "FAILED",
                            "testError": "TEST BLOCKED\nThe employee interface does not expose project creation, so the specified protected API behavior could not be exercised or verified from the page.",
                        },
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            sc_map = fe / "testsprite_tests" / "sc_map.json"
            sc_map.write_text(
                json.dumps({"tc_to_sc": {"TC001": "SC-AUTH-01", "TC002": "SC-PROJ-01", "TC003": "SC-PROJ-02"}}),
                encoding="utf-8",
            )

            res = bridge.triage_failed_scenarios(
                state_path=state_path,
                inventory_path=inv_path,
                report_path=report_json,
                sc_map_path=sc_map,
            )
            by_id = {it["scenario_id"]: it for it in res["items"]}
            self.assertEqual(by_id["SC-AUTH-01"]["failure_class"], "FE_DEFECT")
            self.assertEqual(by_id["SC-AUTH-01"]["verification_runner"], "testsprite")
            self.assertEqual(by_id["SC-PROJ-01"]["failure_class"], "ENV_AUTH_SEED")
            self.assertEqual(by_id["SC-PROJ-01"]["remediation_route"], "fix-bug")
            self.assertEqual(by_id["SC-PROJ-02"]["failure_class"], "NON_UI_OBSERVABLE")
            self.assertEqual(by_id["SC-PROJ-02"]["verification_runner"], "local_api_or_unit")
            self.assertEqual(res["summary_by_class"]["ENV_AUTH_SEED"], 1)
            self.assertEqual(res["summary_by_class"]["NON_UI_OBSERVABLE"], 1)
            self.assertEqual(res["summary_by_class"]["FE_DEFECT"], 1)
            self.assertEqual(set(res["rerun_eligible_scenarios"]), {"SC-AUTH-01", "SC-PROJ-01"})
            self.assertEqual(res["local_verify_scenarios"], ["SC-PROJ-02"])

    def test_to_plan_scenarios_subset_filters_only_requested_scenarios(self):
        with tempfile.TemporaryDirectory() as tmp:
            fe, _, spec_path, state_path, _ = _setup_workspace_with_peer(Path(tmp))
            plan_path = fe / "testsprite_tests" / "testsprite_frontend_test_plan.json"
            res = bridge.export_testsprite_plan(
                spec_path=spec_path,
                state_path=state_path,
                plan_path=plan_path,
                only_scenarios=["SC-PROJ-01"],
            )
            self.assertEqual(res["total_delta"], 1)
            self.assertEqual(res["batch_test_ids"], ["TC001"])
            written = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(len(written), 1)
            self.assertTrue(written[0]["title"].startswith("SC-PROJ-01"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
