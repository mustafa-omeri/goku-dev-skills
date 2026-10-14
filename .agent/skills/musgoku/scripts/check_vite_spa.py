#!/usr/bin/env python3
"""Vite SPA kapisi — Next.js konsepti SPA'ya sizmis mi?

Neden var?
----------
`vite-spa-enforcement.md` "Next.js konseptleri kullanilmaz" diyordu ama
**capraz bir kapisi yoktu**: ajan `"use client"` ya da `next/link` yaziyor,
kimse olcmuyor. Kural TUTUM diye isaretlenmis, yani beyan bekleniyordu.

Oysa bu kural **olculebilir**: Next.js izleri dosyalarda metin olarak duruyor.
Bu script onlari tarar.

Kontroller
----------
E1 next paketi kurulu      package.json dependencies icinde `next` var mi
E2 next yapilandirma dosyasi   next.config.js|ts|mjs|mc|cjs var mi
E3 next/ importu          kaynakta `next/...` veya `next-safe-action` importu
E4 sunucu yonu direktifi  "use client" / "use server" (SPA'da gerek yok)
W1 process.env            Vite'ta `import.meta.env` kullanilmali
W2 SSR veri cekme         getServerSideProps / getStaticProps kalinti mi

E1-E4 hata (exit 1) · W1-W2 uyari · yigin Next.js ise kural gecersiz: exit 0.
Frontend projesi degilse (package.json yok) kapsam disi: exit 0.

Kullanim
--------
    python .agent/skills/musgoku/scripts/check_vite_spa.py
    python .agent/skills/musgoku/scripts/check_vite_spa.py --json

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

SOURCE_DIRS = ("src", "app", "pages", "components", "lib")
SOURCE_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs")
IGNORE_DIRS = {"node_modules", "dist", "build", ".git", "coverage", ".next",
               "__pycache__", ".pytest_cache", "target"}

NEXT_CONFIG_NAMES = ("next.config.js", "next.config.ts", "next.config.mjs",
                     "next.config.cjs")

IMPORT_RE = re.compile(r"""(?:from|import)\s*\(?\s*['"](next/[^'"]+|next-safe-action)['"]""")
DIRECTIVE_RE = re.compile(r'^\s*["\']use (client|server)["\']\s*;?\s*$')
PROCESS_ENV_RE = re.compile(r"\bprocess\.env\.")
SSR_RE = re.compile(r"\b(getServerSideProps|getStaticProps|getStaticPaths)\b")


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


def iter_sources(root: Path):
    for folder in SOURCE_DIRS:
        base = root / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix not in SOURCE_EXT:
                continue
            if any(part in IGNORE_DIRS for part in path.parts):
                continue
            yield path


def check(root: Path):
    errors = []
    warnings = []

    package_json = root / "package.json"
    if not package_json.is_file():
        return errors, warnings, {"stack": "yok", "files": 0}

    try:
        package = json.loads(package_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [("E1", "package.json", f"okunamadi: {exc}")], warnings, {"stack": "bilinmiyor",
                                                                     "files": 0}

    deps = {}
    for key in ("dependencies", "devDependencies"):
        deps.update(package.get(key) or {})

    if "next" in deps:
        # Bu proje Next.js: kural tanımı gereği geçersiz.
        return errors, warnings, {"stack": "next", "files": 0}

    if "vite" not in deps:
        return errors, warnings, {"stack": "bilinmiyor", "files": 0}

    for name in NEXT_CONFIG_NAMES:
        if (root / name).exists():
            errors.append(("E2", name, "Vite projesinde Next.js yapilandirma dosyasi var"))

    scanned = 0
    for path in iter_sources(root):
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()

        for match in IMPORT_RE.finditer(text):
            line = text[:match.start()].count("\n") + 1
            errors.append(("E3", rel,
                           f"satir {line}: Next.js importu -> {match.group(1)}"))

        for number, line_text in enumerate(text.split("\n"), start=1):
            if DIRECTIVE_RE.match(line_text):
                errors.append(("E4", rel,
                               f"satir {number}: sunucu yonu direktifi SPA'da gerek yok "
                               f"({line_text.strip()})"))
        # Test dosyalari vitest/node ortaminda calisir; `process.env` orada
        # normaldir. Uyarinin guvenilirligi icin test dosyalari dislanir.
        is_test = ".test." in rel or ".spec." in rel or "__tests__" in rel
        if not is_test and PROCESS_ENV_RE.search(text):
            warnings.append(("W1", rel, "process.env kullanilmis; import.meta.env kullanin"))
        if not is_test:
            for match in SSR_RE.finditer(text):
                warnings.append(("W2", rel,
                                 f"{match.group(1)} kalinti mi; client-side fetch kullanin"))

    return errors, warnings, {"stack": "vite", "files": scanned}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Vite SPA / Next.js izi kapisi")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = find_project_root()
    errors, warnings, stats = check(root)

    if args.json:
        print(json.dumps({
            **stats,
            "errors": [{"code": c, "file": f, "message": m} for c, f, m in errors],
            "warnings": [{"code": c, "file": f, "message": m} for c, f, m in warnings],
            "exit": 1 if errors else 0,
        }, ensure_ascii=False, indent=2))
        return 1 if errors else 0

    if stats["stack"] != "vite":
        reason = {"next": "proje Next.js — kural gecersiz",
                  "bilinmiyor": "Vite projesi degil — kapsam disi",
                  "yok": "package.json bulunamadi — kapsam disi"}[stats["stack"]]
        print(f"Yigin: {stats['stack']} ({reason})")
        print("\nSONUC: kapsam disi · [OK]")
        return 0

    print(f"Yigin: vite · taranan dosya: {stats['files']}")
    for code, name, message in errors:
        print(f"[HATA] {code} {name}: {message}")
    for code, name, message in warnings:
        print(f"[UYARI] {code} {name}: {message}")
    if errors:
        print(f"\nSONUC: {len(errors)} hata · {len(warnings)} uyari · Next.js izi var")
        return 1
    print(f"\nSONUC: {stats['files']} dosya tarandi · Next.js izi yok · [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())