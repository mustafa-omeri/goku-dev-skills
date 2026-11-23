#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saf Python Diff Triaj, Kapsam Manifesti, Akıllı Demetleme ve Zemin Koruma Motoru.

Harici kaynaklardan cerrahi olarak uyarlanmıştır:
- `awesome-skills/code-review-skill` (`pr-analyzer.py`): boyut/karmaşıklık ve risk sinyalleri
- `alibaba/open-code-review` (`open-code-review-delegate`): kapsam muhasebesi (`coverage_rate`) & akıllı dosya demetleme
- `addyosmani/agent-skills` (`constraint-driven-development`): diff'te zemin düşürme (`@ts-ignore`, stub, skipped test) taraması

Kullanım:
    git diff main...HEAD | python .agent/skills/code-review/scripts/diff_triage.py --json
    python .agent/skills/code-review/scripts/diff_triage.py --ref main --stats
    python .agent/skills/code-review/scripts/diff_triage.py --diff-file patch.diff --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

EXT_LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript/React", ".jsx": "JavaScript/React",
    ".java": "Java", ".kt": "Kotlin", ".go": "Go", ".rs": "Rust",
    ".sql": "SQL", ".md": "Markdown", ".json": "JSON",
    ".yml": "YAML", ".yaml": "YAML", ".toml": "TOML",
    ".css": "CSS", ".scss": "SCSS", ".html": "HTML",
    ".sh": "Shell", ".ps1": "PowerShell",
}

TEST_PATTERNS = (
    r"(?:^|/)test_[^/]+\.py$",
    r"[^/]+_test\.[a-zA-Z0-9]+$",
    r"[^/]+\.(?:test|spec)\.(?:js|ts|tsx|jsx)$",
    r"(?:^|/)(?:tests?|__tests__|spec)/",
)

CONFIG_NAMES = {
    "package.json", "package-lock.json", "pnpm-lock.yaml", "tsconfig.json",
    "vite.config.ts", "vite.config.js", "pyproject.toml", "requirements.txt",
    "pom.xml", "build.gradle", "build.gradle.kts", "docker-compose.yml",
    "Dockerfile", ".gitignore",
}

FLOOR_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("TS_IGNORE", re.compile(r"@ts-ignore|@ts-expect-error")),
    ("ESLINT_DISABLE", re.compile(r"eslint-disable")),
    ("PYTHON_SUPPRESS", re.compile(r"#\s*(?:noqa|type:\s*ignore)\b")),
    ("JAVA_SUPPRESS", re.compile(r"@SuppressWarnings")),
    ("SKIPPED_TEST", re.compile(r"\b(?:it|test|describe)\.skip\s*\(|@pytest\.mark\.skip|@Disabled\b|unittest\.skip")),
    ("UNIMPLEMENTED_STUB", re.compile(r'throw\s+new\s+Error\(\s*["\']Not implemented["\']\s*\)|raise\s+NotImplementedError\b')),
)


def _detect_language(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return EXT_LANGUAGES.get(ext.lower(), "unknown")


def _is_test_file(filename: str) -> bool:
    norm = filename.replace("\\", "/")
    return any(re.search(pat, norm) for pat in TEST_PATTERNS)


def _is_config_file(filename: str) -> bool:
    norm = filename.replace("\\", "/")
    base = os.path.basename(norm)
    if base.startswith(".env") or base in CONFIG_NAMES:
        return True
    return bool(re.search(r"(?:^|/)\.github/workflows/|config\.", norm))


def _parse_diff(diff_text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Git diff metnini dosya istatistiklerine ve '+' satırı zemin ihlallerine ayrıştırır."""
    files: List[Dict[str, Any]] = []
    violations: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    hunk_line = 0

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            if current is not None:
                files.append(current)
            m = re.match(r"diff --git a/(.+?) b/\1$", raw_line)
            if not m:
                m = re.search(r" b/(.+)$", raw_line)
            path = m.group(1) if m else "unknown"
            current = {
                "path": path,
                "additions": 0,
                "deletions": 0,
                "language": _detect_language(path),
                "is_test": _is_test_file(path),
                "is_config": _is_config_file(path),
                "status": "modified",
            }
            hunk_line = 0
            continue

        if current is None:
            continue

        if raw_line.startswith("new file mode"):
            current["status"] = "added"
        elif raw_line.startswith("deleted file mode"):
            current["status"] = "deleted"
        elif raw_line.startswith("@@ "):
            hm = re.search(r"\+(\d+)", raw_line)
            hunk_line = int(hm.group(1)) if hm else 0
        elif raw_line.startswith("+") and not raw_line.startswith("+++"):
            current["additions"] += 1
            added_code = raw_line[1:]
            for code, pat in FLOOR_PATTERNS:
                if code != "SKIPPED_TEST" and current["is_test"]:
                    continue
                if pat.search(added_code):
                    violations.append({
                        "path": current["path"],
                        "line_hint": hunk_line,
                        "pattern": code,
                        "snippet": added_code.strip()[:120],
                    })
            if hunk_line:
                hunk_line += 1
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            current["deletions"] += 1
        elif not raw_line.startswith("\\") and hunk_line:
            hunk_line += 1

    if current is not None:
        files.append(current)

    return files, violations


def _build_smart_bundles(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """İlişkili dosyaları (i18n sözlük çiftleri, kaynak+test) tek inceleme demetinde toplar."""
    bundles: List[Dict[str, Any]] = []
    assigned: set[str] = set()

    # 1. i18n locale çiftleri (ör. locales/tr.json + locales/en.json)
    locale_groups: Dict[str, List[str]] = defaultdict(list)
    for f in files:
        p = f["path"].replace("\\", "/")
        if re.search(r"(?:^|/)(?:locales|i18n|translations)/[^/]+\.json$", p, re.IGNORECASE):
            locale_groups[str(Path(p).parent)].append(p)

    for parent, paths in sorted(locale_groups.items()):
        if len(paths) > 1:
            bundles.append({
                "bundle_id": f"i18n:{parent}",
                "reason": "i18n locale sibling parity",
                "files": sorted(paths),
            })
            assigned.update(paths)

    # 2. Kaynak dosya + ilgili test dosyası demetleri
    test_files = [f["path"].replace("\\", "/") for f in files if f["is_test"]]
    for f in files:
        p = f["path"].replace("\\", "/")
        if p in assigned or f["is_test"]:
            continue
        stem = re.sub(r"\.(?:test|spec)$", "", Path(p).stem)
        matched_tests = [
            t for t in test_files
            if t not in assigned and (Path(t).stem in (f"{stem}.test", f"{stem}.spec", f"test_{stem}", f"{stem}_test"))
        ]
        if matched_tests:
            group = [p] + sorted(matched_tests)
            bundles.append({
                "bundle_id": f"pair:{stem}",
                "reason": "source + test pair",
                "files": group,
            })
            assigned.update(group)

    # 3. Kalan dosyalar tekil birim
    for f in files:
        p = f["path"].replace("\\", "/")
        if p not in assigned:
            bundles.append({
                "bundle_id": f"unit:{p}",
                "reason": "standalone file",
                "files": [p],
            })

    return bundles


def _calculate_complexity_and_size(files: List[Dict[str, Any]]) -> Tuple[float, str, int]:
    if not files:
        return 0.0, "XS", 0

    total_changes = sum(f["additions"] + f["deletions"] for f in files)
    size_factor = min(total_changes / 1000, 1.0)
    file_factor = min(len(files) / 20, 1.0)
    test_lines = sum(f["additions"] + f["deletions"] for f in files if f["is_test"])
    non_test_ratio = 1.0 - (test_lines / max(total_changes, 1))
    languages = {f["language"] for f in files if f["language"] != "unknown"}
    lang_factor = min(len(languages) / 5, 1.0)

    score = round(size_factor * 0.4 + file_factor * 0.2 + non_test_ratio * 0.2 + lang_factor * 0.2, 2)

    if total_changes < 50:
        cat = "XS"
    elif total_changes < 200:
        cat = "S"
    elif total_changes < 400:
        cat = "M"
    elif total_changes < 800:
        cat = "L"
    else:
        cat = "XL"

    est_minutes = max(5, min(120, int((total_changes / 20) * (1 + score))))
    return score, cat, est_minutes


def _identify_risks(files: List[Dict[str, Any]]) -> List[str]:
    if not files:
        return []
    risks: List[str] = []
    total_changes = sum(f["additions"] + f["deletions"] for f in files)
    test_changes = sum(f["additions"] + f["deletions"] for f in files if f["is_test"])

    if total_changes > 400:
        risks.append("LARGE_PR: >400 satır değişiklik — incelemeyi dilimle")
    if test_changes == 0 and total_changes > 20:
        risks.append("NO_TEST_CHANGES: Test dosyası değişikliği yok")
    elif total_changes > 100 and (test_changes / max(total_changes, 1)) < 0.2:
        risks.append("LOW_TEST_RATIO: Test oranı <%20")

    sec_markers = (".env", "auth", "security", "password", "token", "secret", "permission", "rbac")
    for f in files:
        low = f["path"].lower()
        if any(m in low for m in sec_markers):
            risks.append(f"SECURITY_SENSITIVE_FILE: {f['path']}")
            break

    for f in files:
        if "migration" in f["path"].lower() or f["language"] == "SQL":
            risks.append(f"DATABASE_CHANGE: {f['path']}")
            break

    cfg_count = sum(1 for f in files if f["is_config"])
    if cfg_count:
        risks.append(f"CONFIG_CHANGE: {cfg_count} yapılandırma dosyası")

    return risks


def analyze_diff(diff_text: str) -> Dict[str, Any]:
    """Ham git diff metnini analiz edip deterministik triaj, demet, manifest ve zemin ihlali döndürür."""
    files, violations = _parse_diff(diff_text or "")
    total_add = sum(f["additions"] for f in files)
    total_del = sum(f["deletions"] for f in files)
    score, size_cat, est_min = _calculate_complexity_and_size(files)
    bundles = _build_smart_bundles(files)
    risks = _identify_risks(files)

    if violations:
        risks.append(f"FLOOR_WEAKENING: {len(violations)} adet susturma/skip/stub kalıbı tespit edildi")

    checklist = [{"path": f["path"], "status": f["status"], "reviewed": False, "reason": ""} for f in files]
    total_files = len(files)

    return {
        "total_files": total_files,
        "total_additions": total_add,
        "total_deletions": total_del,
        "total_changes": total_add + total_del,
        "size_category": size_cat,
        "complexity_score": score,
        "estimated_review_minutes": est_min,
        "files": files,
        "bundles": bundles,
        "coverage_manifest": {
            "total_files": total_files,
            "reviewed_files": 0,
            "skipped_files": 0,
            "coverage_rate": 1.0 if total_files == 0 else 0.0,
            "checklist": checklist,
        },
        "risk_flags": risks,
        "floor_violations": violations,
    }


def _read_git_diff(ref: Optional[str]) -> str:
    cmd = ["git", "--no-pager", "diff", "--no-ext-diff", "--no-textconv", "--no-color"]
    cmd.append(f"{ref}...HEAD" if ref else "HEAD")
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git diff başarısız (exit {proc.returncode})")
    return proc.stdout


def _format_human(report: Dict[str, Any], show_files: bool = False) -> str:
    lines = [
        "=" * 64,
        "CODE REVIEW DIFF TRIAGE & COVERAGE MANIFEST",
        "=" * 64,
        f"Boyut: {report['size_category']} | Dosya: {report['total_files']} | +{report['total_additions']}/-{report['total_deletions']} | Skor: {report['complexity_score']}/1.0 | Tahmin: ~{report['estimated_review_minutes']} dk",
        f"Demet (Bundle) Sayısı: {len(report['bundles'])}",
    ]
    if report["risk_flags"]:
        lines.append("\nRisk Sinyalleri:")
        for r in report["risk_flags"]:
            lines.append(f"  - {r}")
    if report["floor_violations"]:
        lines.append("\nZemin İhlalleri (Floor Weakening):")
        for v in report["floor_violations"]:
            lines.append(f"  - [{v['pattern']}] {v['path']}:{v['line_hint']} -> {v['snippet']}")
    if show_files and report["files"]:
        lines.append("\nDosya Manifesti:")
        for f in report["files"]:
            tag = "[TEST]" if f["is_test"] else "[CFG]" if f["is_config"] else "[SRC]"
            lines.append(f"  - {tag} {f['path']} (+{f['additions']}/-{f['deletions']}, {f['language']})")
    lines.append("=" * 64)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff Triage, Bundling & Floor Guard")
    parser.add_argument("--diff-file", "-f", help="Hazır diff dosyası yolu")
    parser.add_argument("--ref", help="Git merge-base referansı (ör. main, HEAD~1)")
    parser.add_argument("--json", action="store_true", help="JSON çıktısı ver")
    parser.add_argument("--stats", "-s", action="store_true", help="Dosya listesini de yazdır")
    args = parser.parse_args()

    try:
        if args.diff_file:
            diff_text = Path(args.diff_file).read_text(encoding="utf-8", errors="replace")
        elif args.ref:
            diff_text = _read_git_diff(args.ref)
        elif not sys.stdin.isatty():
            diff_text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        else:
            diff_text = _read_git_diff(None)
    except Exception as exc:
        print(f"[HATA] {exc}", file=sys.stderr)
        return 1

    report = analyze_diff(diff_text)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_human(report, show_files=args.stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
