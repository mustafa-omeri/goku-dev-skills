# -*- coding: utf-8 -*-
"""Canonical data structures, confidence derivation, and deterministic hashing for `fa_engine`."""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SNAPSHOT_SCHEMA_VERSION = "feature-architect/snapshot@2"
KG_SCHEMA_VERSION = "feature-architect/knowledge-graph@2"
V1_GAP_SCHEMA_VERSION = "feature-architect/gap-scan@1"
ENGINE_VERSION = "2.0.0"

IGNORE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        "vendor",
        ".agent",
        ".agents",
        ".claude",
        ".windsurf",
        ".cursor",
        ".fa",
        "dist",
        "build",
        "target",
        "out",
        ".next",
        ".nuxt",
        "coverage",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
        "yedekler",
        "scout",
        "raporlar",
        "temps",
    }
)

HASHABLE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".vue",
        ".svelte",
        ".html",
        ".css",
        ".scss",
        ".java",
        ".kt",
        ".py",
        ".go",
        ".rs",
        ".cs",
        ".sql",
        ".prisma",
        ".graphql",
        ".gql",
        ".proto",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".xml",
        ".md",
    }
)


def normalize_api_path(path: str) -> str:
    """Normalize client and server API paths into a canonical comparable route pattern."""
    p = path.strip()
    p = re.sub(r"^https?://[^/]+", "", p)
    p = p.split("?")[0].split("#")[0]
    p = re.sub(r"^/api(?:/v\d+)?(?=/|$)", "", p)
    p = re.sub(r"^/v\d+(?=/|$)", "", p)
    p = re.sub(r"\$\{[^}]+\}", "{param}", p)
    p = re.sub(r"\{[^}:]+(?::[^}]+)?\}", "{param}", p)
    p = re.sub(r":([a-zA-Z0-9_]+)", "{param}", p)
    p = re.sub(r"<[^>]+>", "{param}", p)
    p = re.sub(r"/+", "/", p)
    p = "/" + p.strip("/")
    return p


def extract_api_version_prefix(path: str) -> str | None:
    """Return explicit version prefix such as '/api/v1' or '/v2' if present."""
    p = re.sub(r"^https?://[^/]+", "", path.strip())
    m = re.match(r"^((?:/api)?/v\d+)(?=/|$)", p)
    if m:
        return m.group(1)
    if p.startswith("/api/") or p == "/api":
        return "/api"
    return None


def derive_confidence_and_status(
    level: str,
    derivation: str,
    fact_type: str,
    requested_status: str = "CONFIRMED",
) -> tuple[str, int]:
    """Deterministically derive (status, confidence 0-100) from evidence strength.

    Rules:
      - Behavioral claims NEVER reach CONFIRMED without L3 runtime evidence.
      - Heuristic derivations NEVER reach CONFIRMED even for structural facts.
      - Structural facts backed by AST, OpenAPI, deterministic syntax, or config/manifest
        can reach CONFIRMED when requested_status == 'CONFIRMED'.
    """
    norm_level = level.upper()
    norm_deriv = derivation.lower()
    norm_type = fact_type.lower()
    req = requested_status.upper()

    if req == "UNKNOWN":
        return "UNKNOWN", 0

    if norm_level == "L3":
        return ("CONFIRMED" if req == "CONFIRMED" else req), 94

    if norm_type == "behavioral":
        if norm_level == "L2":
            return "INFERRED", 74
        if norm_deriv in {"ast", "openapi", "syntax", "config"}:
            return "INFERRED", 52
        return "INFERRED", 40

    # Structural facts
    if norm_deriv == "heuristic":
        return "INFERRED", 56

    if norm_level == "L2":
        conf = 90 if norm_deriv in {"openapi", "ast", "build", "test"} else 84
        return ("CONFIRMED" if req == "CONFIRMED" else "INFERRED"), conf

    # L1 structural with ast / openapi / syntax / config / manifest
    conf_map = {
        "openapi": 92,
        "ast": 88,
        "config": 88,
        "manifest": 88,
        "syntax": 84,
    }
    conf = conf_map.get(norm_deriv, 60)
    status = "CONFIRMED" if (req == "CONFIRMED" and conf >= 80) else "INFERRED"
    return status, conf


def iter_repo_files(root: Path, suffixes: set[str] | frozenset[str] | None = None):
    """Deterministically yield non-ignored files under `root`."""
    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d
            for d in dirnames
            if d not in IGNORE_DIRS and (not d.startswith(".") or d in {".github"})
        )
        # Skip generated council output directories inside target repos for determinism
        rel_dir = Path(dirpath).relative_to(root).as_posix().lower()
        if rel_dir.startswith("docs/plans/council") or rel_dir.startswith("docs/council"):
            dirnames[:] = []
            continue
        dp = Path(dirpath)
        for fname in sorted(filenames):
            p = dp / fname
            if suffixes is None or p.suffix.lower() in suffixes:
                yield p


def compute_input_hash(roots: list[Path]) -> str:
    """Compute a deterministic SHA-256 content digest across all scanned roots."""
    hasher = hashlib.sha256()
    for idx, r in enumerate(sorted({p.resolve() for p in roots}, key=lambda x: x.as_posix())):
        hasher.update(f"ROOT#{idx}\n".encode("utf-8"))
        for fpath in iter_repo_files(r, HASHABLE_EXTENSIONS):
            rel = fpath.relative_to(r).as_posix()
            hasher.update(rel.encode("utf-8"))
            hasher.update(b"\x00")
            try:
                raw = fpath.read_bytes()
            except OSError:
                raw = b"<unreadable>"
            # Normalize CRLF -> LF so hash is cross-platform deterministic
            hasher.update(raw.replace(b"\r\n", b"\n"))
            hasher.update(b"\n")
    return f"sha256:{hasher.hexdigest()}"


@dataclass(frozen=True)
class EvidenceRef:
    kind: str  # code | contract | config | test | runtime | doc
    level: str  # L1 | L2 | L3
    derivation: str  # ast | syntax | openapi | config | manifest | heuristic | runtime
    ref: str  # relative file:line or node id
    line: int = 1
    excerpt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "level": self.level,
            "derivation": self.derivation,
            "ref": self.ref,
            "line": self.line,
            "excerpt": self.excerpt,
        }


@dataclass
class Node:
    id: str  # e.g. Component:SummaryCard or Endpoint:GET:/api/v1/orders
    kind: str
    name: str
    file: str = ""
    line: int = 1
    root_label: str = "primary"
    attrs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "file": self.file,
            "line": self.line,
            "root_label": self.root_label,
            "attrs": dict(sorted(self.attrs.items())),
        }


@dataclass
class Edge:
    source: str
    target: str
    kind: str
    derivation: str = "syntax"
    evidence_ref: str = ""
    unresolved: bool = False
    attrs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "derivation": self.derivation,
            "evidence_ref": self.evidence_ref,
            "unresolved": self.unresolved,
            "attrs": dict(sorted(self.attrs.items())),
        }


@dataclass
class Fact:
    id: str
    code: str
    category: str
    fact_type: str  # structural | behavioral
    status: str  # CONFIRMED | INFERRED | UNKNOWN
    confidence: int
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    summary: str
    location: str
    evidence: list[EvidenceRef] = field(default_factory=list)
    attrs: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        fact_id: str,
        code: str,
        category: str,
        fact_type: str,
        severity: str,
        summary: str,
        location: str,
        evidence: list[EvidenceRef],
        requested_status: str = "CONFIRMED",
        attrs: dict[str, Any] | None = None,
    ) -> "Fact":
        if evidence:
            primary = evidence[0]
            status, conf = derive_confidence_and_status(
                primary.level, primary.derivation, fact_type, requested_status
            )
        else:
            status, conf = "UNKNOWN", 0
        return cls(
            id=fact_id,
            code=code,
            category=category,
            fact_type=fact_type,
            status=status,
            confidence=conf,
            severity=severity,
            summary=summary,
            location=location,
            evidence=evidence,
            attrs=attrs or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "code": self.code,
            "category": self.category,
            "fact_type": self.fact_type,
            "status": self.status,
            "confidence": self.confidence,
            "severity": self.severity,
            "summary": self.summary,
            "location": self.location,
            "evidence": [e.to_dict() for e in self.evidence],
            "attrs": dict(sorted(self.attrs.items())),
        }


@dataclass
class CoverageReport:
    scanned_files: int = 0
    excluded_dirs: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scanned_files": self.scanned_files,
            "excluded_dirs": self.excluded_dirs,
        }


@dataclass
class AnalyzerError:
    analyzer: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"analyzer": self.analyzer, "message": self.message}


@dataclass
class PeerCandidate:
    path: str
    status: str  # CONFIRMED | CANDIDATE_ASK_USER | REJECTED
    confidence: int
    overlap_ratio: float
    matched_paths: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "status": self.status,
            "confidence": self.confidence,
            "overlap_ratio": round(self.overlap_ratio, 4),
            "matched_paths": sorted(self.matched_paths),
            "signals": list(self.signals),
        }


@dataclass
class ContractSource:
    kind: str  # openapi_file | springdoc | nest_swagger | fastapi_openapi | graphql | proto
    path: str
    root_label: str
    confidence: int = 90

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "path": self.path,
            "root_label": self.root_label,
            "confidence": self.confidence,
        }


@dataclass
class SchemaSource:
    kind: str  # sql_migration | prisma | jpa | typeorm | drizzle | sqlalchemy
    path: str
    root_label: str
    entities_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "path": self.path,
            "root_label": self.root_label,
            "entities_count": self.entities_count,
        }


@dataclass
class ProjectProfile:
    root: Path
    explicit_peers: list[Path] = field(default_factory=list)
    peers: list[PeerCandidate] = field(default_factory=list)
    frontend_stacks: list[str] = field(default_factory=list)
    backend_stacks: list[str] = field(default_factory=list)
    contract_sources: list[ContractSource] = field(default_factory=list)
    schema_sources: list[SchemaSource] = field(default_factory=list)
    has_schema_conflict: bool = False
    tenancy_model: str = "unknown"
    topology: str = "unknown"
    proxy_ports: list[int] = field(default_factory=list)
    server_ports: dict[str, list[int]] = field(default_factory=dict)
    ts_compiler_path: str | None = None

    @property
    def confirmed_peer_paths(self) -> list[Path]:
        out: list[Path] = [p.resolve() for p in self.explicit_peers]
        seen = {p.as_posix() for p in out}
        for cand in self.peers:
            if cand.status == "CONFIRMED":
                rp = Path(cand.path).resolve()
                if rp.as_posix() not in seen:
                    seen.add(rp.as_posix())
                    out.append(rp)
        return out

    @property
    def all_active_roots(self) -> list[tuple[str, Path]]:
        roots: list[tuple[str, Path]] = [("primary", self.root.resolve())]
        for idx, peer in enumerate(self.confirmed_peer_paths, start=1):
            roots.append((f"peer_{idx}:{peer.name}", peer))
        return roots

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root.resolve().as_posix(),
            "explicit_peers": [p.resolve().as_posix() for p in self.explicit_peers],
            "confirmed_peers": [p.as_posix() for p in self.confirmed_peer_paths],
            "peer_candidates": [p.to_dict() for p in self.peers],
            "frontend_stacks": sorted(set(self.frontend_stacks)),
            "backend_stacks": sorted(set(self.backend_stacks)),
            "contract_sources": [c.to_dict() for c in self.contract_sources],
            "schema_sources": [s.to_dict() for s in self.schema_sources],
            "has_schema_conflict": self.has_schema_conflict,
            "tenancy_model": self.tenancy_model,
            "topology": self.topology,
            "proxy_ports": sorted(set(self.proxy_ports)),
            "ts_ast_available": bool(self.ts_compiler_path),
        }
