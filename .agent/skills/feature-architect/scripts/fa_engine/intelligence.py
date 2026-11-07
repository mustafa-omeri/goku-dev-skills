#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect v2 — Domain-Neutral Product & Capability Intelligence (`intelligence.py`).

Infers project archetype dimensions (topology, statefulness, identity model, access surface)
strictly from code & documentation signals without hardcoded industry templates.
"""
from __future__ import annotations

from typing import Any

from .model import ProjectProfile


def infer_product_intelligence(profile: ProjectProfile, facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive domain-neutral archetype and capability signals from `ProjectProfile` and `facts`."""
    has_fe = bool(profile.frontend_stacks)
    has_be = bool(profile.backend_stacks)
    has_db = bool(profile.orm_or_schema_sources)

    if has_fe and has_be:
        topology = "full-stack-web"
    elif has_fe:
        topology = "frontend-spa-or-ssr"
    elif has_be:
        topology = "backend-api-service"
    else:
        topology = "cli-or-library"

    auth_signals = [f for f in facts if "AUTH" in str(f.get("category", "")) or "ROLE" in str(f.get("category", ""))]
    identity_model = "role-based-authenticated" if auth_signals else "stateless-or-public"
    statefulness = "persistent-data" if has_db else "stateless"

    missing_strategy_axes: list[str] = []
    if not profile.doc_sources:
        missing_strategy_axes.extend(["primary_value_proposition", "target_user_persona", "scale_target"])

    return {
        "topology": topology,
        "statefulness": statefulness,
        "identity_model": identity_model,
        "access_surface": "authenticated-app" if identity_model == "role-based-authenticated" else "public-or-local",
        "observed_capabilities_status": "CONFIRMED" if profile.doc_sources else "INFERRED",
        "missing_strategy_axes": missing_strategy_axes,
    }
