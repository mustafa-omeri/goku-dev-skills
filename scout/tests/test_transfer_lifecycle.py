#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scout Statü Yaşam Döngüsü ve Aktarım Süreci (Progress) Test Paketi."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scout.engine import (
    load_repos,
    save_repos,
    set_repo_status,
    start_repo_transfer,
    complete_repo_transfer,
    record_repo_history,
    migrate_legacy_statuses,
    find_existing_repo,
    canonical_repo_key,
    VALID_STATUSES
)


class TestScoutTransferLifecycle(unittest.TestCase):
    """Scout durum makinesi, aktarım ilerlemesi ve audit trail testleri."""

    def setUp(self):
        self.mock_repos = [
            {
                "id": 1,
                "url": "https://github.com/test-owner/test-transferred",
                "name": "test-transferred",
                "owner": "test-owner",
                "layer": "Tooling / Agentic",
                "status": "DONE",
                "verdict": "AKTARILDI: .agent/skills/seo-growth/ altına aktarıldı.",
                "plan_file": "plans/test-transferred.md",
                "date": "2026-10-22"
            },
            {
                "id": 2,
                "url": "https://github.com/test-owner/test-better",
                "name": "test-better",
                "owner": "test-owner",
                "layer": "Frontend",
                "status": "DONE",
                "verdict": "BIZ_DAHA_IYIYIZ: Bizim ui-styling sistemimiz daha üstün.",
                "plan_file": "plans/test-better.md",
                "date": "2026-10-25"
            },
            {
                "id": 3,
                "url": "https://github.com/test-owner/test-candidate",
                "name": "test-candidate",
                "owner": "test-owner",
                "layer": "Tooling / Agentic",
                "status": "DONE",
                "verdict": "ZENGINLESTIR: Cerrahi parçalar incelenip ilgili skill'e aktarılabilir.",
                "plan_file": "plans/test-candidate.md",
                "date": "2026-10-26"
            },
            {
                "id": 4,
                "url": "https://github.com/test-owner/test-pending",
                "name": "test-pending",
                "owner": "test-owner",
                "layer": "Backend",
                "status": "PENDING",
                "verdict": "-",
                "plan_file": "",
                "date": "2026-10-30"
            }
        ]

    def test_valid_statuses_includes_lifecycle(self):
        """VALID_STATUSES kümesi yeni yaşam döngüsü statülerini içermelidir."""
        expected = {"PENDING", "PLANNED", "TRANSFERRING", "TRANSFERRED", "REJECTED", "SUSPENDED", "CANCEL"}
        self.assertTrue(expected.issubset(set(VALID_STATUSES)))

    def test_migrate_legacy_statuses(self):
        """Eski DONE kayıtları verdict kararlarına göre otomatik migrate edilmelidir."""
        migrated = migrate_legacy_statuses(self.mock_repos)
        
        # 1. AKTARILDI -> TRANSFERRED
        r1 = next(r for r in migrated if r["id"] == 1)
        self.assertEqual(r1["status"], "TRANSFERRED")
        self.assertEqual(r1.get("progress"), 100)
        self.assertIn("history", r1)

        # 2. BIZ_DAHA_IYIYIZ -> REJECTED
        r2 = next(r for r in migrated if r["id"] == 2)
        self.assertEqual(r2["status"], "REJECTED")
        self.assertEqual(r2.get("progress"), 100)

        # 3. ZENGINLESTIR / KISMEN -> PLANNED
        r3 = next(r for r in migrated if r["id"] == 3)
        self.assertEqual(r3["status"], "PLANNED")
        self.assertEqual(r3.get("progress"), 25)

        # 4. PENDING -> PENDING
        r4 = next(r for r in migrated if r["id"] == 4)
        self.assertEqual(r4["status"], "PENDING")
        self.assertEqual(r4.get("progress"), 0)

    @patch("scout.engine.load_repos")
    @patch("scout.engine.save_repos")
    def test_start_repo_transfer(self, mock_save, mock_load):
        """Aktarımı başlatma durumunu TRANSFERRING yapmalı ve history kaydetmelidir."""
        mock_load.return_value = [dict(r) for r in self.mock_repos]
        mock_save.return_value = True

        res = start_repo_transfer(
            identifier=3,
            target_skill="code-review",
            notes="Stop conditions aktarımı başlatıldı."
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["repo"]["status"], "TRANSFERRING")
        self.assertEqual(res["repo"]["target_skill"], "code-review")
        self.assertEqual(res["repo"]["progress"], 50)
        
        # History denetimi
        history = res["repo"].get("history", [])
        self.assertTrue(len(history) >= 1)
        last_action = history[-1]
        self.assertEqual(last_action["action"], "TRANSFER_STARTED")
        self.assertEqual(last_action["status"], "TRANSFERRING")

    @patch("scout.engine.load_repos")
    @patch("scout.engine.save_repos")
    def test_complete_repo_transfer(self, mock_save, mock_load):
        """Aktarımı tamamlama durumunu TRANSFERRED yapmalı ve transferred_to kaydetmelidir."""
        repo_item = dict(self.mock_repos[2])
        repo_item["status"] = "TRANSFERRING"
        repo_item["target_skill"] = "code-review"
        mock_load.return_value = [repo_item]
        mock_save.return_value = True

        res = complete_repo_transfer(
            identifier=3,
            target_skill="code-review",
            transferred_to=".agent/skills/code-review/references/stop-conditions.md",
            notes="Tüm referanslar aktarıldı ve doğrulandı."
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["repo"]["status"], "TRANSFERRED")
        self.assertEqual(res["repo"]["transferred_to"], ".agent/skills/code-review/references/stop-conditions.md")
        self.assertEqual(res["repo"]["progress"], 100)

        history = res["repo"].get("history", [])
        last_action = history[-1]
        self.assertEqual(last_action["action"], "TRANSFERRED")
        self.assertEqual(last_action["status"], "TRANSFERRED")


    @patch("scout.server.start_repo_transfer")
    @patch("scout.server.parse_repos_md")
    def test_api_transfer_start(self, mock_parse, mock_start):
        """POST /api/repos/transfer/start endpoint'i aktarımı başlatmalıdır."""
        from scout.server import ScoutApiHandler
        import io

        mock_start.return_value = {
            "success": True,
            "repo": {"id": 3, "status": "TRANSFERRING", "target_skill": "code-review"},
            "message": "Aktarım başladı"
        }
        mock_parse.return_value = []

        # Handler simülasyonu
        handler = ScoutApiHandler.__new__(ScoutApiHandler)
        handler.path = "/api/repos/transfer/start"
        body = json.dumps({"id": 3, "target_skill": "code-review", "notes": "test"}).encode("utf-8")
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile = io.BytesIO(body)
        handler.wfile = io.BytesIO()

        responses = []
        headers_sent = []
        handler.send_response = lambda code: responses.append(code)
        handler.send_header = lambda k, v: headers_sent.append((k, v))
        handler.end_headers = lambda: None

        handler.do_POST()
        self.assertIn(200, responses)
        out = json.loads(handler.wfile.getvalue().decode("utf-8"))
        self.assertTrue(out["success"])
        self.assertEqual(out["repo"]["status"], "TRANSFERRING")

    def test_scout_catalog_html_contains_lifecycle_ui(self):
        """Scout Kataloğu HTML çıktısı yeni yaşam döngüsü sekmelerini, progress ve modalları içermelidir."""
        from scout.generate_scout_catalog import generate_html

        html = generate_html(self.mock_repos)
        self.assertIn("badge-transferring", html)
        self.assertIn("badge-planned", html)
        self.assertIn("badge-transferred", html)
        self.assertIn("badge-rejected", html)
        self.assertIn("startTransferModal", html)
        self.assertIn("completeTransferModal", html)
        self.assertIn("historyModal", html)
        self.assertIn("repo-progress-bar", html)
        self.assertIn("tabCountTransferring", html)
        self.assertIn("openStartTransferModal", html)
        self.assertIn("openCompleteTransferModal", html)


if __name__ == "__main__":
    unittest.main()
