#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ecosystem contract tests for `feature-architect` Six-Hat Council & Engine Advisor (S2-09)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / ".agent" / "skills" / "feature-architect"
AGENTS_DIR = SKILL_DIR / "agents"
SCHEMA_PATH = SKILL_DIR / "schemas" / "council-contract.schema.json"
PROTOCOL_PATH = SKILL_DIR / "references" / "council-protocol.md"
REPORT_TEMPLATE_PATH = SKILL_DIR / "references" / "report-template.md"
MERGER_TESTS = SKILL_DIR / "scripts" / "tests" / "test_council_merger.py"
ADVISOR_TESTS = SKILL_DIR / "scripts" / "tests" / "test_engine_advisor.py"

EXPECTED_AGENTS = [
    ("01-snr-product-owner.md", "snr-product-owner", "PO"),
    ("02-snr-software-architect.md", "snr-software-architect", "ARCH"),
    ("03-principal-ui-ux-specialist.md", "principal-ui-ux-specialist", "UX"),
    ("04-snr-seo-specialist.md", "snr-seo-specialist", "SEO"),
    ("05-snr-growth-marketing.md", "snr-growth-marketing", "GRW"),
    ("06-snr-qa-security-auditor.md", "snr-qa-security-auditor", "QA"),
]

REQUIRED_AGENT_HEADINGS = [
    r"^## 1\. Uzmanlık Merceği",
    r"^## 2\. Denetim Kontrol Listesi",
    r"^## 3\. UI/UX Uyumsuzluk Odağı",
    r"^## 4\. PRD Ötesi Yeni Feature Üretimi",
    r"^## 5\. Ezilmez Kırmızı Çizgiler",
]

FORBIDDEN_PROJECT_RE = re.compile(
    r"\bocai\b|FEProjectv1|FEProject\b|bookmarkManagerProject|bookmarkManager|\bkalansure\b",
    re.IGNORECASE,
)


class FeatureArchitectCouncilEcosystemTests(unittest.TestCase):
    def test_01_unit_suites_pass(self) -> None:
        for suite in (MERGER_TESTS, ADVISOR_TESTS):
            self.assertTrue(suite.is_file(), f"Missing test suite: {suite}")
            res = subprocess.run(
                [sys.executable, str(suite)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(
                res.returncode,
                0,
                f"{suite.name} failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}",
            )

    def test_02_schema_is_valid_json_with_required_keys(self) -> None:
        self.assertTrue(SCHEMA_PATH.is_file(), f"Missing schema: {SCHEMA_PATH}")
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema.get("title"), "FeatureArchitectCouncilContract")
        required = set(schema.get("required", []))
        for key in (
            "agent_id",
            "role",
            "health_score",
            "audits",
            "ui_ux_mismatches",
            "new_features",
            "non_negotiable_constraints",
        ):
            self.assertIn(key, required)
        audit_req = set(schema["properties"]["audits"]["items"]["required"])
        self.assertIn("evidence", audit_req)
        self.assertIn("confidence", audit_req)
        feat_req = set(schema["properties"]["new_features"]["items"]["required"])
        self.assertIn("reach", feat_req)
        self.assertIn("confidence", feat_req)

    def test_03_six_agent_files_have_required_frontmatter_and_sections(self) -> None:
        self.assertTrue(AGENTS_DIR.is_dir(), f"Missing agents directory: {AGENTS_DIR}")
        for filename, agent_id, prefix in EXPECTED_AGENTS:
            path = AGENTS_DIR / filename
            self.assertTrue(path.is_file(), f"Missing hat file: {path}")
            raw = path.read_bytes()
            self.assertNotEqual(raw[:3], b"\xef\xbb\xbf", f"UTF-8 BOM detected in {filename}")
            text = raw.decode("utf-8")
            self.assertTrue(text.startswith("---\n") or text.startswith("---\r\n"), f"{filename} missing frontmatter")
            self.assertIn(f"agent_id: {agent_id}", text)
            self.assertIn(f"id_prefix: {prefix}", text)
            self.assertIn("contract: ../schemas/council-contract.schema.json", text)
            for heading_pat in REQUIRED_AGENT_HEADINGS:
                self.assertRegex(text, re.compile(heading_pat, re.MULTILINE), f"{filename} missing {heading_pat}")

    def test_04_skill_md_and_protocol_document_engine_gate_and_modes(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(PROTOCOL_PATH.is_file(), f"Missing protocol doc: {PROTOCOL_PATH}")
        proto_text = PROTOCOL_PATH.read_text(encoding="utf-8")

        for token in (
            "engine_advisor.py",
            "council_merger.py",
            "--mode=council",
            "--mode=complete",
            "--engine=",
            "--hats",
            "docs/plans/council/",
        ):
            self.assertIn(token, skill_text, f"SKILL.md missing {token}")
        for env_name in ("Antigravity", "Claude Code", "OpenCode", "CLI"):
            self.assertIn(env_name, proto_text, f"council-protocol.md missing {env_name}")

    def test_05_report_template_has_seven_council_sections_and_engine_question(self) -> None:
        tpl_text = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
        for expected in (
            "Motor Seçimi",
            "Konsey Sağlık Karnesi",
            "Tamamlama Envanteri",
            "6 Uzman Gözünden Kritik Bulgular",
            "Uyumsuzluk Raporu",
            "Beyond-PRD",
            "Konsey Uzlaşı ve Çatışma Matrisi",
            "5 Katmanlı",
            "CRITICAL",
        ):
            self.assertIn(expected, tpl_text, f"report-template.md missing {expected!r}")

    def test_06_global_purity_across_all_council_files(self) -> None:
        violations = []
        for path in sorted(SKILL_DIR.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix not in {".md", ".py", ".json"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for m in FORBIDDEN_PROJECT_RE.finditer(text):
                violations.append(f"{path.relative_to(ROOT)}: {m.group(0)!r}")
        self.assertEqual(violations, [], "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
