# Organik Trafik Düşüşü & Analitik Teşhis Protokolü (GSC & GA4)

> **Kaynak:** `nowork-studio/notfair-plugin` Cerrahi Entegrasyonu (`plans/notfair-plugin.md`)  
> **Kapsam:** Google Search Console (GSC) ve Google Analytics 4 (GA4) verilerini çapraz karşılaştırarak organik trafik kayıplarının kök nedenini izole etme disiplini.

---

## 1. Düşüşün Şekli ve Zaman Çizelgesi (Semptom İzolasyonu)

Trafik düşüşü analiz edilirken ilk adım zaman aralığının şeklidir:

| Düşüş Şekli | Olası Kök Neden | Doğrulama Yolu |
|---|---|---|
| **Uçurum Düşüşü (Cliff Drop - 24-48 saatte %80+)** | Teknik / İndeksleme Hatası | `robots.txt`, noindex meta tag, DNS/SSL çökmesi, sunucu 5xx hataları |
| **Kademeli / Merdiven Düşüşü (Step Drop - 1-2 haftada)** | Algoritma Güncellemesi (Core Update) | Google Search Status Dashboard, SERP volatilite araçları (Semrush Sensor) |
| **Yavaş Erime (Slow Bleed - 2-3 ayda)** | İçerik Bayatlaması / Rakip Üstünlüğü | Arama niyeti (intent) kayması, rakiplerin yeni içerik kümesi (cluster) üretmesi |
| **Tekil Sayfa Düşüşü (Single Page Drop)** | Kanibalizasyon / Canonical Hatası | Aynı sorgu için yarışan yeni şirket içi sayfalar, yanlış canonical bağlantısı |

---

## 2. GSC ve GA4 Çapraz Doğrulama Matrisi

Tek başına GA4 veya GSC'ye bakmak yanıltıcıdır:

1. **GSC Gösterim (Impression) Stabil, Tıklama (Clicks) Düşmüş:**
   - Sayfa sıralamasını koruyor ancak SERP'te tıklama oranı (CTR) düşmüş.
   - **Kök Neden:** Rakip daha iyi bir meta başlık yazmış veya Google SERP'e yeni AI Overview / Rich Snippet yerleştirmiş.
2. **GSC Gösterim ve Tıklama Beraber Düşmüş:**
   - Sayfa sıralama kaybetmiş veya indeks dışına çıkmış.
   - **Kök Neden:** Algoritma güncellemesi, teknik SEO hatası veya arama talebinin sezonluk azalması.
3. **GSC Tıklama Normal, GA4 Organik Oturum Düşmüş:**
   - Kullanıcılar siteye geliyor ancak analitik scripti çalışmıyor.
   - **Kök Neden:** GA4 Consent Mode v2 / çerez engeli, script yüklenme hatası, Cloudflare bot koruması engeli.

---

## 3. Teşhis ve Eylem Akışı

1. **Adım 1 - Teknik Sağlık Kontrolü:**
   - Sayfanın canlı HTML çıktısında `<meta name="robots" content="noindex">` var mı?
   - `robots.txt` sayfayı engelliyor mu?
   - HTTP durum kodu 200 mü? Canonical URL kendine mi işaret ediyor?
2. **Adım 2 - Sorgu ve Sayfa Segmentasyonu:**
   - GSC'de `Tarih: Son 28 gün vs Önceki dönem` karşılaştırması yapın.
   - Kaybın %80'ini üreten ilk 5 URL'yi ve ilk 10 anahtar kelimeyi izole edin.
3. **Adım 3 - Arama Niyeti Denetimi:**
   - İlgili anahtar kelimeyi gizli sekmede aratın: İlk 3 sıradaki rakiplerin formatı ne (liste mi, rehber mi, araç mı)? Bizim içeriğimiz format olarak geride mi kalmış?
4. **Adım 4 - Cerrahi Düzeltme:**
   - Başlık ve H2'leri arama niyetine göre güncelleyin.
   - Eksik alt başlıkları ve güncel verileri ekleyin.
   - GSC üzerinden "URL Denetimi -> Dizin Oluşturulmasını İste" yapın.
