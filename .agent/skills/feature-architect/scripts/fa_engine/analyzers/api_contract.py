# -*- coding: utf-8 -*-
"""API Contract Intelligence Engine (`api_contract.py`).

Reconciles client HTTP calls & TypeScript expectations against:
  1. OpenAPI / Swagger specification files in the repository (L2, `derivation='openapi'`)
  2. Static controller + DTO declarations across JVM/Python/Node backends (L1, `derivation='syntax'`)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..model import (
    CoverageReport,
    EvidenceRef,
    Fact,
    ProjectProfile,
    extract_api_version_prefix,
    normalize_api_path,
)
from .base import AnalyzerContext, AnalyzerResult


def _canonical_scalar_family(raw_type: str) -> str:
    t = raw_type.strip().lower()
    if t.endswith("[]") or t.startswith(("list<", "set<", "array<", "readonlyarray<")):
        return "array"
    if any(k in t for k in ("bool", "boolean")):
        return "boolean"
    if any(k in t for k in ("int", "integer", "long", "double", "float", "bigdecimal", "number", "short")):
        return "number"
    if any(k in t for k in ("string", "uuid", "char", "localdate", "instant", "offsetdatetime", "datetime", "date")):
        return "string"
    return "object"


def _load_openapi_schemas(profile: ProjectProfile) -> dict[str, dict[str, Any]]:
    """Load OpenAPI schemas & paths if YAML/JSON files exist."""
    root_by_label = dict(profile.all_active_roots)
    specs: dict[str, dict[str, Any]] = {}
    for cs in profile.contract_sources:
        if cs.kind != "openapi_file":
            continue
        base = root_by_label.get(cs.root_label, profile.root)
        fpath = base / cs.path
        if not fpath.is_file():
            continue
        txt = fpath.read_text(encoding="utf-8", errors="replace")
        parsed = None
        if fpath.suffix.lower() == ".json":
            try:
                parsed = json.loads(txt)
            except Exception:
                parsed = None
        else:
            try:
                import yaml  # type: ignore

                parsed = yaml.safe_load(txt)
            except Exception:
                parsed = None
        if isinstance(parsed, dict):
            specs[cs.path] = parsed
    return specs


class ApiContractAnalyzer:
    name = "api_contract"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        if profile.frontend_stacks and (profile.backend_stacks or profile.contract_sources):
            return True, "Client + Server/Contract sources available for reconciliation"
        return False, "Requires both client HTTP calls and server endpoints or OpenAPI contract"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        applicable, reason = self.applies(ctx.profile)
        if not applicable:
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
            )

        fe_state = ctx.shared_state.get("frontend", {})
        be_state = ctx.shared_state.get("backend", {})
        http_calls: list[dict[str, Any]] = fe_state.get("http_calls", [])
        ts_interfaces: dict[str, dict[str, Any]] = fe_state.get("interfaces", {})
        endpoints: list[dict[str, Any]] = be_state.get("endpoints", [])
        be_dtos: dict[str, dict[str, Any]] = be_state.get("dtos", {})

        facts: list[Fact] = []
        limitations: list[str] = []

        openapi_specs = _load_openapi_schemas(ctx.profile)
        has_openapi_file = bool(openapi_specs)
        if not has_openapi_file:
            limitations.append("No static OpenAPI file in repository; contract comparison derived from static DTO/AST types.")

        # Index OpenAPI endpoints & component schemas if available
        oa_endpoints: dict[tuple[str, str], dict[str, Any]] = {}
        oa_schemas: dict[str, dict[str, Any]] = {}
        for spec_key, spec in openapi_specs.items():
            schemas = (spec.get("components") or {}).get("schemas") or spec.get("definitions") or {}
            if isinstance(schemas, dict):
                oa_schemas.update(schemas)
            paths_obj = spec.get("paths") or {}
            if isinstance(paths_obj, dict):
                for raw_p, methods_obj in paths_obj.items():
                    if not isinstance(methods_obj, dict):
                        continue
                    for verb, op in methods_obj.items():
                        if verb.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"} and isinstance(op, dict):
                            oa_endpoints[(verb.upper(), normalize_api_path(raw_p))] = {
                                "spec_ref": f"{spec_key}:1",
                                "raw_path": raw_p,
                                "op": op,
                            }

        # Index static backend endpoints
        be_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for ep in endpoints:
            be_by_key.setdefault((ep["method"], ep["normalized_path"]), []).append(ep)

        for call in http_calls:
            key = (call["method"], call["normalized_path"])
            matched_eps = be_by_key.get(key, [])
            oa_ep = oa_endpoints.get(key)

            # 1. Version prefix skew check (e.g. client /api/v2/orders vs backend /api/v1/orders)
            client_ver = extract_api_version_prefix(call["raw_path"])
            if client_ver and re_ver_is_numbered(client_ver) and matched_eps:
                server_vers = {
                    extract_api_version_prefix(ep["path"])
                    for ep in matched_eps
                    if extract_api_version_prefix(ep["path"]) and re_ver_is_numbered(extract_api_version_prefix(ep["path"]) or "")
                }
                if server_vers and client_ver not in server_vers:
                    # Also check normalized version number (v1 vs v2)
                    c_num = client_ver.split("/")[-1]
                    s_nums = {sv.split("/")[-1] for sv in server_vers if sv}
                    if c_num not in s_nums:
                        ep0 = matched_eps[0]
                        facts.append(
                            Fact.create(
                                fact_id=f"API-VER-{len(facts)+1:03d}",
                                code="API_VERSION_SKEW",
                                category="ARCHITECTURE",
                                fact_type="structural",
                                severity="HIGH",
                                summary=(
                                    f"Client calls `{call['raw_path']}` ({c_num}) at `{call['file']}:{call['line']}`, "
                                    f"but server only exposes version(s) `{', '.join(sorted(s_nums))}` (`{ep0['path']}`)."
                                ),
                                location=f"{call['file']}:{call['line']}",
                                evidence=[
                                    EvidenceRef(
                                        kind="code",
                                        level="L1",
                                        derivation="syntax",
                                        ref=f"{call['file']}:{call['line']}",
                                        line=call["line"],
                                        excerpt=call.get("excerpt", call["raw_path"]),
                                    )
                                ],
                            )
                        )

            # 2. Response DTO contract comparison
            ts_type_name = call.get("response_type")
            ts_iface = ts_interfaces.get(ts_type_name) if ts_type_name else None
            if not ts_iface:
                continue

            # Resolve authoritative server field map (OpenAPI schema first, then static DTO)
            server_fields: dict[str, str] | None = None
            contract_level = "L1"
            contract_deriv = "syntax"
            server_ref = ""

            if oa_ep:
                resp_200 = ((oa_ep["op"].get("responses") or {}).get("200") or (oa_ep["op"].get("responses") or {}).get("201") or {})
                content = (resp_200.get("content") or {}).get("application/json") or {}
                schema = content.get("schema") or {}
                ref_str = schema.get("$ref", "")
                schema_name = ref_str.split("/")[-1] if ref_str else ts_type_name
                oa_schema = oa_schemas.get(schema_name) if schema_name else None
                if isinstance(oa_schema, dict) and isinstance(oa_schema.get("properties"), dict):
                    server_fields = {
                        fname: str((fmeta or {}).get("type", "object"))
                        for fname, fmeta in oa_schema["properties"].items()
                    }
                    contract_level = "L2"
                    contract_deriv = "openapi"
                    server_ref = oa_ep["spec_ref"]

            if server_fields is None and matched_eps:
                ret_dto_name = matched_eps[0].get("return_dto") or ts_type_name
                be_dto = be_dtos.get(ret_dto_name)
                if be_dto:
                    server_fields = {f["name"]: f["type"] for f in be_dto["fields"]}
                    server_ref = f"{be_dto['file']}:1"

            if server_fields is not None:
                missing_fields: list[str] = []
                missing_optional_fields: list[str] = []
                type_mismatches: list[str] = []
                for tf in ts_iface["fields"]:
                    fname = tf["name"]
                    if fname not in server_fields:
                        if not tf["optional"]:
                            missing_fields.append(fname)
                        else:
                            missing_optional_fields.append(fname)
                    else:
                        fe_fam = _canonical_scalar_family(tf["type"])
                        be_fam = _canonical_scalar_family(server_fields[fname])
                        if fe_fam != "object" and be_fam != "object" and fe_fam != be_fam:
                            type_mismatches.append(f"{fname} (client={tf['type']} vs server={server_fields[fname]})")

                if missing_fields or type_mismatches:
                    details: list[str] = []
                    if missing_fields:
                        details.append(f"missing server field(s): {', '.join(missing_fields)}")
                    if type_mismatches:
                        details.append(f"incompatible field type(s): {', '.join(type_mismatches)}")
                    facts.append(
                        Fact.create(
                            fact_id=f"API-DTO-{len(facts)+1:03d}",
                            code="DTO_CONTRACT_MISMATCH",
                            category="ARCHITECTURE",
                            fact_type="structural",
                            severity="HIGH",
                            summary=(
                                f"Contract mismatch on `{call['method']} {call['raw_path']}` (`{ts_type_name}`): "
                                + "; ".join(details)
                                + "."
                            ),
                            location=f"{call['file']}:{call['line']}",
                            evidence=[
                                EvidenceRef(
                                    kind="contract" if contract_deriv == "openapi" else "code",
                                    level=contract_level,
                                    derivation=contract_deriv,
                                    ref=f"{ts_iface['file']}:{ts_iface['line']}",
                                    line=ts_iface["line"],
                                    excerpt=f"interface {ts_type_name}",
                                ),
                                EvidenceRef(
                                    kind="contract" if contract_deriv == "openapi" else "code",
                                    level=contract_level,
                                    derivation=contract_deriv,
                                    ref=server_ref or f"{call['file']}:{call['line']}",
                                    line=1,
                                    excerpt=ts_type_name,
                                ),
                            ],
                            attrs={
                                "endpoint": f"{call['method']} {call['raw_path']}",
                                "ts_type": ts_type_name,
                                "missing_fields": missing_fields,
                                "type_mismatches": type_mismatches,
                            },
                        )
                    )
                elif len(missing_optional_fields) >= 3 and (
                    len(missing_optional_fields) / max(1, len(ts_iface["fields"])) >= 0.4
                ):
                    facts.append(
                        Fact.create(
                            fact_id=f"API-DRIFT-{len(facts)+1:03d}",
                            code="DTO_SCHEMA_DRIFT",
                            category="ARCHITECTURE",
                            fact_type="structural",
                            severity="MEDIUM",
                            summary=(
                                f"DTO schema drift on `{call['method']} {call['raw_path']}` (`{ts_type_name}`): "
                                f"client interface declares {len(missing_optional_fields)} optional field(s) "
                                f"(`{', '.join(missing_optional_fields)}`) absent from backend `{ts_type_name}`."
                            ),
                            location=f"{ts_iface['file']}:{ts_iface['line']}",
                            evidence=[
                                EvidenceRef(
                                    kind="code",
                                    level="L1",
                                    derivation="syntax",
                                    ref=f"{ts_iface['file']}:{ts_iface['line']}",
                                    line=ts_iface["line"],
                                    excerpt=f"interface {ts_type_name}",
                                ),
                                EvidenceRef(
                                    kind="code",
                                    level="L1",
                                    derivation="syntax",
                                    ref=server_ref or f"{call['file']}:{call['line']}",
                                    line=1,
                                    excerpt=ts_type_name,
                                ),
                            ],
                            attrs={
                                "endpoint": f"{call['method']} {call['raw_path']}",
                                "ts_type": ts_type_name,
                                "missing_optional_fields": missing_optional_fields,
                            },
                        )
                    )

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            facts=facts,
            coverage=CoverageReport(scanned_files=len(http_calls) + len(openapi_specs)),
            limitations=limitations,
        )


def re_ver_is_numbered(prefix: str) -> bool:
    return prefix.endswith(("v1", "v2", "v3", "v4", "v5"))
