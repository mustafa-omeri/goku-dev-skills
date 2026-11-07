#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2 TDD Seam Tests: API Contract Intelligence, 3-Tier Authz Surface,
Data Governance, Build/Fitness/Ops/ADR Signals, `kg_query.py` CLI, and v1 Shim Auto-Peer.
"""
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

HERE = Path(__file__).resolve().parent
SCRIPTS_DIR = HERE.parent
KG_QUERY_CLI = SCRIPTS_DIR / "kg_query.py"
FA_SCAN_CLI = SCRIPTS_DIR / "fa_scan.py"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class Phase2AnalyzersAndKnowledgeGraphSeamTests(unittest.TestCase):
    """Tests Phase 2 deep deterministic analyzers and `kg_query.py` CLI at public seams."""

    def test_01_api_contract_intelligence_openapi_and_static_dto_diff(self) -> None:
        from fa_scan import run_scan

        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            fe = ws / "client-web"
            be = ws / "server-api"
            (fe / "src" / "api").mkdir(parents=True)
            (fe / "package.json").write_text(
                json.dumps({"name": "client-web", "dependencies": {"react": "^18.2.0"}}),
                encoding="utf-8",
            )
            (fe / "src" / "api" / "reportsApi.ts").write_text(
                "export interface ReportSummaryDto {\n"
                "  reportTitle: string;\n"
                "  missingOnBackendField: string;\n"
                "  totalCount: boolean;\n"
                "}\n"
                "export const getReportSummary = () => apiClient.get<ApiResponse<ReportSummaryDto>>('/api/v1/reports/summary');\n",
                encoding="utf-8",
            )

            java_ctrl = be / "src" / "main" / "java" / "org" / "acme" / "api"
            java_dto = be / "src" / "main" / "java" / "org" / "acme" / "dto"
            java_ctrl.mkdir(parents=True)
            java_dto.mkdir(parents=True)
            (be / "pom.xml").write_text("<project><artifactId>server-api</artifactId></project>\n", encoding="utf-8")
            (java_dto / "ReportSummaryDto.java").write_text(
                "package org.acme.dto;\n"
                "public class ReportSummaryDto {\n"
                "  private String reportTitle;\n"
                "  private Integer totalCount;\n"
                "}\n",
                encoding="utf-8",
            )
            (java_ctrl / "ReportController.java").write_text(
                "package org.acme.api;\n"
                "@RestController\n"
                '@RequestMapping("/api/v1/reports")\n'
                "public class ReportController {\n"
                '  @GetMapping("/summary")\n'
                "  public ResponseEntity<ReportSummaryDto> summary() { return null; }\n"
                "}\n",
                encoding="utf-8",
            )

            snap = run_scan(fe, peers=[be])
            codes = {f["code"] for f in snap["facts"]}
            self.assertIn("DTO_CONTRACT_MISMATCH", codes)
            dto_facts = [f for f in snap["facts"] if f["code"] == "DTO_CONTRACT_MISMATCH"]
            self.assertTrue(any("missingOnBackendField" in f["summary"] or "totalCount" in f["summary"] for f in dto_facts))

    def test_02_three_tier_authz_and_security_filter_chain_false_positive_guard(self) -> None:
        from fa_scan import run_scan

        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            fe = ws / "portal-ui"
            be = ws / "portal-api"
            (fe / "src" / "pages").mkdir(parents=True)
            (fe / "package.json").write_text(
                json.dumps({"name": "portal-ui", "dependencies": {"react": "^18.2.0"}}),
                encoding="utf-8",
            )
            # ORG_MANAGER can see CreateTenantPanel, which posts to /api/v1/tenants
            (fe / "src" / "pages" / "CreateTenantPanel.tsx").write_text(
                "export function CreateTenantPanel({ role }: { role: string }) {\n"
                "  if (role === 'ORG_MANAGER' || role === 'SUPER_ADMIN') {\n"
                "    return <button onClick={() => apiClient.post('/api/v1/tenants', {})}>New Tenant</button>;\n"
                "  }\n"
                "  return null;\n"
                "}\n",
                encoding="utf-8",
            )

            java_dir = be / "src" / "main" / "java" / "org" / "acme"
            java_dir.mkdir(parents=True)
            (be / "pom.xml").write_text("<project><artifactId>portal-api</artifactId></project>\n", encoding="utf-8")
            # SecurityFilterChain protects /api/v1/billing/** via URL rule, leaves /api/v1/open-admin/** permitAll
            (java_dir / "SecurityConfig.java").write_text(
                "package org.acme;\n"
                "public class SecurityConfig {\n"
                "  public SecurityFilterChain filterChain(HttpSecurity http) {\n"
                '    http.authorizeHttpRequests(auth -> auth.requestMatchers("/api/v1/billing/**").hasRole("FINANCE_ADMIN"));\n'
                '    http.authorizeHttpRequests(auth -> auth.requestMatchers("/api/v1/open-admin/**").permitAll());\n'
                "    return http.build();\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            (java_dir / "TenantController.java").write_text(
                "package org.acme;\n"
                "@RestController\n"
                '@RequestMapping("/api/v1/tenants")\n'
                "public class TenantController {\n"
                '  @PreAuthorize("hasRole(\'SUPER_ADMIN\')")\n'
                "  @PostMapping\n"
                "  public Object createTenant() { return null; }\n"
                "}\n",
                encoding="utf-8",
            )
            # Protected ONLY by SecurityFilterChain -> must NOT trigger BACKEND_AUTHORIZATION_GAP
            (java_dir / "BillingController.java").write_text(
                "package org.acme;\n"
                "@RestController\n"
                '@RequestMapping("/api/v1/billing")\n'
                "public class BillingController {\n"
                '  @DeleteMapping("/invoices/{id}")\n'
                "  public void deleteInvoice() {}\n"
                "}\n",
                encoding="utf-8",
            )
            # Explicitly permitAll mutating admin endpoint -> MUST trigger BACKEND_AUTHORIZATION_GAP
            (java_dir / "OpenAdminController.java").write_text(
                "package org.acme;\n"
                "@RestController\n"
                '@RequestMapping("/api/v1/open-admin")\n'
                "public class OpenAdminController {\n"
                '  @DeleteMapping("/purge")\n'
                "  public void purgeAll() {}\n"
                "}\n",
                encoding="utf-8",
            )
            # Org-scoped entity fetched by raw id without org scope -> RESOURCE_OWNERSHIP_GAP
            (java_dir / "WorkspaceRecord.java").write_text(
                "package org.acme;\n"
                "@Entity\n"
                "public class WorkspaceRecord {\n"
                "  private Long id;\n"
                "  private Long organizationId;\n"
                "}\n",
                encoding="utf-8",
            )
            (java_dir / "WorkspaceRecordRepository.java").write_text(
                "package org.acme;\n"
                "public interface WorkspaceRecordRepository extends JpaRepository<WorkspaceRecord, Long> {}\n",
                encoding="utf-8",
            )
            (java_dir / "WorkspaceRecordService.java").write_text(
                "package org.acme;\n"
                "@Service\n"
                "public class WorkspaceRecordService {\n"
                "  private final WorkspaceRecordRepository repo;\n"
                "  public WorkspaceRecord getOne(Long id) { return repo.findById(id).orElse(null); }\n"
                "}\n",
                encoding="utf-8",
            )

            snap = run_scan(fe, peers=[be])
            codes = {f["code"] for f in snap["facts"]}
            self.assertIn("UI_AUTHORIZATION_MISMATCH", codes)
            self.assertIn("BACKEND_AUTHORIZATION_GAP", codes)
            self.assertIn("RESOURCE_OWNERSHIP_GAP", codes)

            gap_locations = [f["location"] for f in snap["facts"] if f["code"] == "BACKEND_AUTHORIZATION_GAP"]
            self.assertTrue(any("OpenAdminController.java" in loc for loc in gap_locations))
            self.assertFalse(any("BillingController.java" in loc for loc in gap_locations))

    def test_03_data_governance_build_fitness_ops_and_adr_signals(self) -> None:
        from fa_scan import run_scan

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps({"name": "monolith-app", "dependencies": {"react": "^18.2.0"}}),
                encoding="utf-8",
            )
            (root / "vite.config.ts").write_text(
                "export default { build: { chunkSizeWarningLimit: 2500 } };\n",
                encoding="utf-8",
            )
            # Cyclic imports between modA and modB
            (root / "src" / "modules" / "alpha").mkdir(parents=True)
            (root / "src" / "modules" / "beta").mkdir(parents=True)
            (root / "src" / "modules" / "alpha" / "alphaService.ts").write_text(
                "import { betaHelper } from '../beta/betaService';\n"
                "export const alphaHelper = () => betaHelper();\n",
                encoding="utf-8",
            )
            (root / "src" / "modules" / "beta" / "betaService.ts").write_text(
                "import { alphaHelper } from '../alpha/alphaService';\n"
                "export const betaHelper = () => alphaHelper();\n",
                encoding="utf-8",
            )

            mig = root / "db" / "migrations"
            mig.mkdir(parents=True)
            (mig / "V1__schema.sql").write_text(
                "CREATE TABLE invoices (\n"
                "  id BIGINT PRIMARY KEY,\n"
                "  organization_id BIGINT NOT NULL REFERENCES organizations(id),\n"
                "  national_id VARCHAR(32)\n"
                ");\n"
                "ALTER TABLE invoices DROP COLUMN legacy_code;\n",
                encoding="utf-8",
            )

            java_dir = root / "src" / "main" / "java" / "org" / "acme"
            java_dir.mkdir(parents=True)
            (java_dir / "InvoiceService.java").write_text(
                "package org.acme;\n"
                "@Service\n"
                "public class InvoiceService {\n"
                "  private final InvoiceRepository invoiceRepository;\n"
                "  public void syncAll(List<Long> ids) {\n"
                "    for (Long id : ids) {\n"
                "      invoiceRepository.findById(id);\n"
                "    }\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )

            snap = run_scan(root)
            codes = {f["code"] for f in snap["facts"]}
            self.assertIn("BUNDLE_BUDGET_RISK", codes)
            self.assertIn("CIRCULAR_MODULE_DEPENDENCY", codes)
            self.assertIn("MISSING_FK_INDEX", codes)
            self.assertIn("RISKY_MIGRATION_DDL", codes)
            self.assertIn("STATIC_N_PLUS_ONE_CANDIDATE", codes)
            self.assertIn("INFERRED_IMPLICIT_ADR", codes)

    def test_04_kg_query_cli_trace_unresolved_consumers_impact_and_role_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            fe = ws / "ui"
            be = ws / "api"
            out_dir = ws / "out"
            (fe / "src" / "hooks").mkdir(parents=True)
            (fe / "src" / "api").mkdir(parents=True)
            (fe / "package.json").write_text(
                json.dumps({"name": "ui", "dependencies": {"react": "^18.2.0"}}),
                encoding="utf-8",
            )
            (fe / "src" / "api" / "metricsApi.ts").write_text(
                "export const fetchTrends = () => apiClient.get('/api/v1/metrics/trends');\n"
                "export const fetchKpis = () => apiClient.get('/api/v1/metrics/kpis');\n",
                encoding="utf-8",
            )
            (fe / "src" / "hooks" / "useMetrics.ts").write_text(
                "export function useMetrics() {\n"
                "  return metricsApi.fetchTrends();\n"
                "}\n"
                "export function useKpis() {\n"
                "  return metricsApi.fetchKpis();\n"
                "}\n",
                encoding="utf-8",
            )
            java_dir = be / "src" / "main" / "java" / "org" / "acme"
            java_dir.mkdir(parents=True)
            (be / "pom.xml").write_text("<project><artifactId>api</artifactId></project>\n", encoding="utf-8")
            (java_dir / "MetricsController.java").write_text(
                "@RestController\n"
                '@RequestMapping("/api/v1/metrics")\n'
                "public class MetricsController {\n"
                '  @PreAuthorize("hasRole(\'ANALYST\')")\n'
                '  @GetMapping("/kpis")\n'
                "  public Object kpis() { return null; }\n"
                "}\n",
                encoding="utf-8",
            )

            scan_proc = subprocess.run(
                [sys.executable, str(FA_SCAN_CLI), "--root", str(fe), "--peer", str(be), "--out-dir", str(out_dir)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(scan_proc.returncode, 0, scan_proc.stderr)
            kg_path = out_dir / "knowledge-graph.json"
            self.assertTrue(kg_path.is_file())

            # 1. trace
            t_proc = subprocess.run(
                [sys.executable, str(KG_QUERY_CLI), "--kg", str(kg_path), "trace", "--from", "Hook:useMetrics"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(t_proc.returncode, 0, t_proc.stderr)
            t_data = json.loads(t_proc.stdout)
            self.assertTrue(t_data["has_unresolved"])

            # 2. unresolved
            u_proc = subprocess.run(
                [sys.executable, str(KG_QUERY_CLI), "--kg", str(kg_path), "unresolved", "--kind", "handled_by"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(u_proc.returncode, 0, u_proc.stderr)
            u_data = json.loads(u_proc.stdout)
            self.assertEqual(len(u_data["unresolved"]), 1)

            # 3. consumers & impact
            c_proc = subprocess.run(
                [
                    sys.executable,
                    str(KG_QUERY_CLI),
                    "--kg",
                    str(kg_path),
                    "consumers",
                    "Endpoint:GET:/api/v1/metrics/kpis",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(c_proc.returncode, 0, c_proc.stderr)
            c_data = json.loads(c_proc.stdout)
            self.assertTrue(any(c["consumer"] == "Hook:useKpis" for c in c_data["consumers"]))

            # 4. role-surface
            r_proc = subprocess.run(
                [sys.executable, str(KG_QUERY_CLI), "--kg", str(kg_path), "role-surface", "GUEST"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(r_proc.returncode, 0, r_proc.stderr)
            r_data = json.loads(r_proc.stdout)
            self.assertIn("Endpoint:GET:/api/v1/metrics/kpis", r_data["blocked_endpoints"])

    def test_05_v1_gap_scanner_shim_auto_discovers_sibling_peer(self) -> None:
        import gap_scanner

        with tempfile.TemporaryDirectory() as ws_tmp:
            ws = Path(ws_tmp)
            fe = ws / "client-spa"
            be = ws / "service-core"
            (fe / "src" / "api").mkdir(parents=True)
            (fe / "package.json").write_text(
                json.dumps({"name": "client-spa", "dependencies": {"react": "^18.2.0"}}),
                encoding="utf-8",
            )
            (fe / "src" / "api" / "items.ts").write_text(
                "export const getItems = () => apiClient.get('/api/v1/items/active');\n",
                encoding="utf-8",
            )
            java_dir = be / "src" / "main" / "java" / "org" / "acme"
            java_dir.mkdir(parents=True)
            (be / "pom.xml").write_text("<project><artifactId>service-core</artifactId></project>\n", encoding="utf-8")
            (java_dir / "ItemController.java").write_text(
                "@RestController\n"
                '@RequestMapping("/api/v1/items")\n'
                "public class ItemController {\n"
                '  @GetMapping("/active")\n'
                "  public Object active() { return null; }\n"
                '  @GetMapping("/archived")\n'
                "  public Object archived() { return null; }\n"
                "}\n",
                encoding="utf-8",
            )

            # Call gap_scanner.scan WITHOUT peers argument!
            report = gap_scanner.scan(fe)
            self.assertEqual(report["schema"], "feature-architect/gap-scan@1")
            self.assertIn(be.resolve().as_posix(), report["roots"]["peers"])
            orphan_paths = [e["path"] for e in report["orphan_endpoints"]]
            self.assertIn("/api/v1/items/archived", orphan_paths)
            self.assertNotIn("/api/v1/items/active", orphan_paths)

    def test_06_spring_consumes_mapping_resolves_relative_evidence_path(self) -> None:
        from fa_scan import run_scan

        with tempfile.TemporaryDirectory() as ws_tmp:
            ws = Path(ws_tmp)
            be = ws / "service-core"
            java_dir = be / "src" / "main" / "java" / "org" / "acme"
            java_dir.mkdir(parents=True)
            (be / "pom.xml").write_text("<project><artifactId>service-core</artifactId></project>\n", encoding="utf-8")
            (java_dir / "AdminTenantController.java").write_text(
                "@RestController\n"
                '@RequestMapping("/api/v1/admin/tenants")\n'
                "public class AdminTenantController {\n"
                '  @PostMapping(consumes = "application/json")\n'
                "  public Object createTenant() { return null; }\n"
                '  @RequestMapping(value = "/legacy", method = RequestMethod.POST)\n'
                "  public Object createLegacyTenant() { return null; }\n"
                "}\n",
                encoding="utf-8",
            )
            snap = run_scan(be)
            authz_facts = [f for f in snap["facts"] if f["code"] == "BACKEND_AUTHORIZATION_GAP"]
            self.assertEqual(len(authz_facts), 2)
            for af in authz_facts:
                ev_ref = af["evidence"][0]["ref"]
                file_part = ev_ref.rsplit(":", 1)[0]
                self.assertTrue((be / file_part).is_file(), f"Evidence file did not resolve: {ev_ref}")
                self.assertNotIn("application/json", af["summary"])


if __name__ == "__main__":
    unittest.main()
