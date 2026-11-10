#!/usr/bin/env python3
"""Global Cross-Codebase API & Specification Reconciler.

Scans backend controllers and frontend client API calls across projects,
cross-references existing API docs (docs/APIs/), RFCs, and PRDs, and outputs
a structured reconciliation matrix highlighting documentation drift,
contract mismatches, orphaned frontend links/stubs, and spec contradictions.
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
FE_EXTENDED_CLIENT_RE = re.compile(
    r"\b(?:api|http|client|requestService)\.(?:get|post|put|patch|delete)\s*\(\s*[`\"']([^`\"'\s\?]+)",
    re.IGNORECASE,
)
FE_TEMPLATE_LITERAL_RE = re.compile(
    r"(?:[`\"'])(/api/v[0-9]+/[^`\"'\s\?]+|/api/[^`\"'\s\?]+)(?:[`\"'])",
    re.IGNORECASE,
)

# Frontend UI Links & Navigation (React Router, Next.js, HTML)
FE_LINK_RE = re.compile(
    r"<(?:Link|NavLink)\b[^>]*?\b(?:to|href)\s*=\s*[\"']([^\"'#?]+)[\"']",
    re.IGNORECASE,
)
FE_A_HREF_RE = re.compile(
    r"<a\b[^>]*?\bhref\s*=\s*[\"'](/[^\"'#?]+)[\"']",
    re.IGNORECASE,
)
FE_NAVIGATE_RE = re.compile(
    r"\b(?:navigate|router\.push)\s*\(\s*[\"'](/[^\"'#?]+)[\"']",
    re.IGNORECASE,
)
FE_NAV_OBJ_RE = re.compile(
    r"\b(?:to|href|path)\s*:\s*[\"'](/[^\"'#?]+)[\"']",
    re.IGNORECASE,
)

# Stub markers & "connect backend later" indicators
FE_STUB_LINK_RE = re.compile(
    r"""<(?:a|Link|NavLink|Button)\b[^>]*?\b(?:href|to)\s*=\s*["'](#|/todo|/placeholder|/coming-soon|javascript:void\(0\)|)["']""",
    re.IGNORECASE,
)
FE_TODO_BACKEND_RE = re.compile(
    r"(?://|/\*)\s*(?:TODO|FIXME|STUB)[:\s]*(.*?(?:backend|api|endpoint|servis|bağla).*?)(?:\*/|\r?\n|$)",
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
class FrontendCall:
    url: str
    source_file: str
    line: int
    call_type: str = "API_CALL"  # API_CALL, ROUTE_LINK, STUB_MARKER


@dataclass
class DriftFinding:
    type: str  # DOCS_DRIFT, CONTRACT_MISMATCH, ORPHAN_FRONTEND_LINK, STUB_BACKEND_PENDING, RFC_DRIFT, SPEC_CONTRADICTION
    severity: str  # CRITICAL, WARNING, INFO
    title: str
    details: str
    target_file: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)


def discover_rfc_files(root: Path, explicit_path: Optional[Path] = None) -> List[Path]:
    """Projedeki tüm RFC dokümanlarını dinamik ve esnek biçimde keşfeder."""
    if explicit_path and explicit_path.exists():
        if explicit_path.is_file() and explicit_path.suffix.lower() == ".md":
            return [explicit_path]
        if explicit_path.is_dir():
            files = sorted(list(explicit_path.rglob("*.md")))
            if files:
                return files

    found: List[Path] = []
    seen: Set[str] = set()

    # Olası RFC dizinleri
    candidate_dirs = [
        root / "RFCs",
        root / "rfcs",
        root / "RFC",
        root / "docs" / "rfc",
        root / "docs" / "RFCs",
        root / "docs" / "rfcs",
        root / "docs" / "RFC",
        root / "specs" / "rfc",
        root / "specs",
    ]

    for c_dir in candidate_dirs:
        if c_dir.is_dir():
            for p in c_dir.rglob("*.md"):
                p_res = p.resolve()
                name_lower = p.name.lower()
                if any(k in name_lower for k in ("prd", "sartname")):
                    continue
                if str(p_res) not in seen and not any(
                    part.lower() in ("node_modules", ".git", "target", "build", "dist", ".next")
                    for part in p.parts
                ):
                    seen.add(str(p_res))
                    found.append(p)

    # Kök ve docs altındaki *rfc*.md isimli tekil dosyalar
    for p in root.glob("*.md"):
        name_lower = p.name.lower()
        if "rfc" in name_lower and "prd" not in name_lower:
            p_res = p.resolve()
            if str(p_res) not in seen:
                seen.add(str(p_res))
                found.append(p)

    return sorted(found)


def discover_prd_files(root: Path, explicit_path: Optional[Path] = None) -> List[Path]:
    """Projedeki tüm PRD ve şartname dokümanlarını dinamik olarak keşfeder."""
    if explicit_path and explicit_path.exists():
        if explicit_path.is_file():
            return [explicit_path]
        if explicit_path.is_dir():
            files = sorted(list(explicit_path.rglob("*.md")))
            if files:
                return files

    found: List[Path] = []
    seen: Set[str] = set()

    # Kökteki doğrudan adaylar
    for cand_name in ["PRODUCT.md", "PRD.md", "prd.md", "SPEC.md", "spec.md"]:
        candidate = root / cand_name
        if candidate.is_file():
            p_res = candidate.resolve()
            if str(p_res) not in seen:
                seen.add(str(p_res))
                found.append(candidate)

    # docs/ ve RFCs/ altındaki PRD/spec dosyaları
    for sub in ["docs", "RFCs", "rfcs", "specs"]:
        sub_dir = root / sub
        if sub_dir.is_dir():
            for p in sub_dir.rglob("*.md"):
                name_lower = p.name.lower()
                if any(k in name_lower for k in ("prd", "spec", "sartname", "product")):
                    p_res = p.resolve()
                    if str(p_res) not in seen and not any(
                        part.lower() in ("node_modules", ".git", "target", "build", "dist", ".next")
                        for part in p.parts
                    ):
                        seen.add(str(p_res))
                        found.append(p)

    return sorted(found)


def discover_api_docs_path(root: Path, explicit_path: Optional[Path] = None) -> Optional[Path]:
    """API doküman dizinini esnek biçimde tespit eder."""
    if explicit_path and explicit_path.exists() and explicit_path.is_dir():
        return explicit_path

    candidates = [
        root / "docs" / "APIs",
        root / "docs" / "apis",
        root / "docs" / "api",
        root / "APIs",
        root / "apis",
        root / "api_docs",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return None


class ReconcileScanner:
    def __init__(
        self,
        backend_path: Optional[Path] = None,
        frontend_path: Optional[Path] = None,
        docs_api_path: Optional[Path] = None,
        rfc_path: Optional[Path] = None,
        prd_path: Optional[Path] = None,
        project_root: Optional[Path] = None,
    ):
        self.project_root = project_root or Path.cwd()
        self.backend_path = backend_path
        self.frontend_path = frontend_path
        self.docs_api_path = docs_api_path
        self.rfc_path = rfc_path
        self.prd_path = prd_path

        self.backend_endpoints: List[Endpoint] = []
        self.frontend_calls: List[FrontendCall] = []
        self.frontend_links: List[FrontendCall] = []
        self.stub_markers: List[Dict[str, Any]] = []
        self.api_doc_paths: Set[str] = set()
        self.rfc_files: List[Path] = []
        self.prd_files: List[Path] = []
        self.findings: List[DriftFinding] = []

    def scan_backend(self) -> None:
        if not self.backend_path or not self.backend_path.exists():
            return

        for root, _, files in os.walk(self.backend_path):
            if any(skip in root for skip in ("target", "node_modules", ".git", "build", "dist", ".next")):
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
            if any(skip in root for skip in ("node_modules", ".git", "dist", ".next", "build", "coverage")):
                continue
            for file in files:
                ext = Path(file).suffix.lower()
                if ext not in (".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte"):
                    continue

                full_path = Path(root) / file
                try:
                    content = full_path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue

                for lineno, line in enumerate(content.splitlines(), 1):
                    # 1. API Call Invocations (fetch, axios, apiClient, api, http)
                    for match in FE_FETCH_RE.finditer(line):
                        url = match.group(1).strip()
                        self.frontend_calls.append(
                            FrontendCall(url=url, source_file=str(full_path), line=lineno, call_type="API_CALL")
                        )
                    for match in FE_EXTENDED_CLIENT_RE.finditer(line):
                        url = match.group(1).strip()
                        if not any(c.url == url and c.line == lineno for c in self.frontend_calls):
                            self.frontend_calls.append(
                                FrontendCall(url=url, source_file=str(full_path), line=lineno, call_type="API_CALL")
                            )
                    for match in FE_TEMPLATE_LITERAL_RE.finditer(line):
                        url = match.group(1).strip()
                        if not any(c.url == url and c.line == lineno for c in self.frontend_calls):
                            self.frontend_calls.append(
                                FrontendCall(url=url, source_file=str(full_path), line=lineno, call_type="API_CALL")
                            )

                    # 2. UI Navigation & Page Links (Link to, NavLink, a href, router.push, navigate)
                    for match in FE_LINK_RE.finditer(line):
                        link_target = match.group(1).strip()
                        if link_target.startswith("/"):
                            self.frontend_links.append(
                                FrontendCall(url=link_target, source_file=str(full_path), line=lineno, call_type="ROUTE_LINK")
                            )
                    for match in FE_A_HREF_RE.finditer(line):
                        link_target = match.group(1).strip()
                        self.frontend_links.append(
                            FrontendCall(url=link_target, source_file=str(full_path), line=lineno, call_type="ROUTE_LINK")
                        )
                    for match in FE_NAVIGATE_RE.finditer(line):
                        link_target = match.group(1).strip()
                        self.frontend_links.append(
                            FrontendCall(url=link_target, source_file=str(full_path), line=lineno, call_type="ROUTE_LINK")
                        )
                    for match in FE_NAV_OBJ_RE.finditer(line):
                        link_target = match.group(1).strip()
                        if not any(l.url == link_target and l.line == lineno for l in self.frontend_links):
                            self.frontend_links.append(
                                FrontendCall(url=link_target, source_file=str(full_path), line=lineno, call_type="ROUTE_LINK")
                            )

                    # 3. Stub Links & "Connect Backend Later" markers
                    stub_match = FE_STUB_LINK_RE.search(line)
                    if stub_match:
                        marker = stub_match.group(1).strip()
                        self.stub_markers.append({
                            "type": "STUB_LINK",
                            "marker": marker or '""',
                            "source_file": str(full_path),
                            "line": lineno,
                            "snippet": line.strip(),
                        })

                    todo_match = FE_TODO_BACKEND_RE.search(line)
                    if todo_match:
                        comment_text = todo_match.group(1).strip()
                        self.stub_markers.append({
                            "type": "TODO_BACKEND",
                            "marker": comment_text,
                            "source_file": str(full_path),
                            "line": lineno,
                            "snippet": line.strip(),
                        })

    def scan_api_docs(self) -> None:
        effective_docs_path = discover_api_docs_path(self.project_root, self.docs_api_path)
        if not effective_docs_path or not effective_docs_path.exists():
            return

        self.docs_api_path = effective_docs_path
        for root, _, files in os.walk(effective_docs_path):
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
        self.rfc_files = discover_rfc_files(self.project_root, self.rfc_path)

    def scan_prds(self) -> None:
        self.prd_files = discover_prd_files(self.project_root, self.prd_path)

    def cross_analyze(self) -> None:
        be_paths = {ep.path for ep in self.backend_endpoints}

        # 1. Undocumented Backend Endpoints (Docs Drift)
        for ep in self.backend_endpoints:
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
                            f"Option A: Add documentation for '{ep.method} {ep.path}' to docs/APIs/",
                            "Option B: Verify request/response body schemas and auth headers",
                        ],
                    )
                )

        # 2. Frontend / Backend Contract Mismatch (Orphan Client API Calls)
        if self.frontend_path and self.frontend_calls:
            for fe_call in self.frontend_calls:
                fe_url = fe_call.url.split("?")[0]
                matched = any(
                    fe_url == be_p or re.sub(r"\$\{[^\}]+\}", "[^/]+", fe_url) == be_p
                    for be_p in be_paths
                )
                if not matched and (fe_url.startswith("/api/") or "/api/" in fe_url or fe_url.startswith("/v1/")):
                    self.findings.append(
                        DriftFinding(
                            type="CONTRACT_MISMATCH",
                            severity="CRITICAL",
                            title=f"Orphan Frontend API Call: {fe_url}",
                            details=f"Frontend calls '{fe_url}' in {fe_call.source_file}:{fe_call.line} but no matching Backend route was found.",
                            target_file=fe_call.source_file,
                            suggested_actions=[
                                f"Option A: Implement missing endpoint '{fe_url}' in Backend Controller",
                                f"Option B: Correct Frontend route URL if typo exists in {fe_call.source_file}",
                            ],
                        )
                    )

        # 3. Orphaned / Unwired Frontend Links ("Sonradan Backend Yazılacak" Rotalar)
        if self.frontend_path and self.frontend_links:
            seen_unwired_routes: Set[str] = set()
            for link in self.frontend_links:
                route_url = link.url.split("?")[0]
                if route_url in seen_unwired_routes or route_url in ("/", "/login", "/home"):
                    continue

                # Rota /api/ ile başlıyorsa ve backend'de yoksa veya
                # rota belirli bir domain varlığına işaret ediyor ve backend'de ilgili controller yoksa
                is_api_link = route_url.startswith("/api/")
                # Slug parçası çıkar (örn /reports -> reports)
                slug_fragment = route_url.strip("/").split("/")[0] if route_url.strip("/") else ""

                has_be_match = any(
                    route_url == be_p or (slug_fragment and slug_fragment in be_p.lower())
                    for be_p in be_paths
                )

                if is_api_link and not any(route_url == be_p for be_p in be_paths):
                    seen_unwired_routes.add(route_url)
                    self.findings.append(
                        DriftFinding(
                            type="ORPHAN_FRONTEND_LINK",
                            severity="CRITICAL",
                            title=f"Unwired Frontend API Link: {route_url}",
                            details=f"Frontend links to '{route_url}' in {link.source_file}:{link.line} but no backend endpoint exists.",
                            target_file=link.source_file,
                            suggested_actions=[
                                f"Option A: Create Backend endpoint for '{route_url}'",
                                f"Option B: Fix or update frontend navigation target in {link.source_file}",
                            ],
                        )
                    )
                elif slug_fragment and not has_be_match and len(self.backend_endpoints) > 0:
                    # Geliştiricinin menüye/butona koyduğu ama backend'de henüz veri rotası olmayan rotalar
                    # Sadece feature-like rotaları yakala (örn /analytics, /export, /admin/...)
                    if any(feat in route_url.lower() for feat in ("report", "export", "admin", "analytic", "invoice", "payment", "audit", "billing", "metric")):
                        seen_unwired_routes.add(route_url)
                        self.findings.append(
                            DriftFinding(
                                type="ORPHAN_FRONTEND_LINK",
                                severity="WARNING",
                                title=f"Frontend Feature Link Without Backend: {route_url}",
                                details=f"Frontend references route '{route_url}' in {link.source_file}:{link.line} but no matching backend controller/service was found for '{slug_fragment}'.",
                                target_file=link.source_file,
                                suggested_actions=[
                                    f"Option A: Implement supporting Backend REST Controller for '{slug_fragment}'",
                                    f"Option B: Verify if '{route_url}' is a pure client-side view or mock page",
                                ],
                            )
                        )

        # 4. Stub Markers & "Connect Backend Later" Indicators
        for stub in self.stub_markers:
            s_type = stub["type"]
            marker = stub["marker"]
            self.findings.append(
                DriftFinding(
                    type="STUB_BACKEND_PENDING",
                    severity="WARNING" if s_type == "TODO_BACKEND" else "INFO",
                    title=f"Pending Backend Hook [{s_type}]: {marker[:50]}",
                    details=f"Found '{stub['snippet']}' at {stub['source_file']}:{stub['line']}. Indicates code written with intent to wire backend later.",
                    target_file=stub["source_file"],
                    suggested_actions=[
                        "Option A: Implement the required backend endpoint and wire the action",
                        "Option B: Remove placeholder/TODO if feature is deprecated",
                    ],
                )
            )

        # 5. RFC Drift Detection
        for rfc in self.rfc_files:
            try:
                content = rfc.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            if "## Uygulama Gerçekliği" not in content and "## As-Built Status" not in content:
                self.findings.append(
                    DriftFinding(
                        type="RFC_DRIFT",
                        severity="INFO",
                        title=f"RFC Lacks As-Built Addendum: {rfc.name}",
                        details=f"RFC '{rfc.name}' ({rfc.relative_to(self.project_root).as_posix() if rfc.is_relative_to(self.project_root) else rfc.name}) lacks As-Built section.",
                        target_file=str(rfc),
                        suggested_actions=[
                            f"Option A: Append '## Uygulama Gerçekliği & Revizyon Notu (As-Built)' to {rfc.name}",
                            "Option B: Reconcile any design divergence with live codebase",
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
            f"- **Frontend Navigation Links:** {len(self.frontend_links)}",
            f"- **Stub / Pending Markers:** {len(self.stub_markers)}",
            f"- **Documented Endpoints in Docs:** {len(self.api_doc_paths)}",
            f"- **RFC Documents Discovered:** {len(self.rfc_files)}",
            f"- **PRD Documents Discovered:** {len(self.prd_files)}",
            f"- **Total Drift Findings:** {len(self.findings)}",
            "",
        ]

        if self.rfc_files:
            lines.append("### 📁 Keşfedilen RFC Dokümanları:")
            for r in self.rfc_files:
                r_rel = r.relative_to(self.project_root).as_posix() if r.is_relative_to(self.project_root) else r.name
                lines.append(f"- `{r_rel}`")
            lines.append("")

        if self.prd_files:
            lines.append("### 📄 Keşfedilen PRD / Şartname Dokümanları:")
            for p in self.prd_files:
                p_rel = p.relative_to(self.project_root).as_posix() if p.is_relative_to(self.project_root) else p.name
                lines.append(f"- `{p_rel}`")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 🔍 Detected Findings & Reconciliation Matrix",
            "",
        ])

        if not self.findings:
            lines.append("✅ **Zero Drift:** All codebases, API documentation, frontend links, and RFCs are synchronized.")
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

        lines.extend([
            "### 🛑 ONAY KAPISI (APPROVAL GATE)",
            "> Bu rapor bir Uzlaşma Planı taslağıdır. Kullanıcı açık onay vermeden (`proceed` / `onay`)",
            "> kod tabanında veya dokümanlarda tek taraflı değişiklik yapılamaz.",
        ])

        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Global Cross-Codebase API & Specification Reconciler"
    )
    parser.add_argument("--backend", type=str, help="Path to Backend codebase root")
    parser.add_argument("--frontend", type=str, help="Path to Frontend codebase root")
    parser.add_argument("--docs-api", type=str, default=None, help="Path to API docs directory")
    parser.add_argument("--rfcs", type=str, default=None, help="Path to RFCs directory")
    parser.add_argument("--prd", type=str, default=None, help="Path to PRD / Product requirements doc")
    parser.add_argument("--output-plan", type=str, help="Path to write the reconciliation markdown plan")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    curr_root = Path.cwd().resolve()
    be_path = Path(args.backend).resolve() if args.backend else None
    fe_path = Path(args.frontend).resolve() if args.frontend else None
    docs_api_path = Path(args.docs_api).resolve() if args.docs_api and Path(args.docs_api).exists() else None
    rfc_path = Path(args.rfcs).resolve() if args.rfcs and Path(args.rfcs).exists() else None
    prd_path = Path(args.prd).resolve() if args.prd and Path(args.prd).exists() else None

    # Fallback to current directory if neither be nor fe was explicitly passed
    if not be_path and not fe_path:
        be_path = curr_root

    scanner = ReconcileScanner(
        backend_path=be_path,
        frontend_path=fe_path,
        docs_api_path=docs_api_path,
        rfc_path=rfc_path,
        prd_path=prd_path,
        project_root=curr_root,
    )

    scanner.scan_backend()
    scanner.scan_frontend()
    scanner.scan_api_docs()
    scanner.scan_rfcs()
    scanner.scan_prds()
    scanner.cross_analyze()

    if args.json:
        data = {
            "backend_endpoints": [asdict(e) for e in scanner.backend_endpoints],
            "frontend_calls": [asdict(c) for c in scanner.frontend_calls],
            "frontend_links": [asdict(l) for l in scanner.frontend_links],
            "stub_markers": scanner.stub_markers,
            "documented_endpoints": list(scanner.api_doc_paths),
            "rfc_files": [str(p) for p in scanner.rfc_files],
            "prd_files": [str(p) for p in scanner.prd_files],
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
