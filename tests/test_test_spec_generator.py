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


if __name__ == "__main__":
    unittest.main(verbosity=2)
