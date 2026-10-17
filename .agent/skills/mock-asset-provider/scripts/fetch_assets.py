#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mock Asset Provider — Gerçekçi mock görsel ve veri varlıkları tedarik aracı.

UI kartları, profiller, avatarlar, etkinlikler ve ürünler için
deterministik, kırılmayan ve yüksek kaliteli görsel URL'leri üretir veya
yerel proje klasörüne (public/mock-assets/ vb.) indirir.

Kullanım:
    python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --category portraits --gender women --count 5
    python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --category events --seed "rock-festival" --download --output public/mock-assets/events
    python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --from-config
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

# Windows konsol UTF-8 desteği
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

DEFAULT_CONFIG_PATH = Path(".agent/config/assets.json")
DEFAULT_STORAGE_DIR = "public/mock-assets"

# Kırılmayan deterministik public kataloglar
PORTRAIT_WOMEN_MAX = 96
PORTRAIT_MEN_MAX = 99


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    # Script konumu: .agent/skills/mock-asset-provider/scripts/
    return Path(__file__).resolve().parents[4]


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    root = find_project_root()
    path = config_path or (root / DEFAULT_CONFIG_PATH)
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            sys.stderr.write(f"[UYARI] Config okunamadı ({path}): {e}\n")
    return {
        "enabled": True,
        "storage_dir": DEFAULT_STORAGE_DIR,
        "download_locally": True,
        "sources": {
            "github": {"enabled": False, "repo_url": ""},
            "api": {"unsplash_access_key": ""},
            "default_fallbacks": {
                "portraits": "randomuser",
                "events": "picsum",
                "products": "dummyjson",
                "general": "picsum"
            }
        }
    }


def generate_portrait_urls(gender: str = "all", count: int = 1, seed: Optional[str] = None) -> List[str]:
    urls = []
    base_seed = int(hashlib.md5((seed or "default").encode()).hexdigest()[:6], 16)
    for i in range(count):
        idx = (base_seed + i)
        if gender == "women":
            p_id = (idx % PORTRAIT_WOMEN_MAX) + 1
            urls.append(f"https://randomuser.me/api/portraits/women/{p_id}.jpg")
        elif gender == "men":
            p_id = (idx % PORTRAIT_MEN_MAX) + 1
            urls.append(f"https://randomuser.me/api/portraits/men/{p_id}.jpg")
        else:
            is_woman = (idx % 2 == 0)
            if is_woman:
                p_id = ((idx // 2) % PORTRAIT_WOMEN_MAX) + 1
                urls.append(f"https://randomuser.me/api/portraits/women/{p_id}.jpg")
            else:
                p_id = ((idx // 2) % PORTRAIT_MEN_MAX) + 1
                urls.append(f"https://randomuser.me/api/portraits/men/{p_id}.jpg")
    return urls


def generate_avatar_urls(style: str = "avataaars", count: int = 1, seed: Optional[str] = None) -> List[str]:
    urls = []
    base = seed or "avatar"
    for i in range(count):
        s = f"{base}-{i}" if count > 1 else base
        urls.append(f"https://api.dicebear.com/7.x/{style}/svg?seed={s}")
    return urls


def generate_event_urls(count: int = 1, seed: Optional[str] = None, width: int = 800, height: int = 600) -> List[str]:
    urls = []
    base = seed or "event"
    for i in range(count):
        s = f"{base}-{i}" if count > 1 else base
        urls.append(f"https://picsum.photos/seed/{s}/{width}/{height}")
    return urls


def generate_product_urls(count: int = 1, seed: Optional[str] = None, width: int = 600, height: int = 600) -> List[str]:
    urls = []
    base = seed or "product"
    for i in range(count):
        s = f"{base}-{i}" if count > 1 else base
        urls.append(f"https://picsum.photos/seed/{s}/{width}/{height}")
    return urls


def generate_general_urls(count: int = 1, seed: Optional[str] = None, width: int = 800, height: int = 600) -> List[str]:
    urls = []
    base = seed or "general"
    for i in range(count):
        s = f"{base}-{i}" if count > 1 else base
        urls.append(f"https://picsum.photos/seed/{s}/{width}/{height}")
    return urls


def download_file(url: str, dest_path: Path, timeout: int = 8) -> bool:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MockAssetProvider/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            dest_path.write_bytes(data)
            return True
    except Exception as e:
        sys.stderr.write(f"[UYARI] İndirme başarısız ({url}): {e}\n")
        return False


def clone_github_assets(repo_url: str, target_dir: Path) -> bool:
    if not repo_url:
        return False
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        cmd = ["git", "clone", "--depth", "1", repo_url, str(target_dir)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except Exception as e:
        sys.stderr.write(f"[HATA] GitHub repo klonlanamadı ({repo_url}): {e}\n")
        return False


def get_assets(category: str, gender: str = "all", style: str = "avataaars",
               count: int = 1, seed: Optional[str] = None,
               width: int = 800, height: int = 600) -> List[str]:
    cat = category.lower().strip()
    if cat in ("portraits", "portrait", "faces", "face", "people"):
        return generate_portrait_urls(gender=gender, count=count, seed=seed)
    elif cat in ("avatars", "avatar", "svg-avatar"):
        return generate_avatar_urls(style=style, count=count, seed=seed)
    elif cat in ("events", "event", "festival", "concert", "activity"):
        return generate_event_urls(count=count, seed=seed, width=width, height=height)
    elif cat in ("products", "product", "ecommerce", "item"):
        return generate_product_urls(count=count, seed=seed, width=width, height=height)
    else:
        return generate_general_urls(count=count, seed=seed, width=width, height=height)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Mock Asset Provider — Gerçekçi mock görsel ve veri varlıkları tedarik aracı")
    parser.add_argument("--category", default="general",
                        choices=["portraits", "avatars", "events", "products", "general"],
                        help="Görsel kategorisi")
    parser.add_argument("--gender", default="all", choices=["women", "men", "all"],
                        help="Portreler için cinsiyet")
    parser.add_argument("--style", default="avataaars",
                        help="DiceBear avatar stili (avataaars, bottts, shapes, identicon, lorelei)")
    parser.add_argument("--count", type=int, default=1, help="İstenen görsel adedi")
    parser.add_argument("--seed", default=None, help="Deterministik seed kelimesi")
    parser.add_argument("--width", type=int, default=800, help="Genişlik (px)")
    parser.add_argument("--height", type=int, default=600, help="Yükseklik (px)")
    parser.add_argument("--url-only", action="store_true", help="Yalnızca URL listesini döndür")
    parser.add_argument("--download", action="store_true", help="Görselleri yerel klasöre indir")
    parser.add_argument("--output", default=None, help="İndirme hedef klasörü")
    parser.add_argument("--config", default=None, help="Özel assets.json dosya yolu")
    parser.add_argument("--from-config", action="store_true", help="assets.json ayarlarını yürüt")
    parser.add_argument("--json", action="store_true", help="Çıktıyı JSON olarak bas")

    args = parser.parse_args(argv)
    root = find_project_root()
    cfg_path = Path(args.config) if args.config else None
    config = load_config(cfg_path)

    if args.from_config:
        gh = config.get("sources", {}).get("github", {})
        storage = root / config.get("storage_dir", DEFAULT_STORAGE_DIR)
        if gh.get("enabled") and gh.get("repo_url"):
            print(f"GitHub varlık deposu klonlanıyor: {gh['repo_url']} -> {storage}")
            success = clone_github_assets(gh["repo_url"], storage)
            return 0 if success else 1
        else:
            storage.mkdir(parents=True, exist_ok=True)
            print(f"Varlık depolama dizini hazır: {storage} (GitHub entegrasyonu devre dışı, CDN fallback devrede)")
            return 0

    urls = get_assets(
        category=args.category,
        gender=args.gender,
        style=args.style,
        count=args.count,
        seed=args.seed,
        width=args.width,
        height=args.height
    )

    downloaded_files = []
    if args.download:
        out_dir = Path(args.output) if args.output else (root / config.get("storage_dir", DEFAULT_STORAGE_DIR) / args.category)
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = ".svg" if args.category == "avatars" else ".jpg"
        for i, url in enumerate(urls):
            seed_part = f"_{args.seed}" if args.seed else ""
            filename = f"{args.category}{seed_part}_{i+1}{ext}"
            file_path = out_dir / filename
            success = download_file(url, file_path)
            if success:
                try:
                    rel_path = file_path.relative_to(root)
                    downloaded_files.append(str(rel_path).replace("\\", "/"))
                except ValueError:
                    downloaded_files.append(str(file_path).replace("\\", "/"))
            else:
                downloaded_files.append(url)

    result = {
        "status": "ok",
        "category": args.category,
        "count": len(urls),
        "urls": urls,
        "downloaded_files": downloaded_files if args.download else []
    }

    if args.json or args.url_only:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[{args.category.upper()}] {len(urls)} görsel varlığı üretildi:")
        for idx, u in enumerate(urls, 1):
            if downloaded_files:
                print(f"  {idx}. URL: {u} -> İndirilen: {downloaded_files[idx-1]}")
            else:
                print(f"  {idx}. {u}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
