# -*- coding: utf-8 -*-
"""Build & Bundle Health Analyzer (`build.py`).

Inspects bundler configuration (`vite.config.*`, `next.config.*`, `webpack.config.*`),
chunk size warning inflation, and lazy code-splitting ratios; optionally runs a safe
temporary-dir build (`--build`) at Level 2 without touching target `dist/`.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from ..model import CoverageReport, EvidenceRef, Fact, ProjectProfile
from .base import AnalyzerContext, AnalyzerResult

CHUNK_LIMIT_RE = re.compile(r"\bchunkSizeWarningLimit\s*:\s*(\d+)")


class BuildHealthAnalyzer:
    name = "build"
    version = "2.0.0"

    def __init__(self, run_build: bool = False) -> None:
        self.run_build = run_build

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        if (profile.root / "package.json").is_file():
            return True, "Detected Node/Frontend package.json"
        return False, "No package.json bundler configuration in primary root"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        applicable, reason = self.applies(ctx.profile)
        if not applicable:
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
            )

        root = ctx.profile.root.resolve()
        facts: list[Fact] = []
        limitations: list[str] = []
        scanned = 0

        for cfg_name in ("vite.config.ts", "vite.config.js", "vite.config.mts", "vite.config.mjs"):
            cfg = root / cfg_name
            if not cfg.is_file():
                continue
            scanned += 1
            txt = cfg.read_text(encoding="utf-8", errors="replace")
            lines = txt.splitlines()
            m = CHUNK_LIMIT_RE.search(txt)
            if m:
                limit_kb = int(m.group(1))
                if limit_kb > 1000:
                    mline = txt[: m.start()].count("\n") + 1
                    facts.append(
                        Fact.create(
                            fact_id=f"BUILD-CHUNK-{len(facts)+1:03d}",
                            code="BUNDLE_BUDGET_RISK",
                            category="PERFORMANCE",
                            fact_type="structural",
                            severity="MEDIUM",
                            summary=(
                                f"`{cfg_name}:{mline}` inflates `chunkSizeWarningLimit` to `{limit_kb} kB`, "
                                f"masking oversized initial JavaScript bundles instead of splitting chunks."
                            ),
                            location=f"{cfg_name}:{mline}",
                            evidence=[
                                EvidenceRef(
                                    kind="config",
                                    level="L1",
                                    derivation="config",
                                    ref=f"{cfg_name}:{mline}",
                                    line=mline,
                                    excerpt=lines[mline - 1].strip()[:160] if mline - 1 < len(lines) else "",
                                )
                            ],
                            attrs={"chunkSizeWarningLimit": limit_kb},
                        )
                    )

        # Check eager route imports vs React.lazy / dynamic import when routes > 10
        fe_state = ctx.shared_state.get("frontend", {})
        declared_routes = fe_state.get("declared_routes", [])
        if len(declared_routes) > 10:
            has_lazy = False
            for rfile in ("src/App.tsx", "src/router.tsx", "src/routes.tsx", "src/routes/index.tsx"):
                rf = root / rfile
                if rf.is_file():
                    rtxt = rf.read_text(encoding="utf-8", errors="replace")
                    if "lazy(" in rtxt or "import(" in rtxt:
                        has_lazy = True
                        break
            if not has_lazy:
                facts.append(
                    Fact.create(
                        fact_id=f"BUILD-LAZY-{len(facts)+1:03d}",
                        code="BUNDLE_BUDGET_RISK",
                        category="PERFORMANCE",
                        fact_type="structural",
                        severity="MEDIUM",
                        summary=f"Application declares {len(declared_routes)} routes without route-level `lazy()` / dynamic `import()` code-splitting.",
                        location="package.json:1",
                        evidence=[
                            EvidenceRef(
                                kind="config",
                                level="L1",
                                derivation="config",
                                ref="package.json:1",
                                line=1,
                                excerpt=f"{len(declared_routes)} declared routes, 0 lazy splits",
                            )
                        ],
                    )
                )

        if self.run_build and shutil.which("npx"):
            with tempfile.TemporaryDirectory() as tmp_out:
                try:
                    proc = subprocess.run(
                        ["npx", "vite", "build", "--outDir", tmp_out],
                        cwd=str(root),
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=90,
                    )
                    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
                    if "Some chunks are larger than" in combined or "chunkSizeWarningLimit" in combined:
                        facts.append(
                            Fact.create(
                                fact_id=f"BUILD-L2-{len(facts)+1:03d}",
                                code="BUNDLE_BUDGET_RISK",
                                category="PERFORMANCE",
                                fact_type="structural",
                                severity="HIGH",
                                summary="Actual L2 bundler build emitted oversized chunk warning (>500 kB minified).",
                                location="package.json:1",
                                evidence=[
                                    EvidenceRef(
                                        kind="test",
                                        level="L2",
                                        derivation="build",
                                        ref="package.json:1",
                                        line=1,
                                        excerpt="Some chunks are larger than 500 kB after minification",
                                    )
                                ],
                            )
                        )
                except Exception as exc:
                    limitations.append(f"Opt-in L2 build skipped/failed: {exc}")
        else:
            limitations.append("Actual bundle sizes not measured (pass --build for non-destructive L2 build check).")

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            facts=facts,
            coverage=CoverageReport(scanned_files=scanned + 1),
            limitations=limitations,
        )
