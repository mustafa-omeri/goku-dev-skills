#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministik Tasarım Sözleşmesi (DESIGN.md) ve Kod Uyumu Denetleyicisi (check_design_contract.py).

Neden var?
----------
`design-skills-enforcement.md` §2.8 "Çift Katmanlı Proje Belleği Standardı"
her UI projesinin kendi `<repo-kök>/DESIGN.md` sözleşmesine sahip olmasını ve
sonraki tüm tasarım/UI çalışmalarının bu sözleşmeden ilerlemesini zorunlu kılar.

Mevcut (brownfield) projelerde `DESIGN.md` yoksa önce mevcut tasarım değiştirilmeden
`mode: baseline` olarak çıkarılır; sıfır veya yeniden tasarlanan projelerde ise
`mode: crafted | redesign` olarak kreatif yön ve token sözleşmesi mühürlenir.

Kontroller
----------
W0 / E1 (missing-design-contract)       UI dosyası var ancak DESIGN.md yok (varsayılan W0 uyarı; --strict ile E1 hata)
E2 (missing-required-tokens)            DESIGN.md frontmatter içinde zorunlu token anahtarları eksik
E3 (template-placeholder-or-anchor)     Şablon yer tutucuları (<doldur, [Tasarım Sistemi Adı]) veya kopyalanmış şablon parmak izi
E4 (wcag-token-contrast)                DESIGN.md içinde beyan edilen metin/zemin token çiftleri WCAG AA sınırının altında
E5 (undeclared-font-or-color-drift)     Kodda DESIGN.md içinde beyan edilmemiş font ailesi kullanımı
E6 (typography-ceiling-or-mono-leak)    Mono fontun izin verilen seçiciler (code/pre/kbd/samp + allowedSelectors) dışında kullanımı
W1 (missing-rejected-defaults)          mode: crafted/redesign iken "Reddedilen Varsayılanlar" tablosunun eksik olması
W2 (missing-project-evidence)           "0. Proje Kanıtı" bölümünün eksik olması

Kullanım:
    python .agent/skills/musgoku/scripts/check_design_contract.py
    python .agent/skills/musgoku/scripts/check_design_contract.py --strict
    python .agent/skills/musgoku/scripts/check_design_contract.py --include-agent
    python .agent/skills/musgoku/scripts/check_design_contract.py --file .agent/skills-catalog.html
    python .agent/skills/musgoku/scripts/check_design_contract.py --json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from check_theme_contrast import ColorRGBA, calculate_contrast_ratio, parse_color  # noqa: E402

FRONTEND_DIRS = ("src", "app", "pages", "components", "site", "views", "ui")
FRONTEND_EXTS = (".tsx", ".jsx", ".html", ".vue", ".svelte", ".astro", ".css")
IGNORE_DIRS = {
    "node_modules", "dist", "build", ".git", "coverage", ".next", ".astro",
    "__pycache__", ".pytest_cache", "target", "vendor", "public"
}

REQUIRED_COLOR_KEYS = (
    "primary",
    "surface-ground",
    "surface-raised",
    "text-primary",
    "text-body",
    "text-muted",
    "border-subtle",
)
REQUIRED_TYPO_KEYS = ("scale", "body", "display")

GENERIC_FONT_KEYWORDS = {
    "sans-serif", "serif", "monospace", "system-ui", "-apple-system",
    "blinkmacsystemfont", "segoe ui", "roboto", "helvetica neue", "helvetica",
    "arial", "noto sans", "liberation sans", "apple color emoji",
    "segoe ui emoji", "segoe ui symbol", "noto color emoji", "ui-sans-serif",
    "ui-monospace", "ui-serif", "cursive", "fantasy", "inherit", "initial",
    "unset", "revert", "oxygen", "ubuntu", "cantarell", "fira sans", "droid sans",
    "sfmono-regular", "menlo", "monaco", "consolas", "liberation mono", "courier new"
}

DEFAULT_MONO_ALLOWED = {"code", "pre", "kbd", "samp"}


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


def _linear_to_srgb_byte(x: float) -> int:
    x = max(0.0, min(1.0, x))
    if x <= 0.0031308:
        val = 12.92 * x
    else:
        val = 1.055 * math.pow(x, 1.0 / 2.4) - 0.055
    return round(max(0.0, min(1.0, val)) * 255.0)


def parse_oklch_to_rgba(raw: str) -> Optional[ColorRGBA]:
    """oklch(L% C H [/ A]) dizgesini sRGB ColorRGBA nesnesine dönüştürür."""
    val = raw.strip()
    m = re.match(
        r"""^oklch\(\s*([0-9.]+%?)\s+([0-9.]+%?)\s+([0-9.]+)(?:deg)?(?:\s*/\s*([0-9.]+%?))?\s*\)$""",
        val,
        re.IGNORECASE,
    )
    if not m:
        return None

    l_str, c_str, h_str, a_str = m.group(1), m.group(2), m.group(3), m.group(4)
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

    l_cube = l_ * l_ * l_
    m_cube = m_ * m_ * m_
    s_cube = s_ * s_ * s_

    r_lin = +4.0767416621 * l_cube - 3.3077115913 * m_cube + 0.2309699292 * s_cube
    g_lin = -1.2684380046 * l_cube + 2.6097574011 * m_cube - 0.3413193965 * s_cube
    b_lin = -0.0041960863 * l_cube - 0.7034186147 * m_cube + 1.7076147010 * s_cube

    return ColorRGBA(
        r=_linear_to_srgb_byte(r_lin),
        g=_linear_to_srgb_byte(g_lin),
        b=_linear_to_srgb_byte(b_lin),
        a=alpha,
    )


def resolve_any_color(raw: str) -> Optional[ColorRGBA]:
    if not raw or not isinstance(raw, str):
        return None
    val = raw.strip().strip("\"'")
    if val.lower().startswith("oklch("):
        return parse_oklch_to_rgba(val)
    return parse_color(val)


def _strip_inline_comment(val: str) -> str:
    """Tırnak dışındaki # yorumlarını temizler."""
    in_single = False
    in_double = False
    for idx, ch in enumerate(val):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if idx == 0 or val[idx - 1].isspace():
                return val[:idx].strip()
    return val.strip()


def _parse_scalar_or_list(raw_val: str) -> Any:
    cleaned = _strip_inline_comment(raw_val).strip()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        inner = cleaned[1:-1].strip()
        if not inner:
            return []
        items = []
        for part in inner.split(","):
            p = part.strip().strip("\"'")
            if p:
                items.append(p)
        return items
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in ("'", '"'):
        return cleaned[1:-1]
    return cleaned


def parse_design_md(path: Path) -> Tuple[Dict[str, Any], str]:
    """DESIGN.md dosyasının YAML frontmatter ve gövdesini bağımlılıksız ayrıştırır."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    if raw.startswith("\ufeff"):
        raw = raw[1:]
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, raw

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, raw

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])

    root_dict: Dict[str, Any] = {}
    stack: List[Tuple[int, Dict[str, Any]]] = [(-1, root_dict)]

    for line in fm_lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped:
            continue
        key_part, _, val_part = stripped.partition(":")
        key = key_part.strip().strip("\"'")
        val_str = val_part.strip()

        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        current_parent = stack[-1][1]
        if not val_str or val_str.startswith("#"):
            new_map: Dict[str, Any] = {}
            current_parent[key] = new_map
            stack.append((indent, new_map))
        else:
            current_parent[key] = _parse_scalar_or_list(val_str)

    return root_dict, body


def iter_ui_files(root: Path, include_agent: bool = False) -> List[Path]:
    found: List[Path] = []
    for folder in FRONTEND_DIRS:
        base = root / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in FRONTEND_EXTS:
                continue
            if any(part in IGNORE_DIRS for part in path.parts):
                continue
            if not include_agent and ".agent" in path.parts:
                continue
            stem_low = path.stem.lower()
            if stem_low.endswith(".test") or stem_low.endswith(".spec") or "__tests__" in path.parts:
                continue
            found.append(path)

    if not found:
        for path in sorted(root.glob("*")):
            if path.is_file() and path.suffix.lower() in (".html", ".astro", ".svelte", ".vue", ".css"):
                found.append(path)

    if include_agent:
        agent_dir = root / ".agent"
        if agent_dir.is_dir():
            for path in sorted(agent_dir.glob("*.html")):
                if path.is_file():
                    found.append(path)

    return found


def _extract_declared_fonts(typo: Dict[str, Any]) -> Tuple[set[str], set[str], List[str]]:
    """(all_declared_font_names_lower, mono_font_names_lower, mono_allowed_selectors)"""
    declared: set[str] = set()
    mono_fonts: set[str] = set()
    allowed_selectors = list(DEFAULT_MONO_ALLOWED)

    for role in ("display", "headline", "body", "code", "mono"):
        role_obj = typo.get(role)
        if not isinstance(role_obj, dict):
            continue
        ff = role_obj.get("fontFamily", "")
        if isinstance(ff, str) and ff:
            for part in ff.split(","):
                clean = part.strip().strip("\"'").lower()
                if clean and clean not in GENERIC_FONT_KEYWORDS and not clean.startswith("<doldur"):
                    declared.add(clean)
                    if role in ("code", "mono"):
                        mono_fonts.add(clean)
        if role in ("code", "mono"):
            extra_sel = role_obj.get("allowedSelectors") or role_obj.get("code-roles")
            if isinstance(extra_sel, list):
                for s in extra_sel:
                    if isinstance(s, str) and s.strip():
                        allowed_selectors.append(s.strip())

    return declared, mono_fonts, allowed_selectors


def _extract_css_chunks(path: Path) -> List[Tuple[int, str]]:
    """Dosya .css ise tamamını, .html/.vue/.svelte ise <style> bloklarını (başlangıç satırı, içerik) döndürür."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    if path.suffix.lower() == ".css":
        return [(1, content)]

    chunks: List[Tuple[int, str]] = []
    for m in re.finditer(r"""<style\b[^>]*>([\s\S]*?)</style>""", content, re.IGNORECASE):
        start_line = content[: m.start(1)].count("\n") + 1
        chunks.append((start_line, m.group(1)))
    return chunks


def _selector_is_mono_allowed(selector_group: str, allowed_selectors: List[str]) -> bool:
    """Seçici grubundaki her bir virgüllü seçici izin verilen mono seçicilerinden biriyle eşleşiyor mu?"""
    parts = [p.strip() for p in selector_group.split(",") if p.strip()]
    if not parts:
        return True
    for sel in parts:
        if sel.startswith("@") or sel in (":root", ".dark", ".light") or sel.startswith("[data-theme"):
            continue
        sel_tokens = set(re.split(r"""[\s>+~]+""", sel))
        matched = False
        for allow in allowed_selectors:
            allow_clean = allow.strip()
            if not allow_clean:
                continue
            if allow_clean in sel_tokens or sel.endswith(allow_clean) or allow_clean in sel:
                matched = True
                break
        if not matched:
            return False
    return True


def run_checks(
    root: Path,
    specific_files: Optional[List[Path]] = None,
    include_agent: bool = False,
    strict: bool = False,
) -> Dict[str, Any]:
    design_md_path = root / "DESIGN.md"
    has_design_md = design_md_path.is_file()

    if specific_files:
        ui_files = [f.resolve() for f in specific_files if f.is_file()]
    else:
        ui_files = iter_ui_files(root, include_agent=include_agent)

    if not ui_files and not has_design_md:
        return {
            "scope": "out_of_scope",
            "project_root": str(root),
            "mode": "none",
            "files_scanned": 0,
            "errors": [],
            "warnings": [],
            "status": "OK",
            "exit": 0,
        }

    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    if not has_design_md:
        msg = (
            "Proje arayüz dosyaları içeriyor ancak kök dizinde DESIGN.md sözleşmesi bulunamadı. "
            "Mevcut projelerde tasarımı değiştirmeden önce '/ui-polish --baseline' ile mevcut "
            "tasarımı DESIGN.md (mode: baseline) olarak kayıt altına alın."
        )
        if strict:
            errors.append({
                "code": "E1",
                "rule": "missing-design-contract",
                "file": "DESIGN.md",
                "line": 1,
                "message": msg,
            })
        else:
            warnings.append({
                "code": "W0",
                "rule": "missing-design-contract-brownfield",
                "file": "DESIGN.md",
                "line": 1,
                "message": msg,
            })
        return {
            "scope": "in_scope",
            "project_root": str(root),
            "mode": "missing",
            "files_scanned": len(ui_files),
            "errors": errors,
            "warnings": warnings,
            "status": "FAIL" if errors else "OK",
            "exit": 1 if errors else 0,
        }

    fm, body = parse_design_md(design_md_path)
    raw_text = design_md_path.read_text(encoding="utf-8", errors="replace")
    mode = str(fm.get("mode", "crafted")).strip().lower()

    # E3: Template placeholder or copied template fingerprint check
    placeholder_hits = []
    if "<doldur" in raw_text:
        placeholder_hits.append("<doldur:...>")
    if "[Tasarım Sistemi Adı]" in raw_text or "[Proje Adı]" in raw_text:
        placeholder_hits.append("[Tasarım Sistemi Adı]")
    if "oklch(84% 0.19 80)" in raw_text and "oklch(7% 0.006 95)" in raw_text:
        placeholder_hits.append("kopyalanmış eski şablon parmak izi (oklch(84% 0.19 80))")

    if placeholder_hits:
        errors.append({
            "code": "E3",
            "rule": "template-placeholder-or-anchor",
            "file": "DESIGN.md",
            "line": 1,
            "message": f"DESIGN.md içinde doldurulmamış şablon yer tutucusu veya kopya çapa tespit edildi: {', '.join(placeholder_hits)}",
        })

    # E2: Required keys in frontmatter
    colors = fm.get("colors") if isinstance(fm.get("colors"), dict) else {}
    typo = fm.get("typography") if isinstance(fm.get("typography"), dict) else {}
    rounded = fm.get("rounded") if isinstance(fm.get("rounded"), dict) else {}
    spacing = fm.get("spacing") if isinstance(fm.get("spacing"), dict) else {}

    missing_keys: List[str] = []
    for k in REQUIRED_COLOR_KEYS:
        if k not in colors or not colors.get(k):
            missing_keys.append(f"colors.{k}")
    for k in REQUIRED_TYPO_KEYS:
        if k not in typo or not typo.get(k):
            missing_keys.append(f"typography.{k}")
    if not rounded:
        missing_keys.append("rounded")
    if not spacing:
        missing_keys.append("spacing")

    if missing_keys:
        errors.append({
            "code": "E2",
            "rule": "missing-required-tokens",
            "file": "DESIGN.md",
            "line": 1,
            "message": f"DESIGN.md frontmatter içinde zorunlu token anahtarları eksik: {', '.join(missing_keys)}",
        })

    # E4: WCAG contrast check on declared surface/text tokens
    if colors and not placeholder_hits:
        surfaces = []
        for s_key in ("surface-ground", "surface-raised"):
            raw_s = colors.get(s_key)
            c_s = resolve_any_color(str(raw_s)) if raw_s else None
            if c_s:
                surfaces.append((s_key, c_s))

        for s_key, s_col in surfaces:
            for t_key, min_ratio in (("text-primary", 4.5), ("text-body", 4.5), ("text-muted", 3.0)):
                raw_t = colors.get(t_key)
                c_t = resolve_any_color(str(raw_t)) if raw_t else None
                if not c_t:
                    continue
                ratio = calculate_contrast_ratio(c_t, s_col)
                if ratio < min_ratio:
                    errors.append({
                        "code": "E4",
                        "rule": "wcag-token-contrast",
                        "file": "DESIGN.md",
                        "line": 1,
                        "message": (
                            f"DESIGN.md token kontrast ihlali: '{t_key}' ({raw_t}) ile '{s_key}' ({raw_s}) "
                            f"arasındaki kontrast {ratio:.2f}:1 (minimum {min_ratio:.1f}:1 olmalı)."
                        ),
                    })

    # W1 & W2: Body sections
    if "## 0. Proje Kanıtı" not in body and "## 0." not in body:
        warnings.append({
            "code": "W2",
            "rule": "missing-project-evidence",
            "file": "DESIGN.md",
            "line": 1,
            "message": "DESIGN.md içinde '## 0. Proje Kanıtı' bölümü eksik.",
        })

    if mode not in ("baseline", "<doldur: baseline | crafted | redesign>"):
        rej_match = re.search(r"""##\s+3\.\s+Reddedilen Varsayılanlar([\s\S]*?)(?:\n##\s+|\Z)""", body)
        if not rej_match:
            warnings.append({
                "code": "W1",
                "rule": "missing-rejected-defaults",
                "file": "DESIGN.md",
                "line": 1,
                "message": "mode: crafted/redesign iken '## 3. Reddedilen Varsayılanlar' bölümü zorunludur.",
            })
        else:
            sec_text = rej_match.group(1)
            table_rows = [
                ln for ln in sec_text.splitlines()
                if ln.strip().startswith("|") and "---" not in ln and "Reddedilen Aday" not in ln
            ]
            if len(table_rows) < 1:
                warnings.append({
                    "code": "W1",
                    "rule": "missing-rejected-defaults",
                    "file": "DESIGN.md",
                    "line": 1,
                    "message": "'## 3. Reddedilen Varsayılanlar' tablosunda en az 1 reddedilen varsayılan gerekçesi bulunmalıdır.",
                })

    # E5 & E6: Scan UI/CSS files for undeclared fonts and mono font leaks
    declared_fonts, mono_fonts, mono_allowed_selectors = _extract_declared_fonts(typo)

    rule_re = re.compile(r"""([^{}]+)\{([^{}]+)\}""")
    font_decl_re = re.compile(r"""font-family\s*:\s*([^;]+)""", re.IGNORECASE)

    for ui_path in ui_files:
        rel_file = os.path.relpath(ui_path, root).replace("\\", "/")
        for base_line, css_text in _extract_css_chunks(ui_path):
            clean_css = re.sub(r"""/\*[\s\S]*?\*/""", "", css_text)
            for m in rule_re.finditer(clean_css):
                selector = m.group(1).strip()
                decl_body = m.group(2)
                rule_line = base_line + css_text[: m.start()].count("\n")

                for fm_match in font_decl_re.finditer(decl_body):
                    ff_val = fm_match.group(1).strip()

                    # Check if this declaration is a CSS variable definition (--font-...: ...)
                    # Look backwards in decl_body before fm_match
                    prefix_text = decl_body[: fm_match.start()]
                    last_semi = prefix_text.rfind(";")
                    stmt_prefix = prefix_text[last_semi + 1 :].strip()
                    if stmt_prefix.startswith("--"):
                        continue

                    # E6: Check if mono font is used outside allowed selectors
                    uses_mono_var = bool(re.search(r"""var\(\s*--font-(?:mono|code)\b""", ff_val))
                    uses_mono_family = any(mf in ff_val.lower() for mf in mono_fonts) or (
                        "monospace" in ff_val.lower() and not uses_mono_var
                    )
                    if uses_mono_var or uses_mono_family:
                        if not _selector_is_mono_allowed(selector, mono_allowed_selectors):
                            errors.append({
                                "code": "E6",
                                "rule": "typography-ceiling-or-mono-leak",
                                "file": rel_file,
                                "line": rule_line,
                                "message": (
                                    f"Monospace yazı tipi ('{ff_val}') izin verilen kod/komut seçicileri "
                                    f"dışında kullanıldı: '{selector}'. Yalnızca {', '.join(mono_allowed_selectors[:6])} "
                                    f"veya DESIGN.md allowedSelectors listesinde kullanılabilir."
                                ),
                            })

                    # E5: If literal font family names are used (not var(--...)), verify they are declared in DESIGN.md
                    if not ff_val.startswith("var(") and declared_fonts:
                        for part in ff_val.split(","):
                            part_no_imp = re.sub(r"""\s*!important\s*$""", "", part.strip(), flags=re.IGNORECASE)
                            cand = part_no_imp.strip().strip("\"'").lower()
                            if (
                                not cand
                                or cand in GENERIC_FONT_KEYWORDS
                                or cand.startswith("var(")
                            ):
                                continue
                            if cand not in declared_fonts:
                                errors.append({
                                    "code": "E5",
                                    "rule": "undeclared-font-or-color-drift",
                                    "file": rel_file,
                                    "line": rule_line,
                                    "message": (
                                        f"Kodda kullanılan yazı tipi ailesi ('{part_no_imp.strip()}') "
                                        f"DESIGN.md typography bölümünde beyan edilmemiş (Beyan edilenler: {sorted(declared_fonts)})."
                                    ),
                                })

    exit_code = 1 if errors or (strict and warnings) else 0
    return {
        "scope": "in_scope",
        "project_root": str(root),
        "mode": mode,
        "files_scanned": len(ui_files),
        "errors": errors,
        "warnings": warnings,
        "status": "FAIL" if exit_code == 1 else "OK",
        "exit": exit_code,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministik Tasarım Sözleşmesi (DESIGN.md) Denetleyicisi")
    parser.add_argument("--path", type=str, default=None, help="Proje kök dizini")
    parser.add_argument("--file", type=str, action="append", default=None, help="Denetlenecek spesifik dosya yolu")
    parser.add_argument("--include-agent", action="store_true", help=".agent altındaki HTML dosyalarını taramaya dahil et")
    parser.add_argument("--strict", action="store_true", help="Uyarıları (W0-W2) da hata sayarak exit 1 döndür")
    parser.add_argument("--json", action="store_true", help="JSON çıktısı üret")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve() if args.path else find_project_root()
    specific_files = [Path(f) for f in args.file] if args.file else None

    res = run_checks(root, specific_files=specific_files, include_agent=args.include_agent, strict=args.strict)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return res["exit"]

    if res["scope"] == "out_of_scope":
        print(f"[Kapsam dışı] {root} altında UI dosyası veya DESIGN.md bulunamadı · [OK]")
        return 0

    print(f"Tasarım Sözleşmesi Denetimi (Mod: {res['mode']} · Taranan UI dosyası: {res['files_scanned']})")
    for err in res["errors"]:
        print(f"  ❌ [{err['code']} - {err['rule']}] {err['file']}:{err['line']} -> {err['message']}")
    for warn in res["warnings"]:
        print(f"  ⚠️  [{warn['code']} - {warn['rule']}] {warn['file']}:{warn['line']} -> {warn['message']}")

    if res["exit"] == 0:
        print(f"SONUÇ: {len(res['errors'])} hata · {len(res['warnings'])} uyarı · [OK]")
    else:
        print(f"SONUÇ: {len(res['errors'])} hata · {len(res['warnings'])} uyarı · [FAIL]")
    return res["exit"]


if __name__ == "__main__":
    sys.exit(main())
