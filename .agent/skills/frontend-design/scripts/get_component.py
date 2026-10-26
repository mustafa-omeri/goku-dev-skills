#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sıfır-Sürtünmeli Hazır Bileşen Teması Köprüsü (get_component.py).

Neden var?
----------
`frontend-design` becerisi altında 55 adet prodüksiyon kalitesinde, çalışan
HTML/CSS bileşen teması (`component-themes/`) bulunmaktadır.

Bu CLI aracı, ajanın veya geliştiricinin diskteki yüzlerce alt klasörü tek tek
gezip vakit kaybetmesini önler; tek bir komutla arama yapmasını, kategorileri
listelemesini ve doğrudan kopyalanabilir HTML/CSS kodunu çekmesini sağlar.

Kullanım:
    python get_component.py --list
    python get_component.py --type sidebar
    python get_component.py --theme violet-minimal-sidebar
    python get_component.py --theme violet-minimal-sidebar --html
    python get_component.py --theme violet-minimal-sidebar --css
    python get_component.py --search "split screen login"
    python get_component.py --search "pricing" --json
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

SCRIPT_DIR = Path(__file__).resolve().parent
FRONTEND_DESIGN_DIR = SCRIPT_DIR.parent
COMPONENT_THEMES_DIR = FRONTEND_DESIGN_DIR / "component-themes"

CATEGORIES = [
    "sidebars", "navbars", "menus", "parallax",
    "accordions", "cards", "logins", "footers"
]


def load_theme_metadata(theme_dir: Path) -> dict:
    """Belirli bir bileşen temasının dizinini tarar ve meta verilerini döner."""
    theme_name = theme_dir.name
    category = theme_dir.parent.name
    html_file = theme_dir / "index.html"
    css_file = theme_dir / "styles.css"
    
    # .design.md dosyasını bul
    design_files = list(theme_dir.glob("*.design.md"))
    design_file = design_files[0] if design_files else None
    
    title = theme_name.replace("-", " ").title()
    description = ""
    ideal_for = ""
    
    if design_file and design_file.is_file():
        try:
            doc_text = design_file.read_text(encoding="utf-8", errors="replace")
            # İlk başlığı bul
            for line in doc_text.splitlines():
                line_str = line.strip()
                if line_str.startswith("# ") and not title:
                    title = line_str[2:].strip()
                elif line_str.startswith("> ") and not description:
                    description = line_str[2:].strip()
                elif ("ideal for" in line_str.lower() or "best for" in line_str.lower() or "uygun:" in line_str.lower()) and not ideal_for:
                    ideal_for = line_str
        except Exception:
            pass

    if not description:
        description = f"{category.rstrip('s').title()} bileşeni için {theme_name} hazır teması."

    return {
        "name": theme_name,
        "title": title,
        "category": category,
        "description": description,
        "ideal_for": ideal_for,
        "path": str(theme_dir),
        "has_html": html_file.is_file(),
        "has_css": css_file.is_file(),
        "design_file": str(design_file) if design_file else None
    }


def get_all_themes() -> list[dict]:
    """component-themes/ altındaki tüm temaları tarar."""
    themes = []
    if not COMPONENT_THEMES_DIR.is_dir():
        return themes

    for cat_dir in sorted(COMPONENT_THEMES_DIR.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name not in CATEGORIES:
            continue
        for t_dir in sorted(cat_dir.iterdir()):
            if not t_dir.is_dir():
                continue
            if (t_dir / "index.html").is_file() or list(t_dir.glob("*.design.md")):
                themes.append(load_theme_metadata(t_dir))
    return themes


def find_theme_by_name(name: str) -> dict | None:
    all_themes = get_all_themes()
    name_clean = name.lower().strip()
    # Tam eşleşme
    for t in all_themes:
        if t["name"].lower() == name_clean:
            return t
    # Kısmi eşleşme
    for t in all_themes:
        if name_clean in t["name"].lower():
            return t
    return None


def search_themes(query: str) -> list[dict]:
    q = query.lower().strip()
    if not q:
        return []
    words = [w for w in re.split(r'\s+', q) if len(w) > 2]
    exact_matches = []
    word_matches = []

    for t in get_all_themes():
        search_blob = f"{t['name']} {t['title']} {t['category']} {t['description']} {t['ideal_for']}".lower()
        if q in search_blob:
            exact_matches.append(t)
        elif words:
            matched_words = [w for w in words if w in search_blob]
            if matched_words:
                word_matches.append((len(matched_words), t))

    word_matches.sort(key=lambda x: x[0], reverse=True)
    return exact_matches + [t for _, t in word_matches if t not in exact_matches]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Hazır Bileşen Teması Köprüsü (get_component.py)")
    parser.add_argument("--list", "-l", action="store_true", help="Tüm hazır bileşen temalarını listeler")
    parser.add_argument("--type", "-t", type=str, default=None, help="Kategoriye göre filtreler (sidebars, navbars, cards, logins, footers...)")
    parser.add_argument("--theme", type=str, default=None, help="Seçilen temanın kodunu ve detaylarını çeker")
    parser.add_argument("--search", "-s", type=str, default=None, help="Bileşen temaları arasında anahtar kelime araması yapar")
    parser.add_argument("--html", action="store_true", help="Yalnızca HTML kodunu basar")
    parser.add_argument("--css", action="store_true", help="Yalnızca CSS kodunu basar")
    parser.add_argument("--json", action="store_true", help="Makine okunur JSON çıktısı üretir")
    args = parser.parse_args(argv)

    all_themes = get_all_themes()

    # 1. ARAMA
    if args.search:
        results = search_themes(args.search)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return 0
        print(f"\n🔍 '{args.search}' için {len(results)} hazır tema bulundu:")
        print("─" * 70)
        for r in results:
            print(f"• [{r['category']}] {r['name']} — {r['title']}")
            print(f"  {r['description']}")
            print(f"  Komut: python .agent/skills/frontend-design/scripts/get_component.py --theme {r['name']}")
            print()
        return 0

    # 2. TEK TEMA ÇEKME
    if args.theme:
        target = find_theme_by_name(args.theme)
        if not target:
            print(f"HATA: '{args.theme}' adında bir bileşen teması bulunamadı!", file=sys.stderr)
            print("Mevcut temaları görmek için: python get_component.py --list", file=sys.stderr)
            return 1

        t_dir = Path(target["path"])
        html_code = (t_dir / "index.html").read_text(encoding="utf-8", errors="replace") if (t_dir / "index.html").is_file() else ""
        css_code = (t_dir / "styles.css").read_text(encoding="utf-8", errors="replace") if (t_dir / "styles.css").is_file() else ""

        if args.json:
            output_obj = dict(target)
            output_obj["html"] = html_code
            output_obj["css"] = css_code
            print(json.dumps(output_obj, indent=2, ensure_ascii=False))
            return 0

        if args.html and not args.css:
            print(html_code)
            return 0

        if args.css and not args.html:
            print(css_code)
            return 0

        # Tam bundle çıktısı
        print("=" * 70)
        print(f"HAZIR BİLEŞEN TEMASI: {target['name']} ({target['category']})")
        print(f"Açıklama: {target['description']}")
        print(f"Konum   : {target['path']}")
        print("=" * 70)
        print("\n<!-- ═══ HTML ISKELETI (index.html) ═══ -->")
        print(html_code)
        print("\n/* ═══ CSS STILLERI (styles.css) ═══ */")
        print(css_code)
        print("\n" + "=" * 70)
        return 0

    # 3. KATEGORİ VEYA TÜMÜNÜ LİSTELEME
    cat_filter = args.type.lower().strip() if args.type else None
    if cat_filter:
        # Tekil/çoğul normalizasyonu (sidebar -> sidebars)
        if not cat_filter.endswith("s") and cat_filter + "s" in CATEGORIES:
            cat_filter = cat_filter + "s"
        filtered = [t for t in all_themes if t["category"] == cat_filter]
    else:
        filtered = all_themes

    if args.json:
        print(json.dumps(filtered, indent=2, ensure_ascii=False))
        return 0

    print("=" * 70)
    print(f"FRONTEND-DESIGN HAZIR BİLEŞEN KÜTÜPHANESİ ({len(filtered)} / {len(all_themes)} Tema)")
    print("=" * 70)

    # Kategoriye göre grupla
    by_cat: dict[str, list[dict]] = {}
    for t in filtered:
        by_cat.setdefault(t["category"], []).append(t)

    for cat_name, themes in sorted(by_cat.items()):
        print(f"\n📁 [{cat_name.upper()}] ({len(themes)} tema):")
        for t in themes:
            print(f"  • {t['name']:<36} {t['description'][:60]}")

    print("\n" + "─" * 70)
    print("Kullanım İpucu:")
    print("  python get_component.py --theme <tema-adi>         (Tüm HTML + CSS kodunu çeker)")
    print("  python get_component.py --search <kelime>          (Anahtar kelimeyle tema arar)")
    print("  python get_component.py --type <kategori>          (Kategoriye göre listeler)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
