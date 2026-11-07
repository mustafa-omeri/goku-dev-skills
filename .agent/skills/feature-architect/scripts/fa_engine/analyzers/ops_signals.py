# -*- coding: utf-8 -*-
"""Operations, Observability & Performance Signals Analyzer (`ops_signals.py`).

Scans static operational readiness (health checks, structured logging, tracing, rate limits,
idempotency) and flags static N+1 query loop candidates as `INFERRED` behavioral facts.
"""
from __future__ import annotations

import re

from ..model import CoverageReport, EvidenceRef, Fact, ProjectProfile, iter_repo_files
from .base import AnalyzerContext, AnalyzerResult

JAVA_LOOP_REPO_RE = re.compile(
    r"\b(?:for|while)\s*\([^)]*\)\s*\{[^}]{0,600}?\b([A-Za-z0-9_]*(?:Repository|Repo|Dao))\.(find\w+|getBy\w+|save\w*)\s*\(",
    re.MULTILINE | re.DOTALL,
)
TS_LOOP_ORM_RE = re.compile(
    r"\bfor\s*\([^)]*\)\s*\{[^}]{0,600}?\bawait\s+(?:prisma|db|repo|repository)\.[A-Za-z0-9_.]+\s*\(",
    re.MULTILINE | re.DOTALL,
)


class OperationsSignalsAnalyzer:
    name = "ops_signals"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        if profile.backend_stacks:
            return True, "Backend stack present for operational & N+1 signal inspection"
        for _, r in profile.all_active_roots:
            for _ in iter_repo_files(r, {".java", ".kt", ".py"}):
                return True, "Server source files present"
        return False, "No backend service code detected"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        applicable, reason = self.applies(ctx.profile)
        if not applicable:
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
            )

        facts: list[Fact] = []
        scanned = 0
        signals = {
            "health_endpoint": False,
            "structured_logging": False,
            "tracing": False,
            "rate_limiting": False,
            "retry_or_circuit_breaker": False,
        }

        for _, r in ctx.profile.all_active_roots:
            for fp in iter_repo_files(r, {".java", ".kt", ".ts", ".js", ".py", ".xml", ".json", ".yml", ".yaml"}):
                scanned += 1
                rel = fp.relative_to(r).as_posix()
                txt = fp.read_text(encoding="utf-8", errors="replace")
                low = txt.lower()

                if "actuator" in low or "/health" in low:
                    signals["health_endpoint"] = True
                if "slf4j" in low or "pino" in low or "winston" in low or "structlog" in low:
                    signals["structured_logging"] = True
                if "opentelemetry" in low or "micrometer-tracing" in low or "sentry" in low:
                    signals["tracing"] = True
                if "bucket4j" in low or "ratelimit" in low or "throttler" in low or "slowapi" in low:
                    signals["rate_limiting"] = True
                if "resilience4j" in low or "retryable" in low or "tenacity" in low:
                    signals["retry_or_circuit_breaker"] = True

                if fp.suffix.lower() in {".java", ".kt"}:
                    lines = txt.splitlines()
                    for m in JAVA_LOOP_REPO_RE.finditer(txt):
                        mline = txt[: m.start()].count("\n") + 1
                        facts.append(
                            Fact.create(
                                fact_id=f"OPS-N1-{len(facts)+1:03d}",
                                code="STATIC_N_PLUS_ONE_CANDIDATE",
                                category="PERFORMANCE",
                                fact_type="behavioral",
                                severity="MEDIUM",
                                summary=(
                                    f"Loop in `{rel}:{mline}` invokes `{m.group(1)}.{m.group(2)}(...)` per iteration "
                                    f"(N+1 query candidate; verify batching/`findAllById`)."
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
                                requested_status="INFERRED",
                            )
                        )
                elif fp.suffix.lower() in {".ts", ".js"}:
                    lines = txt.splitlines()
                    for m in TS_LOOP_ORM_RE.finditer(txt):
                        mline = txt[: m.start()].count("\n") + 1
                        facts.append(
                            Fact.create(
                                fact_id=f"OPS-N1-{len(facts)+1:03d}",
                                code="STATIC_N_PLUS_ONE_CANDIDATE",
                                category="PERFORMANCE",
                                fact_type="behavioral",
                                severity="MEDIUM",
                                summary=f"Sequential `await` database query inside loop at `{rel}:{mline}` (N+1 query candidate).",
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
                                requested_status="INFERRED",
                            )
                        )

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            facts=facts,
            coverage=CoverageReport(scanned_files=scanned),
            artifacts={"operational_signals": signals},
        )
