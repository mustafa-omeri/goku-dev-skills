---
name: prelaunch-audit
description: >-
  Canlıya çıkış (production launch) öncesi yasal, gizlilik, SEO, erişilebilirlik ve altyapı denetimi yapar; 20 maddelik kontrol listesi, KVKK/GDPR, Consent Mode v2, WCAG 2.2 ve AI bot taksonomisi doğrular. Tetikleyiciler: "prelaunch", "canlıya al", "go live", "yayına alma kontrolü", "prelaunch audit", "go live checklist", "/prelaunch", "/prelaunch-update". Tetiklenmez: salt geliştirme aşamasındaki birim testleri `tdd`'ye aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Canlıya Alma Denetimi (Pre-Launch Orchestrator)

Son veri doğrulaması: 26 Ekim 2026. Web siteleri ve dijital ürünler canlıya (production) alınmadan önce 20 maddelik çekirdek kalite, yasal uyum, SEO, erişilebilirlik ve altyapı denetimini yürütür, bulguları raporlar ve `PRELAUNCH-REPORT.md` belgesini üretir.

---

## Komut Kısayolları

Bu skill iki farklı çalışma moduna sahiptir:

1. **`/prelaunch` (veya `prelaunch`, `canlıya al`, `go live`):**
   20 maddelik çekirdek denetimi ve geçerli koşullu maddeleri çalıştırır, ölçümleri toplar, varsa otomatik düzeltmeleri yapar ve kapsamlı `PRELAUNCH-REPORT.md` karar raporunu hazırlar.
2. **`/prelaunch-update`:**
   Mevzuat, idari para cezaları, Google Search kuralları ve platform standartlarını AI modeli aracılığıyla resmi kaynaklardan sorgulayıp günceller. Ayrıntılar için [Mevzuat Güncelleme Protokolü](references/regulatory-sync-protocol.md) belgesini inceleyin.

---

## Temel İlkeler ve Katı Sınırlar

1. **Önce Ölç, Sonra Düzelt, Sonra Yeniden Ölç:** Kanıtsız (komut çıktısı, dosya yolu, ekran görüntüsü olmadan) hiçbir maddeye `PASS` verilmez.
2. **Hukuki Veri ve Yorum Uydurma Yasağı:** Şirket unvanı, MERSİS, vergi no, fiyat, taahhüt veya müşteri yorumu kesinlikle uydurulamaz. Bilinmeyen değerler `[ŞİRKET ÜNVANI]` şeklinde yer tutucu bırakılır ve raporda listelenir.
3. **Üretilen Hukuki Metinler Taslaktır:** Üretilen aydınlatma, gizlilik ve kullanım şartları metinleri raporda "taslak, hukukçu onayı gerekir" (`NEEDS-HUMAN`) şeklinde işaretlenir.
4. **Platformlar Arası Komutlar:** Betikler Windows, macOS ve Linux uyumludur; ölçüm çıktıları `.prelaunch/` klasörüne yazılır.

---

## 20 Maddelik Çekirdek Denetim Tablosu

| # | Madde | Önem Derecesi | Geçme Kriteri (Tek Satır) | Doğrulama & İlgili Referans |
|---|-------|----------------|---------------------------|------------------------------|
| 1 | Gizlilik Politikası / KVKK | KRİTİK | Kişisel veri işleyen her sitede footer ve formlarda erişilen, gerçek veri akışını anlatan metin | [legal-privacy-compliance.md](references/legal-privacy-compliance.md) |
| 2 | Kullanım Şartları | YÜKSEK | Hesap, ödeme veya SaaS varsa footer ve kayıt adımında link; onay kutusu boş | [legal-privacy-compliance.md](references/legal-privacy-compliance.md) |
| 3 | Çerez Onayı & Consent Mode | KRİTİK | Onaydan önce yalnızca zorunlu çerez; Kabul ve Reddet eşit; Consent Mode v2 varsayılan `denied` | `node .agent/skills/prelaunch-audit/scripts/consent-check.mjs <URL>` |
| 4 | Net CTA | YÜKSEK | İlk mobil ekranda tek birincil eylem, fiil içeren net etiket, çalışan hedef URL | Bu dosya § Madde 4 |
| 5 | Mobil Görünüm & Reflow | KRİTİK | 320-430 px arası yatay kaydırma yok, fontlar ≥ 16 px, zoom kısıtlanmamış | Bu dosya § Madde 5 |
| 6 | Formların Çalışması | KRİTİK | Uçtan uca teslimat kanıtı, spam koruması (turnstile/honeypot), sunucu doğrulaması | Bu dosya § Madde 6 |
| 7 | Kırık Linkler & Çapalar | YÜKSEK | İç linklerde 0 hata; `#`, `javascript:void(0)` veya staging linki yok | `python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py` |
| 8 | Site Hızı (Core Web Vitals) | YÜKSEK | Mobil lab: LCP ≤ 2.5 sn, CLS ≤ 0.1, TBT ≤ 200 ms; görsellerde modern format | Bu dosya § Madde 8 |
| 9 | Erişilebilirlik (WCAG 2.2 AA) | KRİTİK | axe taramasında kritik/ciddi hata 0; tüm akışlar klavye ile tamamlanabiliyor | `node .agent/skills/prelaunch-audit/scripts/axe-runner.mjs <URL>` |
| 10 | Analytics Entegrasyonu | YÜKSEK | Yalnızca onay sonrası çalışır, prod/staging anahtarları ayrı, kişisel veri maskeli | [legal-privacy-compliance.md](references/legal-privacy-compliance.md) |
| 11 | Meta Başlık ve Açıklama | YÜKSEK | Ham HTML'de her sayfada özgün `<title>` (50-60 kar.) ve description (120-155 kar.) | `node .agent/skills/prelaunch-audit/scripts/html-audit.mjs <URL>` |
| 12 | sitemap.xml | YÜKSEK | Yalnızca 200 dönen, kanonik HTTPS URL'ler; doğru ISO 8601 lastmod; robots'ta referans | `python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py` |
| 13 | robots.txt & AI Botlar | KRİTİK | Prod'u engellemeyen (`Disallow: /` olmayan), Sitemap tanımlı, AI bot politikası net | [seo-and-discoverability.md](references/seo-and-discoverability.md) |
| 14 | Canonical URL | KRİTİK | Her sayfada mutlak HTTPS self-canonical, www/çıplak domain tekliği sağlanmış | `node .agent/skills/prelaunch-audit/scripts/html-audit.mjs <URL>` |
| 15 | Görsel Alt Metinleri | ORTA | Her `<img>` etiketinde anlamlı `alt` (dekoratifte `alt=""`), dosya adı basılmamış | `node .agent/skills/prelaunch-audit/scripts/html-audit.mjs <URL>` |
| 16 | Sık Sorulan Sorular (SSS) | ORTA | Gerçek sorulardan oluşan, görünür ve erişilebilir akordeon/liste | [seo-and-discoverability.md](references/seo-and-discoverability.md) |
| 17 | Özel 404 Sayfası | YÜKSEK | Var olmayan adreste gerçek 404 HTTP kodu ve markalı yönlendirici sayfa (soft-404 yok) | [seo-and-discoverability.md](references/seo-and-discoverability.md) |
| 18 | Sosyal Paylaşım (OG/Twitter)| ORTA | `og:title`, `og:description`, `og:image` (1200x630 mutlak URL) eksiksiz | `node .agent/skills/prelaunch-audit/scripts/html-audit.mjs <URL>` |
| 19 | Favicon Seti | ORTA | `favicon.ico`, SVG, `apple-touch-icon` (180x180) ve manifest; default logo yok | `python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py` |
| 20 | llms.txt (Opsiyonel P3) | DÜŞÜK | Yalın markdown özet ve dokümantasyon indeksi | [seo-and-discoverability.md](references/seo-and-discoverability.md) |

---

## Koşullu Ek Maddeler (21-27)

Yalnızca site türüne uyuyorsa uygulanır; uymuyorsa raporda `N/A + gerekçe` belirtilir.

| # | Madde | Koşul | Geçme Kriteri | İlgili Referans |
|---|-------|-------|---------------|------------------|
| 21 | Google Search Console | Her site | Domain mülkiyeti doğrulanmış, sitemap gönderilmiş, Sayfalar raporu hazır | [trust-and-local-structure.md](references/trust-and-local-structure.md) |
| 22 | İç Linkleme & Yetim Sayfalar | Her site | Yetim sayfa 0, taranabilir `<a href>`, önemli sayfalara ≤ 3 tık | [trust-and-local-structure.md](references/trust-and-local-structure.md) |
| 23 | Teşekkür Sayfası & PRG | Form/Ödeme | Form sonrası Post-Redirect-Get (PRG), `noindex`, sitemap dışı | [trust-and-local-structure.md](references/trust-and-local-structure.md) |
| 24 | Structured Data (JSON-LD) | Her site | Organization/WebSite şemaları ham HTML'de, self-serving rating yok | [trust-and-local-structure.md](references/trust-and-local-structure.md) |
| 25 | Harita, Adres, LocalBusiness | Fiziksel konum | NAP tutarlılığı, harita iframe onay arkasında, LocalBusiness JSON-LD | [trust-and-local-structure.md](references/trust-and-local-structure.md) |
| 26 | Müşteri Yorumları | Yorum varsa | Gerçek satın alma doğrulaması (TR m.28/B), filtresiz, sahte yorumsuz | [trust-and-local-structure.md](references/trust-and-local-structure.md) |
| 27 | Sticky Telefon CTA | Hizmet siteleri | Mobilde ≥ 44x44 px dokunma alanı, `tel:` linki, içeriği örtmüyor | [trust-and-local-structure.md](references/trust-and-local-structure.md) |

---

## Madde 4 - Net CTA Detayları
- Her sayfada odaklanılan tek bir birincil eylem olmalıdır.
- Buton etiketi jenerik "Gönder" veya "Tıklayın" yerine fiil içeren "Teklif Al", "Ücretsiz Dene", "Randevu Oluştur" biçiminde olmalıdır.
- Mobil ilk ekranda görünür olmalı ve `cta_click` analitik olayı göndermelidir.

## Madde 5 - Mobil Görünüm Detayları
- `<meta name="viewport" content="width=device-width, initial-scale=1">` zorunludur; `user-scalable=no` yasaktır.
- 320 px genişlikte yatay kaydırma çubuğu çıkmamalıdır.
- Gövde ve form metinleri iOS otomatik yakınlaştırmasını önlemek için ≥ 16 px olmalıdır.

## Madde 6 - Formların Çalışması Detayları
- Formlar yalnızca arayüzde değil, uçtan uca (e-posta veya veritabanı kaydıyla) doğrulanmalıdır.
- Spam botlarına karşı Cloudflare Turnstile veya honeypot alanı bulunmalıdır.
- Buton çift tıklamaya karşı devre dışı bırakılmalı, kullanıcıya erişilebilir yükleniyor durumu gösterilmelidir.

## Madde 8 - Site Hızı Detayları
- LCP elemanında (hero görseli) `fetchpriority="high"` kullanılmalı, LCP görseline `loading="lazy"` konulmamalıdır.
- CLS önlemek için tüm görsel ve iframe'lerde `width`/`height` veya CSS `aspect-ratio` tanımlanmalıdır.

---

## Örnek Rapor Çıktısı (`PRELAUNCH-REPORT.md`)

```markdown
# Canlıya Alma Raporu - {site} - {tarih}
**Karar:** GO | GO (koşullu) | NO-GO (Blocker varsa kesinlikle NO-GO)
**Site Profili:** {tür, hedef pazar, teknoloji yığını}

| # | Madde | Durum | Kanıt / Komut Çıktısı | Sahip / Aksiyon |
|---|-------|-------|------------------------|-----------------|
| 1 | Gizlilik Politikası | PASS | /gizlilik-politikasi (KVKK m.10 uyumlu) | Tamamlandı |
| 3 | Çerez Onayı | PASS | consent-check.mjs (Onay öncesi 0 tracker) | Tamamlandı |
| 13| robots.txt | PASS | prelaunch_checker.py (Disallow: / yok) | Tamamlandı |
...
```
