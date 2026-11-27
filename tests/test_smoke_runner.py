#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etki-Odaklı API & Ekran Smoke Test Orkestratörü (/smoke-test) TDD test paketi."""
from __future__ import annotations

import http.server
import json
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SMOKE_SCRIPTS = ROOT / ".agent" / "skills" / "smoke-test" / "scripts"
sys.path.insert(0, str(SMOKE_SCRIPTS))

import impact_mapper  # noqa: E402
import smoke_runner  # noqa: E402


class _MockApiHandler(http.server.BaseHTTPRequestHandler):
    status_by_path: dict[str, tuple[int, dict]] = {}

    def do_GET(self):  # noqa: N802
        code, payload = self.status_by_path.get(self.path, (404, {"status": "error", "message": "not found"}))
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A003
        return


def _build_temp_fullstack_repo(base: Path) -> Path:
    (base / "src" / "pages").mkdir(parents=True, exist_ok=True)
    (base / "src" / "api").mkdir(parents=True, exist_ok=True)
    (base / "src" / "main" / "java" / "com" / "acme").mkdir(parents=True, exist_ok=True)
    (base / "docs" / "APIs").mkdir(parents=True, exist_ok=True)

    (base / "package.json").write_text(
        json.dumps({"name": "acmeApp", "dependencies": {"react": "^18.2.0", "react-router-dom": "^6.20.0"}}),
        encoding="utf-8",
    )
    (base / "pom.xml").write_text(
        "<project><artifactId>acme</artifactId><dependencies><dependency><artifactId>spring-boot-starter-web</artifactId></dependency></dependencies></project>",
        encoding="utf-8",
    )
    (base / "docs" / "APIs" / "projects.md").write_text(
        "# Projects API\n- `GET /api/v1/projects`\n- `GET /api/v1/health`\n",
        encoding="utf-8",
    )
    (base / "src" / "main" / "java" / "com" / "acme" / "ProjectController.java").write_text(
        """
package com.acme;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class ProjectController {
    @GetMapping("/projects")
    public String listProjects() { return "ok"; }

    @GetMapping("/health")
    public String health() { return "ok"; }
}
""",
        encoding="utf-8",
    )
    (base / "src" / "api" / "projectsApi.ts").write_text(
        """
export async function fetchProjects() {
  return fetch('/api/v1/projects');
}
""",
        encoding="utf-8",
    )
    (base / "src" / "pages" / "ProjectsPage.tsx").write_text(
        """
import { fetchProjects } from '../api/projectsApi';
export function ProjectsPage() {
  fetchProjects();
  return <div>Projects</div>;
}
""",
        encoding="utf-8",
    )
    (base / "src" / "App.tsx").write_text(
        """
import { Routes, Route } from 'react-router-dom';
import { ProjectsPage } from './pages/ProjectsPage';
export function App() {
  return (
    <Routes>
      <Route path="/projects" element={<ProjectsPage />} />
    </Routes>
  );
}
""",
        encoding="utf-8",
    )
    return base


class TestSmokeRunner(unittest.TestCase):
    def test_impact_mapper_traces_changed_endpoint_to_consumer_screen(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _build_temp_fullstack_repo(Path(tmp))
            impact = impact_mapper.map_impact(
                repo,
                scope="all",
                changed_files=["src/main/java/com/acme/ProjectController.java"],
            )
            ep_paths = {ep["path"] for ep in impact["affected_endpoints"]}
            self.assertIn("/api/v1/projects", ep_paths)
            screen_routes = {sc["route"] for sc in impact["affected_screens"]}
            self.assertIn("/projects", screen_routes)
            self.assertEqual(impact["broken_pipelines"], [])
            self.assertEqual(impact_mapper._norm_rel(".agent/skills/x.py"), ".agent/skills/x.py")

    def test_external_https_fetch_is_not_flagged_as_broken_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _build_temp_fullstack_repo(Path(tmp))
            (repo / "src" / "pages" / "ExternalWidget.tsx").write_text(
                "export async function loadExt() { return fetch('https://fakestoreapi.com/products'); }\n",
                encoding="utf-8",
            )
            res = smoke_runner.run_smoke(
                repo,
                scope="last",
                mode="hybrid",
                changed_files=["src/pages/ExternalWidget.tsx"],
                run_tests=False,
            )
            self.assertEqual(res["status"], "PASSED")
            self.assertEqual(res["findings_count"], 0)

    def test_hybrid_mode_skips_doc_only_and_catches_broken_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _build_temp_fullstack_repo(Path(tmp))
            doc_res = smoke_runner.run_smoke(
                repo,
                scope="last",
                mode="hybrid",
                changed_files=["README.md"],
            )
            self.assertEqual(doc_res["status"], "SKIPPED")
            self.assertEqual(doc_res["findings_count"], 0)

            # Break backend handler while client still calls /api/v1/projects
            (repo / "src" / "main" / "java" / "com" / "acme" / "ProjectController.java").write_text(
                "@RestController\n@RequestMapping(\"/api/v1\")\npublic class ProjectController {}\n",
                encoding="utf-8",
            )
            broken_res = smoke_runner.run_smoke(
                repo,
                scope="last",
                mode="hybrid",
                changed_files=["src/main/java/com/acme/ProjectController.java"],
            )
            self.assertEqual(broken_res["status"], "FAILED")
            codes = {f["code"] for f in broken_res["findings"]}
            self.assertIn("BROKEN_DATA_PIPELINE", codes)

    def test_live_mode_catches_api_500_and_passes_after_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _build_temp_fullstack_repo(Path(tmp))
            _MockApiHandler.status_by_path = {
                "/api/v1/projects": (500, {"status": "error", "message": "boom"}),
                "/api/v1/health": (200, {"status": "success", "data": "ok"}),
            }
            with socketserver.TCPServer(("127.0.0.1", 0), _MockApiHandler) as httpd:
                port = httpd.server_address[1]
                t = threading.Thread(target=httpd.serve_forever, daemon=True)
                t.start()
                try:
                    fail_res = smoke_runner.run_smoke(
                        repo,
                        scope="last",
                        mode="live",
                        api_url=f"http://127.0.0.1:{port}",
                        changed_files=["src/main/java/com/acme/ProjectController.java"],
                        skip_browser=True,
                    )
                    self.assertEqual(fail_res["status"], "FAILED")
                    self.assertTrue(any(f["code"] == "API_SMOKE_500" for f in fail_res["findings"]))

                    # Fix the simulated endpoint -> 200 OK
                    _MockApiHandler.status_by_path["/api/v1/projects"] = (
                        200,
                        {"status": "success", "data": []},
                    )
                    pass_res = smoke_runner.run_smoke(
                        repo,
                        scope="last",
                        mode="live",
                        api_url=f"http://127.0.0.1:{port}",
                        changed_files=["src/main/java/com/acme/ProjectController.java"],
                        skip_browser=True,
                    )
                    self.assertEqual(pass_res["status"], "PASSED")
                    self.assertEqual(pass_res["findings_count"], 0)
                finally:
                    httpd.shutdown()

    def test_testsprite_quota_limit_triggers_option_b_live_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _build_temp_fullstack_repo(Path(tmp))
            _MockApiHandler.status_by_path = {
                "/api/v1/projects": (200, {"status": "success", "data": []}),
                "/api/v1/health": (200, {"status": "success", "data": "ok"}),
            }
            with socketserver.TCPServer(("127.0.0.1", 0), _MockApiHandler) as httpd:
                port = httpd.server_address[1]
                t = threading.Thread(target=httpd.serve_forever, daemon=True)
                t.start()
                try:
                    res = smoke_runner.run_smoke(
                        repo,
                        scope="sprint",
                        mode="auto",
                        api_url=f"http://127.0.0.1:{port}",
                        testsprite_status="exhausted",
                        changed_files=["src/main/java/com/acme/ProjectController.java"],
                        skip_browser=True,
                    )
                    self.assertTrue(res["testsprite_fallback_triggered"])
                    self.assertEqual(res["effective_mode"], "live")
                    self.assertEqual(res["status"], "PASSED")
                finally:
                    httpd.shutdown()

    def test_sprint_auditor_smoke_flag_includes_smoke_findings(self):
        auditor_dir = ROOT / ".agent" / "skills" / "verify-sprint" / "scripts"
        if str(auditor_dir) not in sys.path:
            sys.path.insert(0, str(auditor_dir))
        import sprint_auditor  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            repo = _build_temp_fullstack_repo(Path(tmp))
            (repo / "docs" / "specs").mkdir(parents=True, exist_ok=True)
            (repo / "docs" / "specs" / "S1-01.feature").write_text(
                "Feature: Projects\n  Scenario: List\n    Given user\n    When open\n    Then list\n",
                encoding="utf-8",
            )
            (repo / "docs" / "KULLANICI_TEST_REHBERI.md").write_text("# Test Rehberi\n", encoding="utf-8")
            (repo / "docs" / "kullanici-rehberi.html").write_text(
                "<div class='app-sidebar'></div><div id='features-container'></div>",
                encoding="utf-8",
            )
            (repo / "SPRINT_PLAN.md").write_text("# Sprint 1\n", encoding="utf-8")
            (repo / "KANBAN.md").write_text(
                "## Yapıldı\n\n### S1-01 · Projects listesi\n| alan | değer |\n|---|---|\n"
                "| durum | Yapıldı |\n| oncelik | P1 |\n| sprint | S1 |\n"
                "| gherkin | docs/specs/S1-01.feature |\n| kapi | python x.py |\n"
                "| test | Tarayıcıda /projects açılır |\n| risk | düşük |\n",
                encoding="utf-8",
            )
            # Break backend controller so smoke detects BROKEN_DATA_PIPELINE
            (repo / "src" / "main" / "java" / "com" / "acme" / "ProjectController.java").write_text(
                "@RestController\n@RequestMapping(\"/api/v1\")\npublic class ProjectController {}\n",
                encoding="utf-8",
            )
            res = sprint_auditor.audit_sprint(repo, run_smoke=True, smoke_mode="hybrid")
            self.assertEqual(res["status"], "FAILED")
            self.assertTrue(any(f.get("card_id") == "SMOKE" for f in res["findings"]))

    def test_playwright_ui_smoke_isolates_listeners_across_routes(self):
        import types

        created_pages = []

        class _FakePage:
            def __init__(self):
                self.listeners = {}

            def on(self, event, fn):
                self.listeners.setdefault(event, []).append(fn)

            def remove_listener(self, event, fn):
                if event in self.listeners and fn in self.listeners[event]:
                    self.listeners[event].remove(fn)

            def goto(self, url, **_kwargs):
                for fn in list(self.listeners.get("console", [])):
                    fn(types.SimpleNamespace(type="error", text=f"err:{url}"))
                return types.SimpleNamespace(status=200)

            def wait_for_timeout(self, _ms):
                return None

            def evaluate(self, _expr):
                return 42

            def close(self):
                return None

        class _FakeBrowser:
            def new_page(self):
                p = _FakePage()
                created_pages.append(p)
                return p

            def close(self):
                return None

        class _FakePlaywrightCtx:
            def __enter__(self):
                return types.SimpleNamespace(
                    chromium=types.SimpleNamespace(launch=lambda **_kw: _FakeBrowser())
                )

            def __exit__(self, *_args):
                return False

        fake_pw_mod = types.ModuleType("playwright")
        fake_sync_mod = types.ModuleType("playwright.sync_api")
        fake_sync_mod.sync_playwright = lambda: _FakePlaywrightCtx()

        old_pw = sys.modules.get("playwright")
        old_sync = sys.modules.get("playwright.sync_api")
        sys.modules["playwright"] = fake_pw_mod
        sys.modules["playwright.sync_api"] = fake_sync_mod
        try:
            checks, used = smoke_runner._run_playwright_ui_smoke(
                "http://127.0.0.1:5173", ["/a", "/b", "/c"]
            )
            self.assertTrue(used)
            self.assertEqual(len(checks), 3)
            for chk in checks:
                self.assertEqual(
                    len(chk["console_errors"]),
                    1,
                    f"Her rota icin tam 1 console_error olmali (listener birikimi yok): {chk}",
                )
        finally:
            if old_pw is not None:
                sys.modules["playwright"] = old_pw
            else:
                sys.modules.pop("playwright", None)
            if old_sync is not None:
                sys.modules["playwright.sync_api"] = old_sync
            else:
                sys.modules.pop("playwright.sync_api", None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
