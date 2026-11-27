#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TestSprite MCP Köprüsü & Hata Adresleme Motoru (testsprite_bridge.py).

1. `to-plan`: `test-spec-state.json` içindeki çalıştırılması gereken (`NEW`, `STALE`,
   `FAIL`, `FLAKY`) senaryoları `testsprite_frontend_test_plan.json` şemasına dönüştürür
   ve `sc_map.json` (`TC### <-> SC-*`) eşleme haritasını üretir.
2. `triage`: Başarısız (`FAIL` / `FLAKY`) senaryoları `test-inventory.json` (`endpoints`,
   `route_details`, `peers`) ve TestSprite hata raporuyla çaprazlayarak sorunun kardeş
   backend reposunda mı (`peer`) yoksa frontend reposunda mı düzeltilmesi gerektiğini
   dosya yoluyla adresler.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
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

import test_spec_tracker as tracker  # noqa: E402

DELTA_STATUSES = {"NEW", "STALE", "FAIL", "FLAKY"}
API_PATH_IN_ERROR_RE = re.compile(r"(?:\b(GET|POST|PUT|PATCH|DELETE)\s+)?(/(?:api|v\d+)/[A-Za-z0-9_/\-{}:.]+)")
STEP_LINE_RE = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.+)$", re.IGNORECASE)


def _priority_from_tags(tags: list[str]) -> str:
    tag_set = {t.lower() for t in tags}
    if "@p0-critical" in tag_set or "@p1-high" in tag_set or "@smoke" in tag_set:
        return "High"
    if "@p3-low" in tag_set:
        return "Low"
    return "Medium"


def _gherkin_body_to_steps(body: str) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = []
    in_then = False
    for line in body.splitlines():
        m = STEP_LINE_RE.match(line)
        if not m:
            continue
        kw = m.group(1).lower()
        desc = m.group(2).strip()
        if kw == "then":
            in_then = True
        elif kw in {"given", "when"}:
            in_then = False
        steps.append({"type": "assertion" if in_then else "action", "description": desc})
    if not steps:
        steps.append({"type": "assertion", "description": "Verify scenario acceptance criteria"})
    return steps


def export_testsprite_plan(
    spec_path: Path | str,
    state_path: Path | str,
    plan_path: Path | str,
    *,
    map_path: Path | str | None = None,
    batch_size: int = 0,
    batch_index: int = 0,
    include_smoke: bool = False,
) -> dict[str, Any]:
    """Delta senaryolarını TestSprite plan JSON formatına çevirir ve sc_map.json üretir."""
    spec_p = Path(spec_path).resolve()
    state_p = Path(state_path).resolve()
    plan_p = Path(plan_path).resolve()
    map_p = Path(map_path).resolve() if map_path else (plan_p.parent / "sc_map.json")

    if not spec_p.is_file():
        raise FileNotFoundError(f"Spec dosyası bulunamadı: {spec_p}")
    if not state_p.is_file():
        raise FileNotFoundError(f"State defteri bulunamadı: {state_p}")

    state = tracker._read_json(state_p)
    state_scenarios: dict[str, Any] = state.get("scenarios", {})
    parsed = tracker._parse_spec_scenarios(spec_p.read_text(encoding="utf-8"))

    all_items: list[dict[str, Any]] = []
    tc_to_sc: dict[str, str] = {}
    sc_to_tc: dict[str, str] = {}

    seq = 1
    for sc in parsed:
        sid = sc["id"]
        st_entry = state_scenarios.get(sid, {})
        status = st_entry.get("status", "NEW")
        tags = sc.get("tags") or st_entry.get("tags") or []
        include = status in DELTA_STATUSES or (
            include_smoke and status == "PASS" and "@smoke" in tags
        )
        if not include:
            continue

        tc_id = f"TC{seq:03d}"
        seq += 1
        tc_to_sc[tc_id] = sid
        sc_to_tc[sid] = tc_id

        clean_title = re.sub(r"^Scenario(?: Outline)?\s*:\s*", "", sc["title"], flags=re.IGNORECASE).strip()
        surfaces = st_entry.get("bound_surfaces", [])
        ep_desc = ", ".join(s.replace("endpoint:", "").replace("route:", "") for s in surfaces[:4])
        all_items.append(
            {
                "id": tc_id,
                "title": clean_title if sid in clean_title else f"{sid} {clean_title}",
                "description": f"[{sc['module']}] {sid} ({status})" + (f" — Yüzeyler: {ep_desc}" if ep_desc else ""),
                "category": sc["module"],
                "steps": _gherkin_body_to_steps(sc["body"]),
                "priority": _priority_from_tags(tags),
            }
        )

    plan_p.parent.mkdir(parents=True, exist_ok=True)
    bak_p = plan_p.with_suffix(plan_p.suffix + ".bak")
    if plan_p.is_file() and not map_p.is_file() and not bak_p.is_file():
        shutil.copy2(plan_p, bak_p)

    total_delta = len(all_items)
    if batch_size > 0 and total_delta > 0:
        total_batches = math.ceil(total_delta / batch_size)
        start = max(batch_index, 0) * batch_size
        selected_items = all_items[start : start + batch_size]
    else:
        total_batches = 1 if total_delta > 0 else 0
        selected_items = all_items

    plan_p.write_text(json.dumps(selected_items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    map_payload = {
        "spec_file": spec_p.as_posix(),
        "plan_file": plan_p.as_posix(),
        "total_delta": total_delta,
        "batch_size": batch_size,
        "total_batches": total_batches,
        "tc_to_sc": tc_to_sc,
        "sc_to_tc": sc_to_tc,
    }
    map_p.parent.mkdir(parents=True, exist_ok=True)
    map_p.write_text(json.dumps(map_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "total_delta": total_delta,
        "total_batches": total_batches,
        "batch_index": batch_index,
        "batch_count": len(selected_items),
        "batch_test_ids": [it["id"] for it in selected_items],
        "plan_path": plan_p.as_posix(),
        "map_path": map_p.as_posix(),
    }


def _resolve_endpoint_owner(
    ep_file: str,
    root_p: Path,
    peers: list[Path],
) -> tuple[str, str]:
    """Endpoint dosyasının kardeş backend (peer) mi yoksa birincil repo mu olduğunu belirler."""
    if not ep_file:
        return (peers[0].as_posix(), "backend-peer") if peers else (root_p.as_posix(), "primary")

    for peer in peers:
        if (peer / ep_file).is_file():
            return peer.as_posix(), "backend-peer"
    if (root_p / ep_file).is_file():
        return root_p.as_posix(), "primary"

    norm = ep_file.replace("\\", "/")
    if peers and (
        norm.startswith("src/main/java/")
        or norm.endswith((".java", ".kt"))
        or "controller" in norm.lower()
    ):
        return peers[0].as_posix(), "backend-peer"
    return root_p.as_posix(), "primary"


def triage_failed_scenarios(
    state_path: Path | str,
    inventory_path: Path | str,
    *,
    report_path: Path | str | None = None,
    sc_map_path: Path | str | None = None,
) -> dict[str, Any]:
    """FAIL/FLAKY senaryoları envanter + kardeş repo bilgisiyle çaprazlayıp kök hedefi adresler."""
    state_p = Path(state_path).resolve()
    inv_p = Path(inventory_path).resolve()
    state = tracker._read_json(state_p)
    inv = tracker._read_json(inv_p)

    root_p = Path(inv.get("root") or state_p.parent).resolve()
    peers = [Path(p).resolve() for p in inv.get("peers", []) if p]

    ep_by_sig: dict[str, dict[str, Any]] = {}
    ep_by_path: dict[str, list[dict[str, Any]]] = {}
    for ep in inv.get("endpoints", []):
        sig = f"{str(ep.get('method', 'GET')).upper()} {ep['path']}"
        ep_by_sig[sig] = ep
        ep_by_path.setdefault(ep["path"], []).append(ep)

    route_by_path = {rd["path"]: rd for rd in inv.get("route_details", []) if "path" in rd}
    errors_by_sc: dict[str, str] = {}
    if report_path:
        rp = Path(report_path)
        if rp.is_file():
            errors_by_sc = tracker.extract_testsprite_errors(rp, sc_map_path=sc_map_path)

    items: list[dict[str, Any]] = []
    for sid, sc in sorted(state.get("scenarios", {}).items()):
        if sc.get("status") not in {"FAIL", "FLAKY"}:
            continue

        err_txt = errors_by_sc.get(sid, "")
        bound = list(sc.get("bound_surfaces") or [])

        matched_eps: list[dict[str, Any]] = []
        seen_sigs: set[str] = set()
        for b in bound:
            if b.startswith("endpoint:"):
                _, method, path = b.split(":", 2)
                sig = f"{method.upper()} {path}"
                if sig in ep_by_sig and sig not in seen_sigs:
                    matched_eps.append(ep_by_sig[sig])
                    seen_sigs.add(sig)

        for m_method, m_path in API_PATH_IN_ERROR_RE.findall(err_txt):
            if m_method:
                sig = f"{m_method.upper()} {m_path}"
                if sig in ep_by_sig and sig not in seen_sigs:
                    matched_eps.append(ep_by_sig[sig])
                    seen_sigs.add(sig)
            for ep in ep_by_path.get(m_path, []):
                sig = f"{str(ep.get('method', 'GET')).upper()} {ep['path']}"
                if sig not in seen_sigs:
                    matched_eps.append(ep)
                    seen_sigs.add(sig)

        fe_files: list[str] = []
        for b in bound:
            if b.startswith("route:"):
                rpath = b.split(":", 1)[1]
                rd = route_by_path.get(rpath)
                if rd and rd.get("file") and rd["file"] not in fe_files:
                    fe_files.append(rd["file"])

        be_files: list[str] = []
        peer_owner: str | None = None
        for ep in matched_eps:
            f = ep.get("file", "")
            owner, role = _resolve_endpoint_owner(f, root_p, peers)
            if role == "backend-peer":
                peer_owner = owner
            if f and f not in be_files:
                be_files.append(f)

        ep_refs = [f"{str(e.get('method', 'GET')).upper()} {e['path']}" for e in matched_eps]
        has_api_signal = bool(re.search(r"/api/|HTTP\s+[45]\d\d|\b500\b|\b403\b|\b404\b", err_txt, re.IGNORECASE))

        if peer_owner and (be_files or has_api_signal):
            repo_role = "backend-peer"
            owner_repo = peer_owner
            suspect_files = be_files + [f for f in fe_files if f not in be_files]
            recommended_action = (
                f"Endpoint takılması / API hatası tespit edildi ({', '.join(ep_refs[:3]) or 'API'}). "
                f"Önce kardeş backend reposunda ({peer_owner}) şu dosyaları düzelt: {', '.join(be_files[:3]) or 'ilgili controller/service'}; "
                f"ardından frontend ({root_p.name}) tarafındaki {', '.join(fe_files[:2]) or 'çağıran ekran'} akışını doğrula."
            )
        elif be_files:
            repo_role = "backend"
            owner_repo = root_p.as_posix()
            suspect_files = be_files + [f for f in fe_files if f not in be_files]
            recommended_action = (
                f"API endpoint hatası ({', '.join(ep_refs[:3])}): "
                f"{', '.join(be_files[:3])} ve çağıran UI dosyalarını incele."
            )
        else:
            repo_role = "frontend"
            owner_repo = root_p.as_posix()
            suspect_files = fe_files
            recommended_action = (
                f"UI / rota hatası ({root_p.name}): "
                f"{', '.join(fe_files[:3]) or sc.get('module', 'ilgili ekran')} bileşenini incele."
            )

        items.append(
            {
                "scenario_id": sid,
                "module": sc.get("module", ""),
                "status": sc.get("status", "FAIL"),
                "repo_role": repo_role,
                "owner_repo": owner_repo,
                "endpoint_refs": ep_refs,
                "suspect_files": suspect_files,
                "error_excerpt": err_txt[:400],
                "recommended_action": recommended_action,
            }
        )

    return {"failed_count": len(items), "items": items}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TestSprite MCP Köprüsü & Kardeş Repo Hata Adresleme CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("to-plan", help="Delta senaryolarını TestSprite plan JSON formatına çevir")
    p_plan.add_argument("--spec", required=True)
    p_plan.add_argument("--state", default="docs/testing/test-spec-state.json")
    p_plan.add_argument("--plan", default="testsprite_tests/testsprite_frontend_test_plan.json")
    p_plan.add_argument("--map", default="")
    p_plan.add_argument("--batch", type=int, default=0)
    p_plan.add_argument("--batch-index", type=int, default=0)
    p_plan.add_argument("--include-smoke", action="store_true")
    p_plan.add_argument("--json", action="store_true")

    p_tri = sub.add_parser("triage", help="FAIL senaryolarını frontend / kardeş backend reposuna adresle")
    p_tri.add_argument("--state", default="docs/testing/test-spec-state.json")
    p_tri.add_argument("--inventory", default="docs/testing/test-inventory.json")
    p_tri.add_argument("--report", default="")
    p_tri.add_argument("--sc-map", default="")
    p_tri.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "to-plan":
        res = export_testsprite_plan(
            args.spec,
            args.state,
            args.plan,
            map_path=args.map or None,
            batch_size=args.batch,
            batch_index=args.batch_index,
            include_smoke=args.include_smoke,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(
                f"[OK] TestSprite planı yazıldı: {res['batch_count']}/{res['total_delta']} senaryo "
                f"(parti {res['batch_index'] + 1}/{max(res['total_batches'], 1)}) -> {res['plan_path']}"
            )
        return 0

    if args.cmd == "triage":
        res = triage_failed_scenarios(
            args.state,
            args.inventory,
            report_path=args.report or None,
            sc_map_path=args.sc_map or None,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"[TRIAGE] {res['failed_count']} başarısız senaryo analiz edildi.")
            for it in res["items"]:
                print(f"  - {it['scenario_id']} [{it['repo_role']}] -> {it['owner_repo']}")
                print(f"    Öneri: {it['recommended_action']}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
