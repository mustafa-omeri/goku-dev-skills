#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajan Skill & Mimari Katalog Üreticisi (Skills Catalog HTML Generator).

`.agent/skills/` altındaki tüm `SKILL.md` dosyalarını ve kural sözlüklerini
tarayarak kullanıcı dostu, filtrelenebilir, çift görünümlü (Kart Grid & Kompakt Takip Tablosu),
kopyalanabilir ve modern `skills-catalog.html` dosyasını derler.

Kullanım:
    python scripts/generate_skills_catalog.py
    python scripts/generate_skills_catalog.py --check
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
SKILLS_DIR = PROJECT_ROOT / ".agent" / "skills"
ROUTING_FILE = PROJECT_ROOT / ".agent" / "rules" / "skill-trigger-routing.md"
OUTPUT_HTML = PROJECT_ROOT / ".agent" / "skills-catalog.html"

# Windows konsol UTF-8 desteği
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

CATEGORIES = {
    "Tasarım & UI": [
        "frontend-design", "ui-ux-pro-max", "ui-styling", "theme-factory",
        "design-system", "canvas-design", "banner-design", "design",
        "mock-asset-provider", "web-ide-ux-architect", "onboarding-tour"
    ],
    "Kod & Mimari": [
        "musgoku", "react-best-practices", "i18n-localization",
        "tdd", "codebase-design", "domain-modeling"
    ],
    "Teslimat & Kalite": [
        "git-release-workflow", "production-docker-architect",
        "karpathy-guidelines", "task-observer",
        "diagnosing-bugs", "code-review", "my-idea", "security-audit"
    ],
    "Marka & Doküman": [
        "brand", "doc-coauthoring", "slides"
    ]
}

CONFIG_METADATA = {
    "mock-asset-provider": {
        "status": "Opsiyonel Config",
        "badge_class": "badge-warning",
        "file": ".agent/config/assets.json",
        "features": ["GitHub Repo Desteği", "Unsplash API", "Pexels API", "Sıfır-Ayar CDN Fallback", "Yerel İndirme"],
        "detail": "Özel GitHub görsel deposu linki veya Unsplash/Pexels API anahtarı tanımlanabilir. Hiçbir şey verilmezse sıfır-ayar deterministik CDN fallback'leri (RandomUser, Picsum, DiceBear) otomatik devreye girer.",
        "sample_prompt": "Kullanıcı profilleri için kadın ve erkek portreleri içeren gerçekçi mock görseller sağla.",
        "config_snippet": """{
  "enabled": true,
  "storage_dir": "public/mock-assets",
  "download_locally": true,
  "sources": {
    "github": {
      "enabled": true,
      "repo_url": "https://github.com/kullanici/etkinlik-resimleri-paketi",
      "branch": "main",
      "sub_path": "images"
    },
    "api": {
      "unsplash_access_key": "YOUR_UNSPLASH_ACCESS_KEY",
      "pexels_api_key": "YOUR_PEXELS_API_KEY"
    },
    "default_fallbacks": {
      "portraits": "randomuser",
      "events": "picsum",
      "products": "dummyjson",
      "general": "picsum"
    }
  }
}"""
    },
    "design-system": {
        "status": "Opsiyonel Config",
        "badge_class": "badge-warning",
        "file": "tokens.json / css variables",
        "features": ["3 Katmanlı Token", "Primitive Token", "Semantic Token", "Component Token"],
        "detail": "İsteğe bağlı 3 katmanlı token tanımı (primitive, semantic, component). Yoksa varsayılan ölçekleri üretir.",
        "sample_prompt": "Uygulama için 3 katmanlı design token mimarisi ve CSS değişkenleri üret.",
        "config_snippet": """{
  "primitive": {
    "color": { "blue-500": "#3b82f6", "gray-900": "#111827" },
    "spacing": { "4": "1rem", "8": "2rem" }
  },
  "semantic": {
    "bg-primary": "{primitive.color.gray-900}",
    "brand-accent": "{primitive.color.blue-500}"
  }
}"""
    },
    "ui-styling": {
        "status": "Opsiyonel Config",
        "badge_class": "badge-warning",
        "file": "tailwind.config.js / components.json",
        "features": ["Tailwind Config", "shadcn/ui", "Dark Mode", "Accessible Dialog"],
        "detail": "Tailwind CSS ve shadcn/ui yapılandırma dosyaları mevcutsa onları okur ve genişletir.",
        "sample_prompt": "Bileşeni Tailwind CSS utility sınıfları ve dark mode desteğiyle responsive stillendir.",
        "config_snippet": """// tailwind.config.js
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: { border: "hsl(var(--border))" }
    }
  }
}"""
    },
    "task-observer": {
        "status": "Opsiyonel Config",
        "badge_class": "badge-warning",
        "file": ".agent/observations/log.md",
        "features": ["Otomatik Gözlem", "Skill Geliştirme", "İlke Yayılımı"],
        "detail": "Görev sırasında metodolojik eksiklikler `.agent/observations/` klasörüne otomatik kaydedilir.",
        "sample_prompt": "Bu oturumdaki metodoloji ve kural eksikliklerini gözlem olarak log.md'ye kaydet.",
        "config_snippet": """### Observation [N]: [Kısa Başlık]
**Skill:** [hedef skill]
**Issue:** [karşılaşılan durum]
**Suggested improvement:** [somut öneri]
**Principle:** [genellenebilir kural]"""
    },
    "git-release-workflow": {
        "status": "Proje Dosyası",
        "badge_class": "badge-info",
        "file": ".git / Remote Repo",
        "features": ["commitx Peşin Yetki", "Semantik Tag", "Otonom Push"],
        "detail": "Git deposunun ilklendirilmiş ve uzak (remote) deponun tanımlı olması gerekir. `commitx` veya `commitle` ile peşin yetkili çalışır.",
        "sample_prompt": "commitx: Yapılan değişiklikleri semantik sürüm etiketi artırarak commit ve push yap.",
        "config_snippet": """# Peşin Yetkili Doğrudan Yayın (Tek Satır):
commitx
commitle"""
    },
    "production-docker-architect": {
        "status": "Proje Dosyası",
        "badge_class": "badge-info",
        "file": "Dockerfile / docker-compose.yml",
        "features": ["Multi-stage Build", "Non-root User", "Katman Önbellekleme"],
        "detail": "Projeye ait çok aşamalı (multi-stage) ve non-root güvenli container tanımları üretir veya optimize eder.",
        "sample_prompt": "Üretim ortamı için hafif, multi-stage ve güvenli bir Dockerfile hazırla.",
        "config_snippet": """# Dockerfile multi-stage örneği
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html"""
    },
    "i18n-localization": {
        "status": "Proje Dosyası",
        "badge_class": "badge-info",
        "file": "src/locales/*.json / i18n",
        "features": ["Çok Dil Desteği", "Eksik Anahtar Taraması", "Hardcoded Metin Koruması"],
        "detail": "Uygulamanın çeviri sözlük dosyalarını (en.json, tr.json) tarar; eksik anahtarları ve hardcoded metinleri yakalar.",
        "sample_prompt": "Uygulama genelinde hardcoded metinleri tara ve i18n çeviri anahtarlarını denetle.",
        "config_snippet": """// src/locales/tr.json
{
  "events": {
    "countdown_title": "Kalan Süre",
    "filter_active": "Aktif Etkinlikler"
  }
}"""
    },
    "brand": {
        "status": "Proje Dosyası",
        "badge_class": "badge-info",
        "file": "docs/brand-guidelines.md",
        "features": ["Marka Kılavuzu", "Ses Tonu", "Renk/Tipografi Eşlemesi"],
        "detail": "Marka kılavuzunu üretir veya senkronize eder; renk ve font spesifikasyonunu token'lara bağlar.",
        "sample_prompt": "Marka tonu, görsel kimlik ve renk/font kurallarını içeren marka kılavuzunu oluştur.",
        "config_snippet": """# docs/brand-guidelines.md
- Marka Vizyonu ve Değerleri
- Ses Tonu (Voice & Tone)
- Renk Paleti (Primary, Secondary, Accent)
- Tipografi Kuralları"""
    },
    "musgoku": {
        "status": "Proje Dosyası",
        "badge_class": "badge-info",
        "file": "pom.xml / package.json / .agent/rules",
        "features": ["REST Controller", "JPA Entity", "Keyset Pagination", "WebSocket", "Cerrahi Skill Güncelleme"],
        "detail": "Backend (Spring Boot/Java) veya Frontend mimari kuralları, kalite kapılarını ve cerrahi skill güncelleme protokolünü yönetir.",
        "sample_prompt": "Spring Boot REST controller ve JPA entity katmanını pagination ile oluştur; Goku skill setini güncelle.",
        "config_snippet": """// Spring Boot Entity & REST mimarisi
@RestController
@RequestMapping("/api/v1/events")
public class EventController { ... }"""
    },
    "onboarding-tour": {
        "status": "Sıfır-Ayar (Zero-Config)",
        "badge_class": "badge-success",
        "file": "Ek dosya gerekmez (Opsiyonel driver.js / react-joyride)",
        "features": ["Driver.js (Önerilen)", "React Joyride Desteği", "Pulsing Coachmarks", "Otonom Paket Yükleme Protokolü"],
        "detail": "Kullanıcı karşılama (onboarding), spotlight odaklamalı ürün turları, adım adım walkthrough kılavuzları ve pulsing coachmark ipucu balonları tasarlar. Eksik paketleri kurallara göre projeye otonom ekler.",
        "sample_prompt": "Yeni başlayan kullanıcılar için dashboard ve menü adımlarını tanıtan hafif bir Driver.js onboarding turu hazırla.",
        "config_snippet": """// scaffold_tour.py ile TypeScript hook veya bileşen üretilebilir:
// python .agent/skills/onboarding-tour/scripts/scaffold_tour.py --engine driverjs --name demoTour
import { useDemoTour } from './useDemoTour';"""
    },
    "my-idea": {
        "status": "Proje Havuzu",
        "badge_class": "badge-info",
        "file": "docs/idea/myidea.md",
        "features": ["Fikir Havuzu Analizi", "Re-rating Skoru", "Bayat Fikir Eleme", "Top 3 Seçim", "TDD & Sprint Entegrasyonu"],
        "detail": "Proje planı dışındaki serbest fikirleri docs/idea/myidea.md içinde toplar; ajan büyük işler bittiğinde veya kullanıcı isteğiyle fikirleri re-rate eder ve ilk 3 öneriyi sunar.",
        "sample_prompt": "Fikirlerime bak ve güncel proje durumuna göre sıradaki en mantıklı 3 adımı öner.",
        "config_snippet": """# Fikirleri İncele ve Sırala:
python .agent/skills/my-idea/scripts/idea_manager.py --top 3"""
    }
}

DEFAULT_CONFIG_META = {
    "status": "Sıfır-Ayar (Zero-Config)",
    "badge_class": "badge-success",
    "file": "Ek dosya gerekmez",
    "features": ["Doğrudan Promptla Çalışır", "Kural Tabanlı", "Yerleşik Şablonlar"],
    "detail": "Herhangi bir konfigürasyon veya ayar dosyası gerekmez; kural ve metodoloji olarak doğrudan çalışır.",
    "sample_prompt": "Bu sayfa için modern, karakterli ve AI-slop kalıplarından uzak bir arayüz tasarla.",
    "config_snippet": None
}

SAMPLE_PROMPTS = {
    "musgoku": "Spring Boot REST controller ve JPA entity katmanını pagination ile oluştur; veya Goku skill setini güncelle.",
    "ui-ux-pro-max": "Arayüzün renk paleti, tipografi ve erişilebilirlik (WCAG) kurallarını incele.",
    "frontend-design": "Arayüzü modernleştir, AI-slop kalıplarını temizle ve [DESIGN-REFRESH] protokolünü uygula.",
    "canvas-design": "Etkinlik için ölçüsüz görsel sanat ve manifesto afişi posteri oluştur.",
    "banner-design": "Web sitesi hero alanı ve LinkedIn için 1584x396 ölçülü kapak görseli tasarla.",
    "design-system": "Uygulama için 3 katmanlı design token mimarisi (primitive, semantic, component) ve CSS değişkenleri üret.",
    "ui-styling": "Bileşeni Tailwind CSS utility sınıfları ve dark mode desteğiyle responsive stillendir.",
    "theme-factory": "Uygulama için 10 hazır temadan birini seç ve HEX paletini uygula.",
    "design": "Kurumsal kimlik için logo brief'i ve kartvizit tasarım yönergelerini hazırla.",
    "mock-asset-provider": "Kullanıcı profilleri için kadın ve erkek portreleri içeren gerçekçi mock görseller sağla.",
    "web-ide-ux-architect": "Düşük gecikmeli, kod editörü ve split-pane panelli bir IDE arayüzü tasarla.",
    "onboarding-tour": "Yeni başlayan kullanıcılar için dashboard ve menü adımlarını tanıtan hafif bir Driver.js onboarding turu hazırla.",
    "react-best-practices": "React bileşenindeki gereksiz re-render'ları ve waterfall veri çekimlerini ortadan kaldır.",
    "i18n-localization": "Uygulamadaki hardcode metinleri ve eksik çeviri anahtarlarını i18n_checker ile denetle ve düzelt.",
    "tdd": "Yeni sipariş iptal akışını dikiş noktalarında önce kırmızı test yazarak TDD dikey dilimiyle geliştir.",
    "codebase-design": "Ödeme modülünün arayüzünü derinleştir, dikiş noktasını ve silme testini belirle.",
    "domain-modeling": "İş kavramlarını netleştir, GLOSSARY.md sözlüğünü güncelle ve geri dönüşü zor karar için ADR oluştur.",
    "git-release-workflow": "commitx: Yapılan değişiklikleri semantik sürüm etiketi artırarak commit ve push yap.",
    "production-docker-architect": "Üretim ortamı için hafif, multi-stage ve non-root kullanıcılı Dockerfile ve Compose oluştur.",
    "karpathy-guidelines": "Kod karmaşıklığını azalt, gereksiz soyutlamaları sadeleştir ve varsayımları yüzeye çıkar.",
    "task-observer": "Bu oturumdaki metodoloji ve kural eksikliklerini gözlem olarak log.md'ye kaydet ve gelişim öner.",
    "diagnosing-bugs": "Çöken endpoint için kırmızı geri bildirim döngüsü kur, 3 hipotez üret ve hatayı teşhis et.",
    "code-review": "Mevcut branch değişikliklerini Standartlar ve Şartname eksenlerinde iki paralel alt ajanla incele.",
    "my-idea": "Fikirlerime bak ve güncel proje durumuna göre sıradaki en mantıklı 3 adımı öner.",
    "brand": "Marka kılavuzunu, ton ve mesaj çerçevesini docs/brand-guidelines.md olarak oluştur.",
    "doc-coauthoring": "Teknik mimari karar dokümanı (RFC / Decision Doc) taslağı oluştur.",
    "slides": "Yatırımcı sunumu için PAS formülüyle 10 slaytlık pitch deck metni ve düzeni çıkar."
}


def parse_skill_md(skill_path: Path) -> dict:
    text = skill_path.read_text(encoding="utf-8")
    frontmatter = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            raw_fm = text[3:end]
            lines = raw_fm.splitlines()
            current_key = None
            current_val = []
            for line in lines:
                if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
                    if current_key:
                        frontmatter[current_key] = " ".join(current_val).strip()
                    parts = line.split(":", 1)
                    current_key = parts[0].strip()
                    val = parts[1].strip()
                    current_val = [val] if val and val not in (">", ">-", "|", "|-") else []
                elif current_key:
                    current_val.append(line.strip())
            if current_key:
                frontmatter[current_key] = " ".join(current_val).strip()

    name = frontmatter.get("name", skill_path.parent.name)
    desc = frontmatter.get("description", "")

    # Tetikleyicileri ayıkla
    triggers = []
    t_match = re.search(r"Tetikleyiciler:\s*(.*?)(?=\.\s*Tetiklenmez:|$)", desc)
    if t_match:
        raw_trig = t_match.group(1)
        triggers = [t.strip(' "\'') for t in re.findall(r'"([^"]+)"', raw_trig)]

    # Tetiklenmez ayıkla
    negative = ""
    n_match = re.search(r"Tetiklenmez:\s*(.*?)(?=\.?\s*Tam sözlük:|$)", desc)
    if n_match:
        negative = n_match.group(1).strip()

    # Amaç
    purpose = desc
    if "Tetikleyiciler:" in desc:
        purpose = desc.split("Tetikleyiciler:")[0].strip()

    # Kategori
    category = "Diğer"
    for cat, skills in CATEGORIES.items():
        if name in skills:
            category = cat
            break

    # Config meta
    cfg = CONFIG_METADATA.get(name, DEFAULT_CONFIG_META)
    prompt = SAMPLE_PROMPTS.get(name, cfg.get("sample_prompt", "Bu skill'i devreye al."))

    # CLI komutu tespiti
    scripts_dir = skill_path.parent / "scripts"
    cli_cmd = ""
    if scripts_dir.is_dir():
        py_files = sorted(scripts_dir.glob("*.py"))
        if py_files:
            main_script = py_files[0].name
            cli_cmd = f"python .agent/skills/{name}/scripts/{main_script}"

    # Ek anahtar kelimeler (arama için)
    search_keywords = [name, category, purpose, cfg["file"], cfg["detail"]] + triggers
    if "features" in cfg:
        search_keywords.extend(cfg["features"])
    if name == "mock-asset-provider":
        search_keywords.extend(["github", "api", "unsplash", "pexels", "resim", "foto", "avatar", "profil", "etkinlik", "assets.json"])
    if name == "musgoku":
        search_keywords.extend(["goku update", "skill update", "gs update", "güncelle", "cerrahi"])

    return {
        "name": name,
        "category": category,
        "purpose": purpose,
        "triggers": triggers,
        "negative": negative,
        "config_status": cfg["status"],
        "badge_class": cfg["badge_class"],
        "config_file": cfg["file"],
        "config_detail": cfg["detail"],
        "features": cfg.get("features", []),
        "config_snippet": cfg.get("config_snippet"),
        "sample_prompt": prompt,
        "cli_cmd": cli_cmd,
        "search_index": " ".join(search_keywords).lower()
    }


def generate_catalog_html(skills: list[dict]) -> str:
    skills_json = json.dumps(skills, ensure_ascii=False)
    
    pkg_json_file = PROJECT_ROOT / "package.json"
    pkg_version = "1.9.10"
    if pkg_json_file.is_file():
        try:
            pkg_version = json.loads(pkg_json_file.read_text(encoding="utf-8")).get("version", "1.9.10")
        except Exception:
            pass
    cat_badges = {
        "Tasarım & UI": "cat-design",
        "Kod & Mimari": "cat-code",
        "Teslimat & Kalite": "cat-delivery",
        "Marka & Doküman": "cat-brand"
    }

    cat_buttons = "".join(
        f'<button class="chip {cat_badges.get(cat, "")}" onclick="setCategoryFilter(\'{cat}\', this)">'
        f'{cat} <span class="chip-count">({len(skills_in_cat)})</span></button>'
        for cat, skills_in_cat in CATEGORIES.items()
    )

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ajan Skill & Mimari Kataloğu — Goku Dev Skills</title>
  <style>
    :root {{
      --bg: #080c14;
      --surface: #0f172a;
      --surface-hover: #1e293b;
      --card-bg: #0d1527;
      --card-border: rgba(255, 255, 255, 0.08);
      --border: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-glow: rgba(56, 189, 248, 0.18);
      --accent: #818cf8;
      --success: #34d399;
      --success-bg: rgba(52, 211, 153, 0.12);
      --warning: #fbbf24;
      --warning-bg: rgba(251, 191, 36, 0.12);
      --info: #60a5fa;
      --info-bg: rgba(96, 165, 250, 0.12);
      --danger: #f87171;
      --danger-bg: rgba(248, 113, 113, 0.12);
      --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
      --radius-sm: 6px;
      --radius-md: 12px;
      --radius-lg: 18px;
    }}

    [data-theme="light"] {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-hover: #f1f5f9;
      --card-bg: #ffffff;
      --card-border: #e2e8f0;
      --border: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --primary: #0284c7;
      --primary-glow: rgba(2, 132, 199, 0.12);
      --accent: #6366f1;
      --success: #059669;
      --success-bg: rgba(5, 150, 105, 0.1);
      --warning: #d97706;
      --warning-bg: rgba(217, 119, 6, 0.1);
      --info: #2563eb;
      --info-bg: rgba(37, 99, 235, 0.1);
      --danger: #dc2626;
      --danger-bg: rgba(220, 38, 38, 0.08);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.6;
      min-height: 100vh;
      transition: background-color 0.25s, color 0.25s;
    }}

    /* Sticky Ergonomic Header */
    header {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border);
      padding: 1rem 1.5rem;
    }}
    [data-theme="light"] header {{
      background: rgba(255, 255, 255, 0.88);
    }}

    .header-content {{
      max-width: 1440px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1.5rem;
      flex-wrap: wrap;
    }}

    .title-area {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }}
    .title-area h1 {{
      font-size: 1.45rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .title-area h1 span.gradient {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .version-tag {{
      font-family: var(--font-mono);
      font-size: 0.725rem;
      font-weight: 700;
      background: rgba(56, 189, 248, 0.12);
      color: var(--primary);
      border: 1px solid rgba(56, 189, 248, 0.25);
      padding: 0.2rem 0.55rem;
      border-radius: 9999px;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    .view-mode-toggle {{
      display: flex;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.18rem;
      gap: 0.2rem;
    }}
    .btn-view {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.35rem 0.7rem;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.15s;
    }}
    .btn-view.active {{
      background: var(--surface);
      color: var(--primary);
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }}

    .btn-action {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.45rem 0.85rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 0.825rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.15s;
    }}
    .btn-action:hover {{
      background: var(--surface-hover);
      border-color: var(--primary);
    }}

    /* Main Container */
    .container {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}

    /* Hero / Subhead */
    .hero-strip {{
      margin-bottom: 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    .hero-strip p {{
      color: var(--text-muted);
      font-size: 0.95rem;
      max-width: 820px;
      line-height: 1.55;
    }}
    .stat-badge-group {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}
    .stat-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 0.4rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
    }}
    .stat-pill .num {{
      color: var(--primary);
      font-weight: 800;
      font-family: var(--font-mono);
    }}

    /* Toolbar & Search Hub */
    .toolbar {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 1.25rem;
      margin-bottom: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.25);
    }}

    .search-row {{
      display: flex;
      gap: 0.75rem;
      align-items: center;
    }}
    .search-box {{
      position: relative;
      flex: 1;
    }}
    .search-input {{
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.85rem 2.85rem 0.85rem 2.75rem;
      border-radius: var(--radius-sm);
      font-size: 0.975rem;
      outline: none;
      transition: all 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-glow);
    }}
    .search-icon {{
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
      font-size: 1rem;
    }}
    .btn-clear-search {{
      position: absolute;
      right: 0.85rem;
      top: 50%;
      transform: translateY(-50%);
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 0.85rem;
      padding: 0.2rem 0.4rem;
      border-radius: 4px;
      display: none;
    }}
    .btn-clear-search:hover {{
      color: var(--text-main);
    }}
    .kbd-shortcut {{
      position: absolute;
      right: 1rem;
      top: 50%;
      transform: translateY(-50%);
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.7rem;
      font-family: var(--font-mono);
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      pointer-events: none;
    }}

    .filter-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      border-top: 1px solid rgba(255,255,255,0.04);
      padding-top: 0.85rem;
    }}
    .filter-group {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.45rem;
    }}
    .filter-label {{
      font-size: 0.775rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-right: 0.4rem;
    }}

    .chip {{
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }}
    .chip:hover {{
      color: var(--text-main);
      border-color: var(--primary);
    }}
    .chip.active {{
      background: var(--primary);
      border-color: var(--primary);
      color: #0b0f19;
      font-weight: 700;
    }}
    .chip-count {{
      font-size: 0.7rem;
      opacity: 0.8;
      font-family: var(--font-mono);
    }}

    /* Filter status count text */
    .filter-summary {{
      font-size: 0.825rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .btn-reset-filters {{
      background: transparent;
      border: none;
      color: var(--primary);
      text-decoration: underline;
      cursor: pointer;
      font-size: 0.825rem;
    }}

    /* GRID VIEW */
    .skills-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(430px, 1fr));
      gap: 1.5rem;
    }}

    .skill-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
      position: relative;
    }}
    .skill-card:hover {{
      transform: translateY(-2px);
      border-color: var(--primary);
      box-shadow: 0 12px 28px -10px var(--primary-glow);
    }}

    .card-top {{
      margin-bottom: 1.25rem;
    }}

    .card-meta-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }}
    .card-index {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 700;
      opacity: 0.6;
    }}
    .skill-category-badge {{
      font-size: 0.725rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 0.2rem 0.55rem;
      border-radius: 9999px;
    }}
    .cat-design {{ background: rgba(56, 189, 248, 0.1); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.25); }}
    .cat-code {{ background: rgba(52, 211, 153, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.25); }}
    .cat-delivery {{ background: rgba(251, 191, 36, 0.1); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.25); }}
    .cat-brand {{ background: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.25); }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 0.75rem;
    }}
    .skill-name {{
      font-size: 1.25rem;
      font-weight: 800;
      font-family: var(--font-mono);
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    /* Badges */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.22rem 0.65rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 700;
      white-space: nowrap;
    }}
    .badge-success {{
      background: var(--success-bg);
      color: var(--success);
      border: 1px solid rgba(52, 211, 153, 0.25);
    }}
    .badge-warning {{
      background: var(--warning-bg);
      color: var(--warning);
      border: 1px solid rgba(251, 191, 36, 0.3);
    }}
    .badge-info {{
      background: var(--info-bg);
      color: var(--info);
      border: 1px solid rgba(96, 165, 250, 0.3);
    }}

    /* Features Row */
    .features-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin: 0.4rem 0 0.85rem;
    }}
    .feature-tag {{
      font-size: 0.7rem;
      font-weight: 600;
      background: rgba(56, 189, 248, 0.08);
      border: 1px solid rgba(56, 189, 248, 0.2);
      color: var(--primary);
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-sm);
    }}

    .skill-purpose {{
      color: var(--text-main);
      font-size: 0.925rem;
      line-height: 1.55;
      margin-bottom: 1.15rem;
    }}

    .section-title {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 0.45rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .triggers-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin-bottom: 0.9rem;
    }}
    .trigger-pill {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--primary);
      padding: 0.22rem 0.55rem;
      border-radius: var(--radius-sm);
      font-family: var(--font-mono);
      font-size: 0.74rem;
      cursor: pointer;
      transition: all 0.15s;
      user-select: none;
    }}
    .trigger-pill:hover {{
      background: var(--primary);
      color: #0b0f19;
      border-color: var(--primary);
    }}

    .config-box {{
      background: var(--surface);
      border-left: 3px solid var(--border);
      padding: 0.75rem;
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      font-size: 0.825rem;
      margin-bottom: 0.9rem;
    }}
    .config-box.warning {{ border-left-color: var(--warning); }}
    .config-box.info {{ border-left-color: var(--info); }}
    .config-box.success {{ border-left-color: var(--success); }}
    .config-file-name {{
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--text-main);
      display: block;
      margin-bottom: 0.2rem;
    }}
    .config-desc {{
      color: var(--text-muted);
      font-size: 0.785rem;
      line-height: 1.45;
    }}

    /* JSON Accordion */
    .json-accordion {{
      margin: 0.6rem 0 0.9rem;
    }}
    .btn-toggle-json {{
      background: transparent;
      border: 1px dashed var(--border);
      color: var(--primary);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.35rem 0.65rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.2s;
    }}
    .btn-toggle-json:hover {{
      background: var(--surface-hover);
      border-color: var(--primary);
    }}
    .json-code-drawer {{
      display: none;
      margin-top: 0.5rem;
      background: #060911;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.75rem;
      position: relative;
    }}
    .json-code-drawer.open {{
      display: block;
    }}
    .json-code-drawer pre {{
      font-family: var(--font-mono);
      font-size: 0.735rem;
      color: #a5f3fc;
      overflow-x: auto;
      max-height: 220px;
    }}
    .btn-copy-code {{
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.7rem;
      padding: 0.2rem 0.5rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
    }}
    .btn-copy-code:hover {{
      color: var(--primary);
      border-color: var(--primary);
    }}

    .negative-box {{
      background: var(--danger-bg);
      border: 1px solid rgba(248, 113, 113, 0.2);
      border-radius: var(--radius-sm);
      padding: 0.55rem 0.75rem;
      font-size: 0.785rem;
      color: var(--danger);
      margin-bottom: 0.9rem;
    }}

    .card-footer {{
      border-top: 1px solid var(--border);
      padding-top: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .btn-copy-prompt {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.45rem 0.85rem;
      border-radius: var(--radius-sm);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.15s;
    }}
    .btn-copy-prompt:hover {{
      background: var(--surface-hover);
      border-color: var(--primary);
      color: var(--primary);
    }}

    /* TABLE VIEW (Kompakt Takip Modu) */
    .skills-table-wrapper {{
      display: none;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      overflow-x: auto;
      box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.25);
    }}
    .skills-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.875rem;
    }}
    .skills-table th {{
      background: rgba(15, 23, 42, 0.7);
      padding: 0.95rem 1rem;
      font-weight: 700;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      text-transform: uppercase;
      font-size: 0.725rem;
      letter-spacing: 0.05em;
    }}
    .skills-table td {{
      padding: 1rem;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    .skills-table tr:hover td {{
      background: var(--surface-hover);
    }}
    .table-skill-cell {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}
    .table-skill-name {{
      font-family: var(--font-mono);
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--text-main);
    }}
    .table-triggers {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.25rem;
      max-width: 380px;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #10b981;
      color: #ffffff;
      padding: 0.85rem 1.4rem;
      border-radius: var(--radius-md);
      font-size: 0.925rem;
      font-weight: 600;
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.45);
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 9999;
    }}
    .toast.show {{
      transform: translateY(0);
      opacity: 1;
    }}

    .no-results {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 5rem 1rem;
      color: var(--text-muted);
    }}
    .no-results h3 {{
      font-size: 1.35rem;
      margin-bottom: 0.5rem;
      color: var(--text-main);
    }}

    @media (max-width: 900px) {{
      .skills-grid {{ grid-template-columns: 1fr; }}
      .header-content {{ flex-direction: column; align-items: flex-start; }}
    }}
  </style>
</head>
<body data-theme="dark">

  <!-- Sticky Top Header -->
  <header>
    <div class="header-content">
      <div class="title-area">
        <h1>🚀 <span class="gradient">Goku Dev Skills</span> Kataloğu</h1>
        <span class="version-tag">v{pkg_version}</span>
      </div>
      <div class="header-actions">
        <!-- View Mode Switcher -->
        <div class="view-mode-toggle">
          <button class="btn-view active" id="btnViewGrid" onclick="setViewMode('grid')">
            <span>🔲</span> Kart Grid
          </button>
          <button class="btn-view" id="btnViewTable" onclick="setViewMode('table')">
            <span>📑</span> Takip Tablosu
          </button>
        </div>
        <button class="btn-action" id="themeToggleBtn" onclick="toggleTheme()" title="Temayı değiştir (Kısayol: T)">
          <span id="themeIcon">☀️</span> Açık Tema
        </button>
      </div>
    </div>
  </header>

  <div class="container">
    
    <!-- Hero / Summary Strip -->
    <div class="hero-strip">
      <div>
        <p>Yapay zeka kod asistanları (Antigravity, Cursor, Claude Code, Windsurf) için projedeki <strong>{len(skills)} skill</strong>'in sorumluluk sınırları, doğal dil tetikleyici kelimeleri, GitHub/API entegrasyonları ve konfigürasyon gereksinimleri tek bir takip arayüzünde.</p>
      </div>
      <div class="stat-badge-group">
        <div class="stat-pill">Toplam Skill: <span class="num">{len(skills)}</span></div>
        <div class="stat-pill">Kategori: <span class="num">{len(CATEGORIES)}</span></div>
        <div class="stat-pill">Bileşen Teması: <span class="num">55</span></div>
      </div>
    </div>

    <!-- Toolbar: Search & Filter Hub -->
    <div class="toolbar">
      <div class="search-row">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" class="search-input" placeholder="Skill adı, 'goku update', 'banner', 'commitx', 'tokens', 'i18n', 'mock görsel' ara... (Kısayol: / veya Ctrl+K)" oninput="filterSkills()">
          <button class="btn-clear-search" id="btnClearSearch" onclick="clearSearch()">✕</button>
          <span class="kbd-shortcut">/</span>
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-group">
          <span class="filter-label">Kategori:</span>
          <button class="chip active" onclick="setCategoryFilter('all', this)">Tümü <span class="chip-count">({len(skills)})</span></button>
          {cat_buttons}
        </div>
        <div class="filter-group">
          <span class="filter-label">Config:</span>
          <button class="chip active" onclick="setConfigFilter('all', this)">Tümü</button>
          <button class="chip" onclick="setConfigFilter('Sıfır-Ayar', this)">🟢 Sıfır-Ayar</button>
          <button class="chip" onclick="setConfigFilter('Opsiyonel Config', this)">🟡 Opsiyonel</button>
          <button class="chip" onclick="setConfigFilter('Proje Dosyası', this)">🔵 Proje Dosyası</button>
        </div>
      </div>

      <div class="filter-summary" id="filterSummary">
        <span>Tüm skill'ler listeleniyor ({len(skills)})</span>
      </div>
    </div>

    <!-- VIEW 1: Grid Mode -->
    <div class="skills-grid" id="skillsGrid"></div>

    <!-- VIEW 2: Compact Table Mode (Ultra Scanability) -->
    <div class="skills-table-wrapper" id="skillsTableWrapper">
      <table class="skills-table">
        <thead>
          <tr>
            <th style="width: 45px;">#</th>
            <th style="width: 220px;">Skill & Kategori</th>
            <th>Temel Görevi & Yetenekleri</th>
            <th style="width: 360px;">Tetikleyiciler (Triggers)</th>
            <th style="width: 170px;">Config Durumu</th>
            <th style="width: 160px; text-align: right;">Hızlı İşlem</th>
          </tr>
        </thead>
        <tbody id="skillsTableBody"></tbody>
      </table>
    </div>

  </div>

  <!-- Toast Notification -->
  <div class="toast" id="toast">
    <span>✓</span> <span id="toastMsg">Panoya kopyalandı!</span>
  </div>

  <script>
    const allSkills = {skills_json};
    let currentCategory = 'all';
    let currentConfig = 'all';
    let currentSearch = '';
    let currentViewMode = localStorage.getItem('agent_catalog_view') || 'grid';

    const categoryBadgeClassMap = {{
      'Tasarım & UI': 'cat-design',
      'Kod & Mimari': 'cat-code',
      'Teslimat & Kalite': 'cat-delivery',
      'Marka & Doküman': 'cat-brand'
    }};

    function setViewMode(mode) {{
      currentViewMode = mode;
      localStorage.setItem('agent_catalog_view', mode);
      document.getElementById('btnViewGrid').classList.toggle('active', mode === 'grid');
      document.getElementById('btnViewTable').classList.toggle('active', mode === 'table');
      
      const grid = document.getElementById('skillsGrid');
      const table = document.getElementById('skillsTableWrapper');
      
      if (mode === 'grid') {{
        grid.style.display = 'grid';
        table.style.display = 'none';
      }} else {{
        grid.style.display = 'none';
        table.style.display = 'block';
      }}
      renderAll();
    }}

    function renderAll() {{
      const filtered = allSkills.filter(s => {{
        const matchCategory = (currentCategory === 'all' || s.category === currentCategory);
        const matchConfig = (currentConfig === 'all' || s.config_status.includes(currentConfig));
        const query = currentSearch.toLowerCase().trim();
        const matchSearch = !query || s.search_index.includes(query);
        return matchCategory && matchConfig && matchSearch;
      }});

      // Update Filter Summary
      const summary = document.getElementById('filterSummary');
      if (filtered.length === allSkills.length) {{
        summary.innerHTML = `<span>Tüm skill'ler listeleniyor (${{allSkills.length}})</span>`;
      }} else {{
        summary.innerHTML = `
          <span><strong>${{filtered.length}}</strong> / ${{allSkills.length}} skill filtrelendi</span>
          <button class="btn-reset-filters" onclick="resetFilters()">Filtreleri Sıfırla</button>
        `;
      }}

      // Clear search button visibility
      const clearBtn = document.getElementById('btnClearSearch');
      clearBtn.style.display = currentSearch ? 'block' : 'none';

      if (currentViewMode === 'grid') {{
        renderCards(filtered);
      }} else {{
        renderTable(filtered);
      }}
    }}

    function renderCards(filtered) {{
      const grid = document.getElementById('skillsGrid');
      grid.innerHTML = '';

      if (filtered.length === 0) {{
        grid.innerHTML = `
          <div class="no-results">
            <h3>Sonuç Bulunamadı</h3>
            <p>Arama kriterlerine veya seçilen filtrelere uygun skill bulunamadı.</p>
            <button class="btn-action" style="margin-top:1rem" onclick="resetFilters()">Filtreleri Sıfırla</button>
          </div>
        `;
        return;
      }}

      filtered.forEach((s, idx) => {{
        const card = document.createElement('div');
        card.className = 'skill-card';
        card.setAttribute('data-name', s.name);
        card.setAttribute('data-category', s.category);
        
        const triggersHtml = s.triggers.map(t => 
          `<span class="trigger-pill" title="Kopyalamak için tıkla" onclick="copyToClipboard('${{t.replace(/'/g, "\\\\\\'")}}', 'Tetikleyici kopyalandı: \\'${{t}}\\'')">"${{escapeHtml(t)}}"</span>`
        ).join('');

        const featuresHtml = (s.features || []).map(f => 
          `<span class="feature-tag">✦ ${{escapeHtml(f)}}</span>`
        ).join('');

        const configType = s.config_status.includes('Sıfır-Ayar') ? 'success' : 
                           s.config_status.includes('Opsiyonel') ? 'warning' : 'info';

        const jsonSnippetHtml = s.config_snippet ? `
          <div class="json-accordion">
            <button class="btn-toggle-json" onclick="toggleJsonDrawer('json-${{idx}}')">
              <span>⚙️ Config / JSON Şablonunu Göster</span>
            </button>
            <div class="json-code-drawer" id="json-${{idx}}">
              <button class="btn-copy-code" onclick="copyToClipboard('${{s.config_snippet.replace(/'/g, "\\\\'").replace(/\\n/g, "\\\\n")}}', 'Config şablonu kopyalandı!')">Kopyala</button>
              <pre><code>${{escapeHtml(s.config_snippet)}}</code></pre>
            </div>
          </div>
        ` : '';

        const catClass = categoryBadgeClassMap[s.category] || 'cat-design';
        const numPadded = String(idx + 1).padStart(2, '0');

        card.innerHTML = `
          <div class="card-top">
            <div class="card-meta-bar">
              <span class="card-index">#${{numPadded}}</span>
              <span class="skill-category-badge ${{catClass}}">${{escapeHtml(s.category)}}</span>
            </div>

            <div class="card-header">
              <div class="skill-name">${{escapeHtml(s.name)}}</div>
              <span class="badge ${{s.badge_class}}">${{escapeHtml(s.config_status)}}</span>
            </div>

            ${{featuresHtml ? `<div class="features-row">${{featuresHtml}}</div>` : ''}}
            
            <p class="skill-purpose">${{escapeHtml(s.purpose)}}</p>

            <div class="section-title">⚡ Tetikleyiciler (Triggers)</div>
            <div class="triggers-list">${{triggersHtml || '<span style="color:var(--text-muted);font-size:0.8rem">Genel yönlendirici veya davranışsal</span>'}}</div>

            <div class="section-title">⚙️ Konfigürasyon Durumu</div>
            <div class="config-box ${{configType}}">
              <span class="config-file-name">${{escapeHtml(s.config_file)}}</span>
              <span class="config-desc">${{escapeHtml(s.config_detail)}}</span>
            </div>

            ${{jsonSnippetHtml}}

            ${{s.negative ? `
              <div class="section-title">⛔ Kapsam Sınırı (Tetiklenmez)</div>
              <div class="negative-box">${{escapeHtml(s.negative)}}</div>
            ` : ''}}
          </div>

          <div class="card-footer">
            <button class="btn-copy-prompt" onclick="copyToClipboard('${{s.sample_prompt.replace(/'/g, "\\\\\\'")}}', 'Örnek prompt panoya kopyalandı!')">
              📋 Örnek Prompt Kopyala
            </button>
            ${{s.cli_cmd ? `
              <button class="btn-copy-prompt" onclick="copyToClipboard('${{s.cli_cmd.replace(/'/g, "\\\\\\'")}}', 'Komut panoya kopyalandı!')">
                💻 CLI Komutu
              </button>
            ` : ''}}
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function renderTable(filtered) {{
      const tbody = document.getElementById('skillsTableBody');
      tbody.innerHTML = '';

      if (filtered.length === 0) {{
        tbody.innerHTML = `
          <tr>
            <td colspan="6" style="text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
              Filtrelere uygun skill bulunamadı.
            </td>
          </tr>
        `;
        return;
      }}

      filtered.forEach((s, idx) => {{
        const tr = document.createElement('tr');
        tr.setAttribute('data-name', s.name);

        const triggersHtml = s.triggers.slice(0, 5).map(t => 
          `<span class="trigger-pill" style="font-size:0.7rem;" title="Kopyalamak için tıkla" onclick="copyToClipboard('${{t.replace(/'/g, "\\\\\\'")}}', 'Tetikleyici kopyalandı!')">"${{escapeHtml(t)}}"</span>`
        ).join('') + (s.triggers.length > 5 ? `<span style="font-size:0.7rem;color:var(--text-muted);">+${{s.triggers.length - 5}}</span>` : '');

        const catClass = categoryBadgeClassMap[s.category] || 'cat-design';
        const numPadded = String(idx + 1).padStart(2, '0');

        tr.innerHTML = `
          <td style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-muted);font-weight:700;">#${{numPadded}}</td>
          <td>
            <div class="table-skill-cell">
              <span class="table-skill-name">${{escapeHtml(s.name)}}</span>
              <span class="skill-category-badge ${{catClass}}" style="display:inline-block;width:max-content;font-size:0.65rem;padding:0.1rem 0.45rem;">${{escapeHtml(s.category)}}</span>
            </div>
          </td>
          <td>
            <div style="font-size:0.85rem;color:var(--text-main);line-height:1.45;margin-bottom:0.35rem;">${{escapeHtml(s.purpose)}}</div>
            ${{s.features && s.features.length ? `<div class="features-row" style="margin:0;">${{s.features.slice(0, 3).map(f => `<span class="feature-tag" style="font-size:0.65rem;">✦ ${{escapeHtml(f)}}</span>`).join('')}}</div>` : ''}}
          </td>
          <td>
            <div class="table-triggers">${{triggersHtml || '<span style="color:var(--text-muted);font-size:0.75rem;">Genel yönlendirici</span>'}}</div>
          </td>
          <td>
            <span class="badge ${{s.badge_class}}" style="font-size:0.7rem;">${{escapeHtml(s.config_status)}}</span>
            <div style="font-family:var(--font-mono);font-size:0.72rem;color:var(--text-muted);margin-top:0.3rem;">${{escapeHtml(s.config_file)}}</div>
          </td>
          <td style="text-align: right;">
            <button class="btn-copy-prompt" style="padding:0.35rem 0.65rem;font-size:0.75rem;" onclick="copyToClipboard('${{s.sample_prompt.replace(/'/g, "\\\\\\'")}}', 'Örnek prompt kopyalandı!')">
              📋 Kopyala
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function filterSkills() {{
      currentSearch = document.getElementById('searchInput').value;
      renderAll();
    }}

    function clearSearch() {{
      document.getElementById('searchInput').value = '';
      currentSearch = '';
      renderAll();
    }}

    function resetFilters() {{
      currentCategory = 'all';
      currentConfig = 'all';
      currentSearch = '';
      document.getElementById('searchInput').value = '';
      document.querySelectorAll('.chip').forEach(c => {{
        if (c.innerText.includes('Tümü')) c.classList.add('active');
        else c.classList.remove('active');
      }});
      renderAll();
    }}

    function setCategoryFilter(cat, btn) {{
      currentCategory = cat;
      btn.parentElement.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      renderAll();
    }}

    function setConfigFilter(cfg, btn) {{
      currentConfig = cfg;
      btn.parentElement.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      renderAll();
    }}

    function toggleJsonDrawer(id) {{
      const el = document.getElementById(id);
      if (el) {{
        el.classList.toggle('open');
      }}
    }}

    function copyToClipboard(text, msg) {{
      navigator.clipboard.writeText(text).then(() => {{
        showToast(msg || 'Panoya kopyalandı!');
      }}).catch(err => {{
        console.error('Kopyalama hatası:', err);
      }});
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      const toastMsg = document.getElementById('toastMsg');
      toastMsg.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => {{
        toast.classList.remove('show');
      }}, 2400);
    }}

    function toggleTheme() {{
      const body = document.body;
      const isDark = body.getAttribute('data-theme') === 'dark';
      const newTheme = isDark ? 'light' : 'dark';
      body.setAttribute('data-theme', newTheme);
      localStorage.setItem('agent_catalog_theme', newTheme);
      document.getElementById('themeIcon').innerText = isDark ? '🌙' : '☀️';
      document.getElementById('themeToggleBtn').innerHTML = isDark ? '🌙 Koyu Tema' : '☀️ Açık Tema';
    }}

    function escapeHtml(str) {{
      if (!str) return '';
      return str.replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
    }}

    // Global Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {{
      if (e.key === '/' && document.activeElement.id !== 'searchInput') {{
        e.preventDefault();
        document.getElementById('searchInput').focus();
      }}
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {{
        e.preventDefault();
        document.getElementById('searchInput').focus();
      }}
      if (e.key === 'Escape') {{
        if (currentSearch) clearSearch();
      }}
      if (e.key.toLowerCase() === 't' && document.activeElement.tagName !== 'INPUT') {{
        toggleTheme();
      }}
      if (e.key.toLowerCase() === 'v' && document.activeElement.tagName !== 'INPUT') {{
        setViewMode(currentViewMode === 'grid' ? 'table' : 'grid');
      }}
    }});

    // Initialize Theme & View
    const savedTheme = localStorage.getItem('agent_catalog_theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    if (savedTheme === 'light') {{
      document.getElementById('themeIcon').innerText = '🌙';
      document.getElementById('themeToggleBtn').innerHTML = '🌙 Koyu Tema';
    }}

    setViewMode(currentViewMode);
  </script>
</body>
</html>
"""


def main() -> int:
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            skills.append(parse_skill_md(skill_md))

    html_content = generate_catalog_html(skills)

    if "--check" in sys.argv:
        if not OUTPUT_HTML.is_file():
            print(f"HATA: {OUTPUT_HTML} mevcut değil!")
            return 1
        disk_content = OUTPUT_HTML.read_text(encoding="utf-8")
        if disk_content != html_content:
            print(f"HATA: {OUTPUT_HTML} güncel değil! 'python scripts/generate_skills_catalog.py' çalıştırın.")
            return 1
        print(f"[OK] {OUTPUT_HTML} güncel ({len(skills)} skill).")
        return 0

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html_content, encoding="utf-8")
    print(f"Katalog başarıyla derlendi ({len(skills)} skill): {OUTPUT_HTML}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
