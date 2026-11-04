#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect — Global Product Gap & Evidence Scanner.

Project-agnostic, multi-stack static analyzer that produces deterministic
`file:line` evidence for:
  1. Stub & placeholder pages (including i18n-resolved keys and literal text)
  2. Stub actions / dead toast controls
  3. Broken / 404 navigation links vs. declared routes
  4. Candidate orphan backend endpoints (across main root and --peer repos)
  5. Candidate orphan database/entity fields unreferenced in UI views
  6. RBAC roles inventory and core module files (dashboard, profile, settings, notifications)

Exit codes:
  0 — Scan completed (findings are reported in JSON / Markdown output)
  2 — Invalid arguments or root directory does not exist
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCHEMA_VERSION = "feature-architect/gap-scan@1"

IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".agent",
    ".agents",
    ".claude",
    ".windsurf",
    ".cursor",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "yedekler",
    "scout",
    "raporlar",
    "temps",
}

UI_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".html"}
CODE_EXTENSIONS = UI_EXTENSIONS | {".ts", ".js", ".mjs", ".cjs"}

STUB_VALUE_RE = re.compile(
    r"(geli[sş]tir(?:il)?me\s+a[sş]amas[ıi]nda(?:d[ıi]r)?"
    r"|yap[ıi]m\s+a[sş]amas[ıi]nda(?:d[ıi]r)?"
    r"|yak[ıi]nda\s+eklenecek(?:tir)?"
    r"|currently\s+under\s+development"
    r"|page\s+is\s+under\s+development"
    r"|section\s+is\s+(?:currently\s+)?under\s+development"
    r"|will\s+be\s+added\s+soon"
    r"|coming\s+soon"
    r"|under\s+construction"
    r"|work\s+in\s+progress"
    r"|not\s+yet\s+implemented)",
    re.IGNORECASE,
)

STUB_ACTION_VALUE_RE = re.compile(
    r"(will\s+be\s+added\s+soon|yak[ıi]nda\s+eklenecek|updateComingSoon|exportComingSoon)",
    re.IGNORECASE,
)

STUB_KEY_RE = re.compile(
    r"(underDevelopment(?:Desc|Title)?|comingSoon(?:Desc|Title)?|underConstruction)$",
    re.IGNORECASE,
)

LITERAL_STUB_RE = re.compile(
    r"(bu\s+sayfa\s+(?:hen[üu]z\s+)?geli[sş]tir(?:il)?me\s+a[sş]amas[ıi]nda(?:d[ıi]r)?"
    r"|bu\s+alan\s+geli[sş]tir(?:il)?me\s+a[sş]amas[ıi]nda(?:d[ıi]r)?"
    r"|yap[ıi]m\s+a[sş]amas[ıi]nda(?:d[ıi]r)?"
    r"|>\s*Coming\s+Soon\s*<"
    r"|>\s*Under\s+(?:Construction|Development)\s*<"
    r"|this\s+page\s+is\s+(?:currently\s+)?under\s+development)",
    re.IGNORECASE,
)

TOAST_CALL_RE = re.compile(
    r"\b(?:showToast|toast(?:\.\w+)?|alert|notify|addNotification)\s*\(",
    re.IGNORECASE,
)

TODO_RE = re.compile(r"\b(?:TODO|FIXME)\b[:\s]*(.{0,80})")

JSX_ROUTE_RE = re.compile(r"<Route\b[^>]*?\bpath\s*=\s*[\"']([^\"']+)[\"']")
OBJ_ROUTE_RE = re.compile(r"\bpath\s*:\s*[\"'](/[^\"']*)[\"']")

LINK_TO_RE = re.compile(r"<(?:Link|NavLink)\b[^>]*?\bto\s*=\s*[\"'](/[^\"'#?]*)[\"']")
NAVIGATE_RE = re.compile(r"\b(?:navigate|router\.push)\s*\(\s*[\"'](/[^\"'#?]*)[\"']")
NAV_ITEM_PATH_RE = re.compile(r"\b(?:to|href|path)\s*:\s*[\"'](/[^\"'#?]+)[\"']")

PRISMA_MODEL_RE = re.compile(r"^\s*model\s+(\w+)\s*\{([^}]*)\}", re.MULTILINE | re.DOTALL)
PRISMA_FIELD_Skip = {
    "id",
    "createdAt",
    "updatedAt",
    "deletedAt",
    "created_at",
    "updated_at",
    "deleted_at",
    "password",
    "passwordHash",
    "password_hash",
}

ROLE_ENUM_RE = re.compile(r"\benum\s+(\w*Role\w*)\s*\{([^}]*)\}", re.MULTILINE | re.DOTALL)
PREAUTH_ROLE_RE = re.compile(r"has(?:Any)?Role\(([^)]+)\)")

EXPRESS_ROUTE_RE = re.compile(
    r"\b(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*[\"'](/[^\"']+)[\"']",
    re.IGNORECASE,
)


def _is_ignored(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = path.parts
    return any(part in IGNORE_DIRS for part in rel_parts)


def _iter_files(root: Path, suffixes: set[str]):
    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")
        )
        dp = Path(dirpath)
        for fname in sorted(filenames):
            p = dp / fname
            if p.suffix.lower() in suffixes:
                yield p


def _flatten_json(obj: Any, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict):
                out.update(_flatten_json(v, full_key))
            elif isinstance(v, str):
                out[full_key] = v
    return out


def _collect_i18n_stubs(root: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Returns (stub_keys_map, locale_files_list)."""
    stub_keys: dict[str, dict[str, str]] = {}
    locale_files: list[str] = []

    for json_file in _iter_files(root, {".json"}):
        rel = json_file.relative_to(root).as_posix()
        lower_rel = rel.lower()
        if not any(tok in lower_rel for tok in ("locale", "i18n", "messages", "translation", "lang")):
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        locale_files.append(rel)
        flat = _flatten_json(data)
        for key, val in flat.items():
            if STUB_VALUE_RE.search(val) or STUB_KEY_RE.search(key):
                kind = "action" if STUB_ACTION_VALUE_RE.search(val) or STUB_ACTION_VALUE_RE.search(key) else "page"
                if key not in stub_keys:
                    stub_keys[key] = {"value": val, "file": rel, "kind": kind}

    return stub_keys, locale_files


def _scan_stubs_and_todos(
    root: Path, stub_keys: dict[str, dict[str, str]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    stub_pages: list[dict[str, Any]] = []
    stub_actions: list[dict[str, Any]] = []
    todo_count = 0

    key_pattern: re.Pattern[str] | None = None
    if stub_keys:
        escaped = sorted((re.escape(k) for k in stub_keys), key=len, reverse=True)
        key_pattern = re.compile(
            r"\bt\s*\(\s*[\"'](" + "|".join(escaped) + r")[\"']"
        )

    for file_path in _iter_files(root, CODE_EXTENSIONS):
        rel = file_path.relative_to(root).as_posix()
        lower_rel = rel.lower()
        if (
            "/tests/" in f"/{lower_rel}"
            or "/__tests__/" in f"/{lower_rel}"
            or ".test." in lower_rel
            or ".spec." in lower_rel
        ):
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()

        for idx, line in enumerate(lines, start=1):
            if TODO_RE.search(line):
                todo_count += 1

            matched_i18n = False
            if key_pattern:
                for m in key_pattern.finditer(line):
                    matched_i18n = True
                    k = m.group(1)
                    meta = stub_keys[k]
                    is_action = bool(TOAST_CALL_RE.search(line)) or meta["kind"] == "action"
                    entry = {
                        "file": rel,
                        "line": idx,
                        "source": "i18n",
                        "i18n_key": k,
                        "evidence": meta["value"],
                    }
                    if is_action:
                        stub_actions.append(entry)
                    else:
                        stub_pages.append(entry)

            if not matched_i18n:
                # False-positive protection: ignore HTML/JSX input placeholder attributes
                cleaned_line = re.sub(r"\bplaceholder\s*=\s*(?:[\"'][^\"']*[\"']|\{[^}]*\})", "", line)
                lit = LITERAL_STUB_RE.search(cleaned_line)
                if lit:
                    entry = {
                        "file": rel,
                        "line": idx,
                        "source": "literal",
                        "i18n_key": None,
                        "evidence": lit.group(0).strip("<> "),
                    }
                    if TOAST_CALL_RE.search(line):
                        stub_actions.append(entry)
                    else:
                        stub_pages.append(entry)

    return stub_pages, stub_actions, todo_count


def _route_matches(link: str, declared_routes: set[str], wildcard_prefixes: set[str], has_relative_children: bool) -> bool:
    norm_link = "/" + link.strip("/")
    if norm_link in declared_routes or link in declared_routes:
        return True

    for route in declared_routes:
        if route.endswith("/*"):
            continue
        norm_route = "/" + route.strip("/")
        pattern = re.escape(norm_route)
        pattern = re.sub(r"\\:[a-zA-Z0-9_]+", r"[^/]+", pattern)
        pattern = re.sub(r"\\\[[^\]]+\\\]", r"[^/]+", pattern)
        pattern = re.sub(r"\\\{[^}]+\\\}", r"[^/]+", pattern)
        if re.fullmatch(pattern, norm_link):
            return True

    if not has_relative_children:
        for prefix in wildcard_prefixes:
            if norm_link == prefix or norm_link.startswith(prefix + "/"):
                return True

    return False


def _scan_routes_and_links(root: Path) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    declared_raw: list[str] = []
    relative_children: list[str] = []
    links: list[dict[str, Any]] = []
    fe_stack: list[str] = []

    for file_path in _iter_files(root, CODE_EXTENSIONS):
        rel = file_path.relative_to(root).as_posix()
        lower_rel = rel.lower()
        if (
            "/tests/" in f"/{lower_rel}"
            or "/__tests__/" in f"/{lower_rel}"
            or ".test." in lower_rel
            or ".spec." in lower_rel
        ):
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")

        # Next.js App Router file-system routes
        if re.match(r"^(?:src/)?app/(?:.+/)?page\.(?:tsx|jsx|ts|js)$", rel):
            if "nextjs-app-router" not in fe_stack:
                fe_stack.append("nextjs-app-router")
            route_part = re.sub(r"^(?:src/)?app", "", rel)
            route_part = re.sub(r"/page\.(?:tsx|jsx|ts|js)$", "", route_part)
            route_part = re.sub(r"/\([^)]+\)", "", route_part) or "/"
            declared_raw.append(route_part)

        lines = text.splitlines()
        is_nav_file = any(tok in rel.lower() for tok in ("sidebar", "menu", "nav", "header", "layout"))

        for idx, line in enumerate(lines, start=1):
            for m in JSX_ROUTE_RE.finditer(line):
                if "react-router" not in fe_stack:
                    fe_stack.append("react-router")
                r_path = m.group(1).strip()
                if r_path.startswith("/"):
                    declared_raw.append(r_path)
                elif r_path and r_path != "*":
                    relative_children.append(r_path.strip("/"))

            if not is_nav_file and ("createBrowserRouter" in text or "useRoutes" in text or "createRouter" in text):
                for m in OBJ_ROUTE_RE.finditer(line):
                    declared_raw.append(m.group(1).strip())

            for m in LINK_TO_RE.finditer(line):
                links.append({"path": m.group(1), "file": rel, "line": idx})
            for m in NAVIGATE_RE.finditer(line):
                links.append({"path": m.group(1), "file": rel, "line": idx})
            if is_nav_file:
                for m in NAV_ITEM_PATH_RE.finditer(line):
                    links.append({"path": m.group(1), "file": rel, "line": idx})

    wildcard_prefixes: set[str] = set()
    declared_set: set[str] = set()
    for r in declared_raw:
        declared_set.add(r)
        if r.endswith("/*"):
            prefix = "/" + r[:-2].strip("/")
            wildcard_prefixes.add(prefix)
            declared_set.add(prefix)

    for prefix in wildcard_prefixes:
        for child in relative_children:
            declared_set.add(f"{prefix}/{child}")

    broken: list[dict[str, Any]] = []
    if declared_set:
        seen_broken: set[tuple[str, str, int]] = set()
        for lnk in links:
            lp = lnk["path"]
            if not _route_matches(lp, declared_set, wildcard_prefixes, bool(relative_children)):
                key = (lp, lnk["file"], lnk["line"])
                if key not in seen_broken:
                    seen_broken.add(key)
                    broken.append({
                        "link": lp,
                        "file": lnk["file"],
                        "line": lnk["line"],
                        "confidence": "high",
                    })

    return sorted(declared_set), links, broken, fe_stack


def _normalize_api_path(path: str) -> str:
    p = path.strip()
    p = re.sub(r"^https?://[^/]+", "", p)
    p = p.split("?")[0]
    p = re.sub(r"^/api(?:/v\d+)?(?=/|$)", "", p)
    p = re.sub(r"^/v\d+(?=/|$)", "", p)
    p = re.sub(r"\$\{[^}]+\}", "{param}", p)
    p = re.sub(r"\{[^}]+\}", "{param}", p)
    p = re.sub(r":([a-zA-Z0-9_]+)", "{param}", p)
    p = "/" + p.strip("/")
    return p


def _load_check_api_docs():
    here = Path(__file__).resolve()
    candidate = here.parents[2] / "musgoku" / "scripts" / "check_api_docs.py"
    if not candidate.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("check_api_docs", candidate)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    except Exception:
        return None
    return None


def _scan_backend_endpoints(roots: list[Path]) -> tuple[list[dict[str, str]], list[str]]:
    endpoints: list[dict[str, str]] = []
    be_stack: list[str] = []
    api_mod = _load_check_api_docs()

    for r in roots:
        if api_mod is not None:
            java_eps, _, _ = api_mod.scan_java(r)
            if java_eps and "spring" not in be_stack:
                be_stack.append("spring")
            for method, full_path, fname in java_eps:
                endpoints.append({"method": method, "path": full_path, "file": fname})

            multi_eps = api_mod.scan_multi_stack_routes(r)
            if multi_eps and "nextjs-or-fastapi" not in be_stack:
                be_stack.append("nextjs-or-fastapi")
            for method, full_path, fname in multi_eps:
                endpoints.append({"method": method, "path": full_path, "file": fname})

        for fpath in _iter_files(r, {".ts", ".js", ".mjs"}):
            text = fpath.read_text(encoding="utf-8", errors="replace")
            for m in EXPRESS_ROUTE_RE.finditer(text):
                if "express" not in be_stack:
                    be_stack.append("express")
                endpoints.append({
                    "method": m.group(1).upper(),
                    "path": m.group(2),
                    "file": fpath.name,
                })

    return endpoints, be_stack


def _scan_orphan_endpoints(root: Path, peers: list[Path]) -> tuple[list[dict[str, str]], list[str]]:
    all_roots = [root] + list(peers)
    backend_eps, be_stack = _scan_backend_endpoints(all_roots)
    if not backend_eps:
        return [], be_stack

    fe_Paths_norm: set[str] = set()
    str_lit_re = re.compile(r"[\"'`](/[a-zA-Z0-9_/\-{}:.$]+)[\"'`]")
    for fpath in _iter_files(root, CODE_EXTENSIONS):
        text = fpath.read_text(encoding="utf-8", errors="replace")
        for m in str_lit_re.finditer(text):
            fe_Paths_norm.add(_normalize_api_path(m.group(1)))

    orphans: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for ep in backend_eps:
        norm_ep = _normalize_api_path(ep["path"])
        if norm_ep not in fe_Paths_norm:
            key = (ep["method"], ep["path"])
            if key not in seen:
                seen.add(key)
                orphans.append({
                    "method": ep["method"],
                    "path": ep["path"],
                    "file": ep["file"],
                    "confidence": "candidate",
                })

    return orphans, be_stack


def _camel_to_snake(name: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


JPA_FIELD_RE = re.compile(
    r"^[ \t]*private[ \t]+(?:final[ \t]+)?[A-Za-z0-9_<>, \t\?]+[ \t]+([a-z][A-Za-z0-9_]*)[ \t]*(?:=|;)",
    re.MULTILINE,
)
SQL_ADD_COL_RE = re.compile(
    r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:public\.)?[\"`]?(\w+)[\"`]?\s+ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`]?(\w+)[\"`]?",
    re.IGNORECASE,
)


def _scan_orphan_fields(root: Path, peers: list[Path]) -> list[dict[str, str]]:
    all_roots = [root] + list(peers)
    declared_fields: list[tuple[str, str, str]] = []

    for r in all_roots:
        for prisma_file in _iter_files(r, {".prisma"}):
            rel = prisma_file.relative_to(r).as_posix()
            text = prisma_file.read_text(encoding="utf-8", errors="replace")
            for m in PRISMA_MODEL_RE.finditer(text):
                entity = m.group(1)
                body = m.group(2)
                for line in body.splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith("//") or stripped.startswith("@@"):
                        continue
                    tokens = stripped.split()
                    if len(tokens) >= 2:
                        fname = tokens[0]
                        if fname not in PRISMA_FIELD_Skip and not fname.startswith("@"):
                            declared_fields.append((entity, fname, rel))

        for java_file in _iter_files(r, {".java"}):
            text = java_file.read_text(encoding="utf-8", errors="replace")
            if "@Entity" not in text:
                continue
            rel = java_file.relative_to(r).as_posix()
            cls_m = re.search(r"\bclass\s+(\w+)", text)
            entity = cls_m.group(1) if cls_m else java_file.stem
            for m in JPA_FIELD_RE.finditer(text):
                fname = m.group(1)
                if fname not in PRISMA_FIELD_Skip and fname != "serialVersionUID":
                    declared_fields.append((entity, fname, rel))

        for sql_file in _iter_files(r, {".sql"}):
            rel = sql_file.relative_to(r).as_posix()
            text = sql_file.read_text(encoding="utf-8", errors="replace")
            for m in SQL_ADD_COL_RE.finditer(text):
                table_name, col_name = m.group(1), m.group(2)
                if col_name not in PRISMA_FIELD_Skip:
                    declared_fields.append((table_name, col_name, rel))

    if not declared_fields:
        return []

    ui_identifiers: set[str] = set()
    ident_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    for fpath in _iter_files(root, UI_EXTENSIONS | {".ts", ".js"}):
        text = fpath.read_text(encoding="utf-8", errors="replace")
        ui_identifiers.update(ident_re.findall(text))

    orphans: list[dict[str, str]] = []
    for entity, field, source in declared_fields:
        snake = _camel_to_snake(field)
        camel = _snake_to_camel(field)
        if field not in ui_identifiers and snake not in ui_identifiers and camel not in ui_identifiers:
            orphans.append({
                "entity": entity,
                "field": field,
                "source": source,
                "confidence": "candidate",
            })

    return orphans


def _scan_roles(root: Path, peers: list[Path]) -> list[dict[str, str]]:
    roles: list[dict[str, str]] = []
    seen: set[str] = set()
    for r in [root] + list(peers):
        for fpath in _iter_files(r, CODE_EXTENSIONS | {".java", ".prisma"}):
            rel = fpath.relative_to(r).as_posix()
            text = fpath.read_text(encoding="utf-8", errors="replace")
            for m in ROLE_ENUM_RE.finditer(text):
                body = m.group(2)
                for item in re.findall(r"^\s*([A-Z][A-Z0-9_]{2,})\b", body, re.MULTILINE):
                    if item not in seen:
                        seen.add(item)
                        roles.append({"name": item, "source": rel})
            for m in PREAUTH_ROLE_RE.finditer(text):
                for item in re.findall(r"[\"']([A-Z0-9_]+)[\"']", m.group(1)):
                    if item not in seen:
                        seen.add(item)
                        roles.append({"name": item, "source": rel})
    return roles


def _scan_core_modules(root: Path) -> dict[str, list[str]]:
    modules: dict[str, list[str]] = {
        "dashboard": [],
        "profile": [],
        "settings": [],
        "notifications": [],
    }
    for fpath in _iter_files(root, UI_EXTENSIONS):
        rel = fpath.relative_to(root).as_posix()
        lower = rel.lower()
        for key in modules:
            if key in lower:
                modules[key].append(rel)
    return modules


def scan(
    root: Path | str,
    peers: list[Path | str] | None = None,
    focus: list[str] | None = None,
) -> dict[str, Any]:
    """Public seam: runs 5D gap discovery on `root` and optional `peers`."""
    root_path = Path(root).resolve()
    peer_paths = [Path(p).resolve() for p in (peers or [])]

    stub_keys, locale_files = _collect_i18n_stubs(root_path)
    stub_pages, stub_actions, todo_count = _scan_stubs_and_todos(root_path, stub_keys)
    declared_routes, links, broken_routes, fe_stack = _scan_routes_and_links(root_path)
    orphan_endpoints, be_stack = _scan_orphan_endpoints(root_path, peer_paths)
    orphan_fields = _scan_orphan_fields(root_path, peer_paths)
    roles = _scan_roles(root_path, peer_paths)
    core_modules = _scan_core_modules(root_path)

    return {
        "schema": SCHEMA_VERSION,
        "roots": {
            "root": root_path.as_posix(),
            "peers": [p.as_posix() for p in peer_paths],
        },
        "focus": focus or ["all"],
        "stack": {
            "frontend": fe_stack,
            "backend": be_stack,
            "i18n": locale_files,
        },
        "summary": {
            "stub_pages": len(stub_pages),
            "stub_actions": len(stub_actions),
            "broken_routes": len(broken_routes),
            "orphan_endpoints": len(orphan_endpoints),
            "orphan_fields": len(orphan_fields),
            "todo_markers": todo_count,
        },
        "stub_pages": stub_pages,
        "stub_actions": stub_actions,
        "routes": {
            "declared": declared_routes,
            "links": links,
        },
        "broken_routes": broken_routes,
        "orphan_endpoints": orphan_endpoints,
        "orphan_fields": orphan_fields,
        "roles": roles,
        "core_modules": core_modules,
        "warnings": [],
    }


def _format_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# Feature Architect — Gap Scanner Evidence Summary",
        "",
        f"- **Root:** `{report['roots']['root']}`",
        f"- **Peers:** `{', '.join(report['roots']['peers']) or 'none'}`",
        f"- **Stub Pages:** {s['stub_pages']} · **Stub Actions:** {s['stub_actions']} · **Broken Routes:** {s['broken_routes']}",
        f"- **Candidate Orphan Endpoints:** {s['orphan_endpoints']} · **Candidate Orphan Fields:** {s['orphan_fields']}",
        "",
        "## 1. Stub Pages",
    ]
    if report["stub_pages"]:
        for item in report["stub_pages"]:
            lines.append(f"- `{item['file']}:{item['line']}` ({item['source']}: `{item['i18n_key'] or 'literal'}`) — {item['evidence']}")
    else:
        lines.append("- None detected.")

    lines.append("\n## 2. Stub Actions (Dead Controls / Toasts)")
    if report["stub_actions"]:
        for item in report["stub_actions"]:
            lines.append(f"- `{item['file']}:{item['line']}` (`{item['i18n_key'] or 'literal'}`) — {item['evidence']}")
    else:
        lines.append("- None detected.")

    lines.append("\n## 3. Broken / Unresolved Routes")
    if report["broken_routes"]:
        for item in report["broken_routes"]:
            lines.append(f"- `{item['link']}` referenced at `{item['file']}:{item['line']}`")
    else:
        lines.append("- None detected.")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feature Architect — 5D Product Gap Scanner")
    parser.add_argument("--root", default=".", help="Target project root directory")
    parser.add_argument("--peer", action="append", default=[], help="Peer backend/frontend repository path")
    parser.add_argument("--focus", default="", help="Comma-separated focus areas")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--format", choices=["json", "md"], default="md", help="Output format")
    args = parser.parse_args(argv)

    root_path = Path(args.root)
    if not root_path.is_dir():
        print(f"[ERROR] Root directory does not exist: {args.root}", file=sys.stderr)
        return 2

    for p in args.peer:
        if not Path(p).is_dir():
            print(f"[ERROR] Peer directory does not exist: {p}", file=sys.stderr)
            return 2

    focus_list = [f.strip() for f in args.focus.split(",") if f.strip()] if args.focus else None
    report = scan(root_path, peers=args.peer, focus=focus_list)

    if args.json or args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
