# 🎯 İçerik Özeti (Content Brief) & Rakip Boşluk Analizi (Competitive Gap)

Bu kılavuz, arama motorlarında ve yapay zeka yanıt sistemlerinde (AEO/GEO) üst sıralara çıkmak için gereken **Rakip Boşluk Analizi** (Competitive Keyword Gap) metodolojisini ve üretim kalitesinde **İçerik Özeti** (Content Brief) hazırlama standardını belirler.

---

## 1. Rakip Boşluk Analizi (Competitive Gap Framework)

Bir web sayfasını tasarlamadan veya içerik üretmeden önce, sektördeki ilk 3-5 rakibin arama hacmi ve sıralamaları incelenir:

```
    [ Bizim Sayfa ]               [ Rakipler (Top 3) ]
          \                              /
           \       [ Kesişim ]          /
            \--- Ortak Sıralamalar ----/
                     |
        +------------+-------------+
        |                          |
   [ FIRSAT 1 ]               [ FIRSAT 2 ]
  Striking Distance         İçerik Boşluğu (Gap)
   (Sıra 11-20)           (Rakiplerde var, bizde yok)
```

1. **İçerik Boşluğu (Content Gap):** Rakiplerin organik trafik çektiği ancak bizim sitede hiç karşılığı olmayan anahtar kelime öbekleri.
2. **Çarpma Mesafesi (Striking Distance - Pozisyon 11-20):** İlk sayfada olmayan ancak 2. sayfada yer alan sayfalar. Sayfa içi SEO, H2 yapılandırması ve net bir "Answer Block" eklenerek hızla ilk 5 sıraya taşınabilir.
3. **Açı Farkı (Angle Gap):** Rakiplerin yanıt verip eksik bıraktığı alanlar (örn. 2024 yılına ait bayat ekran görüntüleri, kod örneği içermeyen yüzeysel yazılar, fiyat tablosu vermeyen karşılaştırmalar).

---

## 2. Arama Niyeti Sınıflandırması (Search Intent)

İçerik formatı, kullanıcının sorgu arkasındaki niyetine tam uymalıdır:

| Arama Niyeti | Örnek Sorgu | Beklenen Format | Sayfa Bileşenleri |
|---|---|---|---|
| **Informational** (Bilgi Edinme) | "webhook nedir", "react memo nasıl çalışır" | Kapsamlı Rehber, Tanım | Doğrudan yanıt bloğu (Answer Block), kod blokları, SSS |
| **Commercial** (Değerlendirme) | "en iyi e-ticaret altyapıları", "postgresql vs mongodb" | Karşılaştırma, Liste | Karşılaştırma tablosu, artı/eksi kutuları, kıyaslama matrisi |
| **Transactional** (Satın Alma) | "fiyatlandırma", "api anahtarı al", "indir" | Landing Page, Fiyat Ekranı | Fiyatlandırma kartları, CTA butonu, güvenilirlik rozetleri |
| **Navigational** (Gezinme) | "stripe dashboard giriş", "redis docs" | Giriş / Dokümantasyon | Sade gezinme, breadcrumbs, arama çubuğu |

---

## 3. Standart İçerik Özeti Şablonu (Content Brief Template)

Yeni bir içerik veya dokümantasyon sayfası hazırlanırken bu şablon doldurulur:

```markdown
# 📄 İçerik Özeti: [Konu Başlığı]

## 1. Genel Bilgiler
- **Hedef Kitle:** (örn. Kıdemli Frontend Geliştiriciler, B2B SaaS Kurucuları)
- **Arama Niyeti:** [Informational / Commercial / Transactional]
- **Birincil Anahtar Kelime:** (örn. "react server components rehberi")
- **İkincil Anahtar Kelimeler:** (örn. "rsc nedir", "nextjs server actions", "ssr vs rsc")
- **Hedef Kelime Sayısı:** 1.200 - 1.800 kelime

## 2. SERP ve Rakip Açısı (Differentiator)
- **Rakiplerin Eksik Noktası:** Rakipler yalnızca teorik anlatmış; biz çalışan kod demosu ve performans benchmark tablosu ekleyeceğiz.
- **Önerilen URL:** `/blog/react-server-components-rehberi`
- **Önerilen Title:** `React Server Components (RSC) Nedir? Pratik Rehber (2026)` (55 karakter)
- **Önerilen Meta Desc:** `React Server Components mimarisini, SSR farklarını ve hydration maliyetlerini sıfıra indirme yöntemlerini kod örnekleriyle öğrenin.` (138 karakter)

## 3. Yanıt Bloğu Taslağı (Answer Block Draft - Featured Snippet & GEO)
> **React Server Components (RSC)**, React 19 ile standartlaşan ve bileşen mantığının tarayıcı yerine sunucuda çalışarak sıfır istemci bundle boyutu sağlayan modern bir mimaridir. İstemci tarafındaki JavaScript yükünü ortadan kaldırarak İlk İçerikli Boyama (FCP) sürelerini %40'a varan oranda hızlandırır.

## 4. Başlık Hiyerarşisi (H2 / H3 Outline)
- **H1:** React Server Components (RSC) Nedir ve Nasıl Çalışır?
  - **H2:** RSC ve Klasik SSR Arasındaki 3 Temel Fark (Karşılaştırma Tablosu)
  - **H2:** Adım Adım İlk Sunucu Bileşeninizi Oluşturun (Kod Örneği)
  - **H2:** Sık Karşılaşılan Hatalar ve Hydration Sorunları
  - **H2:** Sıkça Sorulan Sorular (FAQPage Schema İçin)
    - **H3:** RSC tarayıcıda çalışır mı?
    - **H3:** State ve Effect hook'ları RSC'de kullanılabilir mi?

## 5. İç ve Dış Linkleme Stratejisi
- **Pillar (Ana) Sayfaya Link:** `/docs/react-mimari-kılavuzu`
- **İlgili Küme Sayfalarına Linkler:** `/blog/react-19-yenilikleri`, `/blog/use-client-direktifi`
- **Birincil Veri Kaynağı:** Resmi React dökümantasyonu ve Web Vitals benchmark raporu.

## 6. Yapılandırılmış Veri (Schema.org)
- Tür: `Article` ve `FAQPage`
```

---

## 4. Alıntıya Hazırlık (Citation Readiness) & Yanıt Bloğu Kuralları

Yapay zeka arama motorları (Perplexity, ChatGPT Search, Gemini) ve Google Featured Snippet'ların sayfayı kaynak alması için 4 kural:

1. **Doğrudan Yanıt Cümlesi (Direct Lead Sentence):** Başlıktan hemen sonraki ilk cümle soruya net tanım vermelidir. *"X bir Y'dir ve Z yapar"* formülü uygulanır. Boş giriş cümlelerinden ("Günümüz dünyasında hız çok önemlidir...") kesinlikle kaçınılır.
2. **40-60 Kelime Kuralı:** Yanıt pasajı 40 ile 60 kelime arasında olmalıdır. Çok kısa yanıtlar yetersiz sayılır; çok uzun yanıtlar özet motorları tarafından parçalanır.
3. **Biçimlendirilmiş Kanıt:** Tanım cümlesini hemen takip eden sıralı liste (`<ol>`), madde imleri (`<ul>`) veya Markdown karşılaştırma tablosu bulunmalıdır.
4. **Tarih ve Birincil Veri:** İçerikte güncel yıl (2026) ve doğrulanabilir sayısal veriler (örn. "%35 performans artışı", "2.1 saniye LCP") yer almalıdır.
