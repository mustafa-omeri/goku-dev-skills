---
name: Knowledge Base and Handoff Management
description: knowledge-base.md ve HANDOFF.md dosyalarının tek konumunu, içerik formatlarını, nelerin yazılıp nelerin yazılmayacağını ve kullanıcıya raporlama zorunluluğunu tanımlar.
sinif: TUTUM
---

# 📚 Bilgi Tabanı ve Oturum Devri Yönetimi

## 0. İki dosya, iki iş — asla karıştırma

| Dosya | Tek konumu | Ne tutar | Ne tutmaz |
|---|---|---|---|
| `knowledge-base.md` | `<repo-kök>\knowledge-base.md` | Kalıcı hata çözümleri ve kalıcı kararlar | Oturum durumu, "sırada ne var" |
| `HANDOFF.md` | `<repo-kök>\HANDOFF.md` | Nerede kaldık, sıradaki iş, bu projede düşülen tuzaklar | Kararların gerekçesi |

Bu ayrım bozulursa aynı bilgi iki yerde yaşar ve biri bayatlar.
Karar gerekçesi `knowledge-base.md`'dedir; `HANDOFF.md` yalnız **yol gösterir.**

⛔ Bu iki dosya **repo kökü dışında hiçbir yere yazılmaz.**

---

## 1. `knowledge-base.md`

### Yazma kuralı

- ⛔ Baştan sona **OKUMA.** Dosya büyüyebilir; token israfıdır. Aynı konuyu tekrar
  arıyorsan `grep`/`search` ile başlık satırlarına bak.
- ✅ Her kalıcı hata çözümü ve her kalıcı karar **append** edilir.
- ⛔ Aynı hatayı/kararı ikinci kez bulursan **tekrar yazma**; terfi öner.
- ⛔ Vault'a hiçbir şey yazma.

### Hata kaydı formatı

```markdown
## <kısa başlık> (YYYY-MM-DD)

### Problem
<Neyi gördün: hata mesajı, ekran davranışı, build çıktısı>

### Root Cause
<Tek cümlede gerçek neden. "Zorunda kaldım" yazma — bu Root Cause değildir.>

### Solution
<Adım adım düzeltme. Kalıcı düzeltme ile geçici bandajı ayır.>

### Files Changed
- path/one
- path/two
```

### Karar kaydı formatı

```markdown
## <karar adı> (YYYY-MM-DD)

### Karar
<Ne yapıldı, tek cümle>

### Karar Gerekçesi
<Sonraki oturumu etkileyen neden>

### Değerlendirilen Alternatifler
- <alternatif> — <somut neden seçilmedi>

### Files Changed
- path/one
```

### Neler yazılmaz

| Yaz | Yazma |
|---|---|
| Kural doğuracak karar (enum, katman sınırı, kütüphane, convention) | O an için çözülen geçici düzeltme |
| Alternatifleri **değerlendirilmiş** seçim | "Zorunda kaldım" — bu bir Root Cause'dur |
| Gerekçesi sonraki oturumu etkileyecek karar | Dosya/fonksiyon adı gibi uygulama detayı |
| Aynı konuda ikinci kez ortaya çıkan hata | Günlük kayıt (`✅ X eklendi`, `🔍 debug log koydum`) |

Günlük kayıt terfi kanıtını yapay olarak şişirir ve dosyayı gürültüye çevirir.

### "Değerlendirilen Alternatifler" boş bırakılamaz

- Gerçekten düşündüysen → alternatif + **somut** gerekçe
- Düşünmediysen → `⚠️ Ajan bu alternatifi değerlendirmedi — <sebep>`
- Kaynakta tartışma yoksa → `Kaynakta tartışma yok, ajan uydurmadı`

---

## 2. `HANDOFF.md`

### Güncelleme zamanı

- Her görev/sürüm/slice bitiminde
- Oturum kapanırken
- Commit onayı **istenmeden hemen önce**

### Zorunlu bölümler

| Bölüm | İçerik |
|---|---|
| Başlık bloğu | Tarih, ajan adı, ilgili PRD/KB dosyası |
| §0 Önce bunu oku | Bu projede **gerçekten yaşanmış** tuzaklar, kural + somut neden + doğru yol |
| §1 Bu oturumda yapılanlar | Backend / frontend / dokümantasyon / test ayrık satırları |
| §2 Sağlık durumu | Kırılgan dosyalar, sahte geçen test riski, dikkat gerektiren noktalar |
| §3 Buradan devam et | Hemen koşturulacak doğrulama komutları + **numaralı** sıradaki işler |
| §4 Bu projede düşülen hatalar | Yeni ders/tuzak (yoksa "yeni yok") |
| §5 Bu projede alınan kararlar | Yeni karar başlığı + `knowledge-base.md` referansı (yoksa "yeni yok") |
| §6 Ortam bilgisi | Port, DB, test hesapları, komutlar — **yalnız gerçekten doğrulanmış** değerler |

### §3 Sıradaki iş — kuralları

- Her iş **numaralı** olur; önceki işin durumu açıkça yazılır.
- Her iş tek cümleyle yazılır ve **hemen başlanabilir** olmalıdır.
- **Eğer açık iş kalmadıysa bunu açıkça yaz:** `Açık iş yok — proje tamamlandı.`
  Boş bırakma, "belki bir şey vardır" deme.
- Sıra numarası olmayan "sıradaki iş" yazımı geçersiz sayılır.

### §0 tuzakları — yazım kuralı

- Yalnız **oturum sırasında bizzat karşılaşılan ve gözlenen** somut hatalar yazılır.
- Tahminle, "muhtemelen şöyle olur" diye tuzak **uydurulmaz.**
- Biçim: `| # | Kural | Somut neden / ne yaşandı | Doğru yol |`
- Bu bölüm `DEV_BRIEF.md` veya vault'un kopyası değildir; **yalnız bu proje.**

### Kalıcılık

Tarih, ajan adı ve ortam değerleri güncellenir. Silinen bir §0 maddesi ancak
o tuzak artık geçerli değilse ve gerekçesi yazılmışsa kaldırılır.

---

## 3. Şeffaf raporlama zorunluluğu

Bu güncellemeler arka planda gizli yapılamaz. Commit onayı istemeden **hemen önce**
yanıtta ayrı bir blok halinde göster:

```markdown
### 📝 OTURUM DEVİR & BİLGİ TABANI GÜNCELLEMESİ (HANDOFF & KB RAPORU)
- **knowledge-base.md:** [Eklenen karar veya hata başlıkları ve kısa özeti (yoksa "yeni yok")]
- **HANDOFF.md:**
  * Güncellik Kanıtı: [Ölçülen gerçek sayılar — test, assert, derleme, chunk boyutları]
  * Nerede Kaldık: [Tamamlanan adım ve durum]
  * Sıradaki İş: [Yeni oturumun başlayacağı ilk somut hedef]
  * Bu Projede Düşülen Hatalar: [Yeni ders/tuzak veya "yeni yok"]
  * Bu Projede Alınan Kararlar: [Yeni karar veya "yeni yok"]
- **Sonraki işler:** [Numaralı liste — açık iş kalmadıysa "Açık iş yok — proje tamamlandı"]
- **Kullanılan MCP:** [context7 / sequential-thinking — ne için kullanıldı veya "kullanılmadı"]
- **Aktif skill'ler:** [Okunan skill adları]
```

⛔ Bu blok gösterilmeden commit onayı istemek veya görevi "tamamlandı" ilan etmek
yasaktır.

### 3.1 Rapor Çıktı Tetikleme Politikası (Enable/Disable Mekanizması)

Rapor bloğunun ne zaman üretileceği token maliyeti ve bağlam optimizasyonu için
ayarlanabilir bir politika ile yönetilir. Ayrıntılı kılavuz: `readme-help.md`.

| # | Tetikleyici Durum | Varsayılan | Davranış |
|---|---|:---:|---|
| 1 | `REPORT_ON_CODE_CHANGES` (Ara kod yazımı/refactor) | ❌ `disabled` | Ara adımlarda rapor basılmaz (token tasarrufu) |
| 2 | `REPORT_ON_INTERMEDIATE_TESTS` (Ara test/build) | ❌ `disabled` | Yalnızca komutun gerçek çıktısı raporlanır |
| 3 | `REPORT_ON_CONVERSATION` (Soru-cevap/diyalog) | ❌ `disabled` | Yalnızca teknik diyalog yürütülür |
| 4 | `REPORT_ON_TASK_COMPLETION` (Görev bitimi & commit öncesi) | ✅ `enabled` | Tek seferlik şeffaf devir kanıtı basılır |
| 5 | `REPORT_ON_SESSION_CLOSE` (Oturum kapanışı/devri) | ✅ `enabled` | Oturum köprüsü için basılır |

> **Yapılandırma:** Kullanıcı bu ayarları `AGENTS.md` → `## Proje Bazlı Ek Kurallar`
> altında değiştirebilir. Belirtilmemişse varsayılan `[disabled, disabled, disabled, enabled, enabled]` geçerlidir.

---

## 4. Vault sınırı

Harici geliştirici hafızası (`<vault>`) salt okunurdur, **asla doğrudan yazılmaz.**

- `raw\` · `projects\` · `global\` · `sources\` · `entities\` ·
  `concepts\` · `profile\` · `log.md` — hepsi Kütüphaneci'nin katmanıdır.
- Karar dosyası yazma · oturum raporu bırakma · hiçbir wiki dosyasını düzenleme.
- Kütüphaneci senin proje kökündeki `knowledge-base.md` kayıtlarını okur ve kalıcı
  kararları ilgili arşiv katmanına **o** taşır.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir istisna veya ek bilgi tabanı kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır. Aynı konuyu karşılayan kural varsa eklenmez.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_