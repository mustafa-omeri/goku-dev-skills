#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect — Six-Hat Council Synthesizer & Zero-Drop Gate (`council_merger.py`).

Validates individual specialist hat JSON reports against `council-contract.schema.json`,
computes equal/custom-weighted maturity scores (with N/A exclusion, weakest-link
reporting, and CRITICAL cap at 60), clusters multi-hat synergy targets, flags
cross-hat trade-off / conflict candidates, ranks Beyond-PRD features via RICE,
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

SCHEMA_VERSION = "feature-architect/council-merge@1"

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

SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SEVERITY_RANK = {name: idx for idx, name in enumerate(SEVERITY_ORDER)}
EFFORT_POINTS = {"S": 1, "M": 2, "L": 3, "XL": 5}
VALID_CONFIDENCE_NUMS = {0.5, 0.8, 1.0}
FINDING_ID_RE = re.compile(r"^(PO|ARCH|UX|SEO|GRW|QA)-[0-9]{2,}$")
LINE_SUFFIX_RE = re.compile(r":\d+(?:-\d+)?$")

SKIP_JSON_FILENAMES = {
    "context-snapshot.json",
    "engine-advice.json",
    "merged.json",
}


def _is_int(val: Any) -> bool:
    return isinstance(val, int) and not isinstance(val, bool)


def _normalize_location(loc: str) -> str:
    cleaned = loc.strip().replace("\\", "/")
    cleaned = LINE_SUFFIX_RE.sub("", cleaned)
    return cleaned


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


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
        if not isinstance(reason, str) or not reason.strip():
            errors.append("'not_applicable_reason' is required when applicability is 'not_applicable'.")
        score = obj.get("health_score")
        if score is not None and (not _is_int(score) or not (0 <= score <= 100)):
            errors.append("'health_score' must be null or integer 0..100 when not_applicable.")
    else:
        score = obj.get("health_score")
        if not _is_int(score) or not (0 <= score <= 100):
            errors.append("'health_score' must be an integer between 0 and 100 when applicable.")

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


def merge(reports: list[dict[str, Any]], weights: dict[str, float] | None = None) -> dict[str, Any]:
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

    weight_map = _parse_weights(weights)

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

    for rep in reports:
        aid = rep["agent_id"]
        role = rep["role"]
        applicability = rep.get("applicability", "applicable")
        score = rep.get("health_score")
        na_reason = rep.get("not_applicable_reason", "")
        constraints_by_agent[aid] = list(rep.get("non_negotiable_constraints", []))
        agent_touched_locations.setdefault(aid, set())

        per_agent.append(
            {
                "agent_id": aid,
                "role": role,
                "applicability": applicability,
                "health_score": score if applicability == "applicable" else None,
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
                sev = aud["severity"]
                if sev == "CRITICAL":
                    has_critical = True
                if sev in ("CRITICAL", "HIGH"):
                    must_carry_ids.add(aud["id"])
                norm_loc = _normalize_location(aud["location"])
                enriched = {**aud, "agent_id": aid, "normalized_location": norm_loc}
                all_audits.append(enriched)
                by_location.setdefault(norm_loc, []).append(enriched)
                agent_touched_locations[aid].add(norm_loc)

            for mm in rep.get("ui_ux_mismatches", []):
                ui_ux_mismatches.append({**mm, "agent_id": aid})
                agent_touched_locations[aid].add(_normalize_location(mm["screen_or_component"]))

    mean_score = round(weighted_sum / weight_total, 1) if weight_total > 0 else 0.0
    critical_cap_applied = bool(has_critical and mean_score > 60.0)
    maturity_score = min(mean_score, 60.0) if has_critical else mean_score

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

    # Beyond-PRD RICE ranking & duplicate title merging
    feature_groups: dict[str, dict[str, Any]] = {}
    for rep in reports:
        if rep.get("applicability", "applicable") == "not_applicable":
            continue
        aid = rep["agent_id"]
        for feat in rep.get("new_features", []):
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
        },
        "must_carry_ids": sorted(must_carry_ids),
        "audits": all_audits,
        "synergy_clusters": synergy_clusters,
        "conflict_candidates": conflict_candidates,
        "ui_ux_mismatches": ui_ux_mismatches,
        "features_ranked": features_ranked,
        "constraints_by_agent": constraints_by_agent,
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
        "## 1. Konsey Sağlık Karnesi",
        f"- **Ağırlıklı Ham Ortalama:** `{h['mean']}/100` ({h['applicable_count']} aktif uzman)",
        f"- **Proje Olgunluk Skoru:** **`{h['maturity']}/100`**{cap_note}",
        f"- **En Zayıf Halka:** {weak_str}",
        "",
        "| Uzman Şapka | Durum | Skor | Not |",
        "| :--- | :--- | :---: | :--- |",
    ]
    for a in h["per_agent"]:
        if a["applicability"] == "not_applicable":
            lines.append(f"| `{a['agent_id']}` | Kapsam Dışı (N/A) | — | {a['not_applicable_reason']} |")
        else:
            lines.append(f"| `{a['agent_id']}` | Aktif | **{a['health_score']}** | {a['role']} |")

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

    lines.extend(["", "## 4. Çatışma Adayları (Hakem Hibrit Çözüm Masası)"])
    if merged["conflict_candidates"]:
        for cc in merged["conflict_candidates"]:
            lines.append(
                f"- **`{cc['location']}`** · Öneren: `{cc['proposer_agent']}` (`{cc['finding_id']}`: {cc['proposal']}) "
                f"↔ Kırmızı Çizgi Sahibi: `{cc['constraint_agent']}` ({'; '.join(cc['constraints'])})"
            )
    else:
        lines.append("- Kırmızı çizgi kesişmesi tespit edilmedi.")

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
            "audits": [
                {
                    "id": "PO-01",
                    "category": "CORE_MODULE_GAP",
                    "severity": "HIGH",
                    "location": "src/pages/Onboarding.tsx:24",
                    "evidence": "src/pages/Onboarding.tsx:24 -> empty welcome panel without activation checklist",
                    "confidence": "verified",
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
                    "five_layer_slice_summary": "DB sessions -> RPC list/revoke -> API service -> Security tab + skeleton -> Audit trail",
                }
            ],
            "non_negotiable_constraints": ["No screen may leave the user without a Next Best Action."],
        },
        {
            "agent_id": "snr-software-architect",
            "role": "Senior Software Architect & Systems Engineer",
            "applicability": "applicable",
            "health_score": 82,
            "audits": [
                {
                    "id": "ARCH-01",
                    "category": "ORPHAN_API_DB",
                    "severity": "MEDIUM",
                    "location": "src/server/auditController.ts:52",
                    "evidence": "src/server/auditController.ts:52 -> GET /api/v1/audit-logs unreferenced in client",
                    "confidence": "verified",
                    "issue": "Audit log endpoint exists in backend but is never consumed by UI.",
                    "fix_proposal": "Wire endpoint into Settings Security timeline via typed API client.",
                }
            ],
            "ui_ux_mismatches": [],
            "new_features": [],
            "non_negotiable_constraints": ["Business logic must never leak directly into UI components."],
        },
        {
            "agent_id": "principal-ui-ux-specialist",
            "role": "Principal UI/UX & Design Systems Specialist",
            "applicability": "applicable",
            "health_score": 74,
            "audits": [
                {
                    "id": "UX-01",
                    "category": "UI_UX",
                    "severity": "HIGH",
                    "location": "src/pages/Onboarding.tsx:60",
                    "evidence": "src/pages/Onboarding.tsx:60 -> raw spinner used during initial fetch",
                    "confidence": "verified",
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
            "non_negotiable_constraints": ["Zero-CLS skeleton and empty state are mandatory on every async view."],
        },
        {
            "agent_id": "snr-seo-specialist",
            "role": "Senior Technical SEO & Web Performance Specialist",
            "applicability": "applicable",
            "health_score": 85,
            "audits": [
                {
                    "id": "SEO-01",
                    "category": "SEO",
                    "severity": "MEDIUM",
                    "location": "src/pages/Landing.tsx:15",
                    "evidence": "src/pages/Landing.tsx:15 -> multiple H1 headings and missing JSON-LD",
                    "confidence": "verified",
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
            "audits": [
                {
                    "id": "GRW-01",
                    "category": "GROWTH",
                    "severity": "MEDIUM",
                    "location": "src/pages/Landing.tsx:30",
                    "evidence": "src/pages/Landing.tsx:30 -> secondary link competes with signup CTA",
                    "confidence": "verified",
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
            "audits": [
                {
                    "id": "QA-01",
                    "category": "SECURITY",
                    "severity": "CRITICAL",
                    "location": "src/server/adminRoutes.ts:19",
                    "evidence": "src/server/adminRoutes.ts:19 -> missing requireRole('ADMIN') middleware",
                    "confidence": "verified",
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
    parser.add_argument("--sample", action="store_true", help="Run with built-in 6-hat sample reports")
    parser.add_argument("--weights", default="", help="Optional weights e.g. po=1,arch=1,ux=1,seo=1,grw=1,qa=1")
    parser.add_argument("--format", choices=["json", "md"], default="json", help="Output format")
    parser.add_argument("--output", help="Optional output file path")
    parser.add_argument("--check-report", help="Consolidated Markdown report path to verify against Zero-Drop rule")
    args = parser.parse_args(argv)

    if not args.sample and not args.inputs:
        print("[ERROR] Specify either --inputs <dir> or --sample.", file=sys.stderr)
        return 1

    try:
        reports = build_sample_reports() if args.sample else _load_reports_from_dir(Path(args.inputs))
        weights = _parse_weight_arg(args.weights)
        merged = merge(reports, weights=weights)
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
