---
name: seo-apply
description: Uçtan uca SEO, yapay zeka arama motoru optimizasyonu ve yapısal veri orkestratörü; meta etiketleri, OpenGraph ve JSON-LD şemalarını uygular. Tetikleyiciler: "/seo-apply", "seo apply", "[SEO-APPLY]", "seo uygula", "meta tag ekle". Tetiklenmez: marka tonu `brand`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# SEO & GEO Apply Ensemble Orchestrator

Bu yetenek, hem geleneksel arama motorları (Google, Bing) hem de yapay zeka arama asistanları (Perplexity, ChatGPT Search) için görünürlüğü maksimize eden SEO/GEO protokolünü işletir.

## Orkestrasyon Akışı

1. **Meta & Başlık Optimizasyonu:**
   - Her sayfa için benzersiz `<title>`, `<meta name="description">` ve OpenGraph/Twitter Card etiketlerini yapılandır.
2. **Yapısal Veri (Schema.org / JSON-LD):**
   - Sayfa tipine uygun JSON-LD yapısal veri bloklarını (Organization, WebSite, Article, Product, SoftwareApplication) enjekte et.
3. **Semantik HTML ve Başlık Hiyerarşisi:**
   - Tek bir `<h1>`, mantıksal `<h2>`-`<h3>` sıralaması ve erişilebilir görsel alt metinlerini doğrula.
4. **Mekanik SEO Denetimi:**
   - `python .agent/skills/seo-growth/scripts/seo_checker.py` çalıştırarak meta eksikliklerini ve DOM kurallarını doğrula.
