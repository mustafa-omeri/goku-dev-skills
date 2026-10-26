---
name: seo-growth
description: >
  Arama motoru optimizasyonu (SEO), yapay zeka araması (GEO) ve büyüme: teknik SEO, meta etiketler, JSON-LD, SERP, E-E-A-T, topic cluster, GTM lansmanı ve CRO formülleri. Tetikleyiciler: "/seo-apply", "seo", "teknik seo", "geo", "ai search", "meta tag", "sitemap", "schema markup", "ürün lansmanı", "seo optimization", "technical seo", "product launch", "growth marketing". Tetiklenmez: marka görsel kimliği `brand`'e, PRD yazım süreci `doc-coauthoring`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# 🚀 seo-growth — SEO, GEO & Büyüme (Growth) Stratejisi

Bu yetenek, web uygulamalarının, landing page'lerin ve açık kaynaklı projelerin arama motoru optimizasyonunu (Teknik SEO, SERP görünürlüğü, JSON-LD Schema, robots.txt, sitemap), yapay zeka yanıt motorları optimizasyonunu (GEO: Generative Engine Optimization / Google AI Overviews, Perplexity, ChatGPT Search), AI crawler direktiflerini, konu kümelerini (Topic Clusters), Google E-E-A-T kalite standartlarını, rakip boşluk analizini (Competitive Gap), içerik özetlerini (Content Brief), Go-To-Market (GTM) lansman kurgusunu ve dönüşüm odaklı metin yazarlığı (CRO) süreçlerini yönetir.

---

## 1. Mimari Kapsam ve Temel Prensipler

1. **Teknik SEO & SERP Mimarisi:**
   - `<title>` (30-65 karakter), `<meta name="description">` (70-160 karakter), `<meta name="viewport">`.
   - Sosyal medya kartları: OpenGraph (`og:title`, `og:description`, `og:image`, `og:url`) ve Twitter Cards (`twitter:card`, `twitter:title`, `twitter:image`).
   - Yapılandırılmış veri: JSON-LD Schema.org (`SoftwareApplication`, `FAQPage`, `Article`, `Organization`).
   - Arama motoru direktifleri: `robots.txt`, `sitemap.xml`, `<link rel="canonical">` (kopya içerik önleme).
   - Semantik başlık hiyerarşisi: Sayfa başına tam 1 adet `<h1>`, sıralı `<h2>`/`<h3>` yapısı ve tüm görsellerde anlamlı `alt` etiketleri.

2. **Yapay Zeka Araması (GEO), AI Crawler Politikası & E-E-A-T:**
   - LLM yanıt motorları (Perplexity, ChatGPT Search, Gemini, Google AI Overviews) için doğrudan tanım cümleleri (Direct Lead Sentences / Answer Blocks).
   - AI bot taksonomisi yönetimi: Canlı arama botlarına (`ChatGPT-User`, `PerplexityBot`, `ClaudeBot`) izin verirken agresif scraper'ları (`CCBot`, `Bytespider`) sınırlandırma.
   - LLM manifestosu: Site kökünde `/llms.txt` ve `/llms-full.txt` protokolü.
   - Google E-E-A-T (Deneyim, Uzmanlık, Yetkinlik, Güvenilirlik) kanıtları ve içerik bayatlaması (Content Drift & Decay) denetimi.
   - Konu Kümeleri (Topic Clusters / Pillar-Cluster modeli) ve çok dilli `hreflang` etiketleri (`x-default` fallback sözleşmesi).

3. **Rakip Boşluk Analizi (Competitive Gap) & İçerik Özeti (Content Brief):**
   - Rakiplerin organik sıralamalarıyla kesişim ve eksik anahtar kelime boşluklarının (Content Gap) tespiti.
   - Çarpma mesafesindeki (Striking distance / pozisyon 11-20) sayfaların ilk 5 sıraya yükseltilmesi.
   - Arama niyeti (Informational, Commercial, Transactional, Navigational) eşlemesi ve standart içerik özeti (Content Brief) hazırlama.

4. **GTM & Dağıtım Stratejisi (Growth Marketing):**
   - 3 Aşamalı lansman protokolü (Pre-launch hazırlık → Lansman günü icra → Post-launch sürdürülebilirlik).
   - Geliştirici platformları: Hacker News (Show HN formatı ve kurucu yorumu), Product Hunt, Reddit (9:1 değer kuralı), Twitter/X ve LinkedIn açık geliştirme (Build in Public).
   - GitHub README vitrini (Hero, TL;DR, demo GIF/SVG, tek satırda kurulum, mimari matris).

5. **Dönüşüm Odaklı Metin Yazımı (CRO & Copywriting):**
   - İkna formülleri: **PAS** (Problem-Agitate-Solve), **AIDA** (Attention-Interest-Desire-Action), **BAB** (Before-After-Bridge), **FAB** (Feature-Advantage-Benefit).
   - Landing page sürtünme azaltma (5 saniye kuralı, tek birincil eylem CTA'sı, gerçek sosyal kanıtlar).

---

## 2. Denetim Aracı: `seo_checker.py`

Projedeki statik HTML, robots.txt veya derlenmiş üretim çıktılarını doğrulamak için yerleşik denetleyici çalıştırılır:

```bash
# Tek bir HTML sayfasını denetle
python .agent/skills/seo-growth/scripts/seo_checker.py index.html

# robots.txt ve AI bot politikalarını denetle
python .agent/skills/seo-growth/scripts/seo_checker.py robots.txt

# Derlenmiş tüm dist veya build çıktısını tara
python .agent/skills/seo-growth/scripts/seo_checker.py dist/

# CI/CD kapısı veya sıkı mod (uyarılarda da exit 1)
python .agent/skills/seo-growth/scripts/seo_checker.py dist/ --strict

# Makine tarafından okunabilir JSON çıktısı al
python .agent/skills/seo-growth/scripts/seo_checker.py public/ --json
```

---

## 3. Derinlemesine Rehberler

Detaylı teknik standartlar, şablonlar ve lansman taktikleri için alt kılavuzları inceleyin:

- **/seo-apply Protokolü:** `references/seo-apply-protocol.md` (Uçtan uca SEO/GEO uygulama, enjeksiyon ve doğrulama akışı).
- **Teknik SEO & Şablonlar:** `references/technical-seo.md` (JSON-LD şablonları, robots.txt, sitemap.xml, canonical).
- **Yapay Zeka Araması (GEO):** `references/geo-ai-search.md` (Google AI Overviews, Perplexity, ChatGPT Search, FAQPage).
- **AI Crawler & Bot Politikası:** `references/ai-crawler-matrix.md` (ChatGPT-User, PerplexityBot, ClaudeBot, robots.txt ve /llms.txt).
- **İçerik Mimarisi & E-E-A-T:** `references/content-architecture-eeat.md` (Topic Clusters, Content Drift, hreflang).
- **İçerik Özeti & Rakip Analizi:** `references/competitive-gap-content-brief.md` (Content brief şablonu, arama niyeti, Answer Block formülü).
- **GTM & Lansman Playbook'u:** `references/growth-gtm-playbook.md` (Show HN, Product Hunt, Reddit, GitHub vitrini).
- **CRO & Metin Yazımı:** `references/copywriting-cro.md` (PAS, AIDA, BAB formülleri ve CTA optimizasyonu).

---

## 4. Sorumluluk Sınırları ve Diğer Skill'lerle Entegrasyon

- **Görsel Kimlik & Marka Tonu:** Logo, kurumsal dil, renk spesifikasyonu `brand` skill'ine aittir.
- **Yazılı Dokümantasyon Süreci:** PRD, teknik spec ve RFC yazımı `doc-coauthoring` skill'ine aittir.
- **Web UI & CSS Tasarımı:** Arayüz bileşenlerinin tasarımı ve Tailwind kodlaması `frontend-design` ve `ui-styling` skill'lerine aittir.
- **Bu Skill'in Sahipliği:** Teknik arama motoru indekslenebilirliği, GEO/AI arama optimizasyonu, AI crawler politikası, meta veriler, schema markup, lansman büyüme planı, rakip analizi ve dönüşüm metinleridir.
