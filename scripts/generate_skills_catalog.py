#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajan Skill & Mimari Katalog Üreticisi (Skills Catalog HTML Generator).

`.agent/skills/` altındaki tüm `SKILL.md` dosyalarını, kural sözlüklerini ve
oturum slash komutlarını (Ensemble Slash Commands) tarayarak kullanıcı dostu,
filtrelenebilir, çift görünümlü (Kart Grid & Kompakt Takip Tablosu),
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
        "diagnosing-bugs", "code-review", "my-idea", "security-audit",
        "prelaunch-audit"
    ],
    "Marka & Doküman": [
        "brand", "doc-coauthoring", "slides", "seo-growth"
    ],
    "Oturum Komutları (Ensemble)": [
        "ui-polish", "verify-prd", "verify-last", "verify-sprint", "fix-bug", "check-security",
        "council", "seo-apply", "commitx", "gs-update",
        "prelaunch", "prelaunch-update"
    ]
}

SLASH_COMMANDS = [
    {
        "command": "/verify-prd",
        "aliases": ["/verify-prd"],
        "name": "PRD & Kabul Kriterleri Doğrulama Motoru",
        "badge": "Kalite & Güven",
        "badge_class": "badge-info",
        "skills": ["doc-coauthoring", "code-review", "Katman Bütünlüğü (5-Layer)"],
        "goal": "\"Bitti ama doğru mu bitti?\" Güven Motoru",
        "description": "Şartnamedeki kabul kriterlerini (Gherkin AC), 5 Katmanlı Dikey Dilimi (DB Migration, View/RPC, Client API, UI UX, Admin Formu) ve kapsam sapmalarını (Scope Creep) denetleyip kanıt tablosu üretir.",
        "sample_prompt": "/verify-prd: Son tamamlanan özelliğin kabul kriterlerini, 5 katman dikey dilim bütünlüğünü ve regression risklerini bağımsız denetle.",
        "protocol": "1. Gherkin AC Denetimi ➜ 2. 5 Katman Analizi ➜ 3. Scope Creep Taraması ➜ 4. Deterministik Test Kanıtı",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/ui-polish",
        "aliases": ["/ui-polish", "[UI-POLISH]", "[DESIGN-REFRESH]"],
        "name": "Tasarım & UI/UX İnce Ayar Üçlüsü",
        "badge": "Tasarım & Zanaat",
        "badge_class": "badge-accent",
        "skills": ["ui-ux-pro-max", "frontend-design", "ui-styling"],
        "goal": "Tasarım & Zanaat Üçlüsü (Hazır Bileşen/Palet, Anti-Slop & WCAG 2.2 AA)",
        "description": "55 hazır bileşen teması (get_component.py) ve 10 ölçülmüş palet (get_palette.py) ile başlayıp, 79 stil ve 192 palet seçimi, generic AI-slop temizliği ve deterministik kontrast/WCAG doğrulaması yapar.",
        "sample_prompt": "/ui-polish: Arayüzü hazır bileşen ve paletlerden ilhamla zenginleştir, generic AI kalıplarını temizle, tipografi ve boşluk ritmini modernleştir, WCAG kontrastını doğrula.",
        "protocol": "get_component.py / get_palette.py (hazır yapı) ➜ ui-ux-pro-max ➜ frontend-design ➜ ui-styling + check_design_slop.py",
        "category": "Tasarım & UI"
    },
    {
        "command": "/check-security",
        "aliases": ["/check-security"],
        "name": "Güvenlik, Savunma & İstismar Kalkanı",
        "badge": "Güvenlik & Savunma",
        "badge_class": "badge-danger",
        "skills": ["security-audit", "development-workflow", "prelaunch-audit"],
        "goal": "OWASP & Public Form Savunması",
        "description": "OWASP zafiyet avcılığı, public form kalkanı (Turnstile, Rate-limit, Sanitization, Blind Insert RLS) ve secrets/env sızıntı denetimi yürütür.",
        "sample_prompt": "/check-security: Sistem genelinde yetki aşımı, public form abuse riskleri ve env sızıntılarını derinlemesine tara.",
        "protocol": "Güvenlik Denetimi ➜ Halka 2 Savunması (Turnstile, Rate-limit, RLS) ➜ Secret/Env Sızıntı Taraması",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/fix-bug",
        "aliases": ["/fix-bug"],
        "name": "Sistematik Hata Teşhis & Kırmızı Döngü",
        "badge": "Hata Teşhisi",
        "badge_class": "badge-warning",
        "skills": ["diagnosing-bugs", "musgoku", "karpathy-guidelines"],
        "goal": "Kırmızı Döngü & Cerrahi Onarım",
        "description": "Kod yazmadan önce hatayı kanıtlayan kırmızı test/kanıt döngüsü kurar, cerrahi onarım yapar, Karpathy gereksiz kod ve yan etki temizliği işletir.",
        "sample_prompt": "/fix-bug: Çöken endpoint için önce kırmızı geri bildirim döngüsü kur, 3 hipotez üret ve cerrahi düzeltme yap.",
        "protocol": "diagnosing-bugs (kırmızı döngü) ➜ musgoku (onarım) ➜ karpathy-guidelines (sadeleştirme)",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/council",
        "aliases": ["/council"],
        "name": "3-Aşamalı Konsey Hakemliği",
        "badge": "Mimari Hakemlik",
        "badge_class": "badge-info",
        "skills": ["karpathy-guidelines", "doc-coauthoring"],
        "goal": "Kör Akran İncelemesi & ADR Kararı",
        "description": "Mimari ikilem ve riskli refactoring kararlarında 3 aşamalı anonim körleme (Blind Review, Borda Skoru & Chairman Synthesis) ve ADR mimari karar kaydı üretir.",
        "sample_prompt": "/council: Mimari ikilem için 3 alternatifli kör hakemlik konseyi topla, Borda puanı hesapla ve ADR kaydı çıkar.",
        "protocol": "Stage 1 (Alternatifler) ➜ Stage 2 (Kör Hakemlik) ➜ Stage 3 (Chairman Sentezi) ➜ docs/adr/ Karar Kaydı",
        "category": "Kod & Mimari"
    },
    {
        "command": "/prelaunch",
        "aliases": ["/prelaunch"],
        "name": "Canlıya Alma Kalite Denetimi",
        "badge": "Lansman & Uyum",
        "badge_class": "badge-success",
        "skills": ["prelaunch-audit"],
        "goal": "20 Maddelik Lansman & KVKK/GDPR Kontrolü",
        "description": "20 maddelik tam kontrol listesi (KVKK m.10, 7499 s. Kanun, Consent Mode v2, ham HTML SEO, WCAG 2.2 AA, robots, sitemap) ve GO/NO-GO karar raporu üretir.",
        "sample_prompt": "/prelaunch: Sitemizi yayına almaya hazır mıyız? 20 maddelik çekirdek denetimi ve yasal onay mekanizmalarını doğrula.",
        "protocol": "20 Çekirdek Madde + Yasal/Privacy + SEO/Crawler + Erişilebilirlik (Axe) ➜ GO/NO-GO Karnesi",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/prelaunch-update",
        "aliases": ["/prelaunch-update"],
        "name": "Mevzuat & Kural Güncelleyici",
        "badge": "Mevzuat Senkronu",
        "badge_class": "badge-warning",
        "skills": ["prelaunch-audit"],
        "goal": "Dinamik Mevzuat ve Para Cezası Güncelleyici",
        "description": "İdari para cezaları, KVKK bildirim limitleri ve Google Search kurallarını resmi kaynaklardan sorgulayıp markdown referanslarını cerrahi günceller.",
        "sample_prompt": "/prelaunch-update: Güncel KVKK ve GDPR idari para cezalarını resmi tebliğlerden sorgula ve dokümanları güncelle.",
        "protocol": "prelaunch_updater.py (Resmi Kaynak Sorgusu ➜ Diff & Markdown Cerrahi Senkronizasyonu)",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/seo-apply",
        "aliases": ["/seo-apply", "[SEO-APPLY]"],
        "name": "Uçtan Uca SEO & GEO Altyapısı",
        "badge": "SEO & Growth",
        "badge_class": "badge-accent",
        "skills": ["seo-growth", "frontend-design"],
        "goal": "Arama Motoru & AI Crawler Altyapısı",
        "description": "Kod tabanına bizzat girer; semantik meta başlık/açıklama, canonical, OpenGraph, JSON-LD Schema.org, AI crawler robots.txt, sitemap.xml ve /llms.txt dosyalarını üretip seo_checker.py ile doğrular.",
        "sample_prompt": "/seo-apply: Sitemiz için JSON-LD şemaları, OpenGraph etiketleri, robots.txt ve llms.txt dosyalarını kur ve doğrula.",
        "protocol": "seo-growth (strateji) ➜ frontend-design (meta/DOM) ➜ seo_checker.py (doğrulama)",
        "category": "Marka & Doküman"
    },
    {
        "command": "/commitx",
        "aliases": ["/commitx", "commitx", "commitle"],
        "name": "Peşin Yetkili Sürüm Yayını",
        "badge": "Sürüm & Git",
        "badge_class": "badge-success",
        "skills": ["git-release-workflow"],
        "goal": "Ara Onaysız Otomatik Commit, Tag & Push",
        "description": "Doğrulama kapılarını çalıştırır; ara onay sormadan git add → git commit → git tag → git push zincirini tek nefeste tamamlar.",
        "sample_prompt": "commitx: Değişiklikleri doğrula, semantik tag artır ve uzak depoya push et.",
        "protocol": "Kapı Doğrulaması ➜ Semver Artırma ➜ git add . ➜ git commit ➜ git tag ➜ git push HEAD & tags",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/gs-update",
        "aliases": ["/gs-update", "GS güncelle", "skill update"],
        "name": "Cerrahi Skill Seti Senkronu",
        "badge": "Bakım & Senkron",
        "badge_class": "badge-info",
        "skills": ["musgoku"],
        "goal": "Sıfır-Şişkinlik ve Proje Kuralı Korumalı Güncelleme",
        "description": "Proje kuralını koruyarak ve gereksiz dosya indirmeden ajan becerilerini cerrahi olarak en son sürüme senkronlar.",
        "sample_prompt": "/gs-update: Kurulu skill setini en son sürüme güncelle, proje ek kurallarını koru.",
        "protocol": "npx goku-dev-skills update (Proje kuralı koruması, yalnızca kurulu olanları güncelleme)",
        "category": "Kod & Mimari"
    }
]

CONFIG_METADATA = {
    "prelaunch-audit": {
        "status": "Production Ready",
        "badge_class": "badge-success",
        "file": ".agent/skills/prelaunch-audit/SKILL.md",
        "features": [
            "20 Maddelik Çekirdek Denetim",
            "KVKK m.10 & 7499 s. Kanun Yurt Dışı Aktarımı",
            "Google Consent Mode v2 & Çerez Doğrulama",
            "WCAG 2.2 AA Headless Axe Taraması",
            "Ham HTML & AI Bot Taksonomisi (llms.txt)",
            "/prelaunch & /prelaunch-update Komutları"
        ],
        "detail": "Canlıya çıkış (production launch) öncesi yasal, gizlilik, SEO, erişilebilirlik ve altyapı denetimi. /prelaunch ile kapsamlı denetim raporu üretir; /prelaunch-update ile mevzuat ve platform değişikliklerini AI modeliyle günceller.",
        "sample_prompt": "/prelaunch: Sitemizi canlıya almaya hazır mıyız? 20 maddelik çekirdek denetimi ve consent kontrolünü çalıştır.",
        "config_snippet": """# /prelaunch veya /prelaunch-update komutu ile doğrudan tetiklenebilir
python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py --url https://example.com
node .agent/skills/prelaunch-audit/scripts/consent-check.mjs https://example.com"""
    },
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
    slash_commands_json = json.dumps(SLASH_COMMANDS, ensure_ascii=False)

    pkg_json_file = PROJECT_ROOT / "package.json"
    pkg_version = "1.12.0"
    if pkg_json_file.is_file():
        try:
            pkg_version = json.loads(pkg_json_file.read_text(encoding="utf-8")).get("version", "1.12.0")
        except Exception:
            pass

    cat_badges = {
        "Tasarım & UI": "cat-design",
        "Kod & Mimari": "cat-code",
        "Teslimat & Kalite": "cat-delivery",
        "Marka & Doküman": "cat-brand",
        "Oturum Komutları (Ensemble)": "cat-ensemble"
    }

    cat_buttons = "".join(
        f'<button class="chip {cat_badges.get(cat, "")}" onclick="setCategoryFilter(\'{cat}\', this)">'
        f'{cat} <span class="chip-count">({len(skills_in_cat)})</span></button>'
        for cat, skills_in_cat in CATEGORIES.items()
    )

    quick_slash_pills = "".join(
        f'<button class="quick-slash-pill" onclick="quickSelectSlash(\'{cmd["command"]}\')" title="{cmd["name"]}: {cmd["goal"]}">'
        f'<svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> {cmd["command"]}</button>'
        for cmd in SLASH_COMMANDS
    )

    return f"""<!DOCTYPE html>
<html lang="tr" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Goku Dev Skills Kataloğu — Ajan Becerileri & Mimari Kurallar</title>
  
  <!-- Craft Typography: Plus Jakarta Sans & JetBrains Mono (Operate Surface Mode) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">

  <style>
    /* ==========================================================================
       3-TIER DESIGN TOKEN ARCHITECTURE (design-system & frontend-design)
       ========================================================================== */
    :root {{
      /* --- Layer 1: Primitive Tokens (Foundational Values) --- */
      --slate-950: #090d16;
      --slate-900: #0f172a;
      --slate-850: #131d33;
      --slate-800: #1e293b;
      --slate-700: #334155;
      --slate-600: #475569;
      --slate-500: #64748b;
      --slate-400: #94a3b8;
      --slate-300: #cbd5e1;
      --slate-200: #e2e8f0;
      --slate-100: #f1f5f9;
      --slate-50:  #f8fafc;
      --white:     #ffffff;

      --sky-400:   #38bdf8;
      --sky-500:   #0ea5e9;
      --sky-600:   #0284c7;

      --indigo-400: #818cf8;
      --indigo-500: #6366f1;

      --emerald-400: #34d399;
      --emerald-500: #10b981;
      --emerald-600: #059669;

      --amber-400: #fbbf24;
      --amber-500: #f59e0b;
      --amber-600: #d97706;

      --rose-400:  #fb7185;
      --rose-500:  #f43f5e;
      --rose-600:  #e11d48;

      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', "SFMono-Regular", Consolas, Menlo, monospace;

      --radius-xs: 4px;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-full: 9999px;

      /* --- Layer 2: Semantic Tokens (Dark Theme - Default) --- */
      --bg-canvas: #070a12;
      --bg-surface: #0e1526;
      --bg-surface-elevated: #131d33;
      --bg-surface-hover: #18243e;
      --bg-subtle: rgba(255, 255, 255, 0.04);

      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-strong: rgba(255, 255, 255, 0.16);
      --border-hover: rgba(56, 189, 248, 0.4);

      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-tertiary: #64748b;

      --accent-primary: var(--sky-400);
      --accent-primary-subtle: rgba(56, 189, 248, 0.1);
      --accent-primary-border: rgba(56, 189, 248, 0.25);

      --accent-slash: var(--rose-400);
      --accent-slash-subtle: rgba(244, 63, 94, 0.1);
      --accent-slash-border: rgba(244, 63, 94, 0.25);

      --status-success: var(--emerald-400);
      --status-success-subtle: rgba(52, 211, 153, 0.1);
      --status-success-border: rgba(52, 211, 153, 0.25);

      --status-warning: var(--amber-400);
      --status-warning-subtle: rgba(251, 191, 36, 0.1);
      --status-warning-border: rgba(251, 191, 36, 0.25);

      --status-info: var(--sky-400);
      --status-info-subtle: rgba(56, 189, 248, 0.1);
      --status-info-border: rgba(56, 189, 248, 0.25);

      --status-danger: var(--rose-400);
      --status-danger-subtle: rgba(248, 113, 113, 0.1);
      --status-danger-border: rgba(248, 113, 113, 0.25);

      --ring-focus: var(--sky-400);

      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.4);
      --shadow-md: 0 6px 18px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 14px 34px rgba(0, 0, 0, 0.55);

      /* --- Layer 3: Component Tokens --- */
      --header-bg: rgba(14, 21, 38, 0.88);
      --card-bg: var(--bg-surface);
      --card-border: var(--border-subtle);
      --search-input-bg: #090e1a;
      --code-block-bg: #060911;
      --pill-bg: var(--bg-surface-elevated);
    }}

    [data-theme="light"] {{
      /* --- Layer 2: Semantic Tokens (Light Theme - Swiss Clean) --- */
      --bg-canvas: #f8fafc;
      --bg-surface: #ffffff;
      --bg-surface-elevated: #f1f5f9;
      --bg-surface-hover: #e2e8f0;
      --bg-subtle: #f8fafc;

      --border-subtle: #e2e8f0;
      --border-strong: #cbd5e1;
      --border-hover: var(--sky-600);

      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-tertiary: #64748b;

      --accent-primary: var(--sky-600);
      --accent-primary-subtle: rgba(2, 132, 199, 0.08);
      --accent-primary-border: rgba(2, 132, 199, 0.2);

      --accent-slash: var(--rose-600);
      --accent-slash-subtle: rgba(225, 29, 72, 0.08);
      --accent-slash-border: rgba(225, 29, 72, 0.2);

      --status-success: var(--emerald-600);
      --status-success-subtle: rgba(5, 150, 105, 0.08);
      --status-success-border: rgba(5, 150, 105, 0.2);

      --status-warning: #b45309;
      --status-warning-subtle: rgba(217, 119, 6, 0.08);
      --status-warning-border: rgba(217, 119, 6, 0.2);

      --status-info: var(--sky-600);
      --status-info-subtle: rgba(2, 132, 199, 0.08);
      --status-info-border: rgba(2, 132, 199, 0.2);

      --status-danger: var(--rose-600);
      --status-danger-subtle: rgba(220, 38, 38, 0.08);
      --status-danger-border: rgba(220, 38, 38, 0.2);

      --ring-focus: var(--sky-600);

      --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06);
      --shadow-md: 0 4px 14px rgba(15, 23, 42, 0.08);
      --shadow-lg: 0 12px 28px rgba(15, 23, 42, 0.12);

      --header-bg: rgba(255, 255, 255, 0.9);
      --card-bg: #ffffff;
      --card-border: #e2e8f0;
      --search-input-bg: #ffffff;
      --code-block-bg: #f8fafc;
      --pill-bg: #f1f5f9;
    }}

    /* ==========================================================================
       THEMED BROWSER SURFACES (design-skills-enforcement.md §2.6 B.4)
       ========================================================================== */
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    ::selection {{
      background: var(--accent-primary-subtle);
      color: var(--accent-primary);
    }}

    input, textarea {{
      caret-color: var(--accent-primary);
    }}

    ::-webkit-scrollbar {{
      width: 7px;
      height: 7px;
    }}
    ::-webkit-scrollbar-track {{
      background: var(--bg-canvas);
    }}
    ::-webkit-scrollbar-thumb {{
      background: var(--border-strong);
      border-radius: var(--radius-full);
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: var(--slate-500);
    }}

    :focus-visible {{
      outline: 2px solid var(--ring-focus);
      outline-offset: 2px;
    }}

    body {{
      font-family: var(--font-sans);
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      line-height: 1.55;
      min-height: 100vh;
      transition: background-color 0.2s cubic-bezier(0.16, 1, 0.3, 1), color 0.2s;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    /* Vector SVG Icon System (No emojis §2.6 A.8) */
    .svg-icon {{
      width: 15px;
      height: 15px;
      display: inline-block;
      vertical-align: -0.15em;
      stroke: currentColor;
      stroke-width: 1.75;
      stroke-linecap: round;
      stroke-linejoin: round;
      fill: none;
      flex-shrink: 0;
    }}
    .svg-icon-lg {{
      width: 18px;
      height: 18px;
    }}
    .svg-slash {{
      color: var(--accent-slash);
    }}

    /* ==========================================================================
       HEADER & NAVIGATION BAR
       ========================================================================== */
    header {{
      position: sticky;
      top: 0;
      z-index: 1000;
      background: var(--header-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 0.75rem 1.75rem;
      transition: border-color 0.2s;
    }}

    .header-content {{
      max-width: 1440px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1.25rem;
      flex-wrap: wrap;
    }}

    .brand-area {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }}
    .brand-area h1 {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.025em;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .version-tag {{
      font-family: var(--font-mono);
      font-size: 0.7rem;
      font-weight: 600;
      background: var(--accent-primary-subtle);
      color: var(--accent-primary);
      border: 1px solid var(--accent-primary-border);
      padding: 0.15rem 0.5rem;
      border-radius: var(--radius-full);
      font-variant-numeric: tabular-nums;
    }}

    /* View Switcher Tabs */
    .view-mode-tabs {{
      display: flex;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 0.2rem;
      gap: 0.2rem;
    }}
    .tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-secondary);
      padding: 0.45rem 0.9rem;
      font-size: 0.825rem;
      font-weight: 600;
      font-family: var(--font-sans);
      cursor: pointer;
      border-radius: var(--radius-xs);
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      transition: background-color 0.15s, color 0.15s;
    }}
    .tab-btn:hover {{
      color: var(--text-primary);
      background: var(--bg-surface-hover);
    }}
    .tab-btn.active {{
      background: var(--bg-surface-elevated);
      color: var(--accent-primary);
      font-weight: 700;
    }}
    .tab-btn.active.slash-active {{
      color: var(--accent-slash);
      background: var(--accent-slash-subtle);
    }}
    .tab-badge {{
      font-family: var(--font-mono);
      font-size: 0.68rem;
      background: var(--bg-subtle);
      border: 1px solid var(--border-subtle);
      padding: 0.08rem 0.35rem;
      border-radius: var(--radius-full);
      font-variant-numeric: tabular-nums;
    }}
    .tab-btn.active .tab-badge {{
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #090d16;
    }}
    .tab-btn.active.slash-active .tab-badge {{
      background: var(--accent-slash);
      border-color: var(--accent-slash);
      color: #ffffff;
    }}

    .theme-toggle-btn {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      padding: 0.42rem 0.8rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 600;
      font-family: var(--font-sans);
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      transition: border-color 0.15s, color 0.15s;
    }}
    .theme-toggle-btn:hover {{
      color: var(--text-primary);
      border-color: var(--border-strong);
    }}

    /* ==========================================================================
       CONTAINER & HERO SECTION
       ========================================================================== */
    .container {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 2rem 1.75rem 4rem;
    }}

    .hero-strip {{
      margin-bottom: 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      flex-wrap: wrap;
      gap: 1.25rem;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 1.5rem;
    }}
    .hero-desc {{
      color: var(--text-secondary);
      font-size: 0.94rem;
      max-width: 780px;
      line-height: 1.6;
    }}
    .hero-command-box {{
      display: inline-flex;
      align-items: center;
      gap: 0.65rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      padding: 0.45rem 0.85rem;
      border-radius: var(--radius-sm);
      margin-top: 0.75rem;
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: var(--text-primary);
      cursor: pointer;
      transition: border-color 0.15s, background-color 0.15s;
    }}
    .hero-command-box:hover {{
      border-color: var(--accent-primary);
      background: var(--bg-surface-elevated);
    }}
    .hero-command-box .cmd-text {{
      color: var(--accent-primary);
      font-weight: 600;
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
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      padding: 0.4rem 0.85rem;
      border-radius: var(--radius-full);
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-secondary);
      font-variant-numeric: tabular-nums;
    }}
    .stat-pill .num {{
      color: var(--accent-primary);
      font-weight: 700;
      font-family: var(--font-mono);
    }}
    .stat-pill.slash-pill .num {{
      color: var(--accent-slash);
    }}

    /* ==========================================================================
       QUICK SLASH COMMAND RIBBON
       ========================================================================== */
    .quick-slash-ribbon {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.75rem 1.15rem;
      margin-bottom: 1.5rem;
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }}
    .quick-ribbon-title {{
      font-size: 0.76rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--accent-slash);
      display: flex;
      align-items: center;
      gap: 0.35rem;
      margin-right: 0.25rem;
      white-space: nowrap;
    }}
    .quick-slash-pill {{
      background: var(--bg-canvas);
      border: 1px solid var(--accent-slash-border);
      color: var(--text-primary);
      padding: 0.3rem 0.6rem;
      border-radius: var(--radius-sm);
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: background-color 0.15s, border-color 0.15s, color 0.15s;
    }}
    .quick-slash-pill:hover {{
      background: var(--accent-slash-subtle);
      border-color: var(--accent-slash);
      color: var(--accent-slash);
    }}

    /* ==========================================================================
       TOOLBAR: SEARCH & FILTER HUB
       ========================================================================== */
    .toolbar {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 1.15rem;
      margin-bottom: 1.75rem;
      display: flex;
      flex-direction: column;
      gap: 0.9rem;
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
      background: var(--search-input-bg);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      padding: 0.75rem 2.75rem 0.75rem 2.6rem;
      border-radius: var(--radius-sm);
      font-size: 0.92rem;
      font-family: var(--font-sans);
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s;
    }}
    .search-input:focus {{
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 3px var(--accent-primary-subtle);
    }}
    .search-icon {{
      position: absolute;
      left: 0.9rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-tertiary);
      pointer-events: none;
    }}
    .btn-clear-search {{
      position: absolute;
      right: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      cursor: pointer;
      font-size: 0.85rem;
      padding: 0.2rem 0.4rem;
      border-radius: var(--radius-xs);
      display: none;
    }}
    .btn-clear-search:hover {{
      color: var(--text-primary);
    }}
    .kbd-shortcut {{
      position: absolute;
      right: 0.9rem;
      top: 50%;
      transform: translateY(-50%);
      background: var(--bg-subtle);
      border: 1px solid var(--border-subtle);
      color: var(--text-tertiary);
      font-size: 0.7rem;
      font-family: var(--font-mono);
      padding: 0.15rem 0.4rem;
      border-radius: var(--radius-xs);
      pointer-events: none;
    }}

    .filter-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.9rem;
      border-top: 1px solid var(--border-subtle);
      padding-top: 0.85rem;
    }}
    .filter-group {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.4rem;
    }}
    .filter-label {{
      font-size: 0.74rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-tertiary);
      margin-right: 0.35rem;
    }}

    .chip {{
      background: var(--bg-canvas);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      padding: 0.32rem 0.75rem;
      border-radius: var(--radius-full);
      font-size: 0.78rem;
      font-weight: 600;
      font-family: var(--font-sans);
      cursor: pointer;
      transition: border-color 0.15s, color 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-variant-numeric: tabular-nums;
    }}
    .chip:hover {{
      color: var(--text-primary);
      border-color: var(--border-strong);
    }}
    .chip.active {{
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #090d16;
      font-weight: 700;
    }}
    .chip-count {{
      font-size: 0.7rem;
      opacity: 0.85;
      font-family: var(--font-mono);
    }}

    .filter-summary {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      padding-top: 0.2rem;
    }}
    .btn-reset-filters {{
      background: transparent;
      border: none;
      color: var(--accent-primary);
      text-decoration: underline;
      cursor: pointer;
      font-size: 0.8rem;
      font-family: var(--font-sans);
    }}

    /* ==========================================================================
       SECTION HEADERS
       ========================================================================== */
    .view-section-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
    }}
    .view-section-title {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    /* ==========================================================================
       CARDS & GRIDS (Craft Floor: No thick stripes, clean 1px borders)
       ========================================================================== */
    .skills-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
      gap: 1.25rem;
    }}

    .skill-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1.35rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: border-color 0.15s, box-shadow 0.15s;
      position: relative;
    }}
    .skill-card:hover {{
      border-color: var(--border-hover);
      box-shadow: var(--shadow-sm);
    }}

    .card-top {{
      margin-bottom: 1.15rem;
    }}

    .card-meta-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }}
    .card-index {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--text-tertiary);
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }}

    .cat-badge {{
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.02em;
      padding: 0.18rem 0.5rem;
      border-radius: var(--radius-xs);
    }}
    .cat-design {{ background: var(--accent-primary-subtle); color: var(--accent-primary); border: 1px solid var(--accent-primary-border); }}
    .cat-code {{ background: var(--status-success-subtle); color: var(--status-success); border: 1px solid var(--status-success-border); }}
    .cat-delivery {{ background: var(--status-warning-subtle); color: var(--status-warning); border: 1px solid var(--status-warning-border); }}
    .cat-brand {{ background: var(--accent-slash-subtle); color: var(--accent-slash); border: 1px solid var(--accent-slash-border); }}
    .cat-ensemble {{ background: var(--accent-secondary-subtle); color: var(--accent-secondary); border: 1px solid var(--accent-secondary-border); }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.85rem;
      margin-bottom: 0.75rem;
    }}
    .skill-name {{
      font-size: 1.15rem;
      font-weight: 700;
      font-family: var(--font-mono);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 0.4rem;
      letter-spacing: -0.02em;
    }}

    /* Badges */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.2rem 0.55rem;
      border-radius: var(--radius-xs);
      font-size: 0.72rem;
      font-weight: 600;
      white-space: nowrap;
    }}
    .badge-success {{
      background: var(--status-success-subtle);
      color: var(--status-success);
      border: 1px solid var(--status-success-border);
    }}
    .badge-warning {{
      background: var(--status-warning-subtle);
      color: var(--status-warning);
      border: 1px solid var(--status-warning-border);
    }}
    .badge-info {{
      background: var(--status-info-subtle);
      color: var(--status-info);
      border: 1px solid var(--status-info-border);
    }}
    .badge-accent {{
      background: var(--accent-slash-subtle);
      color: var(--accent-slash);
      border: 1px solid var(--accent-slash-border);
    }}

    .features-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin: 0.35rem 0 0.85rem;
    }}
    .feature-tag {{
      font-size: 0.7rem;
      font-weight: 600;
      background: var(--bg-subtle);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-xs);
    }}

    .skill-purpose {{
      color: var(--text-primary);
      font-size: 0.88rem;
      line-height: 1.55;
      margin-bottom: 1.15rem;
    }}

    .section-title {{
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-tertiary);
      margin-bottom: 0.45rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .triggers-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin-bottom: 0.95rem;
    }}
    .trigger-pill {{
      background: var(--pill-bg);
      border: 1px solid var(--border-subtle);
      color: var(--accent-primary);
      padding: 0.2rem 0.5rem;
      border-radius: var(--radius-xs);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      cursor: pointer;
      transition: background-color 0.15s, border-color 0.15s;
      user-select: none;
    }}
    .trigger-pill:hover {{
      background: var(--accent-primary-subtle);
      border-color: var(--accent-primary);
    }}

    /* Config Box (Refined 1px border, no thick side stripe §2.6 A.4) */
    .config-box {{
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      padding: 0.75rem 0.85rem;
      border-radius: var(--radius-sm);
      font-size: 0.8rem;
      margin-bottom: 0.9rem;
    }}
    .config-file-name {{
      font-family: var(--font-mono);
      font-weight: 600;
      color: var(--text-primary);
      display: block;
      margin-bottom: 0.2rem;
    }}
    .config-desc {{
      color: var(--text-secondary);
      font-size: 0.77rem;
      line-height: 1.45;
    }}

    /* JSON Drawer */
    .json-accordion {{
      margin: 0.5rem 0 0.9rem;
    }}
    .btn-toggle-json {{
      background: transparent;
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 0.74rem;
      font-weight: 600;
      padding: 0.32rem 0.65rem;
      border-radius: var(--radius-xs);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: color 0.15s, border-color 0.15s;
    }}
    .btn-toggle-json:hover {{
      color: var(--accent-primary);
      border-color: var(--accent-primary-border);
    }}
    .json-code-drawer {{
      display: none;
      margin-top: 0.5rem;
      background: var(--code-block-bg);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 0.75rem;
      position: relative;
    }}
    .json-code-drawer.open {{
      display: block;
    }}
    .json-code-drawer pre {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--text-secondary);
      overflow-x: auto;
      max-height: 220px;
    }}
    .btn-copy-code {{
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 0.7rem;
      padding: 0.18rem 0.45rem;
      border-radius: var(--radius-xs);
      cursor: pointer;
    }}
    .btn-copy-code:hover {{
      color: var(--text-primary);
      border-color: var(--border-strong);
    }}

    .negative-box {{
      background: var(--status-danger-subtle);
      border: 1px solid var(--status-danger-border);
      border-radius: var(--radius-sm);
      padding: 0.55rem 0.75rem;
      font-size: 0.77rem;
      color: var(--status-danger);
      margin-bottom: 0.9rem;
    }}

    .card-footer {{
      border-top: 1px solid var(--border-subtle);
      padding-top: 0.95rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .btn-action {{
      background: var(--pill-bg);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      padding: 0.42rem 0.8rem;
      border-radius: var(--radius-xs);
      font-size: 0.78rem;
      font-weight: 600;
      font-family: var(--font-sans);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: border-color 0.15s, background-color 0.15s;
    }}
    .btn-action:hover {{
      border-color: var(--accent-primary);
      background: var(--bg-surface-hover);
    }}
    .btn-action-slash {{
      background: var(--accent-slash-subtle);
      border: 1px solid var(--accent-slash-border);
      color: var(--accent-slash);
      padding: 0.42rem 0.8rem;
      border-radius: var(--radius-xs);
      font-size: 0.78rem;
      font-weight: 600;
      font-family: var(--font-mono);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: background-color 0.15s, color 0.15s;
    }}
    .btn-action-slash:hover {{
      background: var(--accent-slash);
      color: #ffffff;
    }}

    /* ==========================================================================
       SLASH COMMANDS VIEW
       ========================================================================== */
    .slash-grid {{
      display: none;
      grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
      gap: 1.25rem;
    }}

    .slash-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1.35rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: border-color 0.15s, box-shadow 0.15s;
      position: relative;
    }}
    .slash-card:hover {{
      border-color: var(--accent-slash-border);
      box-shadow: var(--shadow-sm);
    }}

    .slash-header-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }}
    .slash-command-title {{
      font-family: var(--font-mono);
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--accent-slash);
      display: flex;
      align-items: center;
      gap: 0.4rem;
      letter-spacing: -0.02em;
    }}
    .slash-name {{
      font-size: 0.98rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 0.65rem;
    }}

    .ensemble-chain {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.35rem;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      padding: 0.45rem 0.75rem;
      border-radius: var(--radius-xs);
      margin-bottom: 0.85rem;
    }}
    .chain-label {{
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-tertiary);
      margin-right: 0.25rem;
    }}
    .chain-pill {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 600;
      background: var(--bg-canvas);
      border: 1px solid var(--border-subtle);
      color: var(--accent-primary);
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-xs);
    }}
    .chain-arrow {{
      color: var(--text-tertiary);
    }}

    .slash-goal-box {{
      background: var(--accent-slash-subtle);
      border: 1px solid var(--accent-slash-border);
      padding: 0.65rem 0.85rem;
      border-radius: var(--radius-sm);
      margin-bottom: 0.85rem;
    }}
    .slash-goal-title {{
      font-weight: 600;
      font-size: 0.84rem;
      color: var(--accent-slash);
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .slash-protocol-steps {{
      font-size: 0.78rem;
      color: var(--text-secondary);
      line-height: 1.5;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      padding: 0.65rem 0.85rem;
      border-radius: var(--radius-sm);
      margin-bottom: 0.95rem;
      font-family: var(--font-mono);
    }}

    /* ==========================================================================
       TABLE VIEW (Operate Mode: Compact Tabular)
       ========================================================================== */
    .skills-table-wrapper {{
      display: none;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      overflow-x: auto;
      margin-bottom: 2rem;
    }}
    .skills-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.84rem;
      font-variant-numeric: tabular-nums;
    }}
    .skills-table th {{
      background: var(--bg-surface-elevated);
      padding: 0.85rem 1rem;
      font-weight: 700;
      color: var(--text-secondary);
      border-bottom: 1px solid var(--border-subtle);
      text-transform: uppercase;
      font-size: 0.72rem;
      letter-spacing: 0.05em;
    }}
    .skills-table td {{
      padding: 0.95rem 1rem;
      border-bottom: 1px solid var(--border-subtle);
      vertical-align: top;
    }}
    .skills-table tr:hover td {{
      background: var(--bg-surface-hover);
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
      color: var(--text-primary);
    }}
    .table-triggers {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem;
    }}

    /* Empty state */
    .no-results {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 4.5rem 1.5rem;
      background: var(--bg-surface);
      border: 1px dashed var(--border-subtle);
      border-radius: var(--radius-md);
    }}
    .no-results h3 {{
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 0.4rem;
    }}
    .no-results p {{
      color: var(--text-secondary);
      font-size: 0.88rem;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-strong);
      color: var(--text-primary);
      padding: 0.65rem 1.15rem;
      border-radius: var(--radius-sm);
      font-size: 0.82rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      box-shadow: var(--shadow-lg);
      transform: translateY(120%);
      opacity: 0;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s;
      z-index: 9999;
    }}
    .toast.show {{
      transform: translateY(0);
      opacity: 1;
    }}
    .toast .toast-icon {{
      color: var(--status-success);
    }}

    @media (max-width: 900px) {{
      .skills-grid, .slash-grid {{
        grid-template-columns: 1fr;
      }}
      .header-content {{
        flex-direction: column;
        align-items: flex-start;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Sticky Navigation Bar -->
  <header>
    <div class="header-content">
      <div class="brand-area">
        <h1>
          <svg class="svg-icon svg-icon-lg" style="color:var(--accent-primary)" viewBox="0 0 24 24"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
          Goku Dev Skills Kataloğu
        </h1>
        <span class="version-tag">v{pkg_version}</span>
      </div>

      <!-- Primary View Switcher -->
      <div class="view-mode-tabs" role="tablist">
        <button class="tab-btn active" id="tabSkills" onclick="switchView('skills')" role="tab">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          Beceriler <span class="tab-badge">{len(skills)}</span>
        </button>
        <button class="tab-btn" id="tabSlash" onclick="switchView('slash')" role="tab">
          <svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          Slash Komutları <span class="tab-badge">{len(SLASH_COMMANDS)}</span>
        </button>
        <button class="tab-btn" id="tabTable" onclick="switchView('table')" role="tab">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M3 9h18"></path><path d="M3 15h18"></path><path d="M9 3v18"></path></svg>
          Takip Tablosu
        </button>
      </div>

      <!-- Theme Switcher -->
      <button class="theme-toggle-btn" id="themeToggleBtn" onclick="toggleTheme()" title="Temayı Değiştir (Kısayol: T)">
        <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
        <span id="themeToggleLabel">Açık Tema</span>
      </button>
    </div>
  </header>

  <div class="container">

    <!-- Hero / Header Strip -->
    <div class="hero-strip">
      <div>
        <p class="hero-desc">
          Çoklu ajan ekosisteminde çalışan tüm yapay zeka becerileri, kuralları, konfigürasyon gereksinimleri ve
          çoklu skill zincirleyen oturum slash komutları (Ensemble Protocols) için canlı referans kataloğu.
        </p>
        <div class="hero-command-box" onclick="copyToClipboard('npx goku-dev-skills update', 'Güncelleme komutu kopyalandı!')" title="Kopyalamak için tıkla">
          <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
          <span>Güncelleme:</span>
          <span class="cmd-text">npx goku-dev-skills update</span>
          <svg class="svg-icon" style="color:var(--text-tertiary)" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
        </div>
      </div>
      <div class="stat-badge-group">
        <div class="stat-pill">Beceriler: <span class="num">{len(skills)}</span></div>
        <div class="stat-pill slash-pill">Slash Komutları: <span class="num">{len(SLASH_COMMANDS)}</span></div>
        <div class="stat-pill">Kategoriler: <span class="num">{len(CATEGORIES)}</span></div>
      </div>
    </div>

    <!-- Quick Slash Command Ribbon -->
    <div class="quick-slash-ribbon">
      <div class="quick-ribbon-title">
        <svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
        Oturum Slash Komutları:
      </div>
      {quick_slash_pills}
    </div>

    <!-- Toolbar: Search & Filter Hub -->
    <div class="toolbar">
      <div class="search-row">
        <div class="search-box">
          <svg class="svg-icon search-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" class="search-input" id="searchInput" placeholder="Skill adı, tetikleyici, slash komutu, kategori veya açıklama ara... (Kısayol: / veya Ctrl+K)" oninput="filterAll()">
          <button class="btn-clear-search" id="btnClearSearch" onclick="clearSearch()" title="Aramayı Temizle">✕</button>
          <span class="kbd-shortcut">Ctrl+K</span>
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-group">
          <span class="filter-label">Kategori:</span>
          <button class="chip active" onclick="setCategoryFilter('all', this)">Tümü <span class="chip-count">({len(skills)})</span></button>
          {cat_buttons}
        </div>

        <div class="filter-group">
          <span class="filter-label">Konfigürasyon:</span>
          <button class="chip active" onclick="setConfigFilter('all', this)">Tümü</button>
          <button class="chip" onclick="setConfigFilter('Sıfır-Ayar', this)">Sıfır-Ayar</button>
          <button class="chip" onclick="setConfigFilter('Opsiyonel Config', this)">Opsiyonel</button>
          <button class="chip" onclick="setConfigFilter('Proje Dosyası', this)">Proje Dosyası</button>
        </div>
      </div>

      <div class="filter-summary" id="filterSummary">
        <span>Tüm skill\'ler listeleniyor ({len(skills)} beceri)</span>
      </div>
    </div>

    <!-- VIEW 1: SKILLS GRID -->
    <div id="viewSkillsSection">
      <div class="view-section-header">
        <h2 class="view-section-title">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          Ajan Becerileri & Mimari Kurallar
        </h2>
      </div>
      <div class="skills-grid" id="skillsGrid"></div>
    </div>

    <!-- VIEW 2: SLASH COMMANDS GRID -->
    <div id="viewSlashSection" style="display:none;">
      <div class="view-section-header">
        <h2 class="view-section-title" style="color:var(--accent-slash);">
          <svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          Oturum Slash Komutları (Ensemble Protocols)
        </h2>
      </div>
      <div class="slash-grid" id="slashGrid" style="display:grid;"></div>
    </div>

    <!-- VIEW 3: COMPACT TABLE -->
    <div id="viewTableSection" style="display:none;">
      <div class="view-section-header">
        <h2 class="view-section-title">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M3 9h18"></path><path d="M3 15h18"></path><path d="M9 3v18"></path></svg>
          Kompakt Takip Tablosu (Beceriler)
        </h2>
      </div>
      <div class="skills-table-wrapper" style="display:block;">
        <table class="skills-table">
          <thead>
            <tr>
              <th style="width: 48px;">#</th>
              <th style="width: 220px;">Beceri & Kategori</th>
              <th>Amaç & Kapsam</th>
              <th style="width: 280px;">Öne Çıkan Tetikleyiciler</th>
              <th style="width: 170px;">Konfigürasyon</th>
              <th style="width: 130px; text-align: right;">İşlem</th>
            </tr>
          </thead>
          <tbody id="skillsTableBody"></tbody>
        </table>
      </div>

      <div class="view-section-header" style="margin-top:2.5rem;">
        <h2 class="view-section-title" style="color:var(--accent-slash);">
          <svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          Oturum Slash Komutları Tablosu
        </h2>
      </div>
      <div class="skills-table-wrapper" style="display:block;">
        <table class="skills-table">
          <thead>
            <tr>
              <th style="width: 180px;">Komut</th>
              <th style="width: 220px;">Protokol Adı & Rozet</th>
              <th>Hedef & Görev Özeti</th>
              <th style="width: 320px;">Ensemble Zinciri (Beceriler)</th>
              <th style="width: 160px; text-align: right;">İşlem</th>
            </tr>
          </thead>
          <tbody id="slashTableBody"></tbody>
        </table>
      </div>
    </div>

  </div>

  <!-- Toast Notification -->
  <div class="toast" id="toast">
    <svg class="svg-icon toast-icon" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
    <span id="toastMsg">Panoya kopyalandı!</span>
  </div>

  <script>
    const allSkills = {skills_json};
    const allSlashCommands = {slash_commands_json};
    let currentCategory = 'all';
    let currentConfig = 'all';
    let currentSearch = '';
    let activeView = localStorage.getItem('agent_catalog_view') || 'skills';

    const categoryBadgeClassMap = {{
      'Tasarım & UI': 'cat-design',
      'Kod & Mimari': 'cat-code',
      'Teslimat & Kalite': 'cat-delivery',
      'Marka & Doküman': 'cat-brand',
      'Oturum Komutları (Ensemble)': 'cat-ensemble'
    }};

    // SVG icon constants for JS rendering
    const SVG_COPY = '<svg class="svg-icon" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
    const SVG_TERMINAL = '<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>';
    const SVG_SLASH = '<svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>';
    const SVG_SETTINGS = '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>';
    const SVG_SPARKLES = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path></svg>';
    const SVG_TARGET = '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>';
    const SVG_ALERT = '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
    const SVG_SUN = '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    const SVG_MOON = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';

    function switchView(view) {{
      activeView = view;
      localStorage.setItem('agent_catalog_view', view);

      document.getElementById('tabSkills').classList.toggle('active', view === 'skills');
      document.getElementById('tabSlash').classList.toggle('active', view === 'slash');
      document.getElementById('tabSlash').classList.toggle('slash-active', view === 'slash');
      document.getElementById('tabTable').classList.toggle('active', view === 'table');

      document.getElementById('viewSkillsSection').style.display = view === 'skills' ? 'block' : 'none';
      document.getElementById('viewSlashSection').style.display = view === 'slash' ? 'block' : 'none';
      document.getElementById('viewTableSection').style.display = view === 'table' ? 'block' : 'none';

      renderAll();
    }}

    function quickSelectSlash(cmdName) {{
      switchView('slash');
      const searchInput = document.getElementById('searchInput');
      searchInput.value = cmdName;
      currentSearch = cmdName;
      renderAll();
      copyToClipboard(cmdName, `Slash komutu kopyalandı: ${{cmdName}}`);
    }}

    function renderAll() {{
      const query = currentSearch.toLowerCase().trim();

      // Filter skills
      const filteredSkills = allSkills.filter(s => {{
        const matchCategory = (currentCategory === 'all' || s.category === currentCategory);
        const matchConfig = (currentConfig === 'all' || s.config_status.includes(currentConfig));
        const matchSearch = !query || s.search_index.includes(query);
        return matchCategory && matchConfig && matchSearch;
      }});

      // Filter slash commands
      const filteredSlash = allSlashCommands.filter(c => {{
        const matchCategory = (currentCategory === 'all' || c.category === currentCategory);
        const matchSearch = !query || 
          c.command.toLowerCase().includes(query) || 
          c.name.toLowerCase().includes(query) || 
          c.goal.toLowerCase().includes(query) || 
          c.description.toLowerCase().includes(query) ||
          c.skills.some(sk => sk.toLowerCase().includes(query)) ||
          c.aliases.some(a => a.toLowerCase().includes(query));
        return matchCategory && matchSearch;
      }});

      // Update Filter Summary
      const summary = document.getElementById('filterSummary');
      if (activeView === 'skills') {{
        summary.innerHTML = filteredSkills.length === allSkills.length
          ? `<span>Tüm skill\'ler listeleniyor (${{allSkills.length}} beceri)</span>`
          : `<span><strong>${{filteredSkills.length}}</strong> / ${{allSkills.length}} skill filtrelendi</span>
             <button class="btn-reset-filters" onclick="resetFilters()">Filtreleri Sıfırla</button>`;
      }} else if (activeView === 'slash') {{
        summary.innerHTML = filteredSlash.length === allSlashCommands.length
          ? `<span>Tüm oturum slash komutları listeleniyor (${{allSlashCommands.length}} komut)</span>`
          : `<span><strong>${{filteredSlash.length}}</strong> / ${{allSlashCommands.length}} slash komutu filtrelendi</span>
             <button class="btn-reset-filters" onclick="resetFilters()">Filtreleri Sıfırla</button>`;
      }} else {{
        summary.innerHTML = `<span>Takip tablosu: ${{filteredSkills.length}} skill ve ${{filteredSlash.length}} slash komutu listeleniyor</span>`;
      }}

      // Clear search button visibility
      const clearBtn = document.getElementById('btnClearSearch');
      clearBtn.style.display = currentSearch ? 'block' : 'none';

      renderSkillCards(filteredSkills);
      renderSlashCards(filteredSlash);
      renderTable(filteredSkills, filteredSlash);
    }}

    function copySkillPromptByName(name) {{
      const s = allSkills.find(item => item.name === name);
      if (s) copyToClipboard(s.sample_prompt, 'Örnek prompt panoya kopyalandı: ' + s.name);
    }}

    function copySkillCliByName(name) {{
      const s = allSkills.find(item => item.name === name);
      if (s && s.cli_cmd) copyToClipboard(s.cli_cmd, 'CLI komutu kopyalandı: ' + s.name);
    }}

    function copySkillConfigByName(name) {{
      const s = allSkills.find(item => item.name === name);
      if (s && s.config_snippet) copyToClipboard(s.config_snippet, 'Config şablonu kopyalandı: ' + s.name);
    }}

    function copySlashCommand(cmdName) {{
      copyToClipboard(cmdName, 'Slash komutu kopyalandı: ' + cmdName);
    }}

    function copySlashPromptByName(cmdName) {{
      const c = allSlashCommands.find(item => item.command === cmdName);
      if (c) copyToClipboard(c.sample_prompt, 'Örnek prompt kopyalandı: ' + c.command);
    }}

    function copyTriggerFromEl(el) {{
      const t = el.getAttribute('data-trigger') || el.innerText.replace(/^"|"$/g, '');
      copyToClipboard(t, 'Tetikleyici kopyalandı: "' + t + '"');
    }}

    function renderSkillCards(filtered) {{
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
          `<span class="trigger-pill" data-trigger="${{escapeHtml(t)}}" title="Kopyalamak için tıkla" onclick="copyTriggerFromEl(this)">"${{escapeHtml(t)}}"</span>`
        ).join('');

        const featuresHtml = (s.features || []).map(f => 
          `<span class="feature-tag">${{SVG_SPARKLES}} ${{escapeHtml(f)}}</span>`
        ).join('');

        const jsonSnippetHtml = s.config_snippet ? `
          <div class="json-accordion">
            <button class="btn-toggle-json" onclick="toggleJsonDrawer('json-${{idx}}')">
              ${{SVG_SETTINGS}} <span>Config / JSON Şablonu</span>
            </button>
            <div class="json-code-drawer" id="json-${{idx}}">
              <button class="btn-copy-code" onclick="copySkillConfigByName('${{escapeHtml(s.name)}}')">Kopyala</button>
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
              <span class="cat-badge ${{catClass}}">${{escapeHtml(s.category)}}</span>
            </div>

            <div class="card-header">
              <div class="skill-name">${{escapeHtml(s.name)}}</div>
              <span class="badge ${{s.badge_class}}">${{escapeHtml(s.config_status)}}</span>
            </div>

            ${{featuresHtml ? `<div class="features-row">${{featuresHtml}}</div>` : ''}}
            
            <p class="skill-purpose">${{escapeHtml(s.purpose)}}</p>

            <div class="section-title">${{SVG_SLASH}} Tetikleyiciler (Triggers)</div>
            <div class="triggers-list">${{triggersHtml || '<span style="color:var(--text-tertiary);font-size:0.75rem">Genel yönlendirici veya davranışsal</span>'}}</div>

            <div class="section-title">${{SVG_SETTINGS}} Konfigürasyon</div>
            <div class="config-box">
              <span class="config-file-name">${{escapeHtml(s.config_file)}}</span>
              <span class="config-desc">${{escapeHtml(s.config_detail)}}</span>
            </div>

            ${{jsonSnippetHtml}}

            ${{s.negative ? `
              <div class="section-title">${{SVG_ALERT}} Kapsam Sınırı (Tetiklenmez)</div>
              <div class="negative-box">${{escapeHtml(s.negative)}}</div>
            ` : ''}}
          </div>

          <div class="card-footer">
            <button class="btn-action" onclick="copySkillPromptByName('${{escapeHtml(s.name)}}')">
              ${{SVG_COPY}} Örnek Prompt
            </button>
            ${{s.cli_cmd ? `
              <button class="btn-action" onclick="copySkillCliByName('${{escapeHtml(s.name)}}')">
                ${{SVG_TERMINAL}} CLI Komutu
              </button>
            ` : ''}}
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function renderSlashCards(filtered) {{
      const grid = document.getElementById('slashGrid');
      grid.innerHTML = '';

      if (filtered.length === 0) {{
        grid.innerHTML = `
          <div class="no-results">
            <h3>Sonuç Bulunamadı</h3>
            <p>Arama kriterlerine uygun oturum slash komutu bulunamadı.</p>
            <button class="btn-action" style="margin-top:1rem" onclick="resetFilters()">Filtreleri Sıfırla</button>
          </div>
        `;
        return;
      }}

      filtered.forEach((cmd) => {{
        const card = document.createElement('div');
        card.className = 'slash-card';

        const skillsChainHtml = cmd.skills.map((sk, sIdx) => 
          `<span class="chain-pill">${{escapeHtml(sk)}}</span>` + 
          (sIdx < cmd.skills.length - 1 ? `<span class="chain-arrow">→</span>` : '')
        ).join(' ');

        card.innerHTML = `
          <div class="card-top">
            <div class="slash-header-row">
              <span class="slash-command-title">${{SVG_SLASH}} ${{escapeHtml(cmd.command)}}</span>
              <span class="badge ${{cmd.badge_class}}">${{escapeHtml(cmd.badge)}}</span>
            </div>

            <div class="slash-name">${{escapeHtml(cmd.name)}}</div>

            <div class="ensemble-chain">
              <span class="chain-label">Zincir:</span>
              ${{skillsChainHtml}}
            </div>

            <div class="slash-goal-box">
              <div class="slash-goal-title">${{SVG_TARGET}} ${{escapeHtml(cmd.goal)}}</div>
            </div>

            <p class="skill-purpose" style="margin-bottom:0.75rem;">${{escapeHtml(cmd.description)}}</p>

            <div class="section-title">${{SVG_TERMINAL}} Protokol Akışı</div>
            <div class="slash-protocol-steps">${{escapeHtml(cmd.protocol)}}</div>
          </div>

          <div class="card-footer">
            <button class="btn-action-slash" onclick="copySlashCommand('${{escapeHtml(cmd.command)}}')">
              ${{SVG_SLASH}} ${{cmd.command}}
            </button>
            <button class="btn-action" onclick="copySlashPromptByName('${{escapeHtml(cmd.command)}}')">
              ${{SVG_COPY}} Örnek Prompt
            </button>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function renderTable(filteredSkills, filteredSlash) {{
      const tbody = document.getElementById('skillsTableBody');
      tbody.innerHTML = '';

      if (filteredSkills.length === 0) {{
        tbody.innerHTML = `
          <tr>
            <td colspan="6" style="text-align: center; padding: 4rem 1rem; color: var(--text-secondary);">
              Filtrelere uygun skill bulunamadı.
            </td>
          </tr>
        `;
      }} else {{
        filteredSkills.forEach((s, idx) => {{
          const tr = document.createElement('tr');
          tr.setAttribute('data-name', s.name);

          const triggersHtml = s.triggers.slice(0, 5).map(t => 
            `<span class="trigger-pill" style="font-size:0.7rem;" data-trigger="${{escapeHtml(t)}}" title="Kopyalamak için tıkla" onclick="copyTriggerFromEl(this)">"${{escapeHtml(t)}}"</span>`
          ).join('') + (s.triggers.length > 5 ? `<span style="font-size:0.7rem;color:var(--text-tertiary);">+${{s.triggers.length - 5}}</span>` : '');

          const catClass = categoryBadgeClassMap[s.category] || 'cat-design';
          const numPadded = String(idx + 1).padStart(2, '0');

          tr.innerHTML = `
            <td style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-tertiary);font-weight:600;">#${{numPadded}}</td>
            <td>
              <div class="table-skill-cell">
                <span class="table-skill-name">${{escapeHtml(s.name)}}</span>
                <span class="cat-badge ${{catClass}}" style="display:inline-block;width:max-content;font-size:0.65rem;padding:0.1rem 0.45rem;">${{escapeHtml(s.category)}}</span>
              </div>
            </td>
            <td>
              <div style="font-size:0.85rem;color:var(--text-primary);line-height:1.45;margin-bottom:0.35rem;">${{escapeHtml(s.purpose)}}</div>
              ${{s.features && s.features.length ? `<div class="features-row" style="margin:0;">${{s.features.slice(0, 3).map(f => `<span class="feature-tag" style="font-size:0.65rem;">${{SVG_SPARKLES}} ${{escapeHtml(f)}}</span>`).join('')}}</div>` : ''}}
            </td>
            <td>
              <div class="table-triggers">${{triggersHtml || '<span style="color:var(--text-tertiary);font-size:0.75rem;">Genel yönlendirici</span>'}}</div>
            </td>
            <td>
              <span class="badge ${{s.badge_class}}" style="font-size:0.7rem;">${{escapeHtml(s.config_status)}}</span>
              <div style="font-family:var(--font-mono);font-size:0.72rem;color:var(--text-tertiary);margin-top:0.3rem;">${{escapeHtml(s.config_file)}}</div>
            </td>
            <td style="text-align: right;">
              <button class="btn-action" style="padding:0.3rem 0.6rem;font-size:0.74rem;" onclick="copySkillPromptByName('${{escapeHtml(s.name)}}')">
                ${{SVG_COPY}} Kopyala
              </button>
            </td>
          `;
          tbody.appendChild(tr);
        }});
      }}

      // Render Slash Commands in Table
      const slashTbody = document.getElementById('slashTableBody');
      if (slashTbody) {{
        slashTbody.innerHTML = '';
        if (filteredSlash.length === 0) {{
          slashTbody.innerHTML = `
            <tr>
              <td colspan="5" style="text-align: center; padding: 2rem 1rem; color: var(--text-secondary);">
                Filtrelere uygun slash komutu bulunamadı.
              </td>
            </tr>
          `;
        }} else {{
          filteredSlash.forEach((cmd) => {{
            const tr = document.createElement('tr');
            const skillsChainHtml = cmd.skills.map((sk, sIdx) => 
              `<span class="chain-pill" style="font-size:0.68rem;">${{escapeHtml(sk)}}</span>` + 
              (sIdx < cmd.skills.length - 1 ? `<span class="chain-arrow">→</span>` : '')
            ).join(' ');

            tr.innerHTML = `
              <td>
                <span class="slash-command-title" style="font-size:0.95rem;cursor:pointer;" onclick="copySlashCommand('${{escapeHtml(cmd.command)}}')">
                  ${{SVG_SLASH}} ${{escapeHtml(cmd.command)}}
                </span>
              </td>
              <td>
                <div style="font-weight:700;font-size:0.85rem;margin-bottom:0.25rem;">${{escapeHtml(cmd.name)}}</div>
                <span class="badge ${{cmd.badge_class}}" style="font-size:0.68rem;">${{escapeHtml(cmd.badge)}}</span>
              </td>
              <td>
                <div style="font-size:0.82rem;font-weight:600;color:var(--accent-slash);margin-bottom:0.2rem;display:flex;align-items:center;gap:0.3rem;">
                  ${{SVG_TARGET}} ${{escapeHtml(cmd.goal)}}
                </div>
                <div style="font-size:0.78rem;color:var(--text-secondary);">${{escapeHtml(cmd.description)}}</div>
              </td>
              <td>
                <div style="display:flex;flex-wrap:wrap;gap:0.25rem;align-items:center;">
                  ${{skillsChainHtml}}
                </div>
              </td>
              <td style="text-align: right;">
                <button class="btn-action-slash" style="padding:0.3rem 0.6rem;font-size:0.74rem;" onclick="copySlashCommand('${{escapeHtml(cmd.command)}}')">
                  ${{SVG_SLASH}} Kopyala
                </button>
              </td>
            `;
            slashTbody.appendChild(tr);
          }});
        }}
      }}
    }}

function filterAll() {{
      currentSearch = document.getElementById('searchInput').value;
      if (currentSearch.trim().startsWith('/') && activeView === 'skills') {{
        switchView('slash');
      }}
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
      const html = document.documentElement;
      const isDark = html.getAttribute('data-theme') === 'dark';
      const newTheme = isDark ? 'light' : 'dark';
      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('agent_catalog_theme', newTheme);
      updateThemeButton(newTheme);
    }}

    function updateThemeButton(theme) {{
      const btn = document.getElementById('themeToggleBtn');
      if (btn) {{
        if (theme === 'light') {{
          btn.innerHTML = `${{SVG_MOON}} <span id="themeToggleLabel">Koyu Tema</span>`;
        }} else {{
          btn.innerHTML = `${{SVG_SUN}} <span id="themeToggleLabel">Açık Tema</span>`;
        }}
      }}
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
      if (e.key === '1' && document.activeElement.tagName !== 'INPUT') {{
        switchView('skills');
      }}
      if (e.key === '2' && document.activeElement.tagName !== 'INPUT') {{
        switchView('slash');
      }}
      if (e.key === '3' && document.activeElement.tagName !== 'INPUT') {{
        switchView('table');
      }}
    }});

    // Initialize Theme & View
    const savedTheme = localStorage.getItem('agent_catalog_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);

    switchView(activeView);
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
        print(f"[OK] {OUTPUT_HTML} güncel ({len(skills)} skill, {len(SLASH_COMMANDS)} slash komutu).")
        return 0

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html_content, encoding="utf-8")
    print(f"Katalog başarıyla derlendi ({len(skills)} skill, {len(SLASH_COMMANDS)} slash komutu): {OUTPUT_HTML}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
