# knowledge-base.md Şablonu

> Bu dosya **yalnız repo kökünde** tutulur. Kurallar:
> `.agent/rules/knowledge-base-management.md`
>
> ⛔ Ajan bu dosyayı baştan sona **okumaz** (append yazar). Arama yapacaksa
> başlık satırlarına göz atar.

---

## Kullanım

Her kalıcı hata çözümü ve her kalıcı karar için aşağıdaki iki şablondan
biri eklenir. Yeni kayıt **en üste** eklenir.

### Hata kaydı

```markdown
## <kısa başlık> (YYYY-MM-DD)

### Problem
<Neyi gördün: hata mesajı, ekran davranışı, build çıktısı>

### Root Cause
<Tek cümlede gerçek neden>

### Solution
<Kalıcı düzeltme. Geçici bandajı ayrı satırda belirt.>

### Files Changed
- path/one
```

### Karar kaydı

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

---

## Sınırlar

| Yaz | Yazma |
|---|---|
| Kural doğuracak karar | O an için çözülen geçici düzeltme |
| Alternatifleri **değerlendirilmiş** seçim | "Zorunda kaldım" — bu bir Root Cause'dur |
| Sonraki oturumu etkileyen gerekçe | Dosya/fonksiyon adı gibi uygulama detayı |
| İkinci kez ortaya çıkan hata | Günlük kayıt (`✅ eklendi`, `debug log koydum`) |

**"Değerlendirilen Alternatifler" boş bırakılamaz:**

- Düşündüysen → alternatif + somut gerekçe
- Düşünmediysen → `⚠️ Ajan bu alternatifi değerlendirmedi — <sebep>`
- Kaynakta tartışma yoksa → `Kaynakta tartışma yok, ajan uydurmadı`

---

## Kayıt örneği

_(Aşağıdaki örnek silinebilir.)_

## Vite derlemesi TS6133 ile kırıldı (2026-01-15)

### Problem
Production build `tsc -b && vite build` Exit Code 2 ile sonlandı.
Hata `TS6133: 'X' is declared but its value is never read` idi.

### Root Cause
Refactoring sırasında kullanılmayan değişken import'u kaldırılmamıştı.
`tsc --noEmit` çalıştırılmadığı için hata teslimden önce görülmedi.

### Solution
Kullanılmayan değişken ve import kaldırıldı. Bundan sonra "bitti" demeden
önce `npx tsc --noEmit` zorunlu kapı olarak eklendi.

### Files Changed
- src/features/<feature>/components/<Component>.tsx

---

## Bu dosyada olmaması gerekenler

- Oturum durumu, "sıradaki iş" → `HANDOFF.md`
- Vault kararları, proje mimarisi → `<vault>\projects\<slug>\`
- Şifre, belirteç, kişisel veri