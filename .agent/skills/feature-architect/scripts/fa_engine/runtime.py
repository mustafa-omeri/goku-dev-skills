#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect v2 — Opt-in L3 Runtime Verifier & PII/Secret Redactor (`runtime.py`).

Enforces strict safety gates for L3 runtime verification:
1. Localhost-only target restriction (`localhost`, `127.0.0.1`, `[::1]`).
2. Mutation-free (`GET` / `HEAD` / `OPTIONS` only) request guard by default.
3. Zero-leakage PII, JWT/Bearer token, and credential redaction before persisting any log or report.
4. Reconciles L1/L2 `INFERRED` behavioral facts into `CONFIRMED` or `REFUTED` based on L3 observations.
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

ALLOWED_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
SAFE_READ_METHODS = {"GET", "HEAD", "OPTIONS"}

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
BEARER_RE = re.compile(r"(?:Bearer\s+)?eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
SECRET_KV_RE = re.compile(
    r"(?i)\b(password|passwd|secret|api_key|apikey|access_token|refresh_token)\s*([:=])\s*([^\s,;\"']+)"
)


def validate_probe_request(url: str, *, method: str = "GET", allow_mutations: bool = False) -> bool:
    """Validate that a runtime probe URL targets localhost and uses a read-only HTTP method."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_LOCAL_HOSTS:
        raise ValueError(f"Runtime probe blocked: host {host!r} is not localhost ({sorted(ALLOWED_LOCAL_HOSTS)}).")
    upper_method = method.strip().upper()
    if not allow_mutations and upper_method not in SAFE_READ_METHODS:
        raise ValueError(f"Runtime probe blocked: mutating HTTP method {upper_method!r} is forbidden in read-only L3 mode.")
    return True


def redact_sensitive_text(text: str) -> str:
    """Mask email addresses, JWT/Bearer tokens, and secret key-value pairs."""
    out = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    out = BEARER_RE.sub("[REDACTED_TOKEN]", out)
    out = SECRET_KV_RE.sub(r"\1\2[REDACTED_SECRET]", out)
    return out


def reconcile_runtime_observations(
    facts: list[dict[str, Any]],
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Upgrade `INFERRED` facts to `CONFIRMED` or mark `REFUTED` using validated L3 observations."""
    obs_by_id: dict[str, dict[str, Any]] = {}
    for obs in observations:
        if not isinstance(obs, dict):
            continue
        url = str(obs.get("url", "http://localhost"))
        method = str(obs.get("method", "GET"))
        validate_probe_request(url, method=method)
        tid = str(obs.get("target_fact_id", ""))
        if tid:
            obs_by_id[tid] = obs

    reconciled: list[dict[str, Any]] = []
    for fact in facts:
        copy_f = dict(fact)
        fid = str(copy_f.get("id", ""))
        if fid in obs_by_id:
            obs = obs_by_id[fid]
            outcome = str(obs.get("outcome", "")).lower()
            detail = redact_sensitive_text(str(obs.get("detail", "")))
            if outcome == "confirmed":
                copy_f["status"] = "CONFIRMED"
                copy_f["confidence"] = max(int(copy_f.get("confidence", 50)), 92)
                copy_f["verification_level"] = "L3_RUNTIME"
                copy_f["runtime_evidence"] = detail
            elif outcome == "refuted":
                copy_f["status"] = "REFUTED"
                copy_f["confidence"] = 0
                copy_f["verification_level"] = "L3_RUNTIME"
                copy_f["runtime_evidence"] = detail
        reconciled.append(copy_f)
    return reconciled
