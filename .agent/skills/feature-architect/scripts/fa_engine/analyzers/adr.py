# -*- coding: utf-8 -*-
"""Architecture Decision Intelligence Analyzer (`adr.py`).

Discovers explicit ADRs (`docs/adr/*.md`, `PROJECT_BRIEF.md` §3) and infers implicit
architectural decisions (`INFERRED`) when formal ADR records are absent.
"""
from __future__ import annotations

from ..model import CoverageReport, EvidenceRef, Fact, Node, ProjectProfile, iter_repo_files
from .base import AnalyzerContext, AnalyzerResult


class AdrIntelligenceAnalyzer:
    name = "adr"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        if profile.topology == "cli-or-library":
            return False, "Lightweight CLI/library without multi-layer architectural ADR requirement"
        return True, "Multi-module or full-stack architecture decision tracking"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        applicable, reason = self.applies(ctx.profile)
        if not applicable:
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
            )

        nodes: list[Node] = []
        facts: list[Fact] = []
        scanned = 0
        explicit_adrs: list[str] = []

        for label, r in ctx.profile.all_active_roots:
            adr_dir = r / "docs" / "adr"
            if adr_dir.is_dir():
                for md in sorted(adr_dir.glob("*.md")):
                    scanned += 1
                    rel = md.relative_to(r).as_posix()
                    explicit_adrs.append(rel)
                    nodes.append(
                        Node(id=f"Adr:{md.stem}", kind="Adr", name=md.stem, file=rel, line=1, root_label=label)
                    )

        # Count non-test source files to avoid noise on tiny 1-file snippets
        source_count = sum(
            1
            for _, r in ctx.profile.all_active_roots
            for _ in iter_repo_files(r, {".ts", ".tsx", ".js", ".java", ".kt", ".py"})
        )

        if not explicit_adrs and source_count >= 3:
            inferred_choices: list[str] = [f"topology={ctx.profile.topology}"]
            if ctx.profile.frontend_stacks:
                inferred_choices.append(f"frontend={','.join(ctx.profile.frontend_stacks)}")
            if ctx.profile.backend_stacks:
                inferred_choices.append(f"backend={','.join(ctx.profile.backend_stacks)}")
            if ctx.profile.tenancy_model != "unknown":
                inferred_choices.append(f"tenancy={ctx.profile.tenancy_model}")

            anchor_ref = "package.json"
            for cand_manifest in ("package.json", "pom.xml", "build.gradle", "build.gradle.kts", "pyproject.toml", "requirements.txt"):
                if (ctx.profile.root / cand_manifest).is_file():
                    anchor_ref = cand_manifest
                    break
            else:
                for first_src in iter_repo_files(ctx.profile.root, {".ts", ".tsx", ".js", ".java", ".kt", ".py"}):
                    anchor_ref = first_src.relative_to(ctx.profile.root).as_posix()
                    break
            facts.append(
                Fact.create(
                    fact_id="ADR-IMP-001",
                    code="INFERRED_IMPLICIT_ADR",
                    category="ARCHITECTURE",
                    fact_type="behavioral",
                    severity="LOW",
                    summary=(
                        f"No formal ADR documents found under `docs/adr/`; implicit architectural baseline "
                        f"({'; '.join(inferred_choices)}) is undocumented."
                    ),
                    location=f"{anchor_ref}:1",
                    evidence=[
                        EvidenceRef(
                            kind="doc",
                            level="L1",
                            derivation="manifest",
                            ref=f"{anchor_ref}:1",
                            line=1,
                            excerpt="; ".join(inferred_choices),
                        )
                    ],
                    requested_status="INFERRED",
                    attrs={"implicit_decisions": inferred_choices},
                )
            )

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            nodes=nodes,
            facts=facts,
            coverage=CoverageReport(scanned_files=scanned),
            artifacts={"explicit_adrs": explicit_adrs},
        )
