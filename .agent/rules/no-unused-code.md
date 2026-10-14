---
name: No Unused Code
description: Kullanılmayan import, local değişken, dosya ve gereksiz @SuppressWarnings bırakılmasını yasaklar; uyarı susturmanın, çalışan kodu bozmanın neden yasak olduğunu ve doğrulama kapılarını belirtir.
sinif: OLCULEBILIR
kapi:
  - yigin: "TypeScript / React"
    komut: "npx tsc --noEmit"
  - yigin: "Java / Spring derleme"
    komut: "mvn clean compile -DskipTests"
  - yigin: "Java / kullanılmayan kod"
    komut: "pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1"
---

# ⛔ KESİN KURAL: Kullanılmayan Kod Bırakma

Bu kural **her kod değişikliğinde istisnasız** geçerlidir: yeni kod,
refactoring, hata düzeltme ve test kodu dahil.

## 1. Kullanılmayan local değişken

IDE uyarısı: `The value of the local variable X is not used`

- Atanan ama okunmayan her local değişkeni kaldır.
- Değer yalnız yan etki için üretiliyorsa değişkene **atama yapma**, çağrıyı doğrudan yap:
  `var r = service.doWork();` → `service.doWork();`
  (⚠️ yan etkili ifadeyi silme, sadece atamayı kaldır.)
- `@SuppressWarnings("unused")` veya sahte kullanım (`log.debug(x)`, `x.toString()`)
  ile susturmak **yasaktır**.

## 2. Kullanılmayan import

IDE uyarısı: `The import X is never used`

- Dosyada referansı olmayan her `import` satırını kaldır.
- Kod silerken/taşırken o koda ait import'ları **aynı değişiklikte** temizle.
- Wildcard import (`import x.*;`) ile uyarıyı gizlemek **yasaktır.**

## 3. Kullanılmayan dosya / export

- Kaldırılan kodun yalnız kullandığı dosya, fonksiyon veya export varsa onu da kaldır.
- Kullanılmayan bir dosya "ilide yapabilir" gerekçesiyle bırakılmaz;
  gerekçe varsa `knowledge-base.md`'ye yazılır.

## 4. Susturma ve uyarı bırakma

Amaç: **çalışan kod bozulmadan**, ajan hiçbir uyarı ya da derleme hatası
kaynağı bırakmadan temiz kod yazsın. Uyarıyı susturmak çözüm değildir.

### 4.1 Gereksiz `@SuppressWarnings`

IDE uyarısı: `Unnecessary @SuppressWarnings("unchecked")`

- Java dosyalarında IDE/derleyici uyarısı (gereksiz `@SuppressWarnings`,
  kullanılmayan import/değişken, raw type vb.) **asla bırakılmaz.**
- Uyarının işaret ettiği anotasyon (`unchecked`, `rawtypes`, `unused` vb.)
  artık gerekmiyorsa **kaldır.** Düzeltilen kodda eski susturmayı
  "her ihtimale karşı" bırakma.
- Önce uyarının **kaynağını** gider (jenerik tip, doğru cast, `Class<T>`
  kullanımı). Susturma son çaredir ve yalnız gerçekten gerekli en dar kapsamda
  (metot/değişken, sınıf değil) ve nedenini belirten yorumla kullanılır.

### 4.2 ⛔ Çalışan kodu bozma

**Uyarıyı temizlemek için çalışma zamanı davranışını değiştirmek yasaktır.**

- `@SuppressWarnings("unchecked")` altındaki cast gerçekten güvenli mi, yoksa
  runtime'da `ClassCastException` riski mi taşıyor? **Şüphede kalıyorsan
  kaldırma** — uyarı kalmak, çalışma zamanında patlamaktan iyidir.
- Cast'i "doğru" yazmak da risklidir: `Class<T>` + `T` dönüşümü eklemek
  tip güvenliğini artırırken **davranışı değiştirebilir.** Değiştirdiysen
  ilgili **testi koştur.** Test yoksa dokunduğun yolda en az bir çalıştırılabilir
  doğrulama yap; yapamadıysan **"doğrulayamadım" de.**
- Bir uyarıyı susturmak için **config değiştirmek yasaktır** — `tsconfig`'te
  `noUnusedLocals: false`, derleyici bayrağında `-Xlint:-` kapatma, `eslint`
  kuralında `off`. Aynı ilke §2'deki wildcard import yasağıyla ortaktır:
  **kural gevşetilmez, kod düzeltilir.**
- Şüpheli bir uyarıyı **kendi inancınla temizleme.** Listele, kullanıcıya sor,
  kararı `knowledge-base.md`'ye yaz.

> Bu bölüm projeler arası ortaktır. Projeye özgü bir istisna gerekirse
> en alttaki `## Proje Bazlı Ek Kurallar` altına yazılır.

---

## 5. Doğrulama — "bitti" demeden önce

Derleyiciler bu uyarıların bir kısmını üretmez; "derlendi" demek yeterli değildir.

| Yığın | Komut | Beklenen |
|---|---|---|
| TypeScript | `npx tsc --noEmit` | 0 hata |
| TypeScript (build gerçeği) | projenin production build komutu | Exit 0 |
| TypeScript (kullanılmayan kod) | `tsconfig`'te `noUnusedLocals` ve `noUnusedParameters` **açık** olmalı | `tsconfig.json` kontrolü |
| Java | `mvn test-compile` | BUILD SUCCESS |
| Java (kullanılmayan kod/susturma) | `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` | `[OK]` |

`check-unused.ps1` çıktısı:

| Exit | Anlam | Ne yap |
|---|---|---|
| 0 | `[OK]` — bulgu yok | Devam |
| 1 | `[FAIL]` — `dosya:satır` listesi | Hepsini düzelt, tekrar koş |
| 2 | Derleyici hata raporladı — sonuç güvenilir değil | Logu incele, önce build'i düzelt |
| 3 | Arac/canary hatası — denetleyici çalışmadı | Sonuca güvenme, logu oku |

> `[uyarı]` satırları (`unchecked` / `raw type`) **hata değildir** ve kapıyı
> kırmaz. §4.2 gereği çalışan kodu bozarak temizlenmez; dokunduğun dosyada
> değerlendirirsin, dokunmadığın dosyalarda olduğu gibi bırakırsın.

## 6. Temizlik sınırı

- Değiştirdiğin dosyadaki bulguları **temizle** (sen yazmasan da).
- Değiştirmediğin dosyalardaki eski bulgular için izinsiz toplu temizlik yapma.
  Listele, kullanıcıya sor, kararı `knowledge-base.md`'ye yaz.

## 7. Sessizce geçme

Doğrulama komutunu çalıştıramadıysan **"çalıştıramadım" de.**
Sonucu uydurma; kanıtsız "temiz" demek bu kuralın ihlalidir.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir lint/dead-code istisnası gerekirse (ör. generated kod klasörleri), önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_