#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Auth Hero — Proje arketipine özel, yüksek çözünürlüklü ve atmosferik Auth Hero görseli tedarik/üretim aracı.

Kullanım:
    python .agent/skills/mock-asset-provider/scripts/generate_auth_hero.py --archetype docs_tools --output public/assets/auth/hero.jpg
    python .agent/skills/mock-asset-provider/scripts/generate_auth_hero.py --archetype fintech --project-name "My Vault"
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional

# Windows konsol UTF-8 desteği
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

# Arketipe göre küratörlü, yüksek kaliteli ve telifsiz atmosferik fotoğraf URL'leri (1200x800)
# ⛔ Rastgele Picsum hash'leri KESİNLİKLE KULLANILMAZ (anlamsız rastgele fotoğraflar basar).
ARCHETYPE_HERO_CATALOG: Dict[str, List[str]] = {
    "docs_tools": [
        # Ahşap kütüphane rafları, kitaplar ve sıcak arşiv atmosferi (Bookmark, Memory Vault, Kütüphane, Notlar)
        "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=1200",
        "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=1200",
        "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200",
    ],
    "fintech": [
        # Modern mimari, çelik geometri ve kurumsal kasa tonları
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200",
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1200",
    ],
    "developer_tools": [
        # Minimalist karanlık çalışma masası, kod ve loş ortam
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200",
    ],
    "saas_dashboard": [
        # Ferah modern cam mimari, minimal çalışma ortamı
        "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200",
        "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=1200",
    ],
    "creative": [
        # Tasarım atölyesi, sanatsal dokular ve editoryal kompozisyon
        "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1200",
        "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=1200",
    ],
    "general": [
        # Sıcak minimal iç mekan ve doğal ışık
        "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200",
    ]
}

# Takma ad normalizasyonu
ARCHETYPE_ALIASES = {
    "bookmark": "docs_tools",
    "bookmarks": "docs_tools",
    "library": "docs_tools",
    "vault": "docs_tools",
    "notes": "docs_tools",
    "docs": "docs_tools",
    "tools": "docs_tools",
    "archive": "docs_tools",
    "finance": "fintech",
    "crypto": "fintech",
    "dev": "developer_tools",
    "code": "developer_tools",
    "terminal": "developer_tools",
    "saas": "saas_dashboard",
    "dashboard": "saas_dashboard",
    "design": "creative",
    "art": "creative",
}


def normalize_archetype(raw: str) -> str:
    key = raw.lower().strip().replace("-", "_").replace(" ", "_")
    if key in ARCHETYPE_HERO_CATALOG:
        return key
    if key in ARCHETYPE_ALIASES:
        return ARCHETYPE_ALIASES[key]
    for alias_key, target in ARCHETYPE_ALIASES.items():
        if alias_key in key:
            return target
    return "general"


def generate_fallback_svg(project_name: str, archetype: str, width: int = 1200, height: int = 800) -> str:
    """İnternet bağlantısı olmadığında kullanılacak zengin SVG atmosferik arka plan."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <radialGradient id="bgGlow" cx="60%" cy="40%" r="70%">
      <stop offset="0%" stop-color="#2d334d" />
      <stop offset="50%" stop-color="#181a26" />
      <stop offset="100%" stop-color="#0d0e15" />
    </radialGradient>
    <linearGradient id="overlayGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7184ee" stop-opacity="0.25" />
      <stop offset="100%" stop-color="#212625" stop-opacity="0.95" />
    </linearGradient>
    <pattern id="gridPattern" width="40" height="40" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.5" fill="#ffffff" fill-opacity="0.08" />
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#bgGlow)" />
  <rect width="{width}" height="{height}" fill="url(#overlayGrad)" />
  <rect width="{width}" height="{height}" fill="url(#gridPattern)" />
  <!-- Editorial atmospheric shapes -->
  <g opacity="0.12" stroke="#ffffff" stroke-width="1.5" fill="none">
    <circle cx="950" cy="400" r="280" />
    <circle cx="950" cy="400" r="180" />
    <rect x="750" y="220" width="360" height="460" rx="24" />
    <line x1="100" y1="700" x2="1100" y2="700" />
  </g>
  <text x="80" y="740" fill="#ffffff" fill-opacity="0.35" font-family="'Space Grotesk', -apple-system, sans-serif" font-size="28" font-weight="600" letter-spacing="4">{project_name.upper()} • {archetype.upper()}</text>
</svg>"""


def generate_auth_hero(
    archetype: str = "general",
    project_name: str = "Application",
    output_path: Path | str = "public/assets/auth/hero.jpg",
    width: int = 1200,
    height: int = 800,
    timeout: int = 8,
) -> bool:
    target_path = Path(output_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    arch_key = normalize_archetype(archetype)
    urls = ARCHETYPE_HERO_CATALOG.get(arch_key, ARCHETYPE_HERO_CATALOG["general"])
    chosen_url = urls[0]

    # İndirmeyi dene
    req = urllib.request.Request(
        chosen_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GokuAuthHeroGenerator/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            if len(data) > 5000:
                target_path.write_bytes(data)
                print(f"[OK] Auth hero görseli başarıyla indirildi: {target_path} ({len(data)} bayt, arketip: {arch_key})")
                return True
    except Exception as e:
        sys.stderr.write(f"[UYARI] Görsel indirilemedi ({chosen_url}): {e}. Yerel yedek SVG oluşturuluyor...\n")

    fallback_svg = generate_fallback_svg(project_name, arch_key, width, height)
    target_path.write_text(fallback_svg, encoding="utf-8")
    print(f"[OK] Çevrimdışı atmosferik SVG arka planı oluşturuldu: {target_path} (arketip: {arch_key})")
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generate Auth Hero — Proje arketipine özel Auth Hero görseli üretici")
    parser.add_argument("--archetype", default="general", help="Proje arketipi (docs_tools, fintech, saas_dashboard, developer_tools, creative, general)")
    parser.add_argument("--project-name", default="Application", help="Proje adı")
    parser.add_argument("--output", default="public/assets/auth/hero.jpg", help="Çıktı dosya yolu")
    parser.add_argument("--width", type=int, default=1200, help="Genişlik (varsayılan: 1200)")
    parser.add_argument("--height", type=int, default=800, help="Yükseklik (varsayılan: 800)")

    args = parser.parse_args(argv)
    success = generate_auth_hero(
        archetype=args.archetype,
        project_name=args.project_name,
        output_path=args.output,
        width=args.width,
        height=args.height,
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
