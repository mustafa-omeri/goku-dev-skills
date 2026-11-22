#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test-spec-generator (/test-spec) dikiş noktası birim ve CLI regresyon testleri."""
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

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / ".agent" / "skills" / "test-spec-generator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import test_spec_scanner as scanner  # noqa: E402
import check_test_spec as checker  # noqa: E402
import test_spec_tracker as tracker  # noqa: E402


def _create_sample_fullstack_project(proj: Path) -> None:
    (proj / "src" / "pages").mkdir(parents=True)
    (proj / "src" / "api").mkdir(parents=True)
    (proj / "backend" / "src" / "main" / "java" / "com" / "acme").mkdir(parents=True)
    (proj / "docs" / "APIs").mkdir(parents=True)
    (proj / "specs").mkdir(parents=True)

    (proj / "package.json").write_text(
        json.dumps({"name": "acmePortal", "dependencies": {"react": "^18.2.0", "react-router-dom": "^6.20.0"}}),
        encoding="utf-8",
    )
    (proj / "PROJECT_BRIEF.md").write_text(
        "---\nproject: acmePortal\nprimary_language: tr\n---\n# Acme Portal\nReact + Spring Boot\n",
        encoding="utf-8",
    )
    (proj / "PRODUCT.md").write_text(
        "# Ürün Gereksinimleri\n- FR-001: Kullanıcı e-posta ve parola ile oturum açar.\n- US-002: Yönetici proje listesini görüntüler ve yeni proje ekler.\n",
        encoding="utf-8",
    )
    (proj / "docs" / "APIs" / "projects.md").write_text(
        "# Projects API\n- `GET /api/v1/projects`\n- `POST /api/v1/projects`\n",
        encoding="utf-8",
    )
    (proj / "specs" / "AUTH-01.feature").write_text(
        "# language: tr\nFeature: Kimlik Doğrulama\n  Scenario: Geçerli giriş\n    Given Kullanıcı login sayfasındadır\n    When Geçerli bilgilerle giriş yapar\n    Then Dashboard açılır\n",
        encoding="utf-8",
    )
    (proj / "src" / "App.tsx").write_text(
        """
import { Routes, Route } from 'react-router-dom';
export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/projects" element={<ProjectsPage />} />
    </Routes>
  );
}
""",
        encoding="utf-8",
    )
    (proj / "backend" / "src" / "main" / "java" / "com" / "acme" / "ProjectController.java").write_text(
        """
@RestController
@RequestMapping("/api/v1/projects")
public class ProjectController {
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("")
    public List<String> list() { return List.of(); }

    @PreAuthorize("hasRole('ADMIN')")
    @PostMapping("")
    public String create() { return "ok"; }
}
""",
        encoding="utf-8",
    )


VALID_TEST_SPEC = """# ACMEPORTAL — Birleşik Kabul Kriterleri & Gherkin Test Spesifikasyonu

## 0. Test Ortamı, Mimari & Auth Sözleşmesi
- **Proje Slug:** `acmePortal` · **Dil:** `tr`
- **Stack:** React SPA + Spring Boot API
- **Roller:** `ADMIN`

## 1. Uçtan Uca Kapsam ve İzlenebilirlik Matrisi
| Modül | Kaynak | Route / API Endpoint | AC ID'leri | Scenario ID'leri | Etiketler |
|---|---|---|---|---|---|
| Auth | `PRODUCT.md` FR-001 | `/login` | `AC-AUTH-01` | `SC-AUTH-01`, `SC-AUTH-02` | `@smoke @negative` |
| Projects | `PRODUCT.md` US-002 | `/projects`, `GET /api/v1/projects`, `POST /api/v1/projects` | `AC-PROJ-01` | `SC-PROJ-01`, `SC-PROJ-02` | `@e2e @rbac @api` |

## 2. Modül Bazlı Acceptance Criteria & Gherkin Senaryoları

### Modül 1: Auth (`FR-001`, `/login`)
- **AC-AUTH-01:** Geçerli kimlik bilgileriyle giriş yapan kullanıcı `/projects` ekranına yönlendirilir; hatalı parolada `401` döner ve formda hata mesajı gösterilir.

```gherkin
# language: tr
Feature: Kimlik Doğrulama (/login)

  Background:
    Given Uygulama /login sayfasında çalışmaktadır

  @smoke @happy-path
  Scenario: SC-AUTH-01 Geçerli bilgilerle başarılı giriş
    When Kullanıcı geçerli e-posta ve parola ile giriş formunu gönderir
    Then Sunucu 200 döner ve kullanıcı /projects rotasına yönlendirilir

  @negative @validation
  Scenario: SC-AUTH-02 Hatalı parola ile giriş reddedilir
    When Kullanıcı hatalı parola ile giriş formunu gönderir
    Then Sunucu 401 döner ve ekranda hata uyarısı görünür
```

### Modül 2: Projects (`US-002`, `/projects`, `/api/v1/projects`)
- **AC-PROJ-01:** Yalnızca `ADMIN` rolündeki kullanıcılar `GET /api/v1/projects` ve `POST /api/v1/projects` uç noktalarını çağırabilir; yetkisiz roller `403` alır.

```gherkin
Feature: Proje Yönetimi (/projects)

  @e2e @api
  Scenario: SC-PROJ-01 Yönetici proje listeler ve yeni proje oluşturur
    Given Kullanıcı ADMIN rolüyle oturum açmıştır ve /projects sayfasındadır
    When GET /api/v1/projects verisi yüklendikten sonra yeni proje formunu doldurup POST /api/v1/projects isteğini tetikler
    Then Sunucu 201 döner ve yeni proje listede refresh olmadan görünür

  @security @rbac @negative
  Scenario: SC-PROJ-02 Yetkisiz kullanıcı proje oluşturamaz
    Given Kullanıcı ADMIN rolüne sahip değildir
    When POST /api/v1/projects uç noktasına istek gönderir
    Then Sunucu 403 Forbidden döner
```

## 3. Çapraz Sistem & E2E Senaryoları
- `SC-AUTH-01` → `SC-PROJ-01` uçtan uca oturum ve veri kalıcılığı akışı doğrulanır.

## 4. Kapsam Dışı, Varsayımlar & Kod-Doküman Çelişkileri
- Tespit edilen kritik kod-doküman çelişkisi yoktur.

## 5. Otomasyon Çalıştırma Komutları & Dışa Aktarım
- Saf `.feature` üretimi: `python .agent/skills/test-spec-generator/scripts/test_spec_scanner.py --export-feature docs/testing/ACMEPORTAL_ACCEPTANCE_TEST_SPEC.md --out specs/ACMEPORTAL_ALL.feature`
"""


class TestSpecGeneratorTests(unittest.TestCase):
    def test_build_test_inventory_extracts_code_docs_roles_and_features(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "acmePortal"
            proj.mkdir()
            _create_sample_fullstack_project(proj)

            inv = scanner.build_test_inventory(proj)
            self.assertEqual(inv["project_name"], "acmePortal")
            self.assertEqual(inv["primary_language"], "tr")
            self.assertIn("/login", inv["routes"])
            self.assertIn("/projects", inv["routes"])

            ep_sigs = {f"{e['method']} {e['path']}" for e in inv["endpoints"]}
            self.assertIn("GET /api/v1/projects", ep_sigs)
            self.assertIn("POST /api/v1/projects", ep_sigs)
            self.assertIn("ADMIN", inv["roles"])
            self.assertIn("FR-001", inv["requirements"])
            self.assertIn("US-002", inv["requirements"])
            self.assertGreaterEqual(len(inv["existing_features"]), 1)
            self.assertTrue(inv["docs"]["PRODUCT.md"])
            self.assertTrue(inv["docs"]["PROJECT_BRIEF.md"])

    def test_validate_test_spec_accepts_complete_spec_and_rejects_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "acmePortal"
            proj.mkdir()
            _create_sample_fullstack_project(proj)
            inv = scanner.build_test_inventory(proj)

            spec_path = proj / "docs" / "testing" / "ACMEPORTAL_ACCEPTANCE_TEST_SPEC.md"
            spec_path.parent.mkdir(parents=True)
            spec_path.write_text(VALID_TEST_SPEC, encoding="utf-8")

            ok_res = checker.validate_test_spec(spec_path, inventory=inv)
            self.assertEqual(ok_res["status"], "PASS", ok_res)
            self.assertEqual(ok_res["errors"], [])

            # Eksik kapsama (POST /api/v1/projects silinir + RBAC senaryosu/etiketi tamamen çıkarılır)
            incomplete_spec = (
                VALID_TEST_SPEC.replace("POST /api/v1/projects", "REMOVED_ENDPOINT")
                .replace("@security", "@e2e")
                .replace("@rbac", "@smoke")
                .replace("403", "200")
            )
            bad_path = proj / "docs" / "testing" / "BAD_SPEC.md"
            bad_path.write_text(incomplete_spec, encoding="utf-8")

            bad_res = checker.validate_test_spec(bad_path, inventory=inv)
            self.assertEqual(bad_res["status"], "FAIL")
            codes = {e["code"] for e in bad_res["errors"]}
            self.assertIn("E6_UNCOVERED_SURFACE", codes)
            self.assertIn("E7_MISSING_RBAC_SCENARIOS", codes)

    def test_validate_test_spec_rejects_placeholders_and_invalid_gherkin(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "SPEC.md"
            spec_path.write_text(
                "# Test\n## 0. Test Ortamı, Mimari & Auth Sözleşmesi\n<doldur: port>\n## 1. İzlenebilirlik Matrisi\nTODO\n",
                encoding="utf-8",
            )
            res = checker.validate_test_spec(spec_path)
            self.assertEqual(res["status"], "FAIL")
            codes = {e["code"] for e in res["errors"]}
            self.assertIn("E3_PLACEHOLDER_LEAK", codes)
            self.assertIn("E4_INVALID_GHERKIN", codes)
            self.assertIn("E5_MISSING_ACCEPTANCE_CRITERIA", codes)

    def test_export_feature_file_extracts_all_gherkin_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "ACCEPTANCE_TEST_SPEC.md"
            spec_path.write_text(VALID_TEST_SPEC, encoding="utf-8")
            out_feature = Path(tmp) / "ACMEPORTAL_ALL.feature"

            exported = scanner.export_feature_file(spec_path, out_feature)
            self.assertTrue(out_feature.is_file())
            self.assertEqual(exported["feature_count"], 2)
            self.assertEqual(exported["scenario_count"], 4)
            txt = out_feature.read_text(encoding="utf-8")
            self.assertIn("Feature: Kimlik Doğrulama (/login)", txt)
            self.assertIn("Feature: Proje Yönetimi (/projects)", txt)
            self.assertIn("Scenario: SC-PROJ-02 Yetkisiz kullanıcı proje oluşturamaz", txt)

    def test_cli_end_to_end_scanner_checker_and_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "cliProj"
            proj.mkdir()
            _create_sample_fullstack_project(proj)

            inv_file = proj / "inv.json"
            scan_cmd = [
                sys.executable,
                str(SCRIPTS_DIR / "test_spec_scanner.py"),
                "--root",
                str(proj),
                "--json",
                "--out",
                str(inv_file),
            ]
            res_scan = subprocess.run(scan_cmd, capture_output=True, text=True)
            self.assertEqual(res_scan.returncode, 0, res_scan.stderr)
            self.assertTrue(inv_file.is_file())

            spec_path = proj / "docs" / "testing" / "CLIPROJ_ACCEPTANCE_TEST_SPEC.md"
            spec_path.parent.mkdir(parents=True)
            spec_path.write_text(VALID_TEST_SPEC, encoding="utf-8")

            chk_cmd = [
                sys.executable,
                str(SCRIPTS_DIR / "check_test_spec.py"),
                "--spec",
                str(spec_path),
                "--inventory",
                str(inv_file),
                "--json",
            ]
            res_chk = subprocess.run(chk_cmd, capture_output=True, text=True)
            self.assertEqual(res_chk.returncode, 0, res_chk.stdout + res_chk.stderr)

    # --- v2 Artımlı Takip, PASS Referans Defteri, Cerrahi Yama & Delta Export Testleri ---

    def _bootstrap_v2_project(self, proj: Path):
        _create_sample_fullstack_project(proj)
        spec_path = proj / "docs" / "testing" / "ACMEPORTAL_ACCEPTANCE_TEST_SPEC.md"
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        anchored_spec = (
            VALID_TEST_SPEC.replace(
                "### Modül 1: Auth",
                "<!-- TEST-SPEC:MODULE:login:BEGIN -->\n### Modül 1: Auth",
            )
            .replace(
                "### Modül 2: Projects",
                "<!-- TEST-SPEC:MODULE:login:END -->\n\n<!-- TEST-SPEC:MODULE:projects:BEGIN -->\n### Modül 2: Projects",
            )
            .replace(
                "## 3. Çapraz Sistem",
                "<!-- TEST-SPEC:MODULE:projects:END -->\n\n## 3. Çapraz Sistem",
            )
        )
        spec_path.write_text(anchored_spec, encoding="utf-8")
        state_path = proj / "docs" / "testing" / "test-spec-state.json"
        inv = scanner.build_test_inventory(proj)
        tracker.sync_state_from_spec(spec_path, state_path, inv)
        return spec_path, state_path, inv

    def test_v2_unchanged_fast_path_noop_and_minor_css_change_preserves_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "acmePortal"
            proj.mkdir()
            spec_path, state_path, _ = self._bootstrap_v2_project(proj)

            tracker.record_execution_results(
                state_path,
                {"SC-AUTH-01": "PASS", "SC-AUTH-02": "PASS", "SC-PROJ-01": "PASS", "SC-PROJ-02": "PASS"},
                runner="testsprite",
                commit="abc1234",
                evidence_ref="testsprite_tests/report.md",
            )

            # 1. Hiç değişiklik yokken -> NO_OP
            plan_noop = tracker.plan_incremental_update(proj, state_path)
            self.assertEqual(plan_noop["mode"], "NO_OP")
            self.assertFalse(plan_noop["has_changes"])

            # 2. Yalnızca yorum / CSS ekle (Minor değişiklik) -> PASS korunur, yeniden üretim yok
            app_tsx = proj / "src" / "App.tsx"
            app_tsx.write_text(
                app_tsx.read_text(encoding="utf-8") + "\n// sadece kozmetik yorum ve className tweak\n",
                encoding="utf-8",
            )
            plan_minor = tracker.plan_incremental_update(proj, state_path)
            self.assertEqual(plan_minor["mode"], "INCREMENTAL")
            self.assertNotIn("MAJOR", [m["classification"] for m in plan_minor["modules"].values()])

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["scenarios"]["SC-AUTH-01"]["status"], "PASS")
            self.assertEqual(state["scenarios"]["SC-AUTH-01"]["pass_ref"]["runner"], "testsprite")

    def test_v2_major_contract_change_marks_only_affected_module_and_transitions_pass_to_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "acmePortal"
            proj.mkdir()
            _, state_path, _ = self._bootstrap_v2_project(proj)

            tracker.record_execution_results(
                state_path,
                {"SC-AUTH-01": "PASS", "SC-PROJ-01": "PASS", "SC-PROJ-02": "PASS"},
                runner="playwright",
                commit="111aaaa",
                evidence_ref="pw-report.json",
            )

            # ProjectController'a yeni endpoint + rol değişimi (MAJOR)
            ctrl = proj / "backend" / "src" / "main" / "java" / "com" / "acme" / "ProjectController.java"
            ctrl.write_text(
                ctrl.read_text(encoding="utf-8").replace(
                    "public String create() { return \"ok\"; }",
                    "public String create() { return \"ok\"; }\n\n    @PreAuthorize(\"hasRole('SUPERADMIN')\")\n    @DeleteMapping(\"/{id}\")\n    public void remove() {}\n",
                ),
                encoding="utf-8",
            )

            plan = tracker.plan_incremental_update(proj, state_path)
            self.assertEqual(plan["mode"], "INCREMENTAL")
            self.assertTrue(plan["has_changes"])
            self.assertEqual(plan["modules"]["projects"]["classification"], "MAJOR")
            self.assertNotEqual(plan["modules"].get("login", {}).get("classification"), "MAJOR")

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["scenarios"]["SC-AUTH-01"]["status"], "PASS")
            self.assertEqual(state["scenarios"]["SC-PROJ-01"]["status"], "STALE")
            self.assertEqual(state["scenarios"]["SC-PROJ-01"]["last_pass_ref"]["runner"], "playwright")
            self.assertEqual(state["scenarios"]["SC-PROJ-01"]["last_pass_ref"]["verified_commit"], "111aaaa")

    def test_v2_record_results_adapters_and_flaky_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "acmePortal"
            proj.mkdir()
            _, state_path, _ = self._bootstrap_v2_project(proj)

            # JUnit XML adaptörü
            junit_xml = proj / "junit.xml"
            junit_xml.write_text(
                '<testsuite><testcase name="SC-AUTH-01 Geçerli giriş" /><testcase name="SC-AUTH-02 Hatalı parola"><failure message="401 expected" /></testcase></testsuite>',
                encoding="utf-8",
            )
            junit_res = tracker.parse_junit_xml(junit_xml)
            self.assertEqual(junit_res, {"SC-AUTH-01": "PASS", "SC-AUTH-02": "FAIL"})

            # Playwright JSON adaptörü
            pw_json = proj / "pw.json"
            pw_json.write_text(
                json.dumps({"suites": [{"specs": [{"title": "SC-PROJ-01 create", "ok": True}, {"title": "SC-PROJ-02 rbac", "ok": False}]}]}),
                encoding="utf-8",
            )
            self.assertEqual(tracker.parse_playwright_json(pw_json), {"SC-PROJ-01": "PASS", "SC-PROJ-02": "FAIL"})

            # Cucumber JSON adaptörü
            cuc_json = proj / "cucumber.json"
            cuc_json.write_text(
                json.dumps([{"elements": [{"name": "SC-AUTH-01 login", "steps": [{"result": {"status": "passed"}}]}]}]),
                encoding="utf-8",
            )
            self.assertEqual(tracker.parse_cucumber_json(cuc_json), {"SC-AUTH-01": "PASS"})

            # TestSprite rapor adaptörü
            ts_md = proj / "testsprite-report.md"
            ts_md.write_text("- SC-AUTH-01: PASS\n- SC-AUTH-02: FAIL\n", encoding="utf-8")
            self.assertEqual(tracker.parse_testsprite_report(ts_md), {"SC-AUTH-01": "PASS", "SC-AUTH-02": "FAIL"})

            # Flaky tespiti: PASS -> FAIL -> PASS salınımı
            tracker.record_execution_results(state_path, {"SC-AUTH-01": "PASS"}, runner="ci")
            tracker.record_execution_results(state_path, {"SC-AUTH-01": "FAIL"}, runner="ci")
            tracker.record_execution_results(state_path, {"SC-AUTH-01": "PASS"}, runner="ci")
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["scenarios"]["SC-AUTH-01"]["status"], "FLAKY")

    def test_v2_surgical_patch_module_preserves_untouched_modules_and_monotonic_seq(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "acmePortal"
            proj.mkdir()
            spec_path, state_path, _ = self._bootstrap_v2_project(proj)

            before = spec_path.read_text(encoding="utf-8")
            auth_marker_block = before.split("<!-- TEST-SPEC:MODULE:login:BEGIN -->")[1].split("<!-- TEST-SPEC:MODULE:login:END -->")[0]

            new_projects_md = (
                "### Modül 2: Projects (`US-002`, `/projects`, `/api/v1/projects`)\n"
                "- **AC-PROJ-01:** Güncel proje silme ve oluşturma kuralı.\n\n"
                "```gherkin\n"
                "Feature: Proje Yönetimi (/projects)\n\n"
                "  @e2e @api\n"
                "  Scenario: SC-PROJ-01 Yönetici proje listeler ve yeni proje oluşturur\n"
                "    Given Kullanıcı ADMIN rolüyle oturum açmıştır\n"
                "    When GET /api/v1/projects ve POST /api/v1/projects çalışır\n"
                "    Then Sunucu 201 döner\n\n"
                "  @security @rbac @negative\n"
                "  Scenario: SC-PROJ-02 Yetkisiz kullanıcı proje oluşturamaz\n"
                "    Given Kullanıcı ADMIN rolüne sahip değildir\n"
                "    When POST /api/v1/projects istek gönderir\n"
                "    Then Sunucu 403 döner\n\n"
                "  @api @perf\n"
                "  Scenario: SC-PROJ-03 Proje silme idempotency kontrolü\n"
                "    Given Proje kaydı mevcuttur\n"
                "    When DELETE /api/v1/projects/1 iki kez çağrılır\n"
                "    Then İlk çağrı 204 ikinci çağrı 404 döner\n"
                "```"
            )
            tracker.patch_module_section(spec_path, "projects", new_projects_md)
            after = spec_path.read_text(encoding="utf-8")
            auth_after = after.split("<!-- TEST-SPEC:MODULE:login:BEGIN -->")[1].split("<!-- TEST-SPEC:MODULE:login:END -->")[0]
            self.assertEqual(auth_marker_block, auth_after)
            self.assertIn("SC-PROJ-03", after)

            inv = scanner.build_test_inventory(proj)
            state = tracker.sync_state_from_spec(spec_path, state_path, inv)
            self.assertGreaterEqual(state["next_seq"]["PROJ"], 4)

    def test_v2_export_delta_excludes_valid_pass_and_supports_include_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "acmePortal"
            proj.mkdir()
            spec_path, state_path, _ = self._bootstrap_v2_project(proj)

            tracker.record_execution_results(
                state_path,
                {"SC-AUTH-01": "PASS", "SC-AUTH-02": "PASS", "SC-PROJ-01": "FAIL"},
                runner="testsprite",
            )
            # SC-PROJ-02 henüz NEW, SC-PROJ-01 FAIL, SC-AUTH-01/02 PASS (SC-AUTH-01 @smoke)
            delta_md = proj / "docs" / "testing" / "DELTA.md"
            delta_feat = proj / "specs" / "DELTA.feature"

            res = tracker.export_delta_spec(
                spec_path,
                state_path,
                out_md=delta_md,
                out_feature=delta_feat,
                include_smoke=False,
            )
            self.assertEqual(set(res["included_scenarios"]), {"SC-PROJ-01", "SC-PROJ-02"})
            feat_txt = delta_feat.read_text(encoding="utf-8")
            self.assertNotIn("SC-AUTH-01", feat_txt)
            self.assertNotIn("SC-AUTH-02", feat_txt)
            self.assertIn("SC-PROJ-01", feat_txt)
            self.assertIn("SC-PROJ-02", feat_txt)

            res_smoke = tracker.export_delta_spec(
                spec_path,
                state_path,
                out_feature=delta_feat,
                include_smoke=True,
            )
            self.assertIn("SC-AUTH-01", res_smoke["included_scenarios"])
            self.assertNotIn("SC-AUTH-02", res_smoke["included_scenarios"])

    def test_v2_checker_detects_state_drift_stale_pass_claim_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "acmePortal"
            proj.mkdir()
            spec_path, state_path, inv = self._bootstrap_v2_project(proj)

            state = json.loads(state_path.read_text(encoding="utf-8"))
            # Zorla STALE kontrat sapması yarat ama status'u PASS bırak (E9) + spec'ten senaryo çıkar (E8) + mükerrer ID ekle (E10)
            state["scenarios"]["SC-AUTH-01"]["status"] = "PASS"
            state["scenarios"]["SC-AUTH-01"]["pass_ref"] = {
                "runner": "testsprite",
                "verified_contract_hash": "sha256:old_hash",
            }
            state["scenarios"]["SC-AUTH-01"]["contract_hash"] = "sha256:new_hash"
            state["scenarios"]["SC-GHOST-99"] = {"module": "auth", "status": "NEW"}
            state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

            dup_spec = spec_path.read_text(encoding="utf-8").replace(
                "Scenario: SC-AUTH-02 Hatalı parola ile giriş reddedilir",
                "Scenario: SC-AUTH-01 Hatalı parola ile giriş reddedilir",
            )
            spec_path.write_text(dup_spec, encoding="utf-8")

            res = checker.validate_test_spec(spec_path, inventory=inv, state=state)
            self.assertEqual(res["status"], "FAIL")
            codes = {e["code"] for e in res["errors"]}
            self.assertIn("E8_STATE_DRIFT", codes)
            self.assertIn("E9_STALE_PASS_CLAIM", codes)
            self.assertIn("E10_DUPLICATE_SCENARIO_ID", codes)
            warn_codes = {w["code"] for w in res["warnings"]}
            self.assertIn("W2_MISSING_PERF_OR_IDEMPOTENCY", warn_codes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
