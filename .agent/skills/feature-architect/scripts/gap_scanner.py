#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect — Backward-Compatible v1 Gap Scanner Shim (`gap_scanner.py`).

Delegates all discovery and static extraction to the modular `fa_engine` v2 pipeline
(`fa_scan.run_scan`) and emits the exact `feature-architect/gap-scan@1` contract so
existing callers and all v1 unit tests continue working unchanged while gaining
verified automatic peer discovery when `--peer` is omitted.

Exit codes:
  0 — Scan completed (findings are reported in JSON / Markdown output)
  2 — Invalid arguments or root directory does not exist
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fa_scan import run_scan  # noqa: E402

SCHEMA_VERSION = "feature-architect/gap-scan@1"


def scan(
    root: Path | str,
    peers: list[Path | str] | None = None,
    focus: list[str] | None = None,
) -> dict[str, Any]:
    """Public v1 seam: runs `fa_engine` v2 and returns `v1_projection`."""
    snapshot_v2 = run_scan(root, peers=peers, focus=focus)
    return snapshot_v2["v1_projection"]


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
            lines.append(
                f"- `{item['file']}:{item['line']}` ({item['source']}: `{item['i18n_key'] or 'literal'}`) — {item['evidence']}"
            )
    else:
        lines.append("- None detected.")

    lines.append("\n## 2. Stub Actions (Dead Controls / Toasts)")
    if report["stub_actions"]:
        for item in report["stub_actions"]:
            lines.append(
                f"- `{item['file']}:{item['line']}` (`{item['i18n_key'] or 'literal'}`) — {item['evidence']}"
            )
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
    report = scan(root_path, peers=args.peer or None, focus=focus_list)

    for c in report.get("roots", {}).get("peer_candidates", []):
        if c.get("confirmed"):
            print(
                f"🔗 [FA-ENGINE] Sibling Peer Bound: {c['name']} ({c['path']}) — confidence={c['confidence']} [{'; '.join(c.get('signals', []))}]",
                file=sys.stderr,
            )

    if args.json or args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
