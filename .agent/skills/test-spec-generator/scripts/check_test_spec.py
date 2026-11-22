#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tek Dosya Acceptance Criteria & Gherkin Test Spesifikasyonu Doğrulama Kapısı (check_test_spec.py v2).

Üretilen `docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md` dosyasının yapısal bütünlüğünü,
Gherkin sözdizimini, placeholder temizliğini, RBAC güvenlik kapsamasını, envanterdeki
tüm aktif rota / API uç noktalarını kapsayıp kapsamadığını ve v2 state defteriyle
(`test-spec-state.json`) senkronunu deterministik olarak denetler.
"""
from __future__ import annotations

import argparse
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

REQUIRED_SECTION_PATTERNS = (
    ("Bölüm 0 (Test Ortamı & Auth)", re.compile(r"^##\s+0\b", re.MULTILINE)),
    ("Bölüm 1 (İzlenebilirlik Matrisi)", re.compile(r"^##\s+1\b", re.MULTILINE)),
    ("Bölüm 2 (Modül Bazlı AC & Gherkin)", re.compile(r"^##\s+2\b", re.MULTILINE)),
    ("Bölüm 3 (Çapraz Sistem / E2E)", re.compile(r"^##\s+3\b", re.MULTILINE)),
    ("Bölüm 4 (Kapsam Dışı & Çelişkiler)", re.compile(r"^##\s+4\b", re.MULTILINE)),
    ("Bölüm 5 (Otomasyon Çalıştırma)", re.compile(r"^##\s+5\b", re.MULTILINE)),
)

PLACEHOLDER_PATTERNS = (
    re.compile(r"<doldur[^>]*>", re.IGNORECASE),
    re.compile(r"\b(?:TODO|TBD|FIXME)\b"),
    re.compile(r"\((?:yazılacak|yazilacak)\)", re.IGNORECASE),
)

GHERKIN_FENCE_RE = re.compile(r"```gherkin\s*\r?\n(.*?)```", re.DOTALL | re.IGNORECASE)
FEATURE_RE = re.compile(r"^\s*Feature\s*:\s*\S", re.IGNORECASE | re.MULTILINE)
SCENARIO_SPLIT_RE = re.compile(r"(?=^\s*Scenario(?: Outline)?\s*:)", re.IGNORECASE | re.MULTILINE)
SCENARIO_ID_RE = re.compile(r"\b(SC-[A-Z0-9]+-\d+)\b")
GIVEN_RE = re.compile(r"^\s*Given\s+\S", re.IGNORECASE | re.MULTILINE)
WHEN_RE = re.compile(r"^\s*When\s+\S", re.IGNORECASE | re.MULTILINE)
THEN_RE = re.compile(r"^\s*Then\s+\S", re.IGNORECASE | re.MULTILINE)
AC_ID_RE = re.compile(r"\bAC-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
RBAC_MARKER_RE = re.compile(r"@(?:rbac|security|authz)\b|\b403\b", re.IGNORECASE)
NEGATIVE_MARKER_RE = re.compile(r"@(?:negative|validation|edge-case)\b|Scenario Outline:", re.IGNORECASE)
PERF_MARKER_RE = re.compile(r"@(?:perf|sla|pagination|idempotency|concurrency)\b", re.IGNORECASE)

DEFAULT_IGNORE_PREFIXES = (
    "/actuator",
    "/health",
    "/swagger",
    "/v3/api-docs",
    "/favicon",
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def _is_ignored_surface(surface_path: str, extra_ignores: list[str] | None = None) -> bool:
    p = surface_path.strip()
    if not p or p == "*" or p == "/*":
        return True
    for pref in DEFAULT_IGNORE_PREFIXES:
        if p.startswith(pref):
            return True
    for ig in extra_ignores or []:
        if p == ig or p.startswith(ig):
            return True
    return False


def _add_issue(bucket: list[dict[str, str]], code: str, message: str) -> None:
    bucket.append({"code": code, "message": message})


def validate_test_spec(
    spec_path: Path | str,
    *,
    inventory: dict[str, Any] | None = None,
    state: dict[str, Any] | None = None,
    ignore_routes: list[str] | None = None,
) -> dict[str, Any]:
    """Tek dosya test spesifikasyonunu yapı, Gherkin, kapsama ve state uyumu açısından doğrular."""
    spec_p = Path(spec_path).resolve()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not spec_p.is_file():
        _add_issue(errors, "E1_MISSING_SPEC_FILE", f"Spesifikasyon dosyası bulunamadı: {spec_p}")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "metrics": {}}

    text = _read_text(spec_p)
    if not text.strip():
        _add_issue(errors, "E1_MISSING_SPEC_FILE", "Spesifikasyon dosyası boş.")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "metrics": {}}

    # E2: Zorunlu 6 bölüm
    missing_sections = [label for label, pat in REQUIRED_SECTION_PATTERNS if not pat.search(text)]
    if missing_sections:
        _add_issue(
            errors,
            "E2_MISSING_REQUIRED_SECTIONS",
            f"Eksik zorunlu bölümler: {', '.join(missing_sections)}",
        )

    # E3: Şablon / Placeholder sızıntısı
    leaks: list[str] = []
    for pat in PLACEHOLDER_PATTERNS:
        for m in pat.finditer(text):
            leaks.append(m.group(0))
    if leaks:
        _add_issue(
            errors,
            "E3_PLACEHOLDER_LEAK",
            f"Şablon yer tutucu / tamamlanmamış ifade bulundu: {', '.join(sorted(set(leaks))[:5])}",
        )

    # E4 & E10: Gherkin blokları, Given/When/Then geçerliliği ve mükerrer SC-ID kontrolü
    blocks = [m.group(1) for m in GHERKIN_FENCE_RE.finditer(text)]
    total_features = 0
    total_scenarios = 0
    broken_scenarios: list[str] = []
    seen_sc_ids: set[str] = set()
    dup_sc_ids: set[str] = set()

    for idx, blk in enumerate(blocks, start=1):
        if not FEATURE_RE.search(blk):
            broken_scenarios.append(f"Blok #{idx}: Feature: başlığı eksik")
            continue
        total_features += len(FEATURE_RE.findall(blk))
        parts = SCENARIO_SPLIT_RE.split(blk)
        has_background = bool(re.search(r"^\s*Background\s*:", blk, re.IGNORECASE | re.MULTILINE))
        blk_scenarios = [p for p in parts if re.match(r"^\s*Scenario(?: Outline)?\s*:", p, re.IGNORECASE)]
        if not blk_scenarios:
            broken_scenarios.append(f"Blok #{idx}: hiç Scenario tanımlı değil")
            continue
        for sc in blk_scenarios:
            total_scenarios += 1
            title = sc.splitlines()[0].strip()
            idm = SCENARIO_ID_RE.search(title)
            if idm:
                sid = idm.group(1)
                if sid in seen_sc_ids:
                    dup_sc_ids.add(sid)
                seen_sc_ids.add(sid)
            has_given = bool(GIVEN_RE.search(sc)) or has_background
            has_when = bool(WHEN_RE.search(sc))
            has_then = bool(THEN_RE.search(sc))
            if not (has_given and has_when and has_then):
                broken_scenarios.append(f"{title} (Given/When/Then eksik)")

    if not blocks or total_features == 0 or total_scenarios == 0 or broken_scenarios:
        detail = "; ".join(broken_scenarios[:5]) if broken_scenarios else "Hiç ```gherkin bloğu bulunamadı."
        _add_issue(errors, "E4_INVALID_GHERKIN", f"Geçersiz veya eksik Gherkin yapısı: {detail}")

    if dup_sc_ids:
        _add_issue(
            errors,
            "E10_DUPLICATE_SCENARIO_ID",
            f"Mükerrer senaryo kimlikleri tespit edildi: {', '.join(sorted(dup_sc_ids))}",
        )

    # E5: Acceptance Criteria ID varlığı
    ac_ids = sorted(set(AC_ID_RE.findall(text)))
    if not ac_ids:
        _add_issue(
            errors,
            "E5_MISSING_ACCEPTANCE_CRITERIA",
            "Ölçülebilir Kabul Kriteri kimliği (AC-MOD-01 vb.) bulunamadı.",
        )

    # E6, E7, W2: Envanter tabanlı kapsama, RBAC ve performans/idempotency doğrulaması
    uncovered_routes: list[str] = []
    uncovered_endpoints: list[str] = []
    blocks_text = "\n".join(blocks)
    if inventory is not None:
        for route in inventory.get("routes", []):
            r_str = str(route).strip()
            if _is_ignored_surface(r_str, ignore_routes):
                continue
            if r_str not in text:
                uncovered_routes.append(r_str)

        for ep in inventory.get("endpoints", []):
            method = str(ep.get("method", "GET")).upper()
            path = str(ep.get("path", "")).strip()
            if _is_ignored_surface(path, ignore_routes):
                continue
            sig = f"{method} {path}"
            ep_re = re.compile(rf"\b{re.escape(method)}\s+[^\s`\"']*{re.escape(path)}(?![A-Za-z0-9_/-])")
            if sig not in text and not ep_re.search(text):
                uncovered_endpoints.append(sig)

        if uncovered_routes or uncovered_endpoints:
            parts_msg: list[str] = []
            if uncovered_routes:
                parts_msg.append(f"Rotalar: {', '.join(uncovered_routes[:8])}")
            if uncovered_endpoints:
                parts_msg.append(f"Endpointler: {', '.join(uncovered_endpoints[:8])}")
            _add_issue(
                errors,
                "E6_UNCOVERED_SURFACE",
                "Envanterdeki aktif yüzeyler test spesifikasyonunda kapsanmamış -> " + " | ".join(parts_msg),
            )

        roles = [r for r in inventory.get("roles", []) if r]
        if roles and not RBAC_MARKER_RE.search(blocks_text):
            _add_issue(
                errors,
                "E7_MISSING_RBAC_SCENARIOS",
                f"Projede roller ({', '.join(roles)}) tespit edildi ancak Gherkin bloklarında @rbac/@security/403 senaryosu yok.",
            )

        has_mutations_or_lists = any(
            str(ep.get("method", "GET")).upper() in {"POST", "PUT", "PATCH", "GET"}
            for ep in inventory.get("endpoints", [])
        )
        if has_mutations_or_lists and not PERF_MARKER_RE.search(blocks_text):
            _add_issue(
                warnings,
                "W2_MISSING_PERF_OR_IDEMPOTENCY",
                "Endpoint envanterinde liste/mutasyon uçları var ancak @perf/@sla/@pagination/@idempotency/@concurrency senaryosu görülmedi.",
            )

    # E8 & E9: State defteri uyumu ve bayat PASS iddiası kontrolü
    if state is not None:
        state_scenarios = state.get("scenarios", {})
        active_state_ids = {
            sid for sid, sc in state_scenarios.items() if sc.get("status") != "DEPRECATED"
        }
        missing_in_spec = sorted(active_state_ids - seen_sc_ids)
        missing_in_state = sorted(seen_sc_ids - set(state_scenarios.keys()))
        if missing_in_spec or missing_in_state:
            _add_issue(
                errors,
                "E8_STATE_DRIFT",
                f"Spec ve test-spec-state.json uyuşmuyor (spec eksikleri: {missing_in_spec[:5]}, state eksikleri: {missing_in_state[:5]}).",
            )

        stale_pass_claims: list[str] = []
        for sid, sc in state_scenarios.items():
            if sc.get("status") == "PASS":
                pref = sc.get("pass_ref") or {}
                if pref.get("verified_contract_hash") != sc.get("contract_hash"):
                    stale_pass_claims.append(sid)
        if stale_pass_claims:
            _add_issue(
                errors,
                "E9_STALE_PASS_CLAIM",
                f"Kontratı değiştiği halde hâlâ PASS işaretli bayat senaryolar: {', '.join(sorted(stale_pass_claims))}",
            )

    if not NEGATIVE_MARKER_RE.search(text):
        _add_issue(
            warnings,
            "W1_MISSING_NEGATIVE_OR_EDGE",
            "Negatif/validasyon (@negative/@validation) veya Scenario Outline senaryosu görülmedi.",
        )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "ac_count": len(ac_ids),
            "feature_count": total_features,
            "scenario_count": total_scenarios,
            "uncovered_routes": len(uncovered_routes),
            "uncovered_endpoints": len(uncovered_endpoints),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tek dosya ACCEPTANCE_TEST_SPEC.md kapsama, Gherkin ve state kapısı."
    )
    parser.add_argument("--spec", required=True, help="Doğrulanacak test spesifikasyonu (.md) yolu")
    parser.add_argument("--inventory", default="", help="test_spec_scanner.py tarafından üretilen JSON dosyası")
    parser.add_argument("--state", default="", help="test-spec-state.json defteri yolu")
    parser.add_argument("--root", default="", help="Envanter dosyası yoksa projeyi anında tara")
    parser.add_argument("--ignore-route", action="append", default=[], help="Hariç tutulacak rota/prefix")
    parser.add_argument("--json", action="store_true", help="JSON çıktısı ver")
    args = parser.parse_args(argv)

    inv: dict[str, Any] | None = None
    if args.inventory:
        inv_p = Path(args.inventory)
        if not inv_p.is_file():
            print(f"[FAIL] Envanter dosyası bulunamadı: {inv_p}", file=sys.stderr)
            return 2
        inv = json.loads(_read_text(inv_p))
    elif args.root:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import test_spec_scanner  # noqa: E402

        inv = test_spec_scanner.build_test_inventory(args.root)

    st: dict[str, Any] | None = None
    if args.state:
        st_p = Path(args.state)
        if not st_p.is_file():
            print(f"[FAIL] State dosyası bulunamadı: {st_p}", file=sys.stderr)
            return 2
        st = json.loads(_read_text(st_p))

    res = validate_test_spec(args.spec, inventory=inv, state=st, ignore_routes=args.ignore_route)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(
            f"[{res['status']}] AC: {res['metrics'].get('ac_count', 0)} · "
            f"Feature: {res['metrics'].get('feature_count', 0)} · "
            f"Scenario: {res['metrics'].get('scenario_count', 0)}"
        )
        for e in res["errors"]:
            print(f"  ERROR {e['code']}: {e['message']}")
        for w in res["warnings"]:
            print(f"  WARN  {w['code']}: {w['message']}")

    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
