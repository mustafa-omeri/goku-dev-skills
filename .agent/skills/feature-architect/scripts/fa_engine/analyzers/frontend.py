# -*- coding: utf-8 -*-
"""Multi-stack Frontend Deterministic Analyzer (`frontend.py`).

Extracts routes, screens, components, interactive action controls, unwired callback props,
hardcoded UI datasets, UI-without-backend screens, i18n/literal stubs, client API calls,
TypeScript DTO interfaces, and design-token/UX-state telemetry.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..model import (
     CoverageReport,
    Edge,
    EvidenceRef,
    Fact,
    Node,
    ProjectProfile,
    iter_repo_files,
    normalize_api_path,
)
from .base import AnalyzerContext, AnalyzerResult

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

JSX_ROUTE_RE = re.compile(
    r"<Route\b([\s\S]{0,160}?)\bpath\s*=\s*[\"']([^\"']+)[\"']([\s\S]{0,600}?)(?:/>|</Route>)",
    re.MULTILINE,
)
ROUTE_ELEMENT_COMP_RE = re.compile(r"<([A-Z][A-Za-z0-9_]*)\b")
ROUTE_WRAPPER_COMPS = {"RequireAuth", "ProtectedRoute", "PrivateRoute", "AuthGuard", "Suspense", "ErrorBoundary", "Navigate"}
OBJ_ROUTE_RE = re.compile(r"\bpath\s*:\s*[\"'](/[^\"']*)[\"']")
LINK_TO_RE = re.compile(r"<(?:Link|NavLink)\b[^>]*?\bto\s*=\s*[\"'](/[^\"'#?]*)[\"']")
NAVIGATE_RE = re.compile(r"\b(?:navigate|router\.push)\s*\(\s*[\"'](/[^\"'#?]*)[\"']")
WINDOW_LOC_NAV_RE = re.compile(
    r"\b(?:window\.)?location(?:\.href\s*=\s*|\.(?:assign|replace)\s*\(\s*)[\"'`](/[^\"'`#?]+)"
)
NAV_ITEM_PATH_RE = re.compile(r"\b(?:to|href|path)\s*:\s*[\"'](/[^\"'#?]+)[\"']")
NAV_ROLE_ITEM_RE = re.compile(
    r"\{\s*path\s*:\s*[\"']([^\"']+)[\"'][^{}]*?\broles\s*:\s*\[([^\]]+)\]",
    re.DOTALL,
)

TS_INTERFACE_RE = re.compile(
    r"\b(?:export\s+)?interface\s+([A-Z][A-Za-z0-9_]*)\s*(?:extends\s+[^{]+)?\{([^}]*)\}",
    re.MULTILINE | re.DOTALL,
)
TS_FIELD_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)(\?)?\s*:\s*([^;,\n]+)", re.MULTILINE)

COMP_FUNC_RE = re.compile(
    r"\b(?:export\s+(?:default\s+)?)?function\s+([A-Z][A-Za-z0-9_]*)\s*\(([^)]*)\)",
    re.MULTILINE,
)
COMP_ARROW_RE = re.compile(
    r"\b(?:export\s+)?const\s+([A-Z][A-Za-z0-9_]*)\s*(?::\s*React\.FC<([A-Za-z0-9_]+)>)?\s*=\s*\(([^)]*)\)\s*=>",
    re.MULTILINE,
)

HTTP_CALL_TYPED_RE = re.compile(
    r"(?:export\s+(?:const|async\s+function|function)\s+([A-Za-z_][A-Za-z0-9_]*)[^{;\n]*?)?"
    r"\b(axios|apiClient|http|[A-Za-z0-9_]*[Aa]pi)\.(get|post|put|patch|delete)"
    r"(?:\s*<\s*([A-Za-z0-9_<>, \[\]|]+)\s*>)?\s*\(\s*[\"'`]([^\"'`]+)[\"'`]",
    re.MULTILINE,
)
FETCH_CALL_RE = re.compile(
    r"\bfetch\s*\(\s*[\"'`]((?:/|https?://)[^\"'`]+)[\"'`](?:\s*,\s*\{[^}]*?\bmethod\s*:\s*[\"']([A-Za-z]+)[\"'])?",
    re.MULTILINE | re.DOTALL,
)
HOOK_DEF_RE = re.compile(
    r"\bexport\s+(?:function|const)\s+(use[A-Z][A-Za-z0-9_]*)\b([\s\S]{0,1200}?)(?=\nexport\s+|\Z)"
)

HARDCODED_ARRAY_RE = re.compile(
    r"\bconst\s+([a-z][A-Za-z0-9_]*)\s*(?::\s*[^=]+)?=\s*\[\s*\{[\s\S]{10,1200}?\},\s*\{[\s\S]{10,1200}?\}\s*\]",
    re.MULTILINE,
)
HASH_HREF_JSX_RE = re.compile(r"<a\b[^>]*?\bhref\s*=\s*(?:[\"']#[\"']|\{[\"'`]#[\"'`]\})[^>]*>")
HASH_HREF_DATA_RE = re.compile(r"\b(?:href|to|url)\s*:\s*[\"']#[\"']")
EMPTY_ONCLICK_RE = re.compile(r"\bonClick\s*=\s*\{\s*\(\s*\)\s*=>\s*\{\s*\}\s*\}")
ROLE_VISIBILITY_RE = re.compile(
    r"(?:role\s*===\s*[\"']([A-Z0-9_]+)[\"']|roles\s*:\s*\[([^\]]+)\]|allowedRoles\s*=\s*\{\[([^\]]+)\]\})"
)
HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{6}\b")


def _is_test_rel(rel: str) -> bool:
    low = rel.lower()
    return (
        "/tests/" in f"/{low}"
        or "/__tests__/" in f"/{low}"
        or ".test." in low
        or ".spec." in low
        or low.endswith(".d.ts")
    )


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


def _route_matches(
    link: str,
    declared_routes: set[str],
    wildcard_prefixes: set[str],
    has_relative_children: bool,
) -> bool:
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


def _unwrap_generic_type(raw_type: str | None) -> str | None:
    if not raw_type:
        return None
    cleaned = raw_type.strip()
    # Unwrap common envelopes e.g. UnifiedApiResponse<OrderDto> or ApiResponse<Page<ItemDto>>
    for _ in range(3):
        m = re.match(
            r"^(?:UnifiedApiResponse|ApiResponse|ResponseEnvelope|AxiosResponse|Page|PaginatedResponse|Array|ReadonlyArray)\s*<\s*(.+)\s*>$",
            cleaned,
        )
        if m:
            cleaned = m.group(1).strip()
        else:
            break
    if cleaned.endswith("[]"):
        cleaned = cleaned[:-2].strip()
    return cleaned if re.match(r"^[A-Z][A-Za-z0-9_]*$", cleaned) else None


def _find_rendered_hardcoded_arrays(text: str) -> list[tuple[str, int]]:
    """Find `const <arr> = [ { ... }, { ... } ]` rendered via `<arr>.map(` or `<alias>.map(`."""
    found: list[tuple[str, int]] = []
    seen_names: set[str] = set()
    for hm in HARDCODED_ARRAY_RE.finditer(text):
        arr_name = hm.group(1)
        if re.search(rf"\b{re.escape(arr_name)}\.map\s*\(", text):
            hline = text[: hm.start()].count("\n") + 1
            found.append((arr_name, hline))
            seen_names.add(arr_name)

    # Also detect multiline object arrays with nested braces (e.g. defaultActions in QuickActionsPanel)
    decl_re = re.compile(r"\bconst\s+([a-z][A-Za-z0-9_]*)\s*(?::\s*[^=;\n]+)?=\s*\[", re.MULTILINE)
    for dm in decl_re.finditer(text):
        arr_name = dm.group(1)
        if arr_name in seen_names:
            continue
        start_bracket = dm.end() - 1
        depth = 0
        end_bracket = -1
        for i in range(start_bracket, min(len(text), start_bracket + 4500)):
            ch = text[i]
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    end_bracket = i
                    break
        if end_bracket == -1:
            continue
        arr_body = text[start_bracket + 1 : end_bracket]
        if len(re.findall(r"\{\s*(?:id|label|title|key|name)\s*:", arr_body)) < 2:
            continue
        is_mapped = bool(re.search(rf"\b{re.escape(arr_name)}\.map\s*\(", text))
        if not is_mapped:
            alias_m = re.search(
                rf"\bconst\s+([a-z][A-Za-z0-9_]*)\s*=\s*[A-Za-z0-9_?.]+\s*\|\|\s*{re.escape(arr_name)}\b",
                text,
            )
            if alias_m and re.search(rf"\b{re.escape(alias_m.group(1))}\.map\s*\(", text):
                is_mapped = True
        if is_mapped:
            hline = text[: dm.start()].count("\n") + 1
            found.append((arr_name, hline))
            seen_names.add(arr_name)
    return found


def _run_ts_bridge(root: Path, ts_lib: str, rel_files: list[str]) -> dict[str, Any] | None:
    bridge_script = Path(__file__).resolve().parents[2] / "ts_bridge" / "extract.mjs"
    if not bridge_script.is_file() or not rel_files:
        return None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as tf:
            json.dump(rel_files, tf)
            tmp_json = Path(tf.name)
        try:
            proc = subprocess.run(
                [
                    "node",
                    str(bridge_script),
                    "--ts-lib",
                    ts_lib,
                    "--root",
                    str(root),
                    "--files-json",
                    str(tmp_json),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=20,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return json.loads(proc.stdout)
        finally:
            tmp_json.unlink(missing_ok=True)
    except Exception:
        return None
    return None


class FrontendAnalyzer:
    name = "frontend"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        if profile.frontend_stacks:
            return True, f"Detected frontend stack(s): {', '.join(profile.frontend_stacks)}"
        # Also apply if UI files exist in primary root
        for fpath in iter_repo_files(profile.root, UI_EXTENSIONS):
            if not _is_test_rel(fpath.relative_to(profile.root).as_posix()):
                return True, "Detected UI component files in primary root"
        return False, "No frontend framework or UI source files detected"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        root = ctx.profile.root.resolve()
        applicable, reason = self.applies(ctx.profile)
        if not applicable:
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
            )

        nodes: list[Node] = []
        edges: list[Edge] = []
        facts: list[Fact] = []
        limitations: list[str] = []

        # 1. Collect i18n stub keys
        stub_keys: dict[str, dict[str, str]] = {}
        locale_files: list[str] = []
        for json_file in iter_repo_files(root, {".json"}):
            rel = json_file.relative_to(root).as_posix()
            if not any(tok in rel.lower() for tok in ("locale", "i18n", "messages", "translation", "lang")):
                continue
            try:
                data = json.loads(json_file.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            locale_files.append(rel)
            for k, val in _flatten_json(data).items():
                if STUB_VALUE_RE.search(val) or STUB_KEY_RE.search(k):
                    kind = "action" if (STUB_ACTION_VALUE_RE.search(val) or STUB_ACTION_VALUE_RE.search(k)) else "page"
                    stub_keys.setdefault(k, {"value": val, "file": rel, "kind": kind})

        key_pattern: re.Pattern[str] | None = None
        if stub_keys:
            escaped = sorted((re.escape(k) for k in stub_keys), key=len, reverse=True)
            key_pattern = re.compile(r"\bt\s*\(\s*[\"'](" + "|".join(escaped) + r")[\"']")

        code_files: list[Path] = []
        for fp in iter_repo_files(root, CODE_EXTENSIONS):
            if not _is_test_rel(fp.relative_to(root).as_posix()):
                code_files.append(fp)

        ast_data: dict[str, Any] | None = None
        derivation_mode = "syntax"
        if ctx.profile.ts_compiler_path:
            ts_files = [
                fp.relative_to(root).as_posix()
                for fp in code_files
                if fp.suffix.lower() in {".ts", ".tsx", ".js", ".jsx"}
            ]
            ast_data = _run_ts_bridge(root, ctx.profile.ts_compiler_path, ts_files[:25])
            if ast_data is not None:
                derivation_mode = "ast"
        else:
            limitations.append(
                "Target node_modules/typescript not present; using deterministic balanced syntax extractor."
            )

        stub_pages: list[dict[str, Any]] = []
        stub_actions: list[dict[str, Any]] = []
        todo_count = 0
        declared_raw: list[str] = []
        relative_children: list[str] = []
        route_to_comp: dict[str, tuple[str, str, int]] = {}
        links: list[dict[str, Any]] = []
        fe_stack: list[str] = list(ctx.profile.frontend_stacks)
        core_modules: dict[str, list[str]] = {
            "dashboard": [],
            "profile": [],
            "settings": [],
            "notifications": [],
        }

        interfaces: dict[str, dict[str, Any]] = {}
        components: dict[str, dict[str, Any]] = {}
        jsx_usages: list[dict[str, Any]] = []
        http_calls: list[dict[str, Any]] = []
        route_role_map: dict[str, dict[str, Any]] = {}
        action_items: list[dict[str, Any]] = []
        ui_identifiers: set[str] = set()
        ident_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
        hardcoded_hex_count = 0
        skeleton_files = 0

        for fpath in code_files:
            rel = fpath.relative_to(root).as_posix()
            text = fpath.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            ui_identifiers.update(ident_re.findall(text))

            if fpath.suffix.lower() in UI_EXTENSIONS:
                low_rel = rel.lower()
                for mod_key in core_modules:
                    if mod_key in low_rel:
                        core_modules[mod_key].append(rel)
                hardcoded_hex_count += len(HEX_COLOR_RE.findall(text))
                if "skeleton" in text.lower() or "animate-pulse" in text:
                    skeleton_files += 1

            # File-system routes (Next.js App Router & Vue/Nuxt pages)
            if re.match(r"^(?:src/)?app/(?:.+/)?page\.(?:tsx|jsx|ts|js)$", rel):
                if "nextjs-app-router" not in fe_stack:
                    fe_stack.append("nextjs-app-router")
                rp = re.sub(r"^(?:src/)?app", "", rel)
                rp = re.sub(r"/page\.(?:tsx|jsx|ts|js)$", "", rp)
                rp = re.sub(r"/\([^)]+\)", "", rp) or "/"
                declared_raw.append(rp)

            is_nav_file = any(tok in rel.lower() for tok in ("sidebar", "menu", "nav", "header", "layout"))

            for idx, line in enumerate(lines, start=1):
                if TODO_RE.search(line):
                    todo_count += 1

                # Stub detection (i18n + literal)
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
                            "excerpt": line.strip()[:160],
                        }
                        if is_action:
                            stub_actions.append(entry)
                        else:
                            stub_pages.append(entry)

                if not matched_i18n:
                    cleaned_line = re.sub(r"\bplaceholder\s*=\s*(?:[\"'][^\"']*[\"']|\{[^}]*\})", "", line)
                    lit = LITERAL_STUB_RE.search(cleaned_line)
                    if lit:
                        entry = {
                            "file": rel,
                            "line": idx,
                            "source": "literal",
                            "i18n_key": None,
                            "evidence": lit.group(0).strip("<> "),
                            "excerpt": line.strip()[:160],
                        }
                        if TOAST_CALL_RE.search(line):
                            stub_actions.append(entry)
                        else:
                            stub_pages.append(entry)

                # Route & navigation link extraction
                if not is_nav_file and any(
                    tok in text for tok in ("createBrowserRouter", "useRoutes", "createRouter")
                ):
                    for m in OBJ_ROUTE_RE.finditer(line):
                        declared_raw.append(m.group(1).strip())

                for m in LINK_TO_RE.finditer(line):
                    links.append({"path": m.group(1), "file": rel, "line": idx, "excerpt": line.strip()[:160]})
                for m in NAVIGATE_RE.finditer(line):
                    links.append({"path": m.group(1), "file": rel, "line": idx, "excerpt": line.strip()[:160]})
                for m in WINDOW_LOC_NAV_RE.finditer(line):
                    links.append({"path": m.group(1), "file": rel, "line": idx, "excerpt": line.strip()[:160]})
                if is_nav_file:
                    for m in NAV_ITEM_PATH_RE.finditer(line):
                        links.append({"path": m.group(1), "file": rel, "line": idx, "excerpt": line.strip()[:160]})

            for m in JSX_ROUTE_RE.finditer(text):
                if "react-router" not in fe_stack:
                    fe_stack.append("react-router")
                r_path = m.group(2).strip()
                r_line = text[: m.start()].count("\n") + 1
                full_attrs = m.group(1) + " " + m.group(3)
                cand_comps = [
                    c for c in ROUTE_ELEMENT_COMP_RE.findall(full_attrs) if c not in ROUTE_WRAPPER_COMPS
                ]
                comp_name = cand_comps[0] if cand_comps else None
                if r_path.startswith("/"):
                    declared_raw.append(r_path)
                    if comp_name:
                        route_to_comp[r_path] = (comp_name, rel, r_line)
                elif r_path and r_path != "*":
                    clean_rel = r_path.strip("/")
                    relative_children.append(clean_rel)
                    if comp_name:
                        route_to_comp[clean_rel] = (comp_name, rel, r_line)

            for nm in NAV_ROLE_ITEM_RE.finditer(text):
                nav_path = nm.group(1).strip().strip("/")
                roles_found = [
                    r for r in re.findall(r"[A-Z][A-Z0-9_]{2,}", nm.group(2)) if r != "ROLE"
                ]
                if nav_path and roles_found:
                    nline = text[: nm.start()].count("\n") + 1
                    route_role_map[nav_path] = {
                        "path": nav_path,
                        "roles": sorted(set(roles_found)),
                        "file": rel,
                        "line": nline,
                    }

            # LocalStorage phantom persistence in domain services (Notification Matrix, Settings, Preferences)
            stem_low = Path(rel).stem.lower()
            if (
                ("service" in rel.lower() or "store" in rel.lower())
                and not any(tok in stem_low for tok in ("auth", "token", "session", "api-client", "theme", "logger", "storage"))
            ):
                ls_m = re.search(r"\blocalStorage\.(?:getItem|setItem)\s*\(\s*([^,\)]+)", text)
                if ls_m:
                    key_expr = ls_m.group(1).strip()
                    if not any(tk in key_expr.lower() for tk in ("token", "auth", "jwt", "theme", "lang", "i18n")):
                        ls_line = text[: ls_m.start()].count("\n") + 1
                        ls_excerpt = lines[ls_line - 1].strip()[:160] if ls_line - 1 < len(lines) else ls_m.group(0)
                        facts.append(
                            Fact.create(
                                fact_id=f"FE-MOCK-{len(facts)+1:03d}",
                                code="LOCALSTORAGE_PHANTOM_PERSISTENCE",
                                category="ARCHITECTURE",
                                fact_type="structural",
                                severity="HIGH",
                                summary=(
                                    f"Domain service `{rel}:{ls_line}` persists state via browser `localStorage` "
                                    f"(`{key_expr}`) instead of a multi-tenant backend endpoint/database."
                                ),
                                location=f"{rel}:{ls_line}",
                                evidence=[
                                    EvidenceRef(
                                        kind="code",
                                        level="L1",
                                        derivation=derivation_mode,
                                        ref=f"{rel}:{ls_line}",
                                        line=ls_line,
                                        excerpt=ls_excerpt,
                                    )
                                ],
                                attrs={"storage_key_expr": key_expr},
                            )
                        )

            # Interfaces (TS types)
            for im in TS_INTERFACE_RE.finditer(text):
                iname = im.group(1)
                ibody = im.group(2)
                iline = text[: im.start()].count("\n") + 1
                fields: list[dict[str, Any]] = []
                for fm in TS_FIELD_RE.finditer(ibody):
                    fields.append(
                        {
                            "name": fm.group(1),
                            "optional": bool(fm.group(2)),
                            "type": fm.group(3).strip(),
                        }
                    )
                interfaces[iname] = {"name": iname, "file": rel, "line": iline, "fields": fields}
                nodes.append(
                    Node(
                        id=f"TsType:{iname}",
                        kind="TsType",
                        name=iname,
                        file=rel,
                        line=iline,
                        attrs={"fields": fields},
                    )
                )

            # Components & prop wiring
            if fpath.suffix.lower() in {".tsx", ".jsx"}:
                comp_matches: list[tuple[str, str, int]] = []
                for cm in COMP_FUNC_RE.finditer(text):
                    comp_matches.append((cm.group(1), cm.group(2), text[: cm.start()].count("\n") + 1))
                for cm in COMP_ARROW_RE.finditer(text):
                    param_sig = f"{cm.group(3)}: {cm.group(2)}" if cm.group(2) else cm.group(3)
                    comp_matches.append((cm.group(1), param_sig, text[: cm.start()].count("\n") + 1))

                for cname, param_sig, cline in comp_matches:
                    prop_type = None
                    pm = re.search(r":\s*([A-Z][A-Za-z0-9_]*Props\b|[A-Z][A-Za-z0-9_]*)", param_sig)
                    if pm:
                        prop_type = pm.group(1)
                    direct_handlers = re.findall(r"onClick\s*=\s*\{\s*([A-Za-z0-9_]+)\s*\}", text)
                    arrow_handlers = re.findall(
                        r"onClick\s*=\s*\{\s*(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>\s*(?:\{\s*)?([A-Za-z0-9_]+)(?:\?\.)?\s*\(",
                        text,
                    )
                    bound_handlers = sorted(set(direct_handlers + arrow_handlers))
                    has_state = bool(re.search(r"\buseState\s*(?:<[^>]+>)?\s*\(", text))
                    has_save_handler = bool(
                        re.search(r"\b(?:handleSave|onSave|handleSubmit|onSubmit|save\w*)\b", text)
                    )
                    has_api = bool(
                        re.search(
                            r"\b(?:useQuery|useMutation|useSWR|fetch|axios|apiClient|[A-Za-z0-9_]*[Aa]pi\.|use[A-Z]\w*(?:Query|Mutation|Data|Dashboard|Api))\b",
                            text,
                        )
                    )
                    visible_roles: list[str] = []
                    for rm in ROLE_VISIBILITY_RE.finditer(text):
                        raw_r = rm.group(1) or rm.group(2) or rm.group(3) or ""
                        visible_roles.extend(re.findall(r"[A-Z][A-Z0-9_]{2,}", raw_r))

                    is_screen = any(
                        seg in rel.lower() for seg in ("/pages/", "/views/", "page.tsx", "view.tsx")
                    )
                    kind = "Screen" if is_screen else "Component"
                    node_id = f"{kind}:{cname}"
                    components[cname] = {
                        "id": node_id,
                        "kind": kind,
                        "name": cname,
                        "file": rel,
                        "line": cline,
                        "prop_type": prop_type,
                        "bound_handlers": bound_handlers,
                        "has_state": has_state,
                        "has_save_handler": has_save_handler,
                        "has_api": has_api,
                        "visible_roles": sorted(set(visible_roles)),
                    }
                    nodes.append(
                        Node(
                            id=node_id,
                            kind=kind,
                            name=cname,
                            file=rel,
                            line=cline,
                            attrs={
                                "prop_type": prop_type,
                                "has_state": has_state,
                                "has_api": has_api,
                                "visible_roles": sorted(set(visible_roles)),
                            },
                        )
                    )

                    # Extract action items with navigation targets inside components (e.g. QuickActionsPanel)
                    for act_m in re.finditer(
                        r"\bid\s*:\s*[\"']([^\"']+)[\"'][\s\S]{0,320}?(?:window\.location(?:\.href)?\s*=\s*|navigate\s*\(\s*)[\"'](/[^\"']*)[\"']",
                        text,
                    ):
                        act_line = text[: act_m.start()].count("\n") + 1
                        action_items.append(
                            {
                                "id": act_m.group(1),
                                "target": act_m.group(2),
                                "component": cname,
                                "file": rel,
                                "line": act_line,
                                "has_role_guard": bool(re.search(r"\broles?\b", act_m.group(0), re.IGNORECASE)),
                            }
                        )

                # JSX element call sites (for unwired prop & graph edges)
                for jm in re.finditer(r"<([A-Z][A-Za-z0-9_]*)\b([^>]*?)(/?)>", text, re.DOTALL):
                    target_comp = jm.group(1)
                    if target_comp in {"Routes", "Route", "Link", "NavLink", "Fragment", "Suspense"}:
                        continue
                    attr_blob = jm.group(2)
                    jline = text[: jm.start()].count("\n") + 1
                    has_spread = "{..." in attr_blob
                    passed = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=", attr_blob)
                    excerpt_line = lines[jline - 1].strip()[:160] if jline - 1 < len(lines) else ""
                    jsx_usages.append(
                        {
                            "component": target_comp,
                            "file": rel,
                            "line": jline,
                            "passed_props": passed,
                            "has_spread": has_spread,
                            "excerpt": excerpt_line,
                        }
                    )

                # Dead controls (<a href="#">, href: '#', empty onClick={() => {}})
                for idx, line in enumerate(lines, start=1):
                    if HASH_HREF_JSX_RE.search(line) or HASH_HREF_DATA_RE.search(line) or EMPTY_ONCLICK_RE.search(line):
                        facts.append(
                            Fact.create(
                                fact_id=f"FE-DEAD-{len(facts)+1:03d}",
                                code="DEAD_ACTION_CONTROL",
                                category="UI_UX",
                                fact_type="structural",
                                severity="MEDIUM",
                                summary=f"Interactive control in `{rel}:{idx}` points to an inert `#` or empty handler.",
                                location=f"{rel}:{idx}",
                                evidence=[
                                    EvidenceRef(
                                        kind="code",
                                        level="L1",
                                        derivation=derivation_mode,
                                        ref=f"{rel}:{idx}",
                                        line=idx,
                                        excerpt=line.strip()[:160],
                                    )
                                ],
                            )
                        )

                # Hardcoded UI object arrays rendered via .map(...) (including nested & aliased arrays)
                for arr_name, hline in _find_rendered_hardcoded_arrays(text):
                    excerpt_line = lines[hline - 1].strip()[:160] if hline - 1 < len(lines) else arr_name
                    facts.append(
                        Fact.create(
                            fact_id=f"FE-DUMMY-{len(facts)+1:03d}",
                            code="HARDCODED_UI_DATASET",
                            category="PRODUCT",
                            fact_type="structural",
                            severity="MEDIUM",
                            summary=f"Hardcoded UI dataset `{arr_name}` in `{rel}:{hline}` is rendered directly without a backend data source.",
                            location=f"{rel}:{hline}",
                            evidence=[
                                EvidenceRef(
                                    kind="code",
                                    level="L1",
                                    derivation=derivation_mode,
                                    ref=f"{rel}:{hline}",
                                    line=hline,
                                    excerpt=excerpt_line,
                                )
                            ],
                            attrs={"dataset": arr_name},
                        )
                    )

                # UI Craft Floor Deficit check (repetitive <Separator /> + read-only <label>/<p> stacks)
                sep_count = len(re.findall(r"<Separator\b", text))
                readonly_label_p = len(re.findall(r"<label\b[^>]*>.*?</label>\s*<p\b", text, re.DOTALL))
                if sep_count >= 5 and readonly_label_p >= 4:
                    sep_m = re.search(r"<Separator\b", text)
                    sline = (text[: sep_m.start()].count("\n") + 1) if sep_m else 1
                    sexcerpt = lines[sline - 1].strip()[:160] if sline - 1 < len(lines) else "<Separator />"
                    facts.append(
                        Fact.create(
                            fact_id=f"FE-CRAFT-{len(facts)+1:03d}",
                            code="UI_CRAFT_FLOOR_DEFICIT",
                            category="UI_UX",
                            fact_type="structural",
                            severity="MEDIUM",
                            summary=(
                                f"Component `{rel}:{sline}` exhibits repetitive read-only `<label>/<p>` stacks "
                                f"({readonly_label_p} fields) separated by {sep_count} `<Separator>` dividers "
                                f"instead of structured semantic cards/forms."
                            ),
                            location=f"{rel}:{sline}",
                            evidence=[
                                EvidenceRef(
                                    kind="code",
                                    level="L1",
                                    derivation=derivation_mode,
                                    ref=f"{rel}:{sline}",
                                    line=sline,
                                    excerpt=sexcerpt,
                                )
                            ],
                            attrs={"separators": sep_count, "readonly_fields": readonly_label_p},
                        )
                    )

                # Monolithic UI God-Component check (> 1200 lines)
                if len(lines) > 1200:
                    facts.append(
                        Fact.create(
                            fact_id=f"FE-GOD-{len(facts)+1:03d}",
                            code="MONOLITHIC_UI_GOD_COMPONENT",
                            category="ARCHITECTURE",
                            fact_type="structural",
                            severity="HIGH",
                            summary=(
                                f"UI module `{rel}:1` is a {len(lines)}-line monolithic God-component that couples "
                                f"multiple domain workflows without modular sub-components or strategy boundaries."
                            ),
                            location=f"{rel}:1",
                            evidence=[
                                EvidenceRef(
                                    kind="code",
                                    level="L1",
                                    derivation=derivation_mode,
                                    ref=f"{rel}:1",
                                    line=1,
                                    excerpt=lines[0].strip()[:160] if lines else rel,
                                )
                            ],
                            attrs={"line_count": len(lines)},
                        )
                    )

            # Hooks & HTTP client calls
            for hkm in HOOK_DEF_RE.finditer(text):
                hname = hkm.group(1)
                hbody = hkm.group(2)
                hline = text[: hkm.start()].count("\n") + 1
                nodes.append(Node(id=f"Hook:{hname}", kind="Hook", name=hname, file=rel, line=hline))
                for api_call in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*Api\.[A-Za-z_][A-Za-z0-9_]*)\s*\(", hbody):
                    edges.append(
                        Edge(
                            source=f"Hook:{hname}",
                            target=f"ApiClientFn:{api_call}",
                            kind="calls",
                            derivation=derivation_mode,
                            evidence_ref=f"{rel}:{hline}",
                        )
                    )

            for cm in HTTP_CALL_TYPED_RE.finditer(text):
                fn_name = cm.group(1)
                client_obj = cm.group(2)
                verb = cm.group(3).upper()
                resp_generic = cm.group(4)
                raw_path = cm.group(5)
                cline = text[: cm.start()].count("\n") + 1
                excerpt_line = lines[cline - 1].strip()[:160] if cline - 1 < len(lines) else ""
                norm_p = normalize_api_path(raw_path)
                call_id = f"HttpCall:{verb}:{raw_path}@{rel}:{cline}"
                dto_name = _unwrap_generic_type(resp_generic)

                nodes.append(
                    Node(
                        id=call_id,
                        kind="HttpCall",
                        name=f"{verb} {raw_path}",
                        file=rel,
                        line=cline,
                        attrs={
                            "method": verb,
                            "raw_path": raw_path,
                            "normalized_path": norm_p,
                            "response_type": dto_name,
                        },
                    )
                )
                if fn_name:
                    module_stem = Path(rel).stem
                    qual_fn = f"{module_stem}.{fn_name}"
                    nodes.append(
                        Node(id=f"ApiClientFn:{qual_fn}", kind="ApiClientFn", name=qual_fn, file=rel, line=cline)
                    )
                    edges.append(
                        Edge(
                            source=f"ApiClientFn:{qual_fn}",
                            target=call_id,
                            kind="requests",
                            derivation=derivation_mode,
                            evidence_ref=f"{rel}:{cline}",
                        )
                    )
                if dto_name:
                    edges.append(
                        Edge(
                            source=call_id,
                            target=f"TsType:{dto_name}",
                            kind="expects",
                            derivation=derivation_mode,
                            evidence_ref=f"{rel}:{cline}",
                        )
                    )
                http_calls.append(
                    {
                        "id": call_id,
                        "method": verb,
                        "raw_path": raw_path,
                        "normalized_path": norm_p,
                        "response_type": dto_name,
                        "client": client_obj,
                        "file": rel,
                        "line": cline,
                        "excerpt": excerpt_line,
                    }
                )

            for fm in FETCH_CALL_RE.finditer(text):
                raw_path = fm.group(1)
                verb = (fm.group(2) or "GET").upper()
                fline = text[: fm.start()].count("\n") + 1
                excerpt_line = lines[fline - 1].strip()[:160] if fline - 1 < len(lines) else ""
                norm_p = normalize_api_path(raw_path)
                call_id = f"HttpCall:{verb}:{raw_path}@{rel}:{fline}"
                nodes.append(
                    Node(
                        id=call_id,
                        kind="HttpCall",
                        name=f"{verb} {raw_path}",
                        file=rel,
                        line=fline,
                        attrs={"method": verb, "raw_path": raw_path, "normalized_path": norm_p},
                    )
                )
                http_calls.append(
                    {
                        "id": call_id,
                        "method": verb,
                        "raw_path": raw_path,
                        "normalized_path": norm_p,
                        "response_type": None,
                        "client": "fetch",
                        "file": rel,
                        "line": fline,
                        "excerpt": excerpt_line,
                    }
                )

        # Evaluate routes & broken navigation links
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
                full_child = f"{prefix}/{child}"
                declared_set.add(full_child)
                if child in route_to_comp and full_child not in route_to_comp:
                    route_to_comp[full_child] = route_to_comp[child]

        for r_decl in sorted(declared_set):
            nodes.append(Node(id=f"Route:{r_decl}", kind="Route", name=r_decl))
            if r_decl in route_to_comp:
                comp_name, rfile, rline = route_to_comp[r_decl]
                target_id = components.get(comp_name, {}).get("id", f"Component:{comp_name}")
                edges.append(
                    Edge(
                        source=f"Route:{r_decl}",
                        target=target_id,
                        kind="renders",
                        derivation=derivation_mode,
                        evidence_ref=f"{rfile}:{rline}",
                    )
                )

        broken_v1: list[dict[str, Any]] = []
        broken_by_target: dict[str, list[dict[str, Any]]] = {}
        if declared_set:
            seen_broken: set[tuple[str, str, int]] = set()
            for lnk in links:
                lp = lnk["path"]
                if not _route_matches(lp, declared_set, wildcard_prefixes, bool(relative_children)):
                    key = (lp, lnk["file"], lnk["line"])
                    if key not in seen_broken:
                        seen_broken.add(key)
                        broken_v1.append(
                            {
                                "link": lp,
                                "file": lnk["file"],
                                "line": lnk["line"],
                                "confidence": "high",
                            }
                        )
                        broken_by_target.setdefault(lp, []).append(lnk)
                        edges.append(
                            Edge(
                                source=f"File:{lnk['file']}",
                                target=f"Route:{lp}",
                                kind="navigates_to",
                                derivation=derivation_mode,
                                evidence_ref=f"{lnk['file']}:{lnk['line']}",
                                unresolved=True,
                            )
                        )

        for target_lp, occs in sorted(broken_by_target.items()):
            first = occs[0]
            facts.append(
                Fact.create(
                    fact_id=f"FE-ROUTE-{len(facts)+1:03d}",
                    code="BROKEN_ROUTE",
                    category="BROKEN_ROUTE",
                    fact_type="structural",
                    severity="HIGH",
                    summary=f"Navigation target `{target_lp}` is not declared in router ({len(occs)} reference(s)).",
                    location=f"{first['file']}:{first['line']}",
                    evidence=[
                        EvidenceRef(
                            kind="code",
                            level="L1",
                            derivation=derivation_mode,
                            ref=f"{o['file']}:{o['line']}",
                            line=o["line"],
                            excerpt=o.get("excerpt", ""),
                        )
                        for o in occs[:5]
                    ],
                    attrs={"link": target_lp, "occurrences": len(occs)},
                )
            )

        # Unwired optional callback props check
        for usage in jsx_usages:
            comp_meta = components.get(usage["component"])
            if not comp_meta or usage["has_spread"]:
                continue
            ptype = comp_meta.get("prop_type")
            iface = interfaces.get(ptype) if ptype else None
            if not iface:
                continue
            optional_callbacks = {
                f["name"]
                for f in iface["fields"]
                if f["optional"] and f["name"].startswith("on") and "=>" in f["type"]
            }
            bound_callbacks = optional_callbacks & set(comp_meta.get("bound_handlers", []))
            for cb in sorted(bound_callbacks):
                if cb not in usage["passed_props"]:
                    facts.append(
                        Fact.create(
                            fact_id=f"FE-PROP-{len(facts)+1:03d}",
                            code="UNWIRED_ACTION_PROP",
                            category="UI_UX",
                            fact_type="structural",
                            severity="HIGH",
                            summary=(
                                f"`<{usage['component']} />` at `{usage['file']}:{usage['line']}` omits optional "
                                f"action prop `{cb}`, leaving its bound UI button/link non-functional."
                            ),
                            location=f"{usage['file']}:{usage['line']}",
                            evidence=[
                                EvidenceRef(
                                    kind="code",
                                    level="L1",
                                    derivation=derivation_mode,
                                    ref=f"{usage['file']}:{usage['line']}",
                                    line=usage["line"],
                                    excerpt=usage["excerpt"],
                                ),
                                EvidenceRef(
                                    kind="code",
                                    level="L1",
                                    derivation=derivation_mode,
                                    ref=f"{comp_meta['file']}:{comp_meta['line']}",
                                    line=comp_meta["line"],
                                    excerpt=f"onClick={{{cb}}}",
                                ),
                            ],
                            attrs={"component": usage["component"], "missing_prop": cb},
                        )
                    )

        # UI-without-backend screens check (local state + save action, zero API/hook integration)
        for cname, cmeta in sorted(components.items()):
            if cmeta["kind"] == "Screen" and cmeta["has_state"] and cmeta["has_save_handler"] and not cmeta["has_api"]:
                facts.append(
                    Fact.create(
                        fact_id=f"FE-LOCAL-{len(facts)+1:03d}",
                        code="UI_WITHOUT_BACKEND",
                        category="ARCHITECTURE",
                        fact_type="structural",
                        severity="HIGH",
                        summary=(
                            f"Screen `{cname}` (`{cmeta['file']}:{cmeta['line']}`) mutates local UI state with a "
                            f"save/submit handler but has zero backend API or query hook bindings."
                        ),
                        location=f"{cmeta['file']}:{cmeta['line']}",
                        evidence=[
                            EvidenceRef(
                                kind="code",
                                level="L1",
                                derivation=derivation_mode,
                                ref=f"{cmeta['file']}:{cmeta['line']}",
                                line=cmeta["line"],
                                excerpt=f"function {cname}",
                            )
                        ],
                        attrs={"screen": cname},
                    )
                )

        # Emit structured facts for stubs
        for sp in stub_pages:
            facts.append(
                Fact.create(
                    fact_id=f"FE-STUBP-{len(facts)+1:03d}",
                    code="STUB_PAGE",
                    category="STUB_PAGE",
                    fact_type="structural",
                    severity="HIGH",
                    summary=f"Stub/placeholder page content detected in `{sp['file']}:{sp['line']}`.",
                    location=f"{sp['file']}:{sp['line']}",
                    evidence=[
                        EvidenceRef(
                            kind="code",
                            level="L1",
                            derivation=derivation_mode,
                            ref=f"{sp['file']}:{sp['line']}",
                            line=sp["line"],
                            excerpt=sp.get("excerpt", sp["evidence"]),
                        )
                    ],
                )
            )
        for sa in stub_actions:
            facts.append(
                Fact.create(
                    fact_id=f"FE-STUBA-{len(facts)+1:03d}",
                    code="STUB_ACTION",
                    category="STUB_PAGE",
                    fact_type="structural",
                    severity="MEDIUM",
                    summary=f"Stub toast/placeholder action detected in `{sa['file']}:{sa['line']}`.",
                    location=f"{sa['file']}:{sa['line']}",
                    evidence=[
                        EvidenceRef(
                            kind="code",
                            level="L1",
                            derivation=derivation_mode,
                            ref=f"{sa['file']}:{sa['line']}",
                            line=sa["line"],
                            excerpt=sa.get("excerpt", sa["evidence"]),
                        )
                    ],
                )
            )

        v1_stub_pages = [{k: v for k, v in s.items() if k != "excerpt"} for s in stub_pages]
        v1_stub_actions = [{k: v for k, v in s.items() if k != "excerpt"} for s in stub_actions]
        v1_links = [{k: v for k, v in lnk.items() if k != "excerpt"} for lnk in links]

        ctx.shared_state["frontend"] = {
            "interfaces": interfaces,
            "components": components,
            "http_calls": http_calls,
            "route_role_map": route_role_map,
            "action_items": action_items,
            "jsx_usages": jsx_usages,
            "ui_identifiers": ui_identifiers,
            "declared_routes": sorted(declared_set),
            "links": v1_links,
            "broken_routes": broken_v1,
            "stub_pages": v1_stub_pages,
            "stub_actions": v1_stub_actions,
            "todo_count": todo_count,
            "locale_files": locale_files,
            "fe_stack": fe_stack,
            "core_modules": core_modules,
            "design_telemetry": {
                "hardcoded_hex_colors": hardcoded_hex_count,
                "files_with_skeleton_states": skeleton_files,
            },
        }

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            nodes=nodes,
            edges=edges,
            facts=facts,
            coverage=CoverageReport(scanned_files=len(code_files)),
            limitations=limitations,
            artifacts={"design_telemetry": ctx.shared_state["frontend"]["design_telemetry"]},
        )
