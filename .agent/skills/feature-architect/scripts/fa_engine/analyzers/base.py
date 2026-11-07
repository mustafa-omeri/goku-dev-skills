# -*- coding: utf-8 -*-
"""Base protocol and result containers for error-isolated deterministic analyzers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from ..model import CoverageReport, Edge, Fact, Node, ProjectProfile


@dataclass
class AnalyzerContext:
    profile: ProjectProfile
    shared_state: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyzerResult:
    analyzer: str
    version: str
    applicable: bool = True
    applicability_reason: str = "applicable"
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    facts: list[Fact] = field(default_factory=list)
    coverage: CoverageReport = field(default_factory=CoverageReport)
    limitations: list[str] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "analyzer": self.analyzer,
            "version": self.version,
            "applicable": self.applicable,
            "applicability_reason": self.applicability_reason,
            "scanned_files": self.coverage.scanned_files,
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "facts": len(self.facts),
            "limitations": list(self.limitations),
        }


class Analyzer(Protocol):
    name: str
    version: str

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]: ...

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult: ...
