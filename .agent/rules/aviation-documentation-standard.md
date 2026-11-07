---
name: Aviation Documentation Standard
description: Kullanım kılavuzları, kurulum rehberleri, 'nasıl yapılır' dokümantasyonları ve ajan yanıtlarını FAA AC 121-24C Havacılık Yolcu Güvenlik Kartı standardına bağlar (sıfır laf kalabalığı, kronolojik eylem->çıktı, kritik uyarılar ve acil çıkış sorun giderme tablosu).
sinif: OLCULEBILIR
kapi:
  - yigin: "Dokümantasyon / Kılavuz ve Yanıt Standardı (FAA AC 121-24C)"
    komut: "python .agent/skills/musgoku/scripts/check_aviation_docs.py"
---

# ✈️ Dokümantasyon ve Talimat Standardı: "Aviation Passenger Safety Card" (FAA AC 121-24C Style)

> Bu kural; projelerde üretilen tüm kullanıcı kılavuzları (`docs/kullanici-rehberi.html`), test rehberleri
> (`docs/KULLANICI_TEST_REHBERI.md`), `README.md`, kurulum (`setup`) ve "nasıl yapılır" (`how-to`) dokümanlarının
> yanı sıra **AI kod ajanlarının kullanıcıya verdiği tüm yönlendirici yanıtlar ve talimatlar** için bağlayıcıdır.

---

## 1. Neden Havacılık Güvenlik Kartı Standardı? (Philosophy)

Bir uçak acil durumunda yolcuların kalın el kitaplarını veya uzun paragrafları okuyacak zamanı ve dikkati yoktur.
FAA AC 121-24C standardı; sıfır kafa karışıklığı (zero cognitive friction), maksimum görsel netlik ve anında
eyleme geçebilme amacıyla geliştirilmiştir.

Yazılım geliştiriciler ve kullanıcılar da karmaşık komutlar, ortam kurulumları, veritabanı migration'ları ve
mimari seçimler sırasında aynı bilişsel yük ve hata riskiyle karşılaşırlar. Bu nedenle tüm dokümantasyon ve
ajan yanıtları havacılık güvenlik kartı netliğinde olmalıdır.

---

## 2. Beş Temel Kural (Core Rules)

### 1. Sıfır Lakırdı (Zero Fluff — Minimum Text, Maximum Visuals)
- ⛔ Sohbet nezaketleri ("Tabii ki!", "Harika bir fikir!", "Bu rehberde size şunları anlatacağım..."), giriş dolgu paragrafları veya uzun teorik açıklamalar YASAKTIR.
- ✅ Açıklamalar doğrudan ASCII akış şemaları, Markdown tabloları veya girdiden çıktıya somut eşleşmelerle ifade edilir.
- ✅ Tüm eylemler emir kipiyle, tek cümlelik net komutlar halinde yazılır ("Şunu çalıştırın:", "Şu URL'e gidin:").

### 2. Kronolojik ve Sıralı Akış (Chronological & Sequential Flow)
- Her rehber ve işlem sırası kesin, numaralandırılmış bir zinciri (`1, 2, 3...`) takip eder.
- **Her adımın zorunlu sözdizimi:**
  ```markdown
  [Adım N]. [Eylem / Komut] -> [Beklenen Görsel Çıktı / Kanıt]
  ```
- Çıktı doğrulaması içermeyen ("bunu yapın sonra diğerine geçin" şeklindeki) adımlar kural ihlalidir.

### 3. "Brace Position" Kritik Uyarıları (Critical Warnings First)
- Yıkıcı, geri döndürülemez veya yüksek riskli işlemler (tablo silme `DROP`/`TRUNCATE`, veri tabanı migration'ı, gizli anahtar değişimi, `rm -rf`, `push --force`, port çakışması):
  ```markdown
  ⚠️ CRITICAL: [Tam sonuç ve önleyici adım / geri alma yolu]
  ```
- ⛔ **Zamanlama Kuralı:** Bu uyarılar tehlikeli komut çalıştırıldıktan sonra değil, **tam komutun öncesinde** verilmelidir.

### 4. "Ditching / Emergency Exit" Acil Çıkış ve Sorun Giderme Tablosu
- İstisnasız her prosedür, kurulum rehberi, test kılavuzu ve teknik talimat dokümanı en sonunda aşağıdaki 3 sütunlu acil durum kurtarma tablosuyla biter:

```markdown
## 🚨 Ditching & Emergency Exit (Sorun Giderme ve Hızlı Kurtarma)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `[Terminal/UI hatası veya belirti]` | `[Hatanın teknik kök nedeni]` | `[Kullanıcının tek tıkla uygulayacağı komut/adım]` |
```

### 5. Kopyala-Yapıştır Hazır (Copy-Paste Ready)
- Tüm kod blokları ve CLI komutları atomik, parametreleri eksiksiz ve üretim ortamına hazır olmalıdır.
- ⛔ Kod bloklarının içinde kopyalamayı bozan ve çalıştırıldığında hata veren `...`, `<TODO>`, `[buraya kod gelecek]` gibi çıplak yer tutucular bırakılamaz.

---

## 3. Ajan Sohbet Yanıtları Protokolü ve Negatif Sınır (Chat Response Contract & Anti-Panic Receipt Rule)

Kullanıcı ajana "bu proje nasıl kurulur?", "X hatasını nasıl çözerim?", "şu sayfayı nasıl test ederim?" veya
"hangi komutları çalıştırmalıyım?" gibi **kullanıcının bizzat uygulayacağı ileriye dönük yönerge/nasıl yapılır sorusu** sorduğunda ajan yanıtını şu şablonda üretir:

```markdown
### 📋 [İşlem / Görev Adı] (Aviation Quick-Card)

```ascii
[Girdi / İstek] ──> [İşlem Motoru] ──> [Beklenen Sonuç]
```

#### 🚀 Uygulama Adımları
1. **[Eylem 1]:** `[komut / UI adımı]` -> **Beklenen Çıktı:** `[görsel/konsol çıktısı]`
2. **[Eylem 2]:**
   ⚠️ CRITICAL: [Varsa tehlikeli komut öncesi uyarı]
   `[komut / dosya değişikliği]` -> **Beklenen Çıktı:** `[başarı kanıtı]`

#### 🚨 Ditching & Emergency Exit (Olası Hatalar)
| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `[Hata mesajı]` | `[Kök neden]` | `[Düzeltme komutu]` |
```

> ⛔ **Negatif Sınır — Tamamlanmış İşlem Makbuzlarında Acil Çıkış Tablosu Yasağı (Anti-Panic Receipt Rule):**
> - `🚨 Ditching & Emergency Exit` tablosu **yalnızca kullanıcının bizzat çalıştıracağı adımlar içeren** kılavuz, test rehberi ve "nasıl yapılır" yanıtlarında kullanılır.
> - Ajanın zaten bizzat çalıştırıp **`0` hatayla tamamladığı** otonom işlem makbuzlarında (ör. `/commitx` / `git push` tamamlandı raporu, bitmiş dosya okuma/analiz özeti veya basit durum bildirimi) **ASLA** `🚨 Ditching & Emergency Exit` tablosu basılmaz! İşlem başarıyla bitmişken *"Authentication failed / Non-fast-forward olursa şunu yapın"* tablosu basmak gereksiz kontrol, token israfı ve sahte telaş/hata algısı yaratır.

---

## 4. Denetim ve Ölçülebilirlik

Projedeki rehberler ve şablonlar `.agent/skills/musgoku/scripts/check_aviation_docs.py` kapısı ile otomatik olarak taranır:
- Acil durum tablosu eksikliği (`E1`)
- Eylem -> Çıktı formatı eksikliği (`E2`)
- Korumasız yıkıcı komut (`E3`)
- Kopyalamayı bozan kırık yer tutucu (`E4`)
tespit edildiğinde doğrulama kapısı hata verir (`exit 1`).
