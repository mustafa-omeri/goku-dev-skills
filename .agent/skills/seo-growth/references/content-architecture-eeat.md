# İçerik Mimarisi, E-E-A-T ve Güncellik Standartları

Bu doküman; konu kümeleri (Topic Clusters / Pillar-Cluster modeli), Google E-E-A-T kalite ilkeleri, içerik bayatlaması (Content Drift & Decay) denetimi ve uluslararası SEO (`hreflang`) standartlarını belirler.

---

## 1. Konu Kümeleri (Topic Clusters / Pillar-Cluster Mimarisi)

Arama motorları artık bağımsız sayfaları değil, bir alan üzerindeki bütüncül konu otoritesini (Topical Authority) ödüllendirir.

```
                  ┌────────────────────────┐
                  │      PILLAR SAYFA      │
                  │ (Ana Rehber - Geniş)   │
                  └───────────┬────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  CLUSTER SAYFA 1 │ │  CLUSTER SAYFA 2 │ │  CLUSTER SAYFA 3 │
│  (Teknik SEO)    │ │  (Schema.org)    │ │  (GTM Lansman)   │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
             Çift Yönlü İç Linkleme (Internal Linking)
```

1. **Pillar (Sütun) Sayfa:** Konunun tamamını kuşbakışı özetleyen, 2.500+ kelimelik, her alt başlığı kapsayan kapsamlı ana rehber.
2. **Cluster (Küme) Sayfaları:** Pillar'daki belirli bir alt problemi derinlemesine inceleyen odak sayfalar.
3. **Çift Yönlü Linkleme:** Her küme sayfası ana sütun sayfasına açıklayıcı metinle link verir (`"Kapsamlı SEO Rehberimize göz atın"`), sütun sayfası da her kümeye link verir. Bu yapı arama motoru botlarına konunun sahipliğini kanıtlar.

---

## 2. Google E-E-A-T İlkeleri (Arama Kalite Yönergesi)

Google'ın Arama Kalite Değerlendirici Yönergeleri'nde (Search Quality Rater Guidelines) yer alan 4 sütun:

| Sütun | Anlamı | Kod ve İçerik Düzeyinde Kanıtı |
|---|---|---|
| **E (Experience - Deneyim)** | Birinci elden yaşanmış tecrübe | Gerçek terminal çıktıları, gerçek arayüz ekran görüntüleri, bizzat çalıştırılmış test sonuçları ve loglar. |
| **E (Expertise - Uzmanlık)** | Teknik derinlik ve doğruluk | Standart terminoloji, RFC ve W3C şartnamelerine atıf, mimari kararların teknik gerekçelendirilmesi. |
| **A (Authoritativeness - Yetkinlik)** | Sektörel tanınırlık | Doğrulanmış yazar biyografisi, GitHub commit/katkı geçmişi, saygın platformlardan alınan organik atıflar. |
| **T (Trustworthiness - Güvenilirlik)** | Güvenlik ve dürüstlük | Zorunlu HTTPS, açık lisans (MIT vb.), gizlilik ve güvenlik politikaları (`SECURITY.md`), yanıltıcı olmayan başlıklar. |

---

## 3. İçerik Bayatlaması (Content Drift & Decay) Önleme

Zamanla değer kaybeden veya eskiyen içerik arama motoru sıralamalarında hızla düşer:

1. **Tarih Bayatlaması:** Başlık ve meta açıklamalarda geçmiş yılların (ör. `2023`, `2024`) unutulması. Mevcut yılda (`2026`) güncelliği teyit edilmelidir.
2. **Kırık Linkler:** Dış kaynak linklerinin 404'e düşmesi otoriteyi zedeler.
3. **Kullanımdan Kalkan API'ler:** Dokümanlardaki kod örneklerinde güncel olmayan kütüphane metotlarının yer alması.
4. **Periyodik Güncelleme:** Sayfaların `<meta property="article:modified_time">` veya sitemap `lastmod` değerleri gerçek revizyonlarla güncellenmelidir.

---

## 4. Çok Dilli ve Uluslararası SEO (`hreflang`)

Birden fazla dilde veya bölgede yayın yapan siteler için:

```html
<!-- Mevcut sayfa (Türkçe) -->
<link rel="alternate" hreflang="tr" href="https://example.com/tr/sayfa" />

<!-- İngilizce versiyon -->
<link rel="alternate" hreflang="en" href="https://example.com/en/page" />

<!-- Eşleşmeyen tüm diller için varsayılan fallback -->
<link rel="alternate" hreflang="x-default" href="https://example.com/en/page" />
```

**Kritik Kurallar:**
- **Kendine Referans (Self-referential):** Sayfa kendi dilini de `hreflang` olarak listelemelidir.
- **Karşılıklılık (Reciprocity):** Türkçe sayfa İngilizceye link veriyorsa, İngilizce sayfa da mutlaka Türkçeye `hreflang` ile link vermelidir.
- **IP Bazlı Sessiz Yönlendirme Yasağı:** Arama motoru botlarını kullanıcı diline zorla yönlendirmek (302 redirect) indekslemeyi bozar; dil tercihi kullanıcıya bırakılmalıdır.
