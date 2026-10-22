#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEO & Web Standartları Denetleyicisi (SEO Checker).

HTML dosyalarını veya derlenmiş web çıktılarını tarayarak temel SEO, SERP,
Open Graph, Twitter Cards, JSON-LD Schema, semantik başlık hiyerarşisi,
hreflang, robots.txt, AI crawler direktifleri ve içerik bayatlaması (Content Drift)
uygunluğunu doğrular.

Kullanım:
    python .agent/skills/seo-growth/scripts/seo_checker.py <dosya-veya-dizin>
    python .agent/skills/seo-growth/scripts/seo_checker.py index.html --strict
    python .agent/skills/seo-growth/scripts/seo_checker.py dist/ --json
    python .agent/skills/seo-growth/scripts/seo_checker.py robots.txt
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

CURRENT_YEAR = 2026
STALE_YEAR_REGEX = re.compile(r"\b(201\d|202[0-4])\b")


class PageSeoExtractor(HTMLParser):
    """HTML sayfasından SEO ile ilgili kritik etiketleri çıkaran parser."""

    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_h1 = False
        self.in_p = False
        self.in_script_ldjson = False

        self.title_text = []
        self.h1_texts: List[str] = []
        self.current_h1 = []
        self.paragraphs: List[str] = []
        self.current_p = []
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
        elif tag == "p":
            self.in_p = True
            self.current_p = []
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
        elif tag == "p":
            self.in_p = False
            text = "".join(self.current_p).strip()
            if text:
                self.paragraphs.append(text)
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
        elif self.in_p:
            self.current_p.append(data)
        elif self.in_script_ldjson:
            self.current_ld_json.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_text).strip()


def analyze_robots_txt(content: str, file_path: str = "robots.txt") -> Dict[str, Any]:
    """robots.txt dosyasını arama motoru ve AI bot politikaları açısından inceler."""
    errors: List[str] = []
    warnings: List[str] = []
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

    if not lines:
        warnings.append("W_ROBOTS_0: robots.txt dosyası boş veya sadece yorum satırlarından oluşuyor.")

    has_sitemap = any(re.match(r"^sitemap\s*:", line, re.IGNORECASE) for line in lines)
    if not has_sitemap:
        warnings.append("W_ROBOTS_1: robots.txt içinde 'Sitemap:' direktifi bulunamadı.")

    raw_lower = content.lower()
    if re.search(r"user-agent:\s*\*\s*[\r\n]+disallow:\s*/\s*($|[\r\n])", raw_lower):
        warnings.append("W_ROBOTS_2: Tüm arama motorları için 'Disallow: /' tanımlanmış; site indekslenmeye kapalı olabilir.")

    known_ai_bots = ["gptbot", "chatgpt-user", "perplexitybot", "claudebot", "anthropic-ai", "google-extended", "bytespider", "ccbot"]
    configured_ai_bots = [bot for bot in known_ai_bots if bot in raw_lower]

    checks = {
        "has_sitemap": has_sitemap,
        "configured_ai_bots": configured_ai_bots,
        "lines_count": len(lines)
    }

    if not configured_ai_bots:
        warnings.append("W_ROBOTS_3: Modern AI botları (ChatGPT-User, PerplexityBot vb.) için özel politika bulunamadı (Bkz. ai-crawler-matrix.md).")

    score = max(0, 100 - (len(errors) * 20) - (len(warnings) * 10))

    return {
        "file": file_path,
        "type": "robots.txt",
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "score": score,
        "checks": checks,
        "errors": errors,
        "warnings": warnings
    }


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

    # 4. Canonical Link & hreflang
    canonical = None
    hreflangs: Dict[str, str] = {}
    for link in parser.link_tags:
        rel = link.get("rel", "").lower()
        if rel == "canonical":
            canonical = link.get("href", "")
        elif rel == "alternate" and "hreflang" in link:
            hl = link.get("hreflang", "").lower()
            hreflangs[hl] = link.get("href", "")

    checks["canonical"] = canonical
    checks["hreflangs"] = hreflangs

    if not canonical:
        warnings.append("W5: <link rel=\"canonical\"> etiketi bulunamadı (kopya içerik önleme için önerilir).")

    if hreflangs and len(hreflangs) > 1:
        if "x-default" not in hreflangs:
            warnings.append("W11: Çok dilli hreflang tanımları tespit edildi ancak fallback için 'x-default' etiketi eksik.")

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

    # 8. JSON-LD Structured Data & Types
    checks["json_ld_count"] = len(parser.ld_json_scripts)
    valid_ld_json = 0
    schema_types = []
    for script_raw in parser.ld_json_scripts:
        try:
            parsed_json = json.loads(script_raw)
            if isinstance(parsed_json, dict) and "@context" in parsed_json:
                valid_ld_json += 1
                if "@type" in parsed_json:
                    schema_types.append(parsed_json["@type"])
        except json.JSONDecodeError:
            errors.append("E5: <script type=\"application/ld+json\"> içeriği geçerli bir JSON formatında değil.")

    checks["valid_json_ld"] = valid_ld_json
    checks["schema_types"] = schema_types
    if len(parser.ld_json_scripts) == 0:
        warnings.append("W9: JSON-LD yapılandırılmış veri (Schema.org markup) tespit edilemedi.")

    # 9. İçerik Bayatlaması / Content Decay Kontrolü (Eski Yıllar)
    stale_in_title = STALE_YEAR_REGEX.search(title)
    stale_in_h1 = STALE_YEAR_REGEX.search(parser.h1_texts[0]) if parser.h1_texts else None
    if stale_in_title or stale_in_h1:
        found_year = stale_in_title.group(1) if stale_in_title else stale_in_h1.group(1)
        warnings.append(f"W10: Başlıkta geçmiş yıl ({found_year}) tespit edildi. İçerik güncelliğini ve Content Drift durumunu denetleyin.")

    # 10. Robots Meta & Noindex Kontrolü
    if robots_meta:
        robots_lower = robots_meta.lower()
        if "noindex" in robots_lower:
            warnings.append("W12: <meta name=\"robots\"> etiketinde 'noindex' direktifi var; sayfa arama motorları tarafından indekslenmeyecektir.")
        if "noai" in robots_lower or "noimageai" in robots_lower:
            checks["ai_crawler_restriction"] = True

    # 11. Answer Block / Citation Readiness Kontrolü
    # 40-70 kelimelik net tanım paragraflarını arar
    answer_blocks = [p for p in parser.paragraphs if 35 <= len(p.split()) <= 75]
    checks["answer_block_candidates"] = len(answer_blocks)

    # Puanlama
    total_deductions = (len(errors) * 20) + (len(warnings) * 5)
    score = max(0, 100 - total_deductions)

    return {
        "file": file_path,
        "type": "html",
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
        elif target_path.name.lower() == "robots.txt":
            content = target_path.read_text(encoding="utf-8", errors="replace")
            results.append(analyze_robots_txt(content, str(target_path)))
    elif target_path.is_dir():
        for root, dirs, files in os.walk(target_path):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".agent", "target", "build"}]
            for f in files:
                if f.lower().endswith((".html", ".htm")):
                    full_p = Path(root) / f
                    content = full_p.read_text(encoding="utf-8", errors="replace")
                    results.append(analyze_html_content(content, str(full_p)))
        # Kök dizinde robots.txt varsa onu da denetime ekle
        robots_file = target_path / "robots.txt"
        if robots_file.is_file():
            content = robots_file.read_text(encoding="utf-8", errors="replace")
            results.append(analyze_robots_txt(content, str(robots_file)))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="SEO & SERP Architecture Auditor")
    parser.add_argument("target", nargs="?", default=".", help="Hedef HTML/robots.txt dosyası veya dizin")
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
            print(json.dumps({"message": "Taranacak HTML veya robots.txt dosyası bulunamadı.", "results": []}, ensure_ascii=False))
        else:
            print(f"[BİLGİ] {target_path} konumunda incelenecek HTML veya robots.txt dosyası bulunamadı.")
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
            print("  ✅ Temel SEO kuralları, başlıklar ve direktifler eksiksiz.")

    print("\n" + "=" * 70)
    print(f"ÖZET: {len(results)} dosya tarandı | {total_errors} Hata | {total_warnings} Uyarı")

    if total_errors > 0 or (args.strict and total_warnings > 0):
        print("SONUÇ: ❌ SEO denetiminde eksikler tespit edildi.")
        return 1

    print("SONUÇ: ✅ SEO denetimi başarıyla tamamlandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
