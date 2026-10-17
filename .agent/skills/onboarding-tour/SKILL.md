---
name: onboarding-tour
description: >
  Web ve mobil uygulamalarda kullanıcı karşılama, rehberli ürün turu, adım adım walkthrough ve ipucu balonları tasarlar; Driver.js ve React Joyride ile kalıcı durum yönetimi sağlar. Tetikleyiciler: "tur hazırla", "tour hazırla", "desing tour", "ürün turu", "onboarding turu", "ipucu balonu", "product tour", "guided tour", "coachmarks". Tetiklenmez: form arayüzü `frontend-design`'a, slayt sunumu `slides`'a aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
argument-hint: "[engine: driverjs|joyride|coachmark] [tour-name]"
license: MIT
metadata:
  author: antikit
  version: "1.0.0"
---

# Onboarding Tour — Rehberli Ürün ve Kullanıcı Tanıtım Turu

Yazılım ve dijital ürün tasarımlarında (web siteleri, SaaS platformları, mobil web uygulamaları) kullanıcının bir uygulamayı ilk kez açtığında bölümleri adım adım, ipuçlarıyla ve odaklanmış şekilde keşfetmesini sağlayan **Onboarding (Kullanıcı Alıştırma / Kullanıcı Karşılama)** sistemidir.

---

## 🎯 Ne Zaman Devreye Girer? (Tetikleyiciler)

- Kullanıcı yeni bir ekran, dashboard veya özellik eklediğinde bir "ürün turu" veya "tanıtım kılavuzu" istediğinde.
- "tur hazırla", "tour hazırla", "desing tour", "ürün turu", "onboarding turu", "adım adım rehber", "ipucu balonu".
- İngilizce: "create a tour", "design tour", "onboarding tour", "product tour", "guided walkthrough", "coachmarks".

## ⛔ Kapsam Sınırı (Tetiklenmez)

- Form, tablo, buton ve arayüzün kendi görsel yerleşimi `frontend-design` ve `ui-styling` skill'lerine aittir.
- Sunum slaytları ve pitch deck düzenleri `slides` ve `design-system` skill'lerine aittir.
- Kullanıcı yetkilendirme, login ve oturum akışları `musgoku`'ya aittir.
- Tam sözlük: `.agent/rules/skill-trigger-routing.md`

---

## 🧭 3 Temel Onboarding Tasarım Elemanı

1. **Ürün Turu / Rehberli Tur (Product Tour / Guided Tour):**
   - İlgili hedef elemanı (`data-tour="..."`) öne çıkararak diğer kısımları yarı saydam arka planla (`overlay / backdrop`) karartan ve yanında açıklayıcı popover gösteren sıralı turlardır.
2. **İzlenecek Yol / İnteraktif Kılavuz (Walkthrough):**
   - Kullanıcının sadece "Sonraki" butonuna basması yerine, ilgili alana tıklamasını veya bir işlem yapmasını bekleyen etkileşimli turlardır.
3. **İpucu / Antrenör İşaretleri (Coachmarks / Pulsing Beacons):**
   - Karartma yapmaksızın, arayüzdeki kritik veya yeni özelliklerin yanında yanıp sönen küçük halkalardır (pulsing beacons). Kullanıcı dokunduğunda mini ipucu kartı açılır.

---

## ⚖️ Kütüphane Seçim Stratejisi & Bundle Bütçesi

| Kütüphane | Paket Boyutu (gzip) | Lisans | En İyi Kullanım Alanı | Karar |
|---|---|---|---|---|
| **Driver.js** | **~5 KB (Ultra Hafif)** | **MIT (Özgür)** | **Modern SPA, SaaS, Vite/Next.js panelleri** | 🏆 **ÖNERİLEN & VARSAYILAN** |
| **React Joyride** | ~35 KB (Orta/Ağır) | MIT (Özgür) | Adım içinde zengin React JSX formu/bileşeni gereken yerler | ⚠️ Alternatif (Lazy import şart) |
| **Intro.js React** | ~15 KB | ⚠️ **AGPL-3.0 / Ticari Lisans** | Açık kaynak olmayan ticari projelerde ücretlidir | ⛔ **Tavsiye Edilmez (Lisans Riski)** |

> [!IMPORTANT]
> **Neden Driver.js?**
> 1. **Bundle Dostu:** Sadece ~5 KB gzip ek yük getirir (`frontend-bundle-limits.md` sınırlarını zorlamaz).
> 2. **Sıfır Bağımlılık (Zero Dependencies):** Harici büyük kütüphanelere dayanmaz; SVG/Canvas spotlight motoru son derece akıcıdır.
> 3. **React Hooks Uyumu:** `useOnboardingTour` özel hook'u ile declaratif ve temiz bir şekilde yönetilir.
> 4. **Lisans Güvenliği:** MIT lisanslıdır; ticari veya kişisel tüm projelerde telif riski taşımadan serbestçe kullanılır.

---

## 📐 Zorunlu UX ve Mimari Standartları

1. **Kalıcılık (Persistence & Never Harass):**
   - Bir kullanıcı turu tamamladığında veya kapattığında, bu durum `localStorage` (ör. `onboarding_completed_<tur_adi>`) veya veritabanı profilinde kalıcı olarak saklanmalıdır. Kullanıcı her sayfa yenilediğinde tur zorla tekrar açılmamalıdır.
   - İstenildiğinde "Turu Tekrar Başlat" butonu (ör. Yardım menüsünde) sunulmalıdır.
2. **Kaçış Hattı (Escape Hatch):**
   - Her adımda açık ve net bir **"Turu Atla / Kapat (Skip)"** butonu bulunmalı ve klavyeden `Escape` tuşuna basıldığında tur güvenle sonlanmalıdır.
3. **Kırılmayan Hedef Seçiciler (Semantic Selectors):**
   - Kırılgan CSS sınıfları (`.btn-primary`, `div > div:nth-child(3)`) yerine her zaman semantik veri niteliği kullanılmalıdır:
     `data-tour="search-input"`, `data-tour="create-countdown-btn"`.
4. **Mobil ve Küçük Ekran Uyumu (Responsive Ergonomics):**
   - Dar ekranlarda (375px/414px) popover pencerelerinin ekran dışına taşmasını engellemek için `placement: 'auto'` veya `'bottom'` tercih edilmeli, popover genişliği `max-w-[calc(100vw-32px)]` ile sınırlandırılmalıdır.
5. **Lazy Loading (Kod Bölme):**
   - Tur motorları yalnızca ilk açılışta veya kullanıcı yardım istediğinde çalışacağı için `React.lazy()` ile dinamik import edilmeli, ana giriş paketini (`index-*.js`) şişirmemelidir.

## 📦 Ajanın İcra ve Kurulum Protokolü (Autonomous Installation Protocol)

Kullanıcı bir tur talep ettiğinde ajan şu adımları **otonom olarak** işletir:

1. **Paket Kontrolü & Kurulum:**
   - Projenin `package.json` dosyasını inceler.
   - Seçilen motor (`driver.js` veya `react-joyride`) bağımlılıklarda yoksa, projenin paket yöneticisine göre terminalden kurar:
     * pnpm: `pnpm add driver.js`
     * npm: `npm install driver.js`
     * yarn: `yarn add driver.js`
   - *Not:* Eğer kullanıcı harici paket kurulmasını istemiyorsa veya sıfır bağımlılık tercih ediliyorsa, ajan doğrudan **Tarif 2 (Pulsing Coachmark Beacon)** desenini uygular (0 harici paket).
2. **Hook / Bileşen Üretimi:**
   - Yerleşik `scaffold_tour.py` aracını çalıştırarak veya doğrudan hook dosyasını `src/features/onboarding/use<Ad>Tour.ts` altına yazar.
3. **Hedef Seçiciler (Target Selectors):**
   - İlgili ekran bileşenlerine semantik `data-tour="<tur>-<adim>"` etiketlerini yerleştirir.
4. **Doğrulama & Kapı Kontrolü:**
   - `python .agent/skills/musgoku/scripts/check_bundle_limits.py` ve projenin testlerini çalıştırarak bundle bütçesinin korunduğunu kanıtlar.

---

## 🛠️ CLI Şablon Üreteci

Tur şablonu ve TypeScript hook'u oluşturmak için yerleşik script:

```bash
# 1. Varsayılan Driver.js hook'u üretme (önerilen):
python .agent/skills/onboarding-tour/scripts/scaffold_tour.py --engine driverjs --name dashboard --output src/features/onboarding/useDashboardTour.ts

# 2. React Joyride bileşeni üretme:
python .agent/skills/onboarding-tour/scripts/scaffold_tour.py --engine joyride --name product-tour --output src/components/onboarding/ProductTour.tsx

# 3. Bağımsız Coachmark (Pulsing Beacon) ipucu balonu üretme:
python .agent/skills/onboarding-tour/scripts/scaffold_tour.py --engine coachmark --output src/components/ui/CoachmarkBeacon.tsx
```

---

## 💻 Hazır Entegrasyon Tarifleri (Recipes)

### Tarif 1: Driver.js React Hook Kullanımı (`useDashboardTour.ts`)

```tsx
import { useDashboardTour } from '@/features/onboarding/useDashboardTour'

export function DashboardHeader() {
  const { startTour } = useDashboardTour({ autoStart: true })

  return (
    <header className="flex justify-between items-center p-4">
      <h1 data-tour="dashboard-welcome" className="text-xl font-bold">Panom</h1>
      
      <div className="flex gap-2">
        <button data-tour="dashboard-action" className="btn-primary">
          + Yeni Sayaç
        </button>
        <button
          onClick={startTour}
          className="text-xs text-muted-foreground hover:underline"
          title="Kullanım Turunu Başlat"
        >
          ❓ Turu Göster
        </button>
      </div>
    </header>
  )
}
```

### Tarif 2: Bağımsız Coachmark (Yanıp Sönen İpucu Balonu)

```tsx
import { CoachmarkBeacon } from '@/components/ui/CoachmarkBeacon'

export function ShareButton() {
  return (
    <CoachmarkBeacon
      id="social-share-v2"
      title="Yeni: Sosyal Kart Paylaşımı 🎉"
      description="Artık sayaçlarınızı Instagram ve X formatında otomatik görsel kart olarak indirebilirsiniz!"
      placement="bottom"
    >
      <button className="btn-secondary">Paylaş</button>
    </CoachmarkBeacon>
  )
}
```
