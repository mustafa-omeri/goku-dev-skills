#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Frontend bundle ve chunk bütçesi kapısı — Vite/Webpack boyut ve uyarı denetleyicisi.

Neden var?
----------
`frontend-bundle-limits.md` "Vite'ın chunkSizeWarningLimit (>500 kB) sarı uyarısı test
hatası (FAIL) sayılır, düzeltilmeden geçilemez" kuralını koyar. Ancak Vite chunk limiti
aşıldığında terminale uyarı basmasına rağmen çıkış kodunu 0 (exit 0) olarak verir.
Bu durum 'Otomasyon Yeşilliği Yanılgısı'na yol açar: sırf exit 0 olduğu için ajanlar ve
CI kontrolleri bundle limitinin aşıldığını fark etmez.

Bu script:
  1. Frontend projesi olup olmadığını tespit eder (package.json + frontend build script).
  2. vite.config.* içindeki `chunkSizeWarningLimit` değerini (varsayılan: 500 kB) çözer.
  3. `dist/` (veya `build/`) içindeki tüm .js chunk'larının ham ve gzip boyutlarını hesaplar.
  4. İsteğe bağlı veya `dist` yoksa/bayatsa build komutunu çalıştırıp Vite'ın
     "Some chunks are larger than..." uyarısını doğrudan yakalar.
  5. Bütçe ihlallerinde çıkış kodu 1 ile FAIL verir.

Kontroller
----------
E1: Derleme hatası (build komutu başarısız oldu, exit != 0)
E2: Vite sarı uyarısı tespit edildi ("Some chunks are larger than...")
E3: Chunk ham boyutu sınırı aşıldı (> limit_kb)
E4: Başlangıç (entry) chunk gzip sınırı aşıldı (> 200 kB)
E5: Lazy chunk gzip sınırı aşıldı (> 500 kB)

Frontend projesi değilse (package.json yok): exit 0 (kapsam dışı).
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_RAW_LIMIT_KB = 500.0
DEFAULT_ENTRY_GZIP_LIMIT_KB = 200.0
DEFAULT_LAZY_GZIP_LIMIT_KB = 500.0

VITE_CONFIG_NAMES = (
    "vite.config.ts",
    "vite.config.js",
    "vite.config.mjs",
    "vite.config.cjs",
)

CHUNK_WARN_PATTERN = re.compile(
    r"Some chunks are larger than|\(!\)\s*Some chunks are larger",
    re.IGNORECASE,
)


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    # .agent/skills/musgoku/scripts/<file> -> 4 seviye yukarı
    return Path(__file__).resolve().parents[4]


def detect_chunk_limit(project_root: Path) -> float:
    """vite.config dosyasından chunkSizeWarningLimit değerini okur, yoksa 500 döner."""
    for cfg_name in VITE_CONFIG_NAMES:
        cfg_path = project_root / cfg_name
        if cfg_path.is_file():
            try:
                content = cfg_path.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r"chunkSizeWarningLimit\s*:\s*(\d+)", content)
                if m:
                    return float(m.group(1))
            except Exception:
                pass
    return DEFAULT_RAW_LIMIT_KB


def is_frontend_project(project_root: Path) -> bool:
    pkg_json = project_root / "package.json"
    if not pkg_json.is_file():
        return False
    try:
        data = json.loads(pkg_json.read_text(encoding="utf-8", errors="ignore"))
        scripts = data.get("scripts", {})
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "build" in scripts:
            return True
        if any(tool in deps for tool in ("vite", "webpack", "next", "astro", "rollup")):
            return True
    except Exception:
        pass
    return False


def detect_build_command(project_root: Path) -> list[str]:
    if (project_root / "pnpm-lock.yaml").is_file():
        return ["pnpm", "build"]
    if (project_root / "yarn.lock").is_file():
        return ["yarn", "build"]
    return ["npm", "run", "build"]


def find_dist_dir(project_root: Path, custom_dist: str | None = None) -> Path | None:
    if custom_dist:
        d = project_root / custom_dist
        if d.is_dir():
            return d
    for candidate in ("dist", "build", "out"):
        d = project_root / candidate
        if d.is_dir():
            return d
    return None


def run_build(project_root: Path) -> tuple[int, str, list[str]]:
    """Build komutunu çalıştırır, çıkış kodunu ve yakalanan Vite uyarılarını döner."""
    cmd = detect_build_command(project_root)
    errors: list[str] = []
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=os.name == "nt",
        )
        output = proc.stdout or ""
        if proc.returncode != 0:
            errors.append(f"E1: Build başarısız oldu (çıkış kodu: {proc.returncode})")
        if CHUNK_WARN_PATTERN.search(output):
            errors.append("E2: Vite sarı uyarısı tespit edildi: 'Some chunks are larger than ...'")
        return proc.returncode, output, errors
    except Exception as exc:
        return 1, str(exc), [f"E1: Build çalıştırılamadı: {exc}"]


def analyze_chunks(dist_dir: Path, raw_limit_kb: float, entry_gzip_limit_kb: float, lazy_gzip_limit_kb: float):
    """dist dizinindeki .js chunk dosyalarını tarar ve boyut ihlallerini belirler."""
    chunks = []
    errors = []

    js_files = list(dist_dir.rglob("*.js"))
    for js_path in js_files:
        try:
            raw_bytes = js_path.read_bytes()
            size_kb = len(raw_bytes) / 1024.0
            gzip_bytes = gzip.compress(raw_bytes, compresslevel=9)
            gzip_kb = len(gzip_bytes) / 1024.0
            rel_path = js_path.relative_to(dist_dir.parent).as_posix()

            is_entry = js_path.name.startswith("index-") or js_path.name.startswith("main-") or js_path.name == "index.js"

            chunk_info = {
                "file": rel_path,
                "name": js_path.name,
                "size_kb": round(size_kb, 2),
                "gzip_kb": round(gzip_kb, 2),
                "is_entry": is_entry,
                "ok": True,
            }

            # Kontrol E3: Ham boyut sınırı
            if size_kb > raw_limit_kb:
                chunk_info["ok"] = False
                errors.append(
                    f"E3: Chunk ham boyutu sınırı aşıldı: {rel_path} "
                    f"({size_kb:.2f} kB > {raw_limit_kb:.0f} kB)"
                )

            # Kontrol E4: Başlangıç (entry) chunk gzip sınırı
            if is_entry and gzip_kb > entry_gzip_limit_kb:
                chunk_info["ok"] = False
                errors.append(
                    f"E4: Başlangıç (entry) chunk gzip sınırı aşıldı: {rel_path} "
                    f"({gzip_kb:.2f} kB > {entry_gzip_limit_kb:.0f} kB)"
                )

            # Kontrol E5: Lazy chunk gzip sınırı
            if gzip_kb > lazy_gzip_limit_kb:
                chunk_info["ok"] = False
                errors.append(
                    f"E5: Chunk gzip sınırı aşıldı: {rel_path} "
                    f"({gzip_kb:.2f} kB > {lazy_gzip_limit_kb:.0f} kB)"
                )

            chunks.append(chunk_info)
        except Exception as exc:
            errors.append(f"E3: Dosya okunamadı: {js_path.name} ({exc})")

    # En büyük chunk'lar üstte olacak şekilde sırala
    chunks.sort(key=lambda c: c["size_kb"], reverse=True)
    return chunks, errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Frontend bundle ve chunk bütçesi denetleyicisi")
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı")
    parser.add_argument("--build", action="store_true", help="Denetim öncesinde build çalıştır")
    parser.add_argument("--dist", type=str, default=None, help="Özel dist dizini yolu")
    parser.add_argument("--limit", type=float, default=None, help="Özel ham chunk boyutu sınırı (kB)")
    args = parser.parse_args(argv)

    project_root = find_project_root()

    if not is_frontend_project(project_root):
        if args.json:
            print(json.dumps({
                "scope": "out_of_scope",
                "reason": "Frontend projesi değil (package.json veya build script yok)",
                "exit": 0,
            }, indent=2, ensure_ascii=False))
        else:
            print("[KAPSAM DISI] Frontend projesi degil (package.json veya build script yok).")
        return 0

    raw_limit_kb = args.limit if args.limit is not None else detect_chunk_limit(project_root)
    entry_gzip_limit_kb = DEFAULT_ENTRY_GZIP_LIMIT_KB
    lazy_gzip_limit_kb = DEFAULT_LAZY_GZIP_LIMIT_KB

    all_errors: list[str] = []
    dist_dir = find_dist_dir(project_root, args.dist)

    # dist yoksa veya açıkça --build istendiyse derleme yap
    if args.build or dist_dir is None:
        exit_code, _build_out, build_errors = run_build(project_root)
        all_errors.extend(build_errors)
        dist_dir = find_dist_dir(project_root, args.dist)

    if dist_dir is None or not dist_dir.is_dir():
        all_errors.append("E1: dist/ veya build/ dizini bulunamadı. Lütfen önce derleme yapın.")
        chunks = []
    else:
        chunks, chunk_errors = analyze_chunks(dist_dir, raw_limit_kb, entry_gzip_limit_kb, lazy_gzip_limit_kb)
        all_errors.extend(chunk_errors)

    exit_code = 1 if all_errors else 0

    if args.json:
        result = {
            "scope": "in_scope",
            "project_root": str(project_root),
            "raw_limit_kb": raw_limit_kb,
            "entry_gzip_limit_kb": entry_gzip_limit_kb,
            "lazy_gzip_limit_kb": lazy_gzip_limit_kb,
            "chunks_count": len(chunks),
            "chunks_top": chunks[:5],
            "errors": all_errors,
            "exit": exit_code,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return exit_code

    # Standart metin çıktısı
    print("=" * 60)
    print("📦 FRONTEND BUNDLE & CHUNK BÜTÇESİ DENETİMİ")
    print(f"Hedef: {project_root.name} | Ham Eşik: {raw_limit_kb:.0f} kB | Entry Gzip Eşiği: {entry_gzip_limit_kb:.0f} kB")
    print("=" * 60)

    if chunks:
        print("\nEn Büyük Chunk Dosyaları:")
        for c in chunks[:8]:
            status = "✅ [OK]" if c["ok"] else "❌ [FAIL]"
            entry_tag = " (Entry)" if c["is_entry"] else ""
            print(f"  • {c['file']}{entry_tag}: {c['size_kb']} kB │ gzip: {c['gzip_kb']} kB  {status}")

    if all_errors:
        print("\n❌ BÜTÇE İHLALLERİ VE HATALAR:")
        for err in all_errors:
            print(f"  - {err}")
        print("\nSONUÇ: [FAIL] — Vite chunk limiti veya gzip bütçesi aşıldı!")
        return 1

    print("\n✅ SONUÇ: [OK] — Tüm chunk boyutları belirlenen bütçe sınırları dahilinde.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
