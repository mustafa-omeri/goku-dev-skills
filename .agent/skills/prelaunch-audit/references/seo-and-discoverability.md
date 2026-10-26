# SEO ve Keşfedilebilirlik Standartları

Son veri doğrulaması: 26 Ekim 2026. Arama motorları ve yapay zeka indeksleyicilerinin kuralları değiştikçe bu dokümandaki direktifler güncellenir.

---

## 1. Ham HTML Gerçeği (Server Render vs Client Render)

Modern arama motorları ve özellikle yapay zeka arama tarayıcıları (OpenAI, Anthropic, Perplexity), JavaScript kodunu tam çalıştırmadan ham HTML içeriği taramayı tercih edebilir.

- **Kritik Doğrulama:**
  `node .agent/skills/prelaunch-audit/scripts/html-audit.mjs https://example.com` komutuyla ham HTML yanıtında `<title>`, `<meta name="description">`, `<link rel="canonical">`, tek `<h1>` ve OpenGraph etiketlerinin varlığı kontrol edilmelidir.
- SPA (Single Page Application) yapılarında meta etiketler yalnızca istemci tarafında JS ile enjekte ediliyorsa, SSR/SSG (Next.js, Astro) veya derleme zamanı prerendering devreye alınmalıdır.

---

## 2. Meta Başlık ve Açıklama Disiplini

1. **Meta Title (`<title>`):**
   - Uzunluk: ≈50-60 karakter (maksimum 600 piksel genişlik).
   - Format: `Sayfa Konusu | Marka Adı`.
   - Framework varsayılanları ("Vite + React", "Create Next App", "Home") kesinlikle temizlenmelidir.
2. **Meta Description:**
   - Uzunluk: ≈120-155 karakter.
   - Sayfa içeriğiyle doğrudan ilgili, net fayda ve harekete geçirici mesaj (CTA) içeren metin.

---

## 3. sitemap.xml Standartları

- Yalnızca **200 OK** dönen, indexlenebilir, kanonik ve mutlak HTTPS URL'ler yer almalıdır.
- Yönlendirme yapan (301/302), `noindex` işaretli, 404 veren veya parametreli kopyalar sitemap içine konulmaz.
- `lastmod` etiketi ISO 8601 formatında (`YYYY-MM-DD`) yalnızca içerik gerçekten güncellendiğinde verilmelidir.
- `<priority>` ve `<changefreq>` etiketleri modern Google algoritmaları tarafından yok sayıldığından gereksiz yere eklenmemelidir.
- `robots.txt` içinde `Sitemap: https://alanadi.com/sitemap.xml` direktifi tanımlanmalıdır.

---

## 4. robots.txt ve Yapay Zeka (AI) Crawler Taksonomisi

robots.txt dosyasında üç ayrı tarama amacı bilinçli şekilde yapılandırılmalıdır:

| Amaç | Bot Belirteçleri | Tavsiye Edilen Duruş |
|------|------------------|----------------------|
| **AI Arama & Yanıt İndeksi** | `OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot` | İzin Ver (`Allow: /`) - AI arama görünürlüğü için kritik |
| **Kullanıcı Tetiklemeli Getirme** | `ChatGPT-User`, `Claude-User`, `Perplexity-User` | İzin Ver (`Allow: /`) - Kullanıcı chat anında link paylaştığında çalışır |
| **Model Eğitimi & Veri Kazıma** | `GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `Bytespider` | Proje kararına göre kısıtlanabilir (`Disallow: /`) |

**Üretim Uyarısı (BLOCKER):** Staging ortamından kalan `Disallow: /` prodüksiyon sunucusunda asla yer almamalıdır!

---

## 5. Canonical URL ve Özel 404

1. **Canonical URL:**
   Her sayfada tek bir mutlak HTTPS canonical linki (`<link rel="canonical" href="https://example.com/sayfa">`) bulunmalıdır. Sondaki eğik çizgi (trailing slash) ve `www` vs çıplak alan adı politikası tek bir standartta sabitlenmelidir.
2. **Özel 404 Sayfası:**
   Var olmayan bir adrese gidildiğinde sunucu **gerçek 404 HTTP durum kodu** dönmelidir. 200 OK dönüp içinde "Sayfa bulunamadı" yazan soft-404 durumları arama motoru indeksleme bütçesini tüketir.

---

## 6. Favicon ve llms.txt

- **Favicon Seti:** `favicon.ico`, modern `favicon.svg`, 180x180 `apple-touch-icon.png` ve `manifest.json` ikonları eksiksiz sunulmalıdır.
- **llms.txt:** Opsiyonel (P3) standart. Sitenin amacını, ana dokümanlarını ve kurallarını LLM'lerin okuması için `/llms.txt` adresinde yalın markdown formatında sunar.
