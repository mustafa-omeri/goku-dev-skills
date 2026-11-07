#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect v2 — Context-Aware Review Unit Partitioner & Hat Activation (`review_units.py`).

Partitions the Canonical Knowledge Graph (`knowledge-graph.json`) into logical review units
(by route/module/journey) and computes Round 0 specialist hat activation (`lead`, `support`, `skip`)
so hats only review units relevant to their domain and authority boundary.
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


ALL_HATS = (
    "snr-product-owner",
    "snr-software-architect",
    "principal-ui-ux-specialist",
    "snr-seo-specialist",
    "snr-growth-marketing",
    "snr-qa-security-auditor",
)


def partition(kg_data: dict[str, Any], *, is_public_surface: bool = False) -> list[dict[str, Any]]:
    """Partition Knowledge Graph nodes into logical review units with Round 0 hat activations."""
    nodes = kg_data.get("nodes", []) if isinstance(kg_data, dict) else []
    edges = kg_data.get("edges", []) if isinstance(kg_data, dict) else []

    routes = [n for n in nodes if isinstance(n, dict) and n.get("kind") == "Route"]
    units: list[dict[str, Any]] = []

    if not routes:
        # Backend-only / CLI / library fallback unit
        units.append(
            {
                "unit_id": "unit:core-system",
                "title": "Core System & Service Architecture",
                "surface": "public" if is_public_surface else "internal",
                "node_ids": [str(n.get("id")) for n in nodes if isinstance(n, dict) and n.get("id")],
                "hat_activation": {
                    "snr-product-owner": "lead",
                    "snr-software-architect": "lead",
                    "principal-ui-ux-specialist": "support" if any(n.get("kind") == "Component" for n in nodes) else "skip",
                    "snr-seo-specialist": "lead" if is_public_surface else "skip",
                    "snr-growth-marketing": "support" if is_public_surface else "skip",
                    "snr-qa-security-auditor": "lead",
                },
            }
        )
        return units

    adj: dict[str, list[str]] = {}
    for e in edges:
        if isinstance(e, dict):
            s = str(e.get("source", ""))
            t = str(e.get("target", ""))
            if s and t:
                adj.setdefault(s, []).append(t)

    for r in routes:
        rid = str(r.get("id", ""))
        rname = str(r.get("name", rid))
        is_pub = is_public_surface or any(
            k in rname.lower() for k in ("landing", "login", "register", "public", "pricing", "blog")
        )
        # Collect 2-hop neighborhood
        unit_nodes = {rid}
        for n1 in adj.get(rid, []):
            unit_nodes.add(n1)
            for n2 in adj.get(n1, []):
                unit_nodes.add(n2)

        units.append(
            {
                "unit_id": f"unit:{rname}",
                "title": f"Route Journey {rname}",
                "surface": "public" if is_pub else "authenticated",
                "node_ids": sorted(unit_nodes),
                "hat_activation": {
                    "snr-product-owner": "lead",
                    "snr-software-architect": "lead",
                    "principal-ui-ux-specialist": "lead",
                    "snr-seo-specialist": "lead" if is_pub else "skip",
                    "snr-growth-marketing": "lead" if is_pub else "support",
                    "snr-qa-security-auditor": "lead",
                },
            }
        )

    return units


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feature Architect v2 — Review Unit Partitioner")
    parser.add_argument("--kg", required=True, help="Path to knowledge-graph.json")
    parser.add_argument("--public", action="store_true", help="Treat root surface as public web")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    kg_path = Path(args.kg)
    if not kg_path.is_file():
        print(f"[ERROR] Knowledge graph file not found: {kg_path}", file=sys.stderr)
        return 1

    kg_data = json.loads(kg_path.read_text(encoding="utf-8"))
    units = partition(kg_data, is_public_surface=args.public)
    out = json.dumps({"schema": "feature-architect/review-units@1", "units": units}, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
