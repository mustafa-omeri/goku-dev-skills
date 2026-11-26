#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Çift Modlu Etki-Odaklı API & Ekran Smoke Test Orkestratörü (smoke_runner.py).

Seçenek A (Hibrit):
  - Statik kontrat & KG boru hattı denetimi (`BROKEN_DATA_PIPELINE`, `DTO_CONTRACT_MISMATCH`, `API_VERSION_SKEW`)
  - Etkilenen modüllerin hedefli birim/entegrasyon testleri
  - Sunucu açıksa canlı HTTP/UI probe

Seçenek B (Canlı E2E + TestSprite Kota Fallback):
  - TestSprite kredisi/durumu (`ok` | `exhausted` | `paused` | `skip`) denetlenir;
    kredi/limit sorunu varsa veya yerel canlı mod seçildiyse otomatik olarak
    yerel HTTP API Probe + Headless Browser (Playwright / Chrome DevTools MCP) çalıştırılır.
  - İstenirse `--start-cmd` ile sunucu geçici başlatılıp test sonrası temiz kapatılır.
"""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import impact_mapper  # noqa: E402

MUSGOKU_SCRIPTS = THIS_DIR.parents[1] / "musgoku" / "scripts"
TEST_SPEC_SCRIPTS = THIS_DIR.parents[1] / "test-spec-generator" / "scripts"


def _is_port_open(host: str, port: int, timeout: float = 0.08) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _detect_live_urls(
    discovered_ports: list[int],
    explicit_api: str | None,
    explicit_ui: str | None,
    *,
    probe_defaults: bool = True,
) -> tuple[str | None, str | None]:
    api_url = explicit_api.rstrip("/") if explicit_api else None
    ui_url = explicit_ui.rstrip("/") if explicit_ui else None
    if (api_url and ui_url) or not probe_defaults:
        return api_url, ui_url

    open_ports: list[int] = []
    candidates = list(dict.fromkeys(list(discovered_ports) + [8080, 8000, 3001, 5173, 3000, 4173]))
    for p in candidates:
        if _is_port_open("127.0.0.1", int(p)):
            open_ports.append(int(p))

    if not api_url:
        for p in open_ports:
            if p in {8080, 8000, 8081, 3001, 5000}:
                api_url = f"http://127.0.0.1:{p}"
                break
    if not ui_url:
        for p in open_ports:
            if p in {5173, 4173, 3000, 4200}:
                ui_url = f"http://127.0.0.1:{p}"
                break
    return api_url, ui_url


def _probe_http_endpoint(base_url: str, method: str, path: str, timeout: float = 5.0) -> dict[str, Any]:
    """Güvenli HTTP smoke probu (read-only GET veya path parametreli örnek çözümleme)."""
    concrete_path = re_sub_path_params(path)
    url = f"{base_url}{concrete_path}"
    started = time.monotonic()
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            raw = resp.read().decode("utf-8", errors="replace")
            return {
                "method": method,
                "path": path,
                "url": url,
                "status": resp.status,
                "latency_ms": elapsed_ms,
                "body_preview": raw[:200],
                "error": None,
            }
    except urllib.error.HTTPError as err:
        elapsed_ms = round((time.monotonic() - started) * 1000, 1)
        body = ""
        try:
            body = err.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        return {
            "method": method,
            "path": path,
            "url": url,
            "status": err.code,
            "latency_ms": elapsed_ms,
            "body_preview": body,
            "error": f"HTTP {err.code}",
        }
    except Exception as exc:
        elapsed_ms = round((time.monotonic() - started) * 1000, 1)
        return {
            "method": method,
            "path": path,
            "url": url,
            "status": 0,
            "latency_ms": elapsed_ms,
            "body_preview": "",
            "error": str(exc),
        }


def re_sub_path_params(path: str) -> str:
    import re

    out = re.sub(r"\{[^}]+\}", "1", path)
    out = re.sub(r":([A-Za-z_][A-Za-z0-9_]*)", "1", out)
    return out if out.startswith("/") else "/" + out


def _run_targeted_tests(root: Path, test_files: list[str], stacks: dict[str, list[str]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not test_files:
        return results

    py_tests = [f for f in test_files if f.endswith(".py")]
    js_tests = [f for f in test_files if f.endswith((".ts", ".tsx", ".js", ".jsx"))]
    java_tests = [f for f in test_files if f.endswith((".java", ".kt"))]

    if py_tests:
        pytest_exe = shutil.which("pytest")
        cmd = [pytest_exe, "-q", *py_tests] if pytest_exe else [sys.executable, "-m", "unittest", *py_tests]
        proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        results.append({
            "runner": "pytest" if pytest_exe else "unittest",
            "targets": py_tests,
            "exit_code": proc.returncode,
            "summary": (proc.stdout + "\n" + proc.stderr).strip().splitlines()[-1][:200] if (proc.stdout or proc.stderr).strip() else "",
        })

    if js_tests and (root / "package.json").is_file():
        npx_exe = shutil.which("npx")
        if npx_exe:
            pkg_txt = (root / "package.json").read_text(encoding="utf-8", errors="replace")
            runner = "vitest" if "vitest" in pkg_txt else ("jest" if "jest" in pkg_txt else "")
            if runner == "vitest":
                cmd = [npx_exe, "vitest", "run", *js_tests]
            elif runner == "jest":
                cmd = [npx_exe, "jest", "--runInBand", *js_tests]
            else:
                cmd = []
            if cmd:
                proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
                results.append({
                    "runner": runner,
                    "targets": js_tests,
                    "exit_code": proc.returncode,
                    "summary": (proc.stdout + "\n" + proc.stderr).strip().splitlines()[-1][:200] if (proc.stdout or proc.stderr).strip() else "",
                })

    if java_tests and ((root / "pom.xml").is_file() or (root / "mvnw").is_file() or (root / "mvnw.cmd").is_file()):
        mvnw = root / ("mvnw.cmd" if sys.platform.startswith("win") else "mvnw")
        mvn_exe = str(mvnw) if mvnw.is_file() else shutil.which("mvn")
        if mvn_exe:
            classes = ",".join(Path(f).stem for f in java_tests[:10])
            cmd = [mvn_exe, "-B", "test", f"-Dtest={classes}"]
            proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
            results.append({
                "runner": "maven",
                "targets": java_tests,
                "exit_code": proc.returncode,
                "summary": (proc.stdout + "\n" + proc.stderr).strip().splitlines()[-1][:200] if (proc.stdout or proc.stderr).strip() else "",
            })

    return results


def _run_playwright_ui_smoke(ui_url: str, routes: list[str]) -> tuple[list[dict[str, Any]], bool]:
    """Varsa yerel Python Playwright ile headless UI smoke koşar; yoksa (results, False) döner."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        return [], False

    checks: list[dict[str, Any]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            for r in routes:
                concrete_r = re_sub_path_params(r)
                target_url = f"{ui_url}{concrete_r}"
                console_errors: list[str] = []
                page_errors: list[str] = []
                network_failures: list[str] = []

                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                page.on("pageerror", lambda err: page_errors.append(str(err)))
                page.on(
                    "response",
                    lambda resp: network_failures.append(f"{resp.status} {resp.url}") if resp.status >= 500 else None,
                )

                nav_status = 0
                blank_screen = False
                try:
                    resp = page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                    nav_status = resp.status if resp else 0
                    page.wait_for_timeout(400)
                    text_len = page.evaluate("() => (document.body && document.body.innerText || '').trim().length")
                    blank_screen = text_len == 0
                except Exception as exc:
                    page_errors.append(str(exc))

                checks.append({
                    "route": r,
                    "url": target_url,
                    "status": nav_status,
                    "blank_screen": blank_screen,
                    "console_errors": console_errors[:10],
                    "page_errors": page_errors[:10],
                    "network_5xx": network_failures[:10],
                })
        finally:
            browser.close()
    return checks, True


def run_smoke(
    root: Path | str,
    *,
    scope: str = "last",
    mode: str = "auto",
    api_url: str | None = None,
    ui_url: str | None = None,
    start_cmd: str | None = None,
    testsprite_status: str = "skip",
    peers: list[str | Path] | None = None,
    changed_files: list[str] | None = None,
    run_tests: bool = True,
    skip_browser: bool = False,
) -> dict[str, Any]:
    """Etki-odaklı smoke test koşumunu yürütür (Seçenek A + Seçenek B + TestSprite kota fallback)."""
    root_p = Path(root).resolve()
    impact = impact_mapper.map_impact(
        root_p,
        scope=scope,
        peers=peers,
        changed_files=changed_files,
    )

    if impact["doc_only"]:
        return {
            "status": "SKIPPED",
            "effective_mode": mode,
            "testsprite_fallback_triggered": False,
            "findings_count": 0,
            "findings": [],
            "impact": impact,
            "api_probes": [],
            "ui_checks": [],
            "pending_mcp_browser_checks": [],
            "targeted_tests": [],
            "summary": "Yalnızca doküman/meta dosyaları değişti — smoke test kapsam dışı.",
        }

    # TestSprite quota/limit check -> force Option B deterministic local live E2E
    ts_norm = testsprite_status.strip().lower()
    testsprite_fallback = ts_norm in {"exhausted", "paused", "limit", "quota_exceeded", "error"}
    effective_mode = mode
    if mode == "auto":
        if testsprite_fallback or scope == "sprint":
            effective_mode = "live"
        else:
            effective_mode = "hybrid"
    elif testsprite_fallback:
        effective_mode = "live"

    findings: list[dict[str, Any]] = []

    # 1. Option A — Static Contract & Knowledge Graph Pipeline Findings
    for bp in impact["broken_pipelines"]:
        findings.append({
            "code": "BROKEN_DATA_PIPELINE",
            "severity": "CRITICAL",
            "layer": "API-Contract",
            "location": bp.get("location", ""),
            "message": bp.get("summary", "Client HTTP call has no matching backend handler."),
            "remediation_skill": "fix-bug",
        })
    for ci in impact["contract_issues"]:
        findings.append({
            "code": ci.get("code", "DTO_CONTRACT_MISMATCH"),
            "severity": ci.get("severity", "HIGH"),
            "layer": "API-Contract",
            "location": ci.get("location", ""),
            "message": ci.get("summary", "DTO contract mismatch detected."),
            "remediation_skill": "tdd",
        })

    # 2. Option A — Targeted Unit/Integration Tests
    targeted_tests: list[dict[str, Any]] = []
    if run_tests and impact["affected_test_files"]:
        targeted_tests = _run_targeted_tests(root_p, impact["affected_test_files"], impact["stacks"])
        for tr in targeted_tests:
            if tr["exit_code"] != 0:
                findings.append({
                    "code": "TARGETED_TEST_FAIL",
                    "severity": "CRITICAL",
                    "layer": "Tests",
                    "location": ", ".join(tr["targets"][:3]),
                    "message": f"{tr['runner']} failed (exit {tr['exit_code']}): {tr['summary']}",
                    "remediation_skill": "fix-bug",
                })

    # 3. Option B — Live HTTP API & Headless Browser UI Smoke
    booted_proc: subprocess.Popen[Any] | None = None
    need_live_probe = effective_mode == "live" or bool(api_url or ui_url or start_cmd)
    resolved_api, resolved_ui = _detect_live_urls(
        impact["discovered_ports"],
        api_url,
        ui_url,
        probe_defaults=need_live_probe and not (api_url and skip_browser),
    )

    try:
        if start_cmd and not resolved_api and not resolved_ui:
            parts = shlex.split(start_cmd)
            booted_proc = subprocess.Popen(
                parts,
                cwd=str(root_p),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(20):
                time.sleep(0.5)
                resolved_api, resolved_ui = _detect_live_urls(impact["discovered_ports"], api_url, ui_url)
                if resolved_api or resolved_ui:
                    break

        api_probes: list[dict[str, Any]] = []
        if impact["affected_endpoints"]:
            if resolved_api:
                for ep in impact["affected_endpoints"]:
                    if ep["method"] != "GET":
                        # Only probe GET endpoints safely without mutating DB state
                        continue
                    pr = _probe_http_endpoint(resolved_api, ep["method"], ep["path"])
                    api_probes.append(pr)
                    if pr["status"] >= 500 or pr["status"] == 0:
                        findings.append({
                            "code": "API_SMOKE_500",
                            "severity": "CRITICAL",
                            "layer": "Live-API",
                            "location": f"{ep['method']} {ep['path']}",
                            "message": f"Live API smoke failed at {pr['url']} -> status={pr['status']} error={pr['error']}",
                            "remediation_skill": "fix-bug",
                        })
                    elif pr["status"] == 404:
                        findings.append({
                            "code": "API_SMOKE_404",
                            "severity": "HIGH",
                            "layer": "Live-API",
                            "location": f"{ep['method']} {ep['path']}",
                            "message": f"Live endpoint returned 404 Not Found at {pr['url']}",
                            "remediation_skill": "tdd",
                        })
            elif effective_mode == "live":
                findings.append({
                    "code": "RUNTIME_SERVER_UNAVAILABLE",
                    "severity": "HIGH",
                    "layer": "Live-API",
                    "location": "localhost",
                    "message": "Seçenek B (live) smoke modu aktif ancak çalışan API sunucusu veya --api-url bulunamadı.",
                    "remediation_skill": "smoke-test",
                })

        ui_checks: list[dict[str, Any]] = []
        pending_mcp_browser_checks: list[str] = []
        if impact["affected_screens"] and not skip_browser:
            routes = [sc["route"] for sc in impact["affected_screens"]]
            if resolved_ui:
                ui_checks, used_pw = _run_playwright_ui_smoke(resolved_ui, routes)
                if not used_pw:
                    pending_mcp_browser_checks = [f"{resolved_ui}{re_sub_path_params(r)}" for r in routes]
                for uc in ui_checks:
                    if uc["console_errors"] or uc["page_errors"]:
                        findings.append({
                            "code": "UI_CONSOLE_ERROR",
                            "severity": "CRITICAL",
                            "layer": "Live-UI",
                            "location": uc["route"],
                            "message": f"Runtime JS/console error on {uc['url']}: {(uc['page_errors'] + uc['console_errors'])[0]}",
                            "remediation_skill": "fix-bug",
                        })
                    if uc["network_5xx"]:
                        findings.append({
                            "code": "UI_NETWORK_5XX",
                            "severity": "CRITICAL",
                            "layer": "Live-UI",
                            "location": uc["route"],
                            "message": f"Network 5xx observed while rendering {uc['url']}: {uc['network_5xx'][0]}",
                            "remediation_skill": "fix-bug",
                        })
                    if uc["blank_screen"]:
                        findings.append({
                            "code": "UI_BLANK_SCREEN",
                            "severity": "CRITICAL",
                            "layer": "Live-UI",
                            "location": uc["route"],
                            "message": f"Blank screen (empty body text) detected at {uc['url']}",
                            "remediation_skill": "ui-polish",
                        })
            elif effective_mode == "live":
                pending_mcp_browser_checks = [r for r in routes]
    finally:
        if booted_proc is not None:
            booted_proc.terminate()
            try:
                booted_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                booted_proc.kill()

    status = "FAILED" if findings else "PASSED"
    summary = (
        f"mode={effective_mode} · endpoints={len(impact['affected_endpoints'])} · "
        f"screens={len(impact['affected_screens'])} · probes={len(api_probes)} · "
        f"findings={len(findings)}"
        + (" (TestSprite quota fallback -> Option B)" if testsprite_fallback else "")
    )
    return {
        "status": status,
        "effective_mode": effective_mode,
        "testsprite_fallback_triggered": testsprite_fallback,
        "findings_count": len(findings),
        "findings": findings,
        "impact": impact,
        "api_probes": api_probes,
        "ui_checks": ui_checks,
        "pending_mcp_browser_checks": pending_mcp_browser_checks,
        "targeted_tests": targeted_tests,
        "summary": summary,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Impact-Driven API & UI Smoke Test Runner (Option A+B)")
    parser.add_argument("--root", default=".", help="Proje kök dizini")
    parser.add_argument("--scope", choices=["last", "sprint", "all"], default="last")
    parser.add_argument("--mode", choices=["auto", "hybrid", "live"], default="auto")
    parser.add_argument("--api-url", default=None, help="Canlı backend API URL (örn. http://localhost:8080)")
    parser.add_argument("--ui-url", default=None, help="Canlı frontend URL (örn. http://localhost:5173)")
    parser.add_argument("--start-cmd", default=None, help="Sunucu kapalıysa başlatılacak komut")
    parser.add_argument(
        "--testsprite-status",
        choices=["ok", "exhausted", "paused", "skip"],
        default="skip",
        help="TestSprite kota durumu; exhausted/paused durumunda Seçenek B zorunlu koşar",
    )
    parser.add_argument("--peer", action="append", default=[], help="Opsiyonel kardeş repo yolu")
    parser.add_argument("--changed", action="append", default=None, help="Açık değişen dosya listesi")
    parser.add_argument("--no-tests", action="store_true", help="Hedefli unit/integration testlerini atla")
    parser.add_argument("--skip-browser", action="store_true", help="Headless browser UI smoke adımını atla")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    res = run_smoke(
        args.root,
        scope=args.scope,
        mode=args.mode,
        api_url=args.api_url,
        ui_url=args.ui_url,
        start_cmd=args.start_cmd,
        testsprite_status=args.testsprite_status,
        peers=args.peer or None,
        changed_files=args.changed,
        run_tests=not args.no_tests,
        skip_browser=args.skip_browser,
    )

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"[{res['status']}] {res['summary']}")
        for f in res["findings"]:
            print(f"  - [{f['severity']}] {f['code']} ({f['location']}): {f['message']} -> fix: {f['remediation_skill']}")
        if res["pending_mcp_browser_checks"]:
            print(f"  [INFO] Headless browser için chrome-devtools-mcp hedefleri: {res['pending_mcp_browser_checks']}")

    return 1 if res["status"] == "FAILED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
