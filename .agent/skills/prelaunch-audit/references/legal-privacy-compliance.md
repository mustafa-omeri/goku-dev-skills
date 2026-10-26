# Hukuk, Gizlilik ve Çerez Uyumu Rehberi

Son veri doğrulaması: 26 Ekim 2026. Bu rehber hukuki danışmanlık niteliği taşımaz; üretilen tüm metinler taslaktır ve yayına çıkmadan önce işletmenin hukuk müşaviri veya avukatı tarafından onaylanmalıdır.

---

## 1. Veri Akışı ve Üçüncü Taraf Envanteri

Yasal metinler sitenin gerçek teknik davranışını yansıtmalıdır. Metin yazmadan önce projedeki üçüncü taraf betikleri ve veri toplama noktaları haritalandırılır:

1. **Kod Taraması:**
   Aşağıdaki anahtar terimler kod tabanında aranır:
   `googletagmanager`, `gtag`, `google-analytics`, `fbq`, `connect.facebook`, `hotjar`, `clarity.ms`, `intercom`, `crisp`, `tawk`, `hubspot`, `recaptcha`, `hcaptcha`, `turnstile`, `maps.google`, `stripe`, `iyzico`, `paytr`, `sentry`.
2. **Onay Öncesi Ağ Taraması:**
   `node .agent/skills/prelaunch-audit/scripts/consent-check.mjs https://staging.example.com` komutuyla onay verilmeden önce herhangi bir üçüncü taraf izleme isteği gidip gitmediği doğrulanır.
3. **Veri Toplama Formları:**
   İletişim, bülten, teklif ve kayıt formlarında toplanan alanlar ve hedef sunucular belirlenir.

---

## 2. KVKK m.10 ve Aydınlatma Metni Standartları

6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) m.10 uyarınca veri işleyen her sitede aydınlatma yükümlülüğü yerine getirilmelidir.

### Zorunlu Asgari İçerik:
- **Veri Sorumlusu:** Tam ticari unvan, tebligat adresi, MERSİS/VKN, KEP adresi veya kayıtlı e-posta, telefon. Bilinmeyen alanlar `[ŞİRKET ÜNVANI]`, `[MERSİS NO]` gibi yer tutucu olarak bırakılır.
- **İşleme Amaçları ve Hukuki Sebepleri:** KVKK m.5/6 kapsamındaki hukuki gerekçeler (sözleşmenin ifası, kanuni yükümlülük, meşru menfaat veya açık rıza).
- **Aktarılan Taraflar ve Yurt Dışı Aktarımı:**
  - 12 Mart 2024 tarihli 7499 sayılı Kanun değişikliği sonrasında (1 Eylül 2024'ten itibaren yürürlükte), yurt dışı aktarımlarında açık rıza tek başına genel dayanak olmaktan çıkmıştır.
  - Temel mekanizma KVKK Kurulu tarafından yayımlanan **Standart Sözleşme** modelidir. Sözleşme imzalanmasından itibaren **5 iş günü içinde** Kurum'a bildirilmelidir.
  - Bildirim yükümlülüğünün ihlali halinde öngörülen idari para cezası aralığı: **90.308 TL - 1.806.377 TL** (Yeniden değerleme oranına göre güncellenir). Bu bildirim doğrudan işletmenin/hukukçunun sorumluluğundadır (`NEEDS-HUMAN`).
- **İlgili Kişi Hakları (m.11):** Veriye erişim, düzeltme, silme taleplerinin iletilebileceği başvuru kanalları.

---

## 3. Çerez Politikası ve Consent Mode v2

KVKK Çerez Rehberi ve Avrupa GDPR/ePrivacy standartlarına göre:

1. **Zorunlu Çerezler Haricinde Varsayılan Ret:**
   Sepet, oturum güvenliği ve dil tercihi dışındaki analitik, pazarlama ve üçüncü taraf çerezleri onay verilmeden önce asla yüklenemez.
2. **Eşit Görünürlük:**
   Çerez bildiriminde "Tümünü Kabul Et" ve "Tümünü Reddet" butonları aynı boyutta, aynı renkte ve eşit hiyerarşide olmalıdır.
3. **Google Consent Mode v2:**
   Dört ana sinyal (`analytics_storage`, `ad_storage`, `ad_user_data`, `ad_personalization`) onay öncesi varsayılan olarak `denied` modunda başlatılmalı, kullanıcı onay verdiğinde `update` ile güncellenmelidir.
4. **Kalıcı Tercih Erişimi:**
   Her sayfanın footer alanında veya sabit bir ikon ile "Çerez Tercihleri" menüsüne yeniden erişim sağlanmalıdır.

---

## 4. Kullanım Şartları ve Tüketici Mevzuatı (6502 & 6563)

1. **Tüketici Hakları:**
   6502 sayılı Tüketicinin Korunması Hakkında Kanun uyarınca tüketici aleyhine tek taraflı haksız şartlar ve yetkili mahkeme kısıtlamaları geçersizdir.
2. **Ticari Elektronik İleti Onayı:**
   6563 sayılı Elektronik Ticaretin Düzenlenmesi Hakkında Kanun kapsamında pazarlama e-postası ve SMS gönderimi için önceden İYS (İleti Yönetim Sistemi) uyumlu açık onay alınmalıdır. Formlardaki ticari ileti onay kutucukları **önceden işaretlenmemiş (opt-in)** olmalıdır.
