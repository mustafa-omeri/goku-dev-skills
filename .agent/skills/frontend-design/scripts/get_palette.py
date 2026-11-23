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
import colorsys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

CATALOG_PATH = Path(__file__).resolve().parent.parent / "themes" / "palette-catalog.md"
STYLE_THEMES_PATH = Path(__file__).resolve().parent.parent / "themes" / "style-theme-palettes.md"

LOCKED_THEME_REFS = {
    "MIDNIGHT SLATE": "themes.css #03 (nordic-slate)",
    "FOREST EMERALD": "themes.css #04 (verdant-abyss)",
    "PLUM+LIME": "themes.css #14 (plum-lime)",
    "DIGITAL FRESH": "themes.css #15 (digital-fresh)",
    "EARTHY ENERGY": "themes.css #16 (earthy-energy)",
}


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


# --- 88 STYLE THEME COLOR PALETTES (İlham & WCAG Türetim Motoru) -------------

def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0, min(255, r)):02X}{max(0, min(255, g)):02X}{max(0, min(255, b)):02X}"


def _relative_luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    def _lin(c: int) -> float:
        v = c / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = _relative_luminance(hex1)
    l2 = _relative_luminance(hex2)
    bright, dark = max(l1, l2), min(l1, l2)
    return round((bright + 0.05) / (dark + 0.05), 2)


def _saturation(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    _, s, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return s


def _mix_hex(hex1: str, hex2: str, weight_hex1: float) -> str:
    r1, g1, b1 = _hex_to_rgb(hex1)
    r2, g2, b2 = _hex_to_rgb(hex2)
    w = max(0.0, min(1.0, weight_hex1))
    return _rgb_to_hex(
        round(r1 * w + r2 * (1.0 - w)),
        round(g1 * w + g2 * (1.0 - w)),
        round(b1 * w + b2 * (1.0 - w)),
    )


def _tint_towards_target(hex_color: str, target_hex: str, bg_hex: str, min_ratio: float) -> Tuple[str, bool]:
    if _contrast_ratio(hex_color, bg_hex) >= min_ratio:
        return hex_color, False
    for step in range(1, 21):
        w = 1.0 - (step / 20.0)
        cand = _mix_hex(hex_color, target_hex, w)
        if _contrast_ratio(cand, bg_hex) >= min_ratio:
            return cand, True
    return target_hex, True


def parse_style_themes(style_path: Path = STYLE_THEMES_PATH) -> List[Dict[str, Any]]:
    if not style_path.is_file():
        return []
    content = style_path.read_text(encoding="utf-8", errors="replace")
    themes: List[Dict[str, Any]] = []
    current_group = ""
    current_subgroup = ""
    idx = 0

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_group = line[3:].strip()
            current_subgroup = ""
            continue
        if line.startswith("### "):
            current_subgroup = line[4:].strip()
            continue
        m = re.match(r"^-\s*Style\s+Theme\s+([^:]+):\s*(.+)$", line, re.IGNORECASE)
        if not m:
            continue
        name = m.group(1).strip()
        raw_colors = m.group(2).strip()
        colors = []
        for part in raw_colors.split(","):
            cm = re.match(r"^(.*?)\s*(#[0-9A-Fa-f]{6})\s*$", part.strip())
            if cm:
                colors.append({
                    "name": cm.group(1).strip(),
                    "hex": cm.group(2).upper(),
                })
        if not colors:
            continue
        idx += 1
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        themes.append({
            "id": idx,
            "name": name,
            "slug": slug,
            "group": current_group,
            "subgroup": current_subgroup,
            "colors": colors,
            "locked_theme_ref": LOCKED_THEME_REFS.get(name.upper()),
        })
    return themes


def search_style_themes(arg1, arg2=None) -> List[Dict[str, Any]]:
    if isinstance(arg1, list):
        themes = arg1
        query = str(arg2 or "")
    else:
        query = str(arg1 or "")
        themes = arg2 if isinstance(arg2, list) else parse_style_themes()

    q = query.lower().strip()
    if not q:
        return []

    words = [w for w in re.split(r"\s+", q) if len(w) > 2]
    exact_matches = []
    word_matches = []

    for t in themes:
        color_text = " ".join(f"{c['name']} {c['hex']}" for c in t.get("colors", [])).lower()
        combined = f"{t['name'].lower()} {t['slug']} {t['group'].lower()} {t.get('subgroup', '').lower()} {color_text}"
        if q in combined:
            exact_matches.append(t)
        elif words:
            matched = [w for w in words if w in combined]
            if matched:
                word_matches.append((len(matched), t))

    word_matches.sort(key=lambda x: x[0], reverse=True)
    return exact_matches + [t for _, t in word_matches if t not in exact_matches]


def find_style_theme(query: str, themes: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    items = themes if themes is not None else parse_style_themes()
    q = query.strip().lower()
    for t in items:
        if t["name"].lower() == q or t["slug"] == q:
            return t
    matches = search_style_themes(items, query)
    return matches[0] if matches else None


def derive_style_theme_roles(theme: Dict[str, Any], mode: str = "dark") -> Dict[str, Any]:
    """88 ilham paletinden WCAG AA (>=4.5:1) garantili semantik CSS tokenlari turetir."""
    colors = theme.get("colors", [])
    by_lum = sorted(colors, key=lambda c: _relative_luminance(c["hex"]))
    darkest = by_lum[0]["hex"]
    lightest = by_lum[-1]["hex"]
    by_sat = sorted(colors, key=lambda c: (_saturation(c["hex"]), _relative_luminance(c["hex"])), reverse=True)
    accent_primary = by_sat[0]["hex"]
    accent_secondary = by_sat[1]["hex"] if len(by_sat) > 1 else by_lum[len(by_lum) // 2]["hex"]

    adjusted = False
    mode_norm = "light" if str(mode).lower() == "light" else "dark"

    if mode_norm == "dark":
        if _relative_luminance(darkest) > 0.08:
            bg_base = _mix_hex(darkest, "#0B0D14", 0.25)
            adjusted = True
        else:
            bg_base = darkest
        bg_surface = _mix_hex(bg_base, lightest, 0.90)
        bg_elevated = _mix_hex(bg_base, lightest, 0.80)
        raw_text = lightest
        text_primary, txt_adj = _tint_towards_target(raw_text, "#F4F6FA", bg_base, 4.5)
        adjusted = adjusted or txt_adj
        text_secondary = _mix_hex(text_primary, bg_base, 0.82)
        text_muted, _ = _tint_towards_target(_mix_hex(text_primary, bg_base, 0.62), text_primary, bg_base, 3.2)
    else:
        if _relative_luminance(lightest) < 0.72:
            bg_base = _mix_hex(lightest, "#FAF9F6", 0.20)
            adjusted = True
        else:
            bg_base = lightest
        bg_surface = _mix_hex(bg_base, darkest, 0.94)
        bg_elevated = _mix_hex(bg_base, darkest, 0.87)
        raw_text = darkest
        text_primary, txt_adj = _tint_towards_target(raw_text, "#12151C", bg_base, 4.5)
        adjusted = adjusted or txt_adj
        text_secondary = _mix_hex(text_primary, bg_base, 0.80)
        text_muted, _ = _tint_towards_target(_mix_hex(text_primary, bg_base, 0.58), text_primary, bg_base, 3.2)

    border_subtle = _mix_hex(bg_base, text_primary, 0.84)
    border_strong = _mix_hex(bg_base, accent_primary, 0.55)
    c_dark_on_acc = _contrast_ratio("#0D1017", accent_primary)
    c_light_on_acc = _contrast_ratio("#F8FAFC", accent_primary)
    accent_contrast = "#0D1017" if c_dark_on_acc >= c_light_on_acc else "#F8FAFC"

    return {
        "name": theme["name"],
        "slug": theme["slug"],
        "mode": mode_norm,
        "adjusted": adjusted,
        "contrast_ratio": _contrast_ratio(text_primary, bg_base),
        "muted_contrast_ratio": _contrast_ratio(text_muted, bg_base),
        "accent_contrast_ratio": max(c_dark_on_acc, c_light_on_acc),
        "tokens": {
            "bg_base": bg_base,
            "bg_surface": bg_surface,
            "bg_elevated": bg_elevated,
            "border_subtle": border_subtle,
            "border_strong": border_strong,
            "text_primary": text_primary,
            "text_secondary": text_secondary,
            "text_muted": text_muted,
            "accent_primary": accent_primary,
            "accent_secondary": accent_secondary,
            "accent_contrast": accent_contrast,
        },
    }


def format_style_theme_css(theme: Dict[str, Any], mode: str = "dark") -> str:
    derived = derive_style_theme_roles(theme, mode=mode)
    tk = derived["tokens"]
    source_colors = ", ".join(f"{c['name']} {c['hex']}" for c in theme["colors"])
    status_note = "WCAG AA Adjusted (ton koruyucu luminance ayarı)" if derived["adjusted"] else "Exact Palette Contrast Pass"
    lines = [
        f"/* Style Theme [ST-{theme['id']:02d}]: {theme['name']} ({derived['mode']} · {theme['group']}) */",
        f"/* Kaynak Palet: {source_colors} */",
        f"/* WCAG 2.1 Kontrast: text/bg={derived['contrast_ratio']}:1 · muted/bg={derived['muted_contrast_ratio']}:1 · on-accent={derived['accent_contrast_ratio']}:1 ({status_note}) */",
        f':root[data-theme="{theme["slug"]}"],',
        ":root {",
        f"  --bg-base: {tk['bg_base']};",
        f"  --bg-surface: {tk['bg_surface']};",
        f"  --bg-elevated: {tk['bg_elevated']};",
        f"  --border-subtle: {tk['border_subtle']};",
        f"  --border-strong: {tk['border_strong']};",
        f"  --text-primary: {tk['text_primary']};",
        f"  --text-secondary: {tk['text_secondary']};",
        f"  --text-muted: {tk['text_muted']};",
        f"  --accent-primary: {tk['accent_primary']};",
        f"  --accent-secondary: {tk['accent_secondary']};",
        f"  --accent-contrast: {tk['accent_contrast']};",
        "}",
    ]
    return "\n".join(lines)


def format_style_theme_card(theme: Dict[str, Any], mode: str = "dark") -> str:
    derived = derive_style_theme_roles(theme, mode=mode)
    tk = derived["tokens"]
    ref = f" · Kilitli Eşlenik: {theme['locked_theme_ref']}" if theme.get("locked_theme_ref") else ""
    out = [
        f"[ST-{theme['id']:02d}] {theme['name']} ({theme['group']}{ref})",
        f"    Kaynak: {', '.join(c['name'] + ' ' + c['hex'] for c in theme['colors'])}",
        f"    WCAG ({derived['mode']}): text/bg={derived['contrast_ratio']}:1 · muted/bg={derived['muted_contrast_ratio']}:1 · on-accent={derived['accent_contrast_ratio']}:1",
        f"    Türetilen Roller: bg={tk['bg_base']} · surface={tk['bg_surface']} · text={tk['text_primary']} · accent={tk['accent_primary']}",
    ]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Zero-friction CLI tool for frontend-design color palettes (10 measured + 88 style themes).")
    parser.add_argument("--list", "-l", action="store_true", help="List 10 measured palettes with core metrics")
    parser.add_argument("--style-themes", action="store_true", help="List all 88 style theme inspiration palettes")
    parser.add_argument("--id", type=int, help="Select measured palette by ID (1-10)")
    parser.add_argument("--name", type=str, help="Select measured palette by name substring")
    parser.add_argument("--style", type=str, help="Select style theme from 88-palette catalog by name/slug")
    parser.add_argument("--mode", choices=["dark", "light"], default="dark", help="Target surface mode for style theme derivation")
    parser.add_argument("--search", "-s", type=str, help="Search across 10 measured palettes and 88 style themes")
    parser.add_argument("--format", "-f", choices=["text", "css", "json", "markdown"], default="text", help="Output format")
    parser.add_argument("--json", action="store_true", help="Shortcut for --format json")

    args = parser.parse_args()

    palettes = parse_catalog()
    style_themes = parse_style_themes()
    if not palettes and not style_themes:
        print(f"[ERROR] No palettes found in {CATALOG_PATH} or {STYLE_THEMES_PATH}", file=sys.stderr)
        sys.exit(1)

    fmt = "json" if args.json else args.format

    # Handle --style-themes listing
    if args.style_themes:
        if fmt == "json":
            print(json.dumps(style_themes, indent=2, ensure_ascii=False))
        else:
            print(f"=== Style Theme Color Palettes ({len(style_themes)} Palet — İlham & Türetim Kataloğu) ===\n")
            print(f"{'ID':<6} | {'Tema Adı':<22} | {'Grup':<28} | {'Renkler'}")
            print("-" * 110)
            for st in style_themes:
                cols = ", ".join(c["hex"] for c in st["colors"])
                print(f"ST-{st['id']:02d}  | {st['name']:<22} | {st['group']:<28} | {cols}")
            print("\nTip: `python get_palette.py --style \"NORDIC NEON\" --mode dark --format css`")
        return

    # Handle --style selection
    if args.style:
        target = find_style_theme(args.style, style_themes)
        if not target:
            print(f"[ERROR] No style theme matching '{args.style}'", file=sys.stderr)
            sys.exit(1)
        if fmt == "json":
            print(json.dumps({"theme": target, "derived": derive_style_theme_roles(target, mode=args.mode)}, indent=2, ensure_ascii=False))
        elif fmt == "css":
            print(format_style_theme_css(target, mode=args.mode))
        else:
            print(format_style_theme_card(target, mode=args.mode))
            print("\nCSS Variables:")
            print(format_style_theme_css(target, mode=args.mode))
        return

    # Handle search (10 measured + 88 style themes)
    if args.search:
        matched_pal = search_palettes(palettes, args.search)
        matched_styles = search_style_themes(style_themes, args.search)
        if fmt == "json":
            print(json.dumps({"measured_palettes": matched_pal, "style_themes": matched_styles}, indent=2, ensure_ascii=False))
        else:
            print(f"Found {len(matched_pal)} measured palette(s) and {len(matched_styles)} style theme(s) for '{args.search}':\n")
            for p in matched_pal:
                print(format_palette_card(p))
                print()
            for st in matched_styles[:10]:
                print(format_style_theme_card(st, mode=args.mode))
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
        print(f"=== Frontend-Design Palette Catalog ({len(palettes)} Ölçülmüş Palet + {len(style_themes)} Style Theme İlham Paleti) ===\n")
        print(f"{'#':<3} | {'Palet Başlığı':<36} | {'Mod':<8} | {'Zemin':<9} | {'Metin':<9} | {'Vurgu':<9} | {'Kontrast'}")
        print("-" * 95)
        for p in palettes:
            roles = p.get("roles", {})
            z = roles.get("zemin", {}).get("hex", "-")
            m = roles.get("metin", {}).get("hex", "-")
            v = roles.get("vurgu", {}).get("hex", "-")
            contrast_brief = p.get("contrast", "-")
            print(f"{p['id']:<3} | {p['title']:<36} | {p['mode']:<8} | {z:<9} | {m:<9} | {v:<9} | {contrast_brief}")
        print("\nTip: `python get_palette.py --id <num> --format css` (10 Ölçülmüş) | `python get_palette.py --style-themes` (88 Style Theme)")


if __name__ == "__main__":
    main()
