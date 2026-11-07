# -*- coding: utf-8 -*-
"""Multi-stack Backend Deterministic Analyzer (`backend.py`).

Supports JVM/Spring, Node (Express/NestJS/Fastify/Next API), Python (FastAPI/Django/Flask),
and OpenAPI endpoint/DTO extraction.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..discovery import extract_java_endpoints_quick
from ..model import CoverageReport, Edge, Node, ProjectProfile, iter_repo_files, normalize_api_path
from .base import AnalyzerContext, AnalyzerResult

EXPRESS_ROUTE_RE = re.compile(
    r"\b(?:app|router|server)\.(get|post|put|patch|delete)\s*\(\s*[\"'`](/[^\"'`]+)[\"'`]([^;\n]*)",
    re.IGNORECASE,
)
NEST_CTRL_RE = re.compile(r"@Controller\s*\(\s*[\"'`]([^\"'`]*)[\"'`]\s*\)")
NEST_METHOD_RE = re.compile(r"@(Get|Post|Put|Patch|Delete)\s*\(\s*(?:[\"'`]([^\"'`]*)[\"'`])?\s*\)")
PY_ROUTE_RE = re.compile(
    r"@(?:app|router|bp|blueprint)\.(get|post|put|patch|delete)\s*\(\s*[\"'](/[^\"']*)[\"']([^)]*)\)",
    re.IGNORECASE,
)
ROLE_ENUM_RE = re.compile(r"\benum\s+(\w*Role\w*)\s*\{([^}]*)\}", re.MULTILINE | re.DOTALL)
PREAUTH_RE = re.compile(r"@(?:PreAuthorize|Secured|RolesAllowed)\s*\(([^)]+)\)")
HAS_ROLE_RE = re.compile(r"has(?:Any)?(?:Role|Authority)\(([^)]+)\)")

JAVA_DTO_FIELD_RE = re.compile(
    r"^[ \t]*(?:@[A-Za-z0-9_()\"'=,\s]+\s+)*private[ \t]+(?:final[ \t]+)?([A-Za-z0-9_<>,?\[\]]+)[ \t]+([a-z][A-Za-z0-9_]*)[ \t]*(?:=|;)",
    re.MULTILINE,
)
JAVA_RECORD_COMP_RE = re.compile(r"\brecord\s+([A-Z][A-Za-z0-9_]*)\s*\(([^)]*)\)", re.MULTILINE | re.DOTALL)
PYDANTIC_CLASS_RE = re.compile(
    r"^class\s+([A-Z][A-Za-z0-9_]*)\s*\(\s*(?:BaseModel|Schema|serializers\.ModelSerializer)\s*\)\s*:\s*\n((?:[ \t]+.+\n)+)",
    re.MULTILINE,
)
PYDANTIC_FIELD_RE = re.compile(r"^[ \t]+([a-z_][A-Za-z0-9_]*)\s*:\s*([^\n=#]+)", re.MULTILINE)


class BackendAnalyzer:
    name = "backend"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        if profile.backend_stacks:
            return True, f"Detected backend stack(s): {', '.join(profile.backend_stacks)}"
        for _, r in profile.all_active_roots:
            for _ in iter_repo_files(r, {".java", ".kt", ".py"}):
                return True, "Detected backend source files"
        return False, "Pure client/static repository (no backend stack detected)"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        applicable, reason = self.applies(ctx.profile)
        nodes: list[Node] = []
        edges: list[Edge] = []
        scanned = 0
        endpoints: list[dict[str, Any]] = []
        dtos: dict[str, dict[str, Any]] = {}
        roles: list[dict[str, str]] = []
        seen_roles: set[str] = set()
        be_stacks: list[str] = list(ctx.profile.backend_stacks)
        url_security_rules: list[dict[str, Any]] = []

        # Also scan roles in primary frontend root for v1 compatibility
        for label, r in ctx.profile.all_active_roots:
            for rf in iter_repo_files(r, {".ts", ".tsx", ".js", ".java", ".kt", ".prisma", ".py"}):
                txt = rf.read_text(encoding="utf-8", errors="replace")
                rel = rf.relative_to(r).as_posix()
                for m in ROLE_ENUM_RE.finditer(txt):
                    for item in re.findall(r"^\s*([A-Z][A-Z0-9_]{2,})\b", m.group(2), re.MULTILINE):
                        if item not in seen_roles:
                            seen_roles.add(item)
                            roles.append({"name": item, "source": rel})
                            nodes.append(Node(id=f"Role:{item}", kind="Role", name=item, file=rel, root_label=label))
                for m in HAS_ROLE_RE.finditer(txt):
                    for item in re.findall(r"[\"']([A-Z0-9_]+)[\"']", m.group(1)):
                        clean_role = item.removeprefix("ROLE_")
                        if clean_role not in seen_roles:
                            seen_roles.add(clean_role)
                            roles.append({"name": clean_role, "source": rel})
                            nodes.append(
                                Node(id=f"Role:{clean_role}", kind="Role", name=clean_role, file=rel, root_label=label)
                            )

        if not applicable:
            ctx.shared_state["backend"] = {
                "endpoints": [],
                "dtos": {},
                "roles": roles,
                "be_stacks": [],
                "url_security_rules": [],
            }
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
                nodes=nodes,
            )

        for label, r in ctx.profile.all_active_roots:
            # 1. Java / Kotlin (Spring)
            java_quick = extract_java_endpoints_quick(r)
            for method, full_path, rel_file, line_no in java_quick:
                if "spring" not in be_stacks:
                    be_stacks.append("spring")
                fpath = r / rel_file
                txt = fpath.read_text(encoding="utf-8", errors="replace") if fpath.is_file() else ""
                lines = txt.splitlines()
                # Extract method window around line_no for return DTO and method-level @PreAuthorize
                win_start = max(0, line_no - 4)
                win_end = min(len(lines), line_no + 12)
                window = "\n".join(lines[win_start:win_end])
                header = txt[: txt.find("class ")] if "class " in txt else ""

                allowed_roles: list[str] = []
                is_authenticated_guard = False
                for auth_blob in (header, window):
                    for pm in PREAUTH_RE.finditer(auth_blob):
                        expr = pm.group(1)
                        if "isAuthenticated" in expr:
                            is_authenticated_guard = True
                        for rname in re.findall(r"[\"']([A-Z0-9_]+)[\"']", expr):
                            allowed_roles.append(rname.removeprefix("ROLE_"))

                ret_dto = None
                rm_sig = re.search(
                    r"\bpublic\s+([A-Za-z0-9_<>, ?\[\]]+)\s+([a-z][A-Za-z0-9_]*)\s*\(([^)]*)\)",
                    "\n".join(lines[line_no - 1 : win_end]),
                )
                req_dto = None
                if rm_sig:
                    raw_ret = rm_sig.group(1).strip()
                    for _ in range(3):
                        um = re.match(
                            r"^(?:ResponseEntity|ApiResponse|UnifiedApiResponse|Page|List|Set|Optional)\s*<\s*(.+)\s*>$",
                            raw_ret,
                        )
                        if um:
                            raw_ret = um.group(1).strip()
                        else:
                            break
                    if re.match(r"^[A-Z][A-Za-z0-9_]*$", raw_ret) and raw_ret not in {"Object", "String", "Void", "Boolean"}:
                        ret_dto = raw_ret
                    body_m = re.search(r"@RequestBody\s+(?:@\w+\s+)*([A-Z][A-Za-z0-9_]*)", rm_sig.group(3))
                    if body_m:
                        req_dto = body_m.group(1)

                ctrl_name = Path(rel_file).stem
                ep_id = f"Endpoint:{method}:{full_path}"
                nodes.append(
                    Node(
                        id=f"Controller:{ctrl_name}",
                        kind="Controller",
                        name=ctrl_name,
                        file=rel_file,
                        line=1,
                        root_label=label,
                    )
                )
                nodes.append(
                    Node(
                        id=ep_id,
                        kind="Endpoint",
                        name=f"{method} {full_path}",
                        file=rel_file,
                        line=line_no,
                        root_label=label,
                        attrs={
                            "method": method,
                            "path": full_path,
                            "normalized_path": normalize_api_path(full_path),
                            "return_dto": ret_dto,
                            "request_dto": req_dto,
                            "allowed_roles": sorted(set(allowed_roles)),
                            "authenticated": is_authenticated_guard or bool(allowed_roles),
                        },
                    )
                )
                edges.append(
                    Edge(
                        source=f"Controller:{ctrl_name}",
                        target=ep_id,
                        kind="exposes",
                        derivation="syntax",
                        evidence_ref=f"{rel_file}:{line_no}",
                    )
                )
                if ret_dto:
                    edges.append(
                        Edge(
                            source=ep_id,
                            target=f"Dto:{ret_dto}",
                            kind="returns",
                            derivation="syntax",
                            evidence_ref=f"{rel_file}:{line_no}",
                        )
                    )
                for ar in sorted(set(allowed_roles)):
                    edges.append(
                        Edge(
                            source=ep_id,
                            target=f"Role:{ar}",
                            kind="guarded_by",
                            derivation="syntax",
                            evidence_ref=f"{rel_file}:{line_no}",
                        )
                    )
                endpoints.append(
                    {
                        "id": ep_id,
                        "method": method,
                        "path": full_path,
                        "normalized_path": normalize_api_path(full_path),
                        "file": Path(rel_file).name,
                        "rel_file": rel_file,
                        "line": line_no,
                        "root_label": label,
                        "return_dto": ret_dto,
                        "request_dto": req_dto,
                        "allowed_roles": sorted(set(allowed_roles)),
                        "authenticated": is_authenticated_guard or bool(allowed_roles),
                    }
                )

            # Scan Java DTOs, Services, Repositories, and SecurityFilterChain URL rules
            for jf in iter_repo_files(r, {".java", ".kt"}):
                scanned += 1
                rel = jf.relative_to(r).as_posix()
                txt = jf.read_text(encoding="utf-8", errors="replace")
                cname = jf.stem

                if "@Service" in txt:
                    nodes.append(Node(id=f"Service:{cname}", kind="Service", name=cname, file=rel, root_label=label))
                    for repo_ref in re.findall(r"\bprivate\s+final\s+([A-Z][A-Za-z0-9_]*Repository)\b", txt):
                        edges.append(
                            Edge(
                                source=f"Service:{cname}",
                                target=f"Repository:{repo_ref}",
                                kind="delegates_to",
                                derivation="syntax",
                                evidence_ref=f"{rel}:1",
                            )
                        )
                if "@Repository" in txt or "JpaRepository" in txt or "CrudRepository" in txt:
                    nodes.append(
                        Node(id=f"Repository:{cname}", kind="Repository", name=cname, file=rel, root_label=label)
                    )
                    gen_m = re.search(r"(?:JpaRepository|CrudRepository)\s*<\s*([A-Z][A-Za-z0-9_]*)\s*,", txt)
                    if gen_m:
                        edges.append(
                            Edge(
                                source=f"Repository:{cname}",
                                target=f"Entity:{gen_m.group(1)}",
                                kind="persists_to",
                                derivation="syntax",
                                evidence_ref=f"{rel}:1",
                            )
                        )

                # SecurityFilterChain requestMatchers rules
                if "SecurityFilterChain" in txt or "HttpSecurity" in txt:
                    for sm in re.finditer(
                        r"requestMatchers\s*\(([^)]+)\)\s*\.\s*(permitAll|authenticated|hasRole|hasAnyRole|hasAuthority|hasAnyAuthority)\s*\(([^)]*)\)",
                        txt,
                    ):
                        patterns = re.findall(r"[\"'](/[^\"']*)[\"']", sm.group(1))
                        rule_kind = sm.group(2)
                        rule_roles = [
                            x.removeprefix("ROLE_")
                            for x in re.findall(r"[\"']([A-Z0-9_]+)[\"']", sm.group(3) or "")
                        ]
                        sline = txt[: sm.start()].count("\n") + 1
                        for pat in patterns:
                            url_security_rules.append(
                                {
                                    "pattern": pat,
                                    "rule": rule_kind,
                                    "roles": rule_roles,
                                    "file": rel,
                                    "line": sline,
                                }
                            )

                # DTO classes / Java records
                if cname.endswith(("Dto", "DTO", "Response", "Request")) or "/dto/" in f"/{rel.lower()}":
                    fields: list[dict[str, Any]] = []
                    for fm in JAVA_DTO_FIELD_RE.finditer(txt):
                        jtype = fm.group(1).strip()
                        fname = fm.group(2)
                        win = txt[max(0, fm.start() - 120) : fm.start() + 40]
                        not_null = bool(re.search(r"@(?:NotNull|NotBlank|NotEmpty)\b", win))
                        fields.append({"name": fname, "type": jtype, "nullable": not not_null})
                    for rec_m in JAVA_RECORD_COMP_RE.finditer(txt):
                        if rec_m.group(1) == cname:
                            for part in rec_m.group(2).split(","):
                                p_clean = part.strip()
                                pm = re.search(r"([A-Za-z0-9_<>\[\]]+)\s+([a-z][A-Za-z0-9_]*)$", p_clean)
                                if pm:
                                    fields.append(
                                        {
                                            "name": pm.group(2),
                                            "type": pm.group(1),
                                            "nullable": "@NotNull" not in p_clean and "@NotBlank" not in p_clean,
                                        }
                                    )
                    if fields:
                        dtos[cname] = {"name": cname, "file": rel, "root_label": label, "fields": fields}
                        nodes.append(
                            Node(
                                id=f"Dto:{cname}",
                                kind="Dto",
                                name=cname,
                                file=rel,
                                root_label=label,
                                attrs={"fields": fields},
                            )
                        )

            # 2. Node / TS Backend (Express, NestJS, Next.js API)
            for nf in iter_repo_files(r, {".ts", ".js", ".mjs"}):
                rel = nf.relative_to(r).as_posix()
                txt = nf.read_text(encoding="utf-8", errors="replace")
                scanned += 1

                if re.match(r"^(?:src/)?app/api/.+/route\.(?:ts|js)$", rel):
                    if "nextjs-or-fastapi" not in be_stacks:
                        be_stacks.append("nextjs-or-fastapi")
                    api_p = "/" + re.sub(r"^(?:src/)?app/", "", re.sub(r"/route\.(?:ts|js)$", "", rel))
                    for verb in re.findall(r"\bexport\s+async\s+function\s+(GET|POST|PUT|PATCH|DELETE)\b", txt):
                        ep_id = f"Endpoint:{verb}:{api_p}"
                        endpoints.append(
                            {
                                "id": ep_id,
                                "method": verb,
                                "path": api_p,
                                "normalized_path": normalize_api_path(api_p),
                                "file": nf.name,
                                "rel_file": rel,
                                "line": 1,
                                "root_label": label,
                                "return_dto": None,
                                "request_dto": None,
                                "allowed_roles": [],
                                "authenticated": "auth" in txt.lower() or "session" in txt.lower(),
                            }
                        )
                        nodes.append(
                            Node(id=ep_id, kind="Endpoint", name=f"{verb} {api_p}", file=rel, root_label=label)
                        )

                for m in EXPRESS_ROUTE_RE.finditer(txt):
                    if "express" not in be_stacks:
                        be_stacks.append("express")
                    verb = m.group(1).upper()
                    ep_path = m.group(2)
                    tail = m.group(3) or ""
                    eline = txt[: m.start()].count("\n") + 1
                    has_guard = any(
                        g in tail for g in ("requireAuth", "authenticate", "authorize", "authMiddleware", "requireRole")
                    )
                    role_list = re.findall(r"requireRole\s*\(\s*[\"']([A-Z0-9_]+)[\"']", tail)
                    ep_id = f"Endpoint:{verb}:{ep_path}"
                    endpoints.append(
                        {
                            "id": ep_id,
                            "method": verb,
                            "path": ep_path,
                            "normalized_path": normalize_api_path(ep_path),
                            "file": nf.name,
                            "rel_file": rel,
                            "line": eline,
                            "root_label": label,
                            "return_dto": None,
                            "request_dto": None,
                            "allowed_roles": role_list,
                            "authenticated": has_guard or bool(role_list),
                        }
                    )
                    nodes.append(
                        Node(
                            id=ep_id,
                            kind="Endpoint",
                            name=f"{verb} {ep_path}",
                            file=rel,
                            line=eline,
                            root_label=label,
                        )
                    )

                ctrl_m = NEST_CTRL_RE.search(txt)
                if ctrl_m:
                    if "nestjs" not in be_stacks:
                        be_stacks.append("nestjs")
                    prefix = ctrl_m.group(1).strip("/")
                    for mm in NEST_METHOD_RE.finditer(txt):
                        verb = mm.group(1).upper()
                        sub = (mm.group(2) or "").strip("/")
                        full = "/" + "/".join(s for s in (prefix, sub) if s)
                        eline = txt[: mm.start()].count("\n") + 1
                        ep_id = f"Endpoint:{verb}:{full}"
                        endpoints.append(
                            {
                                "id": ep_id,
                                "method": verb,
                                "path": full,
                                "normalized_path": normalize_api_path(full),
                                "file": nf.name,
                                "rel_file": rel,
                                "line": eline,
                                "root_label": label,
                                "return_dto": None,
                                "request_dto": None,
                                "allowed_roles": [],
                                "authenticated": "@UseGuards" in txt,
                            }
                        )
                        nodes.append(
                            Node(
                                id=ep_id,
                                kind="Endpoint",
                                name=f"{verb} {full}",
                                file=rel,
                                line=eline,
                                root_label=label,
                            )
                        )

            # 3. Python Backend (FastAPI / Flask + Pydantic DTOs)
            for pf in iter_repo_files(r, {".py"}):
                rel = pf.relative_to(r).as_posix()
                txt = pf.read_text(encoding="utf-8", errors="replace")
                scanned += 1
                for m in PY_ROUTE_RE.finditer(txt):
                    if "nextjs-or-fastapi" not in be_stacks and "fastapi" not in be_stacks:
                        be_stacks.append("fastapi")
                    verb = m.group(1).upper()
                    ep_path = m.group(2)
                    decorator_args = m.group(3) or ""
                    rm = re.search(r"response_model\s*=\s*([A-Z][A-Za-z0-9_]*)", decorator_args)
                    ret_dto = rm.group(1) if rm else None
                    eline = txt[: m.start()].count("\n") + 1
                    ep_id = f"Endpoint:{verb}:{ep_path}"
                    endpoints.append(
                        {
                            "id": ep_id,
                            "method": verb,
                            "path": ep_path,
                            "normalized_path": normalize_api_path(ep_path),
                            "file": pf.name,
                            "rel_file": rel,
                            "line": eline,
                            "root_label": label,
                            "return_dto": ret_dto,
                            "request_dto": None,
                            "allowed_roles": [],
                            "authenticated": "Depends(" in txt[m.start() : m.end() + 260],
                        }
                    )
                    nodes.append(
                        Node(
                            id=ep_id,
                            kind="Endpoint",
                            name=f"{verb} {ep_path}",
                            file=rel,
                            line=eline,
                            root_label=label,
                        )
                    )
                for pm in PYDANTIC_CLASS_RE.finditer(txt):
                    mname = pm.group(1)
                    fields = []
                    for fm in PYDANTIC_FIELD_RE.finditer(pm.group(2)):
                        ftype = fm.group(2).strip()
                        fields.append(
                            {
                                "name": fm.group(1),
                                "type": ftype,
                                "nullable": "Optional" in ftype or "| None" in ftype,
                            }
                        )
                    if fields:
                        dtos[mname] = {"name": mname, "file": rel, "root_label": label, "fields": fields}
                        nodes.append(
                            Node(
                                id=f"Dto:{mname}",
                                kind="Dto",
                                name=mname,
                                file=rel,
                                root_label=label,
                                attrs={"fields": fields},
                            )
                        )

        ctx.shared_state["backend"] = {
            "endpoints": endpoints,
            "dtos": dtos,
            "roles": roles,
            "be_stacks": be_stacks,
            "url_security_rules": url_security_rules,
        }

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            nodes=nodes,
            edges=edges,
            coverage=CoverageReport(scanned_files=scanned),
        )
