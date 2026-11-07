# -*- coding: utf-8 -*-
"""Multi-source verified project, peer, stack, contract, and schema discovery (`discovery.py`)."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path

from .model import (
    ContractSource,
    PeerCandidate,
    ProjectProfile,
    SchemaSource,
    iter_repo_files,
    normalize_api_path,
)

CLIENT_HTTP_RE = re.compile(
    r"\b(?:fetch|axios(?:\.(?:get|post|put|patch|delete))?|apiClient\.(?:get|post|put|patch|delete)"
    r"|[A-Za-z0-9_]*[Aa]pi\.(?:get|post|put|patch|delete)|http\.(?:get|post|put|patch|delete)|\$fetch)"
    r"\s*(?:<[^>]+>)?\s*\(\s*[\"'`]([^\"'`]+)[\"'`]"
)
API_LITERAL_RE = re.compile(r"[\"'`]((?:/api(?:/v\d+)?|/v\d+)/[A-Za-z0-9_/\-{}:.$]+)[\"'`]")

PROXY_PORT_RE = re.compile(r"https?://(?:localhost|127\.0\.0\.1):(\d{2,5})")
YAML_PORT_RE = re.compile(r"server\s*:\s*(?:\n|\r\n)[ \t]+port\s*:\s*(\d{2,5})")
PROP_PORT_RE = re.compile(r"^\s*(?:server\.port|PORT)\s*[=:]\s*(\d{2,5})\s*$", re.MULTILINE)
CODE_PORT_RE = re.compile(r"\.listen\s*\(\s*(\d{2,5})\b")

SPRING_CONTROLLER_RE = re.compile(r"@(?:[A-Za-z_][A-Za-z0-9_]*\.)*(?:RestController|Controller)\b")
SPRING_MAPPING_HEAD_RE = re.compile(r"@(Get|Post|Put|Patch|Delete|Request)Mapping\b")
STR_QUOTED_RE = re.compile(r"[\"']([^\"']+)[\"']")

EXPRESS_HANDLER_RE = re.compile(
    r"\b(?:app|router|server)\.(get|post|put|patch|delete)\s*\(\s*[\"'`](/[^\"'`]*)[\"'`]",
    re.IGNORECASE,
)
NEST_CTRL_RE = re.compile(r"@Controller\s*\(\s*[\"'`]([^\"'`]*)[\"'`]\s*\)")
NEST_METHOD_RE = re.compile(r"@(Get|Post|Put|Patch|Delete)\s*\(\s*(?:[\"'`]([^\"'`]*)[\"'`])?\s*\)")
PY_ROUTE_RE = re.compile(
    r"@(?:app|router|bp|blueprint)\.(get|post|put|patch|delete|route)\s*\(\s*[\"'](/[^\"']*)[\"']",
    re.IGNORECASE,
)
DJANGO_PATH_RE = re.compile(r"\bpath\s*\(\s*[\"'](api/[^\"']*)[\"']")

MANIFEST_FILENAMES = {
    "package.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
}


def _extract_mapping_paths(arg_str: str | None) -> list[str]:
    if not arg_str or not arg_str.strip():
        return [""]
    # Prefer explicit path=... or value=... if named arguments exist
    named = re.search(r"\b(?:value|path)\s*=\s*(\{[^}]*\}|[\"'][^\"']*[\"'])", arg_str)
    if named:
        found = STR_QUOTED_RE.findall(named.group(1))
        return found if found else [""]
    # Strip non-path named attributes (consumes, produces, headers, params, name, method)
    cleaned = re.sub(
        r"\b(?:consumes|produces|headers|params|name|method)\s*=\s*(?:\{[^}]*\}|[\"'][^\"']*[\"']|[A-Za-z0-9_.]+)",
        "",
        arg_str,
    )
    found = STR_QUOTED_RE.findall(cleaned)
    return found if found else [""]


def _read_annotation_args(text: str, start: int) -> str:
    """Read balanced `(...)` annotation arguments starting at `start` (quote-aware)."""
    i = start
    while i < len(text) and text[i] in " \t\r\n":
        i += 1
    if i >= len(text) or text[i] != "(":
        return ""
    depth = 0
    quote_ch = ""
    j = i
    while j < len(text):
        ch = text[j]
        if quote_ch:
            if ch == "\\":
                j += 2
                continue
            if ch == quote_ch:
                quote_ch = ""
        elif ch in ('"', "'"):
            quote_ch = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[i + 1 : j]
        j += 1
    return ""


def extract_java_endpoints_quick(root: Path) -> list[tuple[str, str, str, int]]:
    """Return list of (HTTP_METHOD, full_path, rel_file, line) across Spring controllers."""
    results: list[tuple[str, str, str, int]] = []
    for fpath in iter_repo_files(root, {".java", ".kt"}):
        text = fpath.read_text(encoding="utf-8", errors="replace")
        if not SPRING_CONTROLLER_RE.search(text):
            continue
        rel = fpath.relative_to(root).as_posix()
        class_prefixes = [""]
        cls_m = re.search(r"\b(?:class|record)\s+\w+", text)
        cls_idx = cls_m.start() if cls_m else -1
        header = text[:cls_idx] if cls_idx != -1 else text[:800]
        rm_head = re.search(r"@RequestMapping\b", header)
        if rm_head:
            class_prefixes = _extract_mapping_paths(_read_annotation_args(header, rm_head.end()))

        body = text[cls_idx:] if cls_idx != -1 else text
        base_line = text[:cls_idx].count("\n") + 1 if cls_idx != -1 else 1
        for m in SPRING_MAPPING_HEAD_RE.finditer(body):
            verb_raw = m.group(1).upper()
            arg_blob = _read_annotation_args(body, m.end())
            if verb_raw == "REQUEST":
                rm_verb = re.search(r"RequestMethod\.(GET|POST|PUT|PATCH|DELETE)", arg_blob)
                method = rm_verb.group(1) if rm_verb else "GET"
            else:
                method = verb_raw
            sub_paths = _extract_mapping_paths(arg_blob)
            line_no = base_line + body[: m.start()].count("\n")
            for cp in class_prefixes:
                for sp in sub_paths:
                    joined = "/" + "/".join(
                        seg.strip("/") for seg in (cp, sp) if seg and seg.strip("/")
                    )
                    results.append((method, joined, rel, line_no))
    return results


def extract_server_paths_quick(root: Path) -> tuple[set[str], list[str], list[int]]:
    """Extract normalized server API paths, detected backend stacks, and server ports."""
    norm_paths: set[str] = set()
    stacks: list[str] = []
    ports: set[int] = set()

    # Ports in config files (never storing secret strings, only numeric port integers)
    for cfg in iter_repo_files(root, {".yml", ".yaml", ".properties", ".toml", ".json", ".ts", ".js", ".py"}):
        name_low = cfg.name.lower()
        if any(
            k in name_low
            for k in ("application", "config", "settings", "server", "main", "app", "env.example")
        ):
            txt = cfg.read_text(encoding="utf-8", errors="replace")
            for pm in YAML_PORT_RE.finditer(txt):
                ports.add(int(pm.group(1)))
            for pm in PROP_PORT_RE.finditer(txt):
                ports.add(int(pm.group(1)))
            for pm in CODE_PORT_RE.finditer(txt):
                ports.add(int(pm.group(1)))

    # Java / Kotlin Spring
    java_eps = extract_java_endpoints_quick(root)
    if java_eps:
        stacks.append("spring")
        for _, p, _, _ in java_eps:
            norm_paths.add(normalize_api_path(p))
    elif (root / "pom.xml").is_file() or (root / "build.gradle").is_file() or (root / "build.gradle.kts").is_file():
        for build_f in ("pom.xml", "build.gradle", "build.gradle.kts"):
            bf = root / build_f
            if bf.is_file() and "spring-boot" in bf.read_text(encoding="utf-8", errors="replace"):
                stacks.append("spring")
        if "spring" not in stacks:
            for jf in iter_repo_files(root, {".java", ".kt"}):
                jtxt = jf.read_text(encoding="utf-8", errors="replace")
                if any(tok in jtxt for tok in ("@Service", "@Entity", "JpaRepository", "@Component")):
                    stacks.append("spring")
                    break

    # Node / TS (Express, NestJS, Fastify, Next API)
    for fpath in iter_repo_files(root, {".ts", ".js", ".mjs", ".cjs"}):
        rel = fpath.relative_to(root).as_posix()
        txt = fpath.read_text(encoding="utf-8", errors="replace")

        if re.match(r"^(?:src/)?app/api/.+/route\.(?:ts|js)$", rel):
            if "nextjs-api" not in stacks:
                stacks.append("nextjs-api")
            api_p = "/" + re.sub(r"^(?:src/)?app/", "", re.sub(r"/route\.(?:ts|js)$", "", rel))
            norm_paths.add(normalize_api_path(api_p))

        for m in EXPRESS_HANDLER_RE.finditer(txt):
            if "express" not in stacks:
                stacks.append("express")
            norm_paths.add(normalize_api_path(m.group(2)))

        ctrl_m = NEST_CTRL_RE.search(txt)
        if ctrl_m:
            if "nestjs" not in stacks:
                stacks.append("nestjs")
            prefix = ctrl_m.group(1).strip("/")
            for mm in NEST_METHOD_RE.finditer(txt):
                sub = (mm.group(2) or "").strip("/")
                full = "/" + "/".join(s for s in (prefix, sub) if s)
                norm_paths.add(normalize_api_path(full))

    # Python (FastAPI, Flask, Django)
    for fpath in iter_repo_files(root, {".py"}):
        txt = fpath.read_text(encoding="utf-8", errors="replace")
        if "FastAPI" in txt or "APIRouter" in txt:
            if "fastapi" not in stacks:
                stacks.append("fastapi")
        elif "Flask" in txt or "Blueprint" in txt:
            if "flask" not in stacks:
                stacks.append("flask")
        for m in PY_ROUTE_RE.finditer(txt):
            norm_paths.add(normalize_api_path(m.group(2)))
        for m in DJANGO_PATH_RE.finditer(txt):
            if "django" not in stacks:
                stacks.append("django")
            norm_paths.add(normalize_api_path("/" + m.group(1)))

    # OpenAPI files
    for oa in _detect_openapi_files(root):
        txt = oa.read_text(encoding="utf-8", errors="replace")
        for pm in re.finditer(r"^[ \t]{2}(/[A-Za-z0-9_/\-{}.]+)\s*:", txt, re.MULTILINE):
            norm_paths.add(normalize_api_path(pm.group(1)))

    return norm_paths, stacks, sorted(ports)


def extract_client_paths_quick(root: Path) -> tuple[set[str], list[str], list[int]]:
    """Extract normalized client HTTP call paths, frontend stacks, and dev-proxy target ports."""
    client_paths: set[str] = set()
    fe_stacks: list[str] = []
    proxy_ports: set[int] = set()

    pkg_file = root / "package.json"
    if pkg_file.is_file():
        try:
            pkg = json.loads(pkg_file.read_text(encoding="utf-8", errors="replace"))
            deps = {
                **(pkg.get("dependencies") or {}),
                **(pkg.get("devDependencies") or {}),
            }
            if "next" in deps:
                fe_stacks.append("nextjs")
            if "react" in deps:
                fe_stacks.append("react")
            if "vue" in deps:
                fe_stacks.append("vue")
            if "nuxt" in deps:
                fe_stacks.append("nuxt")
            if "@angular/core" in deps:
                fe_stacks.append("angular")
            if "svelte" in deps or "@sveltejs/kit" in deps:
                fe_stacks.append("svelte")
            if isinstance(pkg.get("proxy"), str):
                for pm in PROXY_PORT_RE.finditer(pkg["proxy"]):
                    proxy_ports.add(int(pm.group(1)))
        except Exception:
            pass

    for cfg_name in (
        "vite.config.ts",
        "vite.config.js",
        "vite.config.mts",
        "next.config.js",
        "next.config.mjs",
        "next.config.ts",
        "angular.json",
        ".env.example",
        ".env.development",
    ):
        cfg = root / cfg_name
        if cfg.is_file():
            txt = cfg.read_text(encoding="utf-8", errors="replace")
            for pm in PROXY_PORT_RE.finditer(txt):
                proxy_ports.add(int(pm.group(1)))

    for fpath in iter_repo_files(root, {".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue", ".svelte"}):
        rel = fpath.relative_to(root).as_posix().lower()
        if ".test." in rel or ".spec." in rel or "/tests/" in f"/{rel}":
            continue
        txt = fpath.read_text(encoding="utf-8", errors="replace")
        if "<Route" in txt and "react" not in fe_stacks:
            fe_stacks.append("react")
        for m in CLIENT_HTTP_RE.finditer(txt):
            raw = m.group(1)
            if raw.startswith("/") or raw.startswith("http"):
                client_paths.add(normalize_api_path(raw))
        for m in API_LITERAL_RE.finditer(txt):
            client_paths.add(normalize_api_path(m.group(1)))

    return client_paths, fe_stacks, sorted(proxy_ports)


def _detect_openapi_files(root: Path) -> list[Path]:
    matches: list[Path] = []
    for fpath in iter_repo_files(root, {".yaml", ".yml", ".json"}):
        low = fpath.name.lower()
        if any(k in low for k in ("openapi", "swagger", "api-docs")):
            matches.append(fpath)
            continue
        if fpath.stat().st_size <= 512_000:
            head = fpath.read_text(encoding="utf-8", errors="replace")[:600]
            if re.search(r'^\s*["\']?(?:openapi|swagger)["\']?\s*:\s*["\']?[23]\.', head, re.MULTILINE):
                matches.append(fpath)
    return matches


def _discover_contract_sources(roots: list[tuple[str, Path]]) -> list[ContractSource]:
    sources: list[ContractSource] = []
    for label, r in roots:
        for oa in _detect_openapi_files(r):
            sources.append(
                ContractSource(
                    kind="openapi_file",
                    path=oa.relative_to(r).as_posix(),
                    root_label=label,
                    confidence=95,
                )
            )
        for gql in iter_repo_files(r, {".graphql", ".gql"}):
            sources.append(
                ContractSource(
                    kind="graphql_schema",
                    path=gql.relative_to(r).as_posix(),
                    root_label=label,
                    confidence=92,
                )
            )
        for proto in iter_repo_files(r, {".proto"}):
            sources.append(
                ContractSource(
                    kind="grpc_proto",
                    path=proto.relative_to(r).as_posix(),
                    root_label=label,
                    confidence=92,
                )
            )
        pom = r / "pom.xml"
        if pom.is_file():
            ptxt = pom.read_text(encoding="utf-8", errors="replace")
            if "springdoc" in ptxt or "swagger" in ptxt.lower():
                sources.append(
                    ContractSource(
                        kind="springdoc_openapi_generator",
                        path="pom.xml",
                        root_label=label,
                        confidence=85,
                    )
                )
        for gradle_name in ("build.gradle", "build.gradle.kts"):
            gf = r / gradle_name
            if gf.is_file():
                gtxt = gf.read_text(encoding="utf-8", errors="replace")
                if "springdoc" in gtxt or "swagger" in gtxt.lower():
                    sources.append(
                        ContractSource(
                            kind="springdoc_openapi_generator",
                            path=gradle_name,
                            root_label=label,
                            confidence=85,
                        )
                    )
        pkg = r / "package.json"
        if pkg.is_file():
            ptxt = pkg.read_text(encoding="utf-8", errors="replace")
            if "@nestjs/swagger" in ptxt or "@fastify/swagger" in ptxt or "swagger-jsdoc" in ptxt:
                sources.append(
                    ContractSource(
                        kind="node_openapi_generator",
                        path="package.json",
                        root_label=label,
                        confidence=85,
                    )
                )
    return sources


def _discover_schema_and_tenancy(roots: list[tuple[str, Path]]) -> tuple[list[SchemaSource], bool, str]:
    sources: list[SchemaSource] = []
    orm_kinds: set[str] = set()
    has_non_prisma_sql = False
    tenancy_signals: set[str] = set()

    for label, r in roots:
        prisma_count = 0
        first_prisma = ""
        for pf in iter_repo_files(r, {".prisma"}):
            rel = pf.relative_to(r).as_posix()
            txt = pf.read_text(encoding="utf-8", errors="replace")
            models = re.findall(r"^\s*model\s+\w+\s*\{", txt, re.MULTILINE)
            if models:
                prisma_count += len(models)
                first_prisma = first_prisma or rel
                if re.search(r"\btenant_?[iI]d\b", txt):
                    tenancy_signals.add("tenant-column")
                elif re.search(r"\b(?:company|organization|workspace)_?[iI]d\b", txt, re.IGNORECASE):
                    tenancy_signals.add("org-scoped")
        if prisma_count:
            sources.append(SchemaSource(kind="prisma", path=first_prisma, root_label=label, entities_count=prisma_count))
            orm_kinds.add("prisma")

        sql_tables = 0
        first_sql = ""
        for sf in iter_repo_files(r, {".sql"}):
            rel = sf.relative_to(r).as_posix()
            txt = sf.read_text(encoding="utf-8", errors="replace")
            creates = re.findall(r"\b(?:CREATE|ALTER)\s+TABLE\b", txt, re.IGNORECASE)
            if creates:
                sql_tables += len(creates)
                first_sql = first_sql or rel
                if not rel.lower().startswith("prisma/"):
                    has_non_prisma_sql = True
                if re.search(r"\bENABLE\s+ROW\s+LEVEL\s+SECURITY\b", txt, re.IGNORECASE):
                    tenancy_signals.add("rls")
                if re.search(r"\btenant_id\b", txt, re.IGNORECASE):
                    tenancy_signals.add("tenant-column")
                elif re.search(r"\b(?:company_id|organization_id|workspace_id)\b", txt, re.IGNORECASE):
                    tenancy_signals.add("org-scoped")
        if sql_tables:
            sources.append(
                SchemaSource(kind="sql_migration", path=first_sql, root_label=label, entities_count=sql_tables)
            )

        jpa_count = 0
        first_jpa = ""
        for jf in iter_repo_files(r, {".java", ".kt"}):
            txt = jf.read_text(encoding="utf-8", errors="replace")
            if "@Entity" in txt:
                jpa_count += 1
                first_jpa = first_jpa or jf.relative_to(r).as_posix()
                if re.search(r"\btenantId\b|\btenant_id\b", txt):
                    tenancy_signals.add("tenant-column")
                elif re.search(r"\b(?:companyId|company|organizationId|organization|workspaceId)\b", txt):
                    tenancy_signals.add("org-scoped")
            if "MultiTenantConnectionProvider" in txt:
                tenancy_signals.add("schema-per-tenant")
        if jpa_count:
            sources.append(SchemaSource(kind="jpa", path=first_jpa, root_label=label, entities_count=jpa_count))
            orm_kinds.add("jpa")

        typeorm_count = 0
        drizzle_count = 0
        first_typeorm = ""
        first_drizzle = ""
        for tf in iter_repo_files(r, {".ts"}):
            txt = tf.read_text(encoding="utf-8", errors="replace")
            if "@Entity(" in txt and "typeorm" in txt:
                typeorm_count += 1
                first_typeorm = first_typeorm or tf.relative_to(r).as_posix()
            if re.search(r"\b(?:pgTable|mysqlTable|sqliteTable)\s*\(", txt):
                drizzle_count += len(re.findall(r"\b(?:pgTable|mysqlTable|sqliteTable)\s*\(", txt))
                first_drizzle = first_drizzle or tf.relative_to(r).as_posix()
        if typeorm_count:
            sources.append(SchemaSource(kind="typeorm", path=first_typeorm, root_label=label, entities_count=typeorm_count))
            orm_kinds.add("typeorm")
        if drizzle_count:
            sources.append(SchemaSource(kind="drizzle", path=first_drizzle, root_label=label, entities_count=drizzle_count))
            orm_kinds.add("drizzle")

        sqla_count = 0
        first_sqla = ""
        for pyf in iter_repo_files(r, {".py"}):
            txt = pyf.read_text(encoding="utf-8", errors="replace")
            if "__tablename__" in txt:
                sqla_count += 1
                first_sqla = first_sqla or pyf.relative_to(r).as_posix()
        if sqla_count:
            sources.append(
                SchemaSource(kind="sqlalchemy", path=first_sqla, root_label=label, entities_count=sqla_count)
            )
            orm_kinds.add("sqlalchemy")

    has_conflict = len(orm_kinds) >= 2 or ("prisma" in orm_kinds and has_non_prisma_sql)

    if not sources:
        tenancy = "stateless"
    elif "rls" in tenancy_signals:
        tenancy = "rls"
    elif "schema-per-tenant" in tenancy_signals:
        tenancy = "schema-per-tenant"
    elif "tenant-column" in tenancy_signals:
        tenancy = "tenant-column"
    elif "org-scoped" in tenancy_signals:
        tenancy = "org-scoped"
    else:
        tenancy = "single-tenant"

    return sources, has_conflict, tenancy


def _collect_declared_peer_hints(root: Path) -> set[Path]:
    hints: set[Path] = set()
    search_dirs = [root]
    os_temp = Path(tempfile.gettempdir()).resolve()
    if root.parent.resolve() != os_temp and root.parent != root:
        search_dirs.append(root.parent)

    for base in search_dirs:
        for ws_file in base.glob("*.code-workspace"):
            try:
                data = json.loads(ws_file.read_text(encoding="utf-8", errors="replace"))
                for folder in data.get("folders", []):
                    p_str = folder.get("path") if isinstance(folder, dict) else None
                    if p_str:
                        cand = (ws_file.parent / p_str).resolve()
                        if cand.is_dir() and cand != root:
                            hints.add(cand)
            except Exception:
                continue

        for dc_name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
            dc = base / dc_name
            if dc.is_file():
                txt = dc.read_text(encoding="utf-8", errors="replace")
                for m in re.finditer(r"context\s*:\s*([^\s#]+)", txt):
                    raw_ctx = m.group(1).strip("\"'")
                    cand = (dc.parent / raw_ctx).resolve()
                    if cand.is_dir() and cand != root:
                        hints.add(cand)

    brief = root / "PROJECT_BRIEF.md"
    if brief.is_file() and root.parent.resolve() != os_temp:
        btxt = brief.read_text(encoding="utf-8", errors="replace")
        for child in sorted(root.parent.iterdir()):
            if child.is_dir() and child.resolve() != root and re.search(rf"\b{re.escape(child.name)}\b", btxt):
                hints.add(child.resolve())

    return hints


def _is_candidate_repo_dir(d: Path) -> bool:
    if not d.is_dir() or d.name.startswith("."):
        return False
    if any((d / mf).is_file() for mf in MANIFEST_FILENAMES):
        return True
    if (d / "src").is_dir() or (d / "app").is_dir():
        return True
    return False


def _locate_ts_compiler(root: Path) -> str | None:
    if shutil.which("node") is None:
        return None
    candidates = [
        root / "node_modules" / "typescript" / "lib" / "typescript.js",
        root.parent / "node_modules" / "typescript" / "lib" / "typescript.js",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve().as_posix()
    return None


def discover_project(
    root: Path | str,
    explicit_peers: list[Path | str] | None = None,
) -> ProjectProfile:
    """Discover full-stack topology, verified peers, contract sources, and schema sources."""
    root_path = Path(root).resolve()
    exp_peers = [Path(p).resolve() for p in (explicit_peers or []) if Path(p).is_dir()]

    client_paths, fe_stacks, proxy_ports = extract_client_paths_quick(root_path)
    primary_server_paths, be_stacks, primary_ports = extract_server_paths_quick(root_path)

    server_ports: dict[str, list[int]] = {"primary": primary_ports}
    peer_candidates: list[PeerCandidate] = []

    for ep in exp_peers:
        sp, p_stacks, p_ports = extract_server_paths_quick(ep)
        for st in p_stacks:
            if st not in be_stacks:
                be_stacks.append(st)
        server_ports[ep.as_posix()] = p_ports
        matched = sorted(client_paths & sp) if client_paths else []
        ratio = (len(matched) / len(client_paths)) if client_paths else 1.0
        peer_candidates.append(
            PeerCandidate(
                path=ep.as_posix(),
                status="CONFIRMED",
                confidence=100,
                overlap_ratio=ratio,
                matched_paths=matched,
                signals=["explicit_cli"],
            )
        )

    # Automatic sibling & workspace discovery when no explicit peer was passed
    if not exp_peers:
        declared_hints = _collect_declared_peer_hints(root_path)
        sibling_Pool: list[Path] = []
        os_temp = Path(tempfile.gettempdir()).resolve()
        parent = root_path.parent.resolve()
        if parent != os_temp and parent != root_path and parent.is_dir():
            for child in sorted(parent.iterdir(), key=lambda x: x.name)[:25]:
                if child.resolve() == root_path:
                    continue
                if _is_candidate_repo_dir(child):
                    sibling_Pool.append(child.resolve())
        for h in sorted(declared_hints, key=lambda x: x.as_posix()):
            if h not in sibling_Pool:
                sibling_Pool.append(h)

        for cand in sibling_Pool:
            sp, cand_be_stacks, cand_ports = extract_server_paths_quick(cand)
            cand_client_paths, cand_fe_stacks, cand_proxy_ports = extract_client_paths_quick(cand)

            signals: list[str] = []
            if cand in declared_hints:
                signals.append("declared_workspace")

            # Bidirectional overlap: FE root -> BE peer OR BE root -> FE peer
            matched_fe_to_be = sorted(client_paths & sp) if (client_paths and sp) else []
            matched_be_to_fe = (
                sorted(primary_server_paths & cand_client_paths)
                if (primary_server_paths and cand_client_paths)
                else []
            )
            matched = matched_fe_to_be or matched_be_to_fe
            denom = len(client_paths) if matched_fe_to_be else (len(cand_client_paths) if matched_be_to_fe else max(len(client_paths), 1))
            ratio = (len(matched) / denom) if denom else 0.0

            if matched:
                signals.append(f"api_path_overlap:{len(matched)}")
            if (set(proxy_ports) & set(cand_ports)) or (set( primary_ports) & set(cand_proxy_ports)):
                signals.append("proxy_port_match")

            # Strict non-name-based confirmation rule
            if matched and (ratio >= 0.20 or "proxy_port_match" in signals or "declared_workspace" in signals):
                status = "CONFIRMED"
                conf = min(98, 70 + int(ratio * 25) + (10 if "proxy_port_match" in signals else 0))
                for st in cand_be_stacks:
                    if st not in be_stacks:
                        be_stacks.append(st)
                for st in cand_fe_stacks:
                    if st not in fe_stacks:
                        fe_stacks.append(st)
                server_ports[cand.as_posix()] = cand_ports
            elif "declared_workspace" in signals and (cand_be_stacks or cand_fe_stacks):
                status = "CONFIRMED"
                conf = 82
                for st in cand_be_stacks:
                    if st not in be_stacks:
                        be_stacks.append(st)
                server_ports[cand.as_posix()] = cand_ports
            elif matched or ("proxy_port_match" in signals and (cand_be_stacks or cand_fe_stacks)):
                status = "CANDIDATE_ASK_USER"
                conf = 55
            else:
                status = "REJECTED"
                conf = 0

            peer_candidates.append(
                PeerCandidate(
                    path=cand.as_posix(),
                    status=status,
                    confidence=conf,
                    overlap_ratio=ratio,
                    matched_paths=matched,
                    signals=signals,
                )
            )

    profile = ProjectProfile(
        root=root_path,
        explicit_peers=exp_peers,
        peers=peer_candidates,
        frontend_stacks=fe_stacks,
        backend_stacks=be_stacks,
        proxy_ports=proxy_ports,
        server_ports=server_ports,
        ts_compiler_path=_locate_ts_compiler(root_path),
    )

    active_roots = profile.all_active_roots
    profile.contract_sources = _discover_contract_sources(active_roots)
    schema_sources, has_conflict, tenancy = _discover_schema_and_tenancy(active_roots)
    profile.schema_sources = schema_sources
    profile.has_schema_conflict = has_conflict
    profile.tenancy_model = tenancy

    has_fe = bool(profile.frontend_stacks)
    has_be = bool(profile.backend_stacks)
    if has_fe and has_be:
        profile.topology = "fullstack"
    elif has_fe:
        profile.topology = "ssr-webapp" if any(s in profile.frontend_stacks for s in ("nextjs", "nuxt")) else "spa-frontend"
    elif has_be:
        profile.topology = "backend-service"
    else:
        profile.topology = "cli-or-library"

    return profile
