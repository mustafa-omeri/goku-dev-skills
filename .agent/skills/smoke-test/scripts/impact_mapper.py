#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etki-Odaklı Patlama Yarıçapı ve Test Hedefi Çözümleyici (impact_mapper.py).

Bir sprint kartı veya git değişikliği sonrası:
1. Değişen dosyaları çözer (`git status --porcelain` + son commit veya açık `changed_files` / `KANBAN.md`).
2. `feature-architect` (`fa_scan.run_scan_with_graph`) üzerinden Endpoint, HttpCall, Component ve Route düğümlerini çıkarır.
3. `KnowledgeGraph` + frontend import/sembol ters grafiği ile değişen Endpoint/Service/Entity'den
   etkilenen tüketici UI ekranlarını (`/routes`) ve test dosyalarını bulur.
4. `docs/testing/test-spec-state.json` varsa STALE/FAIL/NEW/@smoke senaryolarını eşler.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import deque
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

THIS_DIR = Path(__file__).resolve().parent
SKILLS_ROOT = THIS_DIR.parents[1]
FA_SCRIPTS_DIR = SKILLS_ROOT / "feature-architect" / "scripts"
if str(FA_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(FA_SCRIPTS_DIR))

import fa_scan  # noqa: E402
from fa_engine.model import iter_repo_files, normalize_api_path  # noqa: E402

DOC_ONLY_EXTS = {".md", ".txt", ".rst", ".adoc", ".png", ".jpg", ".jpeg", ".svg", ".webp"}
CODE_DIRS_HINT = ("src/", "app/", "pages/", "components/", "api/", "routers/", "backend/", "supabase/")
TEST_FILE_RE = re.compile(r"(?:\.test\.|\.spec\.|Test\.java$|Tests\.java$|^test_.*\.py$|_test\.py$)")
IMPORT_RE = re.compile(
    r"""(?:import\s+.*?\s+from\s+|import\s*\(\s*|require\s*\(\s*)[\"'`]([^\"'`]+)[\"'`]"""
)
EXPORTED_SYM_RE = re.compile(
    r"\bexport\s+(?:async\s+)?(?:function|const|class)\s+([A-Za-z_][A-Za-z0-9_]*)"
)


def _norm_rel(path_str: str) -> str:
    norm = path_str.replace("\\", "/")
    while norm.startswith("./"):
        norm = norm[2:]
    return norm


def _is_external_http_url(raw_path: str) -> bool:
    low = raw_path.strip().lower()
    if not low.startswith(("http://", "https://")):
        return False
    return not low.startswith(("http://localhost", "https://localhost", "http://127.0.0.1", "https://127.0.0.1"))


def is_doc_or_meta_only(changed_files: list[str]) -> bool:
    if not changed_files:
        return False
    for raw in changed_files:
        norm = _norm_rel(raw).lower()
        if norm.startswith((".agent/", "docs/", "specs/", ".github/")):
            continue
        p = Path(norm)
        if p.suffix.lower() in DOC_ONLY_EXTS:
            continue
        if p.name in {"handoff.md", "kanban.md", "sprint_plan.md", "release_plan.md", "knowledge-base.md"}:
            continue
        return False
    return True


def resolve_changed_files(root: Path, scope: str = "last") -> list[str]:
    """Çalışma ağacı ve (varsa) son commit/sprint kapsamından değişen dosya listesini döndürür."""
    root = root.resolve()
    changed: set[str] = set()
    if (root / ".git").exists():
        for cmd in (
            ["git", "status", "--porcelain"],
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"] if scope == "last" else ["git", "diff", "--name-only", "HEAD~5", "HEAD"],
        ):
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(root),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=5,
                )
                if proc.returncode != 0:
                    continue
                for line in proc.stdout.splitlines():
                    ln = line.strip()
                    if not ln:
                        continue
                    if cmd[1] == "status":
                        parts = ln.split(maxsplit=1)
                        if len(parts) < 2:
                            continue
                        fp = parts[1].strip().strip('"')
                        if " -> " in fp:
                            fp = fp.split(" -> ", 1)[1].strip().strip('"')
                        changed.add(_norm_rel(fp))
                    else:
                        changed.add(_norm_rel(ln.strip('"')))
            except (OSError, subprocess.SubprocessError):
                continue
    return sorted(changed)


def _build_fe_reverse_import_graph(root: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Frontend dosyaları arasında `target_rel -> {importer_rels}` ve `symbol -> {files}` indeksleri kurar."""
    rev_imports: dict[str, set[str]] = {}
    file_symbols: dict[str, set[str]] = {}
    fe_files = list(iter_repo_files(root, {".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte"}))
    all_rel = {_norm_rel(f.relative_to(root).as_posix()): f for f in fe_files}

    for rel, fpath in all_rel.items():
        text = fpath.read_text(encoding="utf-8", errors="replace")
        syms = set(EXPORTED_SYM_RE.findall(text))
        if syms:
            file_symbols[rel] = syms
        for m in IMPORT_RE.finditer(text):
            spec = m.group(1)
            if not spec.startswith("."):
                continue
            cand_base = (fpath.parent / spec).resolve()
            resolved_rel: str | None = None
            for suffix in ("", ".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js"):
                cand = Path(str(cand_base) + suffix)
                try:
                    crel = _norm_rel(cand.relative_to(root).as_posix())
                except ValueError:
                    continue
                if crel in all_rel:
                    resolved_rel = crel
                    break
            if resolved_rel:
                rev_imports.setdefault(resolved_rel, set()).add(rel)

    return rev_imports, file_symbols


def _expand_importers(seed_files: set[str], rev_imports: dict[str, set[str]], max_depth: int = 4) -> set[str]:
    visited: set[str] = set(seed_files)
    queue: deque[tuple[str, int]] = deque((f, 0) for f in seed_files)
    while queue:
        curr, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for parent in rev_imports.get(curr, set()):
            if parent not in visited:
                visited.add(parent)
                queue.append((parent, depth + 1))
    return visited


def _discover_test_files(root: Path, impacted_stems: set[str]) -> list[str]:
    tests: list[str] = []
    for fpath in iter_repo_files(root, {".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".kt"}):
        rel = _norm_rel(fpath.relative_to(root).as_posix())
        if not TEST_FILE_RE.search(fpath.name):
            continue
        if not impacted_stems:
            tests.append(rel)
            continue
        low = rel.lower()
        if any(stem in low for stem in impacted_stems if len(stem) >= 3):
            tests.append(rel)
    return sorted(set(tests))


def _load_delta_scenarios(root: Path, impacted_modules: set[str]) -> list[str]:
    state_p = root / "docs" / "testing" / "test-spec-state.json"
    if not state_p.is_file():
        return []
    try:
        data = json.loads(state_p.read_text(encoding="utf-8"))
    except Exception:
        return []
    selected: list[str] = []
    for sid, meta in data.get("scenarios", {}).items():
        st = meta.get("status", "NEW")
        mod = str(meta.get("module", "")).lower()
        tags = meta.get("tags", [])
        if st in {"NEW", "STALE", "FAIL", "FLAKY"} or "@smoke" in tags or (mod and mod in impacted_modules):
            selected.append(sid)
    return sorted(selected)


def map_impact(
    root: Path | str,
    *,
    scope: str = "last",
    peers: list[str | Path] | None = None,
    changed_files: list[str] | None = None,
) -> dict[str, Any]:
    """Değişikliklerin etkilediği endpoint, UI rotası, test dosyası ve kırık boru hatlarını çıkarır."""
    root_p = Path(root).resolve()
    resolved_changes = (
        [_norm_rel(f) for f in changed_files]
        if changed_files is not None
        else resolve_changed_files(root_p, scope=scope)
    )

    if scope == "last" and resolved_changes and is_doc_or_meta_only(resolved_changes):
        return {
            "root": root_p.as_posix(),
            "scope": scope,
            "doc_only": True,
            "changed_files": resolved_changes,
            "affected_endpoints": [],
            "affected_screens": [],
            "affected_test_files": [],
            "broken_pipelines": [],
            "contract_issues": [],
            "delta_scenarios": [],
            "discovered_ports": [],
            "stacks": {"frontend": [], "backend": []},
        }

    snapshot, kg = fa_scan.run_scan_with_graph(root_p, peers=peers)
    facts = snapshot.get("facts", [])
    raw_broken_pipelines = [
        f for f in facts
        if f.get("code") == "BROKEN_DATA_PIPELINE"
        and not _is_external_http_url(str((f.get("attrs") or {}).get("path", "")))
    ]
    raw_contract_issues = [
        f for f in facts if f.get("code") in {"DTO_CONTRACT_MISMATCH", "API_VERSION_SKEW", "DTO_SCHEMA_DRIFT"}
    ]

    # Index Endpoint, HttpCall, Component, and Route nodes from KnowledgeGraph
    ep_nodes = [n for n in kg.nodes.values() if n.kind == "Endpoint"]
    http_nodes = [n for n in kg.nodes.values() if n.kind == "HttpCall"]
    comp_nodes = {n.id: n for n in kg.nodes.values() if n.kind in {"Component", "Screen"}}
    route_nodes = [n for n in kg.nodes.values() if n.kind == "Route"]

    route_to_comp_file: dict[str, tuple[str, str]] = {}
    for edge in kg.edges:
        if edge.kind == "renders" and edge.source.startswith("Route:"):
            rpath = edge.source.split(":", 1)[1]
            cnode = comp_nodes.get(edge.target)
            cfile = _norm_rel(cnode.file) if cnode and cnode.file else ""
            cname = cnode.name if cnode else edge.target
            route_to_comp_file[rpath] = (cname, cfile)

    changed_set = set(resolved_changes)
    use_all = scope == "all" or (scope == "sprint" and not changed_set)

    affected_ep_ids: set[str] = set()
    affected_endpoints: list[dict[str, Any]] = []

    for ep in ep_nodes:
        ep_file = _norm_rel(ep.file)
        directly_changed = ep_file in changed_set or use_all
        # Also match service/repository stem changes (e.g. ProjectService -> ProjectController)
        if not directly_changed and changed_set:
            ep_stem = Path(ep_file).stem.lower().replace("controller", "").replace("route", "")
            if ep_stem and any(ep_stem in Path(cf).stem.lower() for cf in changed_set):
                directly_changed = True
        if directly_changed:
            affected_ep_ids.add(ep.id)
            affected_endpoints.append({
                "id": ep.id,
                "method": ep.attrs.get("method", "GET"),
                "path": ep.attrs.get("path", ep.name.split(" ", 1)[-1]),
                "normalized_path": ep.attrs.get("normalized_path", ""),
                "file": ep_file,
                "line": ep.line,
                "changed_directly": ep_file in changed_set,
            })

    # Find HttpCalls pointing to affected endpoints (or directly inside changed FE files)
    affected_norm_paths = {
        normalize_api_path(ep["path"]) for ep in affected_endpoints if ep.get("path")
    }
    seed_fe_files: set[str] = {cf for cf in changed_set if cf.endswith((".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte"))}

    for hnode in http_nodes:
        hfile = _norm_rel(hnode.file)
        hnorm = hnode.attrs.get("normalized_path") or normalize_api_path(hnode.attrs.get("raw_path", ""))
        if use_all or hnorm in affected_norm_paths or hfile in changed_set:
            if hfile:
                seed_fe_files.add(hfile)
            # If frontend file changed and backend endpoint exists for it, include that endpoint too
            for ep in ep_nodes:
                ep_norm = ep.attrs.get("normalized_path") or normalize_api_path(ep.attrs.get("path", ""))
                if ep_norm == hnorm and ep.id not in affected_ep_ids:
                    affected_ep_ids.add(ep.id)
                    affected_endpoints.append({
                        "id": ep.id,
                        "method": ep.attrs.get("method", "GET"),
                        "path": ep.attrs.get("path", ep.name.split(" ", 1)[-1]),
                        "normalized_path": ep_norm,
                        "file": _norm_rel(ep.file),
                        "line": ep.line,
                        "changed_directly": False,
                    })

    # Expand from API/hook files up to Screen/Component files via reverse imports
    rev_imports, _ = _build_fe_reverse_import_graph(root_p)
    impacted_fe_files = _expand_importers(seed_fe_files, rev_imports)

    # Also consult KG consumers() for affected endpoints
    for ep_id in list(affected_ep_ids):
        for cons in kg.consumers(ep_id, max_depth=4):
            cnode = kg.nodes.get(cons["consumer"])
            if cnode and cnode.file:
                impacted_fe_files.add(_norm_rel(cnode.file))

    affected_screens: list[dict[str, Any]] = []
    seen_routes: set[str] = set()
    for rnode in route_nodes:
        rpath = rnode.name
        if rpath.endswith("/*"):
            continue
        cname, cfile = route_to_comp_file.get(rpath, ("", ""))
        if use_all or (cfile and cfile in impacted_fe_files):
            if rpath not in seen_routes:
                seen_routes.add(rpath)
                affected_screens.append({
                    "route": rpath,
                    "component": cname or "Unknown",
                    "file": cfile,
                    "reason": "scope_all" if use_all else "impact_graph_consumer",
                })

    impacted_stems: set[str] = set()
    for cf in changed_set | impacted_fe_files:
        stem = Path(cf).stem.lower()
        for suffix in ("controller", "service", "repository", "page", "view", "api"):
            stem = stem.replace(suffix, "")
        if stem:
            impacted_stems.add(stem)
    for ep in affected_endpoints:
        seg = [s for s in ep["path"].split("/") if s and s not in {"api", "v1", "v2"} and not s.startswith("{")]
        if seg:
            impacted_stems.add(seg[0].lower())

    affected_tests = _discover_test_files(root_p, set() if use_all else impacted_stems)
    delta_scenarios = _load_delta_scenarios(root_p, impacted_stems)

    if scope == "last" and changed_set:
        relevant_files = changed_set | impacted_fe_files | {ep["file"] for ep in affected_endpoints if ep.get("file")}
        backend_changed = any(
            cf.endswith((".java", ".kt", ".py")) or "/api/" in cf or "controller" in cf.lower() or "router" in cf.lower()
            for cf in changed_set
        )

        def _is_relevant_fact(fact: dict[str, Any]) -> bool:
            loc_file = _norm_rel(str(fact.get("location", "")).split(":", 1)[0])
            if loc_file in relevant_files:
                return True
            fpath = str((fact.get("attrs") or {}).get("path", ""))
            if fpath and normalize_api_path(fpath) in affected_norm_paths:
                return True
            if backend_changed:
                target_blob = f"{loc_file} {fpath}".lower()
                if any(stem in target_blob for stem in impacted_stems if len(stem) >= 3):
                    return True
            return False

        broken_pipelines = [f for f in raw_broken_pipelines if _is_relevant_fact(f)]
        contract_issues = [f for f in raw_contract_issues if _is_relevant_fact(f)]
    else:
        broken_pipelines = raw_broken_pipelines
        contract_issues = raw_contract_issues

    disc_meta = snapshot.get("discovery_metadata", {})
    stack_meta = snapshot.get("v1_gap_report", {}).get("stack", {})
    ports = disc_meta.get("server_ports", [])

    return {
        "root": root_p.as_posix(),
        "scope": scope,
        "doc_only": False,
        "changed_files": resolved_changes,
        "affected_endpoints": sorted(affected_endpoints, key=lambda x: (x["path"], x["method"])),
        "affected_screens": sorted(affected_screens, key=lambda x: x["route"]),
        "affected_test_files": affected_tests,
        "broken_pipelines": broken_pipelines,
        "contract_issues": contract_issues,
        "delta_scenarios": delta_scenarios,
        "discovered_ports": ports,
        "stacks": {
            "frontend": stack_meta.get("frontend", []),
            "backend": stack_meta.get("backend", []),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Impact-Driven Blast-Radius & Smoke Target Mapper")
    parser.add_argument("--root", default=".", help="Proje kök dizini")
    parser.add_argument("--scope", choices=["last", "sprint", "all"], default="last")
    parser.add_argument("--peer", action="append", default=[], help="Opsiyonel kardeş repo yolu")
    parser.add_argument("--changed", action="append", default=None, help="Açık değişen dosya listesi")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    res = map_impact(
        args.root,
        scope=args.scope,
        peers=args.peer or None,
        changed_files=args.changed,
    )
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(
            f"[IMPACT] scope={res['scope']} doc_only={res['doc_only']} "
            f"endpoints={len(res['affected_endpoints'])} screens={len(res['affected_screens'])} "
            f"tests={len(res['affected_test_files'])} broken_pipelines={len(res['broken_pipelines'])}"
        )
        for ep in res["affected_endpoints"]:
            print(f"  EP  {ep['method']:6} {ep['path']} ({ep['file']})")
        for sc in res["affected_screens"]:
            print(f"  UI  {sc['route']} -> {sc['component']} ({sc['file']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
