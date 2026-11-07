#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 1 TDD Seam Tests: Project Intelligence Discovery, Error-Isolated Engine,
Frontend/Backend Analyzers, Determinism, and v1 Shim Compatibility.
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
FA_SCAN_CLI = SCRIPTS_DIR / "fa_scan.py"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class Phase1DiscoveryAndScanSeamTests(unittest.TestCase):
    """Tests public seams `fa_engine.discovery.discover_project` and `fa_scan.run_scan`."""

    def test_01_parameterless_peer_discovery_requires_overlap_not_folder_name(self) -> None:
        from fa_engine.discovery import discover_project

        with tempfile.TemporaryDirectory() as workspace_tmp:
            ws = Path(workspace_tmp)
            fe_root = ws / "web-portal"
            real_be = ws / "core-service"
            decoy_be = ws / "legacy-backend"

            (fe_root / "src" / "api").mkdir(parents=True)
            (fe_root / "package.json").write_text(
                json.dumps({"name": "web-portal", "dependencies": {"react": "^18.2.0", "react-router-dom": "^6.20.0"}}),
                encoding="utf-8",
            )
            (fe_root / "vite.config.ts").write_text(
                "export default { server: { proxy: { '/api': 'http://localhost:8080' } } };\n",
                encoding="utf-8",
            )
            (fe_root / "src" / "api" / "ordersApi.ts").write_text(
                "export const listOrders = () => apiClient.get('/api/v1/orders/summary');\n"
                "export const createOrder = (p: unknown) => apiClient.post('/api/v1/orders', p);\n",
                encoding="utf-8",
            )

            # Real backend matching API paths and port 8080
            java_dir = real_be / "src" / "main" / "java" / "org" / "acme" / "orders"
            java_dir.mkdir(parents=True)
            (real_be / "pom.xml").write_text(
                "<project><dependencies><dependency><artifactId>springdoc-openapi-starter-webmvc-ui</artifactId></dependency></dependencies></project>\n",
                encoding="utf-8",
            )
            (real_be / "src" / "main" / "resources").mkdir(parents=True)
            (real_be / "src" / "main" / "resources" / "application.yml").write_text(
                "server:\n  port: 8080\n",
                encoding="utf-8",
            )
            (java_dir / "OrderController.java").write_text(
                "@RestController\n"
                '@RequestMapping({"/v1/orders", "/api/v1/orders"})\n'
                "public class OrderController {\n"
                '  @GetMapping("/summary")\n'
                "  public Object summary() { return null; }\n"
                "  @PostMapping\n"
                "  public Object create() { return null; }\n"
                "}\n",
                encoding="utf-8",
            )

            # Decoy backend has "backend" in folder name, but 0% API overlap
            decoy_dir = decoy_be / "src"
            decoy_dir.mkdir(parents=True)
            (decoy_dir / "server.js").write_text(
                "app.get('/api/v1/weather/forecast', (req, res) => res.json({}));\n",
                encoding="utf-8",
            )

            profile = discover_project(fe_root)
            confirmed_paths = [Path(p.path).resolve() for p in profile.peers if p.status == "CONFIRMED"]
            self.assertIn(real_be.resolve(), confirmed_paths)
            self.assertNotIn(decoy_be.resolve(), confirmed_paths)
            self.assertTrue(any("springdoc" in c.kind or "openapi" in c.kind for c in profile.contract_sources))

    def test_02_schema_source_conflict_vs_stateless_cli_not_applicable(self) -> None:
        from fa_engine.discovery import discover_project

        with tempfile.TemporaryDirectory() as tmp_conflict, tempfile.TemporaryDirectory() as tmp_cli:
            c_root = Path(tmp_conflict)
            (c_root / "prisma").mkdir()
            (c_root / "prisma" / "schema.prisma").write_text(
                "model Account {\n  id String @id\n  title String\n}\n",
                encoding="utf-8",
            )
            mig_dir = c_root / "src" / "main" / "resources" / "db" / "migration"
            mig_dir.mkdir(parents=True)
            (mig_dir / "V1__init.sql").write_text(
                "CREATE TABLE accounts (id VARCHAR(36) PRIMARY KEY, title VARCHAR(120));\n",
                encoding="utf-8",
            )
            c_profile = discover_project(c_root)
            self.assertGreaterEqual(len(c_profile.schema_sources), 2)
            self.assertTrue(c_profile.has_schema_conflict)

            cli_root = Path(tmp_cli)
            (cli_root / "pyproject.toml").write_text('[project]\nname = "pure-cli"\n', encoding="utf-8")
            (cli_root / "cli.py").write_text("def main():\n    print('ok')\n", encoding="utf-8")
            cli_profile = discover_project(cli_root)
            self.assertEqual(cli_profile.schema_sources, [])
            self.assertFalse(cli_profile.has_schema_conflict)
            self.assertEqual(cli_profile.topology, "cli-or-library")

    def test_03_frontend_detects_unwired_callback_prop_dummy_data_and_fe_only_screen(self) -> None:
        from fa_scan import run_scan

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps({"name": "spa-app", "dependencies": {"react": "^18.0.0", "react-router-dom": "^6.0.0"}}),
                encoding="utf-8",
            )
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "pages").mkdir(parents=True)

            # Child defines optional onViewDetails callback, rendered as clickable control
            (root / "src" / "components" / "SummaryCard.tsx").write_text(
                "interface SummaryCardProps {\n"
                "  title: string;\n"
                "  onViewDetails?: () => void;\n"
                "}\n"
                "export function SummaryCard({ title, onViewDetails }: SummaryCardProps) {\n"
                "  return (\n"
                "    <div>\n"
                "      <h3>{title}</h3>\n"
                "      <button onClick={onViewDetails}>View Details</button>\n"
                "    </div>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )

            # Parent renders SummaryCard WITHOUT passing onViewDetails, and defines hardcoded dummy items
            (root / "src" / "pages" / "OverviewPage.tsx").write_text(
                "import { SummaryCard } from '../components/SummaryCard';\n"
                "const quickActions = [\n"
                "  { id: '1', label: 'Create Workspace', badge: 5, href: '#' },\n"
                "  { id: '2', label: 'Export Report', badge: 12, href: '#' }\n"
                "];\n"
                "export function OverviewPage() {\n"
                "  return (\n"
                "    <main>\n"
                '      <SummaryCard title="Active Sessions" />\n'
                "      {quickActions.map(a => <a key={a.id} href={a.href}>{a.label}</a>)}\n"
                "    </main>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )

            # Screen with interactive form/toggles saving only to local state, zero API calls
            (root / "src" / "pages" / "PreferencesMatrixPage.tsx").write_text(
                "import { useState } from 'react';\n"
                "export function PreferencesMatrixPage() {\n"
                "  const [matrix, setMatrix] = useState({ email: true, sms: false });\n"
                "  const handleSave = () => { setMatrix({ ...matrix }); };\n"
                "  return <section><button onClick={handleSave}>Save Matrix</button></section>;\n"
                "}\n",
                encoding="utf-8",
            )

            (root / "src" / "App.tsx").write_text(
                "export function App() {\n"
                "  return (\n"
                "    <Routes>\n"
                '      <Route path="/overview" element={<OverviewPage />} />\n'
                '      <Route path="/preferences" element={<PreferencesMatrixPage />} />\n'
                "    </Routes>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )

            snap = run_scan(root)
            fact_codes = {f["code"] for f in snap["facts"]}
            self.assertIn("UNWIRED_ACTION_PROP", fact_codes)
            self.assertIn("DEAD_ACTION_CONTROL", fact_codes)
            self.assertIn("HARDCODED_UI_DATASET", fact_codes)
            self.assertIn("UI_WITHOUT_BACKEND", fact_codes)

            for fact in snap["facts"]:
                self.assertIn(fact["fact_type"], {"structural", "behavioral"})
                if fact["fact_type"] == "behavioral":
                    self.assertNotEqual(fact["status"], "CONFIRMED")

    def test_04_analyzer_error_isolation_and_three_run_determinism(self) -> None:
        from fa_engine.analyzers.base import AnalyzerContext, AnalyzerResult
        from fa_scan import run_scan

        class CrashingAnalyzer:
            name = "synthetic_crasher"
            version = "1.0.0"

            def applies(self, profile):
                return True, "always"

            def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
                raise RuntimeError("boom inside custom analyzer")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "Main.tsx").write_text(
                "export const Main = () => <div>Coming Soon</div>;\n",
                encoding="utf-8",
            )
            isolated = run_scan(root, extra_analyzers=[CrashingAnalyzer()])
            failed_names = [f["analyzer"] for f in isolated["analysis_coverage"]["failed"]]
            self.assertIn("synthetic_crasher", failed_names)
            self.assertEqual(isolated["v1_projection"]["summary"]["stub_pages"], 1)

            hashes = []
            fact_dumps = []
            for _ in range(3):
                s = run_scan(root)
                hashes.append(s["input_hash"])
                fact_dumps.append(json.dumps(s["facts"], sort_keys=True))
            self.assertEqual(len(set(hashes)), 1)
            self.assertEqual(len(set(fact_dumps)), 1)

            # CLI check
            proc = subprocess.run(
                [sys.executable, str(FA_SCAN_CLI), "--root", str(root), "--format", "json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            cli_payload = json.loads(proc.stdout)
            self.assertEqual(cli_payload["schema_version"], "feature-architect/snapshot@2")
            self.assertEqual(cli_payload["input_hash"], hashes[0])


if __name__ == "__main__":
    unittest.main()
