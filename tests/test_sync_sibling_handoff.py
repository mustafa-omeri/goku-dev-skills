#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_sibling_handoff.py dikiş noktası (seam) birim ve CLI regresyon testleri."""
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
SCRIPTS = ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_handoff  # noqa: E402
import sync_sibling_handoff as ssync  # noqa: E402


EXISTING_SIBLING_HANDOFF = """# HANDOFF — SiblingBackend

> Güncel: **2026-11-10** · Ajan: **Antigravity**
> Karar kayıtları: `knowledge-base.md`

---

## 0. ⛔ ÖNCE BUNU OKU — Bu Projede Düşülen ve Kanıtlanmış Tuzaklar

| # | Kural & Tuzak | Somut Neden / Ne Yaşandı | Doğru Yol |
|---|---|---|---|
| 1 | DTO tarih formatı ISO 8601 olmalı | LocalDateTime string sapması | ISO format kullan |

---

## 1. Bu Oturumda Yapılanlar (Özet)

- **Kod:** Mevcut endpointler stabil.

---

## 3. ⏭️ BURADAN DEVAM ET

### Sıradaki işler (Canlı Görev Panosu & RTM İzlenebilirlik Matrisi)

#### 🎯 Aktif Sprint / Anlık Görev Panosu (WIP Maks 3)
| ID | Durum | İş / Hedef | Kapsam / PRD Referansı | Hedef Sürüm |
|---|---|---|---|---|
| BE-CORE-001 | ⬜ | Mevcut sağlık kontrolü iyileştirmesi | `docs/plans/old_plan.md` | v1.0.0 |

#### 📌 Gelecek Fazlar & Parking Lot Yol Haritası (Product Roadmap Backlog)
| Gereksinim ID | Açıklama | Hedef Faz | Hedef Sürüm | PRD / Kaynak Ref | Durum |
|---|---|---|---|---|---|
| BE-PL-001 | Gelecek backlog işi | Phase 2 | v1.1.0 | `PRODUCT.md` | ⬜ Bekliyor |
"""


class TestSyncSiblingHandoff(unittest.TestCase):
    def test_rejects_missing_non_project_and_self_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "frontendApp"
            source.mkdir()
            (source / "package.json").write_text('{"name": "frontendApp"}', encoding="utf-8")

            missing = base / "doesNotExist"
            with self.assertRaises(ValueError):
                ssync.validate_sibling_root(missing, source)

            empty_dir = base / "emptyDir"
            empty_dir.mkdir()
            with self.assertRaises(ValueError):
                ssync.validate_sibling_root(empty_dir, source)

            with self.assertRaises(ValueError):
                ssync.validate_sibling_root(source, source)

    def test_creates_valid_handoff_from_template_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "sampleFrontendApp"
            source.mkdir()
            (source / "package.json").write_text('{"name": "sampleFrontendApp"}', encoding="utf-8")

            sibling = base / "sampleBackendApp"
            sibling.mkdir()
            (sibling / "pom.xml").write_text("<project/>", encoding="utf-8")

            result = ssync.sync_sibling_handoff(
                sibling_root=sibling,
                source_root=source,
                plan_ref="docs/plans/plan_reporting_20261117_120000.md",
                task_id="BE-API-012",
                task_title="Rapor izin endpoint'ine role filtresi ekle",
                summary="POST /api/v1/reports/permissions DTO'suna allowedRoles[] eklenecek.",
                template_path=ROOT / ".agent" / "templates" / "HANDOFF.template.md",
            )

            handoff_file = sibling / "HANDOFF.md"
            self.assertTrue(handoff_file.is_file())
            self.assertEqual(result["created"], True)

            content = handoff_file.read_text(encoding="utf-8")
            self.assertIn("sampleFrontendApp projesindeki `docs/plans/plan_reporting_20261117_120000.md` plan dosyası referansına göre", content)
            self.assertIn("BE-API-012", content)
            self.assertIn("POST /api/v1/reports/permissions", content)

            errors, warnings = check_handoff.validate_handoff(sibling, ignore_git_diff=True)
            self.assertEqual(errors, [], f"Beklenmeyen E hatası: {errors}")
            self.assertEqual(warnings, [], f"Beklenmeyen W uyarısı: {warnings}")

    def test_preserves_existing_content_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "sampleFrontendApp"
            source.mkdir()
            (source / "package.json").write_text('{"name": "sampleFrontendApp"}', encoding="utf-8")

            sibling = base / "sampleBackendApp"
            sibling.mkdir()
            (sibling / "pom.xml").write_text("<project/>", encoding="utf-8")
            (sibling / "HANDOFF.md").write_text(EXISTING_SIBLING_HANDOFF, encoding="utf-8")

            ssync.sync_sibling_handoff(
                sibling_root=sibling,
                source_root=source,
                plan_ref="docs/plans/plan_auth_20261117_140000.md",
                task_id="BE-AUTH-009",
                task_title="Auth DTO senkronu",
                summary="UserResponse içine permissions[] alanı eklenecek.",
            )
            # İkinci çağrı aynı ID'yi çoğaltmamalı
            ssync.sync_sibling_handoff(
                sibling_root=sibling,
                source_root=source,
                plan_ref="docs/plans/plan_auth_20261117_140000.md",
                task_id="BE-AUTH-009",
                task_title="Auth DTO senkronu (güncel)",
                summary="UserResponse içine permissions[] ve roleCode eklenecek.",
            )

            content = (sibling / "HANDOFF.md").read_text(encoding="utf-8")
            self.assertIn("DTO tarih formatı ISO 8601 olmalı", content)
            self.assertIn("BE-CORE-001", content)
            self.assertEqual(content.count("| BE-AUTH-009 |"), 1)
            self.assertIn("Auth DTO senkronu (güncel)", content)
            self.assertIn("sampleFrontendApp projesindeki `docs/plans/plan_auth_20261117_140000.md` plan dosyası referansına göre", content)

            errors, warnings = check_handoff.validate_handoff(sibling, ignore_git_diff=True)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_cli_execution_and_self_root_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "feApp"
            source.mkdir()
            (source / "package.json").write_text('{"name": "feApp"}', encoding="utf-8")
            sibling = base / "beApp"
            sibling.mkdir()
            (sibling / "pom.xml").write_text("<project/>", encoding="utf-8")

            script = SCRIPTS / "sync_sibling_handoff.py"
            res_ok = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--sibling-root",
                    str(sibling),
                    "--source-root",
                    str(source),
                    "--plan",
                    "docs/plans/plan_x_20261117.md",
                    "--task-id",
                    "BE-TSK-001",
                    "--task-title",
                    "Yeni webhook ucu",
                    "--summary",
                    "POST /api/webhooks/sync eklenecek.",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(res_ok.returncode, 0, res_ok.stderr + res_ok.stdout)
            self.assertIn("[OK]", res_ok.stdout)

            res_bad = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--sibling-root",
                    str(source),
                    "--source-root",
                    str(source),
                    "--plan",
                    "docs/plans/plan_x.md",
                    "--task-id",
                    "BE-TSK-001",
                    "--task-title",
                    "Hatalı kendi kendine devir",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertNotEqual(res_bad.returncode, 0)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSyncSiblingHandoff)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
