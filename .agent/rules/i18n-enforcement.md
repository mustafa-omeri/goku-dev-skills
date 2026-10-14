---
name: MuSGoKu i18n Enforcement
description: Tüm kullanıcıya görünen metinlerin i18n anahtarı üzerinden gelmesini, t() defaultValue tuzağının yasaklanmasını, hardcode metnin ve iki dil dosyasının senkron tutulmasını zorunlu kılar; çalıştırılabilir denetleyici komutunu verir.
sinif: OLCULEBILIR
kapi:
  - yigin: "Frontend / i18n"
    komut: "python .agent/skills/i18n-localization/scripts/i18n_checker.py"
---

# 🌐 i18n Zorunlu Uygulama Kuralı

> Bu kural **frontend projesinde** geçerlidir ve tek dilli projeler için
> `Proje Bazlı Ek Kurallar` bölümüne istisna yazılabilir.

## Zorunlu kurallar

1. **Skill zorunluluğu:** Her ekran, sayfa, form, tablo, modal veya bileşen
   geliştirilirken `.agent/skills/i18n-localization/SKILL.md` okunur ve uygulanır.
2. **Hardcode metin kesinlikle yasak:** Kullanıcıya görünen tüm metinler
   `useTranslation()` üzerinden (`t('...')`) i18n anahtarından gelmelidir.
   JSX içine doğrudan Türkçe/İngilizce metin yazılmaz.
3. **Çift dil senkronu:** Eklenen veya düzenlenen her anahtar **aynı hiyerarşik
   yapıyla** hem `tr.json` hem `en.json` dosyasına eklenir. Eksik dil bırakılmaz.
4. **Duplicate anahtar yasak:** Aynı anahtar birden fazla tanımlanmaz.
5. **Dot-notation organizasyonu:** Anahtarlar anlamlı modül adlarıyla
   (`dashboard.platformPerformance.title`) düzenlenir.
6. **Şeffaf bildirim:** Yanıtta `i18n-localization` skill'inin devrede olduğu belirtilir.

## 2. ⛔ `t()` defaultValue tuzağı

```tsx
t('stats.activity', 'Platform Aktivitesi')   // ⛔ YASAK
```

`defaultValue` yalnızca anahtar **bulunamazsa** kullanılır. Anahtar hiçbir
sözlükte tanımlı değilse ekranda **her dilde Türkçe metin** görünür —
kullanıcı İngilizce seçse bile. Bu, "İngilizceye geçince Türkçe kelimeler
kalıyor" şikâyetinin en yaygın nedenidir.

- ⛔ `t()` çağrısında ikinci argüman kullanılmaz.
- Çeviri önce **iki sözlüğe de** eklenir, sonra `t('anahtar')` çağrılır.
- Anahtar eksikse ekranda Türkçe metin değil **hata** görünmelidir.

> **Neden testler yakalamaz:** Sözlük senkron testleri iki sözlüğü karşılaştırır.
> Eksik anahtar **iki sözlükte de yoktur**, dolayısıyla senkron testi geçer.
> Bu yüzden E1'e ek olarak **E3 (kod ↔ sözlük)** kontrolü gerekir.

## 3. ⭐ Derleme zamanı anahtar güvenliği

Hedef budur — TypeScript eksik anahtarı **derleme zamanında** hata olarak
söylemelidir:

```ts
declare module 'i18next' {
  interface CustomTypeOptions {
    resources: typeof resources.en;
    strictKeyChecks: true;
  }
}
```

⛔ **Ama `strictKeyChecks` "zorunlu" ilan edilip olduğu gibi bırakılamaz.**
2026-10-13'te kalansure'de denendi ve **açılamadı:** anahtar kontrolü çalışıyor,
ama `t()` dönüş tipi `unknown`'a düşüyor ve 28 satır
`Type 'unknown' is not assignable to type 'ReactI18NextChildren'` hatası veriyor.

Bu yüzden uygulama sırası şöyledir:

1. Önce **çalışma zamanı kapısını** yeşile getir: `E3` (eksik anahtar) = 0,
   `E4` (defaultValue) = 0.
2. `npx tsc --noEmit` yeşil olmadan `strictKeyChecks` denenmez.
3. Tip genişletmesi **`.d.ts` değil `.ts` dosyasında** olmalıdır.
   `skipLibCheck: true`, `.d.ts` içindeki `declare module` genişlemesini
   yutar — `resources: 42` yazsan bile tsc susar, kontrol hiç çalışmaz.
4. `enableSelector: 'strict'` **körlemesine açılmaz** — denendi, 558 hata
   verdi. Selector modu göç demektir, ayrı bir iş olarak planlanır.
5. Dönüş tipi bozulursa **zorlamama**: kapı çalışma zamanında
   (`i18n_checker.py`) kalır ve bu durum `knowledge-base.md`'ye
   "strictKeyChecks açılamadı + neden" diye yazılır.

> Kuralın öğrettiği: **bir kuralın "zorunlu" olması, ölçülebilir olduğu
> anlamına gelmez.** Bu dosyanın `sinif: OLCULEBILIR` olması, yalnızca
> §4'teki komutun ölçülebilir olduğu anlamına gelir.

## Doğru kullanım

```tsx
import { useTranslation } from 'react-i18next';

function UserList() {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('userManagement.title')}</h1>
      <Button>{t('common.add')}</Button>
      <p>{t('userManagement.noUsersFound')}</p>
    </div>
  );
}
```

## Yapı örneği

```json
{
  "common": {
    "save": "Kaydet",
    "cancel": "Vazgeç",
    "delete": "Sil",
    "edit": "Düzenle",
    "add": "Ekle",
    "search": "Ara",
    "loading": "Yükleniyor...",
    "noData": "Veri bulunamadı",
    "actions": "İşlemler",
    "back": "Geri",
    "saving": "Kaydediliyor..."
  },
  "auth": {
    "login": "Giriş Yap",
    "logout": "Çıkış Yap"
  }
}
```

## Kontrol listesi

- [ ] Yeni bileşende hardcode metin var mı?
- [ ] `useTranslation()` import edilip kullanıldı mı?
- [ ] `t()` çağrısında **defaultValue ikinci argümanı yok mu**?
- [ ] Anahtarlar her iki dil dosyasına aynı hiyerarşiyle eklendi mi?
- [ ] Duplicate anahtar var mı?
- [ ] `strictKeyChecks` etkin mi?
- [ ] Tip kontrolü çalıştırıldı mı (`npx tsc --noEmit`)?
- [ ] Denetleyici çalıştırıldı mı?

## 4. ⛔ Doğrulama kapısı — "bitti" demeden önce

```powershell
python .agent/skills/i18n-localization/scripts/i18n_checker.py
npx tsc --noEmit
```

| Exit | Anlam | Ne yap |
|---|---|---|
| 0 | Temiz | Devam |
| 1 | Hata var (E1/E2/E3/E7) | Hepsini düzelt, tekrar koş |
| 2 | Araç hatası — sözlük klasörü bulunamadı | `--locales` ile belirt |

`E3` (kodda çağrılıp sözlükte olmayan anahtar) **en kritik** kontroldür: sessiz
dil sızıntısının doğrudan kaynağıdır. `E5` (hardcode metin) uyarıdır, kapıyı
kırmaz; dokunduğun dosyada temizle, dokunmadığın dosyalarda izinsiz toplu
temizlik yapma.

## Kural ihlali

İhlal bulursan düzelt ve `knowledge-base.md`'ye yaz. Sessizce geçme.

⛔ Denetleyiciyi çalıştırmadıysan **"çalıştırmadım" de.** Uydurma çıktı,
kanıtsız "temiz" demekten kötüdür.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir i18n kuralı veya istisnası gerekirse (ör. tek dilli admin paneli), önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_