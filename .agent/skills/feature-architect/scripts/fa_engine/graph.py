# -*- coding: utf-8 -*-
"""Canonical Project Knowledge Graph builder and deterministic query engine (`graph.py`)."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .analyzers.base import AnalyzerResult
from .model import KG_SCHEMA_VERSION, Edge, EvidenceRef, Fact, Node, ProjectProfile


@dataclass
class KnowledgeGraph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    _adj: dict[str, list[Edge]] = field(default_factory=dict)
    _rev_adj: dict[str, list[Edge]] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        if node.id not in self.nodes:
            self.nodes[node.id] = node
        else:
            existing = self.nodes[node.id]
            merged_attrs = {**existing.attrs, **node.attrs}
            existing.attrs = merged_attrs
            if not existing.file and node.file:
                existing.file = node.file
                existing.line = node.line

    def add_edge(self, edge: Edge) -> None:
        key = (edge.source, edge.target, edge.kind, edge.unresolved)
        for ex in self.edges:
            if (ex.source, ex.target, ex.kind, ex.unresolved) == key:
                return
        self.edges.append(edge)
        self._adj.setdefault(edge.source, []).append(edge)
        self._rev_adj.setdefault(edge.target, []).append(edge)

    def trace(self, start_id: str, max_depth: int = 6) -> dict[str, Any]:
        """Trace forward outgoing causal chain from `start_id`."""
        visited: set[str] = set()
        steps: list[dict[str, Any]] = []
        queue: deque[tuple[str, int]] = deque([(start_id, 0)])

        while queue:
            curr, depth = queue.popleft()
            if curr in visited or depth >= max_depth:
                continue
            visited.add(curr)
            for edge in self._adj.get(curr, []):
                steps.append(
                    {
                        "depth": depth + 1,
                        "from": edge.source,
                        "kind": edge.kind,
                        "to": edge.target,
                        "unresolved": edge.unresolved,
                        "derivation": edge.derivation,
                        "evidence_ref": edge.evidence_ref,
                    }
                )
                if not edge.unresolved:
                    queue.append((edge.target, depth + 1))

        return {
            "start": start_id,
            "exists": start_id in self.nodes,
            "steps": steps,
            "has_unresolved": any(s["unresolved"] for s in steps),
        }

    def unresolved_edges(self, kind_filter: set[str] | None = None) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for e in self.edges:
            if not e.unresolved:
                continue
            if kind_filter and e.kind not in kind_filter:
                continue
            out.append(e.to_dict())
        return sorted(out, key=lambda x: (x["kind"], x["source"], x["target"]))

    def consumers(self, target_id: str, max_depth: int = 4) -> list[dict[str, Any]]:
        """Find upstream callers/screens/hooks consuming `target_id`."""
        visited: set[str] = set()
        found: list[dict[str, Any]] = []
        queue: deque[tuple[str, int]] = deque([(target_id, 0)])
        while queue:
            curr, depth = queue.popleft()
            if curr in visited or depth >= max_depth:
                continue
            visited.add(curr)
            for edge in self._rev_adj.get(curr, []):
                src_node = self.nodes.get(edge.source)
                found.append(
                    {
                        "distance": depth + 1,
                        "consumer": edge.source,
                        "consumer_kind": src_node.kind if src_node else "Unknown",
                        "via": edge.kind,
                        "target": curr,
                        "evidence_ref": edge.evidence_ref,
                    }
                )
                queue.append((edge.source, depth + 1))
        return found

    def impact(self, node_id: str, max_depth: int = 3) -> dict[str, Any]:
        """Compute both upstream consumers and downstream dependencies affected by `node_id`."""
        upstream = self.consumers(node_id, max_depth=max_depth)
        downstream = self.trace(node_id, max_depth=max_depth)["steps"]
        affected_ids = sorted(
            {u["consumer"] for u in upstream}
            | {d["to"] for d in downstream if not d["unresolved"]}
        )
        return {
            "node": node_id,
            "affected_count": len(affected_ids),
            "affected_nodes": affected_ids,
            "upstream": upstream,
            "downstream": downstream,
        }

    def role_surface(self, role_name: str) -> dict[str, Any]:
        """Return components visible to `role_name` and endpoints guarded for/against `role_name`."""
        norm = role_name.removeprefix("ROLE_")
        visible_ui: list[str] = []
        allowed_eps: list[str] = []
        blocked_eps: list[str] = []
        for nid, node in sorted(self.nodes.items()):
            if node.kind in {"Screen", "Component"}:
                vroles = node.attrs.get("visible_roles") or []
                if not vroles or norm in vroles:
                    visible_ui.append(nid)
            elif node.kind == "Endpoint":
                aroles = node.attrs.get("allowed_roles") or []
                if not aroles or norm in aroles:
                    allowed_eps.append(nid)
                else:
                    blocked_eps.append(nid)
        return {
            "role": norm,
            "visible_ui": visible_ui,
            "allowed_endpoints": allowed_eps,
            "blocked_endpoints": blocked_eps,
        }

    def integrity_summary(self) -> dict[str, Any]:
        total_edges = len(self.edges)
        unresolved_count = sum(1 for e in self.edges if e.unresolved)
        resolved_ratio = ((total_edges - unresolved_count) / total_edges * 100.0) if total_edges else 100.0
        return {
            "nodes_count": len(self.nodes),
            "edges_count": total_edges,
            "unresolved_edges_count": unresolved_count,
            "pipeline_integrity_pct": round(resolved_ratio, 2),
        }

    def to_dict(self) -> dict[str, Any]:
        sorted_nodes = [self.nodes[k].to_dict() for k in sorted(self.nodes)]
        sorted_edges = sorted(
            (e.to_dict() for e in self.edges),
            key=lambda x: (x["source"], x["kind"], x["target"], x["unresolved"]),
        )
        return {
            "schema_version": KG_SCHEMA_VERSION,
            "summary": self.integrity_summary(),
            "nodes": sorted_nodes,
            "edges": sorted_edges,
        }


def build_knowledge_graph(
    profile: ProjectProfile,
    results: list[AnalyzerResult],
    shared_state: dict[str, Any],
) -> tuple[KnowledgeGraph, list[Fact]]:
    """Consolidate analyzer nodes/edges and reconcile cross-layer `HttpCall -> Endpoint` edges."""
    kg = KnowledgeGraph()
    graph_facts: list[Fact] = []

    for res in results:
        for n in res.nodes:
            kg.add_node(n)
        for e in res.edges:
            kg.add_edge(e)

    fe_state = shared_state.get("frontend", {})
    be_state = shared_state.get("backend", {})
    http_calls: list[dict[str, Any]] = fe_state.get("http_calls", [])
    endpoints: list[dict[str, Any]] = be_state.get("endpoints", [])

    # Index backend endpoints by (method, normalized_path) and normalized_path
    by_method_and_path: dict[tuple[str, str], list[dict[str, Any]]] = {}
    by_norm_path: dict[str, list[dict[str, Any]]] = {}
    for ep in endpoints:
        by_method_and_path.setdefault((ep["method"], ep["normalized_path"]), []).append(ep)
        by_norm_path.setdefault(ep["normalized_path"], []).append(ep)

    has_backend_context = bool(profile.backend_stacks or endpoints)

    for call in http_calls:
        key = (call["method"], call["normalized_path"])
        exact = by_method_and_path.get(key, [])
        same_path_other_verb = by_norm_path.get(call["normalized_path"], [])

        if exact:
            for ep in exact:
                kg.add_edge(
                    Edge(
                        source=call["id"],
                        target=ep["id"],
                        kind="handled_by",
                        derivation="syntax",
                        evidence_ref=f"{call['file']}:{call['line']}",
                        unresolved=False,
                    )
                )
        elif has_backend_context:
            reason = "http_method_mismatch" if same_path_other_verb else "missing_backend_handler"
            expected_target = f"Endpoint:{call['method']}:{call['raw_path']}"
            kg.add_edge(
                Edge(
                    source=call["id"],
                    target=expected_target,
                    kind="handled_by",
                    derivation="syntax",
                    evidence_ref=f"{call['file']}:{call['line']}",
                    unresolved=True,
                    attrs={"reason": reason},
                )
            )
            graph_facts.append(
                Fact.create(
                    fact_id=f"KG-PIPE-{len(graph_facts)+1:03d}",
                    code="BROKEN_DATA_PIPELINE",
                    category="ARCHITECTURE",
                    fact_type="structural",
                    severity="HIGH",
                    summary=(
                        f"Client HTTP call `{call['method']} {call['raw_path']}` at `{call['file']}:{call['line']}` "
                        f"has no matching backend handler ({reason})."
                    ),
                    location=f"{call['file']}:{call['line']}",
                    evidence=[
                        EvidenceRef(
                            kind="code",
                            level="L1",
                            derivation="syntax",
                            ref=f"{call['file']}:{call['line']}",
                            line=call["line"],
                            excerpt=call.get("excerpt", f"{call['method']} {call['raw_path']}"),
                        )
                    ],
                    attrs={
                        "method": call["method"],
                        "path": call["raw_path"],
                        "reason": reason,
                        "same_path_methods": sorted({e["method"] for e in same_path_other_verb}),
                    },
                )
            )

    return kg, graph_facts
