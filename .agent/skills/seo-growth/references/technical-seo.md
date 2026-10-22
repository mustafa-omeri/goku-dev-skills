# Teknik SEO & SERP Standartları Rehberi

Bu kılavuz, web sayfalarının arama motorları (Googlebot, Bingbot, Perplexity vb.) ve sosyal medya platformları (Twitter/X, LinkedIn, Slack, WhatsApp vb.) tarafından doğru taranması, indekslenmesi ve yüksek tıklama oranıyla (CTR) SERP'te listelenmesi için gereken teknik mimariyi belirler.

---

## 1. Kritik HTML Meta Etiketleri ve Hiyerarşi

Her HTML sayfasında `<head>` bölümünde şu etiketler eksiksiz yer almalıdır:

```html
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  
  <!-- 1. Title Tag (İdeal: 50-65 karakter) -->
  <title>Ürün Başlığı - Anahtar Değer Önerisi ve Çözüm | Marka</title>
  
  <!-- 2. Meta Description (İdeal: 120-155 karakter) -->
  <meta name="description" content="Ürününüzün sağladığı ana faydayı ve hedef kitlenin yaşadığı problemi çözen net, harekete geçirici ve anahtar kelime içeren açıklama metni." />
  
  <!-- 3. Canonical Tag (Kopya İçerik Önleyici) -->
  <link rel="canonical" href="https://example.com/orijinal-sayfa-url" />
  
  <!-- 4. Robots Direktifleri -->
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  
  <!-- 5. OpenGraph (Facebook, LinkedIn, Discord) -->
  <meta property="og:locale" content="tr_TR" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Sosyal Paylaşım Başlığı" />
  <meta property="og:description" content="Sosyal akışta dikkat çeken 1-2 cümlelik özet değer önerisi." />
  <meta property="og:url" content="https://example.com/orijinal-sayfa-url" />
  <meta property="og:site_name" content="Marka Adı" />
  <meta property="og:image" content="https://example.com/assets/og-image-1200x630.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Görsel açıklaması" />
  
  <!-- 6. Twitter / X Cards -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@marka_hesabi" />
  <meta name="twitter:creator" content="@kurucu_hesabi" />
  <meta name="twitter:title" content="X Akışı İçin Vurucu Başlık" />
  <meta name="twitter:description" content="X akışında okunabilirliği yüksek açıklama." />
  <meta name="twitter:image" content="https://example.com/assets/og-image-1200x630.png" />
  
  <!-- 7. Favicon ve PWA -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
</head>
```

---

## 2. JSON-LD Yapılandırılmış Veri (Schema.org Markup)

Arama motorlarının zengin arama sonuçları (Rich Snippets, Sitelinks, FAQ Accordion vb.) üretebilmesi için `<script type="application/ld+json">` kullanılmalıdır.

### A. SaaS & Web Uygulaması Şablonu (`SoftwareApplication`)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "DevGoku",
  "operatingSystem": "All",
  "applicationCategory": "DeveloperApplication",
  "description": "Yazılım ekipleri için yapay zeka destekli otonom geliştirme ve test kiti.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "ratingCount": "128"
  }
}
</script>
```

### B. Sıkça Sorulan Sorular Şablonu (`FAQPage`)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Sistem hangi framework'leri destekliyor?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "React, Vite, Next.js, Spring Boot ve modern RESTful mimariler tam uyumludur."
      }
    },
    {
      "@type": "Question",
      "name": "Kurulum için kredi kartı gerekir mi?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Hayır, açık kaynaklı temel modülleri doğrudan npx veya yerel CLI ile kurabilirsiniz."
      }
    }
  ]
}
</script>
```

---

## 3. robots.txt ve XML Sitemap Sözleşmesi

### `robots.txt` Standart Yapısı (`public/robots.txt`)

```txt
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /private/
Disallow: /*?*sort=

Sitemap: https://example.com/sitemap.xml
```

### `sitemap.xml` Standart Yapısı (`public/sitemap.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-10-22</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/features</loc>
    <lastmod>2026-10-22</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://example.com/pricing</loc>
    <lastmod>2026-10-22</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

---

## 4. On-Page Semantik İçerik Hiyerarşisi

1. **Tek Bir H1:** Her sayfada yalnızca 1 adet `<h1>` bulunmalıdır. H1, sayfanın ana arama niyetini (search intent) ve değer önerisini taşır.
2. **Hiyerarşik Sıralama:** `<h1>` → `<h2>` → `<h3>` sıralaması atlanmamalıdır (H1'den doğrudan H3'e geçilmez).
3. **Görsel Alt Metinleri:** Her `<img>` etiketinde mutlaka içeriği tarif eden anlamlı bir `alt="..."` özniteliği bulunmalıdır. Dekoratif görseller için `alt="" aria-hidden="true"` kullanılabilir.
4. **URL Slug Ergonomisi:** Küçük harf, tire ile ayrılmış (`/teknik-seo-rehberi`), parametresiz ve net URL'ler tercih edilir.
5. **İç Linkleme (Internal Linking):** İlgili terimler üzerinden doğal metin içi linklemeler yapılmalı, "buraya tıklayın" yerine açıklayıcı anchor text'ler ("detaylı fiyatlandırma tablosu") kullanılmalıdır.
