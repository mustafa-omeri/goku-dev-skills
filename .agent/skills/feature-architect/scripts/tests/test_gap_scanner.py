#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for feature-architect gap_scanner.py at its public seam."""
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
SCANNER_PATH = SCRIPTS_DIR / "gap_scanner.py"
sys.path.insert(0, str(SCRIPTS_DIR))


def _load_scanner():
    import gap_scanner  # noqa: E402
    return gap_scanner


class GapScannerSeamTests(unittest.TestCase):
    """Tests public seam `gap_scanner.scan(root, peers=..., focus=...)` and CLI."""

    def test_01_i18n_nested_stub_resolved_to_component(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "locales").mkdir(parents=True)
            (root / "src" / "locales" / "tr.json").write_text(
                json.dumps({
                    "reportsPage": {
                        "title": "Raporlar",
                        "underDevelopmentDesc": "Bu sayfa geliştirme aşamasındadır."
                    }
                }, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "src" / "pages").mkdir(parents=True)
            (root / "src" / "pages" / "ReportsPage.tsx").write_text(
                "export function ReportsPage() {\n"
                "  const { t } = useTranslation();\n"
                "  return <div><p>{t('reportsPage.underDevelopmentDesc')}</p></div>;\n"
                "}\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            stubs = result["stub_pages"]
            self.assertEqual(len(stubs), 1)
            self.assertEqual(stubs[0]["file"], "src/pages/ReportsPage.tsx")
            self.assertEqual(stubs[0]["line"], 3)
            self.assertEqual(stubs[0]["i18n_key"], "reportsPage.underDevelopmentDesc")
            self.assertEqual(stubs[0]["source"], "i18n")

    def test_02_i18n_flat_dotted_key_stub(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "locales").mkdir(parents=True)
            (root / "src" / "locales" / "en.json").write_text(
                json.dumps({
                    "analytics.underDevelopment": "This page is currently under development."
                }),
                encoding="utf-8",
            )
            (root / "src" / "features").mkdir(parents=True)
            (root / "src" / "features" / "AnalyticsView.tsx").write_text(
                "export const AnalyticsView = () => (\n"
                '  <section>{t("analytics.underDevelopment")}</section>\n'
                ");\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            stubs = result["stub_pages"]
            self.assertEqual(len(stubs), 1)
            self.assertEqual(stubs[0]["file"], "src/features/AnalyticsView.tsx")
            self.assertEqual(stubs[0]["i18n_key"], "analytics.underDevelopment")

    def test_03_literal_coming_soon_jsx(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "pages").mkdir(parents=True)
            (root / "src" / "pages" / "BillingPage.tsx").write_text(
                "export default function BillingPage() {\n"
                "  return <div className='p-6'><h1>Billing</h1><p>Coming Soon</p></div>;\n"
                "}\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            files = [s["file"] for s in result["stub_pages"]]
            self.assertIn("src/pages/BillingPage.tsx", files)

    def test_04_spelling_variant_gelistirilme(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "locales").mkdir(parents=True)
            (root / "src" / "locales" / "tr.json").write_text(
                json.dumps({
                    "portal.desc": "Bu sayfa henüz geliştirilme aşamasındadır."
                }, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "src" / "views").mkdir(parents=True)
            (root / "src" / "views" / "PortalView.tsx").write_text(
                "export const PortalView = () => <p>{t('portal.desc')}</p>;\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            files = [s["file"] for s in result["stub_pages"]]
            self.assertIn("src/views/PortalView.tsx", files)

    def test_05_stub_action_toast(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "locales").mkdir(parents=True)
            (root / "src" / "locales" / "en.json").write_text(
                json.dumps({
                    "item.exportComingSoon": "Export feature will be added soon"
                }),
                encoding="utf-8",
            )
            (root / "src" / "features").mkdir(parents=True)
            (root / "src" / "features" / "ItemDetail.tsx").write_text(
                "export function ItemDetail() {\n"
                "  const onExport = () => {\n"
                '    showToast(t("item.exportComingSoon"), "info");\n'
                "  };\n"
                "  return <button onClick={onExport}>Export</button>;\n"
                "}\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            self.assertEqual(len(result["stub_actions"]), 1)
            self.assertEqual(result["stub_actions"][0]["file"], "src/features/ItemDetail.tsx")
            self.assertEqual(result["stub_actions"][0]["line"], 3)
            self.assertEqual(result["stub_pages"], [])

    def test_06_input_placeholder_is_not_stub(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SearchForm.tsx").write_text(
                "export function SearchForm() {\n"
                '  return <input type="text" placeholder="Ara..." className="border" />;\n'
                "}\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            self.assertEqual(result["stub_pages"], [])
            self.assertEqual(result["stub_actions"], [])

    def test_07_broken_nav_link_detected(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir(parents=True)
            (root / "src" / "App.tsx").write_text(
                "export function App() {\n"
                "  return (\n"
                "    <Routes>\n"
                '      <Route path="/dashboard" element={<Dashboard />} />\n'
                '      <Route path="/profile" element={<Profile />} />\n'
                "    </Routes>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )
            (root / "src" / "Sidebar.tsx").write_text(
                "export function Sidebar() {\n"
                "  return (\n"
                "    <nav>\n"
                '      <Link to="/dashboard">Dashboard</Link>\n'
                '      <Link to="/settings/api-keys">API Keys</Link>\n'
                "    </nav>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            broken = [b["link"] for b in result["broken_routes"]]
            self.assertIn("/settings/api-keys", broken)
            self.assertNotIn("/dashboard", broken)

    def test_08_wildcard_parent_with_child_route_resolves(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir(parents=True)
            (root / "src" / "App.tsx").write_text(
                "export function App() {\n"
                "  return (\n"
                "    <Routes>\n"
                '      <Route path="/main/*" element={<MainArea />} />\n'
                "    </Routes>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )
            (root / "src" / "MainArea.tsx").write_text(
                "export function MainArea() {\n"
                "  return (\n"
                "    <Routes>\n"
                '      <Route path="reports" element={<Reports />} />\n'
                "    </Routes>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )
            (root / "src" / "Sidebar.tsx").write_text(
                "export const Sidebar = () => (\n"
                "  <nav>\n"
                '    <Link to="/main/reports">Reports</Link>\n'
                '    <Link to="/unmounted/ghost">Ghost</Link>\n'
                "  </nav>\n"
                ");\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            broken = [b["link"] for b in result["broken_routes"]]
            self.assertNotIn("/main/reports", broken)
            self.assertIn("/unmounted/ghost", broken)

    def test_09_orphan_endpoint_across_peer_repo(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as fe_tmp, tempfile.TemporaryDirectory() as be_tmp:
            fe_root = Path(fe_tmp)
            be_root = Path(be_tmp)

            (fe_root / "src" / "api").mkdir(parents=True)
            (fe_root / "src" / "api" / "dashboardApi.ts").write_text(
                "export const fetchSummary = () => apiClient.get('/admin/dashboard/summary');\n",
                encoding="utf-8",
            )

            java_dir = be_root / "src" / "main" / "java" / "com" / "example"
            java_dir.mkdir(parents=True)
            (java_dir / "AdminController.java").write_text(
                "package com.example;\n"
                "@RestController\n"
                '@RequestMapping("/api/v1/admin")\n'
                "public class AdminController {\n"
                '  @GetMapping("/dashboard/summary")\n'
                "  public Object summary() { return null; }\n"
                '  @GetMapping("/audit-logs")\n'
                "  public Object auditLogs() { return null; }\n"
                "}\n",
                encoding="utf-8",
            )

            result = scanner.scan(fe_root, peers=[be_root])
            orphan_paths = [e["path"] for e in result["orphan_endpoints"]]
            self.assertIn("/api/v1/admin/audit-logs", orphan_paths)
            self.assertNotIn("/api/v1/admin/dashboard/summary", orphan_paths)

    def test_10_orphan_prisma_field_camel_snake(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "prisma").mkdir(parents=True)
            (root / "prisma" / "schema.prisma").write_text(
                "model User {\n"
                "  id String @id\n"
                "  email String\n"
                "  lastLoginIp String?\n"
                "  notificationPreferences Json?\n"
                "}\n",
                encoding="utf-8",
            )
            (root / "src" / "pages").mkdir(parents=True)
            (root / "src" / "pages" / "ProfilePage.tsx").write_text(
                "export function ProfilePage({ user }: any) {\n"
                "  return <div>{user.email}</div>;\n"
                "}\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            orphan_fields = {(f["entity"], f["field"]) for f in result["orphan_fields"]}
            self.assertIn(("User", "lastLoginIp"), orphan_fields)
            self.assertIn(("User", "notificationPreferences"), orphan_fields)
            self.assertNotIn(("User", "email"), orphan_fields)

    def test_11_roles_detected_from_enum(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "types").mkdir(parents=True)
            (root / "src" / "types" / "auth.ts").write_text(
                "export enum UserRole {\n"
                "  SUPER_ADMIN = 'SUPER_ADMIN',\n"
                "  MANAGER = 'MANAGER',\n"
                "  VIEWER = 'VIEWER',\n"
                "}\n",
                encoding="utf-8",
            )
            result = scanner.scan(root)
            role_names = {r["name"] for r in result["roles"]}
            self.assertTrue({"SUPER_ADMIN", "MANAGER", "VIEWER"}.issubset(role_names))

    def test_12_core_modules_inventory(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (
                "src/features/dashboard/MainDashboard.tsx",
                "src/features/profile/UserProfile.tsx",
                "src/features/settings/AccountSettings.tsx",
            ):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("export default function View() { return <div />; }\n", encoding="utf-8")
            result = scanner.scan(root)
            cm = result["core_modules"]
            self.assertIn("src/features/dashboard/MainDashboard.tsx", cm["dashboard"])
            self.assertIn("src/features/profile/UserProfile.tsx", cm["profile"])
            self.assertIn("src/features/settings/AccountSettings.tsx", cm["settings"])

    def test_13_ignores_vendor_dirs(self):
        scanner = _load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for ignored in ("node_modules/pkg", ".agent/skills/x", "dist", "build", "target"):
                d = root / ignored
                d.mkdir(parents=True, exist_ok=True)
                (d / "Stub.tsx").write_text("export const S = () => <p>Coming Soon</p>;\n", encoding="utf-8")
            (root / "src").mkdir(parents=True)
            (root / "src" / "Clean.tsx").write_text("export const C = () => <p>Active</p>;\n", encoding="utf-8")
            result = scanner.scan(root)
            self.assertEqual(result["stub_pages"], [])

    def test_14_cli_json_contract_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "Page.tsx").write_text(
                "export const Page = () => <div>Bu sayfa geliştirme aşamasındadır.</div>;\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, str(SCANNER_PATH), "--root", str(root), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["schema"], "feature-architect/gap-scan@1")
            self.assertEqual(payload["summary"]["stub_pages"], 1)

            bad = subprocess.run(
                [sys.executable, str(SCANNER_PATH), "--root", str(root / "nonexistent_dir_xyz")],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
