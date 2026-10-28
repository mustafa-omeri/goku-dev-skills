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
        "command": "/ui-polish",
        "aliases": ["/ui-polish", "[UI-POLISH]", "[DESIGN-REFRESH]", "--redesign", "[OVERDRIVE]"],
        "name": "DESIGN.md Sözleşme & 11-Beceri Zanaat Orkestratörü",
        "badge": "Tasarım & Sözleşme",
        "badge_class": "badge-accent",
        "skills": [
            "canvas-design", "design-system", "ui-ux-pro-max", "frontend-design",
            "ui-styling", "banner-design", "brand", "theme-factory",
            "mock-asset-provider", "onboarding-tour", "i18n-localization"
        ],
        "goal": "4 Modlu DESIGN.md Sözleşmesi (Baseline / Crafted / Refinement / Redesign) & 3 Mekanik Kapı",
        "description": "Mevcut projelerde görsel tasarımı değiştirmeden önce mevcut yapıyı belgeleyen <repo-kök>/DESIGN.md (mode: baseline) çıkarır; yalnızca kullanıcı --redesign veya [OVERDRIVE] ile zorladığında ya da sıfırdan tasarımda F2 aşamasında canvas-design + canvas-fonts ile 3 alternatif yön sunar, 3-katmanlı token sözleşmesi kurar ve 3 mekanik kapı (contract, slop, contrast) ile doğrular.",
        "sample_prompt": "/ui-polish: Projeyi analiz et, mevcut tasarım için görsele dokunmadan DESIGN.md (mode: baseline) sözleşmesini oluştur ve 3 mekanik tasarım kapısıyla doğrula.",
        "protocol": "F1 Keşif & Mod Tespiti (baseline | crafted | refinement | redesign) ➜ F2 3 Yön (canvas-design + Reddedilen Varsayılanlar) ➜ F3 DESIGN.md & 3-Katman Token (design-system) ➜ F4-F6 Uygulama ➜ F7 3 Kapı & 6-Görüntü Skor Kartı",
        "usage_snippet": """# 1. Mod 0 (Baseline - Mevcut Projede Görseli Değiştirmeden DESIGN.md Çıkarma):
/ui-polish @[src/index.css]

# 2. Mod B (Refinement - Mevcut DESIGN.md Sözleşmesine Sadık İnce İşçilik):
/ui-polish @[.agent/skills-catalog.html]

# 3. Mod C (Redesign - Kullanıcı Zorlamasıyla 3 Yönlü Yeniden Tasarım):
/ui-polish --redesign @[src/pages/Dashboard.tsx]
# veya: /ui-polish [OVERDRIVE] tasarımı yeniden tasarla

# 4. Üç Mekanik Tasarım Doğrulama Kapısı (0 Hata Zorunlu):
python .agent/skills/musgoku/scripts/check_design_contract.py --strict
python .agent/skills/musgoku/scripts/check_design_slop.py --strict
python .agent/skills/musgoku/scripts/check_theme_contrast.py --strict""",
        "category": "Tasarım & UI"
    },
    {
        "command": "/verify-last",
        "aliases": ["/verify-last", "verify last", "[VERIFY-LAST]"],
        "name": "Mikro: Son Geliştirmeler & Çalışma Ağacı Doğrulama",
        "badge": "Mikro Kalite",
        "badge_class": "badge-info",
        "skills": ["verify-last", "musgoku", "development-workflow"],
        "goal": "Uncommitted Çalışma Ağacı (git status) & Son Commit (HEAD~1..HEAD) Cerrahi Denetimi",
        "description": "Anlık oturumda en son yapılan değişiklikleri, git status / uncommitted çalışma ağacını veya en son commit'i (HEAD~1..HEAD) kapsam-duyarlı derleme, tip, birim testi ve etkilenen katman bütünlüğü açısından doğrular.",
        "sample_prompt": "/verify-last: Son yapılan geliştirmeleri, uncommitted dosyaları ve regresyon riskini cerrahi olarak denetle.",
        "protocol": "1. git status & diff Analizi ➜ 2. Kapsam-Duyarlı Kalite Kapıları (build/tsc/test) ➜ 3. Etkilenen Katman Denetimi ➜ 4. Hızlı Kullanıcı Test Adımı",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/verify-last
/verify-last son commit'i ve açık dosyaları doğrula

# Arkada Çalıştırılan Kapsam-Duyarlı Kontroller:
git status --short
git diff --stat
python .agent/skills/musgoku/scripts/rules_gates.py --strict
python .agent/skills/musgoku/scripts/check_project_brief.py""",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/verify-sprint",
        "aliases": ["/verify-sprint", "verify sprint", "[VERIFY-SPRINT]"],
        "name": "Mezo: Aktif & Son Sprint Hedefleri Kabul Denetimi",
        "badge": "Mezo Kalite",
        "badge_class": "badge-warning",
        "skills": ["verify-sprint", "sprint-delivery-workflow", "tdd"],
        "goal": "Gherkin AC, Kart Başına 5 Katmanlı Dilim & KULLANICI_TEST_REHBERI",
        "description": "Aktif sprinti (SPRINT_PLAN.md) ve tamamlanan sprint sınırındaki kartları (KANBAN.md) denetler; Gherkin senaryolarını, kart başına 5 katmanlı dikey dilimi ve kullanıcı test rehberini doğrular.",
        "sample_prompt": "/verify-sprint: Aktif sprint hedeflerini, kart kabul kriterlerini (Gherkin) ve 5 katman dikey dilim bütünlüğünü denetle.",
        "protocol": "1. SPRINT_PLAN.md & KANBAN.md Senkronu ➜ 2. Gherkin (.feature) AC Doğrulaması ➜ 3. Kart Başına 5 Katman Matrisi ➜ 4. KULLANICI_TEST_REHBERI.md Kanıtı",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/verify-sprint
/verify-sprint aktif sprint kartlarını ve Gherkin senaryolarını denetle

# Mekanik Sprint Panosu Kapısı:
python .agent/skills/musgoku/scripts/check_sprint_board.py""",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/verify-prd",
        "aliases": ["/verify-prd", "/prd-verify", "[VERIFY-PRD]"],
        "name": "Makro: PRD & Tüm Proje Kabul Kriterleri Doğrulama Motoru",
        "badge": "Makro Kalite & Güven",
        "badge_class": "badge-info",
        "skills": ["verify-prd", "doc-coauthoring", "code-review", "Katman Bütünlüğü (5-Layer)"],
        "goal": "\"Bitti ama doğru mu bitti?\" Sahte Bitti (Phantom Done) Avcısı",
        "description": "Tüm proje ve PRD genelinde şartnamedeki kabul kriterlerini (Gherkin AC), 5 Katmanlı Dikey Dilimi (DB Migration, View/RPC, Client API, UI UX, Admin Formu), unutulmuş mock/localStorage kalıntılarını ve kapsam sapmalarını (Scope Creep) denetleyip kanıt karnesi üretir.",
        "sample_prompt": "/verify-prd: Tüm projeyi PRD şartnamesine göre denetle; 5 katman dikey dilim bütünlüğünü ve sahte bitti (Phantom Done) risklerini raporla.",
        "protocol": "1. Gherkin AC & PRD Denetimi ➜ 2. 5 Katmanlı Dikey Dilim Analizi ➜ 3. Mock Kalıntısı & Scope Creep Taraması ➜ 4. Deterministik Test Kanıtı & Kabul Karnesi",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/verify-prd
/verify-prd tüm projeyi PRODUCT.md ve PRD hedeflerine göre denetle

# Denetlenen 5 Katmanlı Dikey Dilim:
# 1. DB/Şema/Migration (check_db_migrations.py)
# 2. Backend/View/RPC (check_api_docs.py)
# 3. İstemci API Entegrasyonu (Canlı View/Endpoint)
# 4. Arayüz/UX & Durumlar (check_design_contract.py)
# 5. Yönetim/Admin Formu & Döngü Kapanışı""",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/check-security",
        "aliases": ["/check-security", "[CHECK-SECURITY]"],
        "name": "Güvenlik, Savunma & İstismar Kalkanı",
        "badge": "Güvenlik & Savunma",
        "badge_class": "badge-danger",
        "skills": ["security-audit", "development-workflow", "prelaunch-audit"],
        "goal": "OWASP Zafiyet Avcılığı & Public Form 6-Katman Savunması",
        "description": "OWASP zafiyet avcılığı, public form kalkanı (Context Binding, Honeypot, Turnstile, Rate-limit, Sanitization, Blind Insert RLS) ve secrets/env sızıntı denetimi yürütür.",
        "sample_prompt": "/check-security: Sistem genelinde yetki aşımı, public form abuse riskleri ve env sızıntılarını derinlemesine tara.",
        "protocol": "1. Guidance/Full-Audit Zafiyet Taraması ➜ 2. Halka 2 Public Form Savunması (Turnstile, Rate-limit, RLS) ➜ 3. Secret/Env Sızıntı & Bulgular Doğrulaması",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/check-security
/check-security public formları ve RLS politikalarını denetle

# Bulgular ve Kapsam Defteri Doğrulayıcıları:
node .agent/skills/security-audit/scripts/validate-findings.cjs
node .agent/skills/security-audit/scripts/validate-coverage-ledger.cjs""",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/fix-bug",
        "aliases": ["/fix-bug", "[FIX-BUG]"],
        "name": "Sistematik Hata Teşhis & Kırmızı Döngü",
        "badge": "Hata Teşhisi",
        "badge_class": "badge-warning",
        "skills": ["diagnosing-bugs", "musgoku", "karpathy-guidelines"],
        "goal": "Önce Kırmızı Geri Bildirim Döngüsü & Cerrahi Onarım",
        "description": "Uygulama koduna dokunmadan önce hatayı deterministik olarak kanıtlayan kırmızı test/kanıt döngüsü kurar, 3 hipotez üretip sınar, cerrahi onarım yapar ve Karpathy gereksiz kod temizliği işletir.",
        "sample_prompt": "/fix-bug: Çöken endpoint için önce kırmızı geri bildirim döngüsü kur, 3 hipotez üret ve cerrahi düzeltme yap.",
        "protocol": "1. Kırmızı Döngü (diagnosing-bugs) ➜ 2. Hipotez & İzolasyon ➜ 3. Cerrahi Onarım (musgoku) ➜ 4. Regresyon Testi & Sadeleştirme (karpathy-guidelines)",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/fix-bug <hata açıklaması veya log>

# Zorunlu 6 Aşama (bug-diagnosis-enforcement.md):
# Faz 1: Kırmızı Geri Bildirim Döngüsü (Hata kanıtlanmadan kod değişmez)
# Faz 2: 3 Somut Hipotez Üretimi
# Faz 3: En Küçük Deney ile Hipotez Eleme
# Faz 4: Kök Neden Onarımı (Semptom gizleme yasak)
# Faz 5: Regresyon Testi (Kırmızı -> Yeşil)
# Faz 6: knowledge-base.md Kaydı""",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/council",
        "aliases": ["/council", "[COUNCIL]", "llm council"],
        "name": "3-Aşamalı LLM Konsey Hakemliği",
        "badge": "Mimari Hakemlik",
        "badge_class": "badge-info",
        "skills": ["karpathy-guidelines", "doc-coauthoring", "domain-modeling"],
        "goal": "Anonim Kör Akran İncelemesi (Borda Skoru) & ADR Kararı",
        "description": "2+ alternatifli mimari ikilem ve riskli refactoring kararlarında 3 aşamalı anonim körleme (Stage 1 Proposals → Stage 2 Blind Review & Borda Skoru → Stage 3 Chairman Synthesis) ve docs/adr/ altında mimari karar kaydı üretir.",
        "sample_prompt": "/council: Mimari ikilem için 3 alternatifli kör hakemlik konseyi topla, Borda puanı hesapla ve ADR kaydı çıkar.",
        "protocol": "Stage 1 (Option A/B/C Önerileri) ➜ Stage 2 (Kör Hakemlik & council_ranker.py) ➜ Stage 3 (Chairman Sentezi) ➜ docs/adr/ Karar Kaydı",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/council <mimari ikilem veya teknoloji seçimi>

# Borda Skoru ve Sıralama Hesaplayıcı CLI:
python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample""",
        "category": "Kod & Mimari"
    },
    {
        "command": "/prelaunch",
        "aliases": ["/prelaunch", "[PRELAUNCH]"],
        "name": "Canlıya Alma Kalite & Uyum Denetimi",
        "badge": "Lansman & Uyum",
        "badge_class": "badge-success",
        "skills": ["prelaunch-audit"],
        "goal": "20 Maddelik Lansman, KVKK/GDPR, Consent Mode v2 & WCAG 2.2 AA",
        "description": "20 maddelik çekirdek kontrol listesi + 7 koşullu madde (KVKK m.10, 7499 s. Kanun yurt dışı aktarımı, Google Consent Mode v2, ham HTML SEO, WCAG 2.2 AA Axe, robots.txt, sitemap.xml, llms.txt) ile GO/NO-GO karar raporu üretir.",
        "sample_prompt": "/prelaunch: Sitemizi yayına almaya hazır mıyız? 20 maddelik çekirdek denetimi ve yasal onay mekanizmalarını doğrula.",
        "protocol": "1. prelaunch_checker.py (Yerel Dosya/Tuzak) ➜ 2. html-audit.mjs (Ham HTML SEO) ➜ 3. consent-check.mjs (Çerez/İzleyici) ➜ 4. axe-runner.mjs (WCAG 2.2 AA) ➜ PRELAUNCH-REPORT.md",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/prelaunch

# Otomasyon Denetim Betikleri:
python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py --dir .
node .agent/skills/prelaunch-audit/scripts/html-audit.mjs https://example.com
node .agent/skills/prelaunch-audit/scripts/consent-check.mjs https://example.com
node .agent/skills/prelaunch-audit/scripts/axe-runner.mjs https://example.com""",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/prelaunch-update",
        "aliases": ["/prelaunch-update", "[PRELAUNCH-UPDATE]"],
        "name": "Mevzuat & Platform Kuralları Güncelleyici",
        "badge": "Mevzuat Senkronu",
        "badge_class": "badge-warning",
        "skills": ["prelaunch-audit"],
        "goal": "Dinamik Mevzuat, İdari Para Cezası ve Bot Kuralları Senkronu",
        "description": "KVKK yeniden değerleme oranı idari para cezaları, 7499 s. Kanun bildirim limitleri, Ticaret Bakanlığı 28/B kuralları ve Google Search / AI crawler değişikliklerini resmi kaynaklardan sorgulayıp referans dosyalarını cerrahi günceller.",
        "sample_prompt": "/prelaunch-update: Güncel KVKK ve GDPR idari para cezalarını resmi tebliğlerden sorgula ve dokümanları güncelle.",
        "protocol": "1. prelaunch_updater.py --check (Tazelik Kontrolü) ➜ 2. --generate-prompt (Resmi Kaynak Sorgusu) ➜ 3. Markdown Referanslarının Cerrahi Güncellenmesi",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/prelaunch-update

# Tazelik Denetimi ve Araştırma Promptu Üretimi:
python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --check
python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --generate-prompt""",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/seo-apply",
        "aliases": ["/seo-apply", "[SEO-APPLY]"],
        "name": "Uçtan Uca SEO & GEO (AI Search) Altyapısı",
        "badge": "SEO & Growth",
        "badge_class": "badge-accent",
        "skills": ["seo-growth", "frontend-design"],
        "goal": "Teknik SEO, JSON-LD Schema.org & AI Crawler (/llms.txt) Kurulumu",
        "description": "Kod tabanına bizzat girer; semantik meta başlık (50-60 kr), açıklama (120-155 kr), canonical, OpenGraph, JSON-LD Schema.org, AI crawler robots.txt, sitemap.xml ve /llms.txt dosyalarını üretip seo_checker.py --strict ile doğrular.",
        "sample_prompt": "/seo-apply: Sitemiz için JSON-LD şemaları, OpenGraph etiketleri, robots.txt ve llms.txt dosyalarını kur ve doğrula.",
        "protocol": "1. seo-growth (Strateji & Şema Seçimi) ➜ 2. frontend-design (Head/Meta & JSON-LD Enjeksiyonu) ➜ 3. robots.txt / sitemap.xml / llms.txt ➜ 4. seo_checker.py --strict",
        "usage_snippet": """# Sohbette Doğrudan Tetikleme:
/seo-apply

# Deterministik SEO & AI Crawler Doğrulama Kapısı:
python .agent/skills/seo-growth/scripts/seo_checker.py --strict""",
        "category": "Marka & Doküman"
    },
    {
        "command": "/commitx",
        "aliases": ["/commitx", "commitx", "commitle"],
        "name": "Peşin Yetkili Otonom Sürüm Yayını",
        "badge": "Sürüm & Git",
        "badge_class": "badge-success",
        "skills": ["git-release-workflow"],
        "goal": "Ara Onaysız Otomatik Kapı Doğrulaması, Commit, Semver Tag & Push",
        "description": "Kullanıcının peşin yetkisiyle kapsam-duyarlı doğrulama kapılarını çalıştırır; ara onay sormadan git add → git commit → semantik git tag (vX.Y.Z) → git push zincirini kesintisiz tamamlar.",
        "sample_prompt": "commitx: Değişiklikleri doğrula, semantik tag artır ve uzak depoya push et.",
        "protocol": "1. Kalite Kapıları & HANDOFF/KB Güncellemesi ➜ 2. Semver Tag Hesaplama ➜ 3. git add -A & git commit ➜ 4. git tag -a vX.Y.Z ➜ 5. git push origin HEAD & --tags",
        "usage_snippet": """# Sohbette Tek Kelimeyle Peşin Yetkili Yayın:
commitx
commitle
/commitx""",
        "category": "Teslimat & Kalite"
    },
    {
        "command": "/gs-update",
        "aliases": ["/gs-update", "GS güncelle", "skill update", "goku update"],
        "name": "Cerrahi Skill Seti Senkronu",
        "badge": "Bakım & Senkron",
        "badge_class": "badge-info",
        "skills": ["musgoku", "gs-update"],
        "goal": "Sıfır-Şişkinlik ve Proje Kuralı Korumalı Güncelleme",
        "description": "AGENTS.md içindeki '## Proje Bazlı Ek Kurallar' bloğunu koruyarak ve kurulu olmayan becerileri/temaları indirmeden mevcut ajan becerilerini en son sürüme cerrahi olarak senkronlar.",
        "sample_prompt": "/gs-update: Kurulu skill setini en son sürüme güncelle, proje ek kurallarını koru.",
        "protocol": "1. npx goku-dev-skills update --check (Önizleme) ➜ 2. Cerrahi Dosya Senkronu ➜ 3. Proje Bazlı Ek Kurallar Bloğu Geri Yazımı ➜ 4. rules_gates.py --strict Doğrulaması",
        "usage_snippet": """# 1. Disk Değişikliği Yapmadan Güncellemeleri Önizle:
npx goku-dev-skills update --check

# 2. Yalnızca Kurulu Skill ve Kuralları Cerrahi Güncelle:
npx goku-dev-skills update

# 3. GitHub Uzak Depodan Doğrudan Güncelle:
npx goku-dev-skills update --remote""",
        "category": "Kod & Mimari"
    }
]

CONFIG_METADATA = {
    "ui-polish": {
        "status": "Tasarım Sözleşmesi",
        "badge_class": "badge-accent",
        "file": "DESIGN.md (Proje Kökü) + 3 Mekanik Kapı",
        "features": [
            "Mod 0: Baseline (Görsele Dokunmaz)",
            "Mod A: Crafted (Sıfırdan 3 Yön)",
            "Mod B: Refinement (Mevcut DESIGN.md)",
            "Mod C: Redesign (--redesign / [OVERDRIVE])",
            "11 Tasarım Becerisi Orkestrasyonu",
            "3 Mekanik Kapı (Contract, Slop, Contrast)"
        ],
        "detail": "Mevcut projelerde görsel tasarımı değiştirmeden önce mevcut yapıyı belgeleyen <repo-kök>/DESIGN.md (mode: baseline) çıkarır. Yalnızca kullanıcı --redesign veya [OVERDRIVE] ile zorladığında ya da sıfırdan tasarımda F2 aşamasında canvas-design + canvas-fonts ile 3 alternatif yön sunar ve 3 mekanik kapıyla doğrular.",
        "sample_prompt": "/ui-polish: Projeyi analiz et, mevcut tasarım için görsele dokunmadan DESIGN.md (mode: baseline) sözleşmesini oluştur ve 3 mekanik tasarım kapısıyla doğrula.",
        "config_snippet": """# 1. Mod 0 (Baseline - Mevcut Tasarımı Değiştirmeden DESIGN.md Çıkarma):
/ui-polish

# 2. Mod C (Redesign - Kullanıcı Zorlamasıyla 3 Yönlü Yeniden Tasarım):
/ui-polish --redesign
/ui-polish [OVERDRIVE] tasarımı yeniden tasarla

# 3. Üç Mekanik Tasarım Doğrulama Kapısı:
python .agent/skills/musgoku/scripts/check_design_contract.py --strict
python .agent/skills/musgoku/scripts/check_design_slop.py --strict
python .agent/skills/musgoku/scripts/check_theme_contrast.py --strict"""
    },
    "frontend-design": {
        "status": "Tasarım & 55 Tema",
        "badge_class": "badge-accent",
        "file": "DESIGN.md + component-themes/ (55 Tema)",
        "features": [
            "55 Hazır Bileşen Teması (get_component.py)",
            "10 WCAG Renk Paleti (get_palette.py)",
            "CC0 Kültür Varlığı Aracı (assets.mjs)",
            "3 Dalga AI-Slop Koruması",
            "İki Satır Başlık & 2 Font Tavanı"
        ],
        "detail": "Üretim kalitesinde web arayüzü kodu üretir. Sıfırdan yazmadan önce 55 hazır HTML/CSS bileşen temasını (sidebars, navbars, cards, logins, footers) ve 10 ölçülmüş WCAG paletini CLI köprüleriyle tarar; DESIGN.md sözleşmesine tam sadık kalır.",
        "sample_prompt": "Arayüzü DESIGN.md sözleşmesine ve hazır bileşen temalarına göre modernleştir, AI-slop kalıplarını temizle.",
        "config_snippet": """# 1. 55 Hazır Bileşen Temasını Listele ve Kodunu Çek:
python .agent/skills/frontend-design/scripts/get_component.py --list
python .agent/skills/frontend-design/scripts/get_component.py --theme violet-minimal-sidebar --html

# 2. 10 Ölçülmüş WCAG Paletini Listele ve CSS Değişkeni Üret:
python .agent/skills/frontend-design/scripts/get_palette.py --list
python .agent/skills/frontend-design/scripts/get_palette.py --id 7 --format css

# 3. CC0 / Public Domain Kültür ve Sanat Görseli Ara:
node .agent/skills/frontend-design/scripts/assets.mjs --search "architectural blueprint" """
    },
    "ui-ux-pro-max": {
        "status": "Aranabilir Veritabanı",
        "badge_class": "badge-info",
        "file": "data/*.csv (79 Stil · 192 Palet · 74 Font · 119 UX)",
        "features": [
            "79 Tasarım Stili",
            "192 Sektörel Renk Paleti",
            "74 Google Font Eşleşmesi",
            "119 UX & Erişilebilirlik Kuralı",
            "40+ Kurumsal Design System İndeksi"
        ],
        "detail": "Aranabilir tasarım/UX referans motoru. --design-system bayrağı ile ürün tipine göre stil, palet, tipografi ve yerel hazır bileşen önerilerini tek sorguda üretir.",
        "sample_prompt": "Geliştirici aracı için uygun tasarım stilini, renk paletini, font eşleşmesini ve UX kurallarını incele.",
        "config_snippet": """# 1. Ürüne Özel Tam Tasarım Sistemi Tavsiyesi Üret:
python .agent/skills/ui-ux-pro-max/scripts/search.py "developer tools dark workstation" --design-system

# 2. Belirli Domain'de Arama Yap (style, color, typography, ux, icons, motion):
python .agent/skills/ui-ux-pro-max/scripts/search.py "sidebar navigation" --domain ux
python .agent/skills/ui-ux-pro-max/scripts/search.py "editorial serif" --domain typography"""
    },
    "canvas-design": {
        "status": "Estetik Yön & Font",
        "badge_class": "badge-accent",
        "file": "canvas-fonts/ (81 Font) + DESIGN.md §2",
        "features": [
            "Estetik Manifesto Üretimi",
            "81 Küratörlü Font (canvas-fonts/)",
            "/ui-polish F2 3 Yön Sentezi",
            "Ölçüsüz Görsel Sanat (.png / .pdf)"
        ],
        "detail": "Ölçüsüz görsel sanat (poster, afiş, manifesto) üretir ve /ui-polish F2 aşamasında projenin estetik yönünü (3 alternatif kreatif yön + Reddedilen Varsayılanlar) ve tipografi karakterini belirler.",
        "sample_prompt": "Proje için 3 farklı estetik manifesto yönü ve canvas-fonts/ kütüphanesinden karakterli başlık/gövde font eşleşmesi üret.",
        "config_snippet": """# 1. /ui-polish F2 Aşamasında Kreatif Yön & Font Seçimi:
# .agent/skills/canvas-design/canvas-fonts/ altındaki 81 font ailesinden
# Display + Sans + Mono eşleşmesi yapılır ve DESIGN.md §2'ye işlenir.

# 2. Müstakil Poster / Görsel Sanat Çıktısı:
# Önce yazılı estetik felsefe üretilir, ardından .png / .pdf kanvasa işlenir."""
    },
    "banner-design": {
        "status": "Sabit Ölçü & Safe-Zone",
        "badge_class": "badge-info",
        "file": "DESIGN.md §8 (OG 1200x630 · LinkedIn · X · Hero)",
        "features": [
            "22 Art-Direction Stili",
            "Platform Güvenli Alan (Safe-Zone) Kuralları",
            "OG 1200x630 & X 1500x500",
            "LinkedIn 1584x396 & Web Hero"
        ],
        "detail": "Sabit piksel ölçülü sosyal medya kapakları, OpenGraph paylaşım kartları, reklam görselleri ve web hero banner'ları için güvenli alan (safe-zone), tipografi ölçeği ve kompozisyon kurallarını yönetir.",
        "sample_prompt": "Web sitesi hero alanı ve OpenGraph (1200x630) paylaşım kartı için güvenli alan kurallarına uygun kapak tasarla.",
        "config_snippet": """# Standart Platform Ölçüleri (DESIGN.md §8):
# - OpenGraph / Twitter Card : 1200 x 630 px (Kenar güvenli payı: %10)
# - X (Twitter) Header       : 1500 x 500 px (Sol alt avatar alanı boş bırakılır)
# - LinkedIn Cover           : 1584 x 396 px
# - YouTube Channel Banner   : 2560 x 1440 px (Merkez güvenli alan: 1546 x 423 px)"""
    },
    "theme-factory": {
        "status": "10 Hazır Tema",
        "badge_class": "badge-success",
        "file": "theme-factory/SKILL.md (10 Küratörlü Tema)",
        "features": [
            "10 Küratörlü HEX Paleti",
            "Başlık & Gövde Font Eşleşmesi",
            "/ui-polish F2 Aday Yön Desteği",
            "Özel Tema Üretimi"
        ],
        "detail": "10 küratörlü renk ve font temasını (HEX paleti + başlık/gövde font çifti) sunar; /ui-polish F2 aşamasında aday yönlerin hızlı karşılaştırılmasında veya sunum/doküman temalandırmasında kullanılır.",
        "sample_prompt": "Uygulama için 10 hazır temadan en uygun 3 adayı karşılaştır ve seçilen paleti DESIGN.md token'larına dönüştür.",
        "config_snippet": """# /ui-polish F2 Aşamasında Kullanım:
# 1. theme-factory içinden ürüne uygun 1-2 aday palet seçilir.
# 2. Seçilen palet doğrudan kopyalanmaz; design-system ile OKLCH/HEX
#    primitive -> semantic -> component token katmanlarına dönüştürülür."""
    },
    "design": {
        "status": "Yönlendirici & Brief",
        "badge_class": "badge-info",
        "file": "Logo (55 Stil) & Kurumsal Kimlik (CIP) Brief",
        "features": [
            "12 Tasarım Becerisi Yönlendiricisi",
            "55 Logo Stili & 30 Palet Arama",
            "50+ Kurumsal Kimlik (CIP) Teslimatı",
            "HTML CIP Sunum Üreticisi"
        ],
        "detail": "Çoklu tasarım alanına giren taleplerde doğru tasarım becerisini seçer; ayrıca çevrimdışı logo brief'i ve kurumsal kimlik (CIP) spesifikasyonu üretir.",
        "sample_prompt": "Kurumsal kimlik için logo brief'i ve kartvizit tasarım yönergelerini hazırla.",
        "config_snippet": """# 1. Logo Stili ve Sektörel Brief Arama:
python .agent/skills/design/scripts/logo/search.py "fintech minimal geometric"

# 2. Kurumsal Kimlik (CIP) Spesifikasyonu Arama ve HTML Render:
python .agent/skills/design/scripts/cip/search.py "technology startup"
python .agent/skills/design/scripts/cip/render-html.py --help"""
    },
    "web-ide-ux-architect": {
        "status": "IDE & Workstation",
        "badge_class": "badge-info",
        "file": "DESIGN.md (Operate Modu · Split-Pane · Ctrl+K)",
        "features": [
            "Split-Pane & Dock Mimarisi",
            "Komut Paleti (Ctrl+K / /)",
            "Sıfır Layout Shift (tabular-nums)",
            "Düşük Gecikmeli Klavye Navigasyonu"
        ],
        "detail": "Kod editörü, terminal, ajan paneli, dosya ağacı ve komut paleti içeren yüksek bilgi yoğunluklu geliştirici araçları ve IDE arayüzleri için mimari rehber.",
        "sample_prompt": "Düşük gecikmeli, kod editörü, komut paleti ve split-pane panelli bir geliştirici çalışma istasyonu tasarla.",
        "config_snippet": """# IDE & Geliştirici Aracı Ergonomi Kuralları:
# - Yüzey Modu : Operate (Sıkı 1px kenarlıklar, sıfır dekoratif blur/glow)
# - Kısayollar : Ctrl+K / '/' (Arama), Esc (Temizle), 1-2-3 (Görünüm), T (Tema)
# - Sayısal    : font-variant-numeric: tabular-nums (Sayaç ve tablolarda zorunlu)"""
    },
    "prelaunch-audit": {
        "status": "Production Ready",
        "badge_class": "badge-success",
        "file": "PRELAUNCH-REPORT.md + 5 Doğrulama Betiği",
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
python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py --dir .
python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --check
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
        "status": "Token & Slayt Motoru",
        "badge_class": "badge-accent",
        "file": "DESIGN.md (§4 Token Sözleşmesi) & CSS Değişkenleri",
        "features": [
            "3 Katmanlı Token (Primitive → Semantic → Component)",
            "DESIGN.md YAML Frontmatter Senkronu",
            "allowedSelectors Monospace İzni",
            "HTML Slayt Render (generate-slide.py)"
        ],
        "detail": "<repo-kök>/DESIGN.md içindeki 3 katmanlı token mimarisini (primitive, semantic, component) ve CSS değişkenlerini üretir; ayrıca sunum slaytlarını token denetimli HTML olarak render eder.",
        "sample_prompt": "DESIGN.md için 3 katmanlı design token mimarisi (primitive, semantic, component) ve CSS değişkenleri üret.",
        "config_snippet": """# 1. DESIGN.md Token Sözleşmesi Doğrulaması:
python .agent/skills/musgoku/scripts/check_design_contract.py --strict

# 2. Sunum / Slayt HTML Render ve Token Denetimi:
python .agent/skills/design-system/scripts/generate-slide.py --help
python .agent/skills/design-system/scripts/html-token-validator.py"""
    },
    "ui-styling": {
        "status": "Tailwind & shadcn/ui",
        "badge_class": "badge-warning",
        "file": "tailwind.config.js / components.json / CSS",
        "features": ["Tailwind CSS Utility", "shadcn/ui & Radix Primitives", "Dark/Light Tema Eşliği", "Erişilebilir Focus-Visible"],
        "detail": "DESIGN.md token sözleşmesini Tailwind CSS ve shadcn/ui bileşenlerine dönüştürür; klavye erişilebilirliği (:focus-visible) ve çift tema (dark/light) uyumunu sağlar.",
        "sample_prompt": "Bileşeni DESIGN.md token'larına bağlı Tailwind CSS sınıfları ve dark/light tema desteğiyle stillendir.",
        "config_snippet": """// tailwind.config.js — DESIGN.md Semantic Token Bağlantısı
module.exports = {
  darkMode: ["class", '[data-theme="dark"]'],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "var(--bg-canvas)",
        surface: "var(--bg-surface)",
        primary: "var(--accent-primary)"
      }
    }
  }
}"""
    },
    "task-observer": {
        "status": "Opsiyonel Config",
        "badge_class": "badge-warning",
        "file": ".agent/observations/log.md",
        "features": ["Otomatik Gözlem", "Skill Geliştirme", "İlke Yayılımı (P1-P3)"],
        "detail": "Görev sırasında metodolojik eksiklikler `.agent/observations/log.md` ve `cross-cutting-principles.md` dosyalarına kaydedilir.",
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
        "file": ".git / Remote Repo / package.json",
        "features": ["commitx Peşin Yetki", "Semantik Tag (vX.Y.Z)", "Otonom Push", "Onaysız Commit Yasağı"],
        "detail": "Kullanıcı onayından sonra veya peşin yetkili `commitx` / `commitle` komutuyla doğrulama kapılarını çalıştırır, semantik sürüm etiketini artırır ve uzak depoya gönderir.",
        "sample_prompt": "commitx: Yapılan değişiklikleri semantik sürüm etiketi artırarak commit ve push yap.",
        "config_snippet": """# Peşin Yetkili Doğrudan Yayın (Ara onay sormadan tamamlar):
commitx
commitle
/commitx"""
    },
    "production-docker-architect": {
        "status": "Proje Dosyası",
        "badge_class": "badge-info",
        "file": "Dockerfile / docker-compose.yml / .dockerignore",
        "features": ["Multi-stage Build", "Non-root User", "Katman Önbellekleme", "Zero-Trust Güvenlik"],
        "detail": "Projeye ait çok aşamalı (multi-stage), minimum imaj boyutlu ve non-root güvenli container tanımları üretir veya optimize eder.",
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
        "status": "Ölçülebilir Kapı",
        "badge_class": "badge-info",
        "file": "src/locales/*.json + i18n_checker.py",
        "features": ["E1 Sözlük Senkronu", "E3 Kod ↔ Sözlük Kontrolü", "E4 defaultValue Yasağı", "E5 Hardcoded Metin Taraması"],
        "detail": "Uygulamanın çeviri sözlük dosyalarını (en.json, tr.json) ve kaynak kodunu tarar; eksik anahtarları, yasaklı defaultValue kullanımını ve hardcoded metinleri yakalar.",
        "sample_prompt": "Uygulama genelinde hardcoded metinleri tara ve i18n çeviri anahtarlarını i18n_checker.py ile denetle.",
        "config_snippet": """# Deterministik i18n Doğrulama Kapısı (E1-E8):
python .agent/skills/i18n-localization/scripts/i18n_checker.py
python .agent/skills/i18n-localization/scripts/i18n_checker.py --strict"""
    },
    "brand": {
        "status": "Proje Dosyası",
        "badge_class": "badge-info",
        "file": "docs/brand-guidelines.md + DESIGN.md",
        "features": ["Marka Kılavuzu", "Ses Tonu (Voice & Tone)", "Renk/Tipografi Eşlemesi", "Tutarlılık Denetimi"],
        "detail": "Marka kılavuzunu (docs/brand-guidelines.md) üretir veya senkronize eder; ses tonu, mesaj çerçevesi ve görsel kimliği DESIGN.md token'larına bağlar.",
        "sample_prompt": "Marka tonu, görsel kimlik ve renk/font kurallarını içeren marka kılavuzunu oluştur.",
        "config_snippet": """# docs/brand-guidelines.md & DESIGN.md Senkronu:
# 1. Marka Özü ve Ses Tonu (Voice & Tone)
# 2. Görsel Kimlik ve Renk Rolleri (DESIGN.md §4 ile senkron)
# 3. Tipografi Hiyerarşisi (DESIGN.md §5 ile senkron)"""
    },
    "musgoku": {
        "status": "Ana Orkestratör",
        "badge_class": "badge-info",
        "file": "PROJECT_BRIEF.md / DB_MIGRATIONS.md / 15 Kapı",
        "features": ["5 Katmanlı Dikey Dilim", "Java/Spring & React/Vite", "15 Ölçülebilir Kalite Kapısı", "Cerrahi Skill Güncelleme"],
        "detail": "Global geliştirme yönlendiricisi. Backend (Java/Spring Boot) ve Frontend (React/TypeScript/Vite) mimarisini, 15 deterministik doğrulama kapısını ve cerrahi skill güncelleme protokolünü yönetir.",
        "sample_prompt": "Spring Boot REST controller ve JPA entity katmanını 5 katmanlı dikey dilimle oluştur; doğrulama kapılarını çalıştır.",
        "config_snippet": """# Temel Mimari & Kalite Kapıları:
python .agent/skills/musgoku/scripts/rules_gates.py --strict
python .agent/skills/musgoku/scripts/check_project_brief.py
python .agent/skills/musgoku/scripts/check_db_migrations.py
python .agent/skills/musgoku/scripts/check_api_docs.py
python .agent/skills/musgoku/scripts/check_bundle_limits.py"""
    },
    "onboarding-tour": {
        "status": "Sıfır-Ayar (Zero-Config)",
        "badge_class": "badge-success",
        "file": "scaffold_tour.py (Driver.js / React Joyride)",
        "features": ["Driver.js (Önerilen)", "React Joyride Desteği", "Pulsing Coachmarks", "Kalıcı Durum Yönetimi"],
        "detail": "Kullanıcı karşılama (onboarding), spotlight odaklamalı ürün turları, adım adım walkthrough kılavuzları ve pulsing coachmark ipucu balonları tasarlar.",
        "sample_prompt": "Yeni başlayan kullanıcılar için dashboard ve menü adımlarını tanıtan hafif bir Driver.js onboarding turu hazırla.",
        "config_snippet": """# TypeScript Onboarding Turu İskeleti Üretme:
python .agent/skills/onboarding-tour/scripts/scaffold_tour.py --engine driverjs --name dashboardTour"""
    },
    "my-idea": {
        "status": "Proje Fikir Havuzu",
        "badge_class": "badge-info",
        "file": "docs/idea/myidea.md + idea_manager.py",
        "features": ["Fikir Havuzu Analizi", "Etki-Efor-Uyum Skoru", "Top 3 Öneri Seçimi", "--to-card Kanban Üretimi"],
        "detail": "Proje planı dışındaki serbest fikirleri docs/idea/myidea.md içinde toplar; ajan büyük işler bittiğinde veya kullanıcı isteğiyle fikirleri puanlar, ilk 3 öneriyi sunar ve seçileni Kanban kartına dönüştürür.",
        "sample_prompt": "Fikirlerime bak ve güncel proje durumuna göre sıradaki en mantıklı 3 adımı öner.",
        "config_snippet": """# 1. Fikir Havuzunu İncele ve İlk 3 Öneriyi Listele:
python .agent/skills/my-idea/scripts/idea_manager.py --list
python .agent/skills/my-idea/scripts/idea_manager.py --top 3

# 2. Seçilen Fikri Standart Kanban Kartına Dönüştür:
python .agent/skills/my-idea/scripts/idea_manager.py --to-card IDEA-001"""
    },
    "react-best-practices": {
        "status": "78 Kural & Vite SPA",
        "badge_class": "badge-success",
        "file": "rules/*.md (78 Kural) + check_vite_spa.py",
        "features": ["Waterfall Eliminasyonu", "Re-render Optimizasyonu", "Compound Components", "Vite SPA vs Next.js İzolasyonu"],
        "detail": "React 19 ve Vite SPA / Next.js için 9 kategoride 78 performans ve bileşen mimarisi kuralı. Vite SPA projelerinde Next.js sızıntısını check_vite_spa.py ile mekanik olarak engeller.",
        "sample_prompt": "React bileşenindeki gereksiz re-render'ları ve waterfall veri çekimlerini ortadan kaldır.",
        "config_snippet": """# Vite SPA İzolasyon ve TypeScript Doğrulama Kapıları:
python .agent/skills/musgoku/scripts/check_vite_spa.py
python .agent/skills/musgoku/scripts/check_bundle_limits.py
npx tsc --noEmit"""
    },
    "tdd": {
        "status": "Kırmızı → Yeşil → Refactor",
        "badge_class": "badge-success",
        "file": "tests/** / *.test.ts / *Test.java",
        "features": ["Önce Kırmızı Test", "Dikey Dilim (Vertical Slice)", "Sahte Mock Yasağı", "Dikiş Noktası (Seam) Testi"],
        "detail": "Yeni iş mantığı, servis veya endpoint geliştirmede üretim kodundan önce başarısız olan (Red) testi yazar, en yalın geçiş kodunu (Green) ekler ve sahte mock testlerinden kaçınır.",
        "sample_prompt": "Yeni sipariş iptal akışını dikiş noktalarında önce kırmızı test yazarak TDD dikey dilimiyle geliştir.",
        "config_snippet": """# TDD Döngüsü (Red -> Green -> Refactor):
# 1. RED     : Davranışı kanıtlayan testi yaz ve başarısız olduğunu gör.
# 2. GREEN   : Testi geçiren en yalın üretim kodunu yaz.
# 3. REFACTOR: Testler yeşil kalırken tekrarı ve kokuları temizle."""
    },
    "diagnosing-bugs": {
        "status": "6 Aşamalı Teşhis",
        "badge_class": "badge-warning",
        "file": "bug-diagnosis-enforcement.md + knowledge-base.md",
        "features": ["Faz 1: Kırmızı Döngü Zorunluluğu", "3 Somut Hipotez", "İzole Deney", "Regresyon Testi & KB Kaydı"],
        "detail": "Koda dokunmadan önce hatayı deterministik olarak yeniden üreten kırmızı geri bildirim döngüsü kurar; tahminle kod değiştirmeyi yasaklar ve kök nedeni regresyon testiyle kapatır.",
        "sample_prompt": "Çöken endpoint için kırmızı geri bildirim döngüsü kur, 3 hipotez üret ve hatayı teşhis et.",
        "config_snippet": """# 6 Aşamalı Hata Teşhis Protokolü (/fix-bug):
# 1. Kırmızı Geri Bildirim Döngüsü (Hatayı yeniden üret)
# 2. 3 Hipotez Kur
# 3. En Küçük Deneyle Sına
# 4. Kök Nedeni Onar
# 5. Regresyon Testini Yeşile Çevir
# 6. knowledge-base.md'ye Kaydet"""
    },
    "code-review": {
        "status": "Çift Eksenli İnceleme",
        "badge_class": "badge-info",
        "file": "Martin Fowler Smells + PRD Şartname Uyumu",
        "features": ["Eksen 1: Standartlar & Smell", "Eksen 2: Şartname & Scope Creep", "Paralel Alt Ajan Denetimi", "Ciddiyet Dereceli Rapor"],
        "detail": "Kod değişikliklerini iki bağımsız eksende inceler: Martin Fowler kod kokuları (bloaters, couplers, dispensables) ve PRD/Gherkin şartname uyumu (eksik katman veya kapsam sapması).",
        "sample_prompt": "Mevcut branch değişikliklerini Standartlar ve Şartname eksenlerinde iki paralel alt ajanla incele.",
        "config_snippet": """# İki Eksenli Kod İnceleme Akışı:
# - Eksen A (Standards): Kod kokuları, tip güvenliği, kullanılmayan kod
# - Eksen B (Spec)     : Gherkin AC, 5 katman bütünlüğü, scope creep"""
    },
    "codebase-design": {
        "status": "Derin Modül Mimarisi",
        "badge_class": "badge-info",
        "file": "PROJECT_BRIEF.md + Modül Sınırları",
        "features": ["Derin Modüller (Deep Modules)", "Dar Arayüz / Karmaşık İçerik", "Dikiş Noktaları (Seam)", "Silme Testi (Deletion Test)"],
        "detail": "John Ousterhout ilkeleriyle sığ modül çoğalmasını engeller; dar ve basit arayüzlerin arkasına karmaşıklığı gizleyen derin modüller ve kolay silinebilir sınırlar tasarlar.",
        "sample_prompt": "Ödeme modülünün arayüzünü derinleştir, dikiş noktasını ve silme testini belirle.",
        "config_snippet": """# Derin Modül Kontrol Listesi:
# 1. Arayüz (interface) uygulamasından çok daha basit mi?
# 2. Bir özellik değiştiğinde tek bir modül mü değişiyor?
# 3. Silme Testi: Modülü tek klasörden yan etkisiz silebilir miyiz?"""
    },
    "domain-modeling": {
        "status": "Ortak Dil & ADR",
        "badge_class": "badge-info",
        "file": "GLOSSARY.md + docs/adr/ADR-*.md",
        "features": ["Ubiquitous Language", "GLOSSARY.md Senkronu", "3 Kriterli ADR Filtresi", "Sınırlandırılmış Bağlam (Bounded Context)"],
        "detail": "İş alanı kavramlarını kod isimlendirmesiyle (tablo, sınıf, endpoint) birebir hizalar; GLOSSARY.md sözlüğünü güncel tutar ve geri dönüşü zor mimari kararlar için ADR üretir.",
        "sample_prompt": "İş kavramlarını netleştir, GLOSSARY.md sözlüğünü güncelle ve geri dönüşü zor karar için ADR oluştur.",
        "config_snippet": """# Kalıcı Mimari Hafıza Dosyaları:
# - <repo-kök>/GLOSSARY.md : İş alanı terimleri ve kod karşılıkları
# - docs/adr/ADR-0001-*.md : Geri dönüşü maliyetli mimari karar kayıtları"""
    },
    "karpathy-guidelines": {
        "status": "Sadelik & LLM Council",
        "badge_class": "badge-success",
        "file": "council_ranker.py + context-compression-headroom.md",
        "features": [
            "Cerrahi Değişiklik & Basitlik",
            "Varsayımları Yüzeye Çıkarma",
            "3 Aşamalı LLM Council (Borda Skoru)",
            "Action-First & Caveman Sıkıştırma",
            "Headroom Sacred Hot Zone"
        ],
        "detail": "Spekülatif karmaşıklığı engeller, varsayımları yüzeye çıkarır, mimari ikilemlerde 3 aşamalı kör konsey hakemliği yürütür ve uzun oturumlarda prompt cache'i (Sacred Hot Zone) korur.",
        "sample_prompt": "Kod karmaşıklığını azalt, gereksiz soyutlamaları sadeleştir veya /council ile 3 alternatifli hakemlik yap.",
        "config_snippet": """# LLM Council Borda Skoru Hesaplayıcı:
python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample"""
    },
    "security-audit": {
        "status": "Zafiyet & Pen-Test",
        "badge_class": "badge-danger",
        "file": "validate-findings.cjs + 14 Saldırı Rehberi",
        "features": [
            "Guidance & Full-Audit Modları",
            "OWASP & Yetki Aşımı (IDOR/BOLA)",
            "Public Form 6-Katman Kalkanı",
            "İzole Alt-Ajan Doğrulaması"
        ],
        "detail": "Kod tabanlarında zafiyet avcılığı, sınır ihlalleri, yetki aşımı ve public form istismar denetimi yürütür; bulguları şema doğrulayıcılarla kanıtlar.",
        "sample_prompt": "/check-security: Sistem genelinde yetki aşımı, public form abuse riskleri ve env sızıntılarını derinlemesine tara.",
        "config_snippet": """# Güvenlik Bulguları ve Kapsam Defteri Doğrulaması:
node .agent/skills/security-audit/scripts/validate-findings.cjs
node .agent/skills/security-audit/scripts/validate-coverage-ledger.cjs"""
    },
    "seo-growth": {
        "status": "SEO & GEO (AI Search)",
        "badge_class": "badge-accent",
        "file": "seo_checker.py + robots.txt + /llms.txt",
        "features": [
            "Teknik SEO & SERP Denetleyicisi",
            "GEO (ChatGPT / Perplexity / AI Overviews)",
            "AI Crawler Matrisi & /llms.txt",
            "JSON-LD Schema.org & Topic Clusters",
            "GTM Lansman & CRO Formülleri"
        ],
        "detail": "Arama motoru optimizasyonu (SEO), yapay zeka arama motoru görünürlüğü (GEO), JSON-LD yapısal veri şemaları ve rekabetçi içerik boşluğu analizini yönetir; seo_checker.py ile doğrular.",
        "sample_prompt": "/seo-apply: Sitemiz için JSON-LD şemaları, OpenGraph etiketleri, robots.txt ve llms.txt dosyalarını kur ve doğrula.",
        "config_snippet": """# Deterministik SEO & GEO Doğrulama Kapısı:
python .agent/skills/seo-growth/scripts/seo_checker.py
python .agent/skills/seo-growth/scripts/seo_checker.py --strict"""
    },
    "doc-coauthoring": {
        "status": "PRD & RFC Süreci",
        "badge_class": "badge-info",
        "file": "PRODUCT.md / SPRINT_PLAN.md / RFC",
        "features": ["3 Aşamalı Yazım Süreci", "Bağlamsız Okur Testi", "[DOM]-[TIP]-[NO] Kurumsal ID", "Gherkin Kabul Kriterleri"],
        "detail": "PRD, teknik şartname, RFC ve karar dokümanlarının yazım sürecini yönetir: bağlam toplama, bölüm bölüm yapılandırma ve bağlamsız okur testi.",
        "sample_prompt": "Yeni özellik için kurumsal ID standartlarına ve Gherkin kabul kriterlerine uygun PRD dokümanı hazırla.",
        "config_snippet": """# Kurumsal Gereksinim ID Standardı ([DOM]-[TIP]-[NO]):
# - PRD / Ürün Gerçeği : <repo-kök>/PRODUCT.md
# - Sprint Planı       : <repo-kök>/SPRINT_PLAN.md
# - Gherkin Senaryoları: specs/S1-01-*.feature"""
    },
    "slides": {
        "status": "Sunum Stratejisi",
        "badge_class": "badge-info",
        "file": "25 Slayt Düzeni + PAS / AIDA / FAB",
        "features": ["Deck Stratejisi & Duygu Yayı", "25 Slayt Düzeni (Layout)", "PAS / AIDA / FAB Metin Formülleri", "design-system HTML Render Bağlantısı"],
        "detail": "Yatırımcı sunumu (pitch deck), teknik sunum ve ürün lansmanı için hikaye akışı, slayt sıralaması ve metin kurgusunu üretir; HTML render işlemini design-system'e devreder.",
        "sample_prompt": "Yatırımcı sunumu için PAS formülüyle 10 slaytlık pitch deck metni ve düzeni çıkar.",
        "config_snippet": """# Slayt İçeriği -> HTML Deck Akışı:
# 1. slides        : Hikaye yayı, 25 layout seçimi ve slayt metinlerini üretir.
# 2. design-system : generate-slide.py ile HTML slaytlarını render eder ve denetler."""
    },
    "verify-last": {
        "status": "Mikro Doğrulama",
        "badge_class": "badge-info",
        "file": "git status / HEAD~1..HEAD",
        "features": ["Uncommitted Çalışma Ağacı", "Son Commit Denetimi", "Kapsam-Duyarlı Build/Test", "Cerrahi 5-Katman Kontrolü"],
        "detail": "Anlık oturumda yapılan son kod değişikliklerini veya son commit'i tüm projeyi taramadan cerrahi olarak derleme, tip ve katman bütünlüğü açısından doğrular.",
        "sample_prompt": "/verify-last: Son yapılan geliştirmeleri, uncommitted dosyaları ve regresyon riskini cerrahi olarak denetle.",
        "config_snippet": """# Mikro Doğrulama Tetikleme:
/verify-last"""
    },
    "verify-sprint": {
        "status": "Mezo Doğrulama",
        "badge_class": "badge-warning",
        "file": "SPRINT_PLAN.md / KANBAN.md / specs/*.feature",
        "features": ["Aktif Sprint Kabul Denetimi", "Gherkin Senaryo Doğrulaması", "Kart Başına 5 Katman", "check_sprint_board.py Kapısı"],
        "detail": "Aktif sprint veya yeni kapanan sprint sınırındaki tüm kartların Gherkin kabul kriterlerini, 5 katmanlı dikey dilimini ve KULLANICI_TEST_REHBERI.md adımlarını doğrular.",
        "sample_prompt": "/verify-sprint: Aktif sprint hedeflerini, kart kabul kriterlerini (Gherkin) ve 5 katman dikey dilim bütünlüğünü denetle.",
        "config_snippet": """# Mezo Sprint Doğrulama ve Kapı Komutu:
/verify-sprint
python .agent/skills/musgoku/scripts/check_sprint_board.py"""
    },
    "verify-prd": {
        "status": "Makro Doğrulama",
        "badge_class": "badge-info",
        "file": "PRODUCT.md / PRD / 5-Katman Dikey Dilim",
        "features": ["Retrospektif Sahte Bitti Avcısı", "5 Katmanlı Dikey Dilim Kanıtı", "Mock/LocalStorage Taraması", "PRD Kabul Karnesi"],
        "detail": "Tüm proje ve PRD genelinde tamamlandı beyan edilen özelliklerin gerçekte 5 katmanının (DB, View/RPC, API, UI, Admin Formu) tam olup olmadığını bağımsız denetler.",
        "sample_prompt": "/verify-prd: Son tamamlanan özelliğin kabul kriterlerini, 5 katman dikey dilim bütünlüğünü ve regression risklerini bağımsız denetle.",
        "config_snippet": """# Makro PRD Doğrulama Tetikleme:
/verify-prd"""
    },
    "fix-bug": {
        "status": "Kırmızı Döngü Orkestratörü",
        "badge_class": "badge-warning",
        "file": "diagnosing-bugs → musgoku → karpathy",
        "features": ["Önce Kırmızı Kanıt Döngüsü", "3 Hipotez & İzolasyon", "Cerrahi Onarım", "Regresyon Testi"],
        "detail": "Hata ayıklama orkestratörü; kod değiştirmeden önce hatayı kanıtlayan kırmızı geri bildirim döngüsü kurar, kök nedeni onarır ve regresyon testi ekler.",
        "sample_prompt": "/fix-bug: Çöken endpoint için önce kırmızı geri bildirim döngüsü kur, 3 hipotez üret ve cerrahi düzeltme yap.",
        "config_snippet": """# Hata Teşhis ve Onarım Komutu:
/fix-bug <hata mesajı veya senaryo>"""
    },
    "check-security": {
        "status": "Güvenlik Orkestratörü",
        "badge_class": "badge-danger",
        "file": "security-audit + Public Form Kalkanı",
        "features": ["OWASP Zafiyet Taraması", "Public Form 6-Katman Kalkanı", "Yetki Aşımı (RLS/IDOR)", "Secret & Env Sızıntı Kontrolü"],
        "detail": "OWASP güvenlik denetimi, public form istismar koruması (Turnstile, Rate-limit, Blind Insert RLS) ve gizli anahtar sızıntılarını doğrulayan orkestratör.",
        "sample_prompt": "/check-security: Sistem genelinde yetki aşımı, public form abuse riskleri ve env sızıntılarını derinlemesine tara.",
        "config_snippet": """# Güvenlik Denetimi Tetikleme:
/check-security"""
    },
    "council": {
        "status": "Konsey Orkestratörü",
        "badge_class": "badge-info",
        "file": "council_ranker.py + docs/adr/",
        "features": ["Stage 1: Anonim Öneriler", "Stage 2: Kör Hakemlik", "Stage 3: Borda Sentezi", "Otomatik ADR Kaydı"],
        "detail": "Üç aşamalı LLM konseyi ve kör hakemlik orkestratörü; mimari ikilemlerde alternatif üretip Borda skoruyla sentezler ve docs/adr/ altında karar kaydı üretir.",
        "sample_prompt": "/council: Mimari ikilem için 3 alternatifli kör hakemlik konseyi topla, Borda puanı hesapla ve ADR kaydı çıkar.",
        "config_snippet": """# Konsey Hakemliği ve Borda Hesaplayıcı:
/council <mimari ikilem>
python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample"""
    },
    "seo-apply": {
        "status": "SEO & GEO Orkestratörü",
        "badge_class": "badge-accent",
        "file": "seo_checker.py + JSON-LD + /llms.txt",
        "features": ["Meta & OpenGraph Enjeksiyonu", "JSON-LD Schema.org", "AI Crawler robots.txt & llms.txt", "seo_checker.py --strict"],
        "detail": "Uçtan uca SEO, yapay zeka arama motoru optimizasyonu (GEO) ve yapısal veri orkestratörü; meta etiketleri, OpenGraph, JSON-LD ve llms.txt kurup mekanik kapıyla doğrular.",
        "sample_prompt": "/seo-apply: Sitemiz için JSON-LD şemaları, OpenGraph etiketleri, robots.txt ve llms.txt dosyalarını kur ve doğrula.",
        "config_snippet": """# Uçtan Uca SEO Kurulumu ve Kapı Doğrulaması:
/seo-apply
python .agent/skills/seo-growth/scripts/seo_checker.py --strict"""
    },
    "commitx": {
        "status": "Otonom Yayın",
        "badge_class": "badge-success",
        "file": "git-release-workflow (Semver + Push)",
        "features": ["Peşin Kullanıcı Yetkisi", "Otomatik Kapı Doğrulaması", "Semantik Tag (vX.Y.Z)", "Kesintisiz Commit & Push"],
        "detail": "Peşin kullanıcı yetkisiyle kesintisiz otonom sürüm yayını orkestratörü; doğrulama kapılarını çalıştırıp semantik sürüm artışı, commit, tag ve push adımlarını tek seferde tamamlar.",
        "sample_prompt": "commitx: Değişiklikleri doğrula, semantik tag artır ve uzak depoya push et.",
        "config_snippet": """# Peşin Yetkili Sürüm Yayını:
commitx
/commitx"""
    },
    "gs-update": {
        "status": "Cerrahi Güncelleyici",
        "badge_class": "badge-info",
        "file": "npx goku-dev-skills update",
        "features": ["Sıfır-Şişkinlik (Zero-Bloat)", "Proje Kuralı Koruması", "--check Dry-Run Önizleme", "--remote GitHub Senkronu"],
        "detail": "Sıfır şişkinlik ve proje kuralı korumalı cerrahi skill seti güncelleme orkestratörü; kurulu olmayan skill veya temaları indirmeden mevcut dağıtımı günceller.",
        "sample_prompt": "/gs-update: Kurulu skill setini en son sürüme güncelle, proje ek kurallarını koru.",
        "config_snippet": """# Cerrahi Skill Seti Güncelleme Komutları:
npx goku-dev-skills update --check
npx goku-dev-skills update
npx goku-dev-skills update --remote"""
    },
    "prelaunch": {
        "status": "Canlıya Alma Orkestratörü",
        "badge_class": "badge-success",
        "file": "PRELAUNCH-REPORT.md (GO / NO-GO)",
        "features": ["20 Çekirdek Madde", "KVKK & Consent Mode v2", "Ham HTML SEO", "WCAG 2.2 AA Axe"],
        "detail": "Yirmi maddelik canlıya alma denetimi ve GO/NO-GO karar orkestratörü; KVKK, Consent Mode v2, ham HTML SEO ve erişilebilirliği doğrulayıp raporlar.",
        "sample_prompt": "/prelaunch: Sitemizi yayına almaya hazır mıyız? 20 maddelik çekirdek denetimi ve yasal onay mekanizmalarını doğrula.",
        "config_snippet": """# Canlıya Alma Denetimi:
/prelaunch
python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py --dir ."""
    },
    "prelaunch-update": {
        "status": "Mevzuat Senkronu",
        "badge_class": "badge-warning",
        "file": "prelaunch_updater.py",
        "features": ["KVKK İdari Para Cezası Senkronu", "7499 s. Kanun Bildirim Sınırları", "Reklam Kurulu 28/B", "AI Bot Kuralları"],
        "detail": "Mevzuat idari para cezaları ve platform kuralları dinamik senkron orkestratörü; resmi kaynakları tarayarak prelaunch-audit referans maddelerini günceller.",
        "sample_prompt": "/prelaunch-update: Güncel KVKK ve GDPR idari para cezalarını resmi tebliğlerden sorgula ve dokümanları güncelle.",
        "config_snippet": """# Mevzuat Tazelik Kontrolü:
/prelaunch-update
python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --check"""
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
    "slides": "Yatırımcı sunumu için PAS formülüyle 10 slaytlık pitch deck metni ve düzeni çıkar.",
    "verify-last": "/verify-last: Son yapılan geliştirmeleri, uncommitted dosyaları ve regresyon riskini cerrahi olarak denetle.",
    "verify-sprint": "/verify-sprint: Aktif sprint hedeflerini, kart kabul kriterlerini (Gherkin) ve 5 katman dikey dilim bütünlüğünü denetle.",
    "verify-prd": "/verify-prd: Son tamamlanan özelliğin kabul kriterlerini, 5 katman dikey dilim bütünlüğünü ve regression risklerini bağımsız denetle.",
    "check-security": "/check-security: Sistem genelinde yetki aşımı, public form abuse riskleri ve env sızıntılarını derinlemesine tara.",
    "fix-bug": "/fix-bug: Çöken endpoint için önce kırmızı geri bildirim döngüsü kur, 3 hipotez üret ve cerrahi düzeltme yap.",
    "council": "/council: Mimari ikilem için 3 alternatifli kör hakemlik konseyi topla, Borda puanı hesapla ve ADR kaydı çıkar.",
    "prelaunch": "/prelaunch: Sitemizi yayına almaya hazır mıyız? 20 maddelik çekirdek denetimi ve yasal onay mekanizmalarını doğrula.",
    "prelaunch-update": "/prelaunch-update: Güncel KVKK ve GDPR idari para cezalarını resmi tebliğlerden sorgula ve dokümanları güncelle.",
    "seo-apply": "/seo-apply: Sitemiz için JSON-LD şemaları, OpenGraph etiketleri, robots.txt ve llms.txt dosyalarını kur ve doğrula.",
    "commitx": "commitx: Değişiklikleri doğrula, semantik tag artır ve uzak depoya push et.",
    "gs-update": "/gs-update: Kurulu skill setini en son sürüme güncelle, proje ek kurallarını koru.",
    "ui-polish": "/ui-polish: Arayüzü hazır bileşen ve paletlerden ilhamla zenginleştir, generic AI kalıplarını temizle, tipografi ve boşluk ritmini modernleştir, WCAG kontrastını doğrula."
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
    pkg_version = "1.14.3"
    if pkg_json_file.is_file():
        try:
            pkg_version = json.loads(pkg_json_file.read_text(encoding="utf-8")).get("version", "1.14.3")
        except Exception:
            pass

    # DESIGN.md sözleşmesinden ana tokenları oku (varsa)
    design_tokens = {
        "surface-ground": "#090a0f",
        "surface-inset": "#06070a",
        "surface-raised": "#10121b",
        "surface-overlay": "#161926",
        "text-primary": "#f8fafc",
        "text-muted": "#94a3b8",
        "primary": "#6366f1",
        "secondary": "#818cf8",
        "accent": "#f43f5e",
    }
    design_md_file = PROJECT_ROOT / "DESIGN.md"
    if design_md_file.is_file():
        try:
            scripts_dir = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            from check_design_contract import parse_design_md
            fm, _ = parse_design_md(design_md_file)
            c_map = fm.get("colors") if isinstance(fm.get("colors"), dict) else {}
            for k in list(design_tokens.keys()):
                if k in c_map and c_map[k]:
                    design_tokens[k] = str(c_map[k]).strip()
        except Exception:
            pass

    cat_badges = {
        "Tasarım & UI": "cat-design",
        "Kod & Mimari": "cat-code",
        "Teslimat & Kalite": "cat-delivery",
        "Marka & Doküman": "cat-brand",
        "Oturum Komutları (Ensemble)": "cat-ensemble"
    }

    cat_icons = {
        "Tasarım & UI": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>',
        "Kod & Mimari": '<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>',
        "Teslimat & Kalite": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        "Marka & Doküman": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>',
        "Oturum Komutları (Ensemble)": '<svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>'
    }

    sidebar_cat_items = "".join(
        f'<button class="sidebar-cat-btn {cat_badges.get(cat, "")}" data-cat="{cat}" onclick="setCategoryFilter(\'{cat}\', this)" title="{cat} ({len(skills_in_cat)} beceri)">'
        f'{cat_icons.get(cat, "")}'
        f'<span class="cat-label">{cat}</span>'
        f'<span class="cat-count">({len(skills_in_cat)})</span></button>'
        for cat, skills_in_cat in CATEGORIES.items()
    )

    quick_slash_pills = "".join(
        f'<button class="quick-slash-pill" onclick="quickSelectSlash(\'{cmd["command"]}\')" title="{cmd["name"]}: {cmd["goal"]}">'
        f'<svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> {cmd["command"]}</button>'
        for cmd in SLASH_COMMANDS
    )

    
    DOMAINS_MAP = [
        {
            "id": "plan",
            "title": "Planlama & Mimari",
            "color_var": "var(--accent-primary)",
            "subtle_var": "var(--accent-primary-subtle)",
            "border_var": "var(--accent-primary-border)",
            "commands": ["/council"]
        },
        {
            "id": "debug",
            "title": "Hata Teşhis & Güvenlik",
            "color_var": "var(--status-danger)",
            "subtle_var": "var(--status-danger-subtle)",
            "border_var": "var(--status-danger-border)",
            "commands": ["/fix-bug", "/check-security"]
        },
        {
            "id": "design",
            "title": "Tasarım & Zanaat",
            "color_var": "var(--status-warning)",
            "subtle_var": "var(--status-warning-subtle)",
            "border_var": "var(--status-warning-border)",
            "commands": ["/ui-polish", "/seo-apply"]
        },
        {
            "id": "release",
            "title": "Yayın & Sürüm",
            "color_var": "var(--status-success)",
            "subtle_var": "var(--status-success-subtle)",
            "border_var": "var(--status-success-border)",
            "commands": ["/commitx", "/prelaunch", "/prelaunch-update", "/gs-update"]
        },
        {
            "id": "accept",
            "title": "Kabul & Doğrulama",
            "color_var": "var(--status-info)",
            "subtle_var": "var(--status-info-subtle)",
            "border_var": "var(--status-info-border)",
            "commands": ["/verify-last", "/verify-sprint", "/verify-prd"]
        }
    ]

    panel_chunks = []
    cmd_by_name = {c["command"]: c for c in SLASH_COMMANDS}
    for d in DOMAINS_MAP:
        cards_html = []
        for cmd_name in d["commands"]:
            cmd = cmd_by_name.get(cmd_name)
            if not cmd:
                continue
            cmd_name_clean = html.escape(cmd["name"])
            cmd_goal_clean = html.escape(cmd["goal"])
            cmd_desc_clean = html.escape(cmd["description"])
            cards_html.append(
                f'<div class="sheet-card" tabindex="0" role="button" data-cmd="{cmd["command"]}" '
                f'data-name="{cmd_name_clean.lower()}" data-desc="{cmd_desc_clean.lower()}" data-goal="{cmd_goal_clean.lower()}" '
                f'onclick="selectFromBottomSheet(\'{cmd["command"]}\')" '
                f'onkeydown="if(event.key===\'Enter\'||event.key===\' \'){{selectFromBottomSheet(\'{cmd["command"]}\');event.preventDefault();}}">'
                f'<div class="sheet-card-top">'
                f'<div class="sheet-card-name-wrap">'
                f'<svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>'
                f'<span class="slash-command-title">{cmd["command"]}</span>'
                f'</div>'
                f'<span class="sheet-card-badge" style="background:{d["subtle_var"]};color:{d["color_var"]};border:1px solid {d["border_var"]};">{d["id"].upper()}</span>'
                f'</div>'
                f'<div class="sheet-card-goal">{cmd_goal_clean}</div>'
                f'<div class="sheet-card-desc">{cmd_name_clean}</div>'
                f'</div>'
            )
        cards_joined = "".join(cards_html)
        panel_chunks.append(
            f'<div class="sheet-domain-panel" data-domain="{d["id"]}">'
            f'<div class="sheet-domain-header">'
            f'<span class="sheet-domain-pill" style="background:{d["subtle_var"]};color:{d["color_var"]};border:1px solid {d["border_var"]};">{d["title"]}</span>'
            f'<span class="sheet-domain-count">({len(d["commands"])})</span>'
            f'</div>'
            f'<div class="sheet-card-grid">'
            f'{cards_joined}'
            f'</div>'
            f'</div>'
        )
    bottom_sheet_panels_html = "".join(panel_chunks)

    return f"""<!DOCTYPE html>
<html lang="tr" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Goku Dev Skills Kokpiti — Ajan Becerileri & Mimari Kurallar</title>
  
  <!-- Craft Typography: Space Grotesk, Plus Jakarta Sans & JetBrains Mono (Obsidian Command Deck) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">

  <style>
    /* ==========================================================================
       3-TIER DESIGN TOKEN ARCHITECTURE (design-system & frontend-design)
       ========================================================================== */
    :root, [data-theme="dark"] {{
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

      --font-display: 'Space Grotesk', 'Plus Jakarta Sans', -apple-system, sans-serif;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', "SFMono-Regular", Consolas, Menlo, monospace;

      --radius-xs: 4px;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-full: 9999px;

      /* --- Layer 2: Semantic Tokens (Dark Theme - Obsidian Command Deck, bound to DESIGN.md) --- */
      --bg-canvas: {design_tokens["surface-ground"]};
      --bg-surface: {design_tokens["surface-raised"]};
      --bg-surface-elevated: {design_tokens["surface-overlay"]};
      --bg-surface-hover: #161a29;
      --bg-subtle: rgba(255, 255, 255, 0.04);

      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-strong: rgba(99, 102, 241, 0.35);
      --border-hover: rgba(99, 102, 241, 0.5);

      --text-primary: {design_tokens["text-primary"]};
      --text-secondary: {design_tokens["text-muted"]};
      --text-tertiary: #8b9bb4;
      --text-on-accent: #ffffff;
      --text-on-brand: #ffffff;

      --accent-primary: {design_tokens["primary"]};
      --accent-primary-subtle: rgba(99, 102, 241, 0.12);
      --accent-primary-border: rgba(99, 102, 241, 0.28);

      --accent-slash: {design_tokens["accent"]};
      --accent-slash-subtle: rgba(244, 63, 94, 0.12);
      --accent-slash-border: rgba(244, 63, 94, 0.28);

      --status-success: var(--emerald-400);
      --status-success-subtle: rgba(52, 211, 153, 0.1);
      --status-success-border: rgba(52, 211, 153, 0.25);

      --status-warning: var(--amber-400);
      --status-warning-subtle: rgba(251, 191, 36, 0.1);
      --status-warning-border: rgba(251, 191, 36, 0.25);

      --status-info: #818cf8;
      --status-info-subtle: rgba(129, 140, 248, 0.12);
      --status-info-border: rgba(129, 140, 248, 0.28);

      --status-danger: var(--rose-400);
      --status-danger-subtle: rgba(248, 113, 113, 0.1);
      --status-danger-border: rgba(248, 113, 113, 0.25);

      --accent-secondary: {design_tokens["secondary"]};
      --accent-secondary-subtle: rgba(129, 140, 248, 0.12);
      --accent-secondary-border: rgba(129, 140, 248, 0.28);

      --ring-focus: #6366f1;

      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.5);
      --shadow-md: 0 6px 18px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
      --shadow-lg: 0 14px 34px rgba(0, 0, 0, 0.65), 0 0 20px -4px rgba(99, 102, 241, 0.2);

      /* --- Layer 3: Component Tokens --- */
      --header-bg: rgba(9, 10, 15, 0.88);
      --card-bg: var(--bg-surface);
      --card-border: var(--border-subtle);
      --search-input-bg: {design_tokens["surface-inset"]};
      --code-block-bg: #06070a;
      --pill-bg: var(--bg-surface-elevated);

      --sidebar-width: 270px;
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
      --text-tertiary: #475569;
      --text-on-accent: #ffffff;
      --text-on-brand: #ffffff;

      --accent-primary: var(--sky-600);
      --accent-primary-subtle: rgba(2, 132, 199, 0.08);
      --accent-primary-border: rgba(2, 132, 199, 0.2);

      --accent-slash: #be123c;
      --accent-slash-subtle: rgba(190, 18, 60, 0.08);
      --accent-slash-border: rgba(190, 18, 60, 0.22);

      --status-success: var(--emerald-600);
      --status-success-subtle: rgba(5, 150, 105, 0.08);
      --status-success-border: rgba(5, 150, 105, 0.2);

      --status-warning: #b45309;
      --status-warning-subtle: rgba(217, 119, 6, 0.08);
      --status-warning-border: rgba(217, 119, 6, 0.2);

      --status-info: var(--sky-600);
      --status-info-subtle: rgba(2, 132, 199, 0.08);
      --status-info-border: rgba(2, 132, 199, 0.2);

      --status-danger: #9f1239;
      --status-danger-subtle: #fff1f2;
      --status-danger-border: #fecdd3;

      --accent-secondary: #4f46e5;
      --accent-secondary-subtle: rgba(79, 70, 229, 0.08);
      --accent-secondary-border: rgba(79, 70, 229, 0.22);

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

      --sidebar-width: 270px;
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
      overflow-x: hidden;
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
       APP SHELL ARCHITECTURE (Collapsible Sidebar + Workspace Main + Drawer)
       ========================================================================== */
    .app-layout {{
      display: flex;
      min-height: 100vh;
      width: 100%;
      background-color: var(--bg-canvas);
    }}

    /* --- 1. COLLAPSIBLE SIDEBAR DOCK (inspired by dark-slate-dock-sidebar) --- */
    .app-sidebar {{
      width: var(--sidebar-width);
      min-width: var(--sidebar-width);
      background: var(--bg-surface);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
      overflow-x: hidden;
      z-index: 200;
      transition: width 0.24s cubic-bezier(0.16, 1, 0.3, 1), min-width 0.24s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .app-sidebar.collapsed {{
      width: 74px;
      min-width: 74px;
    }}

    .sidebar-brand {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1.25rem 1rem 1rem;
      border-bottom: 1px solid var(--border-subtle);
      gap: 0.5rem;
    }}
    .brand-main {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      min-width: 0;
    }}
    .brand-icon {{
      width: 34px;
      height: 34px;
      border-radius: var(--radius-sm);
      background: var(--accent-primary-subtle);
      border: 1px solid var(--accent-primary-border);
      color: var(--accent-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .brand-info {{
      min-width: 0;
      overflow: hidden;
    }}
    .brand-title {{
      font-family: var(--font-display);
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-primary);
      white-space: nowrap;
      letter-spacing: -0.015em;
    }}
    .brand-sub {{
      font-size: 0.7rem;
      color: var(--text-tertiary);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}
    .version-tag {{
      font-family: var(--font-sans);
      font-size: 0.65rem;
      font-weight: 600;
      background: var(--accent-primary-subtle);
      color: var(--accent-primary);
      border: 1px solid var(--accent-primary-border);
      padding: 0.05rem 0.35rem;
      border-radius: var(--radius-full);
      font-variant-numeric: tabular-nums;
    }}

    .sidebar-toggle-btn {{
      background: transparent;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-xs);
      color: var(--text-tertiary);
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      flex-shrink: 0;
      transition: all 0.15s;
    }}
    .sidebar-toggle-btn:hover {{
      color: var(--text-primary);
      background: var(--bg-surface-elevated);
      border-color: var(--border-hover);
    }}

    /* Sidebar Content Sections */
    .sidebar-section {{
      padding: 0.85rem 0.75rem;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .sidebar-section-title {{
      font-size: 0.68rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-tertiary);
      margin-bottom: 0.5rem;
      padding-left: 0.35rem;
    }}

    /* Primary Nav Items */
    .sidebar-nav {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}
    .nav-btn {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      padding: 0.55rem 0.65rem;
      border-radius: var(--radius-xs);
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-secondary);
      font-family: var(--font-sans);
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
      text-align: left;
      transition: all 0.15s;
      width: 100%;
    }}
    .nav-btn:hover {{
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
    }}
    .nav-btn.active {{
      background: var(--accent-primary-subtle);
      border-color: var(--accent-primary-border);
      color: var(--accent-primary);
      font-weight: 600;
    }}
    .nav-btn .nav-badge {{
      margin-left: auto;
      font-size: 0.68rem;
      padding: 0.1rem 0.4rem;
      border-radius: var(--radius-full);
      background: var(--bg-surface-elevated);
      color: var(--text-tertiary);
      font-variant-numeric: tabular-nums;
      font-weight: 600;
    }}
    .nav-btn.active .nav-badge {{
      background: var(--accent-primary);
      color: var(--white);
    }}
    .nav-btn .nav-badge.badge-slash {{
      color: var(--accent-slash);
      background: var(--accent-slash-subtle);
    }}
    .nav-btn.active .nav-badge.badge-slash {{
      background: var(--accent-slash);
      color: var(--white);
    }}

    /* Category List */
    .category-list {{
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }}
    .sidebar-cat-btn {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      padding: 0.45rem 0.65rem;
      border-radius: var(--radius-xs);
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-secondary);
      font-family: var(--font-sans);
      font-size: 0.8rem;
      cursor: pointer;
      text-align: left;
      transition: all 0.15s;
      width: 100%;
    }}
    .sidebar-cat-btn:hover {{
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
    }}
    .sidebar-cat-btn.active {{
      background: var(--bg-surface-elevated);
      border-color: var(--border-strong);
      color: var(--text-primary);
      font-weight: 600;
    }}
    .sidebar-cat-btn .cat-label {{
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .sidebar-cat-btn .cat-count {{
      font-size: 0.7rem;
      color: var(--text-tertiary);
      font-variant-numeric: tabular-nums;
    }}

    /* Quick Filter Chips */
    .quick-preset-chips {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}
    .preset-pill {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.35rem 0.55rem;
      border-radius: var(--radius-xs);
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-size: 0.74rem;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .preset-pill:hover {{
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      border-color: var(--border-hover);
    }}

    /* Sidebar Footer */
    .sidebar-footer {{
      margin-top: auto;
      padding: 0.85rem 0.75rem;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      background: var(--bg-surface);
    }}
    .sidebar-stats {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}
    .stat-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.72rem;
      color: var(--text-tertiary);
    }}
    .stat-val {{
      font-weight: 600;
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
    }}

    .theme-toggle-btn {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      width: 100%;
      padding: 0.45rem 0.65rem;
      border-radius: var(--radius-xs);
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      font-size: 0.78rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .theme-toggle-btn:hover {{
      border-color: var(--accent-primary);
      color: var(--accent-primary);
    }}

    /* Collapsed Sidebar Rules */
    .app-sidebar.collapsed .brand-info,
    .app-sidebar.collapsed .sidebar-section-title,
    .app-sidebar.collapsed .cat-label,
    .app-sidebar.collapsed .cat-count,
    .app-sidebar.collapsed .nav-label,
    .app-sidebar.collapsed .nav-badge,
    .app-sidebar.collapsed .preset-pill,
    .app-sidebar.collapsed .stat-row,
    .app-sidebar.collapsed #themeToggleLabel {{
      display: none !important;
    }}
    .app-sidebar.collapsed .sidebar-brand {{
      justify-content: center;
      padding: 1rem 0.4rem;
    }}
    .app-sidebar.collapsed .brand-main {{
      justify-content: center;
    }}
    .app-sidebar.collapsed .nav-btn,
    .app-sidebar.collapsed .sidebar-cat-btn {{
      justify-content: center;
      padding: 0.55rem;
    }}
    .app-sidebar.collapsed .sidebar-section {{
      padding: 0.65rem 0.35rem;
    }}

    /* --- 2. WORKSPACE MAIN & COMMAND BAR --- */
    .app-main {{
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      background: var(--bg-canvas);
    }}

    .workspace-header {{
      position: sticky;
      top: 0;
      z-index: 150;
      background: var(--header-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 0.65rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }}

    .header-search-bar {{
      position: relative;
      flex: 1;
      max-width: 600px;
      display: flex;
      align-items: center;
    }}
    .search-input {{
      width: 100%;
      background: var(--search-input-bg);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      padding: 0.45rem 2.8rem 0.45rem 2.2rem;
      border-radius: var(--radius-sm);
      font-family: var(--font-sans);
      font-size: 0.85rem;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .search-input:focus {{
      border-color: var(--ring-focus);
      background: var(--bg-surface);
      box-shadow: 0 0 0 3px var(--accent-primary-subtle);
    }}
    .header-search-bar .search-icon {{
      position: absolute;
      left: 0.75rem;
      color: var(--text-tertiary);
      pointer-events: none;
    }}
    .btn-clear-search {{
      position: absolute;
      right: 2.2rem;
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      cursor: pointer;
      font-size: 0.85rem;
      padding: 0.2rem 0.4rem;
      display: none;
    }}
    .kbd-shortcut {{
      position: absolute;
      right: 0.65rem;
      background: var(--bg-surface-elevated);
      color: var(--text-tertiary);
      border: 1px solid var(--border-subtle);
      font-family: var(--font-mono);
      font-size: 0.65rem;
      padding: 0.1rem 0.35rem;
      border-radius: var(--radius-xs);
      pointer-events: none;
    }}

    .header-controls {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }}

    .layout-toggle-group {{
      display: inline-flex;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-xs);
      padding: 2px;
      gap: 2px;
    }}
    .layout-btn {{
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      padding: 0.35rem 0.65rem;
      border-radius: var(--radius-xs);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.78rem;
      font-weight: 600;
      transition: all 0.15s;
    }}
    .layout-btn:hover {{
      color: var(--text-primary);
      background: var(--bg-surface-hover);
    }}
    .layout-btn.active {{
      background: var(--bg-surface);
      color: var(--accent-primary);
      box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    }}

    .mobile-menu-btn {{
      display: none;
      align-items: center;
      justify-content: center;
      width: 38px;
      height: 38px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-xs);
      color: var(--text-primary);
      cursor: pointer;
      flex-shrink: 0;
      transition: all 0.15s;
    }}
    .mobile-menu-btn:hover {{
      background: var(--bg-surface-hover);
      border-color: var(--accent-primary);
    }}
    .mobile-drawer-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(2px);
      z-index: 998;
      opacity: 0;
      visibility: hidden;
      transition: all 0.2s ease;
    }}
    .mobile-drawer-backdrop.active {{
      opacity: 1;
      visibility: visible;
    }}

    .btn-header-cmd {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-family: var(--font-mono);
      font-size: 0.74rem;
      padding: 0.4rem 0.65rem;
      border-radius: var(--radius-xs);
      cursor: pointer;
      transition: all 0.15s;
    }}
    .btn-header-cmd:hover {{
      border-color: var(--accent-primary);
      color: var(--accent-primary);
      background: var(--accent-primary-subtle);
    }}

    /* Workspace Content Area */
    .workspace-body {{
      padding: 1.25rem 1.75rem 3rem;
      max-width: 1440px;
      width: 100%;
    }}

    /* Quick Slash Command Ribbon (Taşmayan Yerleşim - Anti-Scroll Slop) */
    .quick-slash-ribbon {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
      padding: 0.5rem 0.75rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      margin-bottom: 1rem;
    }}
    .quick-ribbon-title {{
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-tertiary);
      display: flex;
      align-items: center;
      gap: 0.35rem;
      margin-right: 0.25rem;
      white-space: nowrap;
    }}
    .quick-slash-pills-wrap {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.4rem;
      flex: 1;
      min-width: 0;
    }}
    .btn-palette-launcher {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: var(--accent-slash-subtle);
      border: 1px solid var(--accent-slash-border);
      color: var(--accent-slash);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.3rem 0.65rem;
      border-radius: var(--radius-full);
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
      margin-left: auto;
    }}
    .btn-palette-launcher:hover {{
      background: var(--accent-slash);
      color: var(--text-primary);
      transform: translateY(-1px);
    }}
    .palette-kbd-badge {{
      display: inline-block;
      font-family: var(--font-mono);
      font-size: 0.62rem;
      padding: 0.1rem 0.35rem;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-xs);
      color: var(--text-tertiary);
    }}
    .quick-slash-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      padding: 0.25rem 0.55rem;
      border-radius: var(--radius-full);
      cursor: pointer;
      transition: all 0.15s;
      flex-shrink: 0;
    }}
    .quick-slash-pill:hover {{
      border-color: var(--accent-slash-border);
      background: var(--accent-slash-subtle);
      color: var(--accent-slash);
      transform: translateY(-1px);
    }}

    /* Adaptive Action Hub & Bottom-Sheet Standard (B.9 / Çözüm 1 & 2) */
    .btn-hub-launcher {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      font-size: 0.78rem;
      font-weight: 700;
      padding: 0.35rem 0.75rem;
      border-radius: var(--radius-full);
      cursor: pointer;
      white-space: nowrap;
      flex-shrink: 0;
      transition: all 0.15s ease;
    }}
    .btn-hub-launcher:hover {{
      border-color: var(--accent-slash-border);
      background: var(--accent-slash-subtle);
      color: var(--accent-slash);
      transform: translateY(-1px);
    }}
    .hub-launcher-count {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0.1rem 0.4rem;
      font-size: 0.65rem;
      font-weight: 800;
      border-radius: var(--radius-full);
      background: var(--border-subtle);
      color: var(--text-secondary);
    }}
    .slash-preview-strip {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      flex: 1;
      min-width: 0;
      overflow: hidden;
    }}
    .btn-ribbon-more {{
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      background: var(--accent-slash-subtle);
      border: 1px dashed var(--accent-slash-border);
      color: var(--accent-slash);
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.25rem 0.55rem;
      border-radius: var(--radius-full);
      cursor: pointer;
      white-space: nowrap;
      flex-shrink: 0;
      transition: all 0.15s ease;
    }}
    .btn-ribbon-more:hover {{
      background: var(--accent-slash);
      color: var(--text-primary);
      border-style: solid;
      transform: translateY(-1px);
    }}

    /* Bottom-Sheet Card Hub Modal */
    .bottom-sheet-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.55);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 990;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }}
    .bottom-sheet-backdrop.active {{
      opacity: 1;
      pointer-events: auto;
    }}
    .bottom-sheet-modal {{
      position: fixed;
      left: 50%;
      bottom: 0;
      transform: translate(-50%, 100%);
      width: 100%;
      max-width: 1100px;
      max-height: 86vh;
      background: var(--bg-surface-elevated);
      border-top-left-radius: var(--radius-lg);
      border-top-right-radius: var(--radius-lg);
      border: 1px solid var(--border-subtle);
      border-bottom: none;
      box-shadow: var(--shadow-lg);
      z-index: 999;
      display: flex;
      flex-direction: column;
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      box-sizing: border-box;
    }}
    .bottom-sheet-modal.active {{
      transform: translate(-50%, 0);
    }}
    .bottom-sheet-handle-wrap {{
      display: flex;
      justify-content: center;
      padding: 0.6rem 0 0.3rem 0;
      cursor: grab;
    }}
    .bottom-sheet-handle {{
      width: 44px;
      height: 4px;
      border-radius: var(--radius-full);
      background: var(--border-strong);
    }}
    .bottom-sheet-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 0.75rem 1.25rem 1rem 1.25rem;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .bottom-sheet-title-wrap {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}
    .bottom-sheet-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0;
      letter-spacing: -0.015em;
    }}
    .bottom-sheet-badge {{
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: var(--radius-full);
      background: var(--accent-slash-subtle);
      color: var(--accent-slash);
      border: 1px solid var(--accent-slash-border);
    }}
    .bottom-sheet-search-wrap {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex: 1;
      max-width: 380px;
      padding: 0.4rem 0.75rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-xs);
      transition: border-color 0.15s;
    }}
    .bottom-sheet-search-wrap:focus-within {{
      border-color: var(--accent-primary);
      outline: 2px solid var(--accent-primary-subtle);
    }}
    .bottom-sheet-search-input {{
      width: 100%;
      border: none;
      background: transparent;
      color: var(--text-primary);
      font-size: 0.82rem;
      outline: none;
    }}
    .bottom-sheet-search-input::placeholder {{
      color: var(--text-tertiary);
    }}
    .bottom-sheet-btn-close {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      color: var(--text-secondary);
      border-radius: var(--radius-xs);
      cursor: pointer;
      transition: all 0.15s;
    }}
    .bottom-sheet-btn-close:hover {{
      background: var(--border-subtle);
      color: var(--text-primary);
    }}
    .bottom-sheet-body {{
      flex: 1;
      overflow-y: auto;
      padding: 1.25rem 1.25rem 2rem 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      overscroll-behavior: contain;
    }}
    .sheet-domain-panel {{
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}
    .sheet-domain-header {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .sheet-domain-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.6rem;
      border-radius: var(--radius-full);
    }}
    .sheet-domain-count {{
      font-size: 0.75rem;
      color: var(--text-tertiary);
      font-weight: 600;
    }}

    /* Equal Dimensions Card Grid Contract (B.9) */
    .sheet-card-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 0.75rem;
    }}
    .sheet-card {{
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 104px;
      padding: 0.85rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
      position: relative;
      text-align: left;
      box-sizing: border-box;
    }}
    .sheet-card:hover {{
      transform: translateY(-2px);
      border-color: var(--accent-slash-border);
      box-shadow: var(--shadow-md);
      background: var(--bg-surface-hover);
    }}
    .sheet-card:focus-visible {{
      outline: 2px solid var(--accent-primary);
      outline-offset: 2px;
    }}
    .sheet-card-top {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 0.5rem;
      margin-bottom: 0.4rem;
    }}
    .sheet-card-name-wrap {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .sheet-card-name-wrap .slash-command-title {{
      font-family: var(--font-mono);
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-primary);
    }}
    .sheet-card-badge {{
      font-size: 0.62rem;
      font-weight: 700;
      padding: 0.1rem 0.35rem;
      border-radius: var(--radius-xs);
      letter-spacing: 0.04em;
    }}
    .sheet-card-goal {{
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 0.25rem;
      line-height: 1.35;
    }}
    .sheet-card-desc {{
      font-size: 0.72rem;
      color: var(--text-secondary);
      line-height: 1.4;
      margin: 0;
    }}
    .bottom-sheet-empty {{
      display: none;
      text-align: center;
      padding: 2.5rem 1rem;
    }}
    .bottom-sheet-empty.visible {{
      display: block;
    }}

    /* Filter Status Bar */
    .filter-status-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.1rem;
      gap: 1rem;
      flex-wrap: wrap;
    }}
    .filter-summary {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }}
    .btn-reset-filters {{
      background: var(--accent-primary-subtle);
      color: var(--accent-primary);
      border: 1px solid var(--accent-primary-border);
      font-size: 0.72rem;
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-xs);
      cursor: pointer;
    }}

    .sort-selector {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      font-size: 0.78rem;
      color: var(--text-secondary);
    }}
    .sort-selector select {{
      background: var(--bg-surface);
      color: var(--text-primary);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-xs);
      padding: 0.25rem 0.55rem;
      font-family: var(--font-sans);
      font-size: 0.78rem;
      cursor: pointer;
    }}

    /* --- SKILLS GRID & LIST VIEW MODES --- */
    .skills-container.layout-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr));
      gap: 1.25rem;
    }}

    .skills-container.layout-list {{
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}

    /* Grid Card Design */
    .skill-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      cursor: pointer;
    }}
    .skill-card:hover {{
      border-color: var(--border-hover);
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }}
    .card-top {{
      padding: 1.1rem 1.25rem 0.75rem;
    }}
    .card-meta-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.65rem;
    }}
    .card-index {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--text-tertiary);
      font-weight: 600;
    }}
    .cat-badge {{
      font-size: 0.68rem;
      font-weight: 600;
      padding: 0.15rem 0.5rem;
      border-radius: var(--radius-full);
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }}
    .cat-design {{
      background: var(--accent-primary-subtle);
      color: var(--accent-primary);
      border: 1px solid var(--accent-primary-border);
    }}
    .cat-code {{
      background: var(--status-info-subtle);
      color: var(--status-info);
      border: 1px solid var(--status-info-border);
    }}
    .cat-delivery {{
      background: var(--status-success-subtle);
      color: var(--status-success);
      border: 1px solid var(--status-success-border);
    }}
    .cat-brand {{
      background: var(--status-warning-subtle);
      color: var(--status-warning);
      border: 1px solid var(--status-warning-border);
    }}
    .cat-ensemble {{
      background: var(--accent-slash-subtle);
      color: var(--accent-slash);
      border: 1px solid var(--accent-slash-border);
    }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.5rem;
      gap: 0.5rem;
    }}
    .skill-name {{
      font-family: var(--font-mono);
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.015em;
    }}
    .badge {{
      font-size: 0.68rem;
      font-weight: 600;
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-xs);
      white-space: nowrap;
    }}
    .badge-accent {{
      background: var(--accent-primary-subtle);
      color: var(--accent-primary);
      border: 1px solid var(--accent-primary-border);
    }}
    .badge-info {{
      background: var(--status-info-subtle);
      color: var(--status-info);
      border: 1px solid var(--status-info-border);
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

    .skill-purpose {{
      font-size: 0.84rem;
      color: var(--text-secondary);
      line-height: 1.45;
      margin-bottom: 0.85rem;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .triggers-preview {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem;
      margin-bottom: 0.85rem;
    }}
    .trigger-pill {{
      font-family: var(--font-mono);
      font-size: 0.7rem;
      background: var(--pill-bg);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-xs);
      cursor: pointer;
      transition: all 0.15s;
    }}
    .trigger-pill:hover {{
      border-color: var(--accent-primary);
      color: var(--accent-primary);
      background: var(--accent-primary-subtle);
    }}

    .card-footer {{
      padding: 0.75rem 1.25rem;
      background: var(--bg-surface-elevated);
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      border-bottom-left-radius: inherit;
      border-bottom-right-radius: inherit;
    }}

    .btn-action {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      font-size: 0.74rem;
      font-weight: 500;
      padding: 0.32rem 0.65rem;
      border-radius: var(--radius-xs);
      cursor: pointer;
      transition: all 0.15s;
    }}
    .btn-action:hover {{
      border-color: var(--accent-primary);
      color: var(--accent-primary);
      background: var(--accent-primary-subtle);
    }}
    .btn-inspect {{
      background: var(--accent-primary-subtle);
      color: var(--accent-primary);
      border-color: var(--accent-primary-border);
      font-weight: 600;
    }}
    .btn-inspect:hover {{
      background: var(--accent-primary);
      color: var(--white);
    }}

    /* List View Item */
    .skill-list-row {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-sm);
      padding: 0.75rem 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      transition: all 0.15s;
      cursor: pointer;
    }}
    .skill-list-row:hover {{
      border-color: var(--border-hover);
      background: var(--bg-surface-hover);
      transform: translateX(2px);
    }}
    .list-row-left {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
      min-width: 220px;
    }}
    .list-skill-name {{
      font-family: var(--font-mono);
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-primary);
    }}
    .list-row-mid {{
      flex: 1;
      min-width: 0;
      font-size: 0.82rem;
      color: var(--text-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .list-row-right {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-shrink: 0;
    }}

    /* --- 3. SLIDE-OVER MASTER-DETAIL INSPECTOR DRAWER --- */
    .drawer-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      z-index: 998;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .drawer-backdrop.active {{
      opacity: 1;
      pointer-events: auto;
    }}

    .detail-drawer {{
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      width: 500px;
      max-width: 92vw;
      background: var(--bg-surface);
      border-left: 1px solid var(--border-subtle);
      box-shadow: var(--shadow-lg);
      z-index: 999;
      transform: translateX(100%);
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .detail-drawer.open {{
      transform: translateX(0);
    }}

    .drawer-header {{
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
      background: var(--bg-surface-elevated);
    }}
    .drawer-title-area {{
      min-width: 0;
    }}
    .drawer-cat-badge {{
      display: inline-block;
      margin-bottom: 0.4rem;
    }}
    .drawer-title {{
      font-family: var(--font-display);
      font-size: 1.2rem;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.02em;
    }}
    .drawer-close-btn {{
      background: transparent;
      border: 1px solid var(--border-subtle);
      color: var(--text-tertiary);
      border-radius: var(--radius-xs);
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1rem;
      transition: all 0.15s;
    }}
    .drawer-close-btn:hover {{
      color: var(--text-primary);
      background: var(--bg-surface);
      border-color: var(--border-hover);
    }}

    .drawer-body {{
      padding: 1.5rem;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .drawer-section-title {{
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-tertiary);
      margin-bottom: 0.45rem;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .drawer-box {{
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 0.85rem;
    }}
    .drawer-box-text {{
      font-size: 0.86rem;
      color: var(--text-primary);
      line-height: 1.55;
    }}

    .drawer-cli-box {{
      background: var(--code-block-bg);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius-sm);
      padding: 0.75rem 0.85rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: var(--accent-primary);
      cursor: pointer;
    }}
    .drawer-cli-code {{
      word-break: break-all;
    }}

    .negative-box {{
      background: var(--status-danger-subtle);
      border: 1px solid var(--status-danger-border);
      color: var(--status-danger);
      padding: 0.75rem;
      border-radius: var(--radius-sm);
      font-size: 0.82rem;
      line-height: 1.45;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--accent-primary-border);
      color: var(--text-primary);
      padding: 0.75rem 1.25rem;
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      font-size: 0.82rem;
      font-weight: 500;
      z-index: 2000;
      opacity: 0;
      transform: translateY(10px);
      pointer-events: none;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .toast.show {{
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }}

    /* Slash View & Table View Styles */
    .slash-grid.layout-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr));
      gap: 1.25rem;
    }}
    .slash-grid.layout-list {{
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}
    .slash-list-row {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-sm);
      padding: 0.75rem 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      transition: all 0.15s;
      cursor: pointer;
    }}
    .slash-list-row:hover {{
      border-color: var(--accent-slash-border);
      background: var(--bg-surface-hover);
      transform: translateX(2px);
    }}
    .slash-command-title {{
      font-family: var(--font-mono);
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--accent-slash);
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }}

    /* Command Palette Modal (Ctrl+K) */
    .cmd-palette-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(4px);
      z-index: 1000;
      opacity: 0;
      visibility: hidden;
      transition: all 0.2s ease;
    }}
    .cmd-palette-backdrop.active {{
      opacity: 1;
      visibility: visible;
    }}
    .cmd-palette-modal {{
      position: fixed;
      top: 15%;
      left: 50%;
      transform: translate(-50%, -20px) scale(0.98);
      width: min(680px, 92vw);
      max-height: 70vh;
      background: var(--bg-surface);
      border: 1px solid var(--border-hover);
      border-radius: var(--radius-lg);
      box-shadow: 0 20px 45px rgba(0,0,0,0.45);
      z-index: 1001;
      display: flex;
      flex-direction: column;
      opacity: 0;
      visibility: hidden;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      overflow: hidden;
    }}
    .cmd-palette-modal.active {{
      opacity: 1;
      visibility: visible;
      transform: translate(-50%, 0) scale(1);
    }}
    .cmd-palette-header {{
      padding: 0.85rem 1.25rem;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      gap: 0.75rem;
      background: var(--bg-surface-elevated);
    }}
    .cmd-palette-input {{
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: var(--text-primary);
      font-size: 0.95rem;
      font-family: inherit;
    }}
    .cmd-palette-close-btn {{
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      font-size: 1.1rem;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
      border-radius: var(--radius-xs);
    }}
    .cmd-palette-close-btn:hover {{
      color: var(--text-primary);
      background: var(--bg-surface-hover);
    }}
    .cmd-palette-body {{
      padding: 0.75rem 1.25rem;
      overflow-y: auto;
      max-height: 48vh;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}
    .cmd-palette-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 0.65rem 0.85rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: var(--card-bg);
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .cmd-palette-item:hover {{
      border-color: var(--accent-slash-border);
      background: var(--accent-slash-subtle);
      transform: translateX(3px);
    }}
    .cmd-palette-item-left {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      min-width: 0;
      flex: 1;
    }}
    .slash-command-title {{
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--accent-slash);
      font-size: 0.9rem;
      white-space: nowrap;
    }}
    .cmd-palette-cmd-desc {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .cmd-palette-footer {{
      padding: 0.65rem 1.25rem;
      border-top: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.75rem;
      color: var(--text-tertiary);
    }}
    .slash-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .slash-card:hover {{
      border-color: var(--accent-slash-border);
      box-shadow: var(--shadow-md);
      transform: translateY(-2px);
    }}
    .slash-header-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }}
    .slash-command-title {{
      font-family: var(--font-mono);
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--accent-slash);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}
    .slash-name {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 0.65rem;
    }}
    .ensemble-chain {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.35rem;
      margin-bottom: 0.85rem;
      background: var(--bg-surface-elevated);
      padding: 0.45rem 0.65rem;
      border-radius: var(--radius-xs);
      border: 1px solid var(--border-subtle);
    }}
    .chain-label {{
      font-size: 0.7rem;
      color: var(--text-tertiary);
      font-weight: 600;
      margin-right: 0.2rem;
    }}
    .chain-pill {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      padding: 0.1rem 0.4rem;
      border-radius: var(--radius-xs);
    }}
    .chain-arrow {{
      color: var(--text-tertiary);
      font-size: 0.75rem;
    }}

    .table-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      overflow-x: auto;
    }}
    .tracking-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
      text-align: left;
    }}
    .tracking-table th {{
      background: var(--bg-surface-elevated);
      color: var(--text-tertiary);
      font-weight: 600;
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--border-subtle);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .tracking-table td {{
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--border-subtle);
      vertical-align: middle;
    }}
    .tracking-table tr:hover td {{
      background: var(--bg-surface-hover);
    }}
    .table-skill-name {{
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--text-primary);
    }}

    @media (max-width: 1024px) {{
      .workspace-body {{
        padding: 1rem 1.25rem 2.5rem;
      }}
    }}

    @media (max-width: 768px) {{
      html, body {{
        overflow-x: hidden;
        max-width: 100vw;
      }}
      .app-layout {{
        overflow-x: hidden;
        max-width: 100vw;
      }}
      .mobile-menu-btn {{
        display: inline-flex;
      }}
      .app-sidebar {{
        position: fixed;
        top: 0;
        left: 0;
        bottom: 0;
        width: 280px !important;
        min-width: 280px !important;
        z-index: 999;
        transform: translateX(-100%);
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 0 25px rgba(0,0,0,0.5);
      }}
      .app-sidebar.mobile-open {{
        transform: translateX(0);
      }}
      .app-main {{
        width: 100%;
        min-width: 0;
      }}
      .workspace-header {{
        padding: 0.75rem 1rem;
        gap: 0.5rem;
      }}
      .header-search-bar {{
        flex: 1 1 180px;
      }}
      .btn-header-cmd span {{
        display: none;
      }}
      .workspace-body {{
        padding: 0.85rem 0.75rem 2.5rem;
      }}
      .btn-action, .layout-btn, .mobile-menu-btn {{
        min-height: 38px;
      }}
    }}

    @media (max-width: 640px) {{
      .bottom-sheet-modal {{
        max-height: 94vh;
        border-radius: 12px 12px 0 0;
      }}
      .bottom-sheet-header {{
        flex-direction: column;
        align-items: stretch;
        gap: 0.6rem;
        padding: 0.75rem 1rem;
      }}
      .bottom-sheet-title-wrap {{
        justify-content: space-between;
      }}
      .bottom-sheet-search-wrap {{
        max-width: 100%;
      }}
      .bottom-sheet-body {{
        padding: 1rem 0.75rem 2rem;
      }}
      .sheet-card-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    @media (max-width: 480px) {{
      .btn-header-cmd {{
        display: none;
      }}
      .btn-palette-launcher {{
        width: 100%;
        justify-content: center;
        margin-left: 0;
      }}
      .layout-btn span {{
        display: none;
      }}
    }}
  </style>
</head>
<body>

  <div class="app-layout" id="appLayout">

    <!-- 1. LEFT COLLAPSIBLE SIDEBAR DOCK -->
    <aside class="app-sidebar" id="appSidebar">
      <!-- Brand & Workspace Header -->
      <div class="sidebar-brand">
        <div class="brand-main">
          <div class="brand-icon">
            <svg class="svg-icon svg-icon-lg" viewBox="0 0 24 24"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
          </div>
          <div class="brand-info">
            <div class="brand-title">Goku Dev Skills</div>
            <div class="brand-sub">Kokpit <span class="version-tag">v{pkg_version}</span></div>
          </div>
        </div>
        <button class="sidebar-toggle-btn" id="sidebarToggleBtn" onclick="toggleSidebar()" title="Menüyü Daralt / Genişlet (Kısayol: [)">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>
        </button>
      </div>

      <!-- Primary Navigation (View Tabs) -->
      <div class="sidebar-section">
        <div class="sidebar-section-title">Görünüm Modu</div>
        <nav class="sidebar-nav">
          <button class="nav-btn active" id="navSkills" onclick="switchView('skills')">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
            <span class="nav-label">Tüm Beceriler</span>
            <span class="nav-badge">{len(skills)}</span>
          </button>
          <button class="nav-btn" id="navSlash" onclick="switchView('slash')">
            <svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
            <span class="nav-label">Slash Komutları</span>
            <span class="nav-badge badge-slash">{len(SLASH_COMMANDS)}</span>
          </button>
          <button class="nav-btn" id="navTable" onclick="switchView('table')">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M3 9h18"></path><path d="M3 15h18"></path><path d="M9 3v18"></path></svg>
            <span class="nav-label">Takip Tablosu</span>
            <span class="nav-badge">Özet</span>
          </button>
        </nav>
      </div>

      <!-- Categories Rail -->
      <div class="sidebar-section">
        <div class="sidebar-section-title">Kategoriler</div>
        <div class="category-list">
          <button class="sidebar-cat-btn active" data-cat="all" onclick="setCategoryFilter('all', this)">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline></svg>
            <span class="cat-label">Tümü</span>
            <span class="cat-count">({len(skills)})</span>
          </button>
          {sidebar_cat_items}
        </div>
      </div>

      <!-- Quick Preset Filters -->
      <div class="sidebar-section">
        <div class="sidebar-section-title">Hızlı Filtreler</div>
        <div class="quick-preset-chips">
          <button class="preset-pill" onclick="quickFilterPreset('core')">
            <span>Goku Çekirdek</span>
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
          <button class="preset-pill" onclick="quickFilterPreset('design-trio')">
            <span>Tasarım Üçlüsü</span>
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
          <button class="preset-pill" onclick="quickFilterPreset('quality')">
            <span>Kalite & Test</span>
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
          <button class="preset-pill" onclick="quickFilterPreset('zero-config')">
            <span>Sıfır-Ayar</span>
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
        </div>
      </div>

      <!-- Sidebar Footer -->
      <div class="sidebar-footer">
        <div class="sidebar-stats">
          <div class="stat-row">
            <span>Aktif Beceriler:</span>
            <span class="stat-val">{len(skills)}</span>
          </div>
          <div class="stat-row">
            <span>Slash Protokoller:</span>
            <span class="stat-val">{len(SLASH_COMMANDS)}</span>
          </div>
        </div>
        <button class="theme-toggle-btn" id="themeToggleBtn" onclick="toggleTheme()" title="Temayı Değiştir (Kısayol: T)">
          <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
          <span id="themeToggleLabel">Açık Tema</span>
        </button>
      </div>
    </aside>

    <!-- 2. MAIN WORKSPACE -->
    <main class="app-main">
      <!-- Top Workspace Command Header -->
      <header class="workspace-header">
        <button class="mobile-menu-btn" id="mobileMenuBtn" onclick="toggleMobileDrawer()" aria-label="Menüyü Aç/Kapat" title="Menü">
          <svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        </button>
        <div class="header-search-bar">
          <svg class="svg-icon search-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" class="search-input" id="searchInput" placeholder="Skill adı, tetikleyici, komut, kural ara... (Kısayol: / veya Ctrl+K)" oninput="filterAll()">
          <button class="btn-clear-search" id="btnClearSearch" onclick="clearSearch()" title="Aramayı Temizle">✕</button>
          <span class="kbd-shortcut">/</span>
        </div>

        <div class="header-controls">
          <div class="layout-toggle-group" role="group" aria-label="Görünüm Seçici">
            <button class="layout-btn active" id="btnLayoutGrid" onclick="setLayoutMode('grid')" aria-pressed="true" title="Izgara Görünümü (Kısayol: G)">
              <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
              <span>Izgara</span>
            </button>
            <button class="layout-btn" id="btnLayoutList" onclick="setLayoutMode('list')" aria-pressed="false" title="Kompakt Liste Görünümü (Kısayol: L)">
              <svg class="svg-icon" viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
              <span>Liste</span>
            </button>
          </div>

          <button class="btn-header-cmd" onclick="copyToClipboard('npx goku-dev-skills update', 'Güncelleme komutu kopyalandı!')" title="Kopyalamak için tıkla">
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
            <span>npx goku-dev-skills update</span>
          </button>
        </div>
      </header>

      <!-- Workspace Body -->
      <div class="workspace-body">
        <!-- Quick Slash Ribbon (Taşmayan Yerleşim - B.9 Adaptive Action Hub) -->
        <div class="quick-slash-ribbon" role="region" aria-label="Oturum Slash Komutları" id="quickSlashRibbon">
          <!-- Çözüm 1: Tek Tıklama Grup & Hub Başlatıcı Butonu -->
          <button class="btn-hub-launcher" id="btnOpenSlashHub" onclick="openBottomSheetHub(this)" title="Tüm komutları alttan açılan kart hub'ında gör">
            <svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
            <span>Oturum Komutları</span>
            <span class="hub-launcher-count" id="hubLauncherCount">{len(SLASH_COMMANDS)}</span>
          </button>

          <!-- Çözüm 2: Alan Genişliğine Göre Sığan Önizleme Çipleri -->
          <div class="slash-preview-strip" id="slashPreviewStrip">
            {quick_slash_pills}
          </div>

          <!-- Çözüm 2: Sığmayanlar İçin '... (+K)' Taşma Butonu -->
          <button class="btn-ribbon-more" id="btnRibbonMore" onclick="openBottomSheetHub(this)" title="Daha fazla komut göster">
            <span>...</span>
            <span id="ribbonMoreCount">+7</span>
          </button>

          <!-- Masaüstü Hızlı Komut Paleti (Ctrl+K) -->
          <button class="btn-palette-launcher" id="btnOpenCmdPalette" onclick="openCommandPalette()" title="Tüm komutları modal paletinde gör ve ara (Kısayol: Ctrl+K)">
            <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
            <span>Komut Paleti ({len(SLASH_COMMANDS)})</span>
            <span class="palette-kbd-badge">Ctrl+K</span>
          </button>
        </div>

        <!-- Filter Status Bar -->
        <div class="filter-status-bar">
          <div class="filter-summary" id="filterSummary">
            <span>Tüm beceriler listeleniyor ({len(skills)} beceri)</span>
          </div>

          <div class="sort-selector">
            <label for="sortSelect">Sırala:</label>
            <select id="sortSelect" onchange="setSort(this.value)">
              <option value="name-asc">İsim (A → Z)</option>
              <option value="name-desc">İsim (Z → A)</option>
              <option value="category">Kategoriye Göre</option>
              <option value="triggers">Tetikleyici Zenginliği</option>
            </select>
          </div>
        </div>

        <!-- VIEW 1: SKILLS CONTAINER (Grid / List) -->
        <div id="viewSkillsSection">
          <div class="skills-container layout-grid" id="skillsContainer"></div>
        </div>

        <!-- VIEW 2: SLASH COMMANDS GRID -->
        <div id="viewSlashSection" style="display:none;">
          <div class="slash-grid" id="slashGrid"></div>
        </div>

        <!-- VIEW 3: FULL TRACKING TABLE -->
        <div id="viewTableSection" style="display:none;">
          <div class="table-card">
            <table class="tracking-table">
              <thead>
                <tr>
                  <th style="width: 45px;">#</th>
                  <th style="width: 170px;">Beceri Adı & Kategori</th>
                  <th>Görev & Özellikler</th>
                  <th style="width: 280px;">Örnek Tetikleyiciler</th>
                  <th style="width: 180px;">Sözleşme / Dosya</th>
                  <th style="width: 120px; text-align: right;">Eylem</th>
                </tr>
              </thead>
              <tbody id="skillsTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </main>

    <!-- 3. SLIDE-OVER MASTER-DETAIL INSPECTOR DRAWER -->
    <div class="drawer-backdrop" id="drawerBackdrop" onclick="closeDrawer()"></div>
    <aside class="detail-drawer" id="detailDrawer">
      <div class="drawer-header">
        <div class="drawer-title-area">
          <div class="drawer-cat-badge" id="drawerCatBadge"></div>
          <h2 class="drawer-title" id="drawerTitle">Beceri Detayı</h2>
        </div>
        <button class="drawer-close-btn" onclick="closeDrawer()" title="Kapat (Kısayol: Esc)">✕</button>
      </div>
      <div class="drawer-body" id="drawerBody"></div>
    </aside>

  </div>

  <!-- 4. COMMAND PALETTE MODAL (Ctrl+K) -->
  <div class="cmd-palette-backdrop" id="cmdPaletteBackdrop" onclick="closeCommandPalette()"></div>
  <div class="cmd-palette-modal" id="cmdPaletteModal" role="dialog" aria-modal="true" aria-labelledby="cmdPaletteTitle">
    <div class="cmd-palette-header">
      <svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
      <input type="text" class="cmd-palette-input" id="cmdPaletteInput" placeholder="Slash komut ara... (/plan, /fix-bug, /goal, /commitx...)" oninput="filterCommandPalette(this.value)" autocomplete="off">
      <button class="cmd-palette-close-btn" onclick="closeCommandPalette()" title="Kapat (Esc)">✕</button>
    </div>
    <div class="cmd-palette-body" id="cmdPaletteList"></div>
    <div class="cmd-palette-footer">
      <span>💡 Bir komuta tıklayarak komutu veya örnek promptunu panoya kopyalayabilirsiniz.</span>
      <span class="palette-kbd-badge">Esc ile Kapat</span>
    </div>
  </div>

  <!-- 5. ALTTAN AÇILAN KART HUB'I (B.9 / Çözüm 1 & 2) -->
  <div class="bottom-sheet-backdrop" id="bottomSheetBackdrop" onclick="closeBottomSheetHub()" aria-hidden="true"></div>
  <div class="bottom-sheet-modal" id="bottomSheetHub" role="dialog" aria-modal="true" aria-labelledby="bottomSheetTitle" aria-hidden="true">
    <div class="bottom-sheet-handle-wrap" onclick="closeBottomSheetHub()">
      <div class="bottom-sheet-handle"></div>
    </div>
    <div class="bottom-sheet-header">
      <div class="bottom-sheet-title-wrap">
        <svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
        <h2 class="bottom-sheet-title" id="bottomSheetTitle">Oturum Komutları Hub'ı</h2>
        <span class="bottom-sheet-badge" id="bottomSheetBadge">{len(SLASH_COMMANDS)} Komut</span>
      </div>
      <div class="bottom-sheet-search-wrap">
        <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input type="text" id="sheetSearchInput" class="bottom-sheet-search-input" placeholder="Komut veya açıklama ara (örn: /plan, /fix)..." oninput="filterBottomSheetCards(this.value)" autocomplete="off" spellcheck="false">
      </div>
      <button class="bottom-sheet-btn-close" id="btnCloseBottomSheet" onclick="closeBottomSheetHub()" aria-label="Paneli Kapat" title="Kapat (Esc)">
        <svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
    <div class="bottom-sheet-body" id="bottomSheetBody">
      {bottom_sheet_panels_html}
      <div class="bottom-sheet-empty" id="bottomSheetEmpty">
        <p style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem;">Eşleşen komut bulunamadı</p>
        <p style="font-size: 0.8rem; color: var(--text-tertiary); margin: 0;">Farklı bir arama terimi deneyebilirsiniz.</p>
      </div>
    </div>
  </div>

  <!-- Mobile Drawer Backdrop -->
  <div class="mobile-drawer-backdrop" id="mobileDrawerBackdrop" onclick="closeMobileDrawer()"></div>

  <!-- Toast Notification Container -->
  <div class="toast" id="toast">
    <svg class="svg-icon" style="color:var(--status-success)" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
    <span id="toastMsg">Panoya kopyalandı!</span>
  </div>

  <script>
    const allSkills = {skills_json};
    const allSlashCommands = {slash_commands_json};

    let activeView = 'skills';
    let currentCategory = 'all';
    let currentConfig = 'all';
    let currentSearch = '';
    let currentSort = 'name-asc';
    let currentLayout = localStorage.getItem('agent_catalog_layout') || 'grid';

    const categoryBadgeClassMap = {json.dumps(cat_badges)};

    const SVG_COPY = `<svg class="svg-icon" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
    const SVG_TERMINAL = `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>`;
    const SVG_INSPECT = `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>`;
    const SVG_ALERT = `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
    const SVG_SETTINGS = `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`;
    const SVG_SPARKLES = `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>`;
    const SVG_SLASH = `<svg class="svg-icon svg-slash" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`;
    const SVG_TARGET = `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>`;
    const SVG_MOON = `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
    const SVG_SUN = `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;

    function switchView(view) {{
      activeView = view;
      document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById(view === 'skills' ? 'navSkills' : (view === 'slash' ? 'navSlash' : 'navTable'));
      if (activeBtn) activeBtn.classList.add('active');

      document.getElementById('viewSkillsSection').style.display = view === 'skills' ? 'block' : 'none';
      document.getElementById('viewSlashSection').style.display = view === 'slash' ? 'block' : 'none';
      document.getElementById('viewTableSection').style.display = view === 'table' ? 'block' : 'none';

      // Kural A: Takip tablosu modunda izgara/liste anahtarı yanıltıcı olmaması için gizlenir
      const layoutGroup = document.querySelector('.layout-toggle-group');
      if (layoutGroup) {{
        layoutGroup.style.display = view === 'table' ? 'none' : 'inline-flex';
      }}

      // Mobilde menü açıksa kapat
      closeMobileDrawer();

      renderAll();
    }}

    function setLayoutMode(mode) {{
      currentLayout = mode;
      localStorage.setItem('agent_catalog_layout', mode);
      
      const btnGrid = document.getElementById('btnLayoutGrid');
      const btnList = document.getElementById('btnLayoutList');
      if (btnGrid) {{
        btnGrid.classList.toggle('active', mode === 'grid');
        btnGrid.setAttribute('aria-pressed', mode === 'grid' ? 'true' : 'false');
      }}
      if (btnList) {{
        btnList.classList.toggle('active', mode === 'list');
        btnList.setAttribute('aria-pressed', mode === 'list' ? 'true' : 'false');
      }}

      const skillsCont = document.getElementById('skillsContainer');
      if (skillsCont) {{
        skillsCont.className = 'skills-container ' + (mode === 'grid' ? 'layout-grid' : 'layout-list');
      }}
      const slashCont = document.getElementById('slashGrid');
      if (slashCont) {{
        slashCont.className = 'slash-grid ' + (mode === 'grid' ? 'layout-grid' : 'layout-list');
      }}

      renderAll();
    }}

    function toggleSidebar() {{
      const sidebar = document.getElementById('appSidebar');
      sidebar.classList.toggle('collapsed');
      const isCollapsed = sidebar.classList.contains('collapsed');
      localStorage.setItem('agent_sidebar_collapsed', isCollapsed ? 'true' : 'false');
    }}

    function quickSelectSlash(cmdName) {{
      switchView('slash');
      const searchInput = document.getElementById('searchInput');
      searchInput.value = cmdName;
      currentSearch = cmdName;
      renderAll();
      copyToClipboard(cmdName, `Slash komutu kopyalandı: ${{cmdName}}`);
    }}

    function quickFilterPreset(preset) {{
      if (preset === 'core') {{
        currentSearch = 'goku';
      }} else if (preset === 'design-trio') {{
        currentCategory = 'Tasarım & UI';
        currentSearch = '';
      }} else if (preset === 'quality') {{
        currentCategory = 'Teslimat & Kalite';
        currentSearch = '';
      }} else if (preset === 'zero-config') {{
        currentConfig = 'Sıfır-Ayar';
        currentSearch = '';
      }}
      document.getElementById('searchInput').value = currentSearch;
      switchView('skills');
      renderAll();
    }}

    function setSort(val) {{
      currentSort = val;
      renderAll();
    }}

    function renderAll() {{
      const query = currentSearch.toLowerCase().trim();

      // Filter skills
      let filteredSkills = allSkills.filter(s => {{
        const matchCategory = (currentCategory === 'all' || s.category === currentCategory);
        const matchConfig = (
          currentConfig === 'all' ||
          s.config_status.includes(currentConfig) ||
          (currentConfig === 'Sözleşme' && (
            s.config_status.includes('Sözleşme') ||
            s.config_status.includes('Kapı') ||
            s.config_status.includes('Doğrulama') ||
            s.config_status.includes('Orkestratör')
          ))
        );
        const matchSearch = !query || s.search_index.includes(query);
        return matchCategory && matchConfig && matchSearch;
      }});

      // Sort skills
      if (currentSort === 'name-asc') {{
        filteredSkills.sort((a, b) => a.name.localeCompare(b.name));
      }} else if (currentSort === 'name-desc') {{
        filteredSkills.sort((a, b) => b.name.localeCompare(a.name));
      }} else if (currentSort === 'category') {{
        filteredSkills.sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));
      }} else if (currentSort === 'triggers') {{
        filteredSkills.sort((a, b) => b.triggers.length - a.triggers.length);
      }}

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
          ? `<span>Tüm beceriler listeleniyor (${{allSkills.length}} beceri)</span>`
          : `<span><strong>${{filteredSkills.length}}</strong> / ${{allSkills.length}} beceri filtrelendi</span>
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

      renderSkillItems(filteredSkills);
      renderSlashCards(filteredSlash);
      renderTable(filteredSkills, filteredSlash);
    }}

    function openDrawer(skillName) {{
      const s = allSkills.find(item => item.name === skillName);
      if (!s) return;

      const catClass = categoryBadgeClassMap[s.category] || 'cat-design';
      document.getElementById('drawerCatBadge').innerHTML = `<span class="cat-badge ${{catClass}}">${{escapeHtml(s.category)}}</span>`;
      document.getElementById('drawerTitle').innerText = s.name;

      const triggersHtml = s.triggers.map(t => 
        `<span class="trigger-pill" data-trigger="${{escapeHtml(t)}}" title="Kopyalamak için tıkla" onclick="copyTriggerFromEl(this)">"${{escapeHtml(t)}}"</span>`
      ).join('');

      const featuresHtml = (s.features || []).map(f => 
        `<div style="font-size:0.8rem;color:var(--text-secondary);display:flex;align-items:center;gap:0.4rem;">${{SVG_SPARKLES}} ${{escapeHtml(f)}}</div>`
      ).join('');

      const body = document.getElementById('drawerBody');
      body.innerHTML = `
        <div>
          <div class="drawer-section-title">Durum & Sözleşme</div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge ${{s.badge_class}}">${{escapeHtml(s.config_status)}}</span>
            <span class="drawer-file-name" style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-tertiary);">${{escapeHtml(s.config_file)}}</span>
          </div>
        </div>

        <div>
          <div class="drawer-section-title">Amaç & Mühendislik Felsefesi</div>
          <div class="drawer-box">
            <p class="drawer-box-text">${{escapeHtml(s.purpose)}}</p>
          </div>
        </div>

        ${{s.features && s.features.length ? `
          <div>
            <div class="drawer-section-title">Zanaat Tabanı & Temel Özellikler</div>
            <div class="drawer-box" style="display:flex;flex-direction:column;gap:0.35rem;">
              ${{featuresHtml}}
            </div>
          </div>
        ` : ''}}

        <div>
          <div class="drawer-section-title">Tetikleyiciler (Triggers) — Kopyalamak için tıkla</div>
          <div style="display:flex;flex-wrap:wrap;gap:0.35rem;">
            ${{triggersHtml || '<span style="color:var(--text-tertiary);font-size:0.75rem">Genel yönlendirici veya davranışsal</span>'}}
          </div>
        </div>

        ${{s.negative ? `
          <div>
            <div class="drawer-section-title">${{SVG_ALERT}} Kapsam Sınırı (Tetiklenmez)</div>
            <div class="negative-box">${{escapeHtml(s.negative)}}</div>
          </div>
        ` : ''}}

        ${{s.cli_cmd ? `
          <div>
            <div class="drawer-section-title">${{SVG_TERMINAL}} Tek Tıkla CLI Komutu</div>
            <div class="drawer-cli-box" onclick="copySkillCliByName('${{escapeHtml(s.name)}}')" title="Kopyalamak için tıkla">
              <span class="drawer-cli-code">${{escapeHtml(s.cli_cmd)}}</span>
              ${{SVG_COPY}}
            </div>
          </div>
        ` : ''}}

        ${{s.config_snippet ? `
          <div>
            <div class="drawer-section-title">${{SVG_SETTINGS}} Kullanım & Config Rehberi</div>
            <div class="drawer-box" style="background:var(--code-block-bg);position:relative;">
              <button class="btn-action" style="position:absolute;top:0.5rem;right:0.5rem;padding:0.2rem 0.5rem;font-size:0.7rem;" onclick="copySkillConfigByName('${{escapeHtml(s.name)}}')">Kopyala</button>
              <pre style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-secondary);overflow-x:auto;padding-top:1.5rem;"><code>${{escapeHtml(s.config_snippet)}}</code></pre>
            </div>
          </div>
        ` : ''}}

        <div>
          <div class="drawer-section-title">${{SVG_COPY}} Örnek Prompt</div>
          <div class="drawer-box" style="cursor:pointer;" onclick="copySkillPromptByName('${{escapeHtml(s.name)}}')" title="Kopyalamak için tıkla">
            <p class="drawer-box-text" style="font-style:italic;">"${{escapeHtml(s.sample_prompt)}}"</p>
          </div>
        </div>
      `;

      document.getElementById('drawerBackdrop').classList.add('active');
      document.getElementById('detailDrawer').classList.add('open');
    }}

    function closeDrawer() {{
      document.getElementById('drawerBackdrop').classList.remove('active');
      document.getElementById('detailDrawer').classList.remove('open');
    }}

    function renderSkillItems(filtered) {{
      const container = document.getElementById('skillsContainer');
      container.innerHTML = '';

      if (filtered.length === 0) {{
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--text-secondary);">
            <h3 style="font-size: 1.1rem; color: var(--text-primary); margin-bottom: 0.5rem;">Sonuç Bulunamadı</h3>
            <p style="font-size: 0.85rem;">Arama kriterlerine veya filtrelere uygun skill bulunamadı.</p>
            <button class="btn-action" style="margin-top:1rem" onclick="resetFilters()">Filtreleri Sıfırla</button>
          </div>
        `;
        return;
      }}

      if (currentLayout === 'grid') {{
        filtered.forEach((s, idx) => {{
          const card = document.createElement('div');
          card.className = 'skill-card';
          card.setAttribute('data-name', s.name);
          card.setAttribute('data-category', s.category);
          card.onclick = (e) => {{
            if (!e.target.closest('button') && !e.target.closest('.trigger-pill')) {{
              openDrawer(s.name);
            }}
          }};

          const triggersPreview = s.triggers.slice(0, 3).map(t => 
            `<span class="trigger-pill" data-trigger="${{escapeHtml(t)}}" title="Kopyala" onclick="copyTriggerFromEl(this)">"${{escapeHtml(t)}}"</span>`
          ).join('') + (s.triggers.length > 3 ? `<span class="stat-val" style="font-size:0.68rem;color:var(--text-tertiary);align-self:center;">+${{s.triggers.length - 3}}</span>` : '');

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

              <p class="skill-purpose">${{escapeHtml(s.purpose)}}</p>

              <div class="triggers-preview">${{triggersPreview || '<span style="color:var(--text-tertiary);font-size:0.72rem">Genel yönlendirici</span>'}}</div>
            </div>

            <div class="card-footer">
              <button class="btn-action btn-inspect" onclick="openDrawer('${{escapeHtml(s.name)}}')">
                ${{SVG_INSPECT}} İncele
              </button>
              <div style="display:flex;gap:0.35rem;">
                <button class="btn-action" onclick="copySkillPromptByName('${{escapeHtml(s.name)}}')" title="Örnek Prompt Kopyala">
                  ${{SVG_COPY}} Prompt
                </button>
                ${{s.cli_cmd ? `
                  <button class="btn-action" onclick="copySkillCliByName('${{escapeHtml(s.name)}}')" title="CLI Komutu Kopyala">
                    ${{SVG_TERMINAL}} CLI
                  </button>
                ` : ''}}
              </div>
            </div>
          `;
          container.appendChild(card);
        }});
      }} else {{
        // LIST VIEW
        filtered.forEach((s, idx) => {{
          const row = document.createElement('div');
          row.className = 'skill-list-row';
          row.setAttribute('data-name', s.name);
          row.onclick = (e) => {{
            if (!e.target.closest('button')) {{
              openDrawer(s.name);
            }}
          }};

          const catClass = categoryBadgeClassMap[s.category] || 'cat-design';
          const numPadded = String(idx + 1).padStart(2, '0');

          row.innerHTML = `
            <div class="list-row-left">
              <span class="card-index">#${{numPadded}}</span>
              <span class="list-skill-name">${{escapeHtml(s.name)}}</span>
              <span class="cat-badge ${{catClass}}" style="font-size:0.65rem;padding:0.1rem 0.4rem;">${{escapeHtml(s.category)}}</span>
            </div>

            <div class="list-row-mid">
              ${{escapeHtml(s.purpose)}}
            </div>

            <div class="list-row-right">
              <span class="badge ${{s.badge_class}}" style="font-size:0.65rem;">${{escapeHtml(s.config_status)}}</span>
              <button class="btn-action btn-inspect" style="padding:0.25rem 0.5rem;font-size:0.72rem;" onclick="openDrawer('${{escapeHtml(s.name)}}')">
                ${{SVG_INSPECT}} İncele
              </button>
              <button class="btn-action" style="padding:0.25rem 0.5rem;font-size:0.72rem;" onclick="copySkillPromptByName('${{escapeHtml(s.name)}}')">
                ${{SVG_COPY}}
              </button>
            </div>
          `;
          container.appendChild(row);
        }});
      }}
    }}

    function renderSlashCards(filtered) {{
      const grid = document.getElementById('slashGrid');
      grid.innerHTML = '';

      if (filtered.length === 0) {{
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--text-secondary);">
            <h3 style="font-size: 1.1rem; color: var(--text-primary); margin-bottom: 0.5rem;">Sonuç Bulunamadı</h3>
            <p style="font-size: 0.85rem;">Arama kriterlerine uygun oturum slash komutu bulunamadı.</p>
            <button class="btn-action" style="margin-top:1rem" onclick="resetFilters()">Filtreleri Sıfırla</button>
          </div>
        `;
        return;
      }}

      if (currentLayout === 'grid') {{
        filtered.forEach((cmd, cIdx) => {{
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

              <div style="font-size:0.8rem;font-weight:600;color:var(--accent-slash);margin-bottom:0.5rem;display:flex;align-items:center;gap:0.35rem;">
                ${{SVG_TARGET}} ${{escapeHtml(cmd.goal)}}
              </div>

              <p class="skill-purpose" style="margin-bottom:0.75rem;">${{escapeHtml(cmd.description)}}</p>

              <div style="font-size:0.72rem;font-weight:700;color:var(--text-tertiary);margin-bottom:0.35rem;text-transform:uppercase;">Protokol Akışı</div>
              <div style="font-size:0.75rem;color:var(--text-secondary);background:var(--bg-surface-elevated);padding:0.45rem 0.65rem;border-radius:var(--radius-xs);">${{escapeHtml(cmd.protocol)}}</div>
            </div>

            <div class="card-footer">
              <button class="btn-action" style="border-color:var(--accent-slash-border);color:var(--accent-slash);" onclick="copySlashCommand('${{escapeHtml(cmd.command)}}')">
                ${{SVG_SLASH}} ${{cmd.command}}
              </button>
              <button class="btn-action" onclick="copySlashPromptByName('${{escapeHtml(cmd.command)}}')">
                ${{SVG_COPY}} Örnek Prompt
              </button>
            </div>
          `;
          grid.appendChild(card);
        }});
      }} else {{
        // LIST VIEW FOR SLASH COMMANDS
        filtered.forEach((cmd, cIdx) => {{
          const row = document.createElement('div');
          row.className = 'slash-list-row';
          const numPadded = String(cIdx + 1).padStart(2, '0');

          row.innerHTML = `
            <div class="list-row-left">
              <span class="card-index">#${{numPadded}}</span>
              <span class="list-slash-cmd">${{SVG_SLASH}} ${{escapeHtml(cmd.command)}}</span>
              <span class="badge ${{cmd.badge_class}}" style="font-size:0.65rem;">${{escapeHtml(cmd.badge)}}</span>
            </div>

            <div class="list-row-mid">
              <span style="font-weight:600;color:var(--text-primary);margin-right:0.35rem;">${{escapeHtml(cmd.name)}}:</span>
              <span>${{escapeHtml(cmd.description)}}</span>
              <span style="font-size:0.72rem;color:var(--text-tertiary);margin-left:0.5rem;">[${{escapeHtml(cmd.skills.join(' → '))}}]</span>
            </div>

            <div class="list-row-right">
              <button class="btn-action" style="padding:0.25rem 0.5rem;font-size:0.72rem;border-color:var(--accent-slash-border);color:var(--accent-slash);" onclick="copySlashCommand('${{escapeHtml(cmd.command)}}')">
                ${{SVG_SLASH}} ${{escapeHtml(cmd.command)}}
              </button>
              <button class="btn-action" style="padding:0.25rem 0.5rem;font-size:0.72rem;" onclick="copySlashPromptByName('${{escapeHtml(cmd.command)}}')">
                ${{SVG_COPY}} Prompt
              </button>
            </div>
          `;
          grid.appendChild(row);
        }});
      }}
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

          const triggersHtml = s.triggers.slice(0, 4).map(t => 
            `<span class="trigger-pill" style="font-size:0.7rem;" data-trigger="${{escapeHtml(t)}}" title="Kopyalamak için tıkla" onclick="copyTriggerFromEl(this)">"${{escapeHtml(t)}}"</span>`
          ).join('') + (s.triggers.length > 4 ? `<span style="font-size:0.7rem;color:var(--text-tertiary);font-variant-numeric:tabular-nums;">+${{s.triggers.length - 4}}</span>` : '');

          const catClass = categoryBadgeClassMap[s.category] || 'cat-design';
          const numPadded = String(idx + 1).padStart(2, '0');

          tr.innerHTML = `
            <td style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-tertiary);font-weight:600;font-variant-numeric:tabular-nums;">#${{numPadded}}</td>
            <td>
              <div style="display:flex;flex-direction:column;gap:0.25rem;">
                <span class="table-skill-name">${{escapeHtml(s.name)}}</span>
                <span class="cat-badge ${{catClass}}" style="display:inline-block;width:max-content;font-size:0.65rem;padding:0.1rem 0.4rem;">${{escapeHtml(s.category)}}</span>
              </div>
            </td>
            <td>
              <div style="font-size:0.82rem;color:var(--text-primary);line-height:1.45;">${{escapeHtml(s.purpose)}}</div>
            </td>
            <td>
              <div style="display:flex;flex-wrap:wrap;gap:0.25rem;">${{triggersHtml || '<span style="color:var(--text-tertiary);font-size:0.72rem;">Genel yönlendirici</span>'}}</div>
            </td>
            <td>
              <span class="badge ${{s.badge_class}}" style="font-size:0.68rem;">${{escapeHtml(s.config_status)}}</span>
              <div class="drawer-file-name" style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-tertiary);margin-top:0.2rem;">${{escapeHtml(s.config_file)}}</div>
            </td>
            <td style="text-align: right;">
              <button class="btn-action btn-inspect" style="padding:0.25rem 0.5rem;font-size:0.72rem;" onclick="openDrawer('${{escapeHtml(s.name)}}')">
                ${{SVG_INSPECT}}
              </button>
            </td>
          `;
          tbody.appendChild(tr);
        }});
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
      currentSort = 'name-asc';
      document.getElementById('searchInput').value = '';
      document.getElementById('sortSelect').value = 'name-asc';
      document.querySelectorAll('.sidebar-cat-btn').forEach(b => {{
        b.classList.toggle('active', b.getAttribute('data-cat') === 'all');
      }});
      renderAll();
    }}

    function setCategoryFilter(cat, btn) {{
      currentCategory = cat;
      document.querySelectorAll('.sidebar-cat-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderAll();
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
      }}, 2200);
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
      if (s && s.config_snippet) copyToClipboard(s.config_snippet, 'Config rehberi kopyalandı: ' + s.name);
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

    function escapeHtml(str) {{
      if (!str) return '';
      return str.replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
    }}

    // Bottom-Sheet Card Hub Functions (B.9 / Çözüm 1 & 2)
    let activeSheetOpener = null;

    function openBottomSheetHub(triggerEl) {{
      activeSheetOpener = triggerEl || document.activeElement;
      const backdrop = document.getElementById('bottomSheetBackdrop');
      const sheet = document.getElementById('bottomSheetHub');
      const search = document.getElementById('sheetSearchInput');
      if (!backdrop || !sheet) return;

      backdrop.classList.add('active');
      sheet.classList.add('active');
      backdrop.setAttribute('aria-hidden', 'false');
      sheet.setAttribute('aria-hidden', 'false');

      if (search) {{
        search.value = '';
        filterBottomSheetCards('');
        setTimeout(() => search.focus(), 60);
      }}
    }}

    function closeBottomSheetHub() {{
      const backdrop = document.getElementById('bottomSheetBackdrop');
      const sheet = document.getElementById('bottomSheetHub');
      if (backdrop) {{
        backdrop.classList.remove('active');
        backdrop.setAttribute('aria-hidden', 'true');
      }}
      if (sheet) {{
        sheet.classList.remove('active');
        sheet.setAttribute('aria-hidden', 'true');
      }}
      if (activeSheetOpener && typeof activeSheetOpener.focus === 'function') {{
        activeSheetOpener.focus();
      }}
    }}

    function filterBottomSheetCards(query) {{
      const q = (query || '').toLowerCase().trim();
      const sheet = document.getElementById('bottomSheetHub');
      if (!sheet) return;
      const panels = sheet.querySelectorAll('.sheet-domain-panel');
      const emptyEl = document.getElementById('bottomSheetEmpty');
      let totalMatches = 0;

      panels.forEach(panel => {{
        const cards = panel.querySelectorAll('.sheet-card');
        let panelMatches = 0;
        cards.forEach(card => {{
          const cmd = card.dataset.cmd || '';
          const name = card.dataset.name || '';
          const desc = card.dataset.desc || '';
          const goal = card.dataset.goal || '';
          const match = !q || cmd.includes(q) || name.includes(q) || desc.includes(q) || goal.includes(q);
          if (match) {{
            card.style.display = 'flex';
            panelMatches++;
            totalMatches++;
          }} else {{
            card.style.display = 'none';
          }}
        }});
        if (panelMatches === 0) {{
          panel.style.display = 'none';
        }} else {{
          panel.style.display = 'flex';
          const countEl = panel.querySelector('.sheet-domain-count');
          if (countEl) countEl.textContent = '(' + panelMatches + ')';
        }}
      }});

      if (emptyEl) {{
        if (totalMatches === 0) {{
          emptyEl.classList.add('visible');
        }} else {{
          emptyEl.classList.remove('visible');
        }}
      }}
    }}

    function selectFromBottomSheet(cmd) {{
      closeBottomSheetHub();
      quickSelectSlash(cmd);
    }}

    function updateSlashRibbonPreview() {{
      const ribbon = document.getElementById('quickSlashRibbon');
      const launcher = document.getElementById('btnOpenSlashHub');
      const palette = document.getElementById('btnOpenCmdPalette');
      const previewStrip = document.getElementById('slashPreviewStrip');
      const moreBtn = document.getElementById('btnRibbonMore');
      const moreCount = document.getElementById('ribbonMoreCount');
      if (!ribbon || !previewStrip || !moreBtn) return;

      const ribbonWidth = ribbon.clientWidth;
      const launcherWidth = launcher ? launcher.offsetWidth : 160;
      const paletteWidth = (palette && palette.offsetParent) ? palette.offsetWidth : 0;
      const moreReserved = 80;
      const available = ribbonWidth - launcherWidth - paletteWidth - moreReserved - 32;

      previewStrip.innerHTML = '';
      if (available <= 50) {{
        moreBtn.style.display = 'inline-flex';
        if (moreCount) moreCount.textContent = '+' + allSlashCommands.length;
        return;
      }}

      let used = 0;
      let count = 0;
      for (let i = 0; i < allSlashCommands.length; i++) {{
        const cmd = allSlashCommands[i];
        const approxWidth = (cmd.command.length * 7.5) + 38;
        if (used + approxWidth > available) {{
          break;
        }}
        used += approxWidth + 6;
        count++;

        const pill = document.createElement('button');
        pill.className = 'quick-slash-pill';
        pill.title = cmd.name + ': ' + cmd.goal;
        pill.innerHTML = SVG_SLASH + ' ' + escapeHtml(cmd.command);
        pill.onclick = () => quickSelectSlash(cmd.command);
        previewStrip.appendChild(pill);
      }}

      const rem = allSlashCommands.length - count;
      if (rem > 0) {{
        moreBtn.style.display = 'inline-flex';
        if (moreCount) moreCount.textContent = '+' + rem;
      }} else {{
        moreBtn.style.display = 'none';
      }}
    }}

    // Command Palette Modal Functions (Ctrl+K)
    function openCommandPalette() {{
      const backdrop = document.getElementById('cmdPaletteBackdrop');
      const modal = document.getElementById('cmdPaletteModal');
      const input = document.getElementById('cmdPaletteInput');
      if (!backdrop || !modal) return;
      
      backdrop.classList.add('active');
      modal.classList.add('active');
      if (input) {{
        input.value = '';
        setTimeout(() => input.focus(), 50);
      }}
      renderCommandPalette(allSlashCommands);
    }}

    function closeCommandPalette() {{
      const backdrop = document.getElementById('cmdPaletteBackdrop');
      const modal = document.getElementById('cmdPaletteModal');
      if (backdrop) backdrop.classList.remove('active');
      if (modal) modal.classList.remove('active');
      const launcher = document.getElementById('btnOpenCmdPalette');
      if (launcher) launcher.focus();
    }}

    function filterCommandPalette(query) {{
      const q = (query || '').toLowerCase().trim();
      if (!q) {{
        renderCommandPalette(allSlashCommands);
        return;
      }}
      const matched = allSlashCommands.filter(c => 
        c.command.toLowerCase().includes(q) ||
        c.name.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q) ||
        c.goal.toLowerCase().includes(q) ||
        c.skills.some(s => s.toLowerCase().includes(q))
      );
      renderCommandPalette(matched);
    }}

    function renderCommandPalette(commands) {{
      const list = document.getElementById('cmdPaletteList');
      if (!list) return;
      list.innerHTML = '';

      if (commands.length === 0) {{
        list.innerHTML = `
          <div style="text-align:center;padding:2rem 1rem;color:var(--text-tertiary);font-size:0.85rem;">
            Eşleşen slash komut bulunamadı.
          </div>
        `;
        return;
      }}

      commands.forEach(cmd => {{
        const item = document.createElement('div');
        item.className = 'cmd-palette-item';
        item.onclick = () => {{
          copySlashCommand(cmd.command);
          closeCommandPalette();
        }};

        item.innerHTML = `
          <div class="cmd-palette-item-left">
            <span class="cmd-palette-cmd-name">${{SVG_SLASH}} ${{escapeHtml(cmd.command)}}</span>
            <span class="badge ${{cmd.badge_class}}" style="font-size:0.65rem;">${{escapeHtml(cmd.badge)}}</span>
            <span class="cmd-palette-cmd-desc">${{escapeHtml(cmd.name)}} — ${{escapeHtml(cmd.goal)}}</span>
          </div>
          <button class="btn-action" style="padding:0.2rem 0.5rem;font-size:0.72rem;color:var(--accent-slash);" onclick="event.stopPropagation();copySlashCommand('${{escapeHtml(cmd.command)}}');closeCommandPalette();">
            Kopyala
          </button>
        `;
        list.appendChild(item);
      }});
    }}

    // Mobile Drawer Functions
    function toggleMobileDrawer() {{
      const sidebar = document.getElementById('appSidebar');
      const backdrop = document.getElementById('mobileDrawerBackdrop');
      if (!sidebar) return;
      const isOpen = sidebar.classList.contains('mobile-open');
      if (isOpen) {{
        closeMobileDrawer();
      }} else {{
        sidebar.classList.add('mobile-open');
        if (backdrop) backdrop.classList.add('active');
      }}
    }}

    function closeMobileDrawer() {{
      const sidebar = document.getElementById('appSidebar');
      const backdrop = document.getElementById('mobileDrawerBackdrop');
      if (sidebar) sidebar.classList.remove('mobile-open');
      if (backdrop) backdrop.classList.remove('active');
    }}

    // Global Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {{
      if (e.key === '/' && document.activeElement.id !== 'searchInput' && document.activeElement.id !== 'cmdPaletteInput') {{
        e.preventDefault();
        document.getElementById('searchInput').focus();
      }}
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {{
        e.preventDefault();
        const palette = document.getElementById('cmdPaletteModal');
        if (palette && palette.classList.contains('active')) {{
          closeCommandPalette();
        }} else {{
          openCommandPalette();
        }}
      }}
      if (e.key === 'Escape') {{
        const sheet = document.getElementById('bottomSheetHub');
        const palette = document.getElementById('cmdPaletteModal');
        if (sheet && sheet.classList.contains('active')) {{
          closeBottomSheetHub();
          return;
        }}
        const drawer = document.getElementById('detailDrawer');
        const sidebar = document.getElementById('appSidebar');
        if (palette && palette.classList.contains('active')) {{
          closeCommandPalette();
        }} else if (drawer && drawer.classList.contains('open')) {{
          closeDrawer();
        }} else if (sidebar && sidebar.classList.contains('mobile-open')) {{
          closeMobileDrawer();
        }} else if (currentSearch) {{
          clearSearch();
        }}
      }}
      if (e.key === '[' && document.activeElement.tagName !== 'INPUT') {{
        toggleSidebar();
      }}
      if (e.key.toLowerCase() === 't' && document.activeElement.tagName !== 'INPUT') {{
        toggleTheme();
      }}
      if (e.key.toLowerCase() === 'g' && document.activeElement.tagName !== 'INPUT') {{
        setLayoutMode('grid');
      }}
      if (e.key.toLowerCase() === 'l' && document.activeElement.tagName !== 'INPUT') {{
        setLayoutMode('list');
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

    // Initialize Theme, Sidebar & Layout
    const savedTheme = localStorage.getItem('agent_catalog_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);

    if (localStorage.getItem('agent_sidebar_collapsed') === 'true') {{
      document.getElementById('appSidebar').classList.add('collapsed');
    }}

    setLayoutMode(currentLayout);
    switchView(activeView);

    if ('ResizeObserver' in window) {{
      let rzTimer;
      const ribbon = document.getElementById('quickSlashRibbon');
      if (ribbon) {{
        const ro = new ResizeObserver(() => {{
          clearTimeout(rzTimer);
          rzTimer = setTimeout(updateSlashRibbonPreview, 50);
        }});
        ro.observe(ribbon);
      }}
    }} else {{
      window.addEventListener('resize', updateSlashRibbonPreview);
    }}
    updateSlashRibbonPreview();
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
