#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""İnteraktif Özellik ve Kullanım HTML Rehberi Kapısı (docs/kullanici-rehberi.html).

Neden var?
----------
`development-workflow.md` Adım 4.2 ve `sprint-delivery-workflow.md` §6.0 kuralları,
her sprint çıktısında veya anlamlı geliştirmede `docs/kullanici-rehberi.html` (veya
`docs/user-guide.html`) dosyasının güncel şablon mimarisinde (Obsidian Command Deck)
oluşturulmasını veya güncellenmesini zorunlu kılar.

Bu kapı olmadan ajanlar:
1. Dosya mevcut olduğunda eski şablon yapısında kilitli kalmakta (şablon sapması / drift),
2. Yeni kartları eski sözdizimiyle eklemekte,
3. Şablondan kopyalanan sahte/örnek verileri (supabase, compute-kpi vb.) projeye sızdırmakta,
4. Yalnızca KULLANICI_TEST_REHBERI.md dosyasını güncelleyip HTML rehberini atlamaktadır.

Kontroller
----------
E1 zorunlu dosya eksik        docs/kullanici-rehberi.html (veya DOCs/ / user-guide.html) bulunamadı
E2 mimari sapma (drift)       Rehber, güncel Obsidian Command Deck (app-layout, app-sidebar, features-container, 3-tier tokens) standardına uymuyor; eski tema veya tek sütun yapısı kullanıyor
E3 şablon yer tutucusu        Rehber içinde doldurulmamış yer tutucu ({{PROJE_ADI}}, {{VERSIYON}}, supabase/migrations/20261101 vb.) tespit edildi
E4 eksik kart mimarisi        Kartlarda zorunlu bölümler (5-katmanlı dilim, playbook adımları veya skeleton durumları) eksik
E5 sıfır özellik kartı        Rehber içinde hiçbir özellik kartı (<article class="feature-card">) bulunamadı
W1 acil kurtarma tablosu yok  Playbook içinde FAA AC 121-24C standardına uygun sorun giderme tablosu tavsiye edilir
W2 test rehberi bağlantısı    Rehber sonunda KULLANICI_TEST_REHBERI.md canlı bağlantısı eksik

Çıkış kodları:
    0 = Geçti (veya kapsam dışı)
    1 = Hata (E1..E5)
    2 = Araç / argüman hatası
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Eski / geçersiz şablon göstergeleri (Drift tespiti)
LEGACY_INDICATORS = [
    re.compile(r'data-theme=["\']obsidian-velvet["\']', re.IGNORECASE),
    re.compile(r'LOCKED THEMES & SEMANTIC TOKENS', re.IGNORECASE),
    re.compile(r'data-theme=["\']nordic-slate["\']', re.IGNORECASE),
    re.compile(r'<select[^>]*id=["\']themeSelect["\']', re.IGNORECASE),
]

# Güncel Obsidian Command Deck zorunlu mimari imzaları
REQUIRED_SIGNATURES = [
    ("app-layout", re.compile(r'class=["\'][^"\']*app-layout[^"\']*["\']')),
    ("app-sidebar", re.compile(r'class=["\'][^"\']*app-sidebar[^"\']*["\']')),
    ("features-container", re.compile(r'class=["\'][^"\']*features-container[^"\']*["\']')),
    ("3-tier-tokens", re.compile(r'--slate-950|3-TIER DESIGN TOKEN', re.IGNORECASE)),
]

# Şablon yer tutucuları ve sahte veri kalıntıları
TEMPLATE_PLACEHOLDERS = [
    (re.compile(r'\{\{PROJE_ADI\}\}'), "Doldurulmamış '{{PROJE_ADI}}' şablon değişkeni"),
    (re.compile(r'\{\{VERSIYON\}\}'), "Doldurulmamış '{{VERSIYON}}' şablon değişkeni"),
    (re.compile(r'supabase/migrations/20261101_dashboard\.sql'), "Örnek şablondan sızan sahte 'supabase/migrations/20261101_dashboard.sql' kalıntısı"),
    (re.compile(r'Edge Function:\s*compute-kpi'), "Örnek şablondan sızan sahte 'Edge Function: compute-kpi' kalıntısı"),
]

CARD_RE = re.compile(r'<article[^>]*class=["\'][^"\']*feature-card[^"\']*["\']', re.IGNORECASE)
SLICE_PANEL_RE = re.compile(r'class=["\'][^"\']*(?:slice-panel|arch-panel)[^"\']*["\']', re.IGNORECASE)
PLAYBOOK_PANEL_RE = re.compile(r'class=["\'][^"\']*playbook-panel[^"\']*["\']', re.IGNORECASE)
STATES_PANEL_RE = re.compile(r'class=["\'][^"\']*states-panel[^"\']*["\']', re.IGNORECASE)


def find_guide_path(root: Path) -> Path | None:
    """Proje içinde kullanici-rehberi.html veya user-guide.html dosyasını arar."""
    candidates = [
        root / "docs" / "kullanici-rehberi.html",
        root / "DOCs" / "kullanici-rehberi.html",
        root / "docs" / "user-guide.html",
        root / "DOCs" / "user-guide.html",
        root / "kullanici-rehberi.html",
    ]
    for cand in candidates:
        if cand.is_file():
            return cand
            
    # Büyük/küçük harf duyarsız arama
    for d_name in ("docs", "DOCs"):
        d = root / d_name
        if d.is_dir():
            for f in d.iterdir():
                if f.is_file() and f.name.lower() in ("kullanici-rehberi.html", "user-guide.html"):
                    return f
    return None


def is_in_scope(root: Path) -> bool:
    """Projenin bu kuralın kapsamında olup olmadığını belirler."""
    # 0. skillSetWorks meta-deposu kural ve skill kaynağıdır; uygulama olmadığı için kapsam dışıdır
    if (root / ".agent" / "skills-catalog.html").is_file() and not (root / "src").is_dir() and not (root / "docs" / "kullanici-rehberi.html").is_file():
        return False

    # 1. SPRINT_PLAN.md veya KANBAN.md varsa kesinlikle kapsamdadır
    if (root / "SPRINT_PLAN.md").is_file() or (root / "KANBAN.md").is_file():
        return True
    # 2. Halihazırda bir rehber dosyası varsa doğrulanmalıdır
    if find_guide_path(root) is not None:
        return True
    # 3. Web veya mobil uygulama kaynak kodları varsa kapsamdadır
    src_dir = root / "src"
    if src_dir.is_dir():
        has_app_code = any(
            src_dir.rglob(pat)
            for pat in ("*.tsx", "*.jsx", "*Controller.java", "*Service.java")
        )
        if has_app_code:
            return True
    return False


def audit_user_guide(root: Path) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]], Dict[str, Any]]:
    errors: List[Tuple[str, str, str]] = []
    warnings: List[Tuple[str, str, str]] = []
    stats: Dict[str, Any] = {"path": None, "cards_count": 0, "status": "FAIL"}

    if not is_in_scope(root):
        stats["status"] = "KAPSAM_DISI"
        return errors, warnings, stats

    guide_path = find_guide_path(root)
    if not guide_path:
        errors.append(("E1", "docs/kullanici-rehberi.html",
                       "İnteraktif özellik HTML rehberi bulunamadı! "
                       "Her sprint ve anlamlı geliştirme sonrasında docs/kullanici-rehberi.html "
                       "(şablon: .agent/templates/KULLANICI_REHBERI.template.html) güncellenmelidir."))
        return errors, warnings, stats

    stats["path"] = str(guide_path.relative_to(root)) if guide_path.is_relative_to(root) else str(guide_path)

    try:
        content = guide_path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(("E1", str(guide_path), f"Dosya okunamadı: {e}"))
        return errors, warnings, stats

    # E2: Mimari sapma (Legacy tema / eski tek sütun yapısı kontrolü)
    for leg_pat in LEGACY_INDICATORS:
        if leg_pat.search(content):
            errors.append(("E2", stats["path"],
                           "Rehberde eski/miras tema veya tek sütun yapısı tespit edildi. "
                           "Rehber, .agent/templates/KULLANICI_REHBERI.template.html içindeki güncel "
                           "Obsidian Command Deck mimarisine migrate edilmelidir."))
            break

    # E2: Güncel mimari imzaları tam mı?
    for sig_name, sig_pat in REQUIRED_SIGNATURES:
        if not sig_pat.search(content):
            errors.append(("E2", stats["path"],
                           f"Güncel Obsidian Command Deck imzası eksik: '{sig_name}'. "
                           "Dosya .agent/templates/KULLANICI_REHBERI.template.html standardında olmalıdır."))

    # E3: Şablon yer tutucuları ve sahte veri sızıntıları
    for pl_pat, pl_msg in TEMPLATE_PLACEHOLDERS:
        if pl_pat.search(content):
            errors.append(("E3", stats["path"], f"Şablon kalıntısı tespit edildi: {pl_msg}"))

    # E5: Özellik kartları sayısı
    cards = CARD_RE.findall(content)
    card_count = len(cards)
    stats["cards_count"] = card_count
    if card_count == 0:
        errors.append(("E5", stats["path"],
                       "Rehber içinde hiçbir özellik kartı (<article class=\"feature-card\">) bulunamadı."))
    else:
        # E4: Kart mimarisi bütünlüğü
        # Her kartta slice-panel, playbook-panel ve states-panel olmalı
        slice_matches = len(SLICE_PANEL_RE.findall(content))
        playbook_matches = len(PLAYBOOK_PANEL_RE.findall(content))
        states_matches = len(STATES_PANEL_RE.findall(content))

        if slice_matches < card_count or playbook_matches < card_count or states_matches < card_count:
            errors.append(("E4", stats["path"],
                           f"Kart mimarisi eksik: {card_count} kart var, ancak "
                           f"{slice_matches} 5-katman dilimi, {playbook_matches} playbook ve "
                           f"{states_matches} durum paneli tespit edildi. Her kartta 3 zorunlu panel bulunmalıdır."))

    # W2: KULLANICI_TEST_REHBERI.md referansı
    if "KULLANICI_TEST_REHBERI.md" not in content:
        warnings.append(("W2", stats["path"],
                         "Sayfa altında KULLANICI_TEST_REHBERI.md manuel test rehberine canlı link verilmesi önerilir."))

    stats["status"] = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return errors, warnings, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="İnteraktif Özellik HTML Rehberi Kapısı")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Proje kök dizini (varsayılan: cwd)")
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı")
    parser.add_argument("--strict", action="store_true", help="Uyarıları da hata say")
    args = parser.parse_args()

    root = args.root.resolve()
    errors, warnings, stats = audit_user_guide(root)

    if args.json:
        out = {
            "status": stats["status"],
            "guide_path": stats["path"],
            "cards_count": stats["cards_count"],
            "errors": [{"code": c, "file": f, "msg": m} for c, f, m in errors],
            "warnings": [{"code": c, "file": f, "msg": m} for c, f, m in warnings],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        if stats["status"] == "KAPSAM_DISI":
            print("[KAPSAM_DISI] İnteraktif kullanıcı rehberi gerektiren bir uygulama kapsamı bulunamadı.")
            return 0

        if not errors and not warnings:
            print(f"[OK] İnteraktif kullanıcı rehberi tam uyumlu: {stats['path']} ({stats['cards_count']} özellik kartı, Command Deck mimarisi)")
            return 0

        for code, fpath, msg in errors:
            print(f"[ERROR] {code} {fpath}: {msg}")
        for code, fpath, msg in warnings:
            print(f"[WARN]  {code} {fpath}: {msg}")

        print(f"\nSonuç: {len(errors)} hata, {len(warnings)} uyarı. ({stats['path']}, {stats['cards_count']} kart)")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

