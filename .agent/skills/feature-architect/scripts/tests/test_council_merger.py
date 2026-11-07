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

    def test_not_applicable_conditional_validation_rejects_score_and_findings(self) -> None:
        bad_na_score = _make_hat_report(
            "snr-seo-specialist",
            "Senior Technical SEO & Web Performance Specialist",
            "SEO",
            health_score=65,
            applicability="not_applicable",
            not_applicable_reason="Private CLI tool without public web pages.",
            audits=[],
            constraints=[],
        )
        errs1 = council_merger.validate_report(bad_na_score)
        self.assertTrue(any("health_score" in e and "null" in e for e in errs1), errs1)

        bad_na_audits = _make_hat_report(
            "snr-seo-specialist",
            "Senior Technical SEO & Web Performance Specialist",
            "SEO",
            health_score=None,
            applicability="not_applicable",
            not_applicable_reason="Private CLI tool without public web pages.",
        )
        errs2 = council_merger.validate_report(bad_na_audits)
        self.assertTrue(any("audits" in e and "empty" in e for e in errs2), errs2)

    def test_health_score_rationale_validation_and_sample_reports(self) -> None:
        too_short = _make_hat_report()
        too_short["health_score_rationale"] = "Too short"
        errs = council_merger.validate_report(too_short)
        self.assertTrue(any("health_score_rationale" in e for e in errs), errs)

        samples = council_merger.build_sample_reports()
        for s in samples:
            self.assertEqual(council_merger.validate_report(s), [])
            if s.get("applicability", "applicable") == "applicable":
                self.assertGreaterEqual(len(s.get("health_score_rationale", "")), 20)

    def test_cross_section_deduplication_and_po_boundary_governance(self) -> None:
        po_slop = _make_hat_report(
            "snr-product-owner",
            "Senior Product Owner & Domain Strategist",
            "PO",
            health_score=62,
            audits=[
                {
                    "id": "PO-01",
                    "category": "STUB_PAGE",
                    "severity": "CRITICAL",
                    "location": "src/features/dashboard/MainDashboard.tsx:412",
                    "evidence": "src/features/dashboard/MainDashboard.tsx:412 -> Route path='settings' element={<PlaceholderPage />}",
                    "confidence": "verified",
                    "issue": "Settings route renders a placeholder page.",
                    "fix_proposal": "Define product requirements for user account preferences on the settings route.",
                }
            ],
            ui_ux_mismatches=[
                {
                    "screen_or_component": "MainDashboard Settings",
                    "theme_reference_gap": "PlaceholderPage Living Surface ve kurumsal mavi kart sistemine uymuyor.",
                    "ux_impact": "Settings route looks unfinished.",
                    "correction": "Design modern blue cards.",
                }
            ],
            new_features=[
                {
                    "feature_id": "FEAT-PO-01",
                    "title": "Full Settings Hub",
                    "rationale": "Settings page is a placeholder.",
                    "user_value": "Users can edit settings.",
                    "reach": 9,
                    "impact_score": 9,
                    "confidence": 1.0,
                    "effort": "M",
                    "target_location": "src/features/settings/Settings.tsx",
                    "five_layer_slice_summary": "1. UserPreferences & NotificationSettings entity/migration -> 2. GET/PUT /api/v1/users/me/settings -> 3. settings.service.ts -> 4. Settings UI -> 5. Route",
                }
            ],
            constraints=[
                "Tüm yeni sayfalar rol tabanlı yetki kontrolü (RBAC) ile korunmalı ve mobil uyumlu olmalıdır."
            ],
        )
        merged = council_merger.merge([po_slop])
        gov = merged["governance"]
        warning_codes = {w["code"] for w in gov["warnings"]}
        self.assertIn("CROSS_SECTION_DUPLICATE_FEATURE", warning_codes)
        self.assertIn("CROSS_SECTION_DUPLICATE_MISMATCH", warning_codes)
        self.assertIn("PO_BOUNDARY_TECHNICAL_ARCHITECTURE", warning_codes)
        self.assertIn("PO_BOUNDARY_VISUAL_THEME", warning_codes)
        self.assertIn("GENERIC_BOILERPLATE_CONSTRAINT", warning_codes)
        # Duplicate feature & visual mismatch are suppressed from ranked outputs
        self.assertEqual(len(merged["features_ranked"]), 0)
        self.assertEqual(len(merged["ui_ux_mismatches"]), 0)

    def test_v1_to_v7_evidence_governance_with_kg_and_six_verb_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "pages").mkdir(parents=True)
            (root / "src" / "legacy").mkdir(parents=True)
            (root / "src" / "pages" / "ActiveSettings.tsx").write_text(
                "export function ActiveSettings() {\n  return <div>Coming Soon</div>;\n}\n",
                encoding="utf-8",
            )
            (root / "src" / "legacy" / "OldCompanyDashboard.tsx").write_text(
                "export function OldCompanyDashboard() {\n  return <div>Under development</div>;\n}\n",
                encoding="utf-8",
            )
            kg_data = {
                "nodes": [
                    {"id": "Route:/settings", "kind": "Route", "name": "/settings", "file": "src/App.tsx", "line": 10},
                    {"id": "Screen:ActiveSettings", "kind": "Screen", "name": "ActiveSettings", "file": "src/pages/ActiveSettings.tsx", "line": 1},
                    {"id": "Endpoint:GET:/api/v1/audit-logs", "kind": "Endpoint", "name": "GET /api/v1/audit-logs", "file": "src/server/AuditController.java", "line": 20},
                ],
                "edges": [
                    {"source": "Route:/settings", "target": "Screen:ActiveSettings", "kind": "renders", "unresolved": False},
                ],
            }
            po = _make_hat_report(
                "snr-product-owner",
                "Senior Product Owner & Domain Strategist",
                "PO",
                audits=[
                    {
                        "id": "PO-01",
                        "category": "STUB_PAGE",
                        "severity": "HIGH",
                        "location": "src/pages/ActiveSettings.tsx:2",
                        "evidence": "src/pages/ActiveSettings.tsx:2 -> Coming Soon",
                        "confidence": "verified",
                        "issue": "Active settings route is incomplete.",
                        "fix_proposal": "Complete user preference workflow on active route.",
                    },
                    {
                        "id": "PO-02",
                        "category": "STUB_PAGE",
                        "severity": "HIGH",
                        "location": "src/legacy/OldCompanyDashboard.tsx:2",
                        "evidence": "src/legacy/OldCompanyDashboard.tsx:2 -> Under development",
                        "confidence": "verified",
                        "issue": "Legacy company dashboard stub file.",
                        "fix_proposal": "Remove unused legacy dashboard.",
                    },
                    {
                        "id": "PO-03",
                        "category": "PRODUCT",
                        "severity": "HIGH",
                        "location": "src/ghost/MissingFile.tsx:99",
                        "evidence": "src/ghost/MissingFile.tsx:99 -> hallucinated line",
                        "confidence": "verified",
                        "issue": "Hallucinated file reference.",
                        "fix_proposal": "Fix hallucination.",
                    },
                ],
                constraints=[],
            )
            arch = _make_hat_report(
                "snr-software-architect",
                "Senior Software Architect & Systems Engineer",
                "ARCH",
                audits=[
                    {
                        "id": "ARCH-01",
                        "category": "ORPHAN_API_DB",
                        "severity": "MEDIUM",
                        "location": "src/pages/ActiveSettings.tsx:1",
                        "evidence": "src/pages/ActiveSettings.tsx:1 -> GET /api/v1/audit-logs exists in backend",
                        "confidence": "verified",
                        "issue": "Existing backend endpoint GET /api/v1/audit-logs is not wired to UI.",
                        "fix_proposal": "Connect existing endpoint to UI.",
                    }
                ],
                constraints=[],
            )
            merged = council_merger.merge([po, arch], project_root=root, kg_data=kg_data)
            by_id = {a["id"]: a for a in merged["audits"]}
            # Hallucinated file PO-03 is rejected by V1
            self.assertNotIn("PO-03", by_id)
            self.assertIn("PO-03", merged["governance"]["rejected_finding_ids"])
            # Active stub PO-01 -> COMPLETE; unreachable legacy PO-02 -> REMOVE + warning; existing endpoint ARCH-01 -> CONNECT
            self.assertEqual(by_id["PO-01"]["decision"], "COMPLETE")
            self.assertEqual(by_id["PO-02"]["decision"], "REMOVE")
            self.assertEqual(by_id["ARCH-01"]["decision"], "CONNECT")
            wcodes = {w["code"] for w in merged["governance"]["warnings"]}
            self.assertIn("UNREACHABLE_LEGACY_COMPONENT_FOR_PO", wcodes)

    def test_challenge_round_revises_decisions_and_attaches_security_blockers(self) -> None:
        po = _make_hat_report(
            "snr-product-owner",
            "Senior Product Owner & Domain Strategist",
            "PO",
            audits=[
                {
                    "id": "PO-01",
                    "category": "CORE_MODULE_GAP",
                    "severity": "HIGH",
                    "location": "src/pages/CompaniesPage.tsx:30",
                    "evidence": "src/pages/CompaniesPage.tsx:30 -> button navigates to /companies/new (404)",
                    "confidence": "verified",
                    "issue": "Create organization flow is missing from UI.",
                    "fix_proposal": "Build new organization creation backend and form.",
                }
            ],
            constraints=[],
        )
        qa = _make_hat_report(
            "snr-qa-security-auditor",
            "Senior QA, Security & 5-Layer TDD Auditor",
            "QA",
            audits=[
                {
                    "id": "QA-01",
                    "category": "SECURITY",
                    "severity": "CRITICAL",
                    "location": "src/pages/CompaniesPage.tsx:30",
                    "evidence": "src/pages/CompaniesPage.tsx:30 -> POST /api/v1/organizations lacks role guard",
                    "confidence": "verified",
                    "issue": "Endpoint lacks server-side role authorization.",
                    "fix_proposal": "Add @PreAuthorize guard before wiring UI.",
                }
            ],
            constraints=[],
        )
        challenges = [
            {
                "challenger": "snr-software-architect",
                "target_id": "PO-01",
                "challenge_type": "EXISTING_CAPABILITY",
                "evidence": "OrganizationController.java:42 -> POST /api/v1/organizations already exists",
                "revised_decision": "CONNECT",
                "resolution": "Backend endpoint already exists; wire existing modal/endpoint instead of rebuilding.",
            }
        ]
        merged = council_merger.merge([po, qa], challenges=challenges)
        by_id = {a["id"]: a for a in merged["audits"]}
        self.assertEqual(by_id["PO-01"]["decision"], "CONNECT")
        self.assertIn("QA-01", by_id["PO-01"]["blocked_by"])
        self.assertEqual(len(merged["challenge_resolutions"]), 1)

    def test_g1_agent_id_to_finding_and_feature_prefix_lock(self) -> None:
        wrong_audit_prefix = _make_hat_report(
            "snr-product-owner",
            "Senior Product Owner & Domain Strategist",
            "ARCH",
        )
        errs_a = council_merger.validate_report(wrong_audit_prefix)
        self.assertTrue(any("PO-" in e for e in errs_a), f"Expected prefix mismatch error, got: {errs_a}")

        wrong_feat_prefix = _make_hat_report(
            "snr-software-architect",
            "Senior Software Architect & Systems Engineer",
            "ARCH",
            new_features=[
                {
                    "feature_id": "FEAT-UX-01",
                    "title": "Typed API Client Layer",
                    "rationale": "Missing service seam.",
                    "user_value": "Reliable data mutations.",
                    "reach": 8,
                    "impact_score": 8,
                    "confidence": 1.0,
                    "effort": "M",
                    "five_layer_slice_summary": "1. Schema -> 2. Endpoint -> 3. Client -> 4. UI -> 5. Tests",
                }
            ],
        )
        errs_f = council_merger.validate_report(wrong_feat_prefix)
        self.assertTrue(any("FEAT-ARCH-" in e for e in errs_f), f"Expected feature_id prefix error, got: {errs_f}")

    def test_g2_all_six_hats_v2_and_v5_deduplication_and_unreachable_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "legacy").mkdir(parents=True)
            (root / "src" / "features" / "dashboard").mkdir(parents=True)
            (root / "src" / "legacy" / "OldViewer.tsx").write_text("export const OldViewer = () => null;\n", encoding="utf-8")
            (root / "src" / "features" / "dashboard" / "MainDashboard.tsx").write_text(
                "export const MainDashboard = () => null;\n", encoding="utf-8"
            )
            kg_data = {
                "nodes": [
                    {
                        "id": "Route:/main",
                        "kind": "Route",
                        "name": "/main",
                        "file": "src/features/dashboard/MainDashboard.tsx",
                        "line": 1,
                    }
                ],
                "edges": [],
            }
            ux = _make_hat_report(
                "principal-ui-ux-specialist",
                "Principal UI/UX & Design Systems Specialist",
                "UX",
                audits=[
                    {
                        "id": "UX-01",
                        "category": "STUB_PAGE",
                        "severity": "HIGH",
                        "location": "src/legacy/OldViewer.tsx:1",
                        "evidence": "src/legacy/OldViewer.tsx:1 -> under development",
                        "confidence": "verified",
                        "issue": "Legacy viewer stub screen.",
                        "fix_proposal": "Build full viewer screen.",
                    }
                ],
            )
            grw = _make_hat_report(
                "snr-growth-marketing",
                "Senior Growth & Product Marketing Specialist",
                "GRW",
                audits=[
                    {
                        "id": "GRW-01",
                        "category": "GROWTH",
                        "severity": "CRITICAL",
                        "location": "src/features/dashboard/MainDashboard.tsx:1",
                        "evidence": "src/features/dashboard/MainDashboard.tsx:1 -> analytics route lacks reminder nudge",
                        "confidence": "verified",
                        "issue": "Analytics module lacks reminder nudge button for pending assessments.",
                        "fix_proposal": "Add reminder nudge action to analytics view.",
                    }
                ],
                new_features=[
                    {
                        "feature_id": "FEAT-GRW-01",
                        "title": "Smart Reminder Nudge Button for Pending Assessments",
                        "rationale": "Analytics module lacks reminder nudge button for pending assessments.",
                        "user_value": "Managers can nudge pending users.",
                        "reach": 8,
                        "impact_score": 8,
                        "confidence": 0.8,
                        "effort": "M",
                        "five_layer_slice_summary": "1. DB -> 2. API -> 3. Client -> 4. Nudge UI -> 5. KPI",
                    }
                ],
            )
            merged = council_merger.merge([ux, grw], project_root=root, kg_data=kg_data)
            by_id = {a["id"]: a for a in merged["audits"]}
            self.assertEqual(by_id["UX-01"]["decision"], "REMOVE")
            wcodes = {w["code"] for w in merged["governance"]["warnings"]}
            self.assertIn("UNREACHABLE_LEGACY_COMPONENT", wcodes)
            self.assertIn("CROSS_SECTION_DUPLICATE_FEATURE", wcodes)
            self.assertEqual(len(merged["features_ranked"]), 0)

    def test_g3_all_six_hats_v6_role_boundary_and_anti_slop_gates(self) -> None:
        arch = _make_hat_report(
            "snr-software-architect",
            "Senior Software Architect & Systems Engineer",
            "ARCH",
            audits=[
                {
                    "id": "ARCH-01",
                    "category": "ARCHITECTURE",
                    "severity": "LOW",
                    "location": "src/pages/Profile.tsx:10",
                    "evidence": "src/pages/Profile.tsx:10 -> card color",
                    "confidence": "verified",
                    "issue": "Card background hex #1B6CA8 and border-radius do not match mavi kart theme.",
                    "fix_proposal": "Change hex color to #0A417A and adjust box-shadow.",
                }
            ],
        )
        grw = _make_hat_report(
            "snr-growth-marketing",
            "Senior Growth & Product Marketing Specialist",
            "GRW",
            audits=[],
            new_features=[
                {
                    "feature_id": "FEAT-GRW-02",
                    "title": "Automated Digest Campaign",
                    "rationale": "Sending automated nudges tamamlanma oranını %35 artırır without any telemetry.",
                    "user_value": "Higher completion.",
                    "reach": 7,
                    "impact_score": 8,
                    "confidence": 0.8,
                    "effort": "M",
                    "five_layer_slice_summary": "1. DB -> 2. Worker -> 3. Client -> 4. UI -> 5. Metrics",
                }
            ],
        )
        seo = _make_hat_report(
            "snr-seo-specialist",
            "Senior Technical SEO & Web Performance Specialist",
            "SEO",
            audits=[
                {
                    "id": "SEO-01",
                    "category": "SEO",
                    "severity": "MEDIUM",
                    "location": "src/features/dashboard/MainDashboard.tsx:20",
                    "evidence": "src/features/dashboard/MainDashboard.tsx:20 -> /main/settings protected route",
                    "confidence": "verified",
                    "issue": "Protected /main/settings route is not indexed in Google.",
                    "fix_proposal": "Add /main/settings to public sitemap.xml and set robots index, follow.",
                }
            ],
        )
        qa = _make_hat_report(
            "snr-qa-security-auditor",
            "Senior QA, Security & 5-Layer TDD Auditor",
            "QA",
            audits=[
                {
                    "id": "QA-01",
                    "category": "SECURITY",
                    "severity": "HIGH",
                    "location": "src/features/auth/Login.tsx:15",
                    "evidence": "src/features/auth/Login.tsx:15 -> login form",
                    "confidence": "verified",
                    "issue": "Missing brute-force protection on login form.",
                    "fix_proposal": "Login formunda istemci tarafı rate-limit veya kilitleme geri bildirimi eklenmeli.",
                }
            ],
        )
        merged = council_merger.merge([arch, grw, seo, qa])
        wcodes = {w["code"] for w in merged["governance"]["warnings"]}
        self.assertIn("ARCH_BOUNDARY_VISUAL_STYLING", wcodes)
        self.assertIn("FABRICATED_METRIC_CLAIM", wcodes)
        self.assertIn("SEO_PROTECTED_ROUTE_INDEXING", wcodes)
        self.assertIn("QA_CLIENT_ONLY_SECURITY_FIX", wcodes)

    def test_g4_audit_council_dir_and_borda_coordination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cdir = Path(tmp)
            samples = council_merger.build_sample_reports()
            # Introduce a short role title and a fabricated metric claim in one report to verify directory audit
            samples[4]["role"] = "Senior Growth Marketing Specialist"
            samples[4]["new_features"] = [
                {
                    "feature_id": "FEAT-GRW-01",
                    "title": "Onboarding Nudge",
                    "rationale": "Bu özellik etkileşimi %40 artırır.",
                    "user_value": "Faster activation.",
                    "reach": 8,
                    "impact_score": 8,
                    "confidence": 0.8,
                    "effort": "S",
                    "five_layer_slice_summary": "1. Flag -> 2. Endpoint -> 3. Service -> 4. Card -> 5. Hide",
                }
            ]
            for idx, rep in enumerate(samples, start=1):
                (cdir / f"0{idx}-{rep['agent_id']}.json").write_text(
                    json.dumps(rep, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            audit_res = council_merger.audit_council_directory(cdir)
            self.assertEqual(audit_res["hat_count"], 6)
            self.assertEqual(audit_res["missing_hats"], [])
            self.assertGreaterEqual(len(audit_res["role_title_mismatches"]), 1)
            wcodes = {w["code"] for w in audit_res["governance"]["warnings"]}
            self.assertIn("FABRICATED_METRIC_CLAIM", wcodes)
            self.assertIn("borda_arbitration_ready", audit_res)


if __name__ == "__main__":
    unittest.main()
