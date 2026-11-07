#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect v2 — Architectural Evolution Horizon Planner (`evolution.py`).

Organizes validated council findings and decisions into `Now / Next / Future` execution
horizons and enforces the zero-fabrication guard on capacity/cost projections (`UNKNOWN`
when measured traffic/cost inputs are absent).
"""
from __future__ import annotations

from typing import Any


def build_evolution_horizon(
    audits: list[dict[str, Any]],
    *,
    scale_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Partition findings into `now`, `next`, and `future` execution horizons."""
    now_bucket: list[dict[str, Any]] = []
    next_bucket: list[dict[str, Any]] = []
    future_bucket: list[dict[str, Any]] = []

    for aud in audits:
        sev = str(aud.get("severity", "MEDIUM")).upper()
        dec = str(aud.get("decision", "COMPLETE")).upper()
        if sev in ("CRITICAL", "HIGH") or dec in ("CONNECT", "FIX"):
            now_bucket.append(aud)
        elif dec == "DEFER" or sev == "LOW":
            future_bucket.append(aud)
        else:
            next_bucket.append(aud)

    return {
        "horizons": {
            "now": now_bucket,
            "next": next_bucket,
            "future": future_bucket,
        },
        "economic_capacity_status": "MEASURED" if scale_metrics else "UNKNOWN",
        "scale_metrics": scale_metrics if scale_metrics else None,
    }
