#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""get_palette.py - Zero-friction CLI tool for frontend-design color palettes.

Parses palette-catalog.md and provides quick search, inspection, and CSS variable generation.

Usage:
  python get_palette.py --list
  python get_palette.py --id 7
  python get_palette.py --id 7 --format css
  python get_palette.py --search "orman"
  python get_palette.py --search "karanlık" --json
"""

import sys
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

CATALOG_PATH = Path(__file__).resolve().parent.parent / "themes" / "palette-catalog.md"


def parse_catalog(catalog_path: Path = CATALOG_PATH) -> List[Dict[str, Any]]:
    if not catalog_path.exists():
        return []

    content = catalog_path.read_text(encoding="utf-8")
    palettes = []

    # Split by section "## <number>. <title>"
    sections = re.split(r'\n(?=## \d+\. )', content)

    for sec in sections:
        header_match = re.match(r'## (\d+)\.\s+([^\n]+)', sec)
        if not header_match:
            continue

        p_id = int(header_match.group(1))
        title = header_match.group(2).strip()

        # Tema yönü
        mode_match = re.search(r'\*\*Tema yönü:\*\*\s*([^\s·]+)', sec)
        mode = mode_match.group(1).strip() if mode_match else "açık"

        # Colors table
        colors = []
        # Find first table after header
        raw_colors_match = re.search(r'\| HEX \| Renk adı \|\n\|---\|---\|\n((?:\| `#[A-Fa-f0-9]{6}` \| [^\n]+\|\n?)+)', sec)
        if raw_colors_match:
            for line in raw_colors_match.group(1).strip().split('\n'):
                cm = re.match(r'\|\s*`?(#[A-Fa-f0-9]{6})`?\s*\|\s*([^\|]+)\|', line)
                if cm:
                    colors.append({
                        "hex": cm.group(1).strip(),
                        "name": cm.group(2).strip()
                    })

        # Roles table
        roles = {}
        roles_match = re.search(r'\*\*Rol önerisi:\*\*\s*\n\s*\| Rol \| HEX \| Renk adı \|\n\|---\|---\|---\|\n((?:\| [^\n]+\|\n?)+)', sec)
        if roles_match:
            for line in roles_match.group(1).strip().split('\n'):
                rm = re.match(r'\|\s*([a-zA-ZçğıöşüÇĞİÖŞÜ]+)\s*\|\s*`?(#[A-Fa-f0-9]{6})`?\s*\|\s*([^\|]+)\|', line)
                if rm:
                    role_key = rm.group(1).strip().lower()
                    roles[role_key] = {
                        "hex": rm.group(2).strip(),
                        "name": rm.group(3).strip()
                    }

        # Contrast
        contrast_match = re.search(r'\*\*Metin/zemin kontrastı:\*\*\s*[^\n]+→\s*\*\*([^\*]+)\*\*', sec)
        contrast = contrast_match.group(1).strip() if contrast_match else ""

        # On accent
        on_accent_match = re.search(r'\*\*Vurgu üzerine metin:\*\*\s*[^\n]+→\s*\*\*önerilen:\s*`?(#[A-Fa-f0-9]{6})`?\*\*', sec)
        on_accent = on_accent_match.group(1).strip() if on_accent_match else "#FFFFFF"

        palettes.append({
            "id": p_id,
            "title": title,
            "mode": mode,
            "colors": colors,
            "roles": roles,
            "contrast": contrast,
            "on_accent": on_accent,
        })

    return palettes


def format_css_variables(palette: Dict[str, Any]) -> str:
    roles = palette.get("roles", {})
    zemin = roles.get("zemin", {}).get("hex", "#FFFFFF")
    metin = roles.get("metin", {}).get("hex", "#111827")
    vurgu = roles.get("vurgu", {}).get("hex", "#3B82F6")
    ikincil = roles.get("ikincil", {}).get("hex", "#F3F4F6")
    yardimci = roles.get("yardimci", {}).get("hex", "#9CA3AF")
    on_accent = palette.get("on_accent", "#FFFFFF")

    lines = [
        f"/* Palette #{palette['id']}: {palette['title']} ({palette['mode']}) */",
        f"/* Contrast: {palette.get('contrast', 'N/A')} */",
        ":root {",
        f"  --bg-primary: {zemin};",
        f"  --text-primary: {metin};",
        f"  --color-accent: {vurgu};",
        f"  --text-on-accent: {on_accent};",
        f"  --bg-secondary: {ikincil};",
        f"  --text-muted: {yardimci};",
        f"  --border-subtle: {yardimci}40;",
        "}"
    ]
    return "\n".join(lines)


def format_palette_card(palette: Dict[str, Any]) -> str:
    roles = palette.get("roles", {})
    out = []
    out.append(f"[{palette['id']}] {palette['title']} ({palette['mode'].upper()})")
    out.append(f"    Kontrast: {palette.get('contrast', 'N/A')} · Vurgu üzeri yazı: {palette.get('on_accent', '#FFFFFF')}")
    out.append("    Roller:")
    for role, data in roles.items():
        out.append(f"      - {role:<10}: {data.get('hex', '')} ({data.get('name', '')})")
    return "\n".join(out)


def search_palettes(arg1, arg2=None) -> List[Dict[str, Any]]:
    if isinstance(arg1, list):
        palettes = arg1
        query = str(arg2 or "")
    else:
        query = str(arg1 or "")
        palettes = arg2 if isinstance(arg2, list) else parse_catalog()

    q = query.lower().strip()
    if not q:
        return []

    words = [w for w in re.split(r'\s+', q) if len(w) > 2]
    exact_matches = []
    word_matches = []

    for p in palettes:
        title = p["title"].lower()
        mode = p["mode"].lower()
        color_names = " ".join([c["name"].lower() for c in p.get("colors", [])])
        role_names = " ".join([r["name"].lower() for r in p.get("roles", {}).values()])
        combined = f"{title} {mode} {color_names} {role_names}"
        if q in combined:
            exact_matches.append(p)
        elif words:
            matched_words = [w for w in words if w in combined]
            if matched_words:
                word_matches.append((len(matched_words), p))

    word_matches.sort(key=lambda x: x[0], reverse=True)
    return exact_matches + [p for _, p in word_matches if p not in exact_matches]


def main():
    parser = argparse.ArgumentParser(description="Zero-friction CLI tool for frontend-design color palettes.")
    parser.add_argument("--list", "-l", action="store_true", help="List all palettes with core metrics")
    parser.add_argument("--id", type=int, help="Select palette by ID (1-10)")
    parser.add_argument("--name", type=str, help="Select palette by name substring")
    parser.add_argument("--search", "-s", type=str, help="Search palettes by keyword, mode, or color name")
    parser.add_argument("--format", "-f", choices=["text", "css", "json", "markdown"], default="text", help="Output format")
    parser.add_argument("--json", action="store_true", help="Shortcut for --format json")

    args = parser.parse_args()

    palettes = parse_catalog()
    if not palettes:
        print(f"[ERROR] No palettes found in {CATALOG_PATH}", file=sys.stderr)
        sys.exit(1)

    fmt = "json" if args.json else args.format

    # Handle search
    if args.search:
        matched = search_palettes(palettes, args.search)
        if fmt == "json":
            print(json.dumps(matched, indent=2, ensure_ascii=False))
        else:
            print(f"Found {len(matched)} matching palette(s) for query '{args.search}':\n")
            for p in matched:
                print(format_palette_card(p))
                print()
        return

    # Handle id
    if args.id is not None:
        matched = [p for p in palettes if p["id"] == args.id]
        if not matched:
            print(f"[ERROR] Palette with ID {args.id} not found (available: 1-{len(palettes)})", file=sys.stderr)
            sys.exit(1)
        target = matched[0]
        if fmt == "json":
            print(json.dumps(target, indent=2, ensure_ascii=False))
        elif fmt == "css":
            print(format_css_variables(target))
        else:
            print(format_palette_card(target))
            print("\nCSS Variables:")
            print(format_css_variables(target))
        return

    # Handle name
    if args.name:
        matched = [p for p in palettes if args.name.lower() in p["title"].lower()]
        if not matched:
            print(f"[ERROR] No palette matching name '{args.name}'", file=sys.stderr)
            sys.exit(1)
        target = matched[0]
        if fmt == "json":
            print(json.dumps(target, indent=2, ensure_ascii=False))
        elif fmt == "css":
            print(format_css_variables(target))
        else:
            print(format_palette_card(target))
            print("\nCSS Variables:")
            print(format_css_variables(target))
        return

    # Default / List
    if fmt == "json":
        print(json.dumps(palettes, indent=2, ensure_ascii=False))
    else:
        print(f"=== Frontend-Design Palette Catalog ({len(palettes)} Palettes) ===\n")
        print(f"{'#':<3} | {'Palet Başlığı':<36} | {'Mod':<8} | {'Zemin':<9} | {'Metin':<9} | {'Vurgu':<9} | {'Kontrast'}")
        print("-" * 95)
        for p in palettes:
            roles = p.get("roles", {})
            z = roles.get("zemin", {}).get("hex", "-")
            m = roles.get("metin", {}).get("hex", "-")
            v = roles.get("vurgu", {}).get("hex", "-")
            contrast_brief = p.get("contrast", "-")
            print(f"{p['id']:<3} | {p['title']:<36} | {p['mode']:<8} | {z:<9} | {m:<9} | {v:<9} | {contrast_brief}")
        print("\nTip: Use `python get_palette.py --id <num> --format css` to generate copy-paste CSS variables.")


if __name__ == "__main__":
    main()
