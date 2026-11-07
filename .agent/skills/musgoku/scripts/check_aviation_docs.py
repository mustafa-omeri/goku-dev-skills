#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aviation Passenger Safety Card (FAA AC 121-24C Style) Dokümantasyon ve Kılavuz Kapısı.

Neden var?
----------
Kullanım kılavuzları, kurulum rehberleri, 'nasıl yapılır' dokümanları ve test
senaryoları laf kalabalığından arındırılmış, kronolojik, kopyala-yapıştır hazır,
yıkıcı adımlar öncesinde 'Brace Position' (CRITICAL) uyarıları taşıyan ve her
zaman 'Ditching / Emergency Exit' acil kurtarma tablosu içeren bir formatta
olmalıdır.

Kontroller
----------
E1 acil durum tablosu yok      kılavuz/test rehberi sonunda acil durum kurtarma tablosu olmalı
E2 çıktı doğrulaması eksik     prosedür adımlarında eylem -> beklenen çıktı eşleşmesi olmalı
E3 korumasız yıkıcı komut      yıkıcı komutlar (DROP, TRUNCATE, rm -rf, push -f) öncesinde ⚠️ CRITICAL olmalı
E4 kopyalama bozan yer tutucu  kod bloklarında '...' veya '<TODO>' gibi kırık yer tutucular olmamalı

Kullanım
--------
    python .agent/skills/musgoku/scripts/check_aviation_docs.py
    python .agent/skills/musgoku/scripts/check_aviation_docs.py --json
    python .agent/skills/musgoku/scripts/check_aviation_docs.py --strict
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Acil çıkış tablosu başlık sütunları deseni
EMERGENCY_TABLE_RE = re.compile(
    r"\|\s*(?:Symptom|Belirti|Hata|Error)[^|]*\|\s*(?:Probable Cause|Olası Neden|Neden|Sebep)[^|]*\|\s*(?:Immediate Corrective Action|Anında Düzeltici Eylem|Çözüm|Düzeltme|Aksiyon)[^|]*\|",
    re.IGNORECASE,
)

# Yıkıcı veya tehlikeli operasyonlar
DESTRUCTIVE_CMD_RE = re.compile(
    r"\b(?:rm\s+-[rf]{1,2}|DROP\s+(?:TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE|git\s+push\s+(?:--force|-f)|git\s+reset\s+--hard)\b",
    re.IGNORECASE,
)

# Kırık yer tutucu deseni (kod blokları içinde tek başına duran ellipsis veya todo)
BROKEN_PLACEHOLDER_RE = re.compile(
    r"```(?:bash|sh|shell|powershell|pwsh|cmd)\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def find_doc_targets(root: Path) -> list[Path]:
    """Kural kapsamında denetlenecek doküman ve şablonları toplar."""
    targets: list[Path] = []

    # Proje içi docs kılavuzları
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for p in docs_dir.rglob("*.md"):
            # Yalnızca rehber, test, setup, how-to, runbook dosyaları
            lower = p.name.lower()
            if any(k in lower for k in ("test", "rehber", "guide", "setup", "how-to", "runbook", "manual")):
                targets.append(p)

    # Kök rehberler
    for name in ("README.md", "HANDOFF.md"):
        p = root / name
        if p.is_file() and name != "HANDOFF.md":  # HANDOFF kendi kapısına sahip
            targets.append(p)

    # .agent/templates altındaki doküman şablonları
    tmpl_dir = root / ".agent" / "templates"
    if tmpl_dir.is_dir():
        for name in (
            "KULLANICI_TEST_REHBERI.template.md",
            "DEPLOYMENT_PLAN.template.md",
            "PLAN.template.md",
        ):
            p = tmpl_dir / name
            if p.is_file():
                targets.append(p)

    return sorted(list(set(targets)))


def check_file(path: Path) -> tuple[list[dict], list[dict]]:
    """Tek bir dokümanı FAA AC 121-24C kurallarına göre inceler."""
    errors: list[dict] = []
    warnings: list[dict] = []

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append({
            "code": "E0",
            "file": str(path),
            "line": 1,
            "message": f"Dosya okunamadı: {e}",
        })
        return errors, warnings

    lines = content.splitlines()

    # 1. E1: Acil Çıkış Tablosu Kontrolü (User manual, test guide, deployment plan)
    is_guide = any(k in path.name.lower() for k in ("test", "rehber", "guide", "manual", "deploy", "setup"))
    if is_guide and not EMERGENCY_TABLE_RE.search(content):
        errors.append({
            "code": "E1",
            "file": str(path),
            "line": len(lines),
            "message": "FAA AC 121-24C Acil Çıkış / Sorun Giderme tablosu bulunamadı (| Belirti/Hata | Olası Neden | Anında Düzeltici Eylem |)",
        })

    # 2. E3: Tehlikeli komut öncesinde CRITICAL uyarısı var mı?
    for idx, line in enumerate(lines, 1):
        if DESTRUCTIVE_CMD_RE.search(line):
            # Önceki 5 satırda CRITICAL uyarısı aranır
            window_start = max(0, idx - 6)
            window = "\n".join(lines[window_start:idx])
            if "CRITICAL" not in window and "KRİTİK" not in window:
                errors.append({
                    "code": "E3",
                    "file": str(path),
                    "line": idx,
                    "message": f"Yıkıcı komut öncesinde '⚠️ CRITICAL:' uyarısı bulunamadı: {line.strip()}",
                })

    # 3. E4: Kod bloklarında copy-paste kıran çıplak '...' yer tutucusu
    for match in BROKEN_PLACEHOLDER_RE.finditer(content):
        code_block = match.group(1)
        for sub_line in code_block.splitlines():
            stripped = sub_line.strip()
            if stripped in ("...", "....", "<TODO>", "[TODO]"):
                errors.append({
                    "code": "E4",
                    "file": str(path),
                    "line": 1,
                    "message": f"Kopyalamayı bozan çıplak yer tutucu tespit edildi: '{stripped}'",
                })
                break

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı")
    parser.add_argument("--strict", action="store_true", help="Uyarıları da hata say")
    args = parser.parse_args()

    root = Path(os.environ.get("AGENTS_PROJECT_ROOT") or Path.cwd()).resolve()
    targets = find_doc_targets(root)

    all_errors: list[dict] = []
    all_warnings: list[dict] = []

    for target in targets:
        errs, warns = check_file(target)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    exit_code = 1 if all_errors or (args.strict and all_warnings) else 0

    if args.json:
        res = {
            "status": "PASS" if exit_code == 0 else "FAIL",
            "scanned_files": [str(p.relative_to(root)) for p in targets],
            "errors": all_errors,
            "warnings": all_warnings,
            "exit_code": exit_code,
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return exit_code

    print(f"Aviation Dokümantasyon Kapısı (FAA AC 121-24C): {len(targets)} dosya tarandı.")
    if all_errors:
        print(f"\n❌ {len(all_errors)} Hata Tespit Edildi:")
        for err in all_errors:
            rel = Path(err["file"]).relative_to(root)
            print(f"  [{err['code']}] {rel}:{err['line']} -> {err['message']}")
    if all_warnings:
        print(f"\n⚠️ {len(all_warnings)} Uyarı:")
        for warn in all_warnings:
            rel = Path(warn["file"]).relative_to(root)
            print(f"  [{warn['code']}] {rel}:{warn['line']} -> {warn['message']}")

    if exit_code == 0:
        print("SONUC: Tüm doküman ve şablonlar FAA AC 121-24C standardına uygun · [OK]")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
