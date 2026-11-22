#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Birleşik Test Envanteri Çıkarıcı & Gherkin Dışa Aktarıcı (test_spec_scanner.py).

`feature-architect` (`fa_scan.run_scan_with_graph`) motorunu yeniden kullanarak
kod tabanı + kardeş repo yüzeylerini (rotalar, API uç noktaları, DB varlıkları,
roller, stub/kırık yapılar, çift-katmanlı `raw_hash`/`contract_hash` parmak izleri,
KG `impact` haritası) ve proje dokümanlarını (`PRODUCT.md`, PRD, API docs,
`specs/*.feature`, `HANDOFF.md`) tek bir deterministik test envanterine toplar.

Ayrıca üretilen tek dosya `ACCEPTANCE_TEST_SPEC.md` içindeki tüm (veya filtrelenmiş)
Gherkin bloklarını saf bir `.feature` dosyasına ayıklar (`--export-feature`).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

THIS_DIR = Path(__file__).resolve().parent
SKILLS_ROOT = THIS_DIR.parents[1]
FA_SCRIPTS_DIR = SKILLS_ROOT / "feature-architect" / "scripts"
if str(FA_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(FA_SCRIPTS_DIR))

import fa_scan  # noqa: E402
from fa_engine.model import iter_repo_files  # noqa: E402

REQ_ID_RE = re.compile(r"\b((?:FR|US|NFR|REQ|EPIC|AC)-[A-Z0-9-]*\d+)\b")
GHERKIN_FENCE_RE = re.compile(r"```gherkin\s*\r?\n(.*?)```", re.DOTALL | re.IGNORECASE)
FEATURE_LINE_RE = re.compile(r"^\s*(?:#[^\n]*\r?\n)*\s*Feature\s*:", re.IGNORECASE | re.MULTILINE)
SCENARIO_LINE_RE = re.compile(r"^\s*Scenario(?: Outline)?\s*:", re.IGNORECASE | re.MULTILINE)
SCENARIO_ID_RE = re.compile(r"\b(SC-[A-Z0-9]+-\d+)\b")
LANGUAGE_HEADER_RE = re.compile(r"^\s*#\s*language\s*:\s*([a-zA-Z_-]+)", re.IGNORECASE | re.MULTILINE)
API_DOC_EP_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/[A-Za-z0-9_/\-{}:.$]+)")

VALIDATION_SIGNAL_RE = re.compile(
    r"@(?:NotNull|NotBlank|NotEmpty|Size|Min|Max|Email|Pattern|Valid|PreAuthorize|Secured|RolesAllowed)\b"
    r"|\bz\.(?:string|number|boolean|object|array|enum)\b"
    r"|\b(?:required|minLength|maxLength|pattern)\s*:",
    re.MULTILINE,
)

CORE_DOC_NAMES = (
    "PROJECT_BRIEF.md",
    "PRODUCT.md",
    "DESIGN.md",
    "DB_MIGRATIONS.md",
    "GLOSSARY.md",
    "HANDOFF.md",
    "README.md",
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def sha256_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n")
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _extract_primary_language(root: Path) -> str:
    brief = root / "PROJECT_BRIEF.md"
    if brief.is_file():
        m = re.search(r"^primary_language:\s*(.+)$", _read_text(brief), re.MULTILINE)
        if m:
            return m.group(1).strip().strip("\"'")
    return "tr"


def _extract_project_slug(root: Path) -> str:
    brief = root / "PROJECT_BRIEF.md"
    if brief.is_file():
        m = re.search(r"^project:\s*(.+)$", _read_text(brief), re.MULTILINE)
        if m:
            return m.group(1).strip().strip("\"'")
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(_read_text(pkg))
            if data.get("name"):
                return str(data["name"]).strip()
        except json.JSONDecodeError:
            pass
    return root.name


def _collect_doc_files(root: Path) -> dict[str, Any]:
    """Projedeki çekirdek dokümanları, PRD/API/RFC dosyalarını ve specs/*.feature dosyalarını tarar."""
    docs_presence: dict[str, bool] = {}
    doc_paths: list[Path] = []

    for name in CORE_DOC_NAMES:
        cand = root / name
        exists = cand.is_file()
        docs_presence[name] = exists
        if exists:
            doc_paths.append(cand)

    glob_patterns = (
        "docs/**/*prd*.md",
        "docs/**/*spec*.md",
        "docs/APIs/**/*.md",
        "docs/rfc/**/*.md",
        "RFCs/**/*.md",
        "*prd*.md",
        "*PRD*.md",
    )
    seen_paths = {p.resolve() for p in doc_paths}
    extra_docs: list[str] = []
    for pat in glob_patterns:
        for p in sorted(root.glob(pat)):
            if p.is_file() and p.resolve() not in seen_paths:
                seen_paths.add(p.resolve())
                doc_paths.append(p)
                extra_docs.append(p.relative_to(root).as_posix())

    requirements: list[str] = []
    seen_reqs: set[str] = set()
    req_lines: dict[str, str] = {}
    doc_endpoints: list[dict[str, str]] = []
    seen_doc_eps: set[tuple[str, str]] = set()
    doc_hashes: dict[str, dict[str, str]] = {}

    for p in doc_paths:
        text = _read_text(p)
        rel = p.relative_to(root).as_posix()
        req_sigs: list[str] = []
        ep_sigs: list[str] = []

        for line in text.splitlines():
            m_req = REQ_ID_RE.search(line)
            if m_req:
                rid = m_req.group(1)
                norm_line = re.sub(r"\s+", " ", line.strip())
                req_sigs.append(f"{rid}:{norm_line}")
                req_lines[rid] = norm_line
                if rid not in seen_reqs:
                    seen_reqs.add(rid)
                    requirements.append(rid)

        for m in API_DOC_EP_RE.finditer(text):
            key = (m.group(1).upper(), m.group(2))
            ep_sigs.append(f"{key[0]} {key[1]}")
            if key not in seen_doc_eps:
                seen_doc_eps.add(key)
                doc_endpoints.append({"method": key[0], "path": key[1], "source": rel})

        if p.name not in {"HANDOFF.md", "README.md"}:
            doc_hashes[rel] = {
                "raw_hash": sha256_file(p),
                "contract_hash": sha256_text(
                    json.dumps({"reqs": sorted(req_sigs), "eps": sorted(ep_sigs)}, sort_keys=True)
                ),
            }

    existing_features: list[dict[str, Any]] = []
    specs_dir = root / "specs"
    if specs_dir.is_dir():
        for fp in sorted(specs_dir.glob("*.feature")):
            ftxt = _read_text(fp)
            scenarios = re.findall(r"^\s*Scenario(?: Outline)?\s*:\s*(.+)$", ftxt, re.MULTILINE)
            tags = sorted(set(re.findall(r"@[A-Za-z0-9_-]+", ftxt)))
            existing_features.append(
                {
                    "file": fp.relative_to(root).as_posix(),
                    "scenarios": [s.strip() for s in scenarios],
                    "tags": tags,
                }
            )

    return {
        "docs": docs_presence,
        "extra_docs": extra_docs,
        "requirements": requirements,
        "req_lines": req_lines,
        "doc_endpoints": doc_endpoints,
        "doc_hashes": doc_hashes,
        "existing_features": existing_features,
    }


def _module_key(path_str: str) -> str:
    cleaned = path_str.strip("/")
    if not cleaned:
        return "root"
    parts = [p for p in cleaned.split("/") if p and not p.startswith(":") and not p.startswith("{")]
    for part in parts:
        if part.lower() in {"api", "v1", "v2", "v3", "main", "app"}:
            continue
        return part.lower()
    return parts[0].lower() if parts else "root"


def _risk_tier(kind: str, method: str, path: str, roles: list[str] | None = None) -> str:
    low_p = path.lower()
    if any(k in low_p for k in ("auth", "login", "register", "password", "token", "pay", "checkout", "billing")):
        return "P0"
    if roles or method.upper() == "DELETE":
        return "P0"
    if method.upper() in {"POST", "PUT", "PATCH"}:
        return "P1"
    if kind == "route" and any(k in low_p for k in ("admin", "settings", "users", "projects")):
        return "P1"
    if any(k in low_p for k in ("health", "actuator", "swagger")):
        return "P3"
    return "P2"


def _extract_validation_signals(file_path: Path) -> list[str]:
    if not file_path.is_file():
        return []
    text = _read_text(file_path)
    return sorted(set(m.group(0).strip() for m in VALIDATION_SIGNAL_RE.finditer(text)))


def _compute_surface_hashes(
    root: Path,
    file_rel: str,
    contract_payload: dict[str, Any],
) -> tuple[str, str]:
    raw_h = ""
    if file_rel:
        cand = root / file_rel
        if cand.is_file():
            raw_h = sha256_file(cand)
            signals = _extract_validation_signals(cand)
            if signals:
                contract_payload = {**contract_payload, "validation_signals": signals}
    contract_h = sha256_text(json.dumps(contract_payload, sort_keys=True, ensure_ascii=False))
    return raw_h, contract_h


def build_test_inventory(
    project_root: Path | str,
    *,
    peers: list[Path | str] | None = None,
    focus: list[str] | None = None,
) -> dict[str, Any]:
    """Kod tabanı (fa_scan) ve dokümanlardan birleşik deterministik test envanteri üretir."""
    root = Path(project_root).resolve()
    snapshot, kg = fa_scan.run_scan_with_graph(root, peers=peers, focus=focus)
    v1 = snapshot.get("v1_projection", {})

    # 1. Rotalar (v1 declared + KG Route/Screen düğümleri)
    routes_set: set[str] = set()
    route_details: list[dict[str, Any]] = []
    for item in v1.get("routes", {}).get("declared", []):
        rpath = item.get("path") if isinstance(item, dict) else str(item)
        rfile = item.get("file", "") if isinstance(item, dict) else ""
        if rpath and rpath not in routes_set:
            routes_set.add(rpath)
            mod = _module_key(rpath)
            raw_h, contract_h = _compute_surface_hashes(
                root,
                rfile,
                {"kind": "route", "path": rpath, "module": mod},
            )
            route_details.append(
                {
                    "path": rpath,
                    "file": rfile,
                    "module": mod,
                    "risk_tier": _risk_tier("route", "GET", rpath),
                    "raw_hash": raw_h,
                    "contract_hash": contract_h,
                }
            )

    for node in kg.nodes.values():
        if node.kind == "Route":
            rpath = node.attrs.get("path") or node.name
            if rpath and rpath not in routes_set:
                routes_set.add(rpath)
                mod = _module_key(rpath)
                raw_h, contract_h = _compute_surface_hashes(
                    root,
                    node.file or "",
                    {"kind": "route", "path": rpath, "module": mod, "attrs": node.attrs},
                )
                route_details.append(
                    {
                        "path": rpath,
                        "file": node.file or "",
                        "module": mod,
                        "risk_tier": _risk_tier("route", "GET", rpath),
                        "raw_hash": raw_h,
                        "contract_hash": contract_h,
                    }
                )

    # 2. Backend Endpoint'leri (KG Endpoint düğümleri)
    endpoints: list[dict[str, Any]] = []
    seen_eps: set[tuple[str, str]] = set()
    for node in sorted(kg.nodes.values(), key=lambda n: n.id):
        if node.kind == "Endpoint":
            method = str(node.attrs.get("method", "GET")).upper()
            path = str(node.attrs.get("path", ""))
            if path and (method, path) not in seen_eps:
                seen_eps.add((method, path))
                roles_list = sorted(str(r) for r in (node.attrs.get("allowed_roles") or []) if r)
                mod = _module_key(path)
                raw_h, contract_h = _compute_surface_hashes(
                    root,
                    node.file or "",
                    {
                        "kind": "endpoint",
                        "method": method,
                        "path": path,
                        "allowed_roles": roles_list,
                    },
                )
                endpoints.append(
                    {
                        "method": method,
                        "path": path,
                        "file": node.file or "",
                        "module": mod,
                        "allowed_roles": roles_list,
                        "risk_tier": _risk_tier("endpoint", method, path, roles_list),
                        "raw_hash": raw_h,
                        "contract_hash": contract_h,
                    }
                )

    # 3. Veri Modelleri / Tablolar / DTO'lar
    data_models: list[dict[str, str]] = []
    for node in sorted(kg.nodes.values(), key=lambda n: n.id):
        if node.kind in {"Table", "Entity", "Dto", "Model"}:
            data_models.append({"kind": node.kind, "name": node.name, "file": node.file or ""})

    # 4. Roller
    roles = sorted({str(r) for r in v1.get("roles", []) if r})
    for ep in endpoints:
        for r in ep.get("allowed_roles", []):
            if r:
                roles.append(str(r))
    roles = sorted(set(roles))

    # 5. Doküman & mevcut feature envanteri
    doc_info = _collect_doc_files(root)
    peer_paths = v1.get("roots", {}).get("peers", [])

    # 6. Modül bazlı gruplama + dosya bazlı çift-katmanlı hash'ler + KG etki haritası
    modules: dict[str, dict[str, Any]] = {}
    file_contracts: dict[str, dict[str, Any]] = {}

    for rd in route_details:
        mk = rd["module"]
        mod = modules.setdefault(mk, {"routes": [], "endpoints": [], "files": []})
        mod["routes"].append(rd["path"])
        if rd["file"]:
            if rd["file"] not in mod["files"]:
                mod["files"].append(rd["file"])
            fc = file_contracts.setdefault(rd["file"], {"routes": [], "endpoints": [], "models": []})
            fc["routes"].append(rd["path"])

    for ep in endpoints:
        mk = ep["module"]
        mod = modules.setdefault(mk, {"routes": [], "endpoints": [], "files": []})
        mod["endpoints"].append(f"{ep['method']} {ep['path']}")
        if ep["file"]:
            if ep["file"] not in mod["files"]:
                mod["files"].append(ep["file"])
            fc = file_contracts.setdefault(ep["file"], {"routes": [], "endpoints": [], "models": []})
            fc["endpoints"].append(
                {
                    "method": ep["method"],
                    "path": ep["path"],
                    "allowed_roles": ep["allowed_roles"],
                }
            )

    for dm in data_models:
        if dm["file"]:
            fc = file_contracts.setdefault(dm["file"], {"routes": [], "endpoints": [], "models": []})
            fc["models"].append(f"{dm['kind']}:{dm['name']}")

    file_hashes: dict[str, dict[str, str]] = {}
    for rel_file, payload in sorted(file_contracts.items()):
        cand = root / rel_file
        if not cand.is_file():
            continue
        raw_h = sha256_file(cand)
        signals = _extract_validation_signals(cand)
        contract_h = sha256_text(
            json.dumps({**payload, "validation_signals": signals}, sort_keys=True, ensure_ascii=False)
        )
        file_hashes[rel_file] = {"raw_hash": raw_h, "contract_hash": contract_h}

    # Tüm kaynak kod dosyalarını da fast-path raw_hash + doğrulama imzası takibine al
    code_suffixes = {".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte", ".java", ".kt", ".py", ".go", ".sql", ".prisma"}
    for fpath in iter_repo_files(root, code_suffixes):
        rel = fpath.relative_to(root).as_posix()
        if rel not in file_hashes:
            raw_h = sha256_file(fpath)
            signals = _extract_validation_signals(fpath)
            file_hashes[rel] = {
                "raw_hash": raw_h,
                "contract_hash": sha256_text(json.dumps({"file": rel, "validation_signals": signals}, sort_keys=True)),
            }

    for doc_rel, dh in doc_info["doc_hashes"].items():
        file_hashes[doc_rel] = dh

    # KG dolaylı etki haritası (file -> impacted surface keys)
    kg_impact_map: dict[str, list[str]] = {}
    for node in sorted(kg.nodes.values(), key=lambda n: n.id):
        if not node.file:
            continue
        imp = kg.impact(node.id, max_depth=3)
        impacted_surfaces: set[str] = set()
        for aid in imp.get("affected_nodes", []) + [node.id]:
            anode = kg.nodes.get(aid)
            if not anode:
                continue
            if anode.kind == "Endpoint":
                m = str(anode.attrs.get("method", "GET")).upper()
                p = str(anode.attrs.get("path", ""))
                if p:
                    impacted_surfaces.add(f"endpoint:{m}:{p}")
            elif anode.kind == "Route":
                p = anode.attrs.get("path") or anode.name
                if p:
                    impacted_surfaces.add(f"route:{p}")
        if impacted_surfaces:
            existing = set(kg_impact_map.get(node.file, []))
            kg_impact_map[node.file] = sorted(existing | impacted_surfaces)

    return {
        "project_name": _extract_project_slug(root),
        "primary_language": _extract_primary_language(root),
        "root": root.as_posix(),
        "peers": peer_paths,
        "stack": v1.get("stack", {}),
        "routes": sorted(routes_set),
        "route_details": sorted(route_details, key=lambda x: x["path"]),
        "endpoints": endpoints,
        "roles": roles,
        "data_models": data_models,
        "modules": dict(sorted(modules.items())),
        "file_hashes": file_hashes,
        "kg_impact_map": kg_impact_map,
        "gaps": {
            "stub_pages": v1.get("stub_pages", []),
            "stub_actions": v1.get("stub_actions", []),
            "broken_routes": v1.get("broken_routes", []),
            "orphan_endpoints": v1.get("orphan_endpoints", []),
            "orphan_fields": v1.get("orphan_fields", []),
        },
        "docs": doc_info["docs"],
        "extra_docs": doc_info["extra_docs"],
        "requirements": doc_info["requirements"],
        "req_lines": doc_info["req_lines"],
        "doc_endpoints": doc_info["doc_endpoints"],
        "existing_features": doc_info["existing_features"],
    }


def _filter_gherkin_block(blk: str, only_scenario_ids: set[str]) -> str:
    """Bir ```gherkin bloğundaki yalnızca hedef Scenario ID'lerini korur."""
    lines = blk.splitlines()
    header_lines: list[str] = []
    scenarios: list[list[str]] = []
    current_sc: list[str] | None = None
    pending_tags: list[str] = []

    for line in lines:
        stripped = line.strip()
        if re.match(r"^Scenario(?: Outline)?\s*:", stripped, re.IGNORECASE):
            if current_sc is not None:
                scenarios.append(current_sc)
            current_sc = pending_tags + [line]
            pending_tags = []
        elif stripped.startswith("@"):
            if current_sc is not None and re.match(r"^Scenario", current_sc[-1].strip(), re.IGNORECASE):
                pending_tags.append(line)
            elif current_sc is None:
                # Feature-level tags vs first scenario tags
                if any(re.match(r"^Feature\s*:", h.strip(), re.IGNORECASE) for h in header_lines):
                    pending_tags.append(line)
                else:
                    header_lines.append(line)
            else:
                # Tag before next scenario while inside previous scenario
                scenarios.append(current_sc)
                current_sc = None
                pending_tags = [line]
        else:
            if current_sc is None:
                if pending_tags:
                    header_lines.extend(pending_tags)
                    pending_tags = []
                header_lines.append(line)
            else:
                current_sc.append(line)

    if current_sc is not None:
        scenarios.append(current_sc)

    kept_scenarios: list[str] = []
    for sc_lines in scenarios:
        sc_text = "\n".join(sc_lines)
        ids = set(SCENARIO_ID_RE.findall(sc_text))
        if ids & only_scenario_ids:
            kept_scenarios.append(sc_text.rstrip())

    if not kept_scenarios:
        return ""
    header_txt = "\n".join(header_lines).rstrip()
    return (header_txt + "\n\n" + "\n\n".join(kept_scenarios)).strip()


def export_feature_file(
    spec_path: Path | str,
    out_path: Path | str | None = None,
    *,
    only_scenario_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Tek ACCEPTANCE_TEST_SPEC.md dosyasındaki ```gherkin bloklarını tek .feature dosyasına ayıklar."""
    spec_p = Path(spec_path).resolve()
    if not spec_p.is_file():
        raise FileNotFoundError(f"Spesifikasyon dosyası bulunamadı: {spec_p}")

    text = _read_text(spec_p)
    blocks = [m.group(1).strip() for m in GHERKIN_FENCE_RE.finditer(text) if m.group(1).strip()]
    if not blocks:
        raise ValueError(f"Dosyada hiç ```gherkin kod bloğu bulunamadı: {spec_p}")

    lang = "tr"
    cleaned_blocks: list[str] = []
    for blk in blocks:
        lm = LANGUAGE_HEADER_RE.search(blk)
        if lm:
            lang = lm.group(1).strip()
            blk = LANGUAGE_HEADER_RE.sub("", blk).strip()
        if only_scenario_ids is not None:
            blk = _filter_gherkin_block(blk, only_scenario_ids)
        if blk:
            cleaned_blocks.append(blk)

    header = f"# language: {lang}\n# Auto-exported from {spec_p.name}\n\n"
    combined = header + ("\n\n".join(cleaned_blocks) + "\n" if cleaned_blocks else "")

    feature_count = len(FEATURE_LINE_RE.findall(combined))
    scenario_count = len(SCENARIO_LINE_RE.findall(combined))

    resolved_out: str | None = None
    if out_path is not None:
        out_p = Path(out_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(combined, encoding="utf-8")
        resolved_out = out_p.as_posix()

    return {
        "feature_count": feature_count,
        "scenario_count": scenario_count,
        "out_path": resolved_out,
        "content": combined,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Projeden birleşik test envanteri çıkarır ve ACCEPTANCE_TEST_SPEC.md -> .feature ayıklar."
    )
    parser.add_argument("--root", default=".", help="Proje kök dizini")
    parser.add_argument("--peer", action="append", default=[], help="Opsiyonel kardeş repo yolu")
    parser.add_argument("--focus", default="", help="Virgülle ayrılmış odaklı modül listesi")
    parser.add_argument("--json", action="store_true", help="JSON çıktısı bas")
    parser.add_argument("--out", default="", help="Çıktı dosyası yolu")
    parser.add_argument("--export-feature", default="", help="Tek .md spesifikasyonundan saf .feature üret")
    args = parser.parse_args(argv)

    if args.export_feature:
        out_target = args.out or None
        res = export_feature_file(args.export_feature, out_target)
        if args.json:
            printable = {k: v for k, v in res.items() if k != "content"}
            print(json.dumps(printable, ensure_ascii=False, indent=2))
        else:
            print(
                f"[OK] Exported {res['feature_count']} Feature(s), {res['scenario_count']} Scenario(s)"
                + (f" -> {res['out_path']}" if res["out_path"] else "")
            )
        return 0

    focus_list = [f.strip() for f in args.focus.split(",") if f.strip()] if args.focus else None
    peers_list: list[Path | str] | None = list(args.peer) if args.peer else None
    inventory = build_test_inventory(args.root, peers=peers_list, focus=focus_list)
    payload = json.dumps(inventory, ensure_ascii=False, indent=2)

    if args.out:
        out_p = Path(args.out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(payload + "\n", encoding="utf-8")

    if args.json or not args.out:
        print(payload)
    else:
        print(
            f"[OK] Inventory written to {args.out}: "
            f"{len(inventory['routes'])} routes, {len(inventory['endpoints'])} endpoints, "
            f"{len(inventory['requirements'])} reqs"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
