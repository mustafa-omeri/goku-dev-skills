---
name: i18n-localization
description: Çok dili uygulamada çeviri anahtarı yönetimini ve denetimini kapsar; eksik anahtarın sessizce ana dilde kalmasını ve hardcode metni yakalar. Tetikleyiciler: "i18n", "çeviri ekle", "çok dil", "locale", "çeviri eksik", "çeviri görünmüyor", "dil değiştir", "İngilizceye geçince Türkçe kalıyor", "translate", "multi-language", "locale file", "missing translation", "hardcoded text". Tetiklenmez: tek dilli projede uygulanmaz; görsel/içerik çevirisi bu skill'in kapsamı dışındadır. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
risk: safe
source: community
date_added: "2026-02-27"
---

# i18n & Localization

> Zorunlu kural: [`rules/i18n-enforcement.md`](../../rules/i18n-enforcement.md)
> Bu skill **rehber ve denetleyicidir** — `scripts/i18n_checker.py` ile birlikte çalışır.

---

## 1. ⛔ En sık ve en sessiz ihlal

```tsx
t('stats.activity', 'Platform Aktivitesi')     // YANLIŞ
```

Bu desende `stats.activity` **hiçbir sözlükte tanımlı değilse**, i18next anahtarı
bulamaz ve `defaultValue`'ya düşer:

| Seçili dil | Ekranda görünen |
|---|---|
| `tr` | `Platform Aktivitesi` |
| `en` | **`Platform Aktivitesi`** ← Türkçe kalıyor |

Sözlükler birbirine **birebir eşit** olduğu için "anahtar senkronu" testleri
geçer. Eksik anahtar iki sözlükte de yoktur — bu yüzden o testler onu göremez.
Kod ajanının gözüne "çeviri yapılmış" gibi görünür, çünkü Türkçe metin
gerçekten ekranda görünmektedir.

**Kural:** `defaultValue` ikinci argümanı kullanılmaz. Metni önce sözlüğe
ekle, sonra `t('anahtar')` çağır. Anahtar eksikse hata **görünür olmalı**,
Türkçe metne düşmemeli.

Aynı tuzak `t(\`status.${x}\`)` gibi **dinamik** anahtarlarda da vardır; üretilen
anahtar kümesi sözlükte yoksa aynı sessiz düşüş olur.

---

## 2. Doğru kurulum

### 2.1 Sözlük yapısı

```
src/locales/
├── tr.json
├── en.json
└── i18n.ts
```

```jsonc
// en.json
{
  "common": {
    "save": "Save",
    "welcome": "Welcome {{name}}"
  }
}
```

- Anahtarlar **modül.alan** biçiminde nokta gösterimiyle düzenlenir.
- Değerler **düz metin**, `{{degisken}}` yer tutuculu. Metin birleştirme (`t() + '!'`)
  yasaktır — çevirmen cümlenin yapısını bozamaz.
- Aynı anahtar birden fazla yerde tanımlanmaz.

### 2.2 ⭐ Derleme zamanı anahtar güvenliği

`defaultValue` tuzağının kalıcı çözümü **tip güvenliğidir**: eksik anahtar
derleme hatasına dönüşür.

```ts
// src/i18next.d.ts  ->  DEGIL. Tip genisletmesi `.ts` dosyasinda olmali.
// src/i18n-types.ts
import { resources } from './i18n';

declare module 'i18next' {
  interface CustomTypeOptions {
    resources: typeof resources.en;
    strictKeyChecks: true;   // defaultValue olsa bile eksik anahtar HATA verir
  }
}
```

`strictKeyChecks` olmadan TypeScript `t('olmayan.anahtar', 'Yedek')` çağrısını
sessizce kabul eder. Bu satır olmadan bu skill'in 1. bölümündeki hata tekrar eder.

⛔ **`.d.ts` dosyasına koyma.** `skipLibCheck: true` olan projede `.d.ts`
içindeki `declare module` genişlemesi **yutulur**: `resources: 42` yazsan bile
tsc hata vermez ve kontrol hiç çalışmaz. Genişletme `.ts` dosyasında olmalıdır.

⛔ **Açılamıyorsa zorlama.** `strictKeyChecks` açıldığında `t()` dönüş tipi
`unknown`'a düşebilir ve derleme kırılır. Böyle bir projede kapı **çalışma
zamanında** (`i18n_checker.py`) kalır; `knowledge-base.md`'ye "strictKeyChecks
açılamadı + neden" yazılır. `enableSelector: 'strict'` de körlemesine
açılmaz — 558 hata verdiği ölçüldü, göç ayrı bir iştir.

### 2.3 Erişilebilirlik ve SEO metinleri

`aria-label`, `title`, `placeholder`, `alt` **görünür metindir** ve aynı kurala
tabidir. Bunlar `t()`'ye girdiyse ekranda görünmez ama ekran okuyucu kullanıcısı
için **görünür**dir.

---

## 3. Denetim

```bash
python .agent/skills/i18n-localization/scripts/i18n_checker.py
python .agent/skills/i18n-localization/scripts/i18n_checker.py --strict
python .agent/skills/i18n-localization/scripts/i18n_checker.py --json
```

| Seçenek | Etki |
|---|---|
| `--strict` | Uyarıları da hata sayar (CI için) |
| `--no-hardcode` | Kaynak taramasını atla (büyük projelerde hız) |
| `--locales <dizin>` | Sözlük klasörünü elle ver |
| `--json` | Makine okunur çıktı |

Ortam: `I18N_PROJECT_ROOT` proje kökünü elle verir.

### Kontroller

| Kod | Ne ölçer | Sonuç |
|---|---|---|
| **E1** | Sözlükler birebir aynı anahtar kümesinde mi | hata |
| **E2** | Boş çeviri var mı | hata |
| **E3** | Kodda çağrılan her `t()` anahtarı tanımlı mı | hata |
| **E4** | `t(key, 'sabit metin')` deseni kullanılmış mı | uyarı |
| **E5** | Kaynakta `t()` olmadan Türkçe UI metni var mı | uyarı |
| **E6** | Yabancı dil sözlüğünde Türkçe değer kalmış mı | uyarı |
| **E8** | Validasyon (Zod/Yup) katmanında Türkçe mesaj var mı — o katman React değildir | uyarı |
| **E7** | `{{degisken}}` yer tutucuları tüm dillerde eşit mi | hata |

Çıkış kodu: `0` temiz · `1` hata var · `2` araç hatası.

**E3 asıl kapıdır.** E1'e benzer görünse de farklıdır: E1 iki sözlüğü
karşılaştırır, E3 **kodu** sözlükle karşılaştırır. E1 geçerken E3 kızabilir —
ve o durum tam olarak 1. bölümdeki sessiz hatadır.

### Test

```bash
cd .agent/skills/i18n-localization/scripts/tests
python -m unittest discover -p "test_*.py"
```

Denetleyicinin kendi testleri hem geçersiz girdiyi reddetmeyi hem de **geçerli
projeyi kabul etmeyi** kanıtlar (`AcceptsValid` sınıfı). "Trending Categories"
Türkçe sayılmaz — false positive regresyonu testle korunur.

---

## 4. Yeni çeviri ekleme sırası

1. **Önce** anahtarı iki sözlüğe de ekle (`tr.json` **ve** `en.json`), aynı
   hiyerarşiyle. Sadece birini eklemek E1'i kırar.
2. Sonra bileşende `t('anahtar')` çağır.
3. **Eksik anahtar bırakma.** Denetleyici E3 hatası verirse iş bitmemiştir.
4. İki dilde de gerçek çeviri yaz — Türkçe metni İngilizce alana kopyalamak
   E6'yı tetikler.

## 5. Uygulama kalıpları

### React (react-i18next)

```tsx
import { useTranslation } from 'react-i18next';

function Welcome() {
  const { t } = useTranslation();
  return <h1>{t('home.title')}</h1>;
}
```

### Next.js (next-intl)

```tsx
import { useTranslations } from 'next-intl';

export default function Page() {
  const t = useTranslations('Home');
  return <h1>{t('title')}</h1>;
}
```

### Python (gettext)

```python
from gettext import gettext as _
print(_("Welcome to our app"))
```

## 6. Biçimlendirme

```tsx
new Intl.DateTimeFormat(locale).format(date)
new Intl.NumberFormat(locale).format(amount)
```

Çok sayılı cümlelerde sözlüğe ayrı anahtarlar yaz — `count` değişkeni tek başına
birden çok dilde çalışmaz (`1 events`):

```json
{ "itemOne": "{{count}} öğe", "itemMany": "{{count}} öğe" }
```

## 7. RTL

```css
.container {
  margin-inline-start: 1rem;   /* margin-left değil */
  padding-inline-end: 1rem;
}
[dir="rtl"] .icon { transform: scaleX(-1); }
```

## 8. Kontrol listesi

- [ ] Her görünür metin `t()` anahtarından mı geliyor
- [ ] `t()` çağrısında `defaultValue` ikinci argümanı **yok mu**
- [ ] Her anahtar **her iki** sözlükte de tanımlı mı
- [ ] `strictKeyChecks` etkin mi
- [ ] Yer tutucular iki dilde de aynı mı
- [ ] `aria-label` / `title` / `placeholder` de anahtardan mı geliyor
- [ ] `i18n_checker.py` çalıştırıldı mı, hata kaldı mı

## When to Use
This skill is applicable to execute the workflow or actions described above.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.