---
name: seo-growth
description: >
  Arama motoru optimizasyonu (SEO) ve büyüme stratejisi: teknik SEO, meta etiketler, JSON-LD schema, robots.txt, sitemap, SERP mimarisi, GTM lansman planı, CRO ve metin formülleri. Tetikleyiciler: "seo", "teknik seo", "meta tag", "sitemap", "schema markup", "ürün lansmanı", "seo optimization", "technical seo", "meta description", "product launch", "gtm strategy", "growth marketing". Tetiklenmez: marka görsel kimliği ve ton `brand`'e, PRD dokümantasyon süreci `doc-coauthoring`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# 🚀 seo-growth — SEO & Büyüme (Growth) Stratejisi

Bu yetenek, web uygulamalarının, landing page'lerin ve açık kaynaklı projelerin arama motoru optimizasyonunu (Teknik SEO, SERP görünürlüğü, JSON-LD Schema, robots.txt, sitemap), Go-To-Market (GTM) lansman kurgusunu, geliştirici dağıtım kanallarını ve dönüşüm odaklı metin yazarlığı (CRO) süreçlerini yönetir.

---

## 1. Mimari Kapsam ve Temel Prensipler

1. **Teknik Arama Motoru Optimizasyonu (Technical & On-Page SEO):**
   - `<title>` (30-65 karakter), `<meta name="description">` (70-160 karakter), `<meta name="viewport">`.
   - Sosyal medya kartları: OpenGraph (`og:title`, `og:description`, `og:image`, `og:url`) ve Twitter Cards (`twitter:card`, `twitter:title`, `twitter:image`).
   - Yapılandırılmış veri: JSON-LD Schema.org (`SoftwareApplication`, `FAQPage`, `Article`, `Organization`).
   - Arama motoru direktifleri: `robots.txt`, `sitemap.xml`, `<link rel="canonical">` (kopya içerik önleme).
   - Semantik başlık hiyerarşisi: Sayfa başına tam 1 adet `<h1>`, sıralı `<h2>`/`<h3>` yapısı ve tüm görsellerde anlamlı `alt` etiketleri.

2. **GTM & Dağıtım Stratejisi (Growth Marketing):**
   - 3 Aşamalı lansman protokolü (Pre-launch hazırlık → Lansman günü icra → Post-launch sürdürülebilirlik).
   - Geliştirici platformları: Hacker News (Show HN formatı ve kurucu yorumu), Product Hunt, Reddit (9:1 değer kuralı), Twitter/X ve LinkedIn açık geliştirme (Build in Public).
   - GitHub README optimizasyonu (Hero, TL;DR, demo GIF/SVG, tek satırda kurulum, mimari matris).

3. **Dönüşüm Odaklı Metin Yazımı (CRO & Copywriting):**
   - İkna formülleri: **PAS** (Problem-Agitate-Solve), **AIDA** (Attention-Interest-Desire-Action), **BAB** (Before-After-Bridge), **FAB** (Feature-Advantage-Benefit).
   - Landing page sürtünme azaltma (5 saniye kuralı, tek birincil eylem CTA'sı, gerçek sosyal kanıtlar).

---

## 2. Denetim Aracı: `seo_checker.py`

Projedeki statik HTML veya derlenmiş üretim çıktılarını doğrulamak için yerleşik denetleyici çalıştırılır:

```bash
# Tek bir HTML sayfasını denetle
python .agent/skills/seo-growth/scripts/seo_checker.py index.html

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

- **Teknik SEO & Şablonlar:** `references/technical-seo.md` (JSON-LD şablonları, robots.txt, sitemap.xml, canonical).
- **GTM & Lansman Playbook'u:** `references/growth-gtm-playbook.md` (Show HN, Product Hunt, Reddit, GitHub vitrini).
- **CRO & Metin Yazımı:** `references/copywriting-cro.md` (PAS, AIDA, BAB formülleri ve CTA optimizasyonu).

---

## 4. Sorumluluk Sınırları ve Diğer Skill'lerle Entegrasyon

- **Görsel Kimlik & Marka Tonu:** Logo, kurumsal dil, renk spesifikasyonu `brand` skill'ine aittir.
- **Yazılı Dokümantasyon Süreci:** PRD, teknik spec ve RFC yazımı `doc-coauthoring` skill'ine aittir.
- **Web UI & CSS Tasarımı:** Arayüz bileşenlerinin tasarımı ve Tailwind kodlaması `frontend-design` ve `ui-styling` skill'lerine aittir.
- **Bu Skill'in Sahipliği:** Teknik arama motoru indekslenebilirliği, meta veriler, schema markup, lansman büyüme planı ve dönüşüm metinleridir.
