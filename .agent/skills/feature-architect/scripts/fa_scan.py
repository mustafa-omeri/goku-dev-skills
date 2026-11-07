#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect v2 Full-Stack Deterministic Scanner CLI (`fa_scan.py`).

Executes:
  1. Multi-source verified discovery (`discovery.py`)
  2. Error-isolated deterministic analyzers (`analyzers/*`)
  3. Canonical Knowledge Graph assembly (`graph.py`)
  4. Snapshot v2 + backward-compatible v1 projection (`snapshot.py`)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fa_engine.analyzers.backend import BackendAnalyzer  # noqa: E402
from fa_engine.analyzers.base import Analyzer, AnalyzerContext, AnalyzerResult  # noqa: E402
from fa_engine.analyzers.frontend import FrontendAnalyzer  # noqa: E402
from fa_engine.discovery import discover_project  # noqa: E402
from fa_engine.graph import KnowledgeGraph, build_knowledge_graph  # noqa: E402
from fa_engine.model import AnalyzerError  # noqa: E402
from fa_engine.snapshot import build_snapshot_v2  # noqa: E402


def _default_analyzers(run_build: bool = False) -> list[Any]:
    analyzers: list[Any] = [
        FrontendAnalyzer(),
        BackendAnalyzer(),
    ]
    # Phase 2 analyzers load dynamically as they are registered in fa_engine/analyzers/
    optional_modules = [
        ("fa_engine.analyzers.data", "DataGovernanceAnalyzer", {}),
        ("fa_engine.analyzers.api_contract", "ApiContractAnalyzer", {}),
        ("fa_engine.analyzers.authz", "AuthorizationSurfaceAnalyzer", {}),
        ("fa_engine.analyzers.build", "BuildHealthAnalyzer", {"run_build": run_build}),
        ("fa_engine.analyzers.fitness", "ArchitectureFitnessAnalyzer", {}),
        ("fa_engine.analyzers.ops_signals", "OperationsSignalsAnalyzer", {}),
        ("fa_engine.analyzers.adr", "AdrIntelligenceAnalyzer", {}),
        ("fa_engine.analyzers.skill_adapters", "SkillAdaptersAnalyzer", {}),
    ]
    for mod_name, cls_name, kwargs in optional_modules:
        try:
            mod = __import__(mod_name, fromlist=[cls_name])
            cls = getattr(mod, cls_name)
            analyzers.append(cls(**kwargs) if kwargs else cls())
        except ImportError:
            continue
    return analyzers


def run_scan_with_graph(
    root: Path | str,
    *,
    peers: list[Path | str] | None = None,
    focus: list[str] | None = None,
    extra_analyzers: list[Analyzer] | None = None,
    run_build: bool = False,
) -> tuple[dict[str, Any], KnowledgeGraph]:
    """Run deterministic L1/L2 scan and return `(snapshot_v2_dict, knowledge_graph)`."""
    profile = discover_project(root, explicit_peers=peers)
    ctx = AnalyzerContext(profile=profile)

    analyzers = _default_analyzers(run_build=run_build)
    if extra_analyzers:
        analyzers.extend(extra_analyzers)

    results: list[AnalyzerResult] = []
    failed: list[AnalyzerError] = []

    for analyzer in analyzers:
        try:
            applicable, reason = analyzer.applies(profile)
            if not applicable:
                res = analyzer.analyze(ctx) if analyzer.name == "backend" else AnalyzerResult(
                    analyzer=analyzer.name,
                    version=getattr(analyzer, "version", "2.0.0"),
                    applicable=False,
                    applicability_reason=reason,
                )
                results.append(res)
                continue
            res = analyzer.analyze(ctx)
            results.append(res)
        except Exception as exc:
            failed.append(AnalyzerError(analyzer=getattr(analyzer, "name", "unknown"), message=str(exc)))

    kg, graph_facts = build_knowledge_graph(profile, results, ctx.shared_state)

    # Emit discovery conflict facts if present
    if profile.has_schema_conflict:
        from fa_engine.model import EvidenceRef, Fact

        kinds = ", ".join(sorted({s.kind for s in profile.schema_sources}))
        first_src = profile.schema_sources[0]
        graph_facts.append(
            Fact.create(
                fact_id="DISC-SCHEMA-001",
                code="SCHEMA_SOURCE_CONFLICT",
                category="ARCHITECTURE",
                fact_type="structural",
                severity="HIGH",
                summary=f"Multiple competing database schema sources detected ({kinds}); authoritative schema source is ambiguous.",
                location=f"{first_src.path}:1",
                evidence=[
                    EvidenceRef(
                        kind="config",
                        level="L1",
                        derivation="manifest",
                        ref=f"{s.path}:1",
                        line=1,
                        excerpt=f"{s.kind} ({s.entities_count} definitions)",
                    )
                    for s in profile.schema_sources
                ],
            )
        )

    snapshot = build_snapshot_v2(
        profile=profile,
        focus=focus,
        analyzer_results=results,
        failed_analyzers=failed,
        kg=kg,
        extra_facts=graph_facts,
        shared_state=ctx.shared_state,
    )
    return snapshot, kg


def run_scan(
    root: Path | str,
    *,
    peers: list[Path | str] | None = None,
    focus: list[str] | None = None,
    extra_analyzers: list[Analyzer] | None = None,
    run_build: bool = False,
) -> dict[str, Any]:
    """Public seam returning deterministic Snapshot v2 dictionary."""
    snapshot, _ = run_scan_with_graph(
        root,
        peers=peers,
        focus=focus,
        extra_analyzers=extra_analyzers,
        run_build=run_build,
    )
    return snapshot


def _format_summary_markdown(snap: dict[str, Any]) -> str:
    radar = snap["readiness_radar"]
    disc = snap["discovery_metadata"]
    lines = [
        "# Feature Architect v2 — Deterministic System Intelligence Summary",
        "",
        f"- **Root:** `{snap['project_metadata']['root']}` · **Topology:** `{snap['project_metadata']['topology']}` · **Tenancy:** `{snap['project_metadata']['tenancy_model']}`",
        f"- **Verified Peers:** `{', '.join(disc['confirmed_peers']) or 'none'}`",
        f"- **Input Hash:** `{snap['input_hash']}`",
        "",
        "## 4-Axis Measured Readiness Radar",
        f"1. **Analysis Coverage:** `{radar['analysis_coverage_files']}` files scanned (`{radar['failed_analyzers_count']}` analyzer failures)",
        f"2. **Knowledge Graph Pipeline Integrity:** `{radar['pipeline_integrity_pct']}%` (`{snap['graph_summary']['unresolved_edges_count']}` unresolved edges)",
        f"3. **Confirmed Structural Risks:** CRITICAL={radar['confirmed_risks']['CRITICAL']} · HIGH={radar['confirmed_risks']['HIGH']} · MEDIUM={radar['confirmed_risks']['MEDIUM']}",
        f"4. **Inferred Risks (Needs L2/L3 Verification):** CRITICAL={radar['inferred_risks']['CRITICAL']} · HIGH={radar['inferred_risks']['HIGH']} · MEDIUM={radar['inferred_risks']['MEDIUM']} (Max Depth: `{radar['max_verification_level']}`)",
        "",
        f"## Top Structural & Contract Facts (`{len(snap['facts'])}` total)",
    ]
    for f in snap["facts"][:25]:
        lines.append(
            f"- **[{f['status']} · {f['severity']} · conf={f['confidence']}]** `{f['code']}` at `{f['location']}` — {f['summary']}"
        )
    if not snap["facts"]:
        lines.append("- Zero structural issues detected.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feature Architect v2 — Full-Stack Deterministic Scanner")
    parser.add_argument("--root", default=".", help="Target project root directory")
    parser.add_argument("--peer", action="append", default=[], help="Optional explicit peer repo path")
    parser.add_argument("--focus", default="", help="Comma-separated focus areas")
    parser.add_argument("--build", action="store_true", help="Run non-destructive temporary bundle check (L2)")
    parser.add_argument("--out-dir", default="", help="Optional directory to persist context-snapshot.json & knowledge-graph.json")
    parser.add_argument("--format", choices=["json", "md"], default="json", help="Stdout output format")
    args = parser.parse_args(argv)

    root_path = Path(args.root)
    if not root_path.is_dir():
        print(f"[ERROR] Root directory does not exist: {args.root}", file=sys.stderr)
        return 2
    for p in args.peer:
        if not Path(p).is_dir():
            print(f"[ERROR] Peer directory does not exist: {p}", file=sys.stderr)
            return 2

    focus_list = [f.strip() for f in args.focus.split(",") if f.strip()] if args.focus else None
    snapshot, kg = run_scan_with_graph(
        root_path,
        peers=args.peer or None,
        focus=focus_list,
        run_build=args.build,
    )

    if args.out_dir:
        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "context-snapshot.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out / "knowledge-graph.json").write_text(
            json.dumps(kg.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if args.format == "md":
        print(_format_summary_markdown(snapshot))
    else:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
