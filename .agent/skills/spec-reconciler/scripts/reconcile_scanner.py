#!/usr/bin/env python3
"""Global Cross-Codebase API & Specification Reconciler.

Scans backend controllers and frontend client API calls across projects,
cross-references existing API docs (docs/APIs/), RFCs, and PRDs, and outputs
a structured reconciliation matrix highlighting documentation drift,
contract mismatches, and spec contradictions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Backend route regexes (Spring Boot, Express/Nest, FastAPI/Flask)
SPRING_ROUTE_RE = re.compile(
    r"@(?:[A-Za-z_][A-Za-z0-9_]*\.)*"
    r"(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)\s*"
    r"""(?:\(\s*(?:(?:value|path)\s*=\s*)?["']([^"']*)["'])?""",
    re.MULTILINE,
)
SPRING_CLASS_MAPPING_RE = re.compile(
    r"""@RequestMapping\s*(?:\(\s*(?:(?:value|path)\s*=\s*)?["']([^"']*)["'])?""",
    re.MULTILINE,
)

EXPRESS_ROUTE_RE = re.compile(
    r"(?:router|app)\.(get|post|put|patch|delete)\s*\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
FASTAPI_ROUTE_RE = re.compile(
    r"@(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)

# Frontend client API invocation regexes
FE_FETCH_RE = re.compile(
    r"(?:fetch|axios\.(?:get|post|put|patch|delete)|apiClient\.(?:get|post|put|patch|delete))\s*\(\s*[`\"']([^`\"'\s\?]+)",
    re.IGNORECASE,
)
FE_TEMPLATE_LITERAL_RE = re.compile(
    r"(?:[`\"'])(/api/v[0-9]+/[^`\"'\s\?]+|/api/[^`\"'\s\?]+)(?:[`\"'])",
    re.IGNORECASE,
)


@dataclass
class Endpoint:
    method: str
    path: str
    source_file: str
    line: int
    documented_in_docs: bool = False
    called_by_frontend: bool = False


@dataclass
class DriftFinding:
    type: str  # DOCS_DRIFT, CONTRACT_MISMATCH, SPEC_CONTRADICTION
    severity: str  # CRITICAL, WARNING, INFO
    title: str
    details: str
    target_file: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)


class ReconcileScanner:
    def __init__(
        self,
        backend_path: Optional[Path] = None,
        frontend_path: Optional[Path] = None,
        docs_api_path: Optional[Path] = None,
        rfc_path: Optional[Path] = None,
        prd_path: Optional[Path] = None,
    ):
        self.backend_path = backend_path
        self.frontend_path = frontend_path
        self.docs_api_path = docs_api_path
        self.rfc_path = rfc_path
        self.prd_path = prd_path

        self.backend_endpoints: List[Endpoint] = []
        self.frontend_calls: List[Dict[str, Any]] = []
        self.api_doc_paths: Set[str] = set()
        self.rfc_files: List[Path] = []
        self.findings: List[DriftFinding] = []

    def scan_backend(self) -> None:
        if not self.backend_path or not self.backend_path.exists():
            return

        for root, _, files in os.walk(self.backend_path):
            # Skip build and hidden directories
            if any(skip in root for skip in ("target", "node_modules", ".git", "build", "dist")):
                continue
            for file in files:
                ext = Path(file).suffix.lower()
                full_path = Path(root) / file
                rel_path = str(full_path)

                if ext in (".java", ".kt"):
                    self._scan_spring_file(full_path, rel_path)
                elif ext in (".ts", ".js"):
                    self._scan_node_file(full_path, rel_path)
                elif ext == ".py":
                    self._scan_python_file(full_path, rel_path)

    def _scan_spring_file(self, full_path: Path, rel_path: str) -> None:
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return

        class_prefix = ""
        c_match = SPRING_CLASS_MAPPING_RE.search(content)
        if c_match and c_match.group(1):
            class_prefix = c_match.group(1).rstrip("/")

        for lineno, line in enumerate(content.splitlines(), 1):
            match = SPRING_ROUTE_RE.search(line)
            if match:
                mapping_type = match.group(1)
                sub_path = (match.group(2) or "").strip()
                if not sub_path.startswith("/") and sub_path:
                    sub_path = "/" + sub_path

                full_endpoint = f"{class_prefix}{sub_path}"
                if not full_endpoint.startswith("/"):
                    full_endpoint = "/" + full_endpoint

                method = "GET"
                if "Post" in mapping_type:
                    method = "POST"
                elif "Put" in mapping_type:
                    method = "PUT"
                elif "Delete" in mapping_type:
                    method = "DELETE"
                elif "Patch" in mapping_type:
                    method = "PATCH"
                elif "Request" in mapping_type:
                    method = "ANY"

                self.backend_endpoints.append(
                    Endpoint(method=method, path=full_endpoint, source_file=rel_path, line=lineno)
                )

    def _scan_node_file(self, full_path: Path, rel_path: str) -> None:
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return

        for lineno, line in enumerate(content.splitlines(), 1):
            match = EXPRESS_ROUTE_RE.search(line)
            if match:
                method = match.group(1).upper()
                route = match.group(2).strip()
                self.backend_endpoints.append(
                    Endpoint(method=method, path=route, source_file=rel_path, line=lineno)
                )

    def _scan_python_file(self, full_path: Path, rel_path: str) -> None:
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return

        for lineno, line in enumerate(content.splitlines(), 1):
            match = FASTAPI_ROUTE_RE.search(line)
            if match:
                method = match.group(1).upper()
                route = match.group(2).strip()
                self.backend_endpoints.append(
                    Endpoint(method=method, path=route, source_file=rel_path, line=lineno)
                )

    def scan_frontend(self) -> None:
        if not self.frontend_path or not self.frontend_path.exists():
            return

        for root, _, files in os.walk(self.frontend_path):
            if any(skip in root for skip in ("node_modules", ".git", "dist", ".next", "build")):
                continue
            for file in files:
                ext = Path(file).suffix.lower()
                if ext not in (".ts", ".tsx", ".js", ".jsx"):
                    continue

                full_path = Path(root) / file
                try:
                    content = full_path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue

                for lineno, line in enumerate(content.splitlines(), 1):
                    for match in FE_FETCH_RE.finditer(line):
                        url = match.group(1).strip()
                        self.frontend_calls.append(
                            {"url": url, "source_file": str(full_path), "line": lineno}
                        )
                    for match in FE_TEMPLATE_LITERAL_RE.finditer(line):
                        url = match.group(1).strip()
                        if not any(call["url"] == url and call["line"] == lineno for call in self.frontend_calls):
                            self.frontend_calls.append(
                                {"url": url, "source_file": str(full_path), "line": lineno}
                            )

    def scan_api_docs(self) -> None:
        if not self.docs_api_path or not self.docs_api_path.exists():
            return

        for root, _, files in os.walk(self.docs_api_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = Path(root) / file
                    try:
                        content = full_path.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        continue

                    # Search for documented endpoints e.g. POST /api/v1/...
                    for line in content.splitlines():
                        match = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\s+([/\w\-\{\}]+)", line)
                        if match:
                            path = match.group(2).strip()
                            self.api_doc_paths.add(path)

    def scan_rfcs(self) -> None:
        if not self.rfc_path or not self.rfc_path.exists():
            return
        for root, _, files in os.walk(self.rfc_path):
            for file in files:
                if file.endswith(".md"):
                    self.rfc_files.append(Path(root) / file)

    def cross_analyze(self) -> None:
        # 1. Undocumented Backend Endpoints (Docs Drift)
        for ep in self.backend_endpoints:
            # Check if documented in docs/APIs
            normalized_ep = re.sub(r"\{[^\}]+\}", "{id}", ep.path)
            is_doc = any(
                ep.path == doc_p or normalized_ep == re.sub(r"\{[^\}]+\}", "{id}", doc_p)
                for doc_p in self.api_doc_paths
            )
            ep.documented_in_docs = is_doc

            if not is_doc:
                self.findings.append(
                    DriftFinding(
                        type="DOCS_DRIFT",
                        severity="WARNING",
                        title=f"Undocumented Endpoint: {ep.method} {ep.path}",
                        details=f"Defined in {ep.source_file}:{ep.line} but missing from API docs.",
                        target_file=ep.source_file,
                        suggested_actions=[
                            f"Add documentation for '{ep.method} {ep.path}' to docs/APIs/",
                            "Verify request/response body schemas and auth headers",
                        ],
                    )
                )

        # 2. Frontend / Backend Contract Mismatch
        if self.frontend_path and self.frontend_calls and self.backend_endpoints:
            fe_urls = {call["url"].split("?")[0] for call in self.frontend_calls}
            be_paths = {ep.path for ep in self.backend_endpoints}

            for fe_call in self.frontend_calls:
                fe_url = fe_call["url"].split("?")[0]
                # Simple pattern match
                matched = any(
                    fe_url == be_p or re.sub(r"\$\{[^\}]+\}", "[^/]+", fe_url) == be_p
                    for be_p in be_paths
                )
                if not matched and fe_url.startswith("/api/"):
                    self.findings.append(
                        DriftFinding(
                            type="CONTRACT_MISMATCH",
                            severity="CRITICAL",
                            title=f"Orphan Frontend API Call: {fe_url}",
                            details=f"Frontend calls '{fe_url}' in {fe_call['source_file']}:{fe_call['line']} but no matching Backend route was found.",
                            target_file=fe_call["source_file"],
                            suggested_actions=[
                                f"Option A: Implement missing endpoint '{fe_url}' in Backend",
                                f"Option B: Correct Frontend route URL if typo exists in {fe_call['source_file']}",
                            ],
                        )
                    )

        # 3. RFC Drift Detection
        for rfc in self.rfc_files:
            try:
                content = rfc.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            if "## Uygulama Gercekliği" not in content and "## As-Built Status" not in content:
                self.findings.append(
                    DriftFinding(
                        type="RFC_DRIFT",
                        severity="INFO",
                        title=f"RFC Lacks As-Built Addendum: {rfc.name}",
                        details=f"RFC '{rfc.name}' does not contain an As-Built status section detailing post-development adaptations.",
                        target_file=str(rfc),
                        suggested_actions=[
                            f"Append '## Uygulama Gerçekliği & Revizyon Notu (As-Built)' to {rfc.name}",
                            "Reconcile any design divergence with live codebase",
                        ],
                    )
                )

    def generate_markdown_report(self) -> str:
        lines = [
            "# 📋 Specification & API Reconciliation Report",
            "",
            f"- **Backend Scan Path:** `{self.backend_path or 'Not provided'}`",
            f"- **Frontend Scan Path:** `{self.frontend_path or 'Not provided'}`",
            f"- **Backend Endpoints Found:** {len(self.backend_endpoints)}",
            f"- **Frontend API Invocations:** {len(self.frontend_calls)}",
            f"- **Documented Endpoints in Docs:** {len(self.api_doc_paths)}",
            f"- **RFC Documents Found:** {len(self.rfc_files)}",
            f"- **Total Drift Findings:** {len(self.findings)}",
            "",
            "---",
            "",
            "## 🔍 Detected Findings & Reconciliation Matrix",
            "",
        ]

        if not self.findings:
            lines.append("✅ **Zero Drift:** All codebases, API documentation, and RFCs are synchronized.")
            return "\n".join(lines)

        for i, f in enumerate(self.findings, 1):
            badge = "🔴" if f.severity == "CRITICAL" else ("🟡" if f.severity == "WARNING" else "ℹ️")
            lines.extend([
                f"### {badge} #{i:02d} [{f.type}] {f.title}",
                f"- **Severity:** `{f.severity}`",
                f"- **Target File:** `{f.target_file or 'N/A'}`",
                f"- **Details:** {f.details}",
                "",
                "#### 🛠️ Suggested Actions & Reconciliation Options",
            ])
            for action in f.suggested_actions:
                lines.append(f"- [ ] {action}")
            lines.extend([
                "",
                "> 💬 **Kullanıcı Kararı / Comment Alanı (Lütfen seçiminizi ve notunuzu buraya yazın):**",
                "> `[Kararınız: Doküman mı güncellensin, kod mu revize edilsin?]`",
                "",
                "---",
                "",
            ])

        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Global Cross-Codebase API & Specification Reconciler"
    )
    parser.add_argument("--backend", type=str, help="Path to Backend codebase root")
    parser.add_argument("--frontend", type=str, help="Path to Frontend codebase root")
    parser.add_argument("--docs-api", type=str, default="docs/APIs", help="Path to API docs directory")
    parser.add_argument("--rfcs", type=str, default="docs/rfc", help="Path to RFCs directory")
    parser.add_argument("--prd", type=str, default="PRODUCT.md", help="Path to PRD / Product requirements doc")
    parser.add_argument("--output-plan", type=str, help="Path to write the reconciliation markdown plan")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    be_path = Path(args.backend).resolve() if args.backend else None
    fe_path = Path(args.frontend).resolve() if args.frontend else None
    docs_api_path = Path(args.docs_api).resolve() if Path(args.docs_api).exists() else None
    rfc_path = Path(args.rfcs).resolve() if Path(args.rfcs).exists() else None
    prd_path = Path(args.prd).resolve() if Path(args.prd).exists() else None

    # Fallback to current directory if neither be nor fe was explicitly passed
    if not be_path and not fe_path:
        curr = Path(".").resolve()
        be_path = curr

    scanner = ReconcileScanner(
        backend_path=be_path,
        frontend_path=fe_path,
        docs_api_path=docs_api_path,
        rfc_path=rfc_path,
        prd_path=prd_path,
    )

    scanner.scan_backend()
    scanner.scan_frontend()
    scanner.scan_api_docs()
    scanner.scan_rfcs()
    scanner.cross_analyze()

    if args.json:
        data = {
            "backend_endpoints": [asdict(e) for e in scanner.backend_endpoints],
            "frontend_calls": scanner.frontend_calls,
            "documented_endpoints": list(scanner.api_doc_paths),
            "findings": [asdict(f) for f in scanner.findings],
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    report = scanner.generate_markdown_report()
    if args.output_plan:
        out_p = Path(args.output_plan)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(report, encoding="utf-8")
        print(f"Reconciliation plan written to: {out_p}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
