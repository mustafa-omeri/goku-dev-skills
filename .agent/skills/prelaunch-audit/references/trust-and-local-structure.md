# Yapı, Yerel Güvenilirlik ve Dönüşüm Mimarisi (Maddeler 21-27)

Son veri doğrulaması: 26 Ekim 2026. Bu maddeler projenin türüne ve iş modeline göre koşullu olarak uygulanır. Koşul sağlanmıyorsa denetim raporunda `N/A + gerekçe` yazılır.

---

## Madde 21 - Google Search Console & Webmaster Doğrulaması

- **Koşul:** Her web sitesi için zorunludur.
- **Uygulama:**
  - DNS TXT kaydı ile Alan Adı (Domain) mülkiyeti doğrulaması tercih edilir (`NEEDS-HUMAN`).
  - Alternatif olarak HTML etiket doğrulayıcısı `<meta name="google-site-verification" content="...">` şablona eklenir.
  - Yayın günü `sitemap.xml` GSC üzerinden teslim edilir ve ana sayfa için URL Denetimi ile canlı getirme testi yapılır.

---

## Madde 22 - İç Linkleme ve Yetim Sayfa (Orphan Page) Engeli

- **Koşul:** Her site.
- **Standartlar:**
  - İndekslenmesi istenen hiçbir sayfa yetim (gelen iç linki sıfır olan) kalmamalıdır.
  - Önemli dönüşüm ve ürün/hizmet sayfalarına ana sayfadan en fazla **3 tıklama** ile ulaşılabilmelidir.
  - Linkler taranabilir `<a href="...">` biçiminde olmalı; yalnızca JavaScript click olaylarına bağlanmamalıdır.
  - Anchor metinleri "buraya tıklayın" yerine "Kurumsal Web Tasarım Hizmetleri" gibi bağlamsal ve açıklayıcı olmalıdır.

---

## Madde 23 - Teşekkür Sayfası ve Post-Redirect-Get (PRG)

- **Koşul:** Form, rezervasyon, teklif alma veya ödeme adımı içeren siteler.
- **Standartlar:**
  - Form gönderimi sonrası sayfa yenilendiğinde mükerrer form ve mükerrer dönüşüm olayı gitmemesi için **Post-Redirect-Get (PRG)** deseni uygulanmalı veya yerinde tek seferlik başarı bayrağı kullanılmalıdır.
  - `/tesekkurler` sayfası arama motorlarına kapatılmalı (`noindex`), sitemap'e dahil edilmemelidir. Ancak robots.txt ile `Disallow` edilmemelidir (Google `noindex` etiketini okuyabilmelidir).
  - URL üzerinde e-posta veya kişisel veri taşınmamalıdır (`/tesekkurler?email=...` YASAKTIR).

---

## Madde 24 - Yapılandırılmış Veri (JSON-LD) ve Breadcrumb

- **Koşul:** Organization/WebSite her sitede; BreadcrumbList gerçek hiyerarşisi olan sitelerde.
- **Standartlar:**
  - Sayfada görünür olan içerikle %100 uyumlu JSON-LD şemaları kullanılmalıdır.
  - `Organization` (name, url, logo, sameAs).
  - İşletmenin kendi ana sayfasında kendi hakkında yıldız puanlaması yapması (Self-serving `AggregateRating`) Google kurallarınca yasaklanmıştır; zengin sonuç cezası almamak için eklenmemelidir.

---

## Madde 25 - Google Harita, Fiziksel Adres ve LocalBusiness

- **Koşul:** Fiziksel ofisi, mağazası veya hizmet bölgesi olan işletmeler.
- **Standartlar:**
  - **NAP Tutarlılığı:** İsim (Name), Adres (Address) ve Telefon (Phone) sitede, Google İşletme Profilinde ve resmi kayıtlarda birebir aynı yazılmalıdır.
  - Harita iframe'leri üçüncü taraf çerez ve veri aktarımı sayıldığından, çerez onayı arkasında veya statik harita görseli + harita yönlendirme linki olarak sunulmalıdır.
  - Telefon numaraları mobil tıklanabilir `tel:+90...` formatında olmalıdır.

---

## Madde 26 - Müşteri Yorumları ve Reklam Kurulu 28/B Mevzuatı

- **Koşul:** Sitede müşteri yorumları veya referansları (testimonials) sergileniyorsa.
- **Yasal Mevzuat (Ticaret Bakanlığı RG 33297, m.28/B):**
  1. Değerlendirmeleri yalnızca mal veya hizmeti **gerçekten satın almış tüketiciler** yapabilir. Satın alma doğrulaması (sipariş no, üyelik) zorunludur.
  2. Olumlu veya olumsuz ayrımı yapılmaksızın yorumlar en az bir yıl boyunca yayımlanmalıdır. Olumsuz yorumların haksız yere gizlenmesi ağır idari para cezalarına (2 Milyon TL üzeri yaptırımlar) tabidir.
  3. Yapay veya satın alınmış yorum yayımlamak kesinlikle yasaktır.
  4. Referanslarda kişi adı ve fotoğrafı kullanılıyorsa KVKK m.10 kapsamında aydınlatma ve açık izin belgesi bulunmalıdır.

---

## Madde 27 - Mobil Sticky İletişim CTA'sı

- **Koşul:** Telefonla veya WhatsApp ile hızlı randevu/satış alan hizmet siteleri.
- **Standartlar:**
  - Mobilde başparmak erişim bölgesinde (thumb zone) en az 44x44 piksel tıklama alanına sahip `tel:` butonu.
  - Sayfa içeriğini ve form alanlarını örtmemeli, WCAG 2.4.11 odak görünürlüğünü engellememelidir.
