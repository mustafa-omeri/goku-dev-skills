# 🤖 AI Crawler & Bot Yönetim Politikası (AI Crawler Policy Matrix)

Bu kılavuz, yapay zeka arama motorları (Perplexity, ChatGPT Search, Claude, Google AI Overviews) ve LLM model eğitim botlarının (GPTBot, CCBot, Bytespider) web sitenizi tarama ve içerik tüketme davranışlarını yönetmek için gereken standartları, `robots.txt` direktiflerini ve `/llms.txt` protokolünü tanımlar.

---

## 1. AI Bot Taksonomisi: Arama vs. Model Eğitimi

Yapay zeka botları iki temel kategoriye ayrılır:
1. **Canlı Arama & Atıf Botları (Search & Retrieval):** Kullanıcı bir yapay zeka arayüzünde soru sorduğunda gerçek zamanlı olarak sayfayı ziyaret eder, içeriği okur ve kullanıcıya kaynak linki (citation / referral traffic) verir. Bu botların engellenmesi siteden yapay zeka arama trafiğini tamamen keser.
2. **Model Eğitim Botları (Training & Scraping):** Gelecekteki yapay zeka modellerini eğitmek amacıyla tüm interneti arşivler. Genellikle doğrudan trafik sağlamaz; sadece içeriği ağırlık matrislerine dahil eder.

### 📋 AI Crawler Referans Tablosu

| User-Agent | Sağlayıcı | Kategori | Davranış & Amaç | Önerilen Politika |
|---|---|---|---|---|
| `ChatGPT-User` | OpenAI | Arama / Canlı | ChatGPT kullanıcısının web araması tetiklemesiyle gelir | **Allow** (Doğrudan trafik) |
| `GPTBot` | OpenAI | Model Eğitimi | GPT modellerinin eğitimi için veri toplar | İsteğe Bağlı / Seçici |
| `PerplexityBot` | Perplexity AI | Arama / Canlı | Perplexity yanıt motoru araması ve kaynak alıntılama | **Allow** (Trafik & Atıf) |
| `ClaudeBot` | Anthropic | Arama / Canlı | Claude yanıt motoru ve web indeksleme | **Allow** (Trafik & Atıf) |
| `anthropic-ai` | Anthropic | Model Eğitimi | Claude modellerinin genel eğitimi | İsteğe Bağlı / Seçici |
| `Google-Extended` | Google | Model Eğitimi | Gemini ve Vertex AI model eğitimi (Google Search'ü etkilemez) | İsteğe Bağlı |
| `Googlebot` | Google | Arama / İndeks | Google Search ve AI Overviews temel indeksleyicisi | **Allow** (Kritik) |
| `Applebot-Extended` | Apple | Model Eğitimi | Apple Intelligence modellerinin eğitimi | İsteğe Bağlı |
| `Bytespider` | ByteDance | Model Eğitimi | TikTok ve ByteDance LLM scraper'ı (aşırı agresif tarama riski) | **Disallow** (Sunucu yükü) |
| `CCBot` | Common Crawl | Arşiv / Eğitim | Açık kaynaklı model eğitimleri için ham arşiv | **Disallow** / Sınırla |

---

## 2. Standart `robots.txt` Şablonları

### Strateji A: "Maksimum Görünürlük & Yapay Zeka Trafiği" (Önerilen)
Yapay zeka arama motorlarının atıf yapmasına izin verirken, aşırı yük oluşturan agresif scraper'ları sınırlar:

```txt
# robots.txt - AI Search Friendly

User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /private/

# Canlı Arama ve Yanıt Motorları (Trafik ve Atıf Getirenler)
User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

# Agresif ve Trafik Sağlamayan Scraper'ları Engelle
User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /

# Site Haritası ve LLM Manifesti
Sitemap: https://example.com/sitemap.xml
# LLM Manifesti: https://example.com/llms.txt
```

---

### Strateji B: "Arama Serbest, Model Eğitimi Yasak"
İçeriğinizin yapay zeka arama sonuçlarında çıkmasını ve kaynak gösterilmesini istiyor, ancak modellerin eğitilmesinde ücretsiz kullanılmasını istemiyorsanız:

```txt
# robots.txt - Search Allowed, Training Blocked

User-agent: *
Allow: /

# Arama ve Atıf Botları Açık
User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

# Eğitim Botları Engelli
User-agent: GPTBot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /

Sitemap: https://example.com/sitemap.xml
```

---

## 3. `/llms.txt` Standardı (LLM Bilgi Manifesti)

Web sitenizin kök dizinine (`/llms.txt`) yerleştirilen Markdown formatındaki bu dosya, LLM ajanlarının sitenizi anlamasını, dokümantasyonunuza hızlıca erişmesini ve doğru yanıtlar üretmesini sağlar.

### Şablon: `/llms.txt`

```markdown
# Proje / Şirket Adı

> Kısa ve net birincil ürün tanımı: Ne yapar, kimin içindir, temel avantajı nedir.

## Temel Dokümantasyon
- [Hızlı Başlangıç](https://example.com/docs/quickstart.md): 5 dakikada kurulum ve ilk API çağrısı
- [Mimari Kılavuzu](https://example.com/docs/architecture.md): Çekirdek bileşenler ve veri akışı
- [API Referansı](https://example.com/docs/api.md): REST ve SDK metotları

## İsteğe Bağlı: llms-full.txt
Tüm dokümantasyonun tek parça halinde LLM bağlamına (context window) beslenmesi için:
- [Tüm Dokümantasyon (Tek Dosya)](https://example.com/llms-full.txt)
```

---

## 4. Meta Etiketleri ve HTTP Başlıkları (Granular Kontrol)

HTML seviyesinde yapay zeka direktifleri tanımlamak için:

```html
<!-- Yapay zeka modellerinin içeriği eğitim verisi olarak kullanmasını engelleme -->
<meta name="robots" content="noai, noimageai">

<!-- Arama motorunun sayfayı önbelleğe almasını önleme (taze veri zorunluluğu) -->
<meta name="robots" content="noarchive">
```

HTTP yanıt başlıklarında (özellikle API ve PDF dökümanları için):
```http
X-Robots-Tag: noai, noimageai
```
