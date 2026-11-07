# -*- coding: utf-8 -*-
"""Architecture Fitness & Technical Debt Analyzer (`fitness.py`).

Computes module-level coupling/instability, strongly connected import cycles (SCC),
architectural layer drift, and module test coverage edges.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..model import CoverageReport, Edge, EvidenceRef, Fact, Node, ProjectProfile, iter_repo_files
from .base import AnalyzerContext, AnalyzerResult

TS_IMPORT_RE = re.compile(r"\bfrom\s+[\"']([^\"']+)[\"']")
JAVA_PACKAGE_RE = re.compile(r"^\s*package\s+([A-Za-z0-9_.]+)\s*;", re.MULTILINE)
JAVA_IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_.]+)\s*;", re.MULTILINE)


def _infer_ts_module(rel: str) -> str | None:
    parts = rel.split("/")
    for idx, seg in enumerate(parts):
        if seg in {"modules", "features", "domains"} and idx + 1 < len(parts):
            return parts[idx + 1]
    return None


def _tarjan_scc(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    sccs: list[list[str]] = []

    def strongconnect(v: str) -> None:
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in sorted(graph.get(v, set())):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) >= 2:
                sccs.append(sorted(comp))

    for node in sorted(graph):
        if node not in indices:
            strongconnect(node)
    return sccs


class ArchitectureFitnessAnalyzer:
    name = "fitness"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        return True, "Module coupling, layer drift, and test topology apply to all codebases"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        nodes: list[Node] = []
        edges: list[Edge] = []
        facts: list[Fact] = []
        scanned = 0

        module_graph: dict[str, set[str]] = {}
        module_edge_evidence: dict[tuple[str, str], tuple[str, int, str]] = {}
        module_metrics: dict[str, dict[str, Any]] = {}

        for label, r in ctx.profile.all_active_roots:
            # 1. TS/JS module dependency graph + layer drift
            for fp in iter_repo_files(r, {".ts", ".tsx", ".js", ".jsx"}):
                scanned += 1
                rel = fp.relative_to(r).as_posix()
                txt = fp.read_text(encoding="utf-8", errors="replace")
                lines = txt.splitlines()

                is_test = ".test." in rel.lower() or ".spec." in rel.lower() or "/tests/" in f"/{rel.lower()}"
                src_mod = _infer_ts_module(rel)
                if src_mod:
                    module_graph.setdefault(src_mod, set())
                    nodes.append(Node(id=f"Module:{src_mod}", kind="Module", name=src_mod, file=rel, root_label=label))
                    if is_test:
                        nodes.append(Node(id=f"TestSuite:{rel}", kind="TestSuite", name=fp.name, file=rel, root_label=label))
                        edges.append(
                            Edge(
                                source=f"Module:{src_mod}",
                                target=f"TestSuite:{rel}",
                                kind="tested_by",
                                derivation="syntax",
                                evidence_ref=f"{rel}:1",
                            )
                        )

                if is_test:
                    continue

                for im in TS_IMPORT_RE.finditer(txt):
                    imp = im.group(1)
                    iline = txt[: im.start()].count("\n") + 1
                    excerpt = lines[iline - 1].strip()[:160] if iline - 1 < len(lines) else imp

                    # Layer drift: UI component directly importing server ORM / DB driver
                    if fp.suffix.lower() in {".tsx", ".jsx"} and imp in {
                        "@prisma/client",
                        "typeorm",
                        "pg",
                        "mysql2",
                        "mongoose",
                    }:
                        facts.append(
                            Fact.create(
                                fact_id=f"FIT-DRIFT-{len(facts)+1:03d}",
                                code="ARCHITECTURAL_LAYER_DRIFT",
                                category="ARCHITECTURE",
                                fact_type="structural",
                                severity="HIGH",
                                summary=f"UI component `{rel}:{iline}` directly imports database/ORM package `{imp}`.",
                                location=f"{rel}:{iline}",
                                evidence=[
                                    EvidenceRef(
                                        kind="code",
                                        level="L1",
                                        derivation="syntax",
                                        ref=f"{rel}:{iline}",
                                        line=iline,
                                        excerpt=excerpt,
                                    )
                                ],
                            )
                        )

                    if src_mod and imp.startswith("."):
                        resolved = (fp.parent / imp).resolve()
                        try:
                            target_rel = resolved.relative_to(r.resolve()).as_posix()
                        except ValueError:
                            continue
                        dst_mod = _infer_ts_module(target_rel)
                        if dst_mod and dst_mod != src_mod:
                            module_graph.setdefault(src_mod, set()).add(dst_mod)
                            module_graph.setdefault(dst_mod, set())
                            module_edge_evidence.setdefault((src_mod, dst_mod), (rel, iline, excerpt))
                            edges.append(
                                Edge(
                                    source=f"Module:{src_mod}",
                                    target=f"Module:{dst_mod}",
                                    kind="depends_on",
                                    derivation="syntax",
                                    evidence_ref=f"{rel}:{iline}",
                                )
                            )

            # 2. Java layer drift (Controller directly injecting Repository when @Service exists)
            has_services = any(
                "@Service" in jf.read_text(encoding="utf-8", errors="replace")
                for jf in iter_repo_files(r, {".java", ".kt"})
            )
            if has_services:
                for jf in iter_repo_files(r, {".java", ".kt"}):
                    scanned += 1
                    txt = jf.read_text(encoding="utf-8", errors="replace")
                    if not re.search(r"@(?:[A-Za-z_][A-Za-z0-9_]*\.)*(?:RestController|Controller)\b", txt):
                        continue
                    rel = jf.relative_to(r).as_posix()
                    rm = re.search(r"\bprivate\s+(?:final\s+)?([A-Z][A-Za-z0-9_]*Repository)\b", txt)
                    if rm:
                        rline = txt[: rm.start()].count("\n") + 1
                        lines = txt.splitlines()
                        facts.append(
                            Fact.create(
                                fact_id=f"FIT-DRIFT-{len(facts)+1:03d}",
                                code="ARCHITECTURAL_LAYER_DRIFT",
                                category="ARCHITECTURE",
                                fact_type="structural",
                                severity="MEDIUM",
                                summary=(
                                    f"Controller `{rel}:{rline}` bypasses the `@Service` layer and directly injects `{rm.group(1)}`."
                                ),
                                location=f"{rel}:{rline}",
                                evidence=[
                                    EvidenceRef(
                                        kind="code",
                                        level="L1",
                                        derivation="syntax",
                                        ref=f"{rel}:{rline}",
                                        line=rline,
                                        excerpt=lines[rline - 1].strip()[:160] if rline - 1 < len(lines) else rm.group(1),
                                    )
                                ],
                            )
                        )

        # Compute fan-in, fan-out, instability, and SCC cycles
        fan_in: dict[str, int] = {m: 0 for m in module_graph}
        for src_m, targets in module_graph.items():
            for dst_m in targets:
                fan_in[dst_m] = fan_in.get(dst_m, 0) + 1

        for mod_name in sorted(module_graph):
            ce = len(module_graph[mod_name])
            ca = fan_in.get(mod_name, 0)
            instability = round(ce / (ca + ce), 3) if (ca + ce) > 0 else 0.0
            module_metrics[mod_name] = {"fan_in": ca, "fan_out": ce, "instability": instability}

        for cycle in _tarjan_scc(module_graph):
            ev_list: list[EvidenceRef] = []
            first_loc = "module-graph:1"
            for i in range(len(cycle)):
                pair = (cycle[i], cycle[(i + 1) % len(cycle)])
                if pair in module_edge_evidence:
                    erel, eline, eexc = module_edge_evidence[pair]
                    if first_loc == "module-graph:1":
                        first_loc = f"{erel}:{eline}"
                    ev_list.append(
                        EvidenceRef(
                            kind="code",
                            level="L1",
                            derivation="syntax",
                            ref=f"{erel}:{eline}",
                            line=eline,
                            excerpt=eexc,
                        )
                    )
            if not ev_list and module_edge_evidence:
                erel, eline, eexc = next(iter(module_edge_evidence.values()))
                first_loc = f"{erel}:{eline}"
                ev_list.append(
                    EvidenceRef(kind="code", level="L1", derivation="syntax", ref=first_loc, line=eline, excerpt=eexc)
                )

            facts.append(
                Fact.create(
                    fact_id=f"FIT-CYCLE-{len(facts)+1:03d}",
                    code="CIRCULAR_MODULE_DEPENDENCY",
                    category="ARCHITECTURE",
                    fact_type="structural",
                    severity="HIGH",
                    summary=f"Circular dependency cycle detected across modules: `{' <-> '.join(cycle)}`.",
                    location=first_loc,
                    evidence=ev_list,
                    attrs={"cycle": cycle},
                )
            )

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason="Module fitness evaluated",
            nodes=nodes,
            edges=edges,
            facts=facts,
            coverage=CoverageReport(scanned_files=scanned),
            artifacts={"module_metrics": module_metrics},
        )
