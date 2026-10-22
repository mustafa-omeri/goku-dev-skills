#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEO & Web Standartları Denetleyicisi (SEO Checker).

HTML dosyalarını veya derlenmiş web çıktılarını tarayarak temel SEO, SERP,
Open Graph, Twitter Cards, JSON-LD Schema ve semantik başlık hiyerarşisi
uygunluğunu doğrular.

Kullanım:
    python .agent/skills/seo-growth/scripts/seo_checker.py <dosya-veya-dizin>
    python .agent/skills/seo-growth/scripts/seo_checker.py index.html --strict
    python .agent/skills/seo-growth/scripts/seo_checker.py dist/ --json
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional

# Windows konsol UTF-8 desteği
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


class PageSeoExtractor(HTMLParser):
    """HTML sayfasından SEO ile ilgili kritik etiketleri çıkaran parser."""

    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_h1 = False
        self.in_script_ldjson = False

        self.title_text = []
        self.h1_texts: List[str] = []
        self.current_h1 = []
        self.meta_tags: List[Dict[str, str]] = []
        self.link_tags: List[Dict[str, str]] = []
        self.images: List[Dict[str, str]] = []
        self.ld_json_scripts: List[str] = []
        self.current_ld_json = []

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        attr_dict = {k.lower(): v for k, v in attrs if v is not None}

        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
            self.current_h1 = []
        elif tag == "meta":
            self.meta_tags.append(attr_dict)
        elif tag == "link":
            self.link_tags.append(attr_dict)
        elif tag == "img":
            self.images.append(attr_dict)
        elif tag == "script":
            script_type = attr_dict.get("type", "").lower()
            if script_type == "application/ld+json":
                self.in_script_ldjson = True
                self.current_ld_json = []

    def handle_endtag(self, tag: str):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
            text = "".join(self.current_h1).strip()
            if text:
                self.h1_texts.append(text)
        elif tag == "script" and self.in_script_ldjson:
            self.in_script_ldjson = False
            raw_script = "".join(self.current_ld_json).strip()
            if raw_script:
                self.ld_json_scripts.append(raw_script)

    def handle_data(self, data: str):
        if self.in_title:
            self.title_text.append(data)
        elif self.in_h1:
            self.current_h1.append(data)
        elif self.in_script_ldjson:
            self.current_ld_json.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_text).strip()


def analyze_html_content(content: str, file_path: str = "") -> Dict[str, Any]:
    """HTML içeriğini SEO kurallarına göre inceler."""
    parser = PageSeoExtractor()
    try:
        parser.feed(content)
    except Exception as e:
        return {
            "file": file_path,
            "status": "ERROR",
            "errors": [f"HTML ayrıştırma hatası: {e}"],
            "warnings": [],
            "score": 0
        }

    errors: List[str] = []
    warnings: List[str] = []
    checks: Dict[str, Any] = {}

    # 1. Title Tag Kontrolü (İdeal: 30-65 karakter)
    title = parser.title
    checks["title"] = title
    if not title:
        errors.append("E1: <title> etiketi eksik veya boş.")
    elif len(title) < 20:
        warnings.append(f"W1: <title> çok kısa ({len(title)} karakter). Önerilen: 30-65 karakter.")
    elif len(title) > 70:
        warnings.append(f"W2: <title> SERP sınırını aşabilir ({len(title)} karakter). Önerilen: 30-65 karakter.")

    # 2. Meta Description Kontrolü (İdeal: 70-160 karakter)
    desc = None
    viewport = None
    robots_meta = None
    og_tags: Dict[str, str] = {}
    twitter_tags: Dict[str, str] = {}

    for m in parser.meta_tags:
        name = m.get("name", "").lower()
        prop = m.get("property", "").lower()
        cnt = m.get("content", "")

        if name == "description":
            desc = cnt
        elif name == "viewport":
            viewport = cnt
        elif name == "robots":
            robots_meta = cnt
        elif prop.startswith("og:"):
            og_tags[prop] = cnt
        elif name.startswith("twitter:"):
            twitter_tags[name] = cnt

    checks["description"] = desc
    checks["viewport"] = viewport
    checks["robots"] = robots_meta
    checks["open_graph"] = og_tags
    checks["twitter_card"] = twitter_tags

    if not desc:
        errors.append("E2: <meta name=\"description\"> eksik veya boş.")
    elif len(desc) < 50:
        warnings.append(f"W3: Meta description çok kısa ({len(desc)} karakter). Önerilen: 70-160 karakter.")
    elif len(desc) > 165:
        warnings.append(f"W4: Meta description arama motorunda kesilebilir ({len(desc)} karakter > 160).")

    # 3. Viewport (Mobil Uyum)
    if not viewport:
        errors.append("E3: Mobil uyumluluk için <meta name=\"viewport\"> etiketi eksik.")

    # 4. Canonical Link
    canonical = None
    for link in parser.link_tags:
        rel = link.get("rel", "").lower()
        if rel == "canonical":
            canonical = link.get("href", "")
            break
    checks["canonical"] = canonical
    if not canonical:
        warnings.append("W5: <link rel=\"canonical\"> etiketi bulunamadı (kopya içerik önleme için önerilir).")

    # 5. OpenGraph Kontrolleri (og:title, og:description, og:image, og:url)
    missing_og = []
    for req_og in ("og:title", "og:description", "og:image"):
        if req_og not in og_tags or not og_tags[req_og].strip():
            missing_og.append(req_og)
    if missing_og:
        warnings.append(f"W6: Sosyal medya önizlemesi için kritik OpenGraph etiketleri eksik: {', '.join(missing_og)}")

    # 6. Heading 1 Kontrolü (Tam olarak 1 adet olmalı)
    h1_count = len(parser.h1_texts)
    checks["h1_count"] = h1_count
    checks["h1_samples"] = parser.h1_texts[:2]
    if h1_count == 0:
        errors.append("E4: Sayfada hiç <h1> başlığı bulunamadı. Sayfa başına tam 1 adet <h1> zorunludur.")
    elif h1_count > 1:
        warnings.append(f"W7: Sayfada birden fazla <h1> tespit edildi ({h1_count} adet). Sayfa başına tek bir ana <h1> önerilir.")

    # 7. Görsel Alt Etiketi Kontrolü
    images_without_alt = [img.get("src", "unknown") for img in parser.images if "alt" not in img or not img.get("alt", "").strip()]
    checks["total_images"] = len(parser.images)
    checks["images_missing_alt"] = len(images_without_alt)
    if images_without_alt:
        warnings.append(f"W8: {len(images_without_alt)} adet görselde boş veya eksik 'alt' etiketi var.")

    # 8. JSON-LD Structured Data Kontrolü
    checks["json_ld_count"] = len(parser.ld_json_scripts)
    valid_ld_json = 0
    for script_raw in parser.ld_json_scripts:
        try:
            parsed_json = json.loads(script_raw)
            if isinstance(parsed_json, dict) and "@context" in parsed_json:
                valid_ld_json += 1
        except json.JSONDecodeError:
            errors.append("E5: <script type=\"application/ld+json\"> içeriği geçerli bir JSON formatında değil.")

    checks["valid_json_ld"] = valid_ld_json
    if len(parser.ld_json_scripts) == 0:
        warnings.append("W9: JSON-LD yapılandırılmış veri (Schema.org markup) tespit edilemedi.")

    # Puanlama
    total_deductions = (len(errors) * 20) + (len(warnings) * 5)
    score = max(0, 100 - total_deductions)

    return {
        "file": file_path,
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "score": score,
        "checks": checks,
        "errors": errors,
        "warnings": warnings
    }


def scan_path(target_path: Path) -> List[Dict[str, Any]]:
    """Belirtilen dosya veya dizini tarar."""
    results = []
    if target_path.is_file():
        if target_path.suffix.lower() in (".html", ".htm"):
            content = target_path.read_text(encoding="utf-8", errors="replace")
            results.append(analyze_html_content(content, str(target_path)))
    elif target_path.is_dir():
        for root, dirs, files in os.walk(target_path):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".agent", "target", "build"}]
            for f in files:
                if f.lower().endswith((".html", ".htm")):
                    full_p = Path(root) / f
                    content = full_p.read_text(encoding="utf-8", errors="replace")
                    results.append(analyze_html_content(content, str(full_p)))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="SEO & SERP Architecture Auditor")
    parser.add_argument("target", nargs="?", default=".", help="Hedef HTML dosyası veya dizin")
    parser.add_argument("--strict", action="store_true", help="Uyarıları da hata sayarak exit 1 döndürür")
    parser.add_argument("--json", action="store_true", help="Sonuçları JSON formatında basar")

    args = parser.parse_args()
    target_path = Path(args.target).resolve()

    if not target_path.exists():
        if args.json:
            print(json.dumps({"error": f"Yol bulunamadı: {target_path}"}, ensure_ascii=False))
        else:
            print(f"[HATA] Belirtilen hedef bulunamadı: {target_path}", file=sys.stderr)
        return 1

    results = scan_path(target_path)

    if not results:
        if args.json:
            print(json.dumps({"message": "Taranacak HTML dosyası bulunamadı.", "results": []}, ensure_ascii=False))
        else:
            print(f"[BİLGİ] {target_path} konumunda incelenecek HTML dosyası bulunamadı.")
        return 0

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
        has_errors = any(len(r["errors"]) > 0 for r in results)
        has_warnings = any(len(r["warnings"]) > 0 for r in results)
        if has_errors or (args.strict and has_warnings):
            return 1
        return 0

    # İnsan dostu konsol çıktısı
    print("=" * 70)
    print("🔍 SEO & SERP Architecture Denetim Raporu")
    print("=" * 70)

    total_errors = 0
    total_warnings = 0

    for r in results:
        file_name = r["file"]
        status = r["status"]
        score = r["score"]
        errs = r["errors"]
        warns = r["warnings"]
        total_errors += len(errs)
        total_warnings += len(warns)

        status_badge = f"\033[32m[PASS]\033[0m" if status == "PASS" else f"\033[31m[FAIL]\033[0m"
        print(f"\nDosya: \033[1m{file_name}\033[0m {status_badge} (SEO Skoru: {score}/100)")
        print("-" * 70)

        if errs:
            print("  \033[31mHatalar:\033[0m")
            for e in errs:
                print(f"    ❌ {e}")
        if warns:
            print("  \033[33mUyarılar:\033[0m")
            for w in warns:
                print(f"    ⚠️ {w}")
        if not errs and not warns:
            print("  ✅ Temel SEO kuralları, başlıklar ve meta etiketler eksiksiz.")

    print("\n" + "=" * 70)
    print(f"ÖZET: {len(results)} dosya tarandı | {total_errors} Hata | {total_warnings} Uyarı")

    if total_errors > 0 or (args.strict and total_warnings > 0):
        print("SONUÇ: ❌ SEO denetiminde eksikler tespit edildi.")
        return 1

    print("SONUÇ: ✅ SEO denetimi başarıyla tamamlandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
