#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajan Skill & Mimari Katalog Üreticisi (Skills Catalog HTML Generator).

`.agent/skills/` altındaki tüm `SKILL.md` dosyalarını ve kural sözlüklerini
tarayarak kullanıcı dostu, filtrelenebilir, kopyalanabilir ve modern
`skills-catalog.html` dosyasını derler.

Kullanım:
    python scripts/generate_skills_catalog.py
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
        "musgoku", "react-best-practices", "i18n-localization"
    ],
    "Teslimat & Kalite": [
        "git-release-workflow", "production-docker-architect",
        "karpathy-guidelines", "task-observer"
    ],
    "Marka & Doküman": [
        "brand", "doc-coauthoring", "musgoku-prd", "slides"
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
    "musgoku-prd": {
        "status": "Proje Dosyası",
        "badge_class": "badge-info",
        "file": "HANDOFF.md / PRD.md",
        "features": ["HANDOFF Protokolü", "90 Puan Kalite Kapısı", "KVKK Denetimi"],
        "detail": "Proje kökündeki zorunlu HANDOFF.md protokolünü kurar ve 90 puan kalite kapısıyla PRD üretir.",
        "sample_prompt": "Yeni bir özellik için kullanıcı sorularıyla kapsamı netleştirip uygulanabilir bir PRD çıkar.",
        "config_snippet": """# HANDOFF.md Şablonu:
- 0. Bu Projede Düşülen ve Kanıtlanmış Tuzaklar
- 1. Bu Oturumda Yapılanlar
- 2. Güncellik Kanıtı
- 3. Nerede Kaldık
- 4. Sıradaki İş"""
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
        "features": ["REST Controller", "JPA Entity", "Keyset Pagination", "WebSocket"],
        "detail": "Backend (Spring Boot/Java) veya Frontend mimari kuralları ve kalite kapılarını yönetir.",
        "sample_prompt": "Spring Boot REST controller ve JPA entity katmanını pagination ile oluştur.",
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
    "frontend-design": "Arayüzü modernleştir, AI-slop kalıplarını temizle ve [DESIGN-REFRESH] protokolünü uygula.",
    "ui-ux-pro-max": "Arayüzün renk paleti, tipografi ve erişilebilirlik (WCAG) kurallarını incele.",
    "canvas-design": "Etkinlik için ölçüsüz görsel sanat ve manifesto afişi posteri oluştur.",
    "banner-design": "Web sitesi hero alanı ve LinkedIn için 1584x396 ölçülü kapak görseli tasarla.",
    "design": "Kurumsal kimlik için logo brief'i ve kartvizit tasarım yönergelerini hazırla.",
    "slides": "Yatırımcı sunumu için PAS formülüyle 10 slaytlık pitch deck metni ve düzeni çıkar.",
    "doc-coauthoring": "Teknik mimari karar dokümanı (RFC / Decision Doc) taslağı oluştur.",
    "karpathy-guidelines": "Kod karmaşıklığını azalt, gereksiz soyutlamaları sadeleştir ve varsayımları yüzeye çıkar.",
    "react-best-practices": "React bileşenindeki gereksiz re-render'ları ve waterfall veri çekimlerini ortadan kaldır.",
    "theme-factory": "Uygulama için 10 hazır temadan birini seç ve HEX paletini uygula.",
    "web-ide-ux-architect": "Düşük gecikmeli, kod editörü ve split-pane panelli bir IDE arayüzü tasarla.",
    "mock-asset-provider": "Kullanıcı profilleri için kadın ve erkek portreleri içeren gerçekçi mock görseller sağla.",
    "onboarding-tour": "Yeni başlayan kullanıcılar için dashboard ve menü adımlarını tanıtan hafif bir Driver.js onboarding turu hazırla.",
    "production-docker-architect": "Üretim ortamı için hafif, multi-stage ve non-root kullanıcılı Dockerfile ve Compose oluştur.",
    "i18n-localization": "Uygulamadaki hardcode metinleri ve eksik çeviri anahtarlarını i18n_checker ile denetle ve düzelt.",
    "brand": "Marka kılavuzunu, ton ve mesaj çerçevesini docs/brand-guidelines.md olarak oluştur.",
    "musgoku-prd": "Yeni özellik için kapsamı, Gherkin kabul kriterlerini ve 90 puanlık PRD dokümanını hazırla."
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
        py_files = list(scripts_dir.glob("*.py"))
        if py_files:
            main_script = py_files[0].name
            cli_cmd = f"python .agent/skills/{name}/scripts/{main_script}"

    # Ek anahtar kelimeler (arama için)
    search_keywords = [name, category, purpose, cfg["file"], cfg["detail"]] + triggers
    if "features" in cfg:
        search_keywords.extend(cfg["features"])
    if name == "mock-asset-provider":
        search_keywords.extend(["github", "api", "unsplash", "pexels", "resim", "foto", "avatar", "profil", "etkinlik", "assets.json"])

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
    cat_buttons = "".join(
        f'<button class="chip" onclick="setCategoryFilter(\'{cat}\', this)">{cat} ({len(skills_in_cat)})</button>'
        for cat, skills_in_cat in CATEGORIES.items()
    )

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ajan Skill & Mimari Kataloğu — Antigravity Agent Ecosystem</title>
  <style>
    :root {{
      --bg: #0b0f19;
      --surface: #111827;
      --surface-hover: #1f293d;
      --card-bg: #151d30;
      --border: #22304d;
      --text-main: #f3f4f6;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-glow: rgba(56, 189, 248, 0.15);
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
      --danger-bg: rgba(220, 38, 38, 0.1);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.6;
      padding: 0;
      min-height: 100vh;
      transition: background-color 0.25s, color 0.25s;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 2.5rem 1.5rem;
    }}

    /* Header */
    header {{
      background: linear-gradient(180deg, var(--surface) 0%, var(--bg) 100%);
      border-bottom: 1px solid var(--border);
      padding: 2.5rem 1.5rem 1.5rem;
    }}
    .header-content {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 1.5rem;
    }}
    .title-area h1 {{
      font-size: 2.15rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .title-area h1 span.gradient {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .title-area p {{
      color: var(--text-muted);
      font-size: 1rem;
      margin-top: 0.5rem;
      max-width: 800px;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}
    .stat-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      font-size: 0.875rem;
      font-weight: 600;
    }}
    .stat-pill .num {{
      color: var(--primary);
      font-weight: 800;
    }}
    .btn-theme {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.55rem 0.9rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.2s;
    }}
    .btn-theme:hover {{
      background: var(--surface-hover);
      border-color: var(--primary);
    }}

    /* Integration Highlight Banner (GitHub & API Hub) */
    .integration-banner {{
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(129, 140, 248, 0.08) 100%);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: var(--radius-md);
      padding: 1.5rem;
      margin-bottom: 2rem;
      position: relative;
    }}
    .banner-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
    }}
    .banner-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}
    .banner-body {{
      margin-top: 1.25rem;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.25rem;
      border-top: 1px solid rgba(56, 189, 248, 0.15);
      padding-top: 1.25rem;
    }}
    .banner-col h4 {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 0.4rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .banner-col p {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}
    .code-preview {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.85rem;
      font-family: var(--font-mono);
      font-size: 0.775rem;
      color: #38bdf8;
      overflow-x: auto;
      margin-top: 0.5rem;
      position: relative;
    }}

    /* Toolbar */
    .toolbar {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 1.25rem;
      margin-bottom: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.3);
    }}
    .search-box {{
      position: relative;
      width: 100%;
    }}
    .search-input {{
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.85rem 1rem 0.85rem 2.85rem;
      border-radius: var(--radius-sm);
      font-size: 1rem;
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
    }}

    .filter-group {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.5rem;
    }}
    .filter-label {{
      font-size: 0.825rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-right: 0.5rem;
    }}
    .chip {{
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.4rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.825rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
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

    /* Grid of Cards */
    .skills-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
      gap: 1.5rem;
    }}

    /* Skill Card */
    .skill-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
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
    .skill-card-top {{
      margin-bottom: 1.25rem;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 0.75rem;
    }}
    .skill-name {{
      font-size: 1.3rem;
      font-weight: 700;
      font-family: var(--font-mono);
      color: var(--text-main);
    }}
    .skill-category {{
      font-size: 0.725rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--accent);
      background: rgba(129, 140, 248, 0.1);
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
      border: 1px solid rgba(129, 140, 248, 0.25);
    }}

    /* Badges */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.25rem 0.65rem;
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

    /* Feature tags */
    .features-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin: 0.6rem 0 1rem;
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
      font-size: 0.95rem;
      line-height: 1.5;
      margin-bottom: 1.25rem;
    }}

    .section-title {{
      font-size: 0.775rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .triggers-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-bottom: 1rem;
    }}
    .trigger-pill {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--primary);
      padding: 0.25rem 0.55rem;
      border-radius: var(--radius-sm);
      font-family: var(--font-mono);
      font-size: 0.75rem;
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
      font-size: 0.85rem;
      margin-bottom: 1rem;
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
      font-size: 0.8rem;
    }}

    /* Collapsible JSON Preview */
    .json-accordion {{
      margin-top: 0.6rem;
      margin-bottom: 1rem;
    }}
    .btn-toggle-json {{
      background: transparent;
      border: 1px dashed var(--border);
      color: var(--primary);
      font-size: 0.775rem;
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
      background: #080c14;
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
      font-size: 0.75rem;
      color: #a5f3fc;
      overflow-x: auto;
      max-height: 240px;
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
      padding: 0.6rem 0.75rem;
      font-size: 0.8rem;
      color: var(--danger);
      margin-bottom: 1rem;
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
      padding: 0.45rem 0.8rem;
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

    .toast {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #10b981;
      color: #ffffff;
      padding: 0.85rem 1.4rem;
      border-radius: var(--radius-md);
      font-size: 0.95rem;
      font-weight: 600;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
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
      padding: 4rem 1rem;
      color: var(--text-muted);
    }}
    .no-results h3 {{
      font-size: 1.3rem;
      margin-bottom: 0.5rem;
      color: var(--text-main);
    }}

    @media (max-width: 768px) {{
      .skills-grid {{ grid-template-columns: 1fr; }}
      .header-content {{ flex-direction: column; }}
      .title-area h1 {{ font-size: 1.75rem; }}
      .banner-body {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body data-theme="dark">

  <header>
    <div class="header-content">
      <div class="title-area">
        <h1>🚀 <span class="gradient">Ajan Skill & Mimari Kataloğu</span></h1>
        <p>Projedeki {len(skills)} skill'in sorumluluk sınırları, tetikleyici kelimeleri, GitHub/API entegrasyonları ve konfigürasyon gereksinimleri tek bir rehberde.</p>
      </div>
      <div class="header-actions">
        <div class="stat-pill">
          <span>Toplam Skill:</span>
          <span class="num">{len(skills)}</span>
        </div>
        <button class="btn-theme" id="themeToggleBtn" onclick="toggleTheme()">
          <span id="themeIcon">☀️</span> Açık Tema
        </button>
      </div>
    </div>
  </header>

  <div class="container">
    
    <!-- Integration Highlight Banner (GitHub Repo & API Hub) -->
    <div class="integration-banner">
      <div class="banner-header" onclick="toggleBanner()">
        <div class="banner-title">
          <span>⚡</span>
          <span>Özel Entegrasyon Rehberi: GitHub Reposu ve Harici API Ekleme (mock-asset-provider)</span>
        </div>
        <button class="btn-theme" style="padding: 0.3rem 0.7rem; font-size: 0.75rem;">
          <span id="bannerToggleIcon">▼</span> Göster / Gizle
        </button>
      </div>
      <div class="banner-body" id="bannerBody">
        <div class="banner-col">
          <h4>📁 1. Projeye Özel GitHub Görsel Paketi</h4>
          <p>Kullanıcı kendi Figma export paketini veya hazır görsel reposunu projeye bağlayabilir. Ajan tek komutla indirir ve <code>public/mock-assets/</code> dizinine yerleştirir.</p>
          <div class="code-preview">
"github": {{
  "enabled": true,
  "repo_url": "https://github.com/user/event-images-pack"
}}
          </div>
        </div>
        <div class="banner-col">
          <h4>🔑 2. Harici API Entegrasyonu (Unsplash & Pexels)</h4>
          <p>Kullanıcı kendi Unsplash veya Pexels API anahtarını <code>.agent/config/assets.json</code> içine ekleyerek yüksek çözünürlüklü tematik fotoğrafları doğrudan projeye akıtabilir.</p>
          <div class="code-preview">
"api": {{
  "unsplash_access_key": "YOUR_UNSPLASH_KEY",
  "pexels_api_key": "YOUR_PEXELS_KEY"
}}
          </div>
        </div>
        <div class="banner-col">
          <h4>🌐 3. Sıfır-Ayar (Zero-Config) Otomatik Fallback</h4>
          <p>Hiçbir repo veya API anahtarı verilmezse ajan asla boş gri kutu bırakmaz; RandomUser (kadın/erkek portre), Picsum (etkinlik/manzara) ve DiceBear (SVG) servisleriyle besler.</p>
          <button class="btn-copy-prompt" style="margin-top: 0.75rem; width: 100%; justify-content: center;" onclick="copyAssetsJsonTemplate()">
            📋 assets.json Tam Şablonunu Kopyala
          </button>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="Skill adı, 'github', 'api', 'mock görsel', 'banner', 'commitx', 'tokens', 'i18n' ara..." oninput="filterSkills()">
      </div>
      <div class="filter-group">
        <span class="filter-label">Kategori:</span>
        <button class="chip active" onclick="setCategoryFilter('all', this)">Tümü ({len(skills)})</button>
        {cat_buttons}
      </div>
      <div class="filter-group">
        <span class="filter-label">Config Durumu:</span>
        <button class="chip active" onclick="setConfigFilter('all', this)">Tümü</button>
        <button class="chip" onclick="setConfigFilter('Sıfır-Ayar', this)">🟢 Sıfır-Ayar (Zero-Config)</button>
        <button class="chip" onclick="setConfigFilter('Opsiyonel Config', this)">🟡 Opsiyonel Config</button>
        <button class="chip" onclick="setConfigFilter('Proje Dosyası', this)">🔵 Proje Dosyası Gerektiren</button>
      </div>
    </div>

    <!-- Skills Grid -->
    <div class="skills-grid" id="skillsGrid"></div>
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

    function renderCards() {{
      const grid = document.getElementById('skillsGrid');
      grid.innerHTML = '';

      const filtered = allSkills.filter(s => {{
        const matchCategory = (currentCategory === 'all' || s.category === currentCategory);
        const matchConfig = (currentConfig === 'all' || s.config_status.includes(currentConfig));
        const query = currentSearch.toLowerCase().trim();
        const matchSearch = !query || s.search_index.includes(query);
        return matchCategory && matchConfig && matchSearch;
      }});

      if (filtered.length === 0) {{
        grid.innerHTML = `
          <div class="no-results">
            <h3>Sonuç Bulunamadı</h3>
            <p>Arama kriterlerine veya seçilen filtrelere uygun skill bulunamadı.</p>
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

        card.innerHTML = `
          <div class="skill-card-top">
            <div class="card-header">
              <div>
                <div class="skill-name">${{escapeHtml(s.name)}}</div>
                <span class="skill-category">${{escapeHtml(s.category)}}</span>
              </div>
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

    function filterSkills() {{
      currentSearch = document.getElementById('searchInput').value;
      renderCards();
    }}

    function setCategoryFilter(cat, btn) {{
      currentCategory = cat;
      btn.parentElement.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      renderCards();
    }}

    function setConfigFilter(cfg, btn) {{
      currentConfig = cfg;
      btn.parentElement.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      renderCards();
    }}

    function toggleJsonDrawer(id) {{
      const el = document.getElementById(id);
      if (el) {{
        el.classList.toggle('open');
      }}
    }}

    function toggleBanner() {{
      const b = document.getElementById('bannerBody');
      const icon = document.getElementById('bannerToggleIcon');
      if (b.style.display === 'none') {{
        b.style.display = 'grid';
        icon.innerText = '▼';
      }} else {{
        b.style.display = 'none';
        icon.innerText = '▶';
      }}
    }}

    function copyAssetsJsonTemplate() {{
      const tpl = JSON.stringify({{
        "enabled": true,
        "storage_dir": "public/mock-assets",
        "download_locally": true,
        "sources": {{
          "github": {{
            "enabled": true,
            "repo_url": "https://github.com/kullanici/etkinlik-resimleri-paketi",
            "branch": "main",
            "sub_path": "images"
          }},
          "api": {{
            "unsplash_access_key": "YOUR_UNSPLASH_KEY",
            "pexels_api_key": "YOUR_PEXELS_KEY"
          }},
          "default_fallbacks": {{
            "portraits": "randomuser",
            "events": "picsum",
            "products": "dummyjson",
            "general": "picsum"
          }}
        }}
      }}, null, 2);
      copyToClipboard(tpl, ".agent/config/assets.json tam şablonu kopyalandı!");
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

    const savedTheme = localStorage.getItem('agent_catalog_theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    if (savedTheme === 'light') {{
      document.getElementById('themeIcon').innerText = '🌙';
      document.getElementById('themeToggleBtn').innerHTML = '🌙 Koyu Tema';
    }}

    renderCards();
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
