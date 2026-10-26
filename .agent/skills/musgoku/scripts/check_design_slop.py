#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministik Tasarım Zanaat Tabanı ve Anti-Slop Denetleyicisi (check_design_slop.py).

Neden var?
----------
`design-skills-enforcement.md` §2.6 "Tasarım Zanaat Tabanı ve Kesin Yasaklar"
(Craft Floor & Hard Refusals) kuralı; iç içe kartları, gradyan metinleri,
kalın yan şeritleri (border-l-4), sıfır-blur ofset blok gölgeleri, renkli
zeminlerde ham gri metinleri, başlık üstü gereksiz kicker/eyebrow haplarını,
ham emoji/unicode ikonları ve token dışı ham hex renklerini kesin olarak yasaklar.

Bu script, kaynak kodda (JSX, TSX, HTML, Vue, Svelte, Astro, CSS) bu yasaklı
yapay zeka klişelerini (AI slop) deterministik regex ve AST kalıplarıyla denetler.

Kontroller
----------
E1 (nested-card)            İç içe kart (Card içinde Card veya .card içinde card/border-rounded)
E2 (gradient-text)          Gradyan metin (bg-clip-text, text-transparent bg-gradient-, background-clip: text)
E3 (side-accent)            Yuvarlatılmış kartta kalın renkli kenar şeridi (border-l-4 vb. + rounded)
E4 (block-shadow)           Sıfır-blur ofset blok gölge (box-shadow: 4px 4px 0, shadow-[4px_4px_0px...])
E5 (gray-on-color)          Renkli/kromatik zeminde ham gri metin (bg-blue/indigo/... + text-gray/slate/zinc)
E6 (display-fallback)       Display fontta generic/sistem fontu (Impact, Comic Sans veya eksik fallback)
E7 (eyebrow-spam)           Başlık üstü büyük harfli süs hapı (uppercase tracking-widest kicker + h1/h2)
E8 (emoji-icon)             İkon, buton veya rozet olarak ham emoji/unicode kullanımı (§2.6 A.8)
E9 (hardcoded-palette)      Inline style veya kuralda token dışı ham hex kodu kullanımı (§2.6 A.7)
W1 (missing-tabular-nums)   Tablo veya sayaç/istatistik rakamlarında tabular-nums eksikliği

Çıkış Kodları:
- E1-E9 varsa: exit 1
- Yalnız W1 varsa: exit 0 (varsayılan) / exit 1 (--strict bayrağıyla)
- Frontend kodu yoksa: kapsam dışı exit 0

Kullanım:
    python .agent/skills/musgoku/scripts/check_design_slop.py
    python .agent/skills/musgoku/scripts/check_design_slop.py --json
    python .agent/skills/musgoku/scripts/check_design_slop.py --strict
    python .agent/skills/musgoku/scripts/check_design_slop.py --file path/to/file.html
    python .agent/skills/musgoku/scripts/check_design_slop.py --include-agent
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

FRONTEND_DIRS = ("src", "app", "pages", "components", "site", "views", "ui")
FRONTEND_EXTS = (".tsx", ".jsx", ".html", ".vue", ".svelte", ".astro", ".css")
IGNORE_DIRS = {
    "node_modules", "dist", "build", ".git", "coverage", ".next", ".astro",
    "__pycache__", ".pytest_cache", "target", "vendor", "public"
}

# --- REGEX KALIPLARI ---

# E1: Nested Card (Card bileşeni içinde başka bir Card bileşeni)
CARD_TAG_RE = re.compile(r"""<(/)?([a-zA-Z0-9]*Card[a-zA-Z0-9]*)\b([^>]*)(/)?>""")
CARD_PARTS = {
    "CardHeader", "CardContent", "CardFooter", "CardTitle",
    "CardDescription", "CardAction", "CardImage", "CardBody"
}

# E2: Gradient Text
GRADIENT_TEXT_TW_RE = re.compile(
    r"""\b(?:bg-clip-text\s+[^"'>`]*\btext-transparent|text-transparent\s+[^"'>`]*\bbg-clip-text)\b"""
)
GRADIENT_TEXT_CSS_RE = re.compile(
    r"""(?:-webkit-background-clip:\s*text|background-clip:\s*text)[\s\S]*?(?:color:\s*transparent|-webkit-text-fill-color:\s*transparent)"""
)

# E3: Side Accent on Rounded Card (border-l-4 veya benzeri ile rounded- aynı sınıf kümesinde)
SIDE_ACCENT_TW_RE = re.compile(
    r"""\b(?=.*?\b(?:border-[lr][-_]?(?:[2-8]|4px|8px)|border-[tb][-_]?(?:[2-8]|4px|8px))\b)(?=.*?\brounded(?:-[a-z0-9]+)?\b)[^"'>`]*"""
)
SIDE_ACCENT_CSS_RE = re.compile(
    r"""(?:border-(?:left|right|top|bottom)(?:-width)?:\s*(?:[2-9]px|[1-9][0-9]+px)[\s\S]*?border-radius:\s*[1-9]|border-radius:\s*[1-9][\s\S]*?border-(?:left|right|top|bottom)(?:-width)?:\s*(?:[2-9]px|[1-9][0-9]+px))"""
)

# E4: Zero-blur offset block shadow
BLOCK_SHADOW_TW_RE = re.compile(
    r"""\bshadow-\[(?:-?\d+px_){2}0(?:px)?(?:_[^\]]+)?\]"""
)
BLOCK_SHADOW_CSS_RE = re.compile(
    r"""box-shadow:\s*(?:-?\d+px\s+){2}0(?:px)?(?:\s+[^;]+)?;"""
)

# E5: Raw gray on chromatic background
CHROMATIC_BG_RE = re.compile(
    r"""\bbg-(?:blue|indigo|purple|violet|emerald|teal|cyan|rose|pink|amber|orange)-(?:500|600|700|800|900|950)\b"""
)
RAW_GRAY_TEXT_RE = re.compile(
    r"""\btext-(?:gray|slate|zinc|neutral|stone)-(?:400|500|600)\b"""
)

# E6: System display fallback or banned font
BANNED_FONTS_RE = re.compile(
    r"""font-family:\s*[^;]*?\b(?:Impact|Comic Sans|Papyrus)\b""",
    re.IGNORECASE
)

# E7: Eyebrow / Kicker Spam (Uppercase tracking-widest tag immediately preceding an h1/h2)
EYEBROW_SPAM_RE = re.compile(
    r"""<(?:span|p|div)\b[^>]*?\b(?:uppercase\s+tracking-widest|tracking-widest\s+uppercase|uppercase\s+tracking-\[0\.2em\])\b[^>]*>[^<]{1,30}</(?:span|p|div)>\s*<h[12]\b""",
    re.IGNORECASE | re.MULTILINE
)

# E8: Emoji used as an icon or standalone badge in HTML/JSX tags
EMOJI_GLYPHS = r"[🚀⚡🔲📑🔍📋📦💡❌✓🎨🛠️🎯🔥💎⭐🌟📌⚠️💬📊🎉✨🚨🔔]"
EMOJI_STANDALONE_TAG_RE = re.compile(
    rf"""<(span|button|a|div|p|h[1-6])\b[^>]*>\s*({EMOJI_GLYPHS})\s*</\1>""",
    re.UNICODE
)
EMOJI_ICON_CLASS_RE = re.compile(
    rf"""<(?:span|div|button|a)\b[^>]*class=["'][^"']*\b(?:icon|badge|pill|btn|symbol|trigger)[^"']*["'][^>]*>[^<]*({EMOJI_GLYPHS})[^<]*</(?:span|div|button|a)>""",
    re.IGNORECASE | re.UNICODE
)
EMOJI_HEADING_BUTTON_RE = re.compile(
    rf"""<(button|h[1-6]|a)\b[^>]*>\s*({EMOJI_GLYPHS})\s+[^<]+</\1>""",
    re.UNICODE
)

# E9: Inline style with hardcoded hex color
INLINE_HEX_STYLE_RE = re.compile(
    r"""style=["'][^"']*?\b(?:color|background|border-color):\s*(#[0-9a-fA-F]{3,8})\b""",
    re.IGNORECASE
)

# W1: Missing tabular-nums on tables
TABLE_TAG_RE = re.compile(r"""<table\b[^>]*>""")
TABULAR_NUMS_RE = re.compile(r"""\b(?:tabular-nums|font-variant-numeric:\s*tabular-nums)\b""")


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    # .agent/skills/<skill>/scripts/<file> -> proje koku 4 seviye yukarida
    return Path(__file__).resolve().parents[4]


def iter_source_files(root: Path, include_agent: bool = False):
    """Projedeki taranacak frontend kaynak dosyalarını listeler."""
    found_any = False
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
            # Test dosyalarını tarama dışı bırak
            stem_lower = path.stem.lower()
            if stem_lower.endswith(".test") or stem_lower.endswith(".spec") or "__tests__" in path.parts:
                continue
            found_any = True
            yield path

    # Eğer standart klasörler yoksa ama kökte HTML/Astro/Svelte varsa
    if not found_any:
        for path in sorted(root.glob("*")):
            if path.is_file() and path.suffix.lower() in (".html", ".astro", ".svelte", ".vue"):
                yield path

    # Eğer include_agent bayrağı açıksa .agent altındaki HTML dosyalarını da tara
    if include_agent:
        agent_dir = root / ".agent"
        if agent_dir.is_dir():
            for path in sorted(agent_dir.glob("*.html")):
                if path.is_file():
                    yield path


def check_file(path: Path) -> tuple[list[dict], list[dict]]:
    """Tek bir kaynak dosyayı anti-pattern'lere karşı tarar."""
    errors = []
    warnings = []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return [{"code": "E0", "file": str(path), "line": 1, "message": f"Dosya okunamadı: {exc}"}], []

    lines = content.splitlines()

    # E1: Nested Cards
    card_stack = []
    for m in CARD_TAG_RE.finditer(content):
        tag_name = m.group(2)
        if tag_name in CARD_PARTS or not (tag_name == "Card" or tag_name.endswith("Card")):
            continue
        is_close = bool(m.group(1))
        attr_part = m.group(3) or ""
        is_self_closing = bool(m.group(4)) or attr_part.strip().endswith("/")
        if is_close:
            if card_stack and card_stack[-1][0] == tag_name:
                card_stack.pop()
        elif is_self_closing:
            if card_stack:
                line_no = content[:m.start()].count("\n") + 1
                errors.append({
                    "code": "E1",
                    "rule": "nested-card",
                    "file": str(path),
                    "line": line_no,
                    "message": f"İç içe kart (nested card) tespit edildi: <{card_stack[-1][0]}> içinde <{tag_name} />. Düz bento-grid veya section hiyerarşisi kullanın."
                })
        else:
            if card_stack:
                line_no = content[:m.start()].count("\n") + 1
                errors.append({
                    "code": "E1",
                    "rule": "nested-card",
                    "file": str(path),
                    "line": line_no,
                    "message": f"İç içe kart (nested card) tespit edildi: <{card_stack[-1][0]}> içinde <{tag_name}>. Düz bento-grid veya section hiyerarşisi kullanın."
                })
            card_stack.append((tag_name, m.start()))

    # E2: Gradient Text (Tailwind & CSS)
    for idx, line in enumerate(lines, start=1):
        if GRADIENT_TEXT_TW_RE.search(line):
            errors.append({
                "code": "E2",
                "rule": "gradient-text",
                "file": str(path),
                "line": idx,
                "message": "Metin üzerinde gradyan (bg-clip-text / text-transparent) tespit edildi. Vurgu için ağırlık veya renk kontrastı kullanın."
            })
    if GRADIENT_TEXT_CSS_RE.search(content):
        m = GRADIENT_TEXT_CSS_RE.search(content)
        line_no = content[:m.start()].count("\n") + 1
        errors.append({
            "code": "E2",
            "rule": "gradient-text",
            "file": str(path),
            "line": line_no,
            "message": "CSS background-clip: text ile şeffaf metin gradyanı tespit edildi."
        })

    # E3: Side Accent on Rounded Card
    for idx, line in enumerate(lines, start=1):
        if SIDE_ACCENT_TW_RE.search(line):
            errors.append({
                "code": "E3",
                "rule": "side-accent",
                "file": str(path),
                "line": idx,
                "message": "Yuvarlatılmış kartta kalın renkli kenar şeridi (border-l-4 vb. + rounded) tespit edildi. 1px nötr sınır ve zemin kontrastı kullanın."
            })
    if path.suffix == ".css" and SIDE_ACCENT_CSS_RE.search(content):
        m = SIDE_ACCENT_CSS_RE.search(content)
        line_no = content[:m.start()].count("\n") + 1
        errors.append({
            "code": "E3",
            "rule": "side-accent",
            "file": str(path),
            "line": line_no,
            "message": "CSS border-left ve border-radius birlikte tespit edildi. Yuvarlatılmış kartlarda yan şerit yasaktır."
        })

    # E4: Zero-blur offset block shadow
    for idx, line in enumerate(lines, start=1):
        if BLOCK_SHADOW_TW_RE.search(line):
            errors.append({
                "code": "E4",
                "rule": "block-shadow",
                "file": str(path),
                "line": idx,
                "message": "Sıfır-blur ofset blok gölge (shadow-[...0px]) tespit edildi. Doğal ışık kaynağı ve yumuşak blur kullanın."
            })
        if BLOCK_SHADOW_CSS_RE.search(line):
            errors.append({
                "code": "E4",
                "rule": "block-shadow",
                "file": str(path),
                "line": idx,
                "message": "CSS box-shadow içinde 0-blur ofset gölge tespit edildi."
            })

    # E5: Raw gray on chromatic background in same tag/class string
    for idx, line in enumerate(lines, start=1):
        if CHROMATIC_BG_RE.search(line) and RAW_GRAY_TEXT_RE.search(line):
            errors.append({
                "code": "E5",
                "rule": "gray-on-color",
                "file": str(path),
                "line": idx,
                "message": "Renkli/kromatik zemin üzerinde saf gri metin tespit edildi. Metin rengine zemin tonunu (hue tint) katın veya semantic token kullanın."
            })

    # E6: Banned fonts
    for idx, line in enumerate(lines, start=1):
        m = BANNED_FONTS_RE.search(line)
        if m:
            errors.append({
                "code": "E6",
                "rule": "display-fallback",
                "file": str(path),
                "line": idx,
                "message": f"Yasaklı sistem/display fontu tespit edildi: {m.group(0)}. Karakterli font ve uygun fallback kullanın."
            })

    # E7: Eyebrow / Kicker Spam
    for m in EYEBROW_SPAM_RE.finditer(content):
        line_no = content[:m.start()].count("\n") + 1
        errors.append({
            "code": "E7",
            "rule": "eyebrow-spam",
            "file": str(path),
            "line": line_no,
            "message": "Başlık üzerinde jenerik büyük harfli süs hapı (uppercase tracking-widest kicker) tespit edildi. Başlığı doğrudan konuşturun."
        })

    # E8: Emoji used as icon / badge / button prefix
    for idx, line in enumerate(lines, start=1):
        if EMOJI_STANDALONE_TAG_RE.search(line):
            m = EMOJI_STANDALONE_TAG_RE.search(line)
            errors.append({
                "code": "E8",
                "rule": "emoji-icon",
                "file": str(path),
                "line": idx,
                "message": f"İkon/rozet olarak ham emoji ('{m.group(2)}') tespit edildi. SVG vektör ikon (Lucide / Heroicons) kullanın (§2.6 A.8)."
            })
        elif EMOJI_ICON_CLASS_RE.search(line):
            m = EMOJI_ICON_CLASS_RE.search(line)
            errors.append({
                "code": "E8",
                "rule": "emoji-icon",
                "file": str(path),
                "line": idx,
                "message": f"İkon/rozet sınıfında ham emoji ('{m.group(1)}') tespit edildi. SVG vektör ikon kullanın (§2.6 A.8)."
            })
        elif EMOJI_HEADING_BUTTON_RE.search(line):
            m = EMOJI_HEADING_BUTTON_RE.search(line)
            errors.append({
                "code": "E8",
                "rule": "emoji-icon",
                "file": str(path),
                "line": idx,
                "message": f"Başlık veya butonda önek emoji ('{m.group(2)}') tespit edildi. SVG vektör ikon kullanın (§2.6 A.8)."
            })

    # E9: Inline style with hardcoded hex color
    for idx, line in enumerate(lines, start=1):
        m = INLINE_HEX_STYLE_RE.search(line)
        if m:
            errors.append({
                "code": "E9",
                "rule": "hardcoded-palette",
                "file": str(path),
                "line": idx,
                "message": f"Inline style içinde ham renk hex kodu ('{m.group(1)}') tespit edildi. CSS değişkeni (var(--...)) veya token skalası kullanın."
            })

    # W1: Missing tabular-nums in table tag
    if TABLE_TAG_RE.search(content) and not TABULAR_NUMS_RE.search(content):
        errors_in_table = [e for e in errors if e["rule"] == "missing-tabular-nums"]
        if not errors_in_table:
            m = TABLE_TAG_RE.search(content)
            line_no = content[:m.start()].count("\n") + 1
            warnings.append({
                "code": "W1",
                "rule": "missing-tabular-nums",
                "file": str(path),
                "line": line_no,
                "message": "Tablo tespit edildi ancak tabular-nums sınıfı veya font-variant-numeric bulunamadı. Rakam hizalaması için ekleyin."
            })

    return errors, warnings


def run_checks(root: Path, specific_files: list[Path] = None, include_agent: bool = False) -> dict:
    if specific_files:
        files = [f.resolve() for f in specific_files if f.is_file()]
    else:
        files = list(iter_source_files(root, include_agent=include_agent))

    if not files:
        return {
            "scope": "out_of_scope",
            "project_root": str(root),
            "files_scanned": 0,
            "errors": [],
            "warnings": [],
            "status": "OK",
            "exit": 0
        }

    all_errors = []
    all_warnings = []

    for path in files:
        errors, warnings = check_file(path)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    rel_errors = []
    for err in all_errors:
        err_copy = dict(err)
        try:
            err_copy["file"] = os.path.relpath(err_copy["file"], root).replace("\\", "/")
        except Exception:
            pass
        rel_errors.append(err_copy)

    rel_warnings = []
    for w in all_warnings:
        w_copy = dict(w)
        try:
            w_copy["file"] = os.path.relpath(w_copy["file"], root).replace("\\", "/")
        except Exception:
            pass
        rel_warnings.append(w_copy)

    return {
        "scope": "in_scope",
        "project_root": str(root),
        "files_scanned": len(files),
        "errors": rel_errors,
        "warnings": rel_warnings,
        "status": "FAIL" if rel_errors else "OK",
        "exit": 1 if rel_errors else 0
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Deterministik Tasarım Zanaat Tabanı ve Anti-Slop Denetleyicisi")
    parser.add_argument("--json", action="store_true", help="Makine okunur JSON çıktısı üretir")
    parser.add_argument("--strict", action="store_true", help="Uyarıları (W1) da hata sayarak exit 1 döndürür")
    parser.add_argument("--path", type=str, default=None, help="Denetlenecek proje kök dizini")
    parser.add_argument("--file", type=str, action="append", default=None, help="Doğrudan denetlenecek spesifik dosya yolu")
    parser.add_argument("--include-agent", action="store_true", help=".agent klasörü altındaki HTML dosyalarını da taramaya dahil eder")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve() if args.path else find_project_root()
    specific_files = [Path(f) for f in args.file] if args.file else None

    res = run_checks(root, specific_files=specific_files, include_agent=args.include_agent)

    exit_code = res["exit"]
    if args.strict and res["warnings"] and exit_code == 0:
        exit_code = 1
        res["exit"] = 1
        res["status"] = "FAIL"

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return exit_code

    if res["scope"] == "out_of_scope":
        print(f"Kapsam dışı: {root} altında taranacak frontend kaynak dosyası bulunamadı.")
        print("SONUÇ: [OK]")
        return 0

    print(f"Taranan frontend dosya sayısı: {res['files_scanned']}")

    if res["errors"]:
        print(f"\n❌ TASARIM ZANAAT TABANI İHLALLERİ ({len(res['errors'])} hata):")
        for err in res["errors"]:
            print(f"  [{err['code']} - {err['rule']}] {err['file']}:{err['line']} -> {err['message']}")

    if res["warnings"]:
        print(f"\n⚠️ UYARILAR ({len(res['warnings'])} uyarı):")
        for warn in res["warnings"]:
            print(f"  [{warn['code']} - {warn['rule']}] {warn['file']}:{warn['line']} -> {warn['message']}")

    if exit_code == 0:
        print(f"\nSONUÇ: {res['files_scanned']} dosya tarandı · 0 ihlal · [OK]")
    else:
        print(f"\nSONUÇ: {len(res['errors'])} ihlal tespit edildi · [FAIL]")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
