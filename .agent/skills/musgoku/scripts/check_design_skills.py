#!/usr/bin/env python3
"""Tasarim skilleri sahiplik denetleyicisi — "bir konunun tek sahibi vardir" kapisi.

Neden var?
----------
`design-skills-enforcement.md` §3 bir sahiplik tablosu tanimlar ve "bir konuyu
iki skill sahiplenmez" der. Bu, **hicbir arac olcmediği** icin bir niyet
cumlesiydi: iki skill'i ayni konuda cagirmak normal bir seydi ve kimse
farkina varmiyordu. Kanit: `ui-styling/canvas-fonts` ile `canvas-design`
ayni 81 dosyayi tasiyordu — sahiplik cakisilmasi, sonrasi 5,4 MB.

Kontroller
----------
D1 tablo okunamadi / bos satir   sahiplik tablosu bozulmus mu
D2 ayni konu iki kez            bir konunun iki sahibi olmamali
D3 sahibi olmayan skill          tabloya yazilan skill diskte var mi
D4 zorunlu ucle eksik            canvas-design + frontend-design + ui-ux-pro-max
D5 kopuk kapsam disi ilani      "kapsam disi" denilen skill tabloda gorunmeli

Hata (exit 1) · arac hatasi exit 2 · temizse exit 0

Kullanim
--------
    python .agent/skills/musgoku/scripts/check_design_skills.py
    python .agent/skills/musgoku/scripts/check_design_skills.py --json

Ortam
-----
AGENTS_PROJECT_ROOT   proje kokunu elle verir
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RULE_FILE = "rules/design-skills-enforcement.md"
REQUIRED_TRIO = ("canvas-design", "frontend-design", "ui-ux-pro-max")

TABLE_HEADING_RE = re.compile(r"^##\s+3\.\s+Sahiplik", re.MULTILINE)
ROW_RE = re.compile(r"^\|(?P<konu>[^|]+?)\|(?P<sahip>[^|]+?)\|\s*$")
KAPSAM_DISI_RE = re.compile(r"^\*\*Kapsam dısı[^:]*:\*\*\s*(?P<liste>.+)$", re.MULTILINE)
SKILL_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`")


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


def parse_table(text: str):
    """Sahiplik tablosunu [(konu, sahip_skill_listesi)] olarak dondurur."""
    match = TABLE_HEADING_RE.search(text)
    if not match:
        return None
    rows = []
    for line in text[match.end():].split("\n"):
        if line.startswith("## "):
            break
        row = ROW_RE.match(line)
        if not row:
            continue
        konu = row.group("konu").strip()
        if konu in ("Konu", "------", "---"):
            continue
        if set(konu) <= set("- "):
            continue
        sahip = [m.group(1) for m in SKILL_RE.finditer(row.group("sahip"))]
        rows.append((konu, sahip))
    return rows


def parse_out_of_scope(text: str):
    match = KAPSAM_DISI_RE.search(text)
    if not match:
        return []
    return [m.group(1) for m in SKILL_RE.finditer(match.group("liste"))]


def normalize_topic(konu: str) -> str:
    """Konu basligini karsilastirma icin sadelestirir."""
    konu = konu.lower().replace("**", "")
    konu = re.sub(r"\([^)]*\)", "", konu)
    konu = re.sub(r"[^a-z0-9ğüşıöç ]+", " ", konu)
    return re.sub(r"\s+", " ", konu).strip()


def check(root: Path):
    errors = []
    warnings = []

    rule_path = root / ".agent" / RULE_FILE
    if not rule_path.is_file():
        return ([("D1", RULE_FILE, "kural dosyasi bulunamadi")], warnings, 0)

    text = rule_path.read_text(encoding="utf-8")
    rows = parse_table(text)
    out_of_scope = parse_out_of_scope(text)

    if rows is None or not rows:
        return ([("D1", RULE_FILE,
                  "sahiplik tablosu bulunamadi veya bos (§3 basligi ve satirlari bozuk)")],
                warnings, len(rows or []))

    for konu, sahipler in rows:
        if not sahipler:
            errors.append(("D1", "design-skills-enforcement.md",
                           f"konunun sahibi yok: {konu!r}"))
            continue
        for skill in sahipler:
            if skill in out_of_scope:
                continue
            if not (root / ".agent" / "skills" / skill).is_dir():
                errors.append(("D3", "design-skills-enforcement.md",
                               f"tablo bu skill'i sahip gosteriyor ama diskte yok: {skill}"))

    seen = {}
    for konu, _ in rows:
        key = normalize_topic(konu)
        if key in seen:
            errors.append(("D2", "design-skills-enforcement.md",
                           f"konu iki kez tanimli: {seen[key]!r} ve {konu!r}"))
        else:
            seen[key] = konu

    for skill in REQUIRED_TRIO:
        if skill not in [s for _, sahipler in rows for s in sahipler]:
            errors.append(("D4", "design-skills-enforcement.md",
                           f"zorunlu ucle sahiplik tablosunda yok: {skill}"))
        elif not (root / ".agent" / "skills" / skill).is_dir():
            errors.append(("D4", "design-skills-enforcement.md",
                           f"zorunlu ucle skill diskte yok: {skill}"))

    owners = {s for _, sahipler in rows for s in sahipler}
    for skill in out_of_scope:
        if skill in owners:
            continue
        if (root / ".agent" / "skills" / skill).is_dir():
            warnings.append(("D5", "design-skills-enforcement.md",
                             f"kapsam disi ilan edilen skill artik depoda: {skill}"))

    return errors, warnings, len(rows)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Tasarim skilleri sahiplik denetleyicisi")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = find_project_root()
    errors, warnings, row_count = check(root)

    if args.json:
        print(json.dumps({
            "rows": row_count,
            "errors": [{"code": c, "file": f, "message": m} for c, f, m in errors],
            "warnings": [{"code": c, "file": f, "message": m} for c, f, m in warnings],
            "exit": 1 if errors else 0,
        }, ensure_ascii=False, indent=2))
        return 1 if errors else 0

    print(f"Sahiplik tablosu: {row_count} satir · kapsam disi: "
          f"{len(parse_out_of_scope((root / '.agent' / RULE_FILE).read_text(encoding='utf-8')))}")
    for code, name, message in errors:
        print(f"[HATA] {code} {name}: {message}")
    for code, name, message in warnings:
        print(f"[UYARI] {code} {name}: {message}")
    if errors:
        print(f"\nSONUC: {len(errors)} hata · {len(warnings)} uyari · sahiplik gecersiz")
        return 1
    print(f"\nSONUC: {row_count} konu · her konunun tek sahibi var · [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())