# -*- coding: utf-8 -*-
"""3-Tier Authorization & Ownership Surface Analyzer (`authz.py`).

Separates:
  1. `UI_AUTHORIZATION_MISMATCH` (Medium — unauthorized action rendered to role in UI)
  2. `BACKEND_AUTHORIZATION_GAP` (Critical — server endpoint unguarded across annotations AND URL filter chain)
  3. `RESOURCE_OWNERSHIP_GAP` (Critical/High — org/tenant-scoped entity queried by raw ID without scope check)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..model import CoverageReport, EvidenceRef, Fact, ProjectProfile, iter_repo_files, normalize_api_path
from .base import AnalyzerContext, AnalyzerResult

PUBLIC_AUTH_SEGMENTS = ("/auth/", "/login", "/register", "/signup", "/health", "/actuator/health", "/public/", "/webhook")


def _ant_pattern_matches(pattern: str, path: str) -> bool:
    norm_pat = "/" + pattern.strip("/")
    norm_path = "/" + path.strip("/")
    if norm_pat.endswith("/**"):
        base = norm_pat[:-3]
        return norm_path == base or norm_path.startswith(base + "/")
    regex = "^" + re.escape(norm_pat).replace(r"\*", "[^/]*") + "$"
    return bool(re.match(regex, norm_path))


def _resolve_effective_endpoint_security(
    ep: dict[str, Any],
    url_rules: list[dict[str, Any]],
) -> tuple[bool, set[str], bool, dict[str, Any] | None]:
    """Return `(is_guarded, allowed_roles_set, is_explicit_permit_all, matching_url_rule)`."""
    method_roles = set(ep.get("allowed_roles") or [])
    if method_roles or ep.get("authenticated"):
        return True, method_roles, False, None

    for rule in url_rules:
        if _ant_pattern_matches(rule["pattern"], ep["path"]) or _ant_pattern_matches(
            normalize_api_path(rule["pattern"]), ep["normalized_path"]
        ):
            rkind = rule["rule"]
            if rkind == "permitAll":
                return False, set(), True, rule
            return True, set(rule.get("roles") or []), False, rule

    return False, set(), False, None


class AuthorizationSurfaceAnalyzer:
    name = "authz"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        if profile.backend_stacks or profile.frontend_stacks:
            return True, "Active UI/API authorization surface"
        return False, "No UI or backend endpoints detected"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        applicable, reason = self.applies(ctx.profile)
        if not applicable:
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
            )

        fe_state = ctx.shared_state.get("frontend", {})
        be_state = ctx.shared_state.get("backend", {})
        data_state = ctx.shared_state.get("data", {})

        components: dict[str, dict[str, Any]] = fe_state.get("components", {})
        http_calls: list[dict[str, Any]] = fe_state.get("http_calls", [])
        endpoints: list[dict[str, Any]] = be_state.get("endpoints", [])
        url_rules: list[dict[str, Any]] = be_state.get("url_security_rules", [])
        scoped_entities: set[str] = set(data_state.get("scoped_entities", set()))

        facts: list[Fact] = []
        scanned = 0

        # Index endpoints
        be_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for ep in endpoints:
            be_by_key.setdefault((ep["method"], ep["normalized_path"]), []).append(ep)

        # Index HTTP calls by file
        calls_by_file: dict[str, list[dict[str, Any]]] = {}
        for c in http_calls:
            calls_by_file.setdefault(c["file"], []).append(c)

        # 1. UI_AUTHORIZATION_MISMATCH
        for cname, cmeta in sorted(components.items()):
            vroles = set(cmeta.get("visible_roles") or [])
            if not vroles:
                continue
            for call in calls_by_file.get(cmeta["file"], []):
                for ep in be_by_key.get((call["method"], call["normalized_path"]), []):
                    guarded, be_roles, _, _ = _resolve_effective_endpoint_security(ep, url_rules)
                    if guarded and be_roles:
                        excess_ui_roles = sorted(vroles - be_roles)
                        if excess_ui_roles:
                            facts.append(
                                Fact.create(
                                    fact_id=f"AUTHZ-UI-{len(facts)+1:03d}",
                                    code="UI_AUTHORIZATION_MISMATCH",
                                    category="UI_UX",
                                    fact_type="structural",
                                    severity="MEDIUM",
                                    summary=(
                                        f"Component `{cname}` (`{cmeta['file']}:{cmeta['line']}`) exposes action "
                                        f"`{call['method']} {call['raw_path']}` to role(s) `{', '.join(excess_ui_roles)}`, "
                                        f"but backend restricts it to `{', '.join(sorted(be_roles))}`."
                                    ),
                                    location=f"{cmeta['file']}:{cmeta['line']}",
                                    evidence=[
                                        EvidenceRef(
                                            kind="code",
                                            level="L1",
                                            derivation="syntax",
                                            ref=f"{cmeta['file']}:{cmeta['line']}",
                                            line=cmeta["line"],
                                            excerpt=cname,
                                        ),
                                        EvidenceRef(
                                            kind="code",
                                            level="L1",
                                            derivation="syntax",
                                            ref=f"{ep['rel_file']}:{ep['line']}",
                                            line=ep["line"],
                                            excerpt=f"{ep['method']} {ep['path']}",
                                        ),
                                    ],
                                    attrs={
                                        "excess_ui_roles": excess_ui_roles,
                                        "backend_roles": sorted(be_roles),
                                    },
                                )
                            )

        # 2. BACKEND_AUTHORIZATION_GAP (respecting SecurityFilterChain rules to avoid false positives!)
        for ep in endpoints:
            if ep["method"] not in {"POST", "PUT", "PATCH", "DELETE"}:
                continue
            low_p = ep["path"].lower()
            if any(seg in low_p for seg in PUBLIC_AUTH_SEGMENTS):
                continue

            guarded, _, explicit_permit, matched_rule = _resolve_effective_endpoint_security(ep, url_rules)
            if guarded:
                continue

            if explicit_permit:
                facts.append(
                    Fact.create(
                        fact_id=f"AUTHZ-BE-{len(facts)+1:03d}",
                        code="BACKEND_AUTHORIZATION_GAP",
                        category="SECURITY",
                        fact_type="structural",
                        severity="CRITICAL",
                        summary=(
                            f"Mutating endpoint `{ep['method']} {ep['path']}` (`{ep['rel_file']}:{ep['line']}`) "
                            f"is explicitly exposed via `permitAll()` in `{matched_rule['file']}:{matched_rule['line']}`."
                        ),
                        location=f"{ep['rel_file']}:{ep['line']}",
                        evidence=[
                            EvidenceRef(
                                kind="code",
                                level="L2",
                                derivation="config",
                                ref=f"{matched_rule['file']}:{matched_rule['line']}",
                                line=matched_rule["line"],
                                excerpt=f"requestMatchers({matched_rule['pattern']}).permitAll()",
                            )
                        ],
                    )
                )
            elif any(seg in low_p for seg in ("/admin", "/users", "/tenants", "/organizations", "/roles", "/billing")):
                # Sensitive administrative/mutating route with neither annotation nor URL rule
                deriv = "config" if url_rules else "heuristic"
                req_status = "CONFIRMED" if url_rules else "INFERRED"
                facts.append(
                    Fact.create(
                        fact_id=f"AUTHZ-BE-{len(facts)+1:03d}",
                        code="BACKEND_AUTHORIZATION_GAP",
                        category="SECURITY",
                        fact_type="structural",
                        severity="CRITICAL",
                        summary=(
                            f"Sensitive mutating endpoint `{ep['method']} {ep['path']}` (`{ep['rel_file']}:{ep['line']}`) "
                            f"has neither method-level authorization nor matching URL filter protection."
                        ),
                        location=f"{ep['rel_file']}:{ep['line']}",
                        evidence=[
                            EvidenceRef(
                                kind="code",
                                level="L1",
                                derivation=deriv,
                                ref=f"{ep['rel_file']}:{ep['line']}",
                                line=ep["line"],
                                excerpt=f"{ep['method']} {ep['path']}",
                            )
                        ],
                        requested_status=req_status,
                    )
                )

        # 3. RESOURCE_OWNERSHIP_GAP (IDOR / missing tenant or org scope on scoped entities)
        if ctx.profile.tenancy_model in {"org-scoped", "tenant-column"} and scoped_entities:
            ownership_guard_re = re.compile(
                r"(?:get(?:Organization|Company|Workspace|Tenant)Id\s*\("
                r"|\.(?:organizationId|companyId|workspaceId|tenantId|organization_id|tenant_id)\b"
                r"|SecurityContextHolder|@AuthenticationPrincipal|\bPrincipal\b"
                r"|checkOwnership|verifyOwnership|assertTenant)",
                re.IGNORECASE,
            )
            for _, r in ctx.profile.all_active_roots:
                for jf in iter_repo_files(r, {".java", ".kt", ".ts", ".py"}):
                    scanned += 1
                    txt = jf.read_text(encoding="utf-8", errors="replace")
                    rel = jf.relative_to(r).as_posix()
                    for entity in sorted(scoped_entities):
                        repo_pat = re.compile(
                            rf"\b([A-Za-z0-9_]*{re.escape(entity)}Repository|repo|repository)\.(?:findById|deleteById)\s*\(",
                            re.IGNORECASE,
                        )
                        if entity not in txt:
                            continue
                        for m in repo_pat.finditer(txt):
                            # Inspect enclosing method window around the raw findById/deleteById call
                            brace_open = txt.rfind("{", 0, m.start())
                            brace_close = txt.find("}", m.end())
                            method_body = txt[
                                brace_open if brace_open != -1 else max(0, m.start() - 160) : (
                                    brace_close + 1 if brace_close != -1 else min(len(txt), m.end() + 220)
                                )
                            ]
                            if not ownership_guard_re.search(method_body):
                                mline = txt[: m.start()].count("\n") + 1
                                lines = txt.splitlines()
                                facts.append(
                                    Fact.create(
                                        fact_id=f"AUTHZ-OWN-{len(facts)+1:03d}",
                                        code="RESOURCE_OWNERSHIP_GAP",
                                        category="SECURITY",
                                        fact_type="structural",
                                        severity="CRITICAL",
                                        summary=(
                                            f"Scoped entity `{entity}` is accessed via raw `findById/deleteById` in "
                                            f"`{rel}:{mline}` without organization/tenant ownership verification (IDOR risk)."
                                        ),
                                        location=f"{rel}:{mline}",
                                        evidence=[
                                            EvidenceRef(
                                                kind="code",
                                                level="L1",
                                                derivation="syntax",
                                                ref=f"{rel}:{mline}",
                                                line=mline,
                                                excerpt=lines[mline - 1].strip()[:160] if mline - 1 < len(lines) else "",
                                            )
                                        ],
                                        attrs={"entity": entity, "tenancy_model": ctx.profile.tenancy_model},
                                    )
                                )

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            facts=facts,
            coverage=CoverageReport(scanned_files=scanned + len(endpoints)),
        )
