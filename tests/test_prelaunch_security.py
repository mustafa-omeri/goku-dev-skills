#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression & contract tests for Pre-Launch 20-Item Security Checklist & Feature-Architect Integration (S2-07)."""
import json
import os
import re
import shutil
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
PRELAUNCH_DIR = ROOT / ".agent" / "skills" / "prelaunch-audit"
SECURITY_CHECKER = PRELAUNCH_DIR / "scripts" / "security_checker.py"
PRELAUNCH_CHECKER = PRELAUNCH_DIR / "scripts" / "prelaunch_checker.py"
PRELAUNCH_SKILL = PRELAUNCH_DIR / "SKILL.md"
SECURITY_REF = PRELAUNCH_DIR / "references" / "security-compliance.md"
CHECK_SECURITY_SKILL = ROOT / ".agent" / "skills" / "check-security" / "SKILL.md"
FA_SKILL = ROOT / ".agent" / "skills" / "feature-architect" / "SKILL.md"
FA_REPORT_TEMPLATE = ROOT / ".agent" / "skills" / "feature-architect" / "references" / "report-template.md"

FORBIDDEN_PROJECT_RE = re.compile(
    r"\bocai\b|FEProjectv1|FEProject\b|bookmarkManagerProject|bookmarkManager|\bkalansure\b",
    re.IGNORECASE,
)


class PrelaunchSecurityContractTests(unittest.TestCase):
    """Tests the mechanical security_checker, prelaunch-audit, check-security and feature-architect security baseline."""

    def test_01_security_checker_script_exists_and_runnable(self):
        self.assertTrue(SECURITY_CHECKER.is_file(), f"Missing {SECURITY_CHECKER}")
        res = subprocess.run(
            [sys.executable, str(SECURITY_CHECKER), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res.returncode, 0, f"security_checker.py --help failed: {res.stderr}")
        for flag in ("--dir", "--url", "--json"):
            self.assertIn(flag, res.stdout)

    def test_02_detects_blockers_in_mock_fixtures_and_exits_1(self):
        self.assertTrue(SECURITY_CHECKER.is_file(), f"Missing {SECURITY_CHECKER}")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # 1. Leaked secret (dynamically constructed so scanner catches it, but static push protection does not)
            prefix = "sk_live_"
            body = "51Abcdef1234567890abcdef1234567890"
            (tmppath / "api_client.ts").write_text(
                f'const STRIPE_SECRET = "{prefix}{body}";\n',
                encoding="utf-8",
            )
            # 2. Exposed .env file
            (tmppath / ".env").write_text(
                'DATABASE_URL="postgres://user:password@localhost:5432/mydb"\n',
                encoding="utf-8",
            )
            # 3. Insecure password hash (MD5)
            (tmppath / "auth_service.py").write_text(
                'import hashlib\ndef hash_pwd(p):\n    return hashlib.md5(p.encode()).hexdigest()\n',
                encoding="utf-8",
            )
            # 4. Debug mode active
            (tmppath / "settings.py").write_text('DEBUG = True\n', encoding="utf-8")
            # 5. Wildcard CORS with credentials
            (tmppath / "server.js").write_text(
                'app.use(cors({ origin: "*", credentials: true }));\n',
                encoding="utf-8",
            )

            res = subprocess.run(
                [sys.executable, str(SECURITY_CHECKER), "--dir", str(tmppath), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(res.returncode, 1, "Expected security_checker to exit 1 on blockers")
            data = json.loads(res.stdout)
            self.assertEqual(data.get("verdict"), "NO-GO")
            blockers = data.get("blockers", [])
            self.assertTrue(len(blockers) >= 4, f"Expected at least 4 blockers, got {len(blockers)}: {blockers}")

    def test_03_accepts_clean_project_and_exits_0(self):
        self.assertTrue(SECURITY_CHECKER.is_file(), f"Missing {SECURITY_CHECKER}")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "auth.ts").write_text(
                'import bcrypt from "bcrypt";\nconst hash = await bcrypt.hash(password, 12);\n',
                encoding="utf-8",
            )
            (tmppath / "server.ts").write_text(
                'const allowedOrigins = ["https://app.example.com"];\n',
                encoding="utf-8",
            )
            (tmppath / "settings.py").write_text('DEBUG = False\n', encoding="utf-8")

            res = subprocess.run(
                [sys.executable, str(SECURITY_CHECKER), "--dir", str(tmppath), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(res.returncode, 0, f"Expected security_checker to exit 0 on clean code: {res.stdout}")
            data = json.loads(res.stdout)
            self.assertIn(data.get("verdict"), ("GO", "REVIEW COMPLETE"))
            self.assertEqual(len(data.get("blockers", [])), 0)

    def test_04_prelaunch_checker_integrates_security_checker(self):
        self.assertTrue(PRELAUNCH_CHECKER.is_file(), "prelaunch_checker.py missing")
        text = PRELAUNCH_CHECKER.read_text(encoding="utf-8")
        self.assertIn("security_checker", text)
        self.assertIn("check_security_headers", text)

    def test_05_skills_and_feature_architect_integration(self):
        # 1. prelaunch-audit
        self.assertTrue(PRELAUNCH_SKILL.is_file(), "prelaunch-audit/SKILL.md missing")
        prelaunch_text = PRELAUNCH_SKILL.read_text(encoding="utf-8")
        self.assertIn("security_checker.py", prelaunch_text)
        self.assertIn("security-compliance.md", prelaunch_text)

        # 2. security-compliance.md reference exists
        self.assertTrue(SECURITY_REF.is_file(), f"Missing {SECURITY_REF}")
        sec_ref_text = SECURITY_REF.read_text(encoding="utf-8")
        self.assertIn("Argon2id", sec_ref_text)
        self.assertIn("CORS", sec_ref_text)
        self.assertIn("Content-Security-Policy", sec_ref_text)
        self.assertIn("Strict-Transport-Security", sec_ref_text)

        # 3. check-security skill
        self.assertTrue(CHECK_SECURITY_SKILL.is_file(), "check-security/SKILL.md missing")
        check_sec_text = CHECK_SECURITY_SKILL.read_text(encoding="utf-8")
        self.assertIn("security_checker.py", check_sec_text)

        # 4. feature-architect skill & report template
        self.assertTrue(FA_SKILL.is_file(), "feature-architect/SKILL.md missing")
        fa_text = FA_SKILL.read_text(encoding="utf-8")
        self.assertIn("security_checker.py", fa_text)
        self.assertIn("Güvenlik Temeli", fa_text)

        fa_report_text = FA_REPORT_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("Güvenlik Temeli", fa_report_text)
        self.assertIn("OWASP", fa_report_text)

    def test_06_global_purity_no_project_names(self):
        targets = [SECURITY_CHECKER, SECURITY_REF, PRELAUNCH_SKILL, CHECK_SECURITY_SKILL, FA_SKILL, FA_REPORT_TEMPLATE]
        violations = []
        for path in targets:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for m in FORBIDDEN_PROJECT_RE.finditer(text):
                violations.append(f"{path.relative_to(ROOT)}: contains project name {m.group(0)!r}")
        self.assertEqual(violations, [], "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
