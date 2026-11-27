#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Artımlı Test Takip, PASS Referans Defteri, Cerrahi Yama ve Delta Export Motoru (test_spec_tracker.py).

v2 özellikleri:
1. Fast-path SHA-256 kontrolü + çift-katmanlı `raw_hash` / `contract_hash` ile Major vs Minor ayrımı.
2. `docs/testing/test-spec-state.json` üzerinde senaryo yaşam döngüsü (`NEW`, `PASS`, `STALE`, `FAIL`, `FLAKY`, `DEPRECATED`).
3. Çoklu rapor adaptörleri (TestSprite, JUnit XML, Playwright JSON, Cucumber JSON) ve CLI `record`.
4. `<!-- TEST-SPEC:MODULE:<mod>:BEGIN/END -->` çapalarıyla cerrahi modül yaması (`patch-module`).
5. Hedefli delta dışa aktarımı (`export-delta` -> yalnız `NEW + STALE + FAIL + FLAKY`, opsiyonel `--include-smoke`).
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
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

import test_spec_scanner as scanner  # noqa: E402

STATE_SCHEMA_VERSION = "test-spec-state@1"
SCENARIO_ID_RE = re.compile(r"\b(SC-([A-Z0-9]+)-(\d+))\b")
TC_ID_RE = re.compile(r"\b(TC\d{2,4})\b", re.IGNORECASE)
AC_ID_RE = re.compile(r"\bAC-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
TAG_RE = re.compile(r"@[A-Za-z0-9_-]+")


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_short_sha(root: Path) -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "workspace"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _extract_surfaces_from_inventory(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    surfaces: dict[str, dict[str, Any]] = {}
    for rd in inventory.get("route_details", []):
        rpath = rd["path"]
        key = f"route:{rpath}"
        surfaces[key] = {
            "kind": "route",
            "module": rd.get("module") or scanner._module_key(rpath),
            "file": rd.get("file", ""),
            "risk_tier": rd.get("risk_tier", "P2"),
            "raw_hash": rd.get("raw_hash", ""),
            "contract_hash": rd.get("contract_hash", ""),
        }
    for ep in inventory.get("endpoints", []):
        method = str(ep.get("method", "GET")).upper()
        path = ep["path"]
        key = f"endpoint:{method}:{path}"
        surfaces[key] = {
            "kind": "endpoint",
            "module": ep.get("module") or scanner._module_key(path),
            "file": ep.get("file", ""),
            "allowed_roles": list(ep.get("allowed_roles") or []),
            "risk_tier": ep.get("risk_tier", "P2"),
            "raw_hash": ep.get("raw_hash", ""),
            "contract_hash": ep.get("contract_hash", ""),
        }
    return surfaces


def _parse_spec_scenarios(spec_text: str) -> list[dict[str, Any]]:
    """Spec dosyasındaki tüm modül çapalarından ve Gherkin bloklarından SC-* senaryolarını çıkarır."""
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    module_spans: list[tuple[str, int, int]] = []
    for m in re.finditer(
        r"<!--\s*TEST-SPEC:MODULE:([A-Za-z0-9_-]+):BEGIN\s*-->(.*?)<!--\s*TEST-SPEC:MODULE:\1:END\s*-->",
        spec_text,
        re.DOTALL | re.IGNORECASE,
    ):
        module_spans.append((m.group(1).lower(), m.start(), m.end()))

    def _module_for_offset(pos: int, fallback_text: str) -> str:
        for mod_name, s, e in module_spans:
            if s <= pos <= e:
                return mod_name
        # Fallback: extract from Feature: line or route/endpoint inside block
        ep_m = re.search(r"/[a-zA-Z0-9_/-]+", fallback_text)
        return scanner._module_key(ep_m.group(0)) if ep_m else "general"

    for fence_m in scanner.GHERKIN_FENCE_RE.finditer(spec_text):
        blk = fence_m.group(1)
        mod_guess = _module_for_offset(fence_m.start(), blk)
        lines = blk.splitlines()
        pending_tags: list[str] = []
        current: dict[str, Any] | None = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("@"):
                if current is not None:
                    results.append(current)
                    current = None
                pending_tags.extend(TAG_RE.findall(stripped))
            elif re.match(r"^Scenario(?: Outline)?\s*:", stripped, re.IGNORECASE):
                if current is not None:
                    results.append(current)
                idm = SCENARIO_ID_RE.search(stripped)
                sc_id = idm.group(1) if idm else ""
                current = {
                    "id": sc_id,
                    "title": stripped,
                    "module": mod_guess,
                    "tags": sorted(set(pending_tags)),
                    "body_lines": [line],
                }
                pending_tags = []
            elif current is not None:
                current["body_lines"].append(line)

        if current is not None:
            results.append(current)

    final: list[dict[str, Any]] = []
    for item in results:
        sid = item["id"]
        if not sid or sid in seen:
            continue
        seen.add(sid)
        body = "\n".join(item["body_lines"])
        ac_ids = sorted(set(AC_ID_RE.findall(body)))
        final.append(
            {
                "id": sid,
                "title": item["title"],
                "module": item["module"],
                "tags": item["tags"],
                "ac_ids": ac_ids,
                "body": body,
            }
        )
    return final


def _compute_scenario_contract_hash(
    sc_item: dict[str, Any],
    surfaces: dict[str, dict[str, Any]],
) -> tuple[str, list[str]]:
    body = sc_item["body"]
    mod = sc_item["module"]
    bound: list[str] = []

    for skey in sorted(surfaces):
        if skey.startswith("endpoint:"):
            _, method, path = skey.split(":", 2)
            if f"{method} {path}" in body or path in body:
                bound.append(skey)
        elif skey.startswith("route:"):
            path = skey.split(":", 1)[1]
            if path in body:
                bound.append(skey)

    if not bound:
        bound = sorted(k for k, v in surfaces.items() if v.get("module") == mod)

    payload = {
        "module": mod,
        "surfaces": {k: surfaces[k].get("contract_hash", "") for k in sorted(bound) if k in surfaces},
    }
    chash = scanner.sha256_text(json.dumps(payload, sort_keys=True))
    return chash, bound


def sync_state_from_spec(
    spec_path: Path | str,
    state_path: Path | str,
    inventory: dict[str, Any],
) -> dict[str, Any]:
    """Spec dosyasını ve envanteri okuyarak `test-spec-state.json` defterini senkronlar."""
    spec_p = Path(spec_path).resolve()
    state_p = Path(state_path).resolve()
    root_p = Path(inventory.get("root") or spec_p.parent).resolve()

    prev_state: dict[str, Any] = _read_json(state_p) if state_p.is_file() else {}
    prev_scenarios: dict[str, Any] = prev_state.get("scenarios", {})
    prev_next_seq: dict[str, int] = dict(prev_state.get("next_seq", {}))

    surfaces = _extract_surfaces_from_inventory(inventory)
    parsed_scenarios = _parse_spec_scenarios(spec_p.read_text(encoding="utf-8"))

    new_scenarios: dict[str, Any] = {}
    for sc in parsed_scenarios:
        sid = sc["id"]
        chash, bound = _compute_scenario_contract_hash(sc, surfaces)
        for skey in bound:
            if skey in surfaces:
                surfaces[skey].setdefault("scenario_ids", []).append(sid)

        idm = SCENARIO_ID_RE.search(sid)
        if idm:
            prefix, num = idm.group(2), int(idm.group(3))
            prev_next_seq[prefix] = max(prev_next_seq.get(prefix, 1), num + 1)

        prev_entry = prev_scenarios.get(sid, {})
        prev_status = prev_entry.get("status", "NEW")
        pass_ref = prev_entry.get("pass_ref")
        last_pass_ref = prev_entry.get("last_pass_ref")
        history = list(prev_entry.get("history", []))
        rev = int(prev_entry.get("spec_revision", 1))

        if prev_status == "PASS" and pass_ref:
            if pass_ref.get("verified_contract_hash") == chash:
                status = "PASS"
            else:
                status = "STALE"
                last_pass_ref = pass_ref
                pass_ref = None
                rev += 1
                history.append({"at": _utc_now(), "status": "STALE", "reason": "contract_hash_changed"})
        elif prev_entry and prev_entry.get("contract_hash") != chash and prev_status in {"NEW", "FAIL", "FLAKY"}:
            rev += 1
            status = prev_status
        else:
            status = prev_status if prev_entry else "NEW"

        entry: dict[str, Any] = {
            "module": sc["module"],
            "ac_ids": sc["ac_ids"],
            "bound_surfaces": bound,
            "tags": sc["tags"],
            "spec_revision": rev,
            "contract_hash": chash,
            "status": status,
            "history": history[-20:],
        }
        if pass_ref:
            entry["pass_ref"] = pass_ref
        if last_pass_ref:
            entry["last_pass_ref"] = last_pass_ref
        new_scenarios[sid] = entry

    try:
        spec_rel = spec_p.relative_to(root_p).as_posix()
    except ValueError:
        spec_rel = spec_p.as_posix()

    state = {
        "schema_version": STATE_SCHEMA_VERSION,
        "project_name": inventory.get("project_name", root_p.name),
        "spec_file": spec_rel,
        "last_scan_at": _utc_now(),
        "last_scan_commit": _git_short_sha(root_p),
        "next_seq": dict(sorted(prev_next_seq.items())),
        "file_hashes": inventory.get("file_hashes", {}),
        "surfaces": surfaces,
        "scenarios": new_scenarios,
    }
    _write_json(state_p, state)
    return state


def plan_incremental_update(
    project_root: Path | str,
    state_path: Path | str,
    *,
    peers: list[Path | str] | None = None,
    focus: list[str] | None = None,
    force_modules: list[str] | None = None,
) -> dict[str, Any]:
    """Kod & doküman değişikliklerini UNCHANGED / MINOR / MAJOR olarak sınıflandırır ve STALE geçişini yapar."""
    root = Path(project_root).resolve()
    state_p = Path(state_path).resolve()
    forced = {m.strip().lower() for m in (force_modules or []) if m.strip()}

    if not state_p.is_file():
        inv = scanner.build_test_inventory(root, peers=peers, focus=focus)
        mod_plan = {
            mod: {
                "classification": "MAJOR",
                "action": "ADD",
                "reasons": ["İlk kurulum (BOOTSTRAP)"],
                "affected_surfaces": data.get("routes", []) + data.get("endpoints", []),
                "stale_scenarios": [],
            }
            for mod, data in inv.get("modules", {}).items()
        }
        return {
            "mode": "BOOTSTRAP",
            "has_changes": bool(mod_plan),
            "modules": mod_plan,
            "stale_scenarios": [],
            "inventory": inv,
        }

    state = _read_json(state_p)
    prev_file_hashes: dict[str, dict[str, str]] = state.get("file_hashes", {})

    # Fast-path: tracked file'ların hiçbiri değişmediyse ve forced module yoksa NO_OP
    if prev_file_hashes and not forced and not focus:
        all_match = True
        for rel_f, hashes in prev_file_hashes.items():
            cand = root / rel_f
            if not cand.is_file() or scanner.sha256_file(cand) != hashes.get("raw_hash"):
                all_match = False
                break
        if all_match:
            return {
                "mode": "NO_OP",
                "has_changes": False,
                "modules": {
                    m: {
                        "classification": "UNCHANGED",
                        "action": "SKIP",
                        "reasons": ["Fast-path SHA-256 eşleşti"],
                        "affected_surfaces": [],
                        "stale_scenarios": [],
                    }
                    for m in sorted({v.get("module", "general") for v in state.get("surfaces", {}).values()})
                },
                "stale_scenarios": [],
            }

    inv = scanner.build_test_inventory(root, peers=peers, focus=focus)
    new_surfaces = _extract_surfaces_from_inventory(inv)
    old_surfaces: dict[str, Any] = state.get("surfaces", {})
    new_file_hashes = inv.get("file_hashes", {})
    kg_impact_map = inv.get("kg_impact_map", {})

    # Hangi dosyaların contract_hash'i değişti?
    contract_changed_files = {
        rel for rel, fh in new_file_hashes.items() if prev_file_hashes.get(rel, {}).get("contract_hash") != fh.get("contract_hash")
    }
    impacted_by_kg: set[str] = set()
    for rel in contract_changed_files:
        impacted_by_kg.update(kg_impact_map.get(rel, []))

    raw_changed_files = {
        rel for rel, fh in new_file_hashes.items() if prev_file_hashes.get(rel, {}).get("raw_hash") != fh.get("raw_hash")
    }

    mod_plan: dict[str, dict[str, Any]] = {}

    def _ensure_mod(mod: str) -> dict[str, Any]:
        return mod_plan.setdefault(
            mod,
            {
                "classification": "UNCHANGED",
                "action": "SKIP",
                "reasons": [],
                "affected_surfaces": [],
                "stale_scenarios": [],
            },
        )

    def _elevate(mod: str, cls_name: str, action: str, reason: str, surface_key: str) -> None:
        order = {"UNCHANGED": 0, "MINOR": 1, "MAJOR": 2}
        entry = _ensure_mod(mod)
        if order[cls_name] > order[entry["classification"]]:
            entry["classification"] = cls_name
            entry["action"] = action
        if reason not in entry["reasons"]:
            entry["reasons"].append(reason)
        if surface_key and surface_key not in entry["affected_surfaces"]:
            entry["affected_surfaces"].append(surface_key)

    major_surface_keys: set[str] = set()
    deprecated_surface_keys: set[str] = set()

    for skey, sdata in new_surfaces.items():
        mod = sdata["module"]
        if mod in forced:
            _elevate(mod, "MAJOR", "UPDATE", f"--force-module {mod}", skey)
            major_surface_keys.add(skey)
            continue
        if skey not in old_surfaces:
            _elevate(mod, "MAJOR", "ADD", f"Yeni yüzey eklendi: {skey}", skey)
            major_surface_keys.add(skey)
            continue
        old_s = old_surfaces[skey]
        if old_s.get("contract_hash") != sdata.get("contract_hash") or skey in impacted_by_kg:
            _elevate(mod, "MAJOR", "UPDATE", f"Kontrat/etki değişimi: {skey}", skey)
            major_surface_keys.add(skey)
            continue
        if sdata.get("file") in raw_changed_files or old_s.get("raw_hash") != sdata.get("raw_hash"):
            _elevate(mod, "MINOR", "KEEP", f"Kozmetik/yorum değişikliği ({sdata.get('file')})", skey)
        else:
            _ensure_mod(mod)

    for skey, old_s in old_surfaces.items():
        if skey not in new_surfaces:
            mod = old_s.get("module", "general")
            _elevate(mod, "MAJOR", "DEPRECATE", f"Kaldırılan yüzey: {skey}", skey)
            deprecated_surface_keys.add(skey)

    # Etkilenen senaryoları defterde STALE / DEPRECATED durumuna çek
    scenarios = state.get("scenarios", {})
    stale_ids: list[str] = []
    state_dirty = False
    for sid, sc in scenarios.items():
        bound = set(sc.get("bound_surfaces", []))
        if bound & deprecated_surface_keys and not (bound - deprecated_surface_keys):
            if sc.get("status") != "DEPRECATED":
                sc["status"] = "DEPRECATED"
                sc.setdefault("history", []).append({"at": _utc_now(), "status": "DEPRECATED"})
                state_dirty = True
            continue
        if bound & major_surface_keys:
            if sc.get("status") == "PASS":
                sc["last_pass_ref"] = sc.pop("pass_ref", sc.get("last_pass_ref"))
                sc["status"] = "STALE"
                sc["spec_revision"] = int(sc.get("spec_revision", 1)) + 1
                sc.setdefault("history", []).append({"at": _utc_now(), "status": "STALE", "reason": "major_surface_change"})
                state_dirty = True
                stale_ids.append(sid)
                _ensure_mod(sc.get("module", "general"))["stale_scenarios"].append(sid)

    if state_dirty:
        state["last_scan_at"] = _utc_now()
        state["last_scan_commit"] = _git_short_sha(root)
        _write_json(state_p, state)

    has_changes = any(m["classification"] in {"MINOR", "MAJOR"} for m in mod_plan.values())
    return {
        "mode": "INCREMENTAL",
        "has_changes": has_changes,
        "modules": dict(sorted(mod_plan.items())),
        "stale_scenarios": sorted(stale_ids),
        "next_seq": state.get("next_seq", {}),
        "inventory": inv,
    }


def patch_module_section(
    spec_path: Path | str,
    module_name: str,
    new_module_markdown: str,
    *,
    matrix_row: str | None = None,
) -> dict[str, Any]:
    """ACCEPTANCE_TEST_SPEC.md içindeki yalnız hedef modül bloğunu cerrahi olarak günceller."""
    spec_p = Path(spec_path).resolve()
    if not spec_p.is_file():
        raise FileNotFoundError(f"Spec dosyası bulunamadı: {spec_p}")

    text = spec_p.read_text(encoding="utf-8")
    mod = module_name.strip().lower()
    begin_tag = f"<!-- TEST-SPEC:MODULE:{mod}:BEGIN -->"
    end_tag = f"<!-- TEST-SPEC:MODULE:{mod}:END -->"
    wrapped = f"{begin_tag}\n{new_module_markdown.strip()}\n{end_tag}"

    pattern = re.compile(
        rf"<!--\s*TEST-SPEC:MODULE:{re.escape(mod)}:BEGIN\s*-->.*?<!--\s*TEST-SPEC:MODULE:{re.escape(mod)}:END\s*-->",
        re.DOTALL | re.IGNORECASE,
    )
    if pattern.search(text):
        updated = pattern.sub(lambda _m: wrapped, text, count=1)
        action = "REPLACED"
    else:
        sec3 = re.search(r"^##\s+3\b", text, re.MULTILINE)
        if sec3:
            idx = sec3.start()
            updated = text[:idx].rstrip() + "\n\n" + wrapped + "\n\n" + text[idx:]
        else:
            updated = text.rstrip() + "\n\n" + wrapped + "\n"
        action = "INSERTED"

    if matrix_row:
        sec2 = re.search(r"^##\s+2\b", updated, re.MULTILINE)
        sec1 = re.search(r"^##\s+1\b", updated, re.MULTILINE)
        if sec1 and sec2:
            head = updated[: sec1.end()]
            mid = updated[sec1.end() : sec2.start()]
            tail = updated[sec2.start() :]
            mid_lines = mid.splitlines()
            replaced_row = False
            row_key = matrix_row.split("|")[1].strip() if "|" in matrix_row else mod
            for i, ln in enumerate(mid_lines):
                if ln.strip().startswith("|") and re.search(rf"\|\s*{re.escape(row_key)}\s*\|", ln, re.IGNORECASE):
                    mid_lines[i] = matrix_row.strip()
                    replaced_row = True
                    break
            if not replaced_row:
                last_tbl = max((i for i, ln in enumerate(mid_lines) if ln.strip().startswith("|")), default=-1)
                if last_tbl != -1:
                    mid_lines.insert(last_tbl + 1, matrix_row.strip())
            updated = head + "\n".join(mid_lines) + "\n" + tail

    spec_p.write_text(updated, encoding="utf-8")
    return {"module": mod, "action": action, "spec_path": spec_p.as_posix()}


def _is_flaky_history(history: list[dict[str, Any]]) -> bool:
    outcomes = [h.get("status") for h in history[-4:] if h.get("status") in {"PASS", "FAIL"}]
    if len(outcomes) < 3:
        return False
    flips = sum(1 for a, b in zip(outcomes, outcomes[1:]) if a != b)
    return flips >= 2


def record_execution_results(
    state_path: Path | str,
    results: dict[str, str],
    *,
    runner: str = "manual",
    commit: str | None = None,
    run_id: str | None = None,
    evidence_ref: str | None = None,
) -> dict[str, Any]:
    """Senaryo koşum sonuçlarını (PASS/FAIL) state defterine yazar ve FLAKY salınımı tespit eder."""
    state_p = Path(state_path).resolve()
    if not state_p.is_file():
        raise FileNotFoundError(f"State defteri bulunamadı: {state_p}")

    state = _read_json(state_p)
    scenarios = state.get("scenarios", {})
    resolved_commit = commit or _git_short_sha(state_p.parent)
    now = _utc_now()
    rid = run_id or f"{runner}-{now.replace(':', '').replace('-', '')}"
    updated_ids: list[str] = []

    for sc_id, raw_outcome in results.items():
        outcome = raw_outcome.strip().upper()
        if outcome not in {"PASS", "FAIL"} or sc_id not in scenarios:
            continue
        sc = scenarios[sc_id]
        hist = sc.setdefault("history", [])
        hist.append({"at": now, "status": outcome, "runner": runner, "commit": resolved_commit})
        sc["history"] = hist[-20:]

        if _is_flaky_history(sc["history"]):
            sc["status"] = "FLAKY"
        else:
            sc["status"] = outcome

        if outcome == "PASS":
            sc["pass_ref"] = {
                "runner": runner,
                "run_id": rid,
                "verified_at": now,
                "verified_commit": resolved_commit,
                "verified_contract_hash": sc.get("contract_hash", ""),
                "evidence_ref": evidence_ref or "",
            }
        updated_ids.append(sc_id)

    _write_json(state_p, state)
    return {"updated_count": len(updated_ids), "updated_ids": updated_ids, "state_path": state_p.as_posix()}


def parse_junit_xml(xml_path: Path | str) -> dict[str, str]:
    """JUnit XML çıktısından SC-XXX -> PASS/FAIL eşleşmelerini çıkarır."""
    tree = ET.parse(Path(xml_path))
    root = tree.getroot()
    out: dict[str, str] = {}
    for tc in root.iter("testcase"):
        name = (tc.attrib.get("name") or "") + " " + (tc.attrib.get("classname") or "")
        m = SCENARIO_ID_RE.search(name)
        if not m:
            continue
        if tc.find("skipped") is not None:
            continue
        failed = tc.find("failure") is not None or tc.find("error") is not None
        out[m.group(1)] = "FAIL" if failed else "PASS"
    return out


def parse_playwright_json(json_path: Path | str) -> dict[str, str]:
    """Playwright JSON raporundan SC-XXX -> PASS/FAIL eşleşmelerini çıkarır."""
    data = _read_json(Path(json_path))
    out: dict[str, str] = {}

    def _walk_suite(suite: dict[str, Any]) -> None:
        for spec in suite.get("specs", []):
            title = spec.get("title", "")
            m = SCENARIO_ID_RE.search(title)
            if m:
                ok = spec.get("ok")
                if ok is None:
                    tests = spec.get("tests", [])
                    ok = all(t.get("status") in {"expected", "passed"} for t in tests) if tests else False
                out[m.group(1)] = "PASS" if ok else "FAIL"
        for sub in suite.get("suites", []):
            _walk_suite(sub)

    for s in data.get("suites", []):
        _walk_suite(s)
    return out


def parse_cucumber_json(json_path: Path | str) -> dict[str, str]:
    """Cucumber JSON raporundan SC-XXX -> PASS/FAIL eşleşmelerini çıkarır."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    if not isinstance(data, list):
        return out
    for feat in data:
        for el in feat.get("elements", []):
            m = SCENARIO_ID_RE.search(el.get("name", ""))
            if not m:
                continue
            steps = el.get("steps", [])
            statuses = [s.get("result", {}).get("status", "") for s in steps]
            if not statuses:
                continue
            out[m.group(1)] = "PASS" if all(st == "passed" for st in statuses) else "FAIL"
    return out


def _load_tc_to_sc_map(report_path: Path, sc_map_path: Path | str | None = None) -> dict[str, str]:
    """sc_map.json üzerinden TC### -> SC-* eşleme haritasını yükler."""
    candidates: list[Path] = []
    if sc_map_path:
        candidates.append(Path(sc_map_path))
    else:
        candidates.append(report_path.parent / "sc_map.json")
        candidates.append(report_path.parent.parent / "sc_map.json")
    for cand in candidates:
        if cand.is_file():
            try:
                data = _read_json(cand)
                raw = data.get("tc_to_sc", data if isinstance(data, dict) else {})
                return {str(k).upper(): str(v) for k, v in raw.items() if str(v).startswith("SC-")}
            except Exception:
                continue
    return {}


def _resolve_sc_id_from_text(text: str, tc_to_sc: dict[str, str]) -> str | None:
    sm = SCENARIO_ID_RE.search(text)
    if sm:
        return sm.group(1)
    tm = TC_ID_RE.search(text)
    if tm:
        return tc_to_sc.get(tm.group(1).upper())
    return None


def _split_testsprite_md_blocks(text: str) -> list[str]:
    """Markdown TestSprite raporunu test başlıklarına / ayraçlara göre bloklara böler."""
    lines = text.splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []
    for ln in lines:
        s = ln.strip()
        if re.match(r"^#{3,4}\s+.*(?:Test\s+TC\d+|SC-[A-Z0-9]+-\d+)", s, re.IGNORECASE):
            if current:
                blocks.append(current)
            current = [ln]
        elif s == "---" and current:
            blocks.append(current)
            current = []
        else:
            current.append(ln)
    if current:
        blocks.append(current)
    return ["\n".join(b) for b in blocks if "\n".join(b).strip()]


def parse_testsprite_report(
    report_path: Path | str,
    *,
    sc_map_path: Path | str | None = None,
) -> dict[str, str]:
    """TestSprite Markdown (`raw_report.md` / `report.md`) veya JSON (`test_results.json`) çıktısından SC-XXX -> PASS/FAIL çıkarır."""
    p = Path(report_path)
    tc_to_sc = _load_tc_to_sc_map(p, sc_map_path=sc_map_path)
    text = p.read_text(encoding="utf-8", errors="replace")
    out: dict[str, str] = {}

    stripped = text.lstrip()
    if p.suffix.lower() == ".json" or stripped.startswith("["):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                sid = _resolve_sc_id_from_text(str(item.get("title", "")), tc_to_sc)
                if not sid:
                    continue
                st = str(item.get("testStatus", "")).strip().upper()
                if st in {"FAILED", "FAIL", "ERROR"}:
                    out[sid] = "FAIL"
                elif st in {"PASSED", "PASS", "SUCCESS"}:
                    out[sid] = "PASS"
            return out

    fail_re = re.compile(r"\b(?:FAIL|FAILED|ERROR)\b|❌", re.IGNORECASE)
    pass_re = re.compile(r"\b(?:PASS|PASSED|SUCCESS)\b|✅", re.IGNORECASE)
    status_line_re = re.compile(r"^\s*[-*]?\s*\*{0,2}Status\*{0,2}\s*:\s*(.+)$", re.IGNORECASE)

    for block in _split_testsprite_md_blocks(text):
        lines = block.splitlines()
        # Tek bir blokta birden fazla SC/TC ID'si olan düz liste varsa satır bazlı parse'a düş
        line_ids = {
            sid
            for ln in lines
            if (sid := _resolve_sc_id_from_text(ln, tc_to_sc)) is not None
        }
        has_heading = bool(re.match(r"^\s*#{2,4}\s+", lines[0])) if lines else False
        if not has_heading and len(line_ids) > 1:
            for ln in lines:
                sid = _resolve_sc_id_from_text(ln, tc_to_sc)
                if not sid:
                    continue
                if fail_re.search(ln):
                    out[sid] = "FAIL"
                elif pass_re.search(ln):
                    out[sid] = "PASS"
            continue

        sid = _resolve_sc_id_from_text(lines[0] if lines else block, tc_to_sc) or _resolve_sc_id_from_text(block, tc_to_sc)
        if not sid:
            continue

        matched_status: str | None = None
        for ln in lines:
            sm = status_line_re.match(ln)
            if sm:
                val = sm.group(1)
                if fail_re.search(val):
                    matched_status = "FAIL"
                    break
                if pass_re.search(val):
                    matched_status = "PASS"
                    break
        if matched_status is None:
            filtered = "\n".join(
                ln for ln in lines if "AI_ANALYSIS" not in ln and not ln.strip().startswith("- **Test Visualization")
            )
            if fail_re.search(filtered):
                matched_status = "FAIL"
            elif pass_re.search(filtered):
                matched_status = "PASS"
        if matched_status:
            out[sid] = matched_status
    return out


def extract_testsprite_errors(
    report_path: Path | str,
    *,
    sc_map_path: Path | str | None = None,
) -> dict[str, str]:
    """TestSprite JSON veya Markdown raporundan SC-* başına hata metnini çıkarır."""
    p = Path(report_path)
    tc_to_sc = _load_tc_to_sc_map(p, sc_map_path=sc_map_path)
    text = p.read_text(encoding="utf-8", errors="replace")
    errors: dict[str, str] = {}

    if p.suffix.lower() == ".json" or text.lstrip().startswith("["):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return errors
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                sid = _resolve_sc_id_from_text(str(item.get("title", "")), tc_to_sc)
                err = str(item.get("testError", "")).strip()
                if sid and err:
                    errors[sid] = err
        return errors

    for block in _split_testsprite_md_blocks(text):
        sid = _resolve_sc_id_from_text(block, tc_to_sc)
        if sid and ("TEST FAILURE" in block or "❌" in block or "Test Error" in block):
            errors[sid] = block.strip()
    return errors


def export_delta_spec(
    spec_path: Path | str,
    state_path: Path | str,
    *,
    out_md: Path | str | None = None,
    out_feature: Path | str | None = None,
    include_smoke: bool = False,
) -> dict[str, Any]:
    """Yalnızca NEW, STALE, FAIL, FLAKY (+ opsiyonel @smoke PASS) senaryolarını delta dosyasına ayıklar."""
    spec_p = Path(spec_path).resolve()
    state_p = Path(state_path).resolve()
    state = _read_json(state_p)
    scenarios = state.get("scenarios", {})

    selected_ids: set[str] = set()
    for sid, sc in scenarios.items():
        st = sc.get("status", "NEW")
        if st in {"NEW", "STALE", "FAIL", "FLAKY"}:
            selected_ids.add(sid)
        elif include_smoke and st == "PASS" and "@smoke" in sc.get("tags", []):
            selected_ids.add(sid)

    feat_res = scanner.export_feature_file(
        spec_p,
        out_path=out_feature,
        only_scenario_ids=selected_ids,
    )

    out_md_resolved: str | None = None
    if out_md is not None:
        md_p = Path(out_md).resolve()
        md_p.parent.mkdir(parents=True, exist_ok=True)
        full_text = spec_p.read_text(encoding="utf-8")
        sec0_m = re.search(r"(##\s+0\b.*?)(?=^##\s+1\b)", full_text, re.DOTALL | re.MULTILINE)
        sec0_txt = sec0_m.group(1).strip() if sec0_m else "## 0. Test Ortamı\n- Kaynak spec: " + spec_p.name
        rows = [
            "| Scenario ID | Modül | Durum | Önceki PASS Ref |",
            "|---|---|---|---|",
        ]
        for sid in sorted(selected_ids):
            sc = scenarios.get(sid, {})
            lpr = sc.get("last_pass_ref") or sc.get("pass_ref") or {}
            ref_txt = f"{lpr.get('runner', '-')} @ {lpr.get('verified_commit', '-')}" if lpr else "—"
            rows.append(f"| `{sid}` | `{sc.get('module', '-')}` | `{sc.get('status', 'NEW')}` | {ref_txt} |")

        delta_body = (
            f"# {state.get('project_name', 'Project')} — Delta Test Spesifikasyonu\n\n"
            f"> Yalnız çalıştırılması gereken senaryolar (`NEW + STALE + FAIL + FLAKY`"
            f"{' + @smoke' if include_smoke else ''}). Toplam: {len(selected_ids)} senaryo.\n\n"
            f"{sec0_txt}\n\n"
            "## 1. Delta Kapsam Tablosu\n"
            + "\n".join(rows)
            + "\n\n## 2. Seçili Gherkin Senaryoları\n\n```gherkin\n"
            + feat_res["content"].strip()
            + "\n```\n"
        )
        md_p.write_text(delta_body, encoding="utf-8")
        out_md_resolved = md_p.as_posix()

    return {
        "included_scenarios": sorted(selected_ids),
        "included_count": len(selected_ids),
        "feature_count": feat_res["feature_count"],
        "scenario_count": feat_res["scenario_count"],
        "out_md": out_md_resolved,
        "out_feature": feat_res["out_path"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="test-spec-generator v2 artımlı takip & PASS defteri CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="Major vs Minor değişiklik analizi yap")
    p_plan.add_argument("--root", default=".")
    p_plan.add_argument("--state", default="docs/testing/test-spec-state.json")
    p_plan.add_argument("--peer", action="append", default=[])
    p_plan.add_argument("--focus", default="")
    p_plan.add_argument("--force-module", action="append", default=[])
    p_plan.add_argument("--json", action="store_true")

    p_sync = sub.add_parser("sync", help="Spec dosyasından state defterini senkronla")
    p_sync.add_argument("--root", default=".")
    p_sync.add_argument("--spec", required=True)
    p_sync.add_argument("--state", default="docs/testing/test-spec-state.json")

    p_patch = sub.add_parser("patch-module", help="Spec içindeki tek bir modül bloğunu cerrahi güncelle")
    p_patch.add_argument("--spec", required=True)
    p_patch.add_argument("--module", required=True)
    p_patch.add_argument("--content-file", required=True)
    p_patch.add_argument("--matrix-row", default="")

    p_rec = sub.add_parser("record", help="PASS/FAIL sonuçlarını state defterine işle")
    p_rec.add_argument("--state", default="docs/testing/test-spec-state.json")
    p_rec.add_argument("--result", action="append", default=[], help="Örn: SC-AUTH-01=PASS")
    p_rec.add_argument("--runner", default="manual")
    p_rec.add_argument("--commit", default="")
    p_rec.add_argument("--evidence", default="")
    p_rec.add_argument("--import-junit", default="")
    p_rec.add_argument("--import-playwright", default="")
    p_rec.add_argument("--import-cucumber", default="")
    p_rec.add_argument("--import-testsprite", default="")
    p_rec.add_argument("--sc-map", default="")

    p_delta = sub.add_parser("export-delta", help="Yalnızca NEW/STALE/FAIL senaryolarını dışa aktar")
    p_delta.add_argument("--spec", required=True)
    p_delta.add_argument("--state", default="docs/testing/test-spec-state.json")
    p_delta.add_argument("--out-md", default="")
    p_delta.add_argument("--out-feature", default="")
    p_delta.add_argument("--include-smoke", action="store_true")
    p_delta.add_argument("--json", action="store_true")

    p_stat = sub.add_parser("status", help="State defteri özet durumunu bas")
    p_stat.add_argument("--state", default="docs/testing/test-spec-state.json")
    p_stat.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "plan":
        focus_list = [f.strip() for f in args.focus.split(",") if f.strip()] if args.focus else None
        res = plan_incremental_update(
            args.root,
            args.state,
            peers=args.peer or None,
            focus=focus_list,
            force_modules=args.force_module or None,
        )
        if args.json:
            printable = {k: v for k, v in res.items() if k != "inventory"}
            print(json.dumps(printable, ensure_ascii=False, indent=2))
        else:
            print(f"[{res['mode']}] has_changes={res['has_changes']} stale={len(res.get('stale_scenarios', []))}")
            for mod, info in res["modules"].items():
                print(f"  - {mod}: {info['classification']} ({info['action']}) -> {', '.join(info['reasons']) or '—'}")
        return 0

    if args.cmd == "sync":
        inv = scanner.build_test_inventory(args.root)
        st = sync_state_from_spec(args.spec, args.state, inv)
        print(f"[OK] Synced {len(st['scenarios'])} scenarios -> {args.state}")
        return 0

    if args.cmd == "patch-module":
        content = Path(args.content_file).read_text(encoding="utf-8")
        res = patch_module_section(args.spec, args.module, content, matrix_row=args.matrix_row or None)
        print(f"[OK] {res['action']} module '{res['module']}' in {res['spec_path']}")
        return 0

    if args.cmd == "record":
        results: dict[str, str] = {}
        for item in args.result:
            if "=" in item:
                k, v = item.split("=", 1)
                results[k.strip()] = v.strip().upper()
        if args.import_junit:
            results.update(parse_junit_xml(args.import_junit))
        if args.import_playwright:
            results.update(parse_playwright_json(args.import_playwright))
        if args.import_cucumber:
            results.update(parse_cucumber_json(args.import_cucumber))
        if args.import_testsprite:
            results.update(parse_testsprite_report(args.import_testsprite, sc_map_path=args.sc_map or None))

        has_import = any(
            [args.import_junit, args.import_playwright, args.import_cucumber, args.import_testsprite]
        )
        res = record_execution_results(
            args.state,
            results,
            runner=args.runner,
            commit=args.commit or None,
            evidence_ref=args.evidence or None,
        )
        print(f"[OK] Recorded {res['updated_count']} results -> {res['state_path']}")
        if has_import and res["updated_count"] == 0:
            print(
                "[WARN] Rapordan state defteriyle eşleşen SC-* senaryosu bulunamadı (0 sonuç).",
                file=sys.stderr,
            )
            return 2
        return 0

    if args.cmd == "export-delta":
        res = export_delta_spec(
            args.spec,
            args.state,
            out_md=args.out_md or None,
            out_feature=args.out_feature or None,
            include_smoke=args.include_smoke,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"[OK] Delta exported: {res['included_count']} scenario(s)")
        return 0

    if args.cmd == "status":
        st = _read_json(Path(args.state))
        counts: dict[str, int] = {}
        for sc in st.get("scenarios", {}).values():
            s = sc.get("status", "NEW")
            counts[s] = counts.get(s, 0) + 1
        summary = {"project": st.get("project_name"), "total": len(st.get("scenarios", {})), "by_status": counts}
        print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json else f"[STATUS] {summary}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
