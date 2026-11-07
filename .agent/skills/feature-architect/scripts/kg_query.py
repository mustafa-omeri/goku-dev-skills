#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canonical Knowledge Graph Query CLI (`kg_query.py`).

Provides deterministic queries over `knowledge-graph.json` (or live `--root`):
  - `trace --from <NodeId> [--depth N]`
  - `unresolved [--kind k1,k2]`
  - `consumers <NodeId> [--depth N]`
  - `impact <NodeId> [--depth N]`
  - `role-surface <RoleName>`
  - `summary`
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

from fa_engine.graph import KnowledgeGraph  # noqa: E402
from fa_engine.model import Edge, Node  # noqa: E402


def load_kg_from_file(path: Path) -> KnowledgeGraph:
    raw = json.loads(path.read_text(encoding="utf-8"))
    kg = KnowledgeGraph()
    for n in raw.get("nodes", []):
        kg.add_node(
            Node(
                id=n["id"],
                kind=n["kind"],
                name=n["name"],
                file=n.get("file", ""),
                line=int(n.get("line", 1)),
                root_label=n.get("root_label", "primary"),
                attrs=dict(n.get("attrs") or {}),
            )
        )
    for e in raw.get("edges", []):
        kg.add_edge(
            Edge(
                source=e["source"],
                target=e["target"],
                kind=e["kind"],
                derivation=e.get("derivation", "syntax"),
                evidence_ref=e.get("evidence_ref", ""),
                unresolved=bool(e.get("unresolved", False)),
                attrs=dict(e.get("attrs") or {}),
            )
        )
    return kg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feature Architect v2 — Canonical Knowledge Graph Query CLI")
    parser.add_argument("--kg", default="", help="Path to persisted knowledge-graph.json")
    parser.add_argument("--root", default="", help="Optional project root to build KG on the fly if --kg is omitted")

    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_trace = sub.add_parser("trace", help="Trace outgoing causal chain from a node")
    p_trace.add_argument("--from", dest="start_node", required=True, help="Starting node ID (e.g. Hook:useMetrics)")
    p_trace.add_argument("--depth", type=int, default=6)

    p_unres = sub.add_parser("unresolved", help="List unresolved broken edges in the Knowledge Graph")
    p_unres.add_argument("--kind", default="", help="Comma-separated edge kinds (e.g. handled_by,navigates_to)")

    p_cons = sub.add_parser("consumers", help="List upstream consumers of an endpoint, hook, or entity")
    p_cons.add_argument("target_node", help="Target node ID")
    p_cons.add_argument("--depth", type=int, default=4)

    p_imp = sub.add_parser("impact", help="Compute upstream & downstream blast radius for a node")
    p_imp.add_argument("node_id", help="Node ID to evaluate")
    p_imp.add_argument("--depth", type=int, default=3)

    p_role = sub.add_parser("role-surface", help="Inspect UI visibility and endpoint authorization for a role")
    p_role.add_argument("role_name", help="Role identifier (e.g. ADMIN, ORG_MANAGER)")

    sub.add_parser("summary", help="Emit Knowledge Graph node/edge integrity summary")

    args = parser.parse_args(argv)

    if args.kg:
        kg_file = Path(args.kg)
        if not kg_file.is_file():
            print(f"[ERROR] Knowledge Graph file not found: {args.kg}", file=sys.stderr)
            return 2
        kg = load_kg_from_file(kg_file)
    elif args.root:
        root_dir = Path(args.root)
        if not root_dir.is_dir():
            print(f"[ERROR] Root directory not found: {args.root}", file=sys.stderr)
            return 2
        from fa_scan import run_scan_with_graph

        _, kg = run_scan_with_graph(root_dir)
    else:
        print("[ERROR] Either --kg <knowledge-graph.json> or --root <project-dir> is required.", file=sys.stderr)
        return 2

    payload: dict[str, Any]
    if args.subcommand == "trace":
        payload = kg.trace(args.start_node, max_depth=args.depth)
    elif args.subcommand == "unresolved":
        kinds = {k.strip() for k in args.kind.split(",") if k.strip()} if args.kind else None
        unres = kg.unresolved_edges(kind_filter=kinds)
        payload = {"count": len(unres), "unresolved": unres}
    elif args.subcommand == "consumers":
        cons = kg.consumers(args.target_node, max_depth=args.depth)
        payload = {"target": args.target_node, "count": len(cons), "consumers": cons}
    elif args.subcommand == "impact":
        payload = kg.impact(args.node_id, max_depth=args.depth)
    elif args.subcommand == "role-surface":
        payload = kg.role_surface(args.role_name)
    else:
        payload = kg.integrity_summary()

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
