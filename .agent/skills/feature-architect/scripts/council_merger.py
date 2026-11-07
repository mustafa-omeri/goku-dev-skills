#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect — Six-Hat Council Synthesizer & Zero-Drop Gate (`council_merger.py`).

Validates individual specialist hat JSON reports against `council-contract.schema.json`,
enforces V1-V8 Evidence Governance & Anti-Slop gates, resolves Round 2 Challenge Round
cross-examinations, assigns 6-Verb Decisions (`CONNECT | FIX | REFACTOR | COMPLETE | REMOVE | DEFER`),
computes equal/custom-weighted maturity scores (with N/A exclusion, weakest-link
reporting, 4-Axis Readiness Radar, and CRITICAL cap at 60), clusters multi-hat synergy targets,
flags cross-hat trade-off / conflict candidates, ranks Beyond-PRD features via RICE,
and verifies consolidated Markdown reports against silent CRITICAL/HIGH drops.

Exit codes:
  0 — Validated & merged (or `--check-report` passed with zero dropped IDs)
  1 — Schema / input validation error
  2 — Zero-Drop gate violation (`--check-report` detected missing CRITICAL/HIGH IDs)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCHEMA_VERSION = "feature-architect/council-merge@2"

VALID_AGENTS = {
    "snr-product-owner",
    "snr-software-architect",
    "principal-ui-ux-specialist",
    "snr-seo-specialist",
    "snr-growth-marketing",
    "snr-qa-security-auditor",
}

AGENT_SHORT_WEIGHT_KEYS = {
    "po": "snr-product-owner",
    "arch": "snr-software-architect",
    "ux": "principal-ui-ux-specialist",
    "seo": "snr-seo-specialist",
    "grw": "snr-growth-marketing",
    "qa": "snr-qa-security-auditor",
}

AGENT_CONTRACT_MAP: dict[str, dict[str, str]] = {
    "snr-product-owner": {
        "prefix": "PO",
        "canonical_role": "Senior Product Owner & Domain Strategist",
    },
    "snr-software-architect": {
        "prefix": "ARCH",
        "canonical_role": "Senior Software Architect & Systems Engineer",
    },
    "principal-ui-ux-specialist": {
        "prefix": "UX",
        "canonical_role": "Principal UI/UX & Design Systems Specialist",
    },
    "snr-seo-specialist": {
        "prefix": "SEO",
        "canonical_role": "Senior Technical SEO & Web Performance Specialist",
    },
    "snr-growth-marketing": {
        "prefix": "GRW",
        "canonical_role": "Senior Growth & Product Marketing Specialist",
    },
    "snr-qa-security-auditor": {
        "prefix": "QA",
        "canonical_role": "Senior QA, Security & 5-Layer TDD Auditor",
    },
}

VALID_CATEGORIES = {
    "STUB_PAGE",
    "BROKEN_ROUTE",
    "ORPHAN_API_DB",
    "CORE_MODULE_GAP",
    "ARCHITECTURE",
    "UI_UX",
    "PRODUCT",
    "PERFORMANCE",
    "SEO",
    "GROWTH",
    "SECURITY",
    "QA",
}

VALID_DECISIONS = {
    "CONNECT",
    "FIX",
    "REFACTOR",
    "COMPLETE",
    "REMOVE",
    "DEFER",
    "INVESTIGATE",
}

SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SEVERITY_RANK = {name: idx for idx, name in enumerate(SEVERITY_ORDER)}
EFFORT_POINTS = {"S": 1, "M": 2, "L": 3, "XL": 5}
VALID_CONFIDENCE_NUMS = {0.5, 0.8, 1.0}
FINDING_ID_RE = re.compile(r"^(PO|ARCH|UX|SEO|GRW|QA)-[0-9]{2,}$")
FEATURE_ID_RE = re.compile(r"^FEAT-(PO|ARCH|UX|SEO|GRW|QA)-[0-9]+$")
LINE_SUFFIX_RE = re.compile(r":\d+(?:-\d+)?$")

GENERIC_CONSTRAINT_RE = re.compile(
    r"(?:tüm yeni sayfalar.*rbac.*mobil uyumlu|"
    r"^(?:follow best practices|ensure good ux|use scalable architecture|maintain security|write clean code)\.?$)",
    re.IGNORECASE,
)

PO_TECH_ARCH_RE = re.compile(
    r"(?:entity/migration|\b(?:GET|POST|PUT|DELETE|PATCH)\s*/api/|\b[a-z0-9_-]+\.service\.ts\b|"
    r"\bCREATE\s+TABLE\b|@PreAuthorize|\bRepository\b)",
    re.IGNORECASE,
)

PO_VISUAL_THEME_RE = re.compile(
    r"(?:living surface|mavi kart|blue card|#[0-9a-f]{3,6}\b|border-radius|box-shadow)",
    re.IGNORECASE,
)

ARCH_SEAM_KEYWORDS_RE = re.compile(
    r"(?:controller|service|repository|endpoint|contract|dto|migration|router|seam|chunk|bundle|query|isolation)",
    re.IGNORECASE,
)

FABRICATED_METRIC_CLAIM_RE = re.compile(
    r"(?:%[0-9]{1,3}\s*(?:artırır|azaltır|düşürür|yükseltir|iyileştirir|hızlandırır)|"
    r"\b(?:increases?|boosts?|improves?|reduces?)\b[^.]{0,40}\bby\s+[0-9]{1,3}%)",
    re.IGNORECASE,
)

TELEMETRY_PROOF_RE = re.compile(
    r"(?:telemetry_ref:|measured_baseline:|benchmark_evidence:|telemetri_kanıtı:)",
    re.IGNORECASE,
)

SEO_PROTECTED_ROUTE_RE = re.compile(
    r"(?:/main(?:/|\b)|/admin(?:/|\b)|/dashboard(?:/|\b)|/settings(?:/|\b)|protected\s+route)",
    re.IGNORECASE,
)

SEO_INDEX_PROPOSAL_RE = re.compile(
    r"(?:sitemap\.xml|\bindex\s*,\s*follow\b|indexed\s+in\s+google|google'a\s+indeks)",
    re.IGNORECASE,
)

QA_CLIENT_ONLY_SECURITY_RE = re.compile(
    r"(?:istemci\s+tarafı\s+rate-?limit|client-?side(?:\s+only)?\s+rate\s*limit|"
    r"istemci\s+tarafı\s+geçici\s+kilitlenme)",
    re.IGNORECASE,
)

QA_SERVER_ENFORCEMENT_RE = re.compile(
    r"(?:server-?side|backend|sunucu\s+tarafı|@PreAuthorize|middleware|filter\s+chain)",
    re.IGNORECASE,
)

STOPWORDS = {
    "page", "route", "screen", "component", "view", "renders", "lacks", "missing",
    "without", "with", "from", "into", "that", "this", "user", "users", "main",
    "src", "pages", "features", "components", "tsx", "ts", "jsx", "js", "java",
}

SKIP_JSON_FILENAMES = {
    "context-snapshot.json",
    "engine-advice.json",
    "merged.json",
    "project-knowledge-graph.json",
    "reconciliation-matrix.json",
    "challenges.json",
}


def _is_int(val: Any) -> bool:
    return isinstance(val, int) and not isinstance(val, bool)


def _normalize_location(loc: str) -> str:
    cleaned = loc.strip().replace("\\", "/")
    cleaned = LINE_SUFFIX_RE.sub("", cleaned)
    return cleaned


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


def _extract_topic_tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9_]{4,}", text.lower())
    return {w for w in words if w not in STOPWORDS and not w.isdigit()}


def validate_report(obj: Any) -> list[str]:
    """Validate a single specialist hat report dict; returns list of human-readable errors."""
    if not isinstance(obj, dict):
        return ["Report root must be a JSON object."]

    errors: list[str] = []
    required_top = (
        "agent_id",
        "role",
        "health_score",
        "audits",
        "ui_ux_mismatches",
        "new_features",
        "non_negotiable_constraints",
    )
    for key in required_top:
        if key not in obj:
            errors.append(f"Missing required field '{key}'.")

    agent_id = obj.get("agent_id")
    if agent_id is not None and (not isinstance(agent_id, str) or not agent_id.strip()):
        errors.append("'agent_id' must be a non-empty string.")
    elif isinstance(agent_id, str) and agent_id not in VALID_AGENTS:
        errors.append(f"'agent_id'={agent_id!r} must be one of {sorted(VALID_AGENTS)}.")

    role = obj.get("role")
    if role is not None and (not isinstance(role, str) or len(role.strip()) < 2):
        errors.append("'role' must be a string of length >= 2.")

    applicability = obj.get("applicability", "applicable")
    if applicability not in ("applicable", "not_applicable"):
        errors.append("'applicability' must be 'applicable' or 'not_applicable'.")

    if applicability == "not_applicable":
        reason = obj.get("not_applicable_reason", "")
        if not isinstance(reason, str) or len(reason.strip()) < 10:
            errors.append("'not_applicable_reason' (min 10 chars) is required when applicability is 'not_applicable'.")
        score = obj.get("health_score")
        if score is not None:
            errors.append("'health_score' must be null when applicability is 'not_applicable'.")
        for empty_key in ("audits", "ui_ux_mismatches", "new_features"):
            arr = obj.get(empty_key)
            if isinstance(arr, list) and len(arr) > 0:
                errors.append(f"'{empty_key}' must be empty when applicability is 'not_applicable'.")
    else:
        score = obj.get("health_score")
        if not _is_int(score) or not (0 <= score <= 100):
            errors.append("'health_score' must be an integer between 0 and 100 when applicable.")
        if "health_score_rationale" in obj:
            rationale = obj.get("health_score_rationale")
            if not isinstance(rationale, str) or len(rationale.strip()) < 20:
                errors.append("'health_score_rationale' must be a string of at least 20 characters when applicable.")

    expected_prefix = (
        AGENT_CONTRACT_MAP[agent_id]["prefix"]
        if isinstance(agent_id, str) and agent_id in AGENT_CONTRACT_MAP
        else None
    )

    audits = obj.get("audits")
    if audits is not None:
        if not isinstance(audits, list):
            errors.append("'audits' must be a list.")
        else:
            seen_ids: set[str] = set()
            for idx, item in enumerate(audits):
                prefix = f"audits[{idx}]"
                if not isinstance(item, dict):
                    errors.append(f"{prefix} must be an object.")
                    continue
                for req in ("id", "category", "severity", "location", "evidence", "confidence", "issue", "fix_proposal"):
                    val = item.get(req)
                    if not isinstance(val, str) or not val.strip():
                        errors.append(f"{prefix}.{req} must be a non-empty string.")
                fid = item.get("id")
                if isinstance(fid, str) and fid.strip():
                    if not FINDING_ID_RE.match(fid):
                        errors.append(f"{prefix}.id={fid!r} must match ^(PO|ARCH|UX|SEO|GRW|QA)-[0-9]{{2,}}$.")
                    elif expected_prefix is not None and not fid.startswith(f"{expected_prefix}-"):
                        errors.append(
                            f"{prefix}.id={fid!r} must use prefix '{expected_prefix}-' for agent_id={agent_id!r}."
                        )
                    if fid in seen_ids:
                        errors.append(f"{prefix}.id={fid!r} is duplicated within report.")
                    seen_ids.add(fid)
                cat = item.get("category")
                if isinstance(cat, str) and cat not in VALID_CATEGORIES:
                    errors.append(f"{prefix}.category={cat!r} invalid.")
                sev = item.get("severity")
                if isinstance(sev, str) and sev not in SEVERITY_RANK:
                    errors.append(f"{prefix}.severity={sev!r} must be CRITICAL|HIGH|MEDIUM|LOW.")
                conf = item.get("confidence")
                if isinstance(conf, str) and conf not in ("verified", "candidate"):
                    errors.append(f"{prefix}.confidence={conf!r} must be verified|candidate.")
                dec = item.get("decision")
                if dec is not None and (not isinstance(dec, str) or dec not in VALID_DECISIONS):
                    errors.append(f"{prefix}.decision={dec!r} must be one of {sorted(VALID_DECISIONS)}.")

    mismatches = obj.get("ui_ux_mismatches")
    if mismatches is not None:
        if not isinstance(mismatches, list):
            errors.append("'ui_ux_mismatches' must be a list.")
        else:
            for idx, mm in enumerate(mismatches):
                prefix = f"ui_ux_mismatches[{idx}]"
                if not isinstance(mm, dict):
                    errors.append(f"{prefix} must be an object.")
                    continue
                for req in ("screen_or_component", "theme_reference_gap", "ux_impact", "correction"):
                    val = mm.get(req)
                    if not isinstance(val, str) or not val.strip():
                        errors.append(f"{prefix}.{req} must be a non-empty string.")

    features = obj.get("new_features")
    if features is not None:
        if not isinstance(features, list):
            errors.append("'new_features' must be a list.")
        else:
            for idx, feat in enumerate(features):
                prefix = f"new_features[{idx}]"
                if not isinstance(feat, dict):
                    errors.append(f"{prefix} must be an object.")
                    continue
                for req_s in ("feature_id", "title", "rationale", "user_value", "effort", "five_layer_slice_summary"):
                    val = feat.get(req_s)
                    if not isinstance(val, str) or not val.strip():
                        errors.append(f"{prefix}.{req_s} must be a non-empty string.")
                feat_id = feat.get("feature_id")
                if isinstance(feat_id, str) and feat_id.strip():
                    if not FEATURE_ID_RE.match(feat_id):
                        errors.append(f"{prefix}.feature_id={feat_id!r} must match ^FEAT-(PO|ARCH|UX|SEO|GRW|QA)-[0-9]+$.")
                    elif expected_prefix is not None and not feat_id.startswith(f"FEAT-{expected_prefix}-"):
                        errors.append(
                            f"{prefix}.feature_id={feat_id!r} must use prefix 'FEAT-{expected_prefix}-' for agent_id={agent_id!r}."
                        )
                for req_i in ("reach", "impact_score"):
                    val = feat.get(req_i)
                    if not _is_int(val) or not (1 <= val <= 10):
                        errors.append(f"{prefix}.{req_i} must be an integer 1..10.")
                conf_v = feat.get("confidence")
                if isinstance(conf_v, bool) or not isinstance(conf_v, (int, float)) or float(conf_v) not in VALID_CONFIDENCE_NUMS:
                    errors.append(f"{prefix}.confidence must be one of 0.5, 0.8, 1.0.")
                eff = feat.get("effort")
                if isinstance(eff, str) and eff not in EFFORT_POINTS:
                    errors.append(f"{prefix}.effort={eff!r} must be S|M|L|XL.")

    constraints = obj.get("non_negotiable_constraints")
    if constraints is not None:
        if not isinstance(constraints, list) or any(not isinstance(c, str) or not c.strip() for c in constraints):
            errors.append("'non_negotiable_constraints' must be a list of non-empty strings.")

    return errors


def _parse_weights(weights: dict[str, float] | None) -> dict[str, float]:
    resolved = {agent: 1.0 for agent in VALID_AGENTS}
    if not weights:
        return resolved
    for k, v in weights.items():
        canon = AGENT_SHORT_WEIGHT_KEYS.get(k.lower(), k)
        if canon in resolved:
            resolved[canon] = float(v)
    return resolved


def _compute_reachable_kg_files(kg_data: dict[str, Any] | None) -> set[str] | None:
    if not isinstance(kg_data, dict):
        return None
    nodes = kg_data.get("nodes", [])
    edges = kg_data.get("edges", [])
    if not isinstance(nodes, list):
        return None

    node_by_id: dict[str, dict[str, Any]] = {}
    queue: list[str] = []
    for n in nodes:
        if isinstance(n, dict) and "id" in n:
            nid = str(n["id"])
            node_by_id[nid] = n
            if n.get("kind") == "Route":
                queue.append(nid)

    adj: dict[str, list[str]] = {}
    for e in edges if isinstance(edges, list) else []:
        if isinstance(e, dict) and not e.get("unresolved", False):
            src = str(e.get("source", ""))
            dst = str(e.get("target", ""))
            if src and dst:
                adj.setdefault(src, []).append(dst)

    visited: set[str] = set(queue)
    while queue:
        curr = queue.pop(0)
        for nxt in adj.get(curr, []):
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)

    reachable_files: set[str] = set()
    for nid in visited:
        n = node_by_id.get(nid, {})
        f = n.get("file")
        if isinstance(f, str) and f.strip():
            reachable_files.add(_normalize_location(f))
    return reachable_files


def _classify_six_verb_decision(aud: dict[str, Any], *, force_remove: bool = False) -> str:
    if force_remove:
        return "REMOVE"
    explicit = aud.get("decision")
    if isinstance(explicit, str) and explicit in ("CONNECT", "FIX", "REFACTOR", "COMPLETE", "REMOVE", "DEFER"):
        return explicit

    norm_loc = _normalize_location(aud.get("location", "")).lower()
    text = f"{aud.get('issue', '')} {aud.get('fix_proposal', '')} {aud.get('evidence', '')}".lower()
    cat = aud.get("category", "")

    if "/legacy/" in f"/{norm_loc}" or any(w in text for w in ("remove unused", "dead code", "legacy", "kaldırılmalı")):
        return "REMOVE"
    if aud.get("confidence") == "candidate" and any(w in text for w in ("defer", "investigate", "hypothesis")):
        return "DEFER"
    if cat == "ORPHAN_API_DB" or any(
        w in text
        for w in (
            "connect existing",
            "wire endpoint",
            "already exists in backend",
            "exists in backend",
            "not wired to ui",
            "unreferenced in client",
        )
    ):
        return "CONNECT"
    if cat in ("BROKEN_ROUTE", "SECURITY", "QA") or any(
        w in text for w in ("404", "rbac", "idor", "auth guard", "broken link", "broken route")
    ):
        return "FIX"
    if cat in ("ARCHITECTURE", "PERFORMANCE") or any(
        w in text for w in ("refactor", "split chunk", "n+1", "god component", "duplication")
    ):
        return "REFACTOR"
    return "COMPLETE"


def merge(
    reports: list[dict[str, Any]],
    weights: dict[str, float] | None = None,
    *,
    project_root: Path | str | None = None,
    kg_data: dict[str, Any] | None = None,
    challenges: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate and synthesize specialist hat reports into a deterministic council bundle."""
    if not reports:
        raise ValueError("At least one specialist report is required to merge.")

    all_errors: list[str] = []
    for idx, rep in enumerate(reports):
        errs = validate_report(rep)
        if errs:
            tag = rep.get("agent_id", f"report[{idx}]") if isinstance(rep, dict) else f"report[{idx}]"
            all_errors.extend(f"[{tag}] {e}" for e in errs)
    if all_errors:
        raise ValueError("Invalid council report(s):\n" + "\n".join(all_errors))

    root_path = Path(project_root) if project_root is not None else None
    reachable_kg_files = _compute_reachable_kg_files(kg_data)
    weight_map = _parse_weights(weights)

    governance: dict[str, Any] = {
        "warnings": [],
        "rejected_finding_ids": [],
    }

    per_agent: list[dict[str, Any]] = []
    weighted_sum = 0.0
    weight_total = 0.0
    weakest: dict[str, Any] | None = None
    has_critical = False
    must_carry_ids: set[str] = set()

    by_location: dict[str, list[dict[str, Any]]] = {}
    all_audits: list[dict[str, Any]] = []
    ui_ux_mismatches: list[dict[str, Any]] = []
    constraints_by_agent: dict[str, list[str]] = {}
    agent_touched_locations: dict[str, set[str]] = {}
    report_audit_topics: dict[str, set[str]] = {}

    for rep in reports:
        aid = rep["agent_id"]
        role = rep["role"]
        applicability = rep.get("applicability", "applicable")
        score = rep.get("health_score")
        rationale = rep.get("health_score_rationale")
        na_reason = rep.get("not_applicable_reason", "")
        raw_constraints = list(rep.get("non_negotiable_constraints", []))
        constraints_by_agent[aid] = raw_constraints
        agent_touched_locations.setdefault(aid, set())
        report_audit_topics.setdefault(aid, set())

        # V4: Generic Boilerplate Constraint Check
        for c_str in raw_constraints:
            if GENERIC_CONSTRAINT_RE.search(c_str.strip()):
                governance["warnings"].append(
                    {
                        "code": "GENERIC_BOILERPLATE_CONSTRAINT",
                        "agent_id": aid,
                        "detail": c_str,
                    }
                )

        per_agent.append(
            {
                "agent_id": aid,
                "role": role,
                "applicability": applicability,
                "health_score": score if applicability == "applicable" else None,
                "health_score_rationale": rationale if applicability == "applicable" else None,
                "not_applicable_reason": na_reason if applicability == "not_applicable" else "",
            }
        )

        if applicability == "applicable":
            w = weight_map.get(aid, 1.0)
            weighted_sum += float(score) * w
            weight_total += w
            if weakest is None or score < weakest["health_score"]:
                weakest = {"agent_id": aid, "role": role, "health_score": score}

            for aud in rep.get("audits", []):
                norm_loc = _normalize_location(aud["location"])

                # V1: Disk existence verification when project_root is provided
                if root_path is not None:
                    candidate_file = root_path / norm_loc
                    if not candidate_file.is_file():
                        governance["rejected_finding_ids"].append(aud["id"])
                        governance["warnings"].append(
                            {
                                "code": "HALLUCINATED_EVIDENCE_PATH",
                                "agent_id": aid,
                                "finding_id": aud["id"],
                                "detail": f"Referenced file '{norm_loc}' does not exist under project_root.",
                            }
                        )
                        continue

                # V2: Knowledge Graph active route reachability check for STUB_PAGE across all 6 hats
                force_remove = False
                if (
                    aud.get("category") == "STUB_PAGE"
                    and reachable_kg_files is not None
                    and norm_loc not in reachable_kg_files
                ):
                    force_remove = True
                    governance["warnings"].append(
                        {
                            "code": "UNREACHABLE_LEGACY_COMPONENT",
                            "agent_id": aid,
                            "finding_id": aud["id"],
                            "detail": f"Component '{norm_loc}' has no active incoming Route edge in Knowledge Graph; reclassified to REMOVE.",
                        }
                    )
                    if aid == "snr-product-owner":
                        governance["warnings"].append(
                            {
                                "code": "UNREACHABLE_LEGACY_COMPONENT_FOR_PO",
                                "agent_id": aid,
                                "finding_id": aud["id"],
                                "detail": f"Component '{norm_loc}' has no active incoming Route edge in Knowledge Graph; reclassified to REMOVE.",
                            }
                        )

                # V6: Role-specific boundary & anti-slop checks on audits[] across all 6 hats
                aud_text = f"{aud.get('location', '')} {aud.get('evidence', '')} {aud.get('issue', '')} {aud.get('fix_proposal', '')}"
                if (
                    aid == "snr-software-architect"
                    and PO_VISUAL_THEME_RE.search(aud_text)
                    and not ARCH_SEAM_KEYWORDS_RE.search(aud_text)
                ):
                    governance["warnings"].append(
                        {
                            "code": "ARCH_BOUNDARY_VISUAL_STYLING",
                            "agent_id": aid,
                            "finding_id": aud["id"],
                            "detail": aud.get("issue", ""),
                        }
                    )

                if FABRICATED_METRIC_CLAIM_RE.search(aud_text) and not TELEMETRY_PROOF_RE.search(aud_text):
                    governance["warnings"].append(
                        {
                            "code": "FABRICATED_METRIC_CLAIM",
                            "agent_id": aid,
                            "finding_id": aud["id"],
                            "detail": aud.get("issue", ""),
                        }
                    )

                if (
                    aid == "snr-seo-specialist"
                    and SEO_PROTECTED_ROUTE_RE.search(aud_text)
                    and SEO_INDEX_PROPOSAL_RE.search(aud.get("fix_proposal", ""))
                ):
                    governance["warnings"].append(
                        {
                            "code": "SEO_PROTECTED_ROUTE_INDEXING",
                            "agent_id": aid,
                            "finding_id": aud["id"],
                            "detail": aud.get("fix_proposal", ""),
                        }
                    )

                if (
                    aid == "snr-qa-security-auditor"
                    and aud.get("category") in ("SECURITY", "QA")
                    and QA_CLIENT_ONLY_SECURITY_RE.search(aud.get("fix_proposal", ""))
                    and not QA_SERVER_ENFORCEMENT_RE.search(aud.get("fix_proposal", ""))
                ):
                    governance["warnings"].append(
                        {
                            "code": "QA_CLIENT_ONLY_SECURITY_FIX",
                            "agent_id": aid,
                            "finding_id": aud["id"],
                            "detail": aud.get("fix_proposal", ""),
                        }
                    )

                decision = _classify_six_verb_decision(aud, force_remove=force_remove)
                sev = aud["severity"]
                if sev == "CRITICAL":
                    has_critical = True
                if sev in ("CRITICAL", "HIGH"):
                    must_carry_ids.add(aud["id"])

                enriched = {
                    **aud,
                    "agent_id": aid,
                    "normalized_location": norm_loc,
                    "decision": decision,
                    "blocked_by": list(aud.get("blocked_by", [])),
                }
                all_audits.append(enriched)
                by_location.setdefault(norm_loc, []).append(enriched)
                agent_touched_locations[aid].add(norm_loc)
                report_audit_topics[aid].update(
                    _extract_topic_tokens(f"{aud.get('location', '')} {aud.get('issue', '')} {aud.get('evidence', '')}")
                )

            for mm in rep.get("ui_ux_mismatches", []):
                mm_text = f"{mm.get('screen_or_component', '')} {mm.get('theme_reference_gap', '')} {mm.get('ux_impact', '')} {mm.get('correction', '')}"
                suppress_mm = False

                # V6: PO Authority Boundary on Visual Theme / Colors
                if aid == "snr-product-owner" and PO_VISUAL_THEME_RE.search(mm_text):
                    governance["warnings"].append(
                        {
                            "code": "PO_BOUNDARY_VISUAL_THEME",
                            "agent_id": aid,
                            "detail": mm.get("theme_reference_gap", ""),
                        }
                    )
                    suppress_mm = True

                # V5: Cross-Section Duplicate Mismatch check across all 6 hats
                mm_tokens = _extract_topic_tokens(mm_text)
                overlap = mm_tokens & report_audit_topics.get(aid, set())
                if len(overlap) >= 2 or (
                    overlap and (aid == "snr-product-owner" or "placeholder" in mm_text.lower() or "settings" in overlap)
                ):
                    governance["warnings"].append(
                        {
                            "code": "CROSS_SECTION_DUPLICATE_MISMATCH",
                            "agent_id": aid,
                            "detail": mm.get("screen_or_component", ""),
                        }
                    )
                    suppress_mm = True

                if not suppress_mm:
                    ui_ux_mismatches.append({**mm, "agent_id": aid})
                    agent_touched_locations[aid].add(_normalize_location(mm["screen_or_component"]))

    # Attach security blockers (CRITICAL SECURITY findings on the same normalized_location)
    critical_sec_by_loc: dict[str, list[str]] = {}
    for aud in all_audits:
        if aud.get("severity") == "CRITICAL" and aud.get("category") in ("SECURITY", "QA"):
            critical_sec_by_loc.setdefault(aud["normalized_location"], []).append(aud["id"])

    for aud in all_audits:
        sec_ids = critical_sec_by_loc.get(aud["normalized_location"], [])
        for sid in sec_ids:
            if sid != aud["id"] and sid not in aud["blocked_by"]:
                aud["blocked_by"].append(sid)

    # Round 2 Challenge Round resolution
    challenge_resolutions: list[dict[str, Any]] = []
    if challenges:
        audits_by_id = {a["id"]: a for a in all_audits}
        for ch in challenges:
            if not isinstance(ch, dict):
                continue
            target_id = ch.get("target_id")
            target_aud = audits_by_id.get(str(target_id))
            if target_aud is not None:
                prev_dec = target_aud.get("decision")
                rev_dec = ch.get("revised_decision")
                if isinstance(rev_dec, str) and rev_dec in VALID_DECISIONS:
                    target_aud["decision"] = rev_dec
                extra_blockers = ch.get("blocked_by", [])
                if isinstance(extra_blockers, list):
                    for b in extra_blockers:
                        if isinstance(b, str) and b not in target_aud["blocked_by"]:
                            target_aud["blocked_by"].append(b)
                challenge_resolutions.append(
                    {
                        "challenger": ch.get("challenger", ""),
                        "target_id": target_id,
                        "challenge_type": ch.get("challenge_type", ""),
                        "previous_decision": prev_dec,
                        "revised_decision": target_aud.get("decision"),
                        "evidence": ch.get("evidence", ""),
                        "resolution": ch.get("resolution", ""),
                    }
                )

    mean_score = round(weighted_sum / weight_total, 1) if weight_total > 0 else 0.0
    critical_cap_applied = bool(has_critical and mean_score > 60.0)
    maturity_score = min(mean_score, 60.0) if has_critical else mean_score

    # 4-Axis Readiness Radar
    score_by_agent = {
        a["agent_id"]: float(a["health_score"])
        for a in per_agent
        if a["applicability"] == "applicable" and a["health_score"] is not None
    }

    def _axis_avg(agent_ids: tuple[str, ...]) -> float | None:
        vals = [score_by_agent[a] for a in agent_ids if a in score_by_agent]
        return round(sum(vals) / len(vals), 1) if vals else None

    readiness_axes = {
        "product_depth": _axis_avg(("snr-product-owner", "snr-growth-marketing")),
        "architecture_contract_integrity": _axis_avg(("snr-software-architect",)),
        "ux_operational_readiness": _axis_avg(("principal-ui-ux-specialist", "snr-seo-specialist")),
        "security_quality_assurance": _axis_avg(("snr-qa-security-auditor",)),
    }

    # Synergy clustering: >= 2 distinct agents flagging the same normalized location
    synergy_clusters: list[dict[str, Any]] = []
    for norm_loc in sorted(by_location.keys()):
        entries = by_location[norm_loc]
        distinct_agents = sorted({e["agent_id"] for e in entries})
        if len(distinct_agents) >= 2:
            max_rank = max(SEVERITY_RANK[e["severity"]] for e in entries)
            esc_rank = min(max_rank + 1, len(SEVERITY_ORDER) - 1)
            synergy_clusters.append(
                {
                    "location": norm_loc,
                    "agents": distinct_agents,
                    "finding_ids": [e["id"] for e in entries],
                    "base_max_severity": SEVERITY_ORDER[max_rank],
                    "escalated_severity": SEVERITY_ORDER[esc_rank],
                    "issues": [f"[{e['id']}] {e['issue']}" for e in entries],
                }
            )

    # Conflict candidates: proposer touches location L where another agent has red-line constraints and also touches L
    conflict_candidates: list[dict[str, Any]] = []
    seen_conflicts: set[tuple[str, str, str, str]] = set()
    for aud in all_audits:
        loc = aud["normalized_location"]
        proposer = aud["agent_id"]
        for other_agent, red_lines in constraints_by_agent.items():
            if other_agent == proposer or not red_lines:
                continue
            if loc in agent_touched_locations.get(other_agent, set()):
                key = (loc, proposer, aud["id"], other_agent)
                if key not in seen_conflicts:
                    seen_conflicts.add(key)
                    conflict_candidates.append(
                        {
                            "location": loc,
                            "proposer_agent": proposer,
                            "finding_id": aud["id"],
                            "proposal": aud["fix_proposal"],
                            "constraint_agent": other_agent,
                            "constraints": red_lines,
                        }
                    )

    # Beyond-PRD RICE ranking, V5 Cross-Section Deduplication & V6 Boundary/Anti-Slop Checks
    feature_groups: dict[str, dict[str, Any]] = {}
    for rep in reports:
        if rep.get("applicability", "applicable") == "not_applicable":
            continue
        aid = rep["agent_id"]
        audit_topics = report_audit_topics.get(aid, set())
        for feat in rep.get("new_features", []):
            slice_summary = feat.get("five_layer_slice_summary", "")
            feat_full_text = (
                f"{feat.get('title', '')} {feat.get('rationale', '')} {feat.get('user_value', '')} {slice_summary}"
            )

            # V6: PO Authority Boundary on Concrete Technical Architecture
            if aid == "snr-product-owner" and PO_TECH_ARCH_RE.search(slice_summary):
                governance["warnings"].append(
                    {
                        "code": "PO_BOUNDARY_TECHNICAL_ARCHITECTURE",
                        "agent_id": aid,
                        "feature_id": feat.get("feature_id", ""),
                        "detail": slice_summary,
                    }
                )

            # V6: Fabricated Metric Claim check across all 6 hats
            if FABRICATED_METRIC_CLAIM_RE.search(feat_full_text) and not TELEMETRY_PROOF_RE.search(feat_full_text):
                governance["warnings"].append(
                    {
                        "code": "FABRICATED_METRIC_CLAIM",
                        "agent_id": aid,
                        "feature_id": feat.get("feature_id", ""),
                        "detail": feat.get("rationale", ""),
                    }
                )

            # V5: Cross-Section Duplicate Feature check across all 6 hats
            feat_tokens = _extract_topic_tokens(
                f"{feat.get('title', '')} {feat.get('rationale', '')} {feat.get('target_location', '')}"
            )
            overlap = feat_tokens & audit_topics
            if len(overlap) >= 2 or (
                overlap and ("placeholder" in feat_tokens or "settings" in overlap or feat.get("target_location"))
            ):
                governance["warnings"].append(
                    {
                        "code": "CROSS_SECTION_DUPLICATE_FEATURE",
                        "agent_id": aid,
                        "feature_id": feat.get("feature_id", ""),
                        "detail": feat.get("title", ""),
                    }
                )
                continue

            norm_t = _normalize_title(feat["title"])
            if norm_t not in feature_groups:
                feature_groups[norm_t] = {
                    "title": feat["title"].strip(),
                    "feature_ids": [feat["feature_id"]],
                    "proposed_by": [aid],
                    "rationales": [feat["rationale"]],
                    "user_value": feat["user_value"],
                    "reach": int(feat["reach"]),
                    "impact_score": int(feat["impact_score"]),
                    "confidence": float(feat["confidence"]),
                    "effort": feat["effort"],
                    "five_layer_slice_summary": feat["five_layer_slice_summary"],
                }
            else:
                grp = feature_groups[norm_t]
                if feat["feature_id"] not in grp["feature_ids"]:
                    grp["feature_ids"].append(feat["feature_id"])
                if aid not in grp["proposed_by"]:
                    grp["proposed_by"].append(aid)
                if feat["rationale"] not in grp["rationales"]:
                    grp["rationales"].append(feat["rationale"])
                grp["reach"] = max(grp["reach"], int(feat["reach"]))
                grp["impact_score"] = max(grp["impact_score"], int(feat["impact_score"]))
                grp["confidence"] = max(grp["confidence"], float(feat["confidence"]))
                if EFFORT_POINTS[feat["effort"]] < EFFORT_POINTS[grp["effort"]]:
                    grp["effort"] = feat["effort"]

    features_ranked: list[dict[str, Any]] = []
    for grp in feature_groups.values():
        eff_pts = EFFORT_POINTS[grp["effort"]]
        rice = round((grp["reach"] * grp["impact_score"] * grp["confidence"]) / eff_pts, 2)
        features_ranked.append(
            {
                "title": grp["title"],
                "feature_ids": grp["feature_ids"],
                "proposed_by": sorted(grp["proposed_by"]),
                "rationale": " | ".join(grp["rationales"]),
                "user_value": grp["user_value"],
                "reach": grp["reach"],
                "impact_score": grp["impact_score"],
                "confidence": grp["confidence"],
                "effort": grp["effort"],
                "rice_score": rice,
                "five_layer_slice_summary": grp["five_layer_slice_summary"],
            }
        )

    features_ranked.sort(key=lambda f: (-f["rice_score"], -f["impact_score"], f["title"].lower()))

    applicable_count = sum(1 for a in per_agent if a["applicability"] == "applicable")

    return {
        "schema": SCHEMA_VERSION,
        "health": {
            "per_agent": per_agent,
            "applicable_count": applicable_count,
            "mean": mean_score,
            "weakest": weakest,
            "has_critical": has_critical,
            "critical_cap_applied": critical_cap_applied,
            "maturity": maturity_score,
            "readiness_axes": readiness_axes,
        },
        "must_carry_ids": sorted(must_carry_ids),
        "audits": all_audits,
        "synergy_clusters": synergy_clusters,
        "conflict_candidates": conflict_candidates,
        "challenge_resolutions": challenge_resolutions,
        "ui_ux_mismatches": ui_ux_mismatches,
        "features_ranked": features_ranked,
        "constraints_by_agent": constraints_by_agent,
        "governance": governance,
    }


def check_report(markdown_text: str, merged: dict[str, Any]) -> list[str]:
    """Verify that every CRITICAL and HIGH finding ID appears as an exact token in `markdown_text`."""
    missing: list[str] = []
    for fid in merged.get("must_carry_ids", []):
        token_re = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(fid)}(?![A-Za-z0-9_-])")
        if not token_re.search(markdown_text):
            missing.append(fid)
    return missing


def format_markdown(merged: dict[str, Any]) -> str:
    """Render deterministic Markdown summary of the merged council output."""
    h = merged["health"]
    cap_note = " *(CRITICAL tavanı 60 uygulandı)*" if h["critical_cap_applied"] else ""
    weak = h["weakest"]
    weak_str = f"`{weak['agent_id']}` ({weak['health_score']}/100)" if weak else "Yok"

    lines = [
        "# Feature Architect — 6 Şapkalı Konsey Birleştirme Özeti",
        "",
        "## 1. Konsey Sağlık Karnesi ve 4 Eksenli Hazırlık Radarı",
        f"- **Ağırlıklı Ham Ortalama:** `{h['mean']}/100` ({h['applicable_count']} aktif uzman)",
        f"- **Proje Olgunluk Skoru:** **`{h['maturity']}/100`**{cap_note}",
        f"- **En Zayıf Halka:** {weak_str}",
        "",
        "| Uzman Şapka | Durum | Skor | Gerekçe / Not |",
        "| :--- | :--- | :---: | :--- |",
    ]
    for a in h["per_agent"]:
        if a["applicability"] == "not_applicable":
            lines.append(f"| `{a['agent_id']}` | Kapsam Dışı (N/A) | — | {a['not_applicable_reason']} |")
        else:
            note = a.get("health_score_rationale") or a["role"]
            lines.append(f"| `{a['agent_id']}` | Aktif | **{a['health_score']}** | {note} |")

    lines.extend(["", "## 2. Zero-Drop Zorunlu Takip Kimlikleri (`CRITICAL` & `HIGH`)"])
    if merged["must_carry_ids"]:
        lines.append("- " + ", ".join(f"`{fid}`" for fid in merged["must_carry_ids"]))
    else:
        lines.append("- Kritik veya yüksek seviyeli bulgu yok.")

    lines.extend(["", "## 3. Sinerji Kümeleri (Ortak Hedefler)"])
    if merged["synergy_clusters"]:
        for cl in merged["synergy_clusters"]:
            agents_str = ", ".join(f"`{x}`" for x in cl["agents"])
            ids_str = ", ".join(f"`{x}`" for x in cl["finding_ids"])
            lines.append(
                f"- **`{cl['location']}`** ({cl['base_max_severity']} -> **{cl['escalated_severity']}**) · "
                f"Uzmanlar: {agents_str} · Bulgular: {ids_str}"
            )
    else:
        lines.append("- Ortak konumda kesişen çoklu uzman bulgusu yok.")

    lines.extend(["", "## 4. Çatışma Adayları ve 2. Tur Çapraz Sorgu Çözümleri"])
    if merged["conflict_candidates"]:
        for cc in merged["conflict_candidates"]:
            lines.append(
                f"- **`{cc['location']}`** · Öneren: `{cc['proposer_agent']}` (`{cc['finding_id']}`: {cc['proposal']}) "
                f"↔ Kırmızı Çizgi Sahibi: `{cc['constraint_agent']}` ({'; '.join(cc['constraints'])})"
            )
    else:
        lines.append("- Kırmızı çizgi kesişmesi tespit edilmedi.")

    if merged.get("challenge_resolutions"):
        for cr in merged["challenge_resolutions"]:
            lines.append(
                f"- **[Challenge `{cr['target_id']}`]** `{cr['challenger']}` ({cr['challenge_type']}): "
                f"`{cr['previous_decision']}` -> **`{cr['revised_decision']}`** ({cr['resolution']})"
            )

    lines.extend(["", "## 5. Beyond-PRD Yeni Özellikler (RICE Sıralaması)"])
    if merged["features_ranked"]:
        lines.extend(
            [
                "| RICE | Başlık | Önerenler | Efor | 5 Katmanlı Dilim Özeti |",
                "| :---: | :--- | :--- | :---: | :--- |",
            ]
        )
        for f in merged["features_ranked"]:
            props = ", ".join(f["proposed_by"])
            lines.append(
                f"| **{f['rice_score']}** | {f['title']} | `{props}` | `{f['effort']}` | {f['five_layer_slice_summary']} |"
            )
    else:
        lines.append("- Yeni özellik önerisi yok.")

    return "\n".join(lines) + "\n"


def build_sample_reports() -> list[dict[str, Any]]:
    """Built-in realistic 6-hat sample reports for `--sample` verification."""
    return [
        {
            "agent_id": "snr-product-owner",
            "role": "Senior Product Owner & Domain Strategist",
            "applicability": "applicable",
            "health_score": 78,
            "health_score_rationale": "Core onboarding flow is present on src/pages/Onboarding.tsx:24 but lacks an activation checklist (-22 pts).",
            "audits": [
                {
                    "id": "PO-01",
                    "category": "CORE_MODULE_GAP",
                    "severity": "HIGH",
                    "location": "src/pages/Onboarding.tsx:24",
                    "evidence": "src/pages/Onboarding.tsx:24 -> empty welcome panel without activation checklist",
                    "confidence": "verified",
                    "decision": "COMPLETE",
                    "issue": "New users land on an empty screen with no Next Best Action.",
                    "fix_proposal": "Add 3-step interactive onboarding checklist connected to profile state.",
                }
            ],
            "ui_ux_mismatches": [],
            "new_features": [
                {
                    "feature_id": "FEAT-PO-01",
                    "title": "Active Sessions & Device Revocation",
                    "rationale": "Enterprise users need self-service session visibility.",
                    "user_value": "Immediate control over active logins.",
                    "reach": 8,
                    "impact_score": 9,
                    "confidence": 1.0,
                    "effort": "M",
                    "five_layer_slice_summary": "1. Session visibility data -> 2. Revocation capability -> 3. Client state sync -> 4. Security tab + skeleton -> 5. Audit trail closure",
                }
            ],
            "non_negotiable_constraints": ["No primary onboarding screen may leave the user without a Next Best Action."],
        },
        {
            "agent_id": "snr-software-architect",
            "role": "Senior Software Architect & Systems Engineer",
            "applicability": "applicable",
            "health_score": 82,
            "health_score_rationale": "5-layer slice structure is solid overall, with 1 unwired backend audit-log endpoint (-18 pts).",
            "audits": [
                {
                    "id": "ARCH-01",
                    "category": "ORPHAN_API_DB",
                    "severity": "MEDIUM",
                    "location": "src/server/auditController.ts:52",
                    "evidence": "src/server/auditController.ts:52 -> GET /api/v1/audit-logs unreferenced in client",
                    "confidence": "verified",
                    "decision": "CONNECT",
                    "issue": "Audit log endpoint exists in backend but is never consumed by UI.",
                    "fix_proposal": "Wire endpoint into Settings Security timeline via typed API client.",
                }
            ],
            "ui_ux_mismatches": [],
            "new_features": [],
            "non_negotiable_constraints": ["Domain business logic must never leak directly into JSX view components."],
        },
        {
            "agent_id": "principal-ui-ux-specialist",
            "role": "Principal UI/UX & Design Systems Specialist",
            "applicability": "applicable",
            "health_score": 74,
            "health_score_rationale": "Design tokens are mostly consistent, but Onboarding.tsx:60 uses a raw spinner causing layout shift (-26 pts).",
            "audits": [
                {
                    "id": "UX-01",
                    "category": "UI_UX",
                    "severity": "HIGH",
                    "location": "src/pages/Onboarding.tsx:60",
                    "evidence": "src/pages/Onboarding.tsx:60 -> raw spinner used during initial fetch",
                    "confidence": "verified",
                    "decision": "FIX",
                    "issue": "Generic spinner causes layout shift on initial load.",
                    "fix_proposal": "Replace spinner with zero-CLS geometry-matched skeleton cassette.",
                }
            ],
            "ui_ux_mismatches": [
                {
                    "screen_or_component": "src/pages/Onboarding.tsx",
                    "theme_reference_gap": "Missing card elevation and skeleton cassette tokens",
                    "ux_impact": "Layout jump (CLS) on slow connections",
                    "correction": "Apply Living Surface semantic card tokens and form skeleton",
                }
            ],
            "new_features": [],
            "non_negotiable_constraints": ["Zero-CLS skeleton and actionable empty state are mandatory on every async view."],
        },
        {
            "agent_id": "snr-seo-specialist",
            "role": "Senior Technical SEO & Web Performance Specialist",
            "applicability": "applicable",
            "health_score": 85,
            "health_score_rationale": "Public landing route is crawlable, but Landing.tsx:15 has duplicate H1 tags and lacks JSON-LD (-15 pts).",
            "audits": [
                {
                    "id": "SEO-01",
                    "category": "SEO",
                    "severity": "MEDIUM",
                    "location": "src/pages/Landing.tsx:15",
                    "evidence": "src/pages/Landing.tsx:15 -> multiple H1 headings and missing JSON-LD",
                    "confidence": "verified",
                    "decision": "FIX",
                    "issue": "Public landing page has duplicate H1 tags.",
                    "fix_proposal": "Keep single semantic H1 and add SoftwareApplication JSON-LD.",
                }
            ],
            "ui_ux_mismatches": [],
            "new_features": [],
            "non_negotiable_constraints": ["Public indexable pages must never block crawlers with full-screen gates."],
        },
        {
            "agent_id": "snr-growth-marketing",
            "role": "Senior Growth & Product Marketing Specialist",
            "applicability": "applicable",
            "health_score": 79,
            "health_score_rationale": "Value proposition is clear on Landing.tsx:30, but secondary navigation competes with the primary signup CTA (-21 pts).",
            "audits": [
                {
                    "id": "GRW-01",
                    "category": "GROWTH",
                    "severity": "MEDIUM",
                    "location": "src/pages/Landing.tsx:30",
                    "evidence": "src/pages/Landing.tsx:30 -> secondary link competes with signup CTA",
                    "confidence": "verified",
                    "decision": "REFACTOR",
                    "issue": "Primary signup CTA lacks visual prominence.",
                    "fix_proposal": "Introduce sticky inline signup bar with clear value micro-copy.",
                }
            ],
            "ui_ux_mismatches": [],
            "new_features": [],
            "non_negotiable_constraints": ["Every landing screen must expose a single primary conversion goal."],
        },
        {
            "agent_id": "snr-qa-security-auditor",
            "role": "Senior QA, Security & 5-Layer TDD Auditor",
            "applicability": "applicable",
            "health_score": 68,
            "health_score_rationale": "Server-side validation is present on main flows, but orphan admin export route lacks RBAC middleware (-32 pts).",
            "audits": [
                {
                    "id": "QA-01",
                    "category": "SECURITY",
                    "severity": "CRITICAL",
                    "location": "src/server/adminRoutes.ts:19",
                    "evidence": "src/server/adminRoutes.ts:19 -> missing requireRole('ADMIN') middleware",
                    "confidence": "verified",
                    "decision": "FIX",
                    "issue": "Orphan admin export endpoint lacks server-side RBAC check.",
                    "fix_proposal": "Add server-side role guard + red-green integration test before UI wiring.",
                }
            ],
            "ui_ux_mismatches": [],
            "new_features": [
                {
                    "feature_id": "FEAT-QA-01",
                    "title": "Active Sessions & Device Revocation",
                    "rationale": "Prevents persistent access after credential leak.",
                    "user_value": "Zero-trust account protection.",
                    "reach": 9,
                    "impact_score": 9,
                    "confidence": 1.0,
                    "effort": "M",
                    "five_layer_slice_summary": "DB sessions -> Auth controller -> Typed client -> Security UI + skeleton -> Security log",
                }
            ],
            "non_negotiable_constraints": ["Authorization and input validation must never rely solely on frontend checks."],
        },
    ]


def _load_reports_from_dir(inputs_dir: Path) -> list[dict[str, Any]]:
    if not inputs_dir.is_dir():
        raise ValueError(f"Inputs directory does not exist: {inputs_dir}")
    reports: list[dict[str, Any]] = []
    for p in sorted(inputs_dir.glob("*.json")):
        if p.name in SKIP_JSON_FILENAMES:
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        reports.append(data)
    if not reports:
        raise ValueError(f"No specialist JSON reports found in {inputs_dir}")
    return reports


def audit_council_directory(
    council_dir: Path | str,
    *,
    project_root: Path | str | None = None,
) -> dict[str, Any]:
    """Audit a coordinated `docs/plans/council/<YYYY-MM-DD>/` folder across all 6 hats and `/council` Borda links."""
    cdir = Path(council_dir)
    if not cdir.is_dir():
        raise ValueError(f"Council directory does not exist: {cdir}")

    reports = _load_reports_from_dir(cdir)
    present_agents: set[str] = set()
    schema_errors: dict[str, list[str]] = {}
    role_title_mismatches: list[dict[str, str]] = []
    missing_rationale_agents: list[str] = []

    valid_reports: list[dict[str, Any]] = []
    for idx, rep in enumerate(reports):
        aid = rep.get("agent_id", f"report[{idx}]") if isinstance(rep, dict) else f"report[{idx}]"
        if isinstance(aid, str) and aid in VALID_AGENTS:
            present_agents.add(aid)
        errs = validate_report(rep)
        if errs:
            schema_errors[str(aid)] = errs
        else:
            valid_reports.append(rep)

        if isinstance(rep, dict) and aid in AGENT_CONTRACT_MAP:
            expected_role = AGENT_CONTRACT_MAP[aid]["canonical_role"]
            actual_role = str(rep.get("role", "")).strip()
            if actual_role != expected_role:
                role_title_mismatches.append(
                    {
                        "agent_id": aid,
                        "actual_role": actual_role,
                        "expected_role": expected_role,
                    }
                )
            if rep.get("applicability", "applicable") == "applicable" and not rep.get("health_score_rationale"):
                missing_rationale_agents.append(aid)

    kg_path = cdir / "project-knowledge-graph.json"
    kg_data = json.loads(kg_path.read_text(encoding="utf-8")) if kg_path.is_file() else None
    chal_path = cdir / "challenges.json"
    challenges = json.loads(chal_path.read_text(encoding="utf-8")) if chal_path.is_file() else None

    merged: dict[str, Any] = {}
    if valid_reports:
        merged = merge(
            valid_reports,
            project_root=project_root,
            kg_data=kg_data,
            challenges=challenges,
        )

    report_md_path = cdir / "feature-architect-council-report.md"
    zero_drop_missing: list[str] = []
    if report_md_path.is_file() and merged:
        zero_drop_missing = check_report(
            report_md_path.read_text(encoding="utf-8", errors="replace"),
            merged,
        )

    conflicts = merged.get("conflict_candidates", []) if merged else []
    missing_hats = sorted(VALID_AGENTS - present_agents)

    return {
        "council_dir": str(cdir),
        "hat_count": len(present_agents),
        "missing_hats": missing_hats,
        "schema_errors": schema_errors,
        "role_title_mismatches": role_title_mismatches,
        "missing_rationale_agents": sorted(missing_rationale_agents),
        "governance": merged.get("governance", {"warnings": [], "rejected_finding_ids": []}),
        "conflict_candidates": conflicts,
        "borda_arbitration_ready": bool(conflicts),
        "zero_drop_missing_ids": zero_drop_missing,
    }


def _parse_weight_arg(raw: str) -> dict[str, float]:
    out: dict[str, float] = {}
    if not raw.strip():
        return out
    for part in raw.split(","):
        if "=" not in part:
            raise ValueError(f"Invalid weight specification {part!r}; expected key=value.")
        k, v = part.split("=", 1)
        out[k.strip()] = float(v.strip())
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feature Architect — Six-Hat Council Synthesizer & Zero-Drop Gate")
    parser.add_argument("--inputs", help="Directory containing specialist hat JSON reports")
    parser.add_argument("--audit-council-dir", help="Audit an existing docs/plans/council/<YYYY-MM-DD> directory")
    parser.add_argument("--sample", action="store_true", help="Run with built-in 6-hat sample reports")
    parser.add_argument("--weights", default="", help="Optional weights e.g. po=1,arch=1,ux=1,seo=1,grw=1,qa=1")
    parser.add_argument("--project-root", help="Optional target project root for V1 file/line existence checks")
    parser.add_argument("--kg", help="Optional path to project-knowledge-graph.json for V2 route reachability checks")
    parser.add_argument("--challenges", help="Optional path to challenges.json for Round 2 cross-examination")
    parser.add_argument("--format", choices=["json", "md"], default="json", help="Output format")
    parser.add_argument("--output", help="Optional output file path")
    parser.add_argument("--check-report", help="Consolidated Markdown report path to verify against Zero-Drop rule")
    args = parser.parse_args(argv)

    if args.audit_council_dir:
        try:
            audit_res = audit_council_directory(
                Path(args.audit_council_dir),
                project_root=Path(args.project_root) if args.project_root else None,
            )
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            return 1
        rendered = json.dumps(audit_res, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 1 if audit_res["schema_errors"] or audit_res["zero_drop_missing_ids"] else 0

    if not args.sample and not args.inputs:
        print("[ERROR] Specify either --inputs <dir>, --audit-council-dir <dir>, or --sample.", file=sys.stderr)
        return 1

    try:
        reports = build_sample_reports() if args.sample else _load_reports_from_dir(Path(args.inputs))
        weights = _parse_weight_arg(args.weights)
        kg_data = json.loads(Path(args.kg).read_text(encoding="utf-8")) if args.kg else None
        challenges = json.loads(Path(args.challenges).read_text(encoding="utf-8")) if args.challenges else None
        merged = merge(
            reports,
            weights=weights,
            project_root=Path(args.project_root) if args.project_root else None,
            kg_data=kg_data,
            challenges=challenges,
        )
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.check_report:
        md_path = Path(args.check_report)
        if not md_path.is_file():
            print(f"[ERROR] Report file not found: {md_path}", file=sys.stderr)
            return 1
        md_text = md_path.read_text(encoding="utf-8", errors="replace")
        missing = check_report(md_text, merged)
        if missing:
            print(
                f"[ZERO-DROP VIOLATION] Consolidated report is missing {len(missing)} CRITICAL/HIGH finding ID(s): "
                + ", ".join(missing),
                file=sys.stderr,
            )
            return 2
        print(f"[OK] Zero-Drop gate passed ({len(merged['must_carry_ids'])} CRITICAL/HIGH IDs verified).")
        return 0

    rendered = format_markdown(merged) if args.format == "md" else json.dumps(merged, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
