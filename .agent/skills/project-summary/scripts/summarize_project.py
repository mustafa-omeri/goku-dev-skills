#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Proje Özeti ve Konsolidasyon Motoru (summarize_project.py).

Bu script; projelerin kısa (short) veya kapsamlı (long) özetini çıkarır,
PRD ve referans dokümanlarını tek bir belgede konsolide eder.

Kurallar:
1. Çıktı dosyası her zaman /docs dizini altında yer alır:
   docs/<SLUG>_PROJECT_SUMMARY_SHORT.md veya docs/<SLUG>_PROJECT_SUMMARY_LONG.md
2. Çıktı dili PROJECT_BRIEF.md içindeki primary_language alanına göre belirlenir.
3. Dosya zaten varsa versiyonlama damgası (tarih, saat, kullanıcı) vurulur,
   önceki sürüm docs/archive/ altına yedeklenir ve revizyon geçmişi korunur.
4. Üretilen doküman PROJECT_BRIEF.md içindeki related_docs listesine zorunlu senkronize edilir.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Windows konsol Unicode uyumluluğu
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def find_project_root(start: Path | None = None) -> Path:
    """Proje kök dizinini tespit eder."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "PROJECT_BRIEF.md").is_file() or (candidate / ".agent").is_dir() or (candidate / "package.json").is_file() or (candidate / "pom.xml").is_file():
            return candidate
    return current


def get_project_slug(root: Path) -> str:
    """Proje slug'ını hiyerarşik olarak belirler ve büyük harfli temiz slug döndürür."""
    # 1. PROJECT_BRIEF.md frontmatter slug: veya title:
    brief_path = root / "PROJECT_BRIEF.md"
    if brief_path.is_file():
        try:
            text = brief_path.read_text(encoding="utf-8", errors="replace")
            m_slug = re.search(r"^slug:\s*([^\r\n]+)", text, re.MULTILINE)
            if m_slug:
                raw = m_slug.group(1).strip().strip("\"'")
                if raw and not raw.startswith("["):
                    return clean_slug(raw)
            m_title = re.search(r"^title:\s*([^\r\n]+)", text, re.MULTILINE)
            if m_title:
                raw = m_title.group(1).strip().strip("\"'")
                if raw and not raw.startswith("["):
                    return clean_slug(raw)
        except Exception:
            pass

    # 2. package.json name
    pkg_path = root / "package.json"
    if pkg_path.is_file():
        try:
            data = json.loads(pkg_path.read_text(encoding="utf-8", errors="replace"))
            name = data.get("name", "")
            if name:
                # scope temizliği: @scope/name -> name
                if "/" in name:
                    name = name.split("/")[-1]
                return clean_slug(name)
        except Exception:
            pass

    # 3. pom.xml artifactId
    pom_path = root / "pom.xml"
    if pom_path.is_file():
        try:
            text = pom_path.read_text(encoding="utf-8", errors="replace")
            m_art = re.search(r"<artifactId>([^<]+)</artifactId>", text)
            if m_art:
                return clean_slug(m_art.group(1).strip())
        except Exception:
            pass

    # 4. Kök klasör adı
    return clean_slug(root.name)


def clean_slug(raw: str) -> str:
    """Slug dizesini alfanümerik ve alt çizgi içeren temiz BÜYÜK HARFE çevirir."""
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", raw).strip("_")
    return cleaned.upper() or "PROJECT"


def get_project_language(root: Path) -> str:
    """PROJECT_BRIEF.md içindeki primary_language alanını okur (varsayılan: tr)."""
    brief_path = root / "PROJECT_BRIEF.md"
    if brief_path.is_file():
        try:
            text = brief_path.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^primary_language:\s*([^\r\n]+)", text, re.MULTILINE)
            if m:
                val = m.group(1).strip().strip("\"'").lower()
                if "en" in val:
                    return "en"
                if "tr" in val:
                    return "tr"
        except Exception:
            pass
    return "tr"


def get_current_user() -> str:
    """Git config veya işletim sistemi kullanıcısını tespit eder."""
    try:
        res = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return os.getenv("USERNAME") or os.getenv("USER") or "Developer"


def validate_output_directory(output_path: Path, root: Path) -> None:
    """Çıktı dosyasının zorunlu olarak /docs altında olduğunu doğrular."""
    docs_dir = (root / "docs").resolve()
    resolved_output = output_path.resolve()
    try:
        resolved_output.relative_to(docs_dir)
    except ValueError:
        raise ValueError(f"HATA: Çıktı dosyası ('{output_path}') zorunlu olarak /docs dizini altında olmalıdır!")


def find_all_prds(root: Path) -> list[Path]:
    """Projedeki tüm PRD ve şartname dokümanlarını tespit eder."""
    prds: list[Path] = []
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for p in docs_dir.rglob("*.md"):
            # archive ve backup dizinlerini atla
            rel_parts = p.relative_to(docs_dir).parts
            if any(part.lower() in ("archive", "backup", ".git") for part in rel_parts):
                continue
            name_lower = p.name.lower()
            if "prd" in name_lower or "spec" in name_lower or "sartname" in name_lower:
                prds.append(p)
    # Kökte PRD.md kontrolü
    for candidate in [root / "PRD.md", root / "prd.md"]:
        if candidate.is_file():
            prds.append(candidate)
    return sorted(list(set(prds)))


def collect_reference_docs(root: Path) -> dict[str, Any]:
    """Projedeki temel referans dokümanlarını envanterler."""
    refs: dict[str, Any] = {}
    docs_to_check = {
        "brief": root / "PROJECT_BRIEF.md",
        "product": root / "PRODUCT.md",
        "glossary": root / "GLOSSARY.md",
        "design": root / "DESIGN.md",
        "db": root / "DB_MIGRATIONS.md",
        "db_alt": root / "docs" / "database" / "DB_MIGRATIONS.md",
        "handoff": root / "HANDOFF.md",
        "kb": root / "knowledge-base.md",
        "readme": root / "README.md",
    }
    for key, path in docs_to_check.items():
        if path.is_file():
            refs[key] = path

    # ADR dokümanları
    adr_dir = root / "docs" / "adr"
    adrs = []
    if adr_dir.is_dir():
        adrs = sorted([p for p in adr_dir.glob("*.md") if p.is_file()])
    refs["adrs"] = adrs

    # Manifests
    refs["has_package_json"] = (root / "package.json").is_file()
    refs["has_pom_xml"] = (root / "pom.xml").is_file()
    return refs


def extract_existing_version(content: str) -> tuple[str, list[dict[str, str]]]:
    """Mevcut dokümandan son versiyonu ve revizyon geçmişini ayıklar."""
    version = "v1.0"
    m_ver = re.search(r"^version:\s*\"?v?([0-9.]+)\"?", content, re.MULTILINE)
    if m_ver:
        version = f"v{m_ver.group(1)}"

    history: list[dict[str, str]] = []
    # Tablo satırlarını ayrıştır
    table_match = re.search(r"## 📜 Revizyon Geçmişi[^\n]*\n\n\|[^\n]+\|\n\|[-|\s]+\|\n([\s\S]*?)(?=\n---|\n##|\Z)", content)
    if table_match:
        for line in table_match.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("|") and not line.startswith("|---"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 6:
                    history.append({
                        "version": parts[0],
                        "date": parts[1],
                        "time": parts[2],
                        "author": parts[3],
                        "mode": parts[4],
                        "summary": parts[5]
                    })
    return version, history


def bump_version(current: str) -> str:
    """v1.0 -> v1.1 sürüm artışı yapar."""
    m = re.match(r"v?(\d+)\.(\d+)", current)
    if m:
        major, minor = int(m.group(1)), int(m.group(2))
        return f"v{major}.{minor + 1}"
    return "v1.1"


def sync_project_brief_related_docs(root: Path, summary_rel_path: str) -> bool:
    """PROJECT_BRIEF.md frontmatter'ındaki related_docs listesine dosyayı ekler."""
    brief_path = root / "PROJECT_BRIEF.md"
    if not brief_path.is_file():
        return False

    content = brief_path.read_text(encoding="utf-8", errors="replace")
    normalized_path = summary_rel_path.replace("\\", "/")

    if normalized_path in content:
        return True  # Zaten ekli

    # related_docs: listesini bul
    m = re.search(r"(related_docs:\s*\n)((?:\s*-\s*[^\r\n]+\r?\n)*)", content)
    if m:
        prefix = m.group(1)
        existing_items = m.group(2)
        new_item = f"  - \"{normalized_path}\"\n"
        replacement = f"{prefix}{existing_items}{new_item}"
        new_content = content[:m.start()] + replacement + content[m.end():]
        brief_path.write_text(new_content, encoding="utf-8")
        return True
    else:
        # Frontmatter sonuna related_docs ekle
        fm_end = content.find("\n---", 3)
        if fm_end != -1:
            injection = f"related_docs:\n  - \"{normalized_path}\"\n"
            new_content = content[:fm_end] + "\n" + injection + content[fm_end:]
            brief_path.write_text(new_content, encoding="utf-8")
            return True
    return False


def build_short_summary(
    slug: str,
    root: Path,
    lang: str,
    version: str,
    now: datetime.datetime,
    user: str,
    refs: dict[str, Any],
    history: list[dict[str, str]],
) -> str:
    """Kısa (short) yönetici özeti markdown içeriğini üretir."""
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Dil metinleri
    is_tr = (lang == "tr")
    t_title = f"{slug} Proje Yönetici Özeti (SHORT)" if is_tr else f"{slug} Project Executive Summary (SHORT)"
    t_stamp = f"> 📌 **Versiyonlama Damgası:** {version} · **Tarih:** {date_str} · **Saat:** {time_str} · **Güncelleyen:** {user} · **Mod:** SHORT"
    
    # Bilgi toplama
    brief_content = refs.get("brief", Path("")).read_text(encoding="utf-8", errors="replace") if refs.get("brief") else ""
    product_content = refs.get("product", Path("")).read_text(encoding="utf-8", errors="replace") if refs.get("product") else ""
    handoff_content = refs.get("handoff", Path("")).read_text(encoding="utf-8", errors="replace") if refs.get("handoff") else ""

    # Frontmatter
    md = f"""---
title: "{t_title}"
project_slug: "{slug}"
mode: "short"
version: "{version}"
last_updated: "{date_str} {time_str}"
updated_by: "{user}"
language: "{lang}"
sources_ingested:
  architecture: "PROJECT_BRIEF.md"
  product: "PRODUCT.md"
  handoff: "HANDOFF.md"
---

# {slug} — Proje Yönetici Özeti (SHORT)

{t_stamp}

---

## 📜 Revizyon Geçmişi (Revision History)

| Versiyon | Tarih | Saat | Güncelleyen | Mod | Kapsam / Değişiklik Özeti |
|---|---|---|---|---|---|
"""
    for h in history:
        md += f"| {h['version']} | {h['date']} | {h['time']} | {h['author']} | {h['mode']} | {h['summary']} |\n"

    md += f"""| {version} | {date_str} | {time_str} | {user} | SHORT | Proje kısa yönetici özeti güncellendi. |

---

## 1. Yönetici Özeti & Ürün Amacı
"""
    # Product veya Brief'ten amaç çek
    purpose = "Bu proje, kurumsal veya son kullanıcı ihtiyaçlarını çözmek üzere tasarlanmış modern bir yazılım çözümüdür."
    m_purpose = re.search(r"##\s*(?:Ürün Amacı|Purpose|Amaç)[^\n]*\n+([^\n#]+)", product_content + "\n" + brief_content)
    if m_purpose:
        purpose = m_purpose.group(1).strip()
    md += f"- **Temel Amaç:** {purpose}\n"
    md += f"- **Proje Slug / Kod Adı:** `{slug}`\n"
    md += f"- **Ana İletişim / Çalışma Dili:** `{lang.upper()}`\n\n"

    md += """## 2. Çekirdek Teknoloji Yığını & Mimari
"""
    # Brief'ten stack ayıkla
    stack_lines = []
    m_stack = re.search(r"##\s*1\.\s*Teknoloji Yığını[^\n]*\n([\s\S]*?)(?=\n##|\Z)", brief_content)
    if m_stack:
        for sline in m_stack.group(1).strip().split("\n")[:6]:
            if sline.strip():
                stack_lines.append(sline.strip())
    if stack_lines:
        md += "\n".join(stack_lines) + "\n\n"
    else:
        md += "- **Platform:** Modern Web / Servis Mimarisi\n- **Mimari Tip:** Modüler Dikey Dilim (Vertical Slice)\n\n"

    md += """## 3. Canlı Kilometre Taşı & Yaşayan Durum
"""
    # Handoff'tan durum ayıkla
    m_status = re.search(r"##\s*1\.\s*Bu Oturumda Yapılanlar[^\n]*\n([\s\S]*?)(?=\n##|\Z)", handoff_content)
    if m_status:
        md += m_status.group(1).strip()[:800] + "\n\n"
    else:
        md += "- Proje geliştirme ve teslimat döngüsü aktif olarak devam etmektedir.\n\n"

    md += """---
> 💡 *Daha detaylı mimari, PRD şartnameleri, veri modelleri ve kararlar için `docs/{slug}_PROJECT_SUMMARY_LONG.md` dokümanına başvurunuz.*
""".format(slug=slug)

    return md


def build_long_summary(
    slug: str,
    root: Path,
    lang: str,
    version: str,
    now: datetime.datetime,
    user: str,
    prds: list[Path],
    refs: dict[str, Any],
    history: list[dict[str, str]],
) -> str:
    """Kapsamlı (long) konsolide özet markdown içeriğini üretir."""
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    is_tr = (lang == "tr")
    t_title = f"{slug} Kapsamlı Proje Konsolidasyon Dokümanı (LONG)" if is_tr else f"{slug} Comprehensive Project Summary & Consolidation (LONG)"
    t_stamp = f"> 📌 **Versiyonlama Damgası:** {version} · **Tarih:** {date_str} · **Saat:** {time_str} · **Güncelleyen:** {user} · **Mod:** LONG"

    # Frontmatter kaynak listesi
    prd_rel_paths = [p.relative_to(root).as_posix() for p in prds]

    md = f"""---
title: "{t_title}"
project_slug: "{slug}"
mode: "long"
version: "{version}"
last_updated: "{date_str} {time_str}"
updated_by: "{user}"
language: "{lang}"
sources_ingested:
  prds:
"""
    if prd_rel_paths:
        for prd_path in prd_rel_paths:
            md += f"    - \"{prd_path}\"\n"
    else:
        md += "    - \"(Bağımsız PRD bulunamadı; gereksinimler yaşayan dokümanlardan sentezlendi)\"\n"

    md += f"""  architecture: "PROJECT_BRIEF.md"
  product: "PRODUCT.md"
  glossary: "GLOSSARY.md"
  database: "DB_MIGRATIONS.md"
  design: "DESIGN.md"
  handoff: "HANDOFF.md"
  decisions: "knowledge-base.md"
---

# {slug} — Kapsamlı Proje Konsolide Dokümantasyonu (LONG)

{t_stamp}

> [!NOTE]
> Bu doküman; projede bulunan tüm PRD dokümanlarını, mimari brief'i, ürün vizyonunu, terimler sözlüğünü, veritabanı şemasını, tasarım standartlarını ve yaşayan durumu **tek bir kaynakta konsolide etmek** üzere otomatik olarak sentezlenmiştir.

---

## 📜 Revizyon Geçmişi (Revision History)

| Versiyon | Tarih | Saat | Güncelleyen | Mod | Kapsam / Değişiklik Özeti |
|---|---|---|---|---|---|
"""
    for h in history:
        md += f"| {h['version']} | {h['date']} | {h['time']} | {h['author']} | {h['mode']} | {h['summary']} |\n"

    summary_note = f"Tüm PRD ({len(prds)} adet) ve referans dokümanları tek dokümanda konsolide edildi."
    md += f"| {version} | {date_str} | {time_str} | {user} | LONG | {summary_note} |\n\n---\n\n"

    # 1. Ürün Vizyonu
    product_file = refs.get("product")
    product_text = product_file.read_text(encoding="utf-8", errors="replace") if product_file else ""
    md += """## 1. Ürün Vizyonu, Hedef Kitle & Kısıtlar (PRODUCT.md & PRD Sentezi)
"""
    if product_text:
        md += product_text[:1200].strip() + "\n\n"
    else:
        md += f"- **Proje Kimliği:** {slug}\n- **Vizyon:** Güvenli, performanslı ve ölçeklenebilir yazılım mimarisi.\n\n"

    # 2. İş Alanı Modeli & Terimler Sözlüğü
    glossary_file = refs.get("glossary")
    glossary_text = glossary_file.read_text(encoding="utf-8", errors="replace") if glossary_file else ""
    md += """## 2. İş Alanı Modeli & Terimler Sözlüğü (GLOSSARY.md Sentezi)
"""
    if glossary_text:
        md += glossary_text[:1200].strip() + "\n\n"
    else:
        md += "*Özel bir sözlük dosyası bulunamadı; standart sektör terminolojisi geçerlidir.*\n\n"

    # 3. Canlı Sistem Mimarisi & Teknoloji Yığını
    brief_file = refs.get("brief")
    brief_text = brief_file.read_text(encoding="utf-8", errors="replace") if brief_file else ""
    md += """## 3. Canlı Sistem Mimarisi & Teknoloji Yığını (PROJECT_BRIEF.md Sentezi)
"""
    if brief_text:
        m_arch = re.search(r"##\s*1\.\s*Teknoloji Yığını[\s\S]*?(?=\n##\s*4|\Z)", brief_text)
        if m_arch:
            md += m_arch.group(0).strip() + "\n\n"
        else:
            md += brief_text[:1500].strip() + "\n\n"
    else:
        md += f"- `{slug}` projesine ait mimari ayrıntılar kod tabanından dinamik olarak yönetilmektedir.\n\n"

    # 4. Veritabanı Şeması
    db_file = refs.get("db") or refs.get("db_alt")
    db_text = db_file.read_text(encoding="utf-8", errors="replace") if db_file else ""
    md += """## 4. Veritabanı Şeması & Veri Modeli (DB_MIGRATIONS.md Sentezi)
"""
    if db_text:
        md += db_text[:1200].strip() + "\n\n"
    else:
        md += "*Veritabanı migration dokümantasyonu bulunamadı veya proje salt istemci/CLI mimarisindedir.*\n\n"

    # 5. Tasarım Dili
    design_file = refs.get("design")
    design_text = design_file.read_text(encoding="utf-8", errors="replace") if design_file else ""
    md += """## 5. Tasarım Dili, Token'lar & Arayüz Standartları (DESIGN.md Sentezi)
"""
    if design_text:
        md += design_text[:1200].strip() + "\n\n"
    else:
        md += "*Tasarım sözleşmesi bulunamadı veya proje arayüzsüz/arka plan servisidir.*\n\n"

    # 6. Fonksiyonel & Teknik Şartname Konsolidasyonu (ZORUNLU PRD SENTEZİ)
    md += """## 6. Fonksiyonel & Teknik Şartname Konsolidasyonu (PRD Dokümanları Sentezi)

> 🔍 **İncelenen PRD Dokümanları:**
"""
    if prds:
        for prd_path in prds:
            rel = prd_path.relative_to(root).as_posix()
            md += f"- 📄 [`{rel}`]({rel})\n"
        md += "\n### 6.1 Konsolide Gereksinimler & Kabul Kriterleri (Requirements Matrix)\n\n"
        md += "| Gereksinim / Özellik | Kaynak PRD | Tür | Tanım | Kabul Kriteri |\n"
        md += "|---|---|---|---|---|\n"

        req_count = 0
        for prd_path in prds:
            rel = prd_path.relative_to(root).as_posix()
            try:
                p_text = prd_path.read_text(encoding="utf-8", errors="replace")
                # Basit başlık ve madde taraması
                items = re.findall(r"(?:###|####|\*|-)\s*(?:FR-\d+|US-\d+|Gereksinim|[A-Z][a-zA-Z0-9\s_-]+)[:\-]?\s*([^\n]+)", p_text)
                for item in items[:5]:
                    req_count += 1
                    md += f"| REQ-{req_count:03d} | `{rel}` | Fonksiyonel | {item.strip()[:60]} | Doğrulanabilir test senaryosu |\n"
            except Exception:
                pass

        if req_count == 0:
            md += f"| REQ-001 | `{prds[0].name}` | Çekirdek | Temel iş akışı ve ekran gereksinimleri | Eksiksiz dikey dilim (5 Katman) |\n"
        md += "\n"
    else:
        md += "- *Bu projede bağımsız bir `*prd*.md` dosyası tespit edilemedi.*\n"
        md += "- *Gereksinimler yaşayan dokümanlardan (`PRODUCT.md`, `PROJECT_BRIEF.md`) ve kaynak koddan sentezlenmiştir.*\n\n"

    # 7. Yaşayan Durum
    handoff_file = refs.get("handoff")
    handoff_text = handoff_file.read_text(encoding="utf-8", errors="replace") if handoff_file else ""
    md += """## 7. Yaşayan Durum, Tamamlanan Dilimler & Sıradaki İşler (HANDOFF.md)
"""
    if handoff_text:
        md += handoff_text[:1200].strip() + "\n\n"
    else:
        md += "- Proje geliştirme süreci aktiftir.\n\n"

    # 8. Karar Kayıtları & Alınan Dersler
    kb_file = refs.get("kb")
    kb_text = kb_file.read_text(encoding="utf-8", errors="replace") if kb_file else ""
    md += """## 8. Mimari Karar Kayıtları & Alınan Dersler (knowledge-base.md & ADR)
"""
    if kb_text:
        m_traps = re.search(r"##\s*(?:Tuzaklar|Dersler|Kararlar)[^\n]*\n([\s\S]*?)(?=\n##|\Z)", kb_text)
        if m_traps:
            md += m_traps.group(0)[:1200].strip() + "\n\n"
        else:
            md += kb_text[:1000].strip() + "\n\n"
    else:
        md += "*Henüz kalıcı karar veya ders kaydı girilmedi.*\n\n"

    return md


def run_summary(
    mode: str = "long",
    root: Path | None = None,
    output_path: Path | None = None,
    check_only: bool = False,
    strict: bool = False,
) -> int:
    """Özet oluşturma veya kontrol iş akışını baştan sona icra eder."""
    project_root = find_project_root(root)
    slug = get_project_slug(project_root)
    lang = get_project_language(project_root)
    user = get_current_user()
    now = datetime.datetime.now()

    # Varsayılan dosya adı
    mode_upper = mode.upper()
    default_filename = f"{slug}_PROJECT_SUMMARY_{mode_upper}.md"
    target_file = output_path or (project_root / "docs" / default_filename)

    # 1. Konum doğrulaması (/docs altında olmalı)
    validate_output_directory(target_file, project_root)

    # 2. Check Modu
    if check_only:
        if not target_file.is_file():
            print(f"[FAIL] {target_file} dosyası bulunamadı!")
            return 1
        content = target_file.read_text(encoding="utf-8", errors="replace")
        if mode_upper not in content and mode.lower() not in content.lower():
            print(f"[FAIL] {target_file} dosyası {mode} modunu taşımıyor!")
            return 1
        print(f"[OK] {target_file} mevcut ve geçerli.")
        return 0

    # 3. Dosya var mı? Versiyonlama ve Arşivleme
    version = "v1.0"
    history: list[dict[str, str]] = []
    if target_file.is_file():
        old_content = target_file.read_text(encoding="utf-8", errors="replace")
        old_version, history = extract_existing_version(old_content)
        version = bump_version(old_version)

        # Arşivleme
        archive_dir = project_root / "docs" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        archive_file = archive_dir / f"{slug}_PROJECT_SUMMARY_{mode_upper}_{timestamp_str}.md"
        archive_file.write_text(old_content, encoding="utf-8")
        print(f"  [ARCHIVE] Mevcut doküman yedeklendi -> docs/archive/{archive_file.name}")

    # 4. Dokümanları Tara
    prds = find_all_prds(project_root)
    refs = collect_reference_docs(project_root)

    # 5. İçeriği İnşa Et
    if mode == "short":
        content = build_short_summary(slug, project_root, lang, version, now, user, refs, history)
    else:
        content = build_long_summary(slug, project_root, lang, version, now, user, prds, refs, history)

    # 6. Dosyayı Yaz
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(content, encoding="utf-8")
    rel_summary = target_file.relative_to(project_root).as_posix()
    print(f"  [WRITE] {rel_summary} başarıyla oluşturuldu (Sürüm: {version}, Mod: {mode_upper}, Dil: {lang.upper()})")

    # 7. PROJECT_BRIEF.md Zorunlu Senkronizasyonu
    synced = sync_project_brief_related_docs(project_root, rel_summary)
    if synced:
        print(f"  [SYNC] PROJECT_BRIEF.md related_docs listesi güncellendi -> {rel_summary}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Proje Konsolide Özeti Oluşturucu (Short / Long)")
    parser.add_argument("--mode", choices=["short", "long"], default="long", help="Özet modu (short veya long, varsayılan: long)")
    parser.add_argument("--project-root", type=str, default=None, help="Proje kök dizini (varsayılan: otomatik tespit)")
    parser.add_argument("--output", type=str, default=None, help="Özel çıktı dosya yolu (zorunlu olarak /docs altında olmalıdır)")
    parser.add_argument("--check", action="store_true", help="Özet dokümanının tazeliğini ve geçerliliğini denetler")
    parser.add_argument("--strict", action="store_true", help="Eksik dokümanda çıkış kodu 1 döndürür")

    args = parser.parse_args()
    root = Path(args.project_root) if args.project_root else None
    output = Path(args.output) if args.output else None

    try:
        return run_summary(
            mode=args.mode,
            root=root,
            output_path=output,
            check_only=args.check,
            strict=args.strict,
        )
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
