# KULLANICI_TEST_REHBERI.md — Çıktıları Nasıl Test Edersiniz

> Bu dosya her projede `docs/KULLANICI_TEST_REHBERI.md` altında tutulur ve `.agent/templates/KULLANICI_TEST_REHBERI.template.md`
> şablonundan oluşturulur.
> Kurallar: `.agent/rules/sprint-delivery-workflow.md` · `.agent/rules/development-workflow.md`
> Amacı: ajanın "yaptım / test edildi / tüm testler yeşil" demesini, kullanıcının
> **kendi gözüyle tarayıcıda veya konsolda doğrulayabileceği** somut adımlara çevirmektir.

---

## 1. Temel yöntem — 5 adım

| # | Adım | Soru |
|---|---|---|
| 1 | **Ne değişti?** | Dosya listesini okuyun. Beklediğiniz dosya listede mi? |
| 2 | **Kanıt komutu çalıştırın** | Ajan hangi komutu gösterdiyse **onu siz** çalıştırın. |
| 3 | **Sayıyı karşılaştırın** | "0 hata", "4/4", "[OK]" — sayı yoksa kanıt yoktur. |
| 4 | **Bir adımı bozun** | Kontrollü olarak bir şeyi kırın; kapı gerçekten kırmızıya dönüyor mu? |
| 5 | **Geri alınabilir mi?** | Geri alma yolu var mı (yedek, geri commit, geri alma komutu)? |

⛔ **4. adım atlanırsa kapının çalıştığını bilemezsiniz.** Hep yeşil gören bir
denetleyici, hiç çalışmayan bir denetleyiciden ayırt edilemez.

---

## 2. Sözlük: kanıt hangi kelimeye karşılık gelir

| Ajanın dediği | Kanıt mı? | Doğrulaması |
|---|---|---|
| "uyguladım" | ⛔ hayır | sayı yok |
| "test edildi" | ⛔ hayır | hangi komut? |
| "çalışıyor" | ⛔ hayır | neyi gördün? |
| "tüm testler yeşil" | ⚠️ kısmi | otomasyon geçti, kullanıcı gözüyle ne değişti? |
| "0 hata · 34 test" | ✅ evet | tekrar koşun |
| "doğrulanamadı" | ✅ evet | dürüst beyan — en iyisi |

---

## 3. Bu Projenin Çıktıları için Test ve Doğrulama Adımları

_(Bu bölüm projeye özeldir. Her yeni özellikte/sprintte ajan bu bölümü günceller.)_

### 3.1 Otomatik Doğrulama Kapıları (Terminal Testi)

```bash
# Projenin tip, derleme ve test komutları
[komut 1 — ör: npm run typecheck / mvn test-compile]
[komut 2 — ör: npm test / mvn test]
```

### 3.2 Canlı Önizleme / Tarayıcı Testi (Varsa)

```bash
# Uygulama sunucusu / dev / preview komutları
[sunucu başlatma komutu]
# Açılacak yerel URL: http://localhost:PORT
```

### 3.3 Özellik Bazlı Kullanıcı Kabul Senaryoları (Manuel Test)

> ⛔ **Veri Üreten/Toplayan Özelliklerde Zorunlu 3 Katman:**
> Form, bildirim veya geri bildirim gibi veri toplayan her teslimatta test adımları yalnızca ekrandaki mesaja bakarak bitti sayılamaz. Aşağıdaki 3 katmanlı format zorunludur:

* **Özellik / Senaryo 1 (Standart UI / 3 Cihaz Ergonomisi ve Modal Doğrulaması):**
  - **Masaüstü Testi (> 1024px):**
    1. Tarayıcıda `URL` adresine gidin.
    2. Sol menünün, geniş bilgi ızgarasının ve çok sütunlu yerleşimin ferah oturduğunu görün.
    3. Modal/Popup açan butona tıklayın: Merkezli, `max-w-lg` şık bir Dialog açıldığını ve sayfa temasını (renk, radius, backdrop) koruduğunu doğrulayın.
  - **Tablet Testi (768px – 1024px / F12 Responsive iPad):**
    1. `F12` açıp genişliği `768px` ile `1024px` arasına getirin.
    2. Düzenin mobildeki gibi tek sütuna büzüşmediğini; dengeli 2 sütunlu grid veya Split-View (sol liste, sağ detay) olarak açıldığını gözlemleyin.
    3. Kenar çubuğunun daraltılmış/katlanabilir olduğunu ve dokunma alanlarının ferah olduğunu doğrulayın.
  - **Mobil Testi (375px / F12 Responsive iPhone/Android):**
    1. Genişliği `375px` yapın.
    2. Tek sütun akışını, kritik butonların ekranın alt kısmında (Thumb Zone) yer aldığını ve yatay kayma (horizontal overflow) olmadığını görün.
    3. Modal/Popup açan butona tıklayın: **ÖNEMLİ:** Modalın ortada sıkışmak yerine ekranın altından yükselen bir **Bottom Sheet (Drawer)** olarak açıldığını, parmakla aşağı kaydırılıp kapatılabildiğini ve form alanlarına odaklanıldığında klavye altında kalmadığını doğrulayın.
  - **4 UX Durumu Kontrolü:**
    1. *Loading:* Sayfa yüklenirken veya butona basıldığında skeleton/spinner ve buton disable durumunu görün.
    2. *Empty:* Veri yokken veya filtre boşken yönlendirici ikon + CTA butonunu görün.
    3. *Error:* Yanlış veride anlaşılır inline hata ve "Yeniden Dene" butonunu görün.
    4. *Feedback:* İşlem bitince Toast onay bildirimini görün.

* **Özellik / Senaryo 2 (Veri Toplayan / Form Özelliği — 3 Katmanlı Doğrulama):**
  - **Katman 1 (Görsel UX):**
    1. `URL` sayfasına gidin ve form alanlarını doldurun.
    2. Gönder butonuna tıklayın.
    3. Ekranda beklenen başarı bildirimini (`[Başarı Mesajı]`) ve formun sıfırlandığını görün.
  - **Katman 2 (Ağ / Network Doğrulaması):**
    1. Tarayıcıda `F12` Geliştirici Araçlarını açıp **Network (Ağ)** sekmesine gelin.
    2. Formu gönderdiğinizde çıkan API isteğini (`POST /api/...` veya Supabase REST) bulun.
    3. Yanıt durum kodunun `201 Created` veya `200 OK` olduğunu ve giden payload'u doğrulayın.
  - **Katman 3 (Veritabanı Kalıcılık Doğrulaması):**
    1. Veritabanı sorgusu veya yönetim panelinde yeni kaydı sorgulayın:
       ```sql
       SELECT id, created_at, [ilgili_kolonlar] FROM [tablo_adi] ORDER BY created_at DESC LIMIT 1;
       ```
    2. Gönderdiğiniz verinin DB'ye kaydedildiğini ve yetkisiz kişilerin erişemeyeceğini (RLS) doğrulayın.

---

## 4. Sprint kuralıyla üretilen çıktıları nasıl test edersiniz

Her `Yapıldı` kartı bir `test:` alanı taşır. `KANBAN.md`'de o satırı okuyun ve
**o adımı birebir uygulayın.**

| Kart durumu | Sizin testiniz |
|---|---|
| `Bekliyor` | henüz test yoktur — kart kapanmadan da test edilmez |
| `Yapılıyor` | ara çıktıyı inceleyin, Gherkin dosyası gerçekten var mı? |
| `Sınırdı` | komutu çalıştırın, gerçekten geçiyor mu? |
| `Yapıldı` | `test:` alanındaki adımı uygulayın, ölçülebilir sonucu görün |

**Bir kartın `test:` alanı şunlarsa test edilmemiş sayılır:**

- "test edildi" · "çalışıyor" · "doğrulandı"
- "yazılacak" · "TBD" · "?"
- Ölçülebilir sonuç içermeyen her cümle

---

## 5. Test edilemeyen çıktı — dürüst beyan

Bazı işler kullanıcı tarafından doğrudan test edilemez (ör. bir refactoring, arka plan temizliği).
Bu durumda ajan **"bu çıktı doğrudan kullanıcı tarafından gözlemlenemez,
şu teknik ölçümle destekliyorum"** demelidir. Uydurma test adımı yazmaz.

---

## 6. Tek cümlelik onay şablonu

Bir çıktıyı onaylarken şunu yazabilirsiniz:

> "Test ettim: `<komut/ekran>` → `<sonuç>`, `<bozma testi>` → `<beklenen kırmızı>`."
