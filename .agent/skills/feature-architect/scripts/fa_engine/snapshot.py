# -*- coding: utf-8 -*-
"""Snapshot v2 assembler and backward-compatible v1 projection (`snapshot.py`)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .analyzers.base import AnalyzerResult
from .graph import KnowledgeGraph
from .model import (
    ENGINE_VERSION,
    SNAPSHOT_SCHEMA_VERSION,
    V1_GAP_SCHEMA_VERSION,
    AnalyzerError,
    Fact,
    ProjectProfile,
    compute_input_hash,
    iter_repo_files,
    normalize_api_path,
)


def _build_v1_orphan_endpoints(
    root: Path,
    shared_state: dict[str, Any],
) -> list[dict[str, str]]:
    be_state = shared_state.get("backend", {})
    endpoints: list[dict[str, Any]] = be_state.get("endpoints", [])
    if not endpoints:
        return []

    fe_paths_norm: set[str] = set()
    str_lit_re = re.compile(r"[\"'`](/[a-zA-Z0-9_/\-{}:.$]+)[\"'`]")
    for fpath in iter_repo_files(root, {".tsx", ".jsx", ".vue", ".svelte", ".html", ".ts", ".js", ".mjs", ".cjs"}):
        txt = fpath.read_text(encoding="utf-8", errors="replace")
        for m in str_lit_re.finditer(txt):
            fe_paths_norm.add(normalize_api_path(m.group(1)))

    orphans: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for ep in endpoints:
        if ep["normalized_path"] not in fe_paths_norm:
            key = (ep["method"], ep["path"])
            if key not in seen:
                seen.add(key)
                orphans.append(
                    {
                        "method": ep["method"],
                        "path": ep["path"],
                        "file": ep["file"],
                        "confidence": "candidate",
                    }
                )
    return orphans


def build_snapshot_v2(
    *,
    profile: ProjectProfile,
    focus: list[str] | None,
    analyzer_results: list[AnalyzerResult],
    failed_analyzers: list[AnalyzerError],
    kg: KnowledgeGraph,
    extra_facts: list[Fact],
    shared_state: dict[str, Any],
) -> dict[str, Any]:
    """Assemble deterministic Snapshot v2 along with complete v1 projection."""
    all_roots_paths = [r for _, r in profile.all_active_roots]
    input_hash = compute_input_hash(all_roots_paths)

    all_facts: list[Fact] = []
    analyzer_versions: dict[str, str] = {}
    limitations: list[str] = []
    scanned_total = 0
    analyzer_summaries: list[dict[str, Any]] = []

    for res in analyzer_results:
        analyzer_versions[res.analyzer] = res.version
        scanned_total += res.coverage.scanned_files
        all_facts.extend(res.facts)
        for lim in res.limitations:
            if lim not in limitations:
                limitations.append(lim)
        analyzer_summaries.append(res.to_summary_dict())

    all_facts.extend(extra_facts)
    # Deterministic sort of facts by (code, location, summary)
    sorted_facts = sorted(
        (f.to_dict() for f in all_facts),
        key=lambda x: (x["code"], x["location"], x["summary"]),
    )
    for idx, fdict in enumerate(sorted_facts, start=1):
        fdict["seq"] = idx

    fe_state = shared_state.get("frontend", {})
    be_state = shared_state.get("backend", {})
    data_state = shared_state.get("data", {})

    stub_pages = fe_state.get("stub_pages", [])
    stub_actions = fe_state.get("stub_actions", [])
    broken_routes = fe_state.get("broken_routes", [])
    declared_routes = fe_state.get("declared_routes", [])
    links = fe_state.get("links", [])
    orphan_endpoints = _build_v1_orphan_endpoints(profile.root, shared_state)
    orphan_fields = data_state.get("v1_orphan_fields", [])
    roles = be_state.get("roles", [])
    core_modules = fe_state.get(
        "core_modules",
        {"dashboard": [], "profile": [], "settings": [], "notifications": []},
    )

    v1_projection = {
        "schema": V1_GAP_SCHEMA_VERSION,
        "roots": {
            "root": profile.root.resolve().as_posix(),
            "peers": [p.as_posix() for p in profile.confirmed_peer_paths],
        },
        "focus": focus or ["all"],
        "stack": {
            "frontend": fe_state.get("fe_stack", profile.frontend_stacks),
            "backend": be_state.get("be_stack", profile.backend_stacks),
            "i18n": fe_state.get("locale_files", []),
        },
        "summary": {
            "stub_pages": len(stub_pages),
            "stub_actions": len(stub_actions),
            "broken_routes": len(broken_routes),
            "orphan_endpoints": len(orphan_endpoints),
            "orphan_fields": len(orphan_fields),
            "todo_markers": fe_state.get("todo_count", 0),
        },
        "stub_pages": stub_pages,
        "stub_actions": stub_actions,
        "routes": {
            "declared": declared_routes,
            "links": links,
        },
        "broken_routes": broken_routes,
        "orphan_endpoints": orphan_endpoints,
        "orphan_fields": orphan_fields,
        "roles": roles,
        "core_modules": core_modules,
        "warnings": [err.message for err in failed_analyzers],
    }

    confirmed_by_sev: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    inferred_by_sev: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in sorted_facts:
        sev = f["severity"]
        if f["status"] == "CONFIRMED":
            confirmed_by_sev[sev] = confirmed_by_sev.get(sev, 0) + 1
        elif f["status"] == "INFERRED":
            inferred_by_sev[sev] = inferred_by_sev.get(sev, 0) + 1

    kg_summary = kg.integrity_summary()

    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "engine_version": ENGINE_VERSION,
        "input_hash": input_hash,
        "project_metadata": {
            "root": profile.root.resolve().as_posix(),
            "topology": profile.topology,
            "tenancy_model": profile.tenancy_model,
            "focus": focus or ["all"],
        },
        "discovery_metadata": profile.to_dict(),
        "analyzer_versions": dict(sorted(analyzer_versions.items())),
        "analysis_coverage": {
            "scanned_files": scanned_total,
            "analyzers": analyzer_summaries,
            "failed": [e.to_dict() for e in failed_analyzers],
        },
        "readiness_radar": {
            "analysis_coverage_files": scanned_total,
            "failed_analyzers_count": len(failed_analyzers),
            "pipeline_integrity_pct": kg_summary["pipeline_integrity_pct"],
            "confirmed_risks": confirmed_by_sev,
            "inferred_risks": inferred_by_sev,
            "max_verification_level": "L2" if profile.contract_sources else "L1",
        },
        "entities_summary": {
            "routes": len(declared_routes),
            "http_calls": len(fe_state.get("http_calls", [])),
            "endpoints": len(be_state.get("endpoints", [])),
            "dtos": len(be_state.get("dtos", {})),
            "roles": len(roles),
        },
        "graph_summary": kg_summary,
        "unresolved_dependencies": kg.unresolved_edges(),
        "facts": sorted_facts,
        "limitations": limitations,
        "v1_projection": v1_projection,
    }
