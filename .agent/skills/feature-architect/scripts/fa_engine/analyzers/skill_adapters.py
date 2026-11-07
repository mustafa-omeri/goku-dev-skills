# -*- coding: utf-8 -*-
"""Optional Skill Output Adapter (`skill_adapters.py`).

Prevents God-skill duplication by ingesting existing structured JSON reports emitted
by sibling skills (`security-audit`, `prelaunch`, `code-review`) when present in `docs/plans/`.
"""
from __future__ import annotations

import json

from ..model import CoverageReport, EvidenceRef, Fact, ProjectProfile
from .base import AnalyzerContext, AnalyzerResult


class SkillAdaptersAnalyzer:
    name = "skill_adapters"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        plans_dir = profile.root / "docs" / "plans"
        if plans_dir.is_dir() and any(plans_dir.glob("*audit*.json")):
            return True, "Found sibling skill audit JSON artifact(s)"
        return False, "No pre-computed sibling skill JSON reports in docs/plans/"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        applicable, reason = self.applies(ctx.profile)
        if not applicable:
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
            )

        plans_dir = ctx.profile.root / "docs" / "plans"
        facts: list[Fact] = []
        scanned = 0
        for jf in sorted(plans_dir.glob("*audit*.json")):
            scanned += 1
            rel = jf.relative_to(ctx.profile.root).as_posix()
            try:
                data = json.loads(jf.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            for item in data.get("findings", []) if isinstance(data, dict) else []:
                if not isinstance(item, dict):
                    continue
                facts.append(
                    Fact.create(
                        fact_id=f"ADAPT-{len(facts)+1:03d}",
                        code="SIBLING_SKILL_FINDING",
                        category=str(item.get("category", "SECURITY")),
                        fact_type="structural",
                        severity=str(item.get("severity", "MEDIUM")),
                        summary=str(item.get("summary", item.get("title", "Imported finding"))),
                        location=str(item.get("location", f"{rel}:1")),
                        evidence=[
                            EvidenceRef(
                                kind="doc",
                                level="L1",
                                derivation="config",
                                ref=f"{rel}:1",
                                line=1,
                                excerpt=str(item.get("id", jf.name)),
                            )
                        ],
                    )
                )

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            facts=facts,
            coverage=CoverageReport(scanned_files=scanned),
        )
