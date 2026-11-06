#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit & CLI contract tests for `council_merger.py` (Six-Hat Council synthesizer)."""
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

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
MERGER_SCRIPT = SCRIPTS_DIR / "council_merger.py"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import council_merger  # noqa: E402


def _make_hat_report(
    agent_id: str = "snr-product-owner",
    role: str = "Senior Product Owner & Domain Strategist",
    prefix: str = "PO",
    health_score: int | None = 82,
    applicability: str = "applicable",
    not_applicable_reason: str = "",
    audits: list[dict] | None = None,
    ui_ux_mismatches: list[dict] | None = None,
    new_features: list[dict] | None = None,
    constraints: list[str] | None = None,
) -> dict:
    return {
        "agent_id": agent_id,
        "role": role,
        "applicability": applicability,
        "not_applicable_reason": not_applicable_reason,
        "health_score": health_score,
        "audits": audits if audits is not None else [
            {
                "id": f"{prefix}-01",
                "category": "CORE_MODULE_GAP",
                "severity": "MEDIUM",
                "location": "src/pages/Dashboard.tsx:44",
                "evidence": "src/pages/Dashboard.tsx:44 -> static welcome card without actionable KPIs",
                "confidence": "verified",
                "issue": "Dashboard lacks actionable workflow items.",
                "fix_proposal": "Add pending approvals queue card wired to existing API.",
            }
        ],
        "ui_ux_mismatches": ui_ux_mismatches if ui_ux_mismatches is not None else [],
        "new_features": new_features if new_features is not None else [],
        "non_negotiable_constraints": constraints if constraints is not None else [
            "Every primary screen must expose a clear Next Best Action."
        ],
    }


class CouncilMergerUnitTests(unittest.TestCase):
    def test_valid_report_passes_schema(self) -> None:
        report = _make_hat_report()
        errors = council_merger.validate_report(report)
        self.assertEqual(errors, [])

    def test_missing_evidence_rejected(self) -> None:
        bad_audit = {
            "id": "PO-01",
            "category": "STUB_PAGE",
            "severity": "HIGH",
            "location": "src/pages/Reports.tsx:12",
            "confidence": "verified",
            "issue": "Stub page left in navigation.",
            "fix_proposal": "Implement reports view.",
        }
        report = _make_hat_report(audits=[bad_audit])
        errors = council_merger.validate_report(report)
        self.assertTrue(any("evidence" in err for err in errors), f"Expected evidence error, got: {errors}")

    def test_bad_severity_and_score_range_rejected(self) -> None:
        bad_audit = {
            "id": "INVALID-1",
            "category": "STUB_PAGE",
            "severity": "BLOCKER_PLUS",
            "location": "src/pages/Reports.tsx:12",
            "evidence": "src/pages/Reports.tsx:12",
            "confidence": "verified",
            "issue": "Stub.",
            "fix_proposal": "Fix.",
        }
        report = _make_hat_report(health_score=140, audits=[bad_audit])
        errors = council_merger.validate_report(report)
        self.assertTrue(any("health_score" in err for err in errors), errors)
        self.assertTrue(any("severity" in err for err in errors), errors)
        self.assertTrue(any("id" in err for err in errors), errors)

    def test_not_applicable_agent_excluded_from_score(self) -> None:
        po = _make_hat_report("snr-product-owner", "PO", "PO", health_score=80)
        arch = _make_hat_report("snr-software-architect", "Arch", "ARCH", health_score=90)
        seo = _make_hat_report(
            "snr-seo-specialist",
            "SEO",
            "SEO",
            health_score=None,
            applicability="not_applicable",
            not_applicable_reason="Auth-behind internal enterprise dashboard; public indexing disabled.",
            audits=[],
            constraints=[],
        )
        merged = council_merger.merge([po, arch, seo])
        self.assertEqual(merged["health"]["mean"], 85.0)
        self.assertEqual(merged["health"]["maturity"], 85.0)
        self.assertEqual(merged["health"]["applicable_count"], 2)

    def test_critical_cap_limits_maturity_to_60(self) -> None:
        po = _make_hat_report("snr-product-owner", "PO", "PO", health_score=92)
        qa = _make_hat_report(
            "snr-qa-security-auditor",
            "QA & Security",
            "QA",
            health_score=88,
            audits=[
                {
                    "id": "QA-01",
                    "category": "SECURITY",
                    "severity": "CRITICAL",
                    "location": "src/api/adminController.ts:29",
                    "evidence": "src/api/adminController.ts:29 -> missing role check on orphan delete endpoint",
                    "confidence": "verified",
                    "issue": "Unauthenticated orphan delete endpoint allows IDOR.",
                    "fix_proposal": "Enforce server-side RBAC guard and integration test.",
                }
            ],
        )
        merged = council_merger.merge([po, qa])
        self.assertEqual(merged["health"]["mean"], 90.0)
        self.assertTrue(merged["health"]["critical_cap_applied"])
        self.assertEqual(merged["health"]["maturity"], 60.0)
        self.assertIn("QA-01", merged["must_carry_ids"])

    def test_weakest_link_reported(self) -> None:
        po = _make_hat_report("snr-product-owner", "PO", "PO", health_score=84)
        ux = _make_hat_report("principal-ui-ux-specialist", "UX", "UX", health_score=58)
        arch = _make_hat_report("snr-software-architect", "Arch", "ARCH", health_score=79)
        merged = council_merger.merge([po, ux, arch])
        self.assertEqual(merged["health"]["weakest"]["agent_id"], "principal-ui-ux-specialist")
        self.assertEqual(merged["health"]["weakest"]["health_score"], 58)

    def test_synergy_cluster_two_agents_same_location_escalates_severity(self) -> None:
        po = _make_hat_report(
            "snr-product-owner",
            "PO",
            "PO",
            audits=[
                {
                    "id": "PO-02",
                    "category": "CORE_MODULE_GAP",
                    "severity": "MEDIUM",
                    "location": "src/pages/Onboarding.tsx:18",
                    "evidence": "src/pages/Onboarding.tsx:18 -> empty welcome step",
                    "confidence": "verified",
                    "issue": "No guided activation step.",
                    "fix_proposal": "Add interactive checklist.",
                }
            ],
        )
        grw = _make_hat_report(
            "snr-growth-marketing",
            "Growth",
            "GRW",
            audits=[
                {
                    "id": "GRW-01",
                    "category": "GROWTH",
                    "severity": "HIGH",
                    "location": "src/pages/Onboarding.tsx:75",
                    "evidence": "src/pages/Onboarding.tsx:75 -> missing primary CTA button",
                    "confidence": "verified",
                    "issue": "High drop-off risk on first visit.",
                    "fix_proposal": "Add single high-contrast activation CTA.",
                }
            ],
        )
        merged = council_merger.merge([po, grw])
        clusters = merged["synergy_clusters"]
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["location"], "src/pages/Onboarding.tsx")
        self.assertEqual(clusters[0]["agents"], ["snr-growth-marketing", "snr-product-owner"])
        self.assertEqual(clusters[0]["base_max_severity"], "HIGH")
        self.assertEqual(clusters[0]["escalated_severity"], "CRITICAL")

    def test_conflict_candidate_on_shared_location(self) -> None:
        grw = _make_hat_report(
            "snr-growth-marketing",
            "Growth",
            "GRW",
            audits=[
                {
                    "id": "GRW-03",
                    "category": "GROWTH",
                    "severity": "MEDIUM",
                    "location": "src/pages/Landing.tsx:10",
                    "evidence": "src/pages/Landing.tsx:10 -> passive hero section",
                    "confidence": "verified",
                    "issue": "Low signup conversion.",
                    "fix_proposal": "Show full-screen signup gate modal on initial load.",
                }
            ],
            constraints=["Every landing view must present one primary conversion goal."],
        )
        seo = _make_hat_report(
            "snr-seo-specialist",
            "SEO",
            "SEO",
            audits=[
                {
                    "id": "SEO-02",
                    "category": "SEO",
                    "severity": "HIGH",
                    "location": "src/pages/Landing.tsx:42",
                    "evidence": "src/pages/Landing.tsx:42 -> missing semantic main heading",
                    "confidence": "verified",
                    "issue": "Landing page lacks indexable H1 hierarchy.",
                    "fix_proposal": "Render semantic H1 and crawlable links without intrusive interstitials.",
                }
            ],
            constraints=["Indexable public pages must never block crawlers or trigger CLS via intrusive modals."],
        )
        merged = council_merger.merge([grw, seo])
        self.assertGreaterEqual(len(merged["conflict_candidates"]), 1)
        locs = {c["location"] for c in merged["conflict_candidates"]}
        self.assertIn("src/pages/Landing.tsx", locs)

    def test_rice_calculation_and_duplicate_feature_merging(self) -> None:
        po = _make_hat_report(
            "snr-product-owner",
            "PO",
            "PO",
            new_features=[
                {
                    "feature_id": "FEAT-PO-1",
                    "title": "Active Sessions & Device Management",
                    "rationale": "Users cannot revoke stolen sessions.",
                    "user_value": "Enterprise account control.",
                    "reach": 8,
                    "impact_score": 9,
                    "confidence": 1.0,
                    "effort": "M",
                    "five_layer_slice_summary": "DB session table -> RPC list/revoke -> API client -> Settings Security tab + skeleton -> Audit log closure",
                },
                {
                    "feature_id": "FEAT-PO-2",
                    "title": "Weekly Digest Export",
                    "rationale": "Summary email.",
                    "user_value": "Passive reporting.",
                    "reach": 4,
                    "impact_score": 5,
                    "confidence": 0.5,
                    "effort": "L",
                    "five_layer_slice_summary": "DB pref -> Worker -> API -> Toggle UI -> Admin stats",
                },
            ],
        )
        qa = _make_hat_report(
            "snr-qa-security-auditor",
            "QA",
            "QA",
            new_features=[
                {
                    "feature_id": "FEAT-QA-1",
                    "title": "  active sessions & device management ",
                    "rationale": "Security baseline requires session revocation.",
                    "user_value": "Zero-trust session hygiene.",
                    "reach": 9,
                    "impact_score": 9,
                    "confidence": 1.0,
                    "effort": "M",
                    "five_layer_slice_summary": "DB sessions -> Auth controller -> Service seam -> Security UI -> Security log",
                }
            ],
        )
        merged = council_merger.merge([po, qa])
        ranked = merged["features_ranked"]
        self.assertEqual(len(ranked), 2)
        # First feature: max reach=9, impact=9, conf=1.0, effort=M(2) => RICE = 9*9*1.0/2 = 40.5
        self.assertEqual(ranked[0]["rice_score"], 40.5)
        self.assertEqual(sorted(ranked[0]["proposed_by"]), ["snr-product-owner", "snr-qa-security-auditor"])
        # Second feature: 4*5*0.5/3 = 3.33
        self.assertEqual(ranked[1]["rice_score"], 3.33)

    def test_check_report_detects_dropped_critical_with_exact_token_boundary(self) -> None:
        qa = _make_hat_report(
            "snr-qa-security-auditor",
            "QA",
            "QA",
            audits=[
                {
                    "id": "QA-01",
                    "category": "SECURITY",
                    "severity": "CRITICAL",
                    "location": "src/api/auth.ts:10",
                    "evidence": "src/api/auth.ts:10",
                    "confidence": "verified",
                    "issue": "Missing auth guard.",
                    "fix_proposal": "Add guard.",
                },
                {
                    "id": "QA-10",
                    "category": "SECURITY",
                    "severity": "HIGH",
                    "location": "src/api/auth.ts:30",
                    "evidence": "src/api/auth.ts:30",
                    "confidence": "verified",
                    "issue": "Missing rate limit.",
                    "fix_proposal": "Add rate limit.",
                },
            ],
        )
        merged = council_merger.merge([qa])
        # Markdown mentions QA-10, NOT QA-01 (substring trap: QA-01 must not match QA-010!)
        bad_md = "# Consolidated Report\nIncluded: QA-10 and QA-010 only.\n"
        missing = council_merger.check_report(bad_md, merged)
        self.assertEqual(missing, ["QA-01"])

        good_md = "# Consolidated Report\nIncluded: `QA-01` and `QA-10`.\n"
        self.assertEqual(council_merger.check_report(good_md, merged), [])

    def test_merger_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            p1 = tdir / "01-po.json"
            p1.write_text(
                json.dumps(
                    _make_hat_report(
                        "snr-product-owner",
                        "PO",
                        "PO",
                        audits=[
                            {
                                "id": "PO-01",
                                "category": "STUB_PAGE",
                                "severity": "CRITICAL",
                                "location": "src/pages/Billing.tsx:9",
                                "evidence": "src/pages/Billing.tsx:9 -> Coming Soon",
                                "confidence": "verified",
                                "issue": "Billing page is stub.",
                                "fix_proposal": "Build 5-layer billing slice.",
                            }
                        ],
                    )
                ),
                encoding="utf-8",
            )
            # Auxiliary files in council dir must be safely ignored
            (tdir / "context-snapshot.json").write_text('{"schema":"snapshot"}', encoding="utf-8")

            # 0 = valid merge
            res_ok = subprocess.run(
                [sys.executable, str(MERGER_SCRIPT), "--inputs", str(tdir), "--format", "json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(res_ok.returncode, 0, res_ok.stderr)

            # 2 = zero-drop violation when PO-01 is missing from markdown report
            md_path = tdir / "report.md"
            md_path.write_text("# Report without the critical ID\n", encoding="utf-8")
            res_drop = subprocess.run(
                [sys.executable, str(MERGER_SCRIPT), "--inputs", str(tdir), "--check-report", str(md_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(res_drop.returncode, 2)
            self.assertIn("PO-01", res_drop.stdout + res_drop.stderr)

            # 1 = schema error
            (tdir / "02-bad.json").write_text('{"agent_id": "broken"}', encoding="utf-8")
            res_bad = subprocess.run(
                [sys.executable, str(MERGER_SCRIPT), "--inputs", str(tdir)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(res_bad.returncode, 1)


if __name__ == "__main__":
    unittest.main()
