#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect v2 Synthetic Golden Benchmark & Ad-hoc External Evaluator (`quality_bench.py`).

Measures:
  1. Structural Recall across 14 domain-neutral synthetic micro-repo scenarios
  2. Precision (penalizing unexpected structural facts & forbidden false positives)
  3. Clean Reference Repository False Positive Rate (`clean_repo_fpr <= 0.02`)
  4. Evidence Integrity (`V1` file:line resolution across primary + confirmed peers == 100%)
  5. Multi-run Determinism (`input_hash` and `facts` identical across N runs)
  6. Optional read-only `--external-root <path>` benchmark without persisting external traces
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BENCH_DIR = Path(__file__).resolve().parent
REPO_ROOT = BENCH_DIR.parents[1]
SCRIPTS_DIR = REPO_ROOT / ".agent" / "skills" / "feature-architect" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fa_scan import run_scan  # noqa: E402


def _verify_fact_evidence_on_disk(fact: dict[str, Any], search_roots: list[Path]) -> bool:
    ev_list = fact.get("evidence") or []
    if not ev_list:
        return False
    for ev in ev_list:
        ref = str(ev.get("ref", ""))
        if ":" not in ref:
            return False
        file_part, line_str = ref.rsplit(":", 1)
        try:
            line_no = int(line_str)
        except ValueError:
            return False
        if line_no < 1:
            return False
        matched_file = None
        for r in search_roots:
            cand = r / file_part
            if cand.is_file():
                matched_file = cand
                break
        if matched_file is None:
            return False
        total_lines = len(matched_file.read_text(encoding="utf-8", errors="replace").splitlines())
        if line_no > max(total_lines, 1):
            return False
    return True


def evaluate_synthetic_fixtures(determinism_runs: int = 3) -> dict[str, Any]:
    spec_path = BENCH_DIR / "fixtures" / "synthetic_scenarios.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    scenarios = spec.get("scenarios", [])

    tp_total = 0
    fn_total = 0
    fp_total = 0
    evidence_valid = 0
    evidence_total = 0
    clean_repo_fpr = 0.0
    all_deterministic = True
    scenario_reports: list[dict[str, Any]] = []

    for sc in scenarios:
        with tempfile.TemporaryDirectory() as ws_tmp:
            ws = Path(ws_tmp)
            for rel_path, content in sc["files"].items():
                p = ws / rel_path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")

            primary_root = ws / sc["primary_subdir"]
            runs: list[dict[str, Any]] = []
            for _ in range(max(1, determinism_runs)):
                runs.append(run_scan(primary_root))

            hashes = {r["input_hash"] for r in runs}
            serialized_facts = {json.dumps(r["facts"], sort_keys=True) for r in runs}
            det_ok = len(hashes) == 1 and len(serialized_facts) == 1
            if not det_ok:
                all_deterministic = False

            snap = runs[0]
            confirmed_peers = [Path(p) for p in snap["discovery_metadata"]["confirmed_peers"]]
            search_roots = [primary_root.resolve()] + confirmed_peers

            found_codes = {f["code"] for f in snap["facts"]}
            structural_codes = {f["code"] for f in snap["facts"] if f["fact_type"] == "structural"}

            expected = set(sc.get("expected_codes") or [])
            forbidden = set(sc.get("forbidden_codes") or [])

            tp = len(expected & found_codes)
            fn = len(expected - found_codes)
            # Unexpected structural codes (excluding explicitly expected codes) or forbidden codes count as FP
            unexpected_structural = structural_codes - expected
            forbidden_hits = found_codes & forbidden
            fp = len(unexpected_structural | forbidden_hits)

            # Peer discovery assertions if present
            peer_ok = True
            if sc.get("expect_confirmed_peer"):
                exp_peer = (ws / sc["expect_confirmed_peer"]).resolve().as_posix()
                if exp_peer not in snap["discovery_metadata"]["confirmed_peers"]:
                    peer_ok = False
                    fn += 1
                else:
                    tp += 1
            if sc.get("expect_rejected_peer"):
                rej_peer = (ws / sc["expect_rejected_peer"]).resolve().as_posix()
                if rej_peer in snap["discovery_metadata"]["confirmed_peers"]:
                    peer_ok = False
                    fp += 1

            # Location-specific guard checks (e.g. S12)
            if sc.get("expected_location_substr"):
                sub = sc["expected_location_substr"]
                if not any(sub in f["location"] for f in snap["facts"]):
                    fn += 1
            if sc.get("forbidden_location_substr"):
                fsub = sc["forbidden_location_substr"]
                if any(fsub in f["location"] for f in snap["facts"]):
                    fp += 1

            for f in snap["facts"]:
                evidence_total += 1
                if _verify_fact_evidence_on_disk(f, search_roots):
                    evidence_valid += 1

            if sc.get("clean_reference"):
                nodes_n = max(int(snap["graph_summary"]["nodes_count"]), 1)
                clean_repo_fpr = round(len(structural_codes) / nodes_n, 4)

            tp_total += tp
            fn_total += fn
            fp_total += fp

            scenario_reports.append(
                {
                    "id": sc["id"],
                    "passed": (fn == 0 and fp == 0 and peer_ok and det_ok),
                    "expected_codes": sorted(expected),
                    "found_codes": sorted(found_codes),
                    "tp": tp,
                    "fn": fn,
                    "fp": fp,
                    "deterministic": det_ok,
                }
            )

    recall = round(tp_total / max(tp_total + fn_total, 1), 4)
    precision = round(tp_total / max(tp_total + fp_total, 1), 4)
    ev_integrity = round(evidence_valid / evidence_total, 4) if evidence_total > 0 else 1.0

    return {
        "schema": "feature-architect/bench-report@2",
        "scenarios_count": len(scenarios),
        "metrics": {
            "structural_recall": recall,
            "precision": precision,
            "clean_repo_fpr": clean_repo_fpr,
            "evidence_integrity": ev_integrity,
            "determinism_pass": all_deterministic,
            "tp": tp_total,
            "fn": fn_total,
            "fp": fp_total,
        },
        "scenarios": scenario_reports,
    }


def evaluate_external_root(ext_root: Path, determinism_runs: int = 2) -> dict[str, Any]:
    runs = [run_scan(ext_root) for _ in range(max(1, determinism_runs))]
    hashes = {r["input_hash"] for r in runs}
    fact_Payloads = {json.dumps(r["facts"], sort_keys=True) for r in runs}
    snap = runs[0]
    peers = [Path(p) for p in snap["discovery_metadata"]["confirmed_peers"]]
    roots = [ext_root.resolve()] + peers
    valid_ev = sum(1 for f in snap["facts"] if _verify_fact_evidence_on_disk(f, roots))
    total_ev = len(snap["facts"])
    return {
        "schema": "feature-architect/external-bench@2",
        "topology": snap["project_metadata"]["topology"],
        "tenancy_model": snap["project_metadata"]["tenancy_model"],
        "confirmed_peers_count": len(peers),
        "scanned_files": snap["analysis_coverage"]["scanned_files"],
        "graph_summary": snap["graph_summary"],
        "readiness_radar": snap["readiness_radar"],
        "facts_count": total_ev,
        "facts_by_code": _count_by_code(snap["facts"]),
        "evidence_integrity": round(valid_ev / total_ev, 4) if total_ev else 1.0,
        "determinism_pass": len(hashes) == 1 and len(fact_Payloads) == 1,
    }


def _count_by_code(facts: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for f in facts:
        c = f["code"]
        counts[c] = counts.get(c, 0) + 1
    return dict(sorted(counts.items()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feature Architect v2 — Golden Benchmark Suite")
    parser.add_argument("--fixtures", action="store_true", help="Evaluate the 14 synthetic golden fixtures")
    parser.add_argument("--external-root", default="", help="Optional read-only external repo path to benchmark")
    parser.add_argument("--determinism-runs", type=int, default=3, help="Number of consecutive runs for hash check")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    if args.external_root:
        ext = Path(args.external_root)
        if not ext.is_dir():
            print(f"[ERROR] External root does not exist: {args.external_root}", file=sys.stderr)
            return 2
        report = evaluate_external_root(ext, determinism_runs=args.determinism_runs)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["determinism_pass"] and report["evidence_integrity"] == 1.0 else 1

    report = evaluate_synthetic_fixtures(determinism_runs=args.determinism_runs)
    m = report["metrics"]
    gates_ok = (
        m["structural_recall"] >= 0.90
        and m["precision"] >= 0.80
        and m["clean_repo_fpr"] <= 0.02
        and m["evidence_integrity"] == 1.0
        and m["determinism_pass"]
    )

    if args.json or not sys.stdout.isatty():
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"Feature Architect v2 Benchmark ({report['scenarios_count']} scenarios): "
            f"Recall={m['structural_recall']*100:.1f}% · Precision={m['precision']*100:.1f}% · "
            f"Clean FPR={m['clean_repo_fpr']*100:.2f}% · Evidence={m['evidence_integrity']*100:.0f}% · "
            f"Determinism={'PASS' if m['determinism_pass'] else 'FAIL'}"
        )
    return 0 if gates_ok else 1


if __name__ == "__main__":
    sys.exit(main())
