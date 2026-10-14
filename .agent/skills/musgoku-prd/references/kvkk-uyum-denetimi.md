# KVKK / Gizlilik Uyum Denetimi — Referans

> **Ne zaman açılır:** §2 Adım 0'daki **veri ekseni** "EVET" cevaplandığında.
> Veri ekseni: "Bu iş kişisel veri topluyor, saklıyor, işliyor **ya da** toplayan bir sisteme
> dokunuyor mu?" — cevap `EVET` ise bu referans okunur ve §20.1 raporu üretilir.
> Cevap `HAYIR` ise §21'e gerekçesiyle yazılır.
>
> **Bu referans, kapı satırlarını (§20 Tier A-2) tanımlar ve nasıl kanıtlanacağını anlatır.**
> Üretilen kanıt PRD'nin §20.1'ine yazılır.

---

## 0. Bu referansın tek kuralı

**Kanıt yoksa `Uyumlu` yazılmaz.** Tahmin yürütmek hukuki denetimde en pahalı hatadır:
denetimi geçmiş görünen ama gerçekte eksik olan bir rapor, hiç rapor vermekten kötüdür —
çünkü işletme "kontrol edildi" sanır. Emin olmadığın her yerde **`Doğrulanmalı`** yaz.

Bu, §2b'deki `[VERIFY]` etiketinin rapor düzeyindeki karşılığıdır. `Doğrulanmalı`
sütunu, "kontrol edilmedi" demektir — denetimi bitirmiş gibi göstermek için bu sütun
keyfî olarak temizlenmez.

### Durum sözlüğü — dört değer, başka yok

| Durum | Ne demek | Kabul kanıtı |
|---|---|---|
| **Uyumlu** | Gereksinim karşılanıyor **ve** kanıtı raporda | Kod satırı, sayfa URL'si, ölçüm kaydı |
| **Eksik** | Gereksinim hiç yok | Yokluğun kendisi kanıttır (`dosya:satır` = —) |
| **Uyuşmazlık** | İki kanıt birbiriyle çelişiyor | Her iki kanıt da raporda (metin ↔ site, kod ↔ metin) |
| **Doğrulanmalı** | Kanıt görülemedi veya koda gömülü değil | Kim, ne zaman, nasıl kontrol edecek |

**"Kötü", "riskli", "olması gerekir" bir durum değildir.** Durum bir gözlemdir; yorum
"Ne yapılmalı" sütununa yazılır.

---

## 1. Uygulama tipi matrisi (6 tip)

Tip, denetimlerin **hangi kadarının zorunlu** olduğunu belirler — hangi denetimin
**uygulanmayacağını** değil. Uygulanmayan denetim `Opsiyonel` olur ve gerekçesi bir
cümlede yazılır (bkz. §20 "Satır silme" kuralı).

`Z` = Zorunlu · `Ş` = Şartlı · `O` = Opsiyonel (gerekçeyle)

| Uygulama tipi | KV-01 | KV-02 | KV-03 | KV-04 | KV-05 | KV-06 | En sık kaçırılan tek madde |
|---|---|---|---|---|---|---|---|
| **Statik / kurumsal web** (landing, kurumsal site, portfolyo, dokümantasyon) | Z | Z | Z | Z | Ş | O | Analytics/pixel'in metinde **hiç anılmaması** — kod yüklü, izleme yapıyor, gizlilik metni sessiz |
| **Web uygulaması** (üyelik, giriş, panel) | Z | Z | Z | Z | Z | Z | Loglarda düz metin e-posta / telefon / şifre; ve **SaaS'ta veri sorumlusu–veri işleyen ayrımının** hiç yazılmaması |
| **E-ticaret / ödeme** | Z | Z | Z | Z | Z | Z | Ödeme sağlayıcısının (iyzico, PayTR, Stripe) "aktarılan taraf" sayılmaması |
| **Backend / API servisi** (kullanıcıya görünmez) | Z | Z | Ş | O | O | Z | Saklama süresi ve **yetkisiz uç nokta**; log maskeleme yok sayılıyor |
| **Mobil** (iOS / Android) | Z | Z | Z | Ş | O | Z | İzin ↔ KVKK eşlemesi ve **üçüncü taraf SDK'ların** topladığı veri (uygulama içi SDK envanteri) |
| **WordPress / hazır tema** | Z | Z | Z | Z | Z | Ş | **Eklenti listesi = dış servis listesi** — eklenti eklendi, metin güncellenmedi |

**SaaS / çok kiracılı ürün ayrı tip değildir**, "Web uygulaması" tipinin en kritik
varyantıdır ve şu üçünü ayrıca zorunlu kılar:

1. **Veri sorumlusu kimdir, veri işleyen kimdir?** Çok kiracılı SaaS'ta kiracı veri sorumlusu,
   sağlayıcı veri işleyendir (veya tersi). Bu ayrım aydınlatma metninde ve sözleşmede
   **yazmıyorsa** denetim `Eksik`'tir — hangi rolü aldığınızı bilmiyorsanız aydınlatma
   metni de bilemezsiniz.
2. **Alt işleyenler listesi** — alt hosting, ödeme, e-posta, SMS sağlayıcıları.
3. **Saklama ve silme** — hesap kapandığında kiracının verisi ne zaman silinir.

### Tip tespiti koddan nasıl yapılır

| İpucu | Tip |
|---|---|
| `next.config` yok, `index.html` var, sunucu tarafında render yok | Statik/kurumsal web |
| `login`, `register`, `session`, `auth` modülü/endpoint'i var | Web uygulaması |
| `cart`, `checkout`, `order`, `payment`, `stripe`/`iyzico`/`PayTR` | E-ticaret |
| Yalnız API/Controller/Service var, arayüz yok, kullanıcı içeriden geliyor | Backend/API |
| `Info.plist`, `AndroidManifest.xml`, `Podfile`, `build.gradle` | Mobil |
| `wp-content`, `functions.php`, `wp-config.php` | WordPress |

---

## 2. KV-01 — Veri envanteri

**Amaç:** Kişisel veri toplayan **her** noktayı bul ve envantere yaz. Eksik envanter,
eksik aydınlatma metni demektir.

Aranacak toplama noktaları (hepsi):

- Formlar (iletişim, teklif, kayıt, giriş, yorum, destek talebi, anket)
- Üyelik / hesap açma (profil alanları, şifre geri dönüşü)
- Sipariş / ödeme (adres, kart, telefon)
- Bülten / kampanya aboneliği (**tek tıkla** kayıt özellikle riskli — bkz. KV-04)
- Randevu / rezervasyon
- Destek kanalları: **WhatsApp**, canlı destek widget'ı, e-posta, iletişim formu
- Yorum / yıldız puanlama, IP kaydı, cihaz parmak izi
- Dosya yükleme (avatar, belge, ödeme kanıtı)
- Kredi başvurusu / sözleşme / beyanname (varsa — **en yüksek riskli sınıf**)

Her nokta için kaydedilecek alanlar:

| Alan | Açıklama |
|---|---|
| **Toplayan nokta** | Form adı / endpoint (dosya:satır) |
| **Alanlar** | Hangi kişisel veri alanları (ad, e-posta, telefon, adres, TCKN, KVKK No, IP, konum, sağlık, özel nitelikli veri) |
| **Nereye gidiyor** | Veritabanı (hangi tablo/şema) · e-posta servisi · WhatsApp/API · CRM · analytics · ödeme sağlayıcı |
| **Hukuki sebep** | Sözleşme · açık rıza · kanuni yükümlülük · meşru menfaat · **özel nitelikli veri varsa ayrıca açık rıza** |
| **Saklama süresi** | Ne kadar süre, kim siler |
| **Aktarım** | Yurt dışı mı, hangi ülke/servis |

> **Özel nitelikli veri (KVKK m.6):** sağlık, ırk, etnik köken, din, siyasi görüş, sendika
> üyeliği, biyometrik, genetik, cinsel hayat. Bunlar **ayrı ve açık rıza** ister; "hizmetin
> çalışması için gerekli" gerekçesi kabul edilmez. Form tasarımında hiç sorulmamalı.

---

## 3. KV-02 — Dış servisler ve veri aktarımı

Her dış servis için **üç** sütun zorunludur: hangi veri gidiyor, **hangi ülkede işleniyor**,
hangi amaçla. "Veri gönderilmiyor" satırı bile yazılır — çünkü asıl soru "var mı" değil,
"farkında mısınız"dır.

Kontrol edilecek servis listesi (kısmi — bunlardan hangisi kullanılıyorsa):

| Kategori | Servisler |
|---|---|
| Ölçümleme | Google Analytics 4, Google Tag Manager, Mixpanel, Amplitude, Plausible, Matomo |
| Reklam / piksel | Meta (Facebook) Pixel, Conversions API, TikTok Pixel, LinkedIn Insight, Google Ads |
| Oturum kaydı / ısı haritası | Microsoft Clarity, Hotjar, FullStory, LogRocket |
| Harita / konum | Google Maps, Mapbox, Yandex Maps, OpenStreetMap |
| Video | YouTube/Vimeo gömülü oynatıcı |
| Harici font | Google Fonts, Adobe Fonts, Bunny Fonts — **karakter seçici IP + kullanıcı aracı gönderir** |
| Sosyal / paylaşım | Paylaşım düğmeleri, gömülü gönderi (gönderi butonu ilk yüklemede istek atar) |
| Canlı destek | WhatsApp widget, Crisp, Intercom, Tawk.to, Zenvir |
| Form/CRM | Formspree, HubSpot, Mailchimp, Brevo, Google Forms |
| Ödeme | iyzico, PayTR, Param, Stripe, PayPal |
| E-posta | Resend, SendGrid, Mailgun, Postmark |
| Hosting / CDN | Vercel, Netlify, Cloudflare, AWS, Hetzner, DigitalOcean |
| Harici API | OpenAI, Anthropic, OCR, harita, kargo takip, WhatsApp Business API |

> **Yurt dışı aktarımı** (KVKK m.9) bir hizmet seçimi meselesi değil, **hukuki şart**tır:
> veri yurt dışına aktarılıyorsa metinde **hangi ülkeye** aktarıldığı ve **hukuki sebep**
> yazılır. "Bulut" yazmak aktarımı açıklamaz. `[VERIFY: sağlayıcının veri işleme merkezi
> ülkesi — sözleşme/servis şartları incelenmeli]`

> **Piksel ve analytics'te "veri gönderilmiyor" yanılgısı:** Sayfa adresi, yönlendirme,
> form alanları (hash'lenmiş olsa bile IP ile eşleşebilir), oturum kayıtları, ekran
> kaydıleri ve fare hareketleri tipik olarak gönderilir. "Sadece toplam ziyaretçi sayısı"
> ifadesi teknik olarak doğru, hukuki olarak yanıltıcıdır.

---

## 4. KV-03 — Aydınlatma metni ↔ çerez politikası karşılaştırması

Bu denetimin çekirdeği **şablon tuzağıdır:** metinde olup sitede olmayan (veya tam tersi)
her ifade, uyumsuzluk sayılır. Karşılaştırma iki yönlüdür ve **mutlaka iki yönde de yapılır**:

- **A → B:** Metinde geçen her veri veya servis, sitede gerçekten var mı?
- **B → A:** Sitede çalışan her veri toplama veya dış servis, metinde geçiyor mu?

### Zorunlu başlıklar (KVKK m.10)

| Başlık | Eksikse |
|---|---|
| Veri sorumlusu kim, adresi, iletişimi | Metin hukuki olarak geçersiz sayılır |
| Hangi kişisel veriler işleniyor | KV-01 envanteriyle karşılaştırılır |
| İşleme amaçları (amaç + amaç dışı kullanım yasağı) | "hizmet kalitesini artırmak" tek başına amaç değildir |
| Hukuki sebep (madde numarasıyla) | Sözleşme / açık rıza / kanuni yükümlülük / meşru menfaat |
| Aktarılan taraflar ve **yurt dışı aktarımı** | Ülke + hukuki sebep yazılmazsa eksik |
| Veri güvenliği önlemleri | |
| Saklama süresi veya yoksa belirlenme ölçütü | |
| **İlgili kişinin hakları (m.11)** | Aşağıdaki liste |

### md.11 hakları — hepsi yazıyor mu?

- Bilgi talep etme · verilerinin düzeltilmesini/ **silinmesini** isteme ·
- işlemenin sınırlandırılmasını isteme · zararın giderilmesini talep etme ·
- **verilerinin aktarıldığı üçüncü kişileri öğrenme**
- **hukuki sebebin değişmesi hâlinde yeniden bilgilendirme**
- **otomatik yöntemle işleme varsa bunun sonucu**

> Hak listesi kopyalanmış ama **uygulamada karşılığı yoksa** bu bir `Uyuşmazlık`'tır:
> "silme hakkınız var" yazısı, silme endpoint'i/akışı yoksa yanlış beyandır.

### Çerez politikası

Yalnız çerez adı listesi **yetmez**: her çerez için **amaç, süre ve sağlayıcı** gerekir.
Reklam/pazarlama çerezleri için ayrıca **kategori bazlı** onay gerekir.

> **Çerez politikası metni varsa çerez onayı da olmalıdır, tersi de geçerlidir.** Biri varsa
> diğeri yoksa `Uyuşmazlık` — en sık atlanan tutarsızlıktır.

### Sayfa yoksa

Politika/aydınlatma sayfası **yoksa** boş bırakma: satır `Eksik` olur ve kanıt
`Sayfa bulunamadı` yazılır. "Hukuk ekibi hazırlıyor" bir durum değil, bir geçici nottur ve
`Doğrulanmalı` + sahip + tarih ile yazılır.

---

## 5. KV-04 — Onay kutuları

Dört soru, dördü de `Eksik` ise yayın engelidir:

| # | Soru | Uyumlu | Uyumsuz |
|---|---|---|---|
| 1 | **Aydınlatma ve açık rıza tek kutuda mı?** | Ayrı kutular veya metin okunabilir bağlantı | Tek `✓` ile ikisi birden |
| 2 | **Sadece mesaj cevabı için rıza zorunlu mu?** | Cevap vermek serbest; rıza teklif değil ölçüt | "Mesajınızı gönderebilmek için ✓ işaretleyin" |
| 3 | **Pazarlama izni ayrı ve isteğe bağlı mı?** | Ayrı, boş bırakılabilir, önceden işaretli **değil** | Zorunlu · önceden işaretli · "kaldırmak için zorla" |
| 4 | **Onay kanıtı saklanıyor mu?** (metin sürümü, tarih, IP, nasıl) | Kayıt var | Kanıt yok → geri dönüşü kanıtlanamaz |

> **Neden ayrı kutular zorunlu:** aydınlatma metnini **göstermek** ile açık rıza
> **vermek** farklı fiillerdir. Tek kutuda ikisi birleştirilirse rıza, kanıtlanabilir
> ve ayrılabilir biçimde alınmış sayılmaz — ve geri alınabilir olmaz.
>
> **Önceden işaretili kutu** açık rızadır? Değildir. Sadece "işaretli kutu = onay"
> desenini kullanan CMP'ler, kullanıcı hiçbir şeye dokunmadan rıza sayılır. Bu, açık
> değil örtülü rızadır ve reddedilebilir değildir.

> **Sadece iletişim formunda:** e-posta/telefon ile soru-cevap ("dönüş yapalım", "sizi
> arayalım") hizmetin ifası için zorunlu — burada rıza kutusu şart değildir, hatta
> gereksizdir. Buna karşılık **pazarlama** (bülten, kampanya) için rıza şarttır.
> İkisini tek kutuda birleştirmek en yaygın hatadır.

> **Hukuki dayanak:** Açık rıza, KVKK m.3 (tanım: "özgür iradeyle açıklanan rıza") ve
> m.5/1'in **özel nitelikli olmayan** veriler için öngördüğü şarttır.
> `[VERIFY: açık rıza için yazılı olma şartı ve geri alma yükümlülüğünün güncel
> uygulaması — hukuk onaylasın]`

---

## 6. KV-05 — Çerez onayı: gerçekten engelleniyor mu?

**Bir banner çizmek, onay almak değildir.** Kontrol edilecek asıl şey reddedildiğinde
**hiçbir isteğin gitmemesi**.

### Kodda aranacaklar

| Kontrol | Doğru | Yanlış |
|---|---|---|
| Varsayılan izin | `setDefaultConsentState({ analytics_storage: 'denied', ad_storage: 'denied', ... })` | Tanım yok → tarayıcı çerezi **izinli** sayar |
| Karar anında güncelleme | `updateConsentState(...)` / `gtag('consent', 'update', ...)` | Banner var, izin hiç güncellenmiyor |
| Etiket yükleme sırası | İzin kararı **etiketten önce** | GTM/gtag yükleniyor, banner sonra çıkıyor |
| Tetikleyici | GTM'de `Consent Initialization` ile varsayılan; izleme etiketleri consent sinyaline bağlı | "Şu an rıza yok" kontrolü yok |
| Reddin kalıcılığı | Karar saklanır, sayfa yenilense de uygulanır | Her sayfada tekrar sorulur veya karar kaybolur |

> **Yaygın tuzak — `addConsentListener`:** Bu listener yalnızca izin
> `denied ↔ granted` arasında değiştiğinde tetiklenir; **`unset → granted`
> geçişinde tetiklenmez**, çünkü `unset` "granted" sayılır. "Listener var ama analiz
> hiç gelmiyor" şikâyetinin en sık nedeni budur. Varsayılan değer `denied` *değilse*
> listener sessizce hiç çalışmaz. Reddeden kullanıcı yanlışlıkla "granted" sayılır.
>
> **Yaygın tuzak — gelişmiş Analytics:** Analytics'in *gelişmiş* uygulamasında
> `analytics_storage: denied` olsa bile çerezsiz **kimliksiz ölçüm gönderilir**. Bu
> teknik olarak izinli, ama "Reddet dedim, hiçbir şey gitmiyor" testi kırılır.
> Denetimde hangi uygulamanın seçildiği ayrıca sorulur.

### "Reddet" akışı — testi

Reddetme sonrası şu **dördü** de gerçekleşmeli:

1. İzin çerezi `granted` değil (banner tekrar belirmiyor)
2. Network panelinde analytics/pixel/harici istek **hiç** yok
3. Sunucu erişim logunda o oturuma ait üçüncü taraf isteği yok
4. Tarayıcıda çerez listeleniyorsa **yalnız zorunlu** çerezler var

Bunlardan biri tutmuyorsa durum `Uyuşmazlık`'tır (kullanıcıya "reddedebiliyorum" deniyor
ama reddedilmiyor).

> **Kabul ve red tek tıkla:** "Kabul et" ve "Reddet" düğmeleri eşit görünür büyüklükte
> ve eşit konumda olmalı. "Reddet" küçük, gri, köşede ise KVKK m.5/1 gereği
> rıza **serbest iradeyle** alınmış sayılmaz.

---

## 7. KV-06 — Güvenlik

| # | Kontrol | Aranan |
|---|---|---|
| 1 | **Loglarda kişisel veri** | E-posta, ad, telefon, adres, TCKN, şifre, token **düz metin** loglanıyor mu? |
| 2 | **Hız sınırı** | Form gönderme endpoint'inde rate limit var mı? |
| 3 | **Bot koruması** | Captcha veya **honeypot** (görünmez alan — doldurulursa istek reddedilir) |
| 4 | **API anahtarı** | Koda gömülü anahtar var mı (istemci tarafı bundle'ı okunabilir) |
| 5 | **Yetkisiz erişim** | Kişisel veri döndüren uç nokta kimlik doğrulaması olmadan açık mı |
| 6 | **Saklama yolu** | Yedek, log, cache ve dosya sisteminde de kişisel veri kalıyor mu |

> **Log tuzağı:** `console.log('Form gönderildi', formData)` veya
> `logger.info("user", user)` kalıcı düz metin kişisel veri yazar. Üstelik bunlar
> üçüncü taraf hata izleme servislerine (Sentry, LogRocket) otomatik gider. Maskeleme
> (`a***@b.com`) veya **hiç yazmama** gerekir; correlation id ve alan **adları** yeterlidir.
>
> **Anahtar tuzağı:** İstemci tarafı bir "public" anahtarın gömülü olması (Stripe publishable
> key, Firebase yapılandırması) tasarım gereğidir ve `Eksik` sayılmaz. **Gizli** anahtarın
> bundle'a girmesi `Uyuşmazlık`'tır ve anahtar **rotasyon** gerektirir.
>
> **Açık uç nopta tuzağı:** `GET /api/orders/{id}` yalnız `id` tahmin edilebiliyorsa ve
> kimlik doğrulama/ yetki kontrolü yoksa **kabul edilebilir bir bulgu değildir** —
> `Uyuşmazlık` ve derhal kapatılır. Bulgu, şiddet ve düzeltme prosedürüyle birlikte yazılır.

---

## 8. Rapor sözleşmesi — çıktı formatı

Denetim raporu PRD'nin **§20.1**'ine şu sırayla yazılır. Bölüm başlığı, madde, dosya
veya kanıt, durum, gereken işlem, sorumlu ve hedef tarihi olmadan kapanmaz.

### 8.1 Ana denetim tablosu

```markdown
| # | Madde | Dosya:satır | Durum | Ne yapılmalı |
|---|---|---|---|---|
| KV-01 | Veri envanteri — iletişim formu ad, e-posta, telefon topluyor | `src/features/contact/ContactForm.tsx:24-38` | Uyumlu | — |
| KV-01 | Veri envanteri — randevu formunda doğum tarihi (özel nitelikli olabilir) | `src/features/booking/BookingForm.tsx:51` | Eksik | Alanı kaldır veya m.6 açık rıza metnini ekle |
| KV-02 | Meta Pixel yükleniyor, aydınlatma metninde "reklam" geçmiyor | `index.html:31` ↔ `/gizlilik` | Uyuşmazlık | Metne ekle veya pikseli onay kutusuna bağla |
| KV-03 | Aydınlatma metninde md.11 hakları yok | `/gizlilik` | Eksik | Hak listesini metne ekle |
| KV-04 | Pazarlama onayı önceden işaretli | `src/features/newsletter/Newsletter.tsx:19` | Uyuşmazlık | `defaultChecked` kaldır; kutuyu bağlayıcı yapma |
| KV-05 | Reddet sonrası analytics isteği gitmiyor | `ConsentBanner.tsx:41-60` | Uyumlu | — |
| KV-06 | Şifre düz metin loglanıyor | `src/services/auth.service.ts:88` | Uyuşmazlık | Değeri maskele; anahtarı rotasyon et |
```

**Dosya:satır yazımı — §3 istisnası.** Gövde kuralları "dosya yolu ve satır numarası
yazma" yasağını koyar çünkü PRD gövdesi zamanla eskir. **§20.1 bir istisnadır:** denetim
raporu, inceleme anının **kanıt anlık görüntüsüdür** ve izlenebilir olmak zorundadır.
Bu yüzden burada satır numarası yazılır — ve raporun başına
`Denetim tarihi: <tarih> · Kapsam: <commit/branch>` notu düşülür.

### 8.2 Veri envanteri tablosu

```markdown
| Veri | Toplayan nokta | Nereye gidiyor | Hukuki sebep | Saklama | Aktarım |
|---|---|---|---|---|---|
| Ad, soyad, e-posta | İletişim formu | Tablo `contact_requests`, e-posta servisi (Resend, ABD) | Sözleşme (m.5/1) | Talep kapandıktan 6 ay sonra | Resend — ABD, sözleşme daylığı |
| TCKN | Sözleşme imza | Tablo `contracts` | Kanuni yükümlülük (m.5/2) | Sözleşme süresi + 10 yıl | — |
| E-posta | Bülten kaydı | Mailchimp, ABD | Açık rıza (m.5/1) | Abonelik bitene kadar | Mailchimp — ABD, açık rıza daylığı |
```

### 8.3 Koddan doğrulanamayanlar

Bu bölüm **boş bırakılmaz.** Koddan doğrulanamayan her madde buraya, tarayıcı/panel
adımıyla birlikte yazılır:

```markdown
| Madde | Neden koddan doğrulanamadı | Tarayıcıda nasıl kontrol edilir | Kim / Ne zaman |
|---|---|---|---|
| GTM'de pikselin gerçekten onay sonrası tetiklendiği | GTM konteyneri ve etiketleri repoda değil, GTM arayüzünde | GTM Önizleme → "Consent Initialization" tetikleyicisini kontrol et; Reddet → ağ panelinde istek doğmamalı | |
| Analytics'in gelişmiş mi temel mi kurulduğu | Config dosyada değil | GA4 Yönetici → Veri Akışı → Kimlik/Onay ayarları | |
| Saklama süresinin gerçekte uygulandığı | Yazılım kodda yok | Örnek kayıt al → 6 ay sonra silinmiş mi | |
```

### 8.4 Raporun sonu — zorunlu kapanış

Rapor, aşağıdaki paragrafın **birebir** kopyasıyla kapanır:

> Bu inceleme hukuki danışmanlık yerine geçmez; yasal metinler işletme tarafından, gerekirse bir hukukçuyla onaylanmalıdır.

---

## 9. Tarayıcı / panel doğrulama prosedürü

Bu adımlar kodun göstermediği şeyleri kanıtlar. Raporda neye karşılık geldikleri yazılır.

| Ne | Nasıl |
|---|---|
| **Hangi dış servis yükleniyor** | DevTools → **Network** → sayfayı yenile → istek listesini alan adına göre grupla. Reklam/izleme/oturum kaydı isteklerini ayır |
| **Onay öncesi yüklenen kod** | Tercihler panelini **Reddet** yap, sonra Network'i **temizle** ve yenile. Analytics/pixel/harita isteği geliyorsa banner işlevsizdir |
| **Çerez tablosu** | DevTools → **Application → Cookies** → alan adı; "karşılaştırmada zorunlu" işaretli olanlar dışındaki her şey gereksizdir |
| **Yerel depolama** | Application → **Local Storage / Session Storage / IndexedDB** — analytics ID veya form verisi tutuluyor mu |
| **Karar saklanıyor mu** | Reddet → sayfayı yenile → banner geri geliyorsa karar kalıcı değildir |
| **Harici font / embed IP sızıntısı** | Network → `fonts.googleapis.com`, `youtube.com`, `maps.googleapis.com`, `connect.facebook.net` istekleri; bunlar onay öncesi gidiyorsa KV-05 ihlalidir |
| **İletişim formunun nereye gittiği** | Formu gönder → Network → POST hedefi, payload alanları, dönen URL |
| **Loglara kişisel veri düşmesi** | Formu gönder → uygulama konsolu ve sunucu logu; ardından Sentry gibi hata izleme panosunda aynı olay |
| **Açık uç nokta** | Kurban kullanıcının oturumu açıkken Network panelinde istek URL'lerini al → **oturum kapalı**yken aynı istekleri tekrarla; 200 dönüyorsa yetkisiz erişim vardır |
| **Sayfa metinleri** | Aydınlatma metni, çerez politikası, kullanım şartları sayfaları yayınlandı mı, menüden erişilebiliyor mu, dil sürümü gerçekten var mı (çok dilli projede) |
| **Yurt dışı aktarımı** | Ağ isteklerindeki hedef ülke/IP; sağlayıcının veri işleme merkezi sözleşmesinden |
| **Tarayıcı konsol uyarıları** | Çerez uyarısı, CSP ihlali, karışık içerik (mixed content) mesajları |

---

## 10. Sık yapılan KVKK hataları

| Hata | Belirti | Doğru olan |
|---|---|---|
| **Şablon tuzağı** | Metinde var, sitede yok (ya da tam tersi) | Karşılaştırma **iki yönlü** yapılır; `Uyuşmazlık` yazılır |
| **Tek onay kutusu** | Aydınlatma ve rıza tek `✓`'da birleşik | Ayrı kutular; rıza geri alınabilir |
| **Rıza zorunluluğuna bağlanmış hizmet** | "Mesaj gönderebilmek için işaretleyin" | Cevap vermek rızaya bağlı değil; pazarlama ayrı |
| **Önceden işaretli kutu** | `defaultChecked` | Boş kutudan başlar |
| **Onaydan önce yüklenen kod** | Banner var ama `<script>` en başta | İzin kararı etiketten önce |
| **Reddedince de istek** | "Reddet" yalnız banner'i kapatıyor | Tercih kalıcı + istek engellenir |
| **Yalnız çerez listesi** | Tarayıcı çerez adları kopyalanmış | Her çerez için amaç, süre, sağlayıcı |
| **Yurt dışı gizlenmiş** | "Bulut barındırma" | Ülke + hukuki sebep yazılır |
| **Güvenlik: log** | `console.log(formData)`, `logger.info(user)` | Kişisel veri hiç yazılmaz; korelasyon id yeter |
| **Hız sınırı / bot koruması yok** | Form uç noktası açık | Rate limit + captcha/honeypot |
| **Hukuki görünürlük** | "KVKK uyumluyuz" ifadesi, hukuk incelemesi yapılmamış | Bu referansın kapanış paragrafı birebir yazılır |
| **Eksik sayfa "sonra"** | Politika sayfası yayın sonrasına kaldı | Tier A-2 yayın engelleyicidir |
