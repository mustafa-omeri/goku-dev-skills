#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saf Python Diff Triaj, Kapsam Manifesti, Akıllı Demetleme ve Zemin Koruma Testleri."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / ".agent" / "skills" / "code-review" / "scripts" / "diff_triage.py"
SCRIPTS_DIR = SCRIPT_PATH.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from diff_triage import analyze_diff  # noqa: E402


SAMPLE_DIFF = """diff --git a/src/auth/login.ts b/src/auth/login.ts
index 1111111..2222222 100644
--- a/src/auth/login.ts
+++ b/src/auth/login.ts
@@ -1,3 +1,6 @@
 export function login(user: string) {
+  // @ts-ignore
+  if (!user) throw new Error("Not implemented");
   return true;
 }
diff --git a/src/locales/tr.json b/src/locales/tr.json
index 1111111..2222222 100644
--- a/src/locales/tr.json
+++ b/src/locales/tr.json
@@ -1,2 +1,3 @@
 {
+  "auth.title": "Giriş"
 }
diff --git a/src/locales/en.json b/src/locales/en.json
index 1111111..2222222 100644
--- a/src/locales/en.json
+++ b/src/locales/en.json
@@ -1,2 +1,3 @@
 {
+  "auth.title": "Login"
 }
"""


class TestDiffTriage(unittest.TestCase):
    """diff_triage.py genel arayüz (seam) sözleşme testleri."""

    def test_empty_diff_returns_zero_manifest(self):
        res = analyze_diff("")
        self.assertEqual(res["total_files"], 0)
        self.assertEqual(res["coverage_manifest"]["total_files"], 0)
        self.assertEqual(res["coverage_manifest"]["coverage_rate"], 1.0)
        self.assertEqual(res["floor_violations"], [])

    def test_smart_bundling_and_risk_and_floor_violations(self):
        res = analyze_diff(SAMPLE_DIFF)
        self.assertEqual(res["total_files"], 3)
        self.assertEqual(res["coverage_manifest"]["total_files"], 3)
        self.assertEqual(res["coverage_manifest"]["coverage_rate"], 0.0)
        self.assertEqual(len(res["coverage_manifest"]["checklist"]), 3)

        # i18n çiftleri aynı demette toplanmalı
        bundles = res["bundles"]
        i18n_bundle = [b for b in bundles if "locales/tr.json" in " ".join(b["files"]) and "locales/en.json" in " ".join(b["files"])]
        self.assertTrue(i18n_bundle, f"i18n çiftleri demetlenmedi: {bundles}")

        # Güvenlik hassas dosya + test eksikliği riski
        risk_text = " ".join(res["risk_flags"])
        self.assertIn("SECURITY_SENSITIVE_FILE", risk_text)

        # Zemin düşürme (@ts-ignore ve Not implemented) yakalanmalı
        patterns = [v["pattern"] for v in res["floor_violations"]]
        self.assertIn("TS_IGNORE", patterns)
        self.assertIn("UNIMPLEMENTED_STUB", patterns)

    def test_cli_json_output(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--json"],
            input=SAMPLE_DIFF,
            text=True,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["total_files"], 3)


if __name__ == "__main__":
    unittest.main()
