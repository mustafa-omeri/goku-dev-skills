#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministik Tema Kontrastı ve WCAG Uyumu Denetleyicisi (check_theme_contrast.py).

Neden var?
----------
Karanlık, aydınlık veya özel temalarda (ör. havalimanı kalkış panosu / board teması)
arka plan ile metin renkleri arasındaki kontrastın insan gözüyle görünmeyecek kadar
düşük kalması ("karanlık zemin üzerinde lacivert metin" veya "parlak zemin üzerinde
aşırı soluk metin"), otomasyon testleri (build/typecheck/unit) yeşil olsa dahi
ürünü kullanılamaz hale getirir.

Bu script; CSS dosyalarındaki (`:root`, `[data-theme="..."]`, `.dark`, `[data-mode="..."]`)
tema değişkenlerini, yüzeyleri ve metin renklerini sRGB / WCAG 2.1 formülüyle
matematiksel olarak inceler ve bağıl parlaklık (relative luminance) kontrast
oranını deterministik olarak denetler.

Kontroller
----------
E1 (low-contrast-primary)       Birincil metin kontrastı < 4.5:1 (WCAG AA normal metin ihlali)
E2 (low-contrast-muted)         İkincil/muted metin kontrastı < 3.0:1 (WCAG AA geniş metin/UI bileşeni ihlali)
E3 (hardcoded-body-contrast)    Tema seçicisinde gövde metnine verilen sabit rengin zeminle kontrastı < 4.5:1
W1 (sub-optimal-muted)          Muted metin kontrastı 3.0:1 - 4.5:1 arasında (Bilgilendirme; --strict ile hata)
W2 (low-contrast-faint)         Soluk/faint metin kontrastı < 2.5:1
W3 (selection-contrast)         Seçim vurgu rengi (::selection) kontrastı < 3.0:1

Çıkış Kodları:
- E1-E3 varsa: exit 1
- Yalnız W1-W3 varsa: exit 0 (varsayılan) / exit 1 (--strict bayrağıyla)
- CSS tema token'ı yoksa: kapsam dışı exit 0

Kullanım:
    python .agent/skills/musgoku/scripts/check_theme_contrast.py
    python .agent/skills/musgoku/scripts/check_theme_contrast.py --json
    python .agent/skills/musgoku/scripts/check_theme_contrast.py --strict
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSS_SEARCH_DIRS = ("src", "app", "styles", "pages", "components", "site", "ui", "assets")
IGNORE_DIRS = {
    "node_modules", "dist", "build", ".git", "coverage", ".next", ".astro",
    "__pycache__", ".pytest_cache", "target", "vendor", "public", ".agent"
}

# --- RENK VE MATEMATİKSEL WCAG HESAPLAMALARI ---

NAMED_COLORS: Dict[str, Tuple[int, int, int]] = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "transparent": (0, 0, 0),
    "slate-900": (15, 23, 42),
    "slate-950": (2, 6, 23),
    "slate-50": (248, 250, 252),
    "gray-900": (17, 24, 39),
    "gray-50": (249, 250, 251),
    "zinc-900": (24, 24, 27),
    "zinc-50": (250, 250, 250),
}


@dataclass
class ColorRGBA:
    r: int
    g: int
    b: int
    a: float = 1.0

    def composite_over(self, bg: "ColorRGBA") -> "ColorRGBA":
        """Alfa kanalı < 1 olan rengi zemin rengi üzerine harmanlar (Alpha compositing)."""
        if self.a >= 1.0:
            return self
        alpha = max(0.0, min(1.0, self.a))
        comp_r = round(self.r * alpha + bg.r * (1.0 - alpha))
        comp_g = round(self.g * alpha + bg.g * (1.0 - alpha))
        comp_b = round(self.b * alpha + bg.b * (1.0 - alpha))
        return ColorRGBA(r=comp_r, g=comp_g, b=comp_b, a=1.0)

    @property
    def hex(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"


def srgb_channel_to_linear(val: float) -> float:
    """WCAG 2.1 sRGB kanal normalizasyonu (0-1 arası)."""
    val = max(0.0, min(1.0, val))
    if val <= 0.04045:
        return val / 12.92
    return math.pow((val + 0.055) / 1.055, 2.4)


def relative_luminance(c: ColorRGBA) -> float:
    """WCAG 2.1 bağıl parlaklık (relative luminance) formülü."""
    r_lin = srgb_channel_to_linear(c.r / 255.0)
    g_lin = srgb_channel_to_linear(c.g / 255.0)
    b_lin = srgb_channel_to_linear(c.b / 255.0)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def calculate_contrast_ratio(c1: ColorRGBA, c2: ColorRGBA) -> float:
    """İki renk arasındaki kontrast oranını döndürür (1.0:1 ile 21.0:1 arası)."""
    eff_c1 = c1.composite_over(c2)
    lum1 = relative_luminance(eff_c1)
    lum2 = relative_luminance(c2)
    bright = max(lum1, lum2)
    dark = min(lum1, lum2)
    return (bright + 0.05) / (dark + 0.05)


def parse_color(raw_val: str, var_store: Optional[Dict[str, str]] = None) -> Optional[ColorRGBA]:
    """HEX, RGB, RGBA, HSL, HSLA veya var(...) dizgesini ColorRGBA nesnesine dönüştürür."""
    val = raw_val.strip()
    if not val:
        return None

    # var(--foo) referansı çözümleme
    var_match = re.match(r"""var\(\s*(--[a-zA-Z0-9_-]+)(?:\s*,\s*([^)]+))?\s*\)""", val)
    if var_match:
        var_name = var_match.group(1)
        fallback = var_match.group(2)
        if var_store and var_name in var_store:
            return parse_color(var_store[var_name], var_store)
        if fallback:
            return parse_color(fallback, var_store)
        return None

    # Hex (#RGB, #RGBA, #RRGGBB, #RRGGBBAA)
    hex_match = re.match(r"""^#([0-9a-fA-F]{3,8})$""", val)
    if hex_match:
        h = hex_match.group(1)
        if len(h) == 3:
            return ColorRGBA(int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16), 1.0)
        elif len(h) == 4:
            return ColorRGBA(int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16), int(h[3] * 2, 16) / 255.0)
        elif len(h) == 6:
            return ColorRGBA(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
        elif len(h) == 8:
            return ColorRGBA(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255.0)

    # rgb / rgba
    rgb_match = re.match(
        r"""^rgba?\(\s*(\d+)\s*[, ]\s*(\d+)\s*[, ]\s*(\d+)(?:\s*[/,]\s*([0-9.]+%?))?\s*\)$""",
        val,
        re.IGNORECASE,
    )
    if rgb_match:
        r = int(rgb_match.group(1))
        g = int(rgb_match.group(2))
        b = int(rgb_match.group(3))
        a_str = rgb_match.group(4)
        a = 1.0
        if a_str:
            if a_str.endswith("%"):
                a = float(a_str[:-1]) / 100.0
            else:
                a = float(a_str)
        return ColorRGBA(r, g, b, a)

    # hsl / hsla
    hsl_match = re.match(
        r"""^hsla?\(\s*([0-9.]+)(?:deg)?\s*[, ]\s*([0-9.]+)%\s*[, ]\s*([0-9.]+)%(?:\s*[/,]\s*([0-9.]+%?))?\s*\)$""",
        val,
        re.IGNORECASE,
    )
    if hsl_match:
        h = float(hsl_match.group(1)) % 360
        s = float(hsl_match.group(2)) / 100.0
        l = float(hsl_match.group(3)) / 100.0
        a_str = hsl_match.group(4)
        a = 1.0
        if a_str:
            if a_str.endswith("%"):
                a = float(a_str[:-1]) / 100.0
            else:
                a = float(a_str)
        r, g, b = hsl_to_rgb(h, s, l)
        return ColorRGBA(r, g, b, a)

    # Tailwind / shadcn formatı: "210 40% 98%"
    shadcn_match = re.match(r"""^([0-9.]+)\s+([0-9.]+)%\s+([0-9.]+)%$""", val)
    if shadcn_match:
        h = float(shadcn_match.group(1)) % 360
        s = float(shadcn_match.group(2)) / 100.0
        l = float(shadcn_match.group(3)) / 100.0
        r, g, b = hsl_to_rgb(h, s, l)
        return ColorRGBA(r, g, b, 1.0)

    # oklch(L% C H [/ A])
    oklch_match = re.match(
        r"""^oklch\(\s*([0-9.]+%?)\s+([0-9.]+%?)\s+([0-9.]+)(?:deg)?(?:\s*/\s*([0-9.]+%?))?\s*\)$""",
        val,
        re.IGNORECASE,
    )
    if oklch_match:
        l_str, c_str, h_str, a_str = oklch_match.group(1), oklch_match.group(2), oklch_match.group(3), oklch_match.group(4)
        L = float(l_str[:-1]) / 100.0 if l_str.endswith("%") else float(l_str)
        C = float(c_str[:-1]) * 0.4 / 100.0 if c_str.endswith("%") else float(c_str)
        H = float(h_str)
        alpha = 1.0
        if a_str:
            alpha = float(a_str[:-1]) / 100.0 if a_str.endswith("%") else float(a_str)
        h_rad = math.radians(H)
        a_lab = C * math.cos(h_rad)
        b_lab = C * math.sin(h_rad)
        l_ = L + 0.3963377774 * a_lab + 0.2158037573 * b_lab
        m_ = L - 0.1055613458 * a_lab - 0.0638541728 * b_lab
        s_ = L - 0.0894841775 * a_lab - 1.2914855480 * b_lab
        l_c, m_c, s_c = l_ ** 3, m_ ** 3, s_ ** 3
        r_lin = +4.0767416621 * l_c - 3.3077115913 * m_c + 0.2309699292 * s_c
        g_lin = -1.2684380046 * l_c + 2.6097574011 * m_c - 0.3413193965 * s_c
        b_lin = -0.0041960863 * l_c - 0.7034186147 * m_c + 1.7076147010 * s_c

        def _lin_to_byte(x: float) -> int:
            x = max(0.0, min(1.0, x))
            v = 12.92 * x if x <= 0.0031308 else 1.055 * math.pow(x, 1.0 / 2.4) - 0.055
            return round(max(0.0, min(1.0, v)) * 255.0)

        return ColorRGBA(_lin_to_byte(r_lin), _lin_to_byte(g_lin), _lin_to_byte(b_lin), alpha)

    # Named color
    low_val = val.lower()
    if low_val in NAMED_COLORS:
        r, g, b = NAMED_COLORS[low_val]
        return ColorRGBA(r, g, b, 1.0)

    return None


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """HSL değerlerini (0-360, 0-1, 0-1) RGB (0-255) değerlerine dönüştürür."""
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = l - c / 2.0
    r_prime, g_prime, b_prime = 0.0, 0.0, 0.0
    if 0 <= h < 60:
        r_prime, g_prime, b_prime = c, x, 0.0
    elif 60 <= h < 120:
        r_prime, g_prime, b_prime = x, c, 0.0
    elif 120 <= h < 180:
        r_prime, g_prime, b_prime = 0.0, c, x
    elif 180 <= h < 240:
        r_prime, g_prime, b_prime = 0.0, x, c
    elif 240 <= h < 300:
        r_prime, g_prime, b_prime = x, 0.0, c
    elif 300 <= h < 360:
        r_prime, g_prime, b_prime = c, 0.0, x
    r = round((r_prime + m) * 255.0)
    g = round((g_prime + m) * 255.0)
    b = round((b_prime + m) * 255.0)
    return r, g, b


# --- CSS AYRIŞTIRMA VE TEMA BLOKLARI ---

@dataclass
class ThemeBlock:
    selector: str
    file_path: Path
    line_number: int
    variables: Dict[str, str] = field(default_factory=dict)
    direct_bg: Optional[str] = None
    direct_color: Optional[str] = None


@dataclass
class Finding:
    code: str
    message: str
    file_path: Path
    line_number: int
    theme_selector: str
    bg_name: str
    text_name: str
    ratio: float
    required_ratio: float


def extract_theme_blocks(css_path: Path) -> List[ThemeBlock]:
    """CSS dosyasındaki (veya HTML <style> bloklarındaki) tema seçicilerini ve değişkenlerini çıkarır."""
    try:
        raw_file_content = css_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    chunks: List[Tuple[int, str]] = []
    if css_path.suffix.lower() in (".html", ".vue", ".svelte", ".astro"):
        for sm in re.finditer(r"""<style\b[^>]*>([\s\S]*?)</style>""", raw_file_content, re.IGNORECASE):
            base_ln = raw_file_content[: sm.start(1)].count("\n") + 1
            chunks.append((base_ln, sm.group(1)))
    else:
        chunks.append((1, raw_file_content))

    blocks: List[ThemeBlock] = []
    rule_re = re.compile(r"""([^{}]+)\{([^{}]+)\}""")

    for base_ln, content in chunks:
        clean_content = re.sub(r"""/\*[\s\S]*?\*/""", "", content)
        for m in rule_re.finditer(clean_content):
            raw_selector = m.group(1).strip()
            body = m.group(2).strip()
            line_num = base_ln + content[: m.start()].count("\n")

            is_theme_selector = bool(
                re.search(
                    r"""(?::root|\[data-theme[^\]]*\]|\[data-mode[^\]]*\]|\.dark|\.light|body\.dark|html\.dark)""",
                    raw_selector,
                )
            )
            if not is_theme_selector:
                continue

            vars_dict: Dict[str, str] = {}
            direct_bg = None
            direct_color = None

            for decl in body.split(";"):
                decl = decl.strip()
                if not decl or ":" not in decl:
                    continue
                prop, val = decl.split(":", 1)
                prop = prop.strip()
                val = val.strip()

                if prop.startswith("--"):
                    vars_dict[prop] = val
                elif prop in ("background-color", "background"):
                    direct_bg = val
                elif prop == "color":
                    direct_color = val

            if vars_dict or direct_bg or direct_color:
                blocks.append(
                    ThemeBlock(
                        selector=raw_selector,
                        file_path=css_path,
                        line_number=line_num,
                        variables=vars_dict,
                        direct_bg=direct_bg,
                        direct_color=direct_color,
                    )
                )

    return blocks


def categorize_variables(
    vars_dict: Dict[str, str],
) -> Tuple[List[str], List[str], List[str], List[str], Optional[Tuple[str, str]]]:
    """CSS değişkenlerini zemin, birincil metin, ikincil/muted, faint ve selection olarak sınıflandırır."""
    bg_candidates: List[str] = []
    primary_text: List[str] = []
    muted_text: List[str] = []
    faint_text: List[str] = []
    selection_pair: Optional[Tuple[str, str]] = None

    sel_bg = None
    sel_text = None

    for name in vars_dict.keys():
        low = name.lower()

        # Selection değişkenleri ayrıştırılır
        if "selection-bg" in low:
            sel_bg = name
            continue
        if "selection-text" in low:
            sel_text = name
            continue

        # Hariç tutulanlar
        if any(ex in low for ex in ("border", "line", "shadow", "glow", "radius", "font", "size", "caret", "accent", "on-", "inverse")):
            continue

        # Zemin adayları
        if any(bg in low for bg in ("background", "bg", "surface", "canvas", "card", "popover", "panel")):
            if not any(fg in low for fg in ("foreground", "ink", "text")):
                bg_candidates.append(name)
                continue

        # Faint metin
        if any(f in low for f in ("faint", "disabled", "placeholder")):
            faint_text.append(name)
            continue

        # Muted / İkincil metin
        if any(m in low for m in ("muted", "secondary", "tertiary")):
            muted_text.append(name)
            continue

        # Birincil metin
        if any(fg in low for fg in ("foreground", "ink", "text", "primary-text", "color-text", "ink-body")):
            primary_text.append(name)
            continue

    if sel_bg and sel_text:
        selection_pair = (sel_bg, sel_text)

    return bg_candidates, primary_text, muted_text, faint_text, selection_pair


def audit_theme_block(
    block: ThemeBlock,
    theme_hierarchy: Dict[str, Dict[str, str]],
    root_store: Dict[str, str],
    strict: bool = False,
) -> List[Finding]:
    """Bir tema bloğu içindeki renk çiftlerini denetler."""
    findings: List[Finding] = []

    # Bloğun ait olduğu tema önekini bul
    parent_theme_store = {}
    for t_name, t_vars in theme_hierarchy.items():
        if t_name in block.selector:
            parent_theme_store = t_vars
            break

    combined_store = {**root_store, **parent_theme_store, **block.variables}

    bg_vars, primary_vars, muted_vars, faint_vars, selection_pair = categorize_variables(block.variables)

    # Zemin adaylarını derle
    raw_bgs: List[Tuple[str, ColorRGBA]] = []
    base_opaque_bg: Optional[ColorRGBA] = None
    for bg_name in bg_vars:
        c = parse_color(block.variables[bg_name], combined_store)
        if c:
            if c.a >= 0.95 and base_opaque_bg is None:
                base_opaque_bg = c
            raw_bgs.append((bg_name, c))

    if block.direct_bg:
        c = parse_color(block.direct_bg, combined_store)
        if c:
            if c.a >= 0.95 and base_opaque_bg is None:
                base_opaque_bg = c
            raw_bgs.append(("direct-background", c))

    resolved_bgs: List[Tuple[str, ColorRGBA]] = []
    for bg_name, c in raw_bgs:
        if c.a < 1.0 and base_opaque_bg is not None:
            resolved_bgs.append((bg_name, c.composite_over(base_opaque_bg)))
        elif c.a >= 0.5:
            resolved_bgs.append((bg_name, c))

    # Eğer blokta açık zemin yoksa parent tema veya root'tan al
    if not resolved_bgs:
        for r_name in ("--background-color", "--background", "--color-base", "--color-canvas-base", "--theme-surface"):
            if r_name in combined_store:
                c = parse_color(combined_store[r_name], combined_store)
                if c:
                    resolved_bgs.append((f"inherited({r_name})", c))
                    break

    # 0. Selection pair denetimi
    if selection_pair:
        sel_bg_name, sel_text_name = selection_pair
        sel_bg_col = parse_color(block.variables[sel_bg_name], combined_store)
        sel_txt_col = parse_color(block.variables[sel_text_name], combined_store)
        if sel_bg_col and sel_txt_col:
            ratio = calculate_contrast_ratio(sel_txt_col, sel_bg_col)
            if ratio < 3.0:
                findings.append(
                    Finding(
                        code="W3",
                        message=(
                            f"Seçim vurgu renk çifti '{sel_text_name}' ({sel_txt_col.hex}) ve "
                            f"'{sel_bg_name}' ({sel_bg_col.hex}) arasındaki kontrast düşük ({ratio:.2f}:1 < 3.0:1)."
                        ),
                        file_path=block.file_path,
                        line_number=block.line_number,
                        theme_selector=block.selector,
                        bg_name=sel_bg_name,
                        text_name=sel_text_name,
                        ratio=ratio,
                        required_ratio=3.0,
                    )
                )

    if not resolved_bgs:
        return findings

    # Doğrudan gövdeye verilmiş sabit metin rengi kontrolü (sadece body seçicisi için)
    if block.direct_color and ("body" in block.selector or block.selector in (":root", ".dark", ".light")):
        text_color = parse_color(block.direct_color, combined_store)
        if text_color:
            for bg_name, bg_color in resolved_bgs:
                ratio = calculate_contrast_ratio(text_color, bg_color)
                if ratio < 4.5:
                    findings.append(
                        Finding(
                            code="E3",
                            message=(
                                f"Gövde seçicisinde tanımlanan sabit renk ({block.direct_color}) "
                                f"zemin ({bg_name}: {bg_color.hex}) üzerinde yetersiz kontrasta sahip "
                                f"({ratio:.2f}:1 < 4.5:1). Gece/aydınlık modlarında metin görünmez olur."
                            ),
                            file_path=block.file_path,
                            line_number=block.line_number,
                            theme_selector=block.selector,
                            bg_name=bg_name,
                            text_name="direct-color",
                            ratio=ratio,
                            required_ratio=4.5,
                        )
                    )

    # 1. Birincil Metin Kontrolleri (Min 4.5:1)
    for bg_name, bg_color in resolved_bgs:
        for p_name in primary_vars:
            t_color = parse_color(block.variables[p_name], combined_store)
            if not t_color:
                continue
            ratio = calculate_contrast_ratio(t_color, bg_color)
            if ratio < 4.5:
                findings.append(
                    Finding(
                        code="E1",
                        message=(
                            f"Birincil metin token'ı '{p_name}' ({t_color.hex}), "
                            f"'{bg_name}' ({bg_color.hex}) üzerinde WCAG AA sınırının altında "
                            f"({ratio:.2f}:1 < 4.5:1). Okunabilirlik kritik seviyede düşük."
                        ),
                        file_path=block.file_path,
                        line_number=block.line_number,
                        theme_selector=block.selector,
                        bg_name=bg_name,
                        text_name=p_name,
                        ratio=ratio,
                        required_ratio=4.5,
                    )
                )

    # 2. İkincil / Muted Metin Kontrolleri (Min 3.0:1)
    for bg_name, bg_color in resolved_bgs:
        for m_name in muted_vars:
            t_color = parse_color(block.variables[m_name], combined_store)
            if not t_color:
                continue
            ratio = calculate_contrast_ratio(t_color, bg_color)
            if ratio < 3.0:
                findings.append(
                    Finding(
                        code="E2",
                        message=(
                            f"İkincil/muted metin token'ı '{m_name}' ({t_color.hex}), "
                            f"'{bg_name}' ({bg_color.hex}) üzerinde WCAG minimum sınırının altında "
                            f"({ratio:.2f}:1 < 3.0:1). İkincil metin görünmez hale geliyor."
                        ),
                        file_path=block.file_path,
                        line_number=block.line_number,
                        theme_selector=block.selector,
                        bg_name=bg_name,
                        text_name=m_name,
                        ratio=ratio,
                        required_ratio=3.0,
                    )
                )
            elif ratio < 4.5:
                findings.append(
                    Finding(
                        code="W1",
                        message=(
                            f"Muted metin token'ı '{m_name}' ({t_color.hex}), "
                            f"'{bg_name}' ({bg_color.hex}) üzerinde {ratio:.2f}:1 kontrastında "
                            f"(3.0:1 sınırını geçiyor ancak 4.5:1 altında)."
                        ),
                        file_path=block.file_path,
                        line_number=block.line_number,
                        theme_selector=block.selector,
                        bg_name=bg_name,
                        text_name=m_name,
                        ratio=ratio,
                        required_ratio=3.0,
                    )
                )

    # 3. Faint / Disabled Metin Kontrolleri (Min 2.5:1)
    for bg_name, bg_color in resolved_bgs:
        for f_name in faint_vars:
            t_color = parse_color(block.variables[f_name], combined_store)
            if not t_color:
                continue
            ratio = calculate_contrast_ratio(t_color, bg_color)
            if ratio < 2.5:
                findings.append(
                    Finding(
                        code="W2",
                        message=(
                            f"Soluk/faint metin token'ı '{f_name}' ({t_color.hex}), "
                            f"'{bg_name}' ({bg_color.hex}) üzerinde aşırı düşük kontrastta ({ratio:.2f}:1 < 2.5:1)."
                        ),
                        file_path=block.file_path,
                        line_number=block.line_number,
                        theme_selector=block.selector,
                        bg_name=bg_name,
                        text_name=f_name,
                        ratio=ratio,
                        required_ratio=2.5,
                    )
                )

    return findings


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    script_path = Path(__file__).resolve()
    try:
        candidate = script_path.parents[4]
        if (candidate / ".agent").exists() or (candidate / "package.json").exists() or (candidate / "pom.xml").exists():
            return candidate
    except IndexError:
        pass
    return Path.cwd()


def collect_css_files(root: Path, include_agent: bool = False) -> List[Path]:
    """Taranacak CSS ve HTML dosyalarını toplar."""
    css_files: List[Path] = []
    effective_ignore = IGNORE_DIRS - {".agent"} if include_agent else IGNORE_DIRS
    for d in CSS_SEARCH_DIRS:
        target_dir = root / d
        if not target_dir.exists():
            continue
        for p in target_dir.rglob("*"):
            if p.suffix.lower() not in (".css", ".html", ".vue", ".svelte", ".astro"):
                continue
            if any(ign in p.parts for ign in effective_ignore):
                continue
            css_files.append(p)

    for p in root.glob("*"):
        if p.suffix.lower() not in (".css", ".html"):
            continue
        if any(ign in p.parts for ign in effective_ignore):
            continue
        css_files.append(p)

    if include_agent:
        agent_dir = root / ".agent"
        if agent_dir.is_dir():
            for p in sorted(agent_dir.glob("*.html")):
                if p.is_file():
                    css_files.append(p)

    return sorted(set(css_files))


def check(
    root: Path,
    strict: bool = False,
    specific_files: Optional[List[Path]] = None,
    include_agent: bool = False,
) -> Tuple[List[Finding], List[Finding], int, int]:
    """Tüm projeyi denetler."""
    if specific_files:
        css_files = [f.resolve() for f in specific_files if f.is_file()]
    else:
        css_files = collect_css_files(root, include_agent=include_agent)
    if not css_files:
        return [], [], 0, 0

    all_blocks: List[ThemeBlock] = []
    for f in css_files:
        all_blocks.extend(extract_theme_blocks(f))

    if not all_blocks:
        return [], [], 0, 0

    root_store: Dict[str, str] = {}
    theme_hierarchy: Dict[str, Dict[str, str]] = {}

    # 1. Ana tema depolarını oluştur
    for b in all_blocks:
        if ":root" in b.selector:
            root_store.update(b.variables)
        theme_match = re.search(r"""\[data-theme=["']?([a-zA-Z0-9_-]+)["']?\]""", b.selector)
        if theme_match and not any(tag in b.selector for tag in ("h1", "h2", "h3", "body", "p", "div")):
            theme_name = theme_match.group(1)
            theme_hierarchy[f'[data-theme="{theme_name}"]'] = b.variables
            theme_hierarchy[f"[data-theme='{theme_name}']"] = b.variables

    errors: List[Finding] = []
    warnings: List[Finding] = []
    checked_pairs = 0

    for b in all_blocks:
        block_findings = audit_theme_block(b, theme_hierarchy, root_store, strict=strict)
        for f in block_findings:
            if f.code.startswith("E") or (strict and f.code.startswith("W")):
                errors.append(f)
            else:
                warnings.append(f)
        bg_vars, p_vars, m_vars, f_vars, _ = categorize_variables(b.variables)
        checked_pairs += len(bg_vars) * (len(p_vars) + len(m_vars) + len(f_vars))

    return errors, warnings, len(all_blocks), checked_pairs


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministik Tema Kontrastı ve WCAG Uyumu Denetleyicisi")
    parser.add_argument("--root", type=Path, default=None, help="Proje kök dizini")
    parser.add_argument("--file", type=Path, action="append", default=None, help="Denetlenecek spesifik dosya yolu")
    parser.add_argument("--include-agent", action="store_true", help=".agent klasörü altındaki HTML dosyalarını da tarar")
    parser.add_argument("--strict", action="store_true", help="W1-W3 uyarılarını da hata sayarak exit 1 ver")
    parser.add_argument("--json", action="store_true", help="Sonuçları JSON formatında bas")
    args = parser.parse_args()

    root = args.root.resolve() if args.root else find_project_root()
    errors, warnings, block_count, pair_count = check(
        root,
        strict=args.strict,
        specific_files=args.file,
        include_agent=args.include_agent,
    )

    if block_count == 0:
        if args.json:
            print(json.dumps({"status": "kapsam_disi", "blocks": 0, "errors": [], "warnings": []}))
        else:
            print("[Kapsam dışı] CSS tema bloğu veya değişkeni bulunamadı. Kapı atlandı.")
        return 0

    if args.json:
        data = {
            "status": "fail" if errors else "pass",
            "blocks": block_count,
            "checked_pairs": pair_count,
            "errors": [
                {
                    "code": f.code,
                    "message": f.message,
                    "file": str(f.file_path.relative_to(root)),
                    "line": f.line_number,
                    "selector": f.theme_selector,
                    "ratio": f.ratio,
                }
                for f in errors
            ],
            "warnings": [
                {
                    "code": f.code,
                    "message": f.message,
                    "file": str(f.file_path.relative_to(root)),
                    "line": f.line_number,
                    "selector": f.theme_selector,
                    "ratio": f.ratio,
                }
                for f in warnings
            ],
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 1 if errors else 0

    print("=" * 60)
    print("Deterministik Tema Kontrastı ve WCAG Uyumu Denetleyicisi")
    print("=" * 60)
    print(f"Taranan tema bloğu : {block_count}")
    print(f"Denetlenen renk çifti: ~{pair_count}")
    print("-" * 60)

    if not errors and not warnings:
        print("[OK] Tüm tema token'ları ve renk kontrastları WCAG standartlarına uygun!")
        return 0

    if warnings:
        print(f"\n⚠️  UYARILAR ({len(warnings)}):")
        for w in warnings:
            rel = w.file_path.relative_to(root)
            print(f"  [{w.code}] {rel}:{w.line_number} ({w.theme_selector}) -> {w.message}")

    if errors:
        print(f"\n❌ HATALAR ({len(errors)}):")
        for e in errors:
            rel = e.file_path.relative_to(root)
            print(f"  [{e.code}] {rel}:{e.line_number} ({e.theme_selector}) -> {e.message}")
        print("\nSONUÇ: Tema kontrast ihlalleri tespit edildi. Lütfen renk token'larını düzeltin.")
        return 1

    print("\n[OK] Kritik hata yok. Renk kontrastları kabul edilebilir seviyede.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
