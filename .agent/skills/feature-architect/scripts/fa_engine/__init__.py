# -*- coding: utf-8 -*-
"""Feature Architect v2 deterministic analysis engine (`fa_engine`)."""

from .model import (
    KG_SCHEMA_VERSION,
    SNAPSHOT_SCHEMA_VERSION,
    V1_GAP_SCHEMA_VERSION,
    AnalyzerError,
    ContractSource,
    CoverageReport,
    Edge,
    EvidenceRef,
    Fact,
    Node,
    PeerCandidate,
    ProjectProfile,
    SchemaSource,
    compute_input_hash,
    derive_confidence_and_status,
    normalize_api_path,
)

__all__ = [
    "KG_SCHEMA_VERSION",
    "SNAPSHOT_SCHEMA_VERSION",
    "V1_GAP_SCHEMA_VERSION",
    "AnalyzerError",
    "ContractSource",
    "CoverageReport",
    "Edge",
    "EvidenceRef",
    "Fact",
    "Node",
    "PeerCandidate",
    "ProjectProfile",
    "SchemaSource",
    "compute_input_hash",
    "derive_confidence_and_status",
    "normalize_api_path",
]
