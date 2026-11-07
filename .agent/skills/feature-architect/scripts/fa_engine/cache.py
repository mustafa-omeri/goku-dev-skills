#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feature Architect v2 — Incremental SHA-256 Content-Hash Cache (`cache.py`).

Computes per-file SHA-256 digests and identifies changed vs unchanged files across runs
so large repositories can skip re-parsing unmodified files during incremental scans.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_incremental_diff(
    project_root: Path,
    files: list[Path],
    *,
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    """Compare current file SHA-256 digests against cached manifest and update the manifest."""
    resolved_cache_dir = cache_dir or (project_root / ".fa" / "cache")
    resolved_cache_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = resolved_cache_dir / "file-hashes.json"

    previous: dict[str, str] = {}
    if manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                previous = {str(k): str(v) for k, v in data.items()}
        except (OSError, ValueError):
            previous = {}

    current: dict[str, str] = {}
    changed: list[str] = []
    unchanged: list[str] = []

    for fp in sorted(files):
        if not fp.is_file():
            continue
        rel = fp.resolve().relative_to(project_root.resolve()).as_posix()
        digest = _sha256_file(fp)
        current[rel] = digest
        if previous.get(rel) == digest:
            unchanged.append(rel)
        else:
            changed.append(rel)

    manifest_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "changed_files": changed,
        "unchanged_files": unchanged,
        "total_tracked": len(current),
    }
