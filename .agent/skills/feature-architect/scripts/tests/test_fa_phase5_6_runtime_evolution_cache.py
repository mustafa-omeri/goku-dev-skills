#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TDD Phase 5 & 6 tests for `runtime.py`, `evolution.py`, and `cache.py` (`S2-12`)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fa_engine import cache, evolution, runtime  # noqa: E402


class Phase5And6RuntimeEvolutionCacheTests(unittest.TestCase):
    def test_01_runtime_rejects_non_localhost_and_non_get_mutations(self) -> None:
        with self.assertRaises(ValueError):
            runtime.validate_probe_request("https://production.example.com/api/v1/users", method="GET")
        with self.assertRaises(ValueError):
            runtime.validate_probe_request("http://localhost:3000/api/v1/users", method="DELETE")
        ok = runtime.validate_probe_request("http://localhost:5173/main", method="GET")
        self.assertTrue(ok)

    def test_02_runtime_redacts_pii_and_secrets_and_reconciles_l3_evidence(self) -> None:
        raw_log = "User email=alice.smith@company.org token=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc.def password=secret_val_99"
        redacted = runtime.redact_sensitive_text(raw_log)
        self.assertNotIn("alice.smith@company.org", redacted)
        self.assertNotIn("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", redacted)
        self.assertNotIn("secret_val_99", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_TOKEN]", redacted)

        facts = [
            {
                "id": "FACT-01",
                "category": "EMPTY_DATA_PANEL",
                "fact_type": "behavioral",
                "status": "INFERRED",
                "confidence": 55,
                "location": "src/pages/MainDashboard.tsx:88",
            },
            {
                "id": "FACT-02",
                "category": "BROKEN_ROUTE",
                "fact_type": "behavioral",
                "status": "INFERRED",
                "confidence": 60,
                "location": "src/pages/ProfilePage.tsx:12",
            },
        ]
        observations = [
            {
                "target_fact_id": "FACT-01",
                "url": "http://localhost:5173/main",
                "method": "GET",
                "outcome": "confirmed",
                "http_status": 200,
                "detail": "Panel rendered empty array [] from GET /api/v1/trends",
            },
            {
                "target_fact_id": "FACT-02",
                "url": "http://localhost:5173/main/profile",
                "method": "GET",
                "outcome": "refuted",
                "http_status": 200,
                "detail": "Route rendered 200 OK with valid profile card",
            },
        ]
        updated = runtime.reconcile_runtime_observations(facts, observations)
        by_id = {f["id"]: f for f in updated}
        self.assertEqual(by_id["FACT-01"]["status"], "CONFIRMED")
        self.assertGreaterEqual(by_id["FACT-01"]["confidence"], 90)
        self.assertEqual(by_id["FACT-02"]["status"], "REFUTED")

    def test_03_evolution_horizon_and_unknown_scale_guard(self) -> None:
        audits = [
            {"id": "QA-01", "severity": "CRITICAL", "decision": "FIX", "category": "SECURITY", "location": "src/api/auth.ts"},
            {"id": "ARCH-01", "severity": "HIGH", "decision": "CONNECT", "category": "ORPHAN_API_DB", "location": "src/pages/Main.tsx"},
            {"id": "UX-01", "severity": "MEDIUM", "decision": "REFACTOR", "category": "UI_UX", "location": "src/pages/Profile.tsx"},
            {"id": "PO-01", "severity": "LOW", "decision": "DEFER", "category": "PRODUCT", "location": "src/pages/Settings.tsx"},
        ]
        plan = evolution.build_evolution_horizon(audits, scale_metrics=None)
        self.assertIn("QA-01", [i["id"] for i in plan["horizons"]["now"]])
        self.assertIn("ARCH-01", [i["id"] for i in plan["horizons"]["now"]])
        self.assertIn("UX-01", [i["id"] for i in plan["horizons"]["next"]])
        self.assertIn("PO-01", [i["id"] for i in plan["horizons"]["future"]])
        self.assertEqual(plan["economic_capacity_status"], "UNKNOWN")

    def test_04_incremental_sha256_cache_tracks_modified_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f1 = root / "a.ts"
            f2 = root / "b.ts"
            f1.write_text("export const a = 1;\n", encoding="utf-8")
            f2.write_text("export const b = 2;\n", encoding="utf-8")

            cdir = root / ".fa-cache"
            first = cache.compute_incremental_diff(root, [f1, f2], cache_dir=cdir)
            self.assertEqual(sorted(first["changed_files"]), ["a.ts", "b.ts"])
            self.assertEqual(first["unchanged_files"], [])

            # Second run with no changes -> 100% cache hit
            second = cache.compute_incremental_diff(root, [f1, f2], cache_dir=cdir)
            self.assertEqual(second["changed_files"], [])
            self.assertEqual(sorted(second["unchanged_files"]), ["a.ts", "b.ts"])

            # Modify only b.ts -> only b.ts is marked changed
            f2.write_text("export const b = 99;\n", encoding="utf-8")
            third = cache.compute_incremental_diff(root, [f1, f2], cache_dir=cdir)
            self.assertEqual(third["changed_files"], ["b.ts"])
            self.assertEqual(third["unchanged_files"], ["a.ts"])


if __name__ == "__main__":
    unittest.main()
