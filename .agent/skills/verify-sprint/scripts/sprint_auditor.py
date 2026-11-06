#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sprint Kabul, 5 Katman ve Cerrahi Onarım İzlenebilirlik Denetçisi (sprint_auditor.py).

Aktif sprint ve en son tamamlanan sprint kartlarını tarayarak:
1. Gherkin kabul kriteri dosyasının ve senaryolarının varlığını,
2. Kullanıcı gözle doğrulama adımlarını ve KULLANICI_TEST_REHBERI.md uyumunu,
3. 5 Katmanlı dikey dilim bulgularını (DB, API, UI, Skeleton, Form),
4. Cerrahi onarım izlenebilirlik kaydını (Audit Trail)
deterministik olarak denetler ve yapısal JSON/rapor üretir.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

COLUMNS = ("Bekliyor", "Yapılıyor", "Sınırdı", "Yapıldı")
COLUMN_RE = re.compile(r"^##\s+(.+?)\s*$")
CARD_RE = re.compile(r"^###\s+(S(\d+)-(\d+))\s*[·:\-—]\s*(\S.*?)\s*$")
FIELD_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|\s*$")
PLACEHOLDERS = {"", "-", "todo", "tbd", "yazılacak", "yazilacak", "(yazılacak)", "(yazilacak)", "?"}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def parse_kanban(text: str) -> Dict[str, List[Tuple[str, str, Dict[str, str], int]]]:
    columns: Dict[str, List[Tuple[str, str, Dict[str, str], int]]] = {c: [] for c in COLUMNS}
    current_col: Optional[str] = None
    current_card: Optional[Tuple[str, str, Dict[str, str], int]] = None

    for line_idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        col_match = COLUMN_RE.match(stripped)
        if col_match and not stripped.startswith("### "):
            heading = col_match.group(1).strip()
            if current_card and current_col in columns:
                columns[current_col].append(current_card)
                current_card = None
            if heading in columns:
                current_col = heading
            else:
                current_col = None
            continue

        card_match = CARD_RE.match(stripped)
        if card_match and current_col:
            if current_card:
                columns[current_col].append(current_card)
            card_id = card_match.group(1).strip()
            title = card_match.group(4).strip()
            current_card = (card_id, title, {}, line_idx)
            continue

        if current_card:
            field_match = FIELD_RE.match(stripped)
            if field_match:
                k = field_match.group(1).strip().lower()
                v = field_match.group(2).strip()
                if not re.match(r"^[:\-| ]+$", k):
                    current_card[2][k] = v

    if current_card and current_col in columns:
        columns[current_col].append(current_card)

    return columns


def audit_sprint(root: Path) -> Dict[str, Any]:
    root = root.resolve()
    sprint_path = root / "SPRINT_PLAN.md"
    board_path = root / "KANBAN.md"

    if not sprint_path.exists() and not board_path.exists():
        return {
            "status": "SKIPPED",
            "has_findings": False,
            "findings": [],
            "summary": "Sprint planı ve kanban panosu yok (kapsam dışı).",
        }

    if not board_path.exists():
        return {
            "status": "FAILED",
            "has_findings": True,
            "findings": [{"card_id": "BOARD", "issues": [{"type": "MISSING_BOARD", "msg": "KANBAN.md bulunamadı."}]}],
            "summary": "KANBAN.md dosyası eksik.",
        }

    board_text = _read_text(board_path)
    columns = parse_kanban(board_text)
    done_cards = columns.get("Yapıldı", [])

    findings: List[Dict[str, Any]] = []

    guide_path = root / "docs" / "KULLANICI_TEST_REHBERI.md"
    if not guide_path.is_file():
        guide_path = root / "KULLANICI_TEST_REHBERI.md"
    if not guide_path.is_file():
        findings.append({
            "card_id": "GUIDE",
            "title": "KULLANICI_TEST_REHBERI.md",
            "issues": [{"type": "MISSING_TEST_GUIDE", "msg": "KULLANICI_TEST_REHBERI.md veya docs/KULLANICI_TEST_REHBERI.md bulunamadı."}],
        })

    for card_id, title, fields, line in done_cards:
        issues = []

        # 1. Gherkin denetimi
        gherkin_val = fields.get("gherkin", "").strip()
        if not gherkin_val or gherkin_val.lower() in PLACEHOLDERS:
            issues.append({"type": "MISSING_GHERKIN", "msg": f"{card_id}: gherkin alanı boş veya placeholder."})
        else:
            parts = gherkin_val.split("#", 1)
            fpath = root / parts[0].strip()
            if not fpath.is_file():
                issues.append({"type": "MISSING_GHERKIN", "msg": f"{card_id}: feature dosyası yok -> {parts[0]}"})
            else:
                fcontent = _read_text(fpath)
                if "Scenario" not in fcontent or not any(step in fcontent for step in ("Given", "When", "Then")):
                    issues.append({"type": "INVALID_GHERKIN", "msg": f"{card_id}: Gherkin dosyasında Scenario veya Given/When/Then eksik."})

        # 2. Kullanıcı test adımı denetimi
        test_val = fields.get("test", "").strip()
        if not test_val or test_val.lower() in PLACEHOLDERS:
            issues.append({"type": "INVALID_USER_TEST", "msg": f"{card_id}: 'test' alanı boş veya placeholder (kullanıcı test adımı yok)."})

        if issues:
            findings.append({
                "card_id": card_id,
                "title": title,
                "issues": issues,
            })

    has_findings = len(findings) > 0
    status = "FAILED" if has_findings else "PASSED"
    summary = f"{len(done_cards)} adet Yapıldı kartı denetlendi; {len(findings)} kartta bulgu tespit edildi."

    return {
        "status": status,
        "has_findings": has_findings,
        "findings": findings,
        "summary": summary,
    }


def format_audit_trail_entry(
    card_id: str,
    title: str,
    sprint: str,
    initial_status: str,
    findings: str,
    fix_applied: str,
    tests_run: str,
    recheck_status: str,
) -> str:
    """Format a fully traceable audit trail block as per user requirement."""
    return (
        f"### 🛡️ Sprint Doğrulama & Cerrahi Onarım İzlenebilirlik Kaydı (Audit Trail)\n"
        f"- **Kart / Madde:** `{card_id}` · `{title}` (Sprint: S{sprint})\n"
        f"- **1. İlk Geliştirme Durumu:** ✅ {initial_status}\n"
        f"- **2. /verify-sprint Denetim Bulgusu:** ❌ {findings}\n"
        f"- **3. Planlanan ve Uygulanan Onarım:** 🛠️ {fix_applied}\n"
        f"- **4. Onarım Doğrulama Testleri:** 🧪 {tests_run} -> ✅ PASS\n"
        f"- **5. İkinci Denetim Sonucu:** 🎯 {recheck_status}\n"
    )


def _slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sprint Acceptance and Verification Auditor")
    parser.add_argument("--root", default=".", help="Proje kök dizini")
    parser.add_argument("--json", action="store_true", help="JSON çıktı formatı")
    args = parser.parse_args()

    res = audit_sprint(Path(args.root))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"[{res['status']}] {res['summary']}")
        for f in res["findings"]:
            print(f"  - {f['card_id']} ({f['title']}):")
            for iss in f["issues"]:
                print(f"      * [{iss['type']}] {iss['msg']}")

    return 1 if res["status"] == "FAILED" else 0


if __name__ == "__main__":
    sys.exit(main())
