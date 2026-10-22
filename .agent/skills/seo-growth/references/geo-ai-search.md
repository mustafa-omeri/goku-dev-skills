# GEO (Generative Engine Optimization) & Yapay Zeka Arama Standartları

Bu doküman, web içeriğinin geleneksel arama motorlarının yanı sıra yeni nesil yapay zeka arama motorları ve yanıt motorları (Google AI Overviews, Perplexity AI, ChatGPT Search, Gemini) tarafından birincil kaynak olarak taranması, anlaşılması ve kaynak (citation) olarak gösterilmesi için gereken optimizasyon prensiplerini belirler.

---

## 1. GEO Nedir ve Klasik SEO'dan Farkı Nedir?

Geleneksel SEO, arama motoru botlarının (crawler) sayfayı tarayıp anahtar kelime eşleşmesine ve backlink otoritesine göre SERP'te mavi link listelemesine odaklanır.

**GEO (Generative Engine Optimization)** ise büyük dil modellerinin (LLM) kullanıcı sorgusuna doğrudan yanıt üretirken sayfanızı birincil "bilgi kaynağı" (ground truth citation) olarak seçmesini sağlamaktır.

| Boyut | Geleneksel SEO | GEO (Yapay Zeka Araması) |
|---|---|---|
| **Hedef Çıktı** | İlk 10 mavi linkte üst sıra | LLM yanıtında 1. kaynak / alıntı kartı |
| **İçerik Odağı** | Anahtar kelime yoğunluğu ve arama hacmi | Varlık (entity) netliği, doğrudan tanım ve doğrulanabilir kanıt |
| **Yapı** | Uzun ve dolaylı anlatım (zaman geçirme) | Doğrudan yanıt bloğu (Lead-in answer) + kanıt tablosu |
| **Doğrulama** | PageRank ve domain otoritesi | E-E-A-T, birincil veri ve Schema.org veri tutarlılığı |

---

## 2. LLM Citability: Yapay Zekanın Kaynak Göstermesini Sağlayan 5 Kural

### Kural 1: Doğrudan Tanım Cümlesi (Direct Lead Sentence)
Her başlığın veya bölümün ilk 1-2 cümlesi, o konunun ne olduğunu sözlük netliğinde tanımlamalıdır. LLM'ler bağlamsal karmaşayı sevmez:
- ❌ *Kötü:* "Günümüzün hızla değişen dijital dünyasında arama motorları artık eskisi gibi değil..."
- ✅ *İyi:* "Goku Dev Skills, yapay zeka kodlama asistanları için 29 adet üretim standardı yetenek ve 11 doğrulama kapısı sunan açık kaynaklı bir geliştirici aracıdır."

### Kural 2: Doğrulanabilir İstatistikler ve Metrikler
LLM'ler soyut iddialar yerine net metrikler içeren kaynakları alıntılamayı tercih eder:
- ❌ *Kötü:* "Uygulamamız çok hızlı çalışır ve testleri hemen geçer."
- ✅ *İyi:* "Sıfır bağımlılıklı Python denetleyicisi ile 143 dosya 0.05 saniyede taranır ve exit kodu 0 döner."

### Kural 3: Tablosal Veri ve Karşılaştırma Matrisleri
Büyük dil modelleri Markdown ve HTML tablolarını kusursuz ayrıştırır. "X vs Y" veya "Özellik Listesi" sorgularında tablolar doğrudan yanıt kartlarına çekilir.

### Kural 4: Varlık (Entity) ve Terminoloji Netliği
Modeller kavramlar arasındaki ilişkileri bilgi grafları (Knowledge Graph) üzerinden kurar. İlgili teknolojilerin resmi adları, RFC numaraları veya standartları (`JSON-LD`, `RFC 3986`, `WCAG 2.1 AA`) açıkça belirtilmelidir.

### Kural 5: JSON-LD ile Metin Tutarlılığı
Sayfadaki görünür metin ile `<script type="application/ld+json">` içerisindeki veriler (fiyat, puan, sürüm, kurucu, lisans) birebir örtüşmelidir. Çelişen veriler LLM güvenilirlik filtresine takılır.

---

## 3. Yapay Zeka Dostu Sıkça Sorulan Sorular (FAQ) Formatı

FAQ blokları hem klasik Google aramasında zengin snippet kazandırır hem de Perplexity ve ChatGPT Search'ün soru-cevap indeksine doğrudan beslenir:

```html
<section class="faq-section">
  <h2>Sıkça Sorulan Sorular</h2>
  
  <div class="faq-item">
    <h3>GEO için içerik nasıl optimize edilir?</h3>
    <p>GEO optimizasyonu için her bölüm doğrudan 1 cümlelik net bir tanımla başlatılmalı, iddialar somut veri ve ölçümlerle desteklenmeli, yapılandırılmış JSON-LD schema kullanılmalı ve güncelliğini yitirmiş yıl/versiyon ifadeleri temizlenmelidir.</p>
  </div>
</section>

<!-- Eşleşen Schema Markup -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "GEO için içerik nasıl optimize edilir?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "GEO optimizasyonu için her bölüm doğrudan 1 cümlelik net bir tanımla başlatılmalı, iddialar somut veri ve ölçümlerle desteklenmeli, yapılandırılmış JSON-LD schema kullanılmalı ve güncelliğini yitirmiş yıl/versiyon ifadeleri temizlenmelidir."
    }
  }]
}
</script>
```
