#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect — Execution Engine Advisor (`engine_advisor.py`).

Measures target project scale across 5 deterministic dimensions (source files,
lines of code, declared routes, peer repositories, and detected gaps) to advise
whether the 6-Hat Product Council should run in Single-Agent Sequential Isolation
or Parallel Multi-Agent mode, and produces the user confirmation prompt when the
host environment supports sub-agents.

Exit codes:
  0 — Advice computed successfully
  2 — Invalid arguments or missing root directory
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCHEMA_VERSION = "feature-architect/engine-advice@1"

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "vendor",
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
    ".agent",
    ".agents",
    ".claude",
    ".windsurf",
    ".cursor",
    "yedekler",
    "scout",
    "raporlar",
    "temps",
}

SOURCE_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".vue",
    ".svelte",
    ".py",
    ".java",
    ".kt",
    ".go",
    ".rs",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".dart",
    ".sql",
}

GAP_SUMMARY_KEYS = (
    "stub_pages",
    "stub_actions",
    "broken_routes",
    "orphan_endpoints",
    "orphan_fields",
)


def _walk_source_stats(base: Path) -> tuple[int, int]:
    files_count = 0
    loc_count = 0
    if not base.is_dir():
        return 0, 0
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext not in SOURCE_EXTENSIONS:
                continue
            fpath = Path(dirpath) / fname
            files_count += 1
            try:
                with fpath.open("r", encoding="utf-8", errors="replace") as fh:
                    loc_count += sum(1 for _ in fh)
            except OSError:
                continue
    return files_count, loc_count


def collect_metrics(
    root: Path,
    peers: list[Path] | None = None,
    gap_data: dict[str, Any] | None = None,
) -> dict[str, int]:
    """Collect deterministic size metrics across `root`, optional `peers`, and `gap_data`."""
    resolved_root = root.resolve()
    peer_paths = [p.resolve() for p in (peers or [])]

    if gap_data is None:
        scripts_dir = Path(__file__).resolve().parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        import gap_scanner  # type: ignore

        gap_data = gap_scanner.scan(resolved_root, peer_paths, set())

    total_files, total_loc = _walk_source_stats(resolved_root)
    for peer in peer_paths:
        p_files, p_loc = _walk_source_stats(peer)
        total_files += p_files
        total_loc += p_loc

    declared_routes = len(gap_data.get("routes", {}).get("declared", []))
    gap_peers = gap_data.get("roots", {}).get("peers", [])
    peer_count = max(len(peer_paths), len(gap_peers))
    summary = gap_data.get("summary", {})
    total_gaps = sum(int(summary.get(k, 0)) for k in GAP_SUMMARY_KEYS)

    return {
        "source_files": total_files,
        "loc": total_loc,
        "routes": declared_routes,
        "peers": peer_count,
        "gaps": total_gaps,
    }


def _score_band(value: int, low_max: int, mid_max: int) -> int:
    if value <= low_max:
        return 0
    if value <= mid_max:
        return 1
    return 2


def _normalize_subagents_flag(subagents: str | bool) -> bool:
    if isinstance(subagents, bool):
        return subagents
    return str(subagents).strip().lower() in {"yes", "true", "1", "y"}


def advise(metrics: dict[str, int], subagents: str | bool) -> dict[str, Any]:
    """Compute size classification, recommended execution engine, and user prompt."""
    sf = int(metrics.get("source_files", 0))
    loc = int(metrics.get("loc", 0))
    routes = int(metrics.get("routes", 0))
    peers = int(metrics.get("peers", 0))
    gaps = int(metrics.get("gaps", 0))

    points = {
        "source_files": _score_band(sf, 149, 400),
        "loc": _score_band(loc, 14999, 50000),
        "routes": _score_band(routes, 19, 60),
        "peers": 0 if peers == 0 else (1 if peers == 1 else 2),
        "gaps": _score_band(gaps, 14, 40),
    }
    total = sum(points.values())

    if total >= 6:
        size_class = "large"
    elif total >= 3:
        size_class = "medium"
    else:
        size_class = "small"

    has_subagents = _normalize_subagents_flag(subagents)

    if not has_subagents:
        recommendation = "single"
        ask_user = False
        rationale = (
            f"Ortam alt ajan çağrısını desteklemediği için 6 uzman şapka Tek Ajan (Sıralı İzolasyon) "
            f"motoruyla çalıştırılır ({sf} kaynak dosya, {loc} LOC, {routes} rota, {gaps} boşluk)."
        )
        question_prompt = ""
    else:
        ask_user = True
        if size_class == "large":
            recommendation = "multi"
            rationale = (
                f"{sf} kaynak dosya, {loc} LOC, {routes} rota, {peers} peer repo ve {gaps} tespit edilen boşluk "
                f"(ölçek puanı {total}/10 -> large): 6 şapkanın tek bağlamda sıralı çalışması bağlam taşmasına "
                f"ve körlük kaybına yol açacağından paralel Alt Ajanlı motor önerilir."
            )
            opt1 = "1. **Alt Ajanlı — Paralel 6 Uzman (Önerilen):** Tam kör izolasyon, geniş kod tabanında sıfır bağlam taşması (~6x token)."
            opt2 = "2. **Tek Ajan — Sıralı 6 Uzman:** Daha düşük token maliyeti, ancak tek bağlamda kör izolasyon zayıflatılmış olur."
        else:
            recommendation = "single"
            rationale = (
                f"{sf} kaynak dosya, {loc} LOC, {routes} rota, {peers} peer repo ve {gaps} tespit edilen boşluk "
                f"(ölçek puanı {total}/10 -> {size_class}): proje bağlam bütçesi tek ajan için uygundur; "
                f"token verimliliği için Tek Ajan motoru önerilir (tam körlük isterseniz Alt Ajanlı seçebilirsiniz)."
            )
            opt1 = "1. **Tek Ajan — Sıralı 6 Uzman (Önerilen):** Düşük token maliyeti, hızlı yürütme (kör izolasyon zayıflatılmış)."
            opt2 = "2. **Alt Ajanlı — Paralel 6 Uzman:** Tam kör izolasyon ve bağımsız alt ajan denetimi (~6x token)."

        question_prompt = (
            f"🧭 **Motor Seçimi (`/feature-architect`)** — Proje Ölçeği: **{size_class}** "
            f"(`{sf}` dosya · `{loc}` LOC · `{routes}` rota · `{peers}` peer · `{gaps}` boşluk)\n"
            f"- **Analiz Gerekçesi:** {rationale}\n"
            f"{opt1}\n"
            f"{opt2}\n"
            f"Hangi motorla ilerleyelim? (`single` / `multi`)"
        )

    return {
        "schema": SCHEMA_VERSION,
        "metrics": {
            "source_files": sf,
            "loc": loc,
            "routes": routes,
            "peers": peers,
            "gaps": gaps,
        },
        "points": points,
        "total": total,
        "size_class": size_class,
        "subagents": "yes" if has_subagents else "no",
        "recommendation": recommendation,
        "ask_user": ask_user,
        "rationale": rationale,
        "question_prompt": question_prompt,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feature Architect — Single vs Multi-Agent Engine Advisor")
    parser.add_argument("--root", default=".", help="Target project root directory")
    parser.add_argument("--peer", action="append", default=[], help="Optional peer repo directory")
    parser.add_argument("--gap-json", help="Optional pre-computed gap_scanner JSON output path")
    parser.add_argument("--subagents", choices=["yes", "no"], default="yes", help="Whether host supports sub-agents")
    parser.add_argument("--format", choices=["json", "md"], default="json", help="Output format")
    args = parser.parse_args(argv)

    root_path = Path(args.root)
    if not root_path.is_dir():
        print(f"[ERROR] Root directory does not exist: {root_path}", file=sys.stderr)
        return 2

    gap_data = None
    if args.gap_json:
        gap_path = Path(args.gap_json)
        if not gap_path.is_file():
            print(f"[ERROR] Gap JSON file does not exist: {gap_path}", file=sys.stderr)
            return 2
        gap_data = json.loads(gap_path.read_text(encoding="utf-8"))

    peers = [Path(p) for p in args.peer]
    metrics = collect_metrics(root_path, peers=peers, gap_data=gap_data)
    result = advise(metrics, subagents=args.subagents)

    if args.format == "md":
        if result["ask_user"]:
            print(result["question_prompt"])
        else:
            print(f"🧭 **Motor Kararı (`single`):** {result['rationale']}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
