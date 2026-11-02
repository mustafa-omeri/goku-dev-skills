# 🔍 Claude-SEO Kod İnceleme & Denetim Referansı

> **Kaynak Depo:** `AgricIDaniel/claude-seo` ([GitHub](https://github.com/AgricIDaniel/claude-seo))  
> **Scout ID:** `3`  
> **Hedef Yetenek:** `.agent/skills/code-review/` & `.agent/skills/seo-growth/`  
> **Durum:** ✅ AKTARILDI

---

## 1. Entegrasyon Kapsamı ve Mimari Köprü

Bu referans, `AgricIDaniel/claude-seo` deposundaki 26 sub-skill ve 19 denetim ajanından derlenen kuralları `code-review` yeteneğinin **Şartname & Standartlar Denetimi** katmanına bağlar.

### 1.1 İlgili Referans Dokümanları
- **GEO & AI Search Rehberi:** `.agent/skills/seo-growth/references/geo-ai-search.md`
- **E-E-A-T & İçerik Mimarisi:** `.agent/skills/seo-growth/references/content-architecture-eeat.md`
- **Otomasyon Denetim Betiği:** `.agent/skills/seo-growth/scripts/seo_checker.py`

---

## 2. Kod İncelemesinde (Code Review) Denetlenecek SEO Maddeleri

Kod incelemesi sırasında frontend sayfaları ve layout bileşenleri taranırken şu kritik kurallar aranır:

1. **Meta & Canonical Bütünlüğü:**
   - Her sayfada benzersiz bir `<title>` (30-60 karakter) ve `<meta name="description">` (70-155 karakter).
   - Geçerli bir `<link rel="canonical" href="...">`.
2. **OpenGraph & Twitter Cards:**
   - `og:title`, `og:description`, `og:image`, `og:type` ve `twitter:card` eksiksiz tanımlanmalıdır.
3. **Yapısal Veri (JSON-LD):**
   - `@context: "https://schema.org"` ile `WebSite`, `Article`, `Product` veya `Organization` şeması sayfaya gömülmelidir.
4. **GEO (Generative Engine Optimization) Kuralları:**
   - H2/H3 başlıklarının hemen altında doğrudan 1-2 cümlelik net cevap (direct definition).
   - Tablo veya liste formatında alıntılanabilir veri blokları.
5. **E-E-A-T ve Yazar Bilgisi:**
   - Makale ve içerik sayfalarında gerçek yazar adı, uzmanlık unvanı ve güncellenme tarihi.

---

## 3. Doğrulama
- `python .agent/skills/seo-growth/scripts/seo_checker.py [dosya.html]` ile statik HTML sayfaları taranır.
- `W10`: Geçmiş yıl tespiti (Content Drift).
- `W11`: Çok dilli `hreflang` eşleşmesi.
