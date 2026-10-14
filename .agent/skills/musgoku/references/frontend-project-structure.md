# Frontend Proje Yapısı

> Frontend projelerinde dizin ve dosya sorumluluklarının yerleşimi.
> Hangi klasörde ne durur, hangi dosya neyi yapar.
>
> Bu dosya **tekniktir**, projeye özgü değildir. Projenin kendi varyasyonu varsa
> `AGENTS.md` → *Proje Bazlı Ek Kurallar* altında farkı yaz.

---

## 1. Temel şema

```
src/
├── app/                              # giriş noktası, router, provider, global state, config
│   ├── router.tsx                    # route tanımları + yetki koruması
│   ├── providers.tsx                 # context sağlayıcıları (auth, tema, sorgu)
│   ├── store.ts                      # global durum (redux/zustand/redux toolkit)
│   └── config/                       # uygulama düzeyi sabitler ve ayarlar
│
├── tenants/                          # çok kiracılı projede kiracıya özel katman
│   └── <tenantCode>/
│       ├── layout/                   # kiracı düzeyi yerleşim
│       ├── theme/                    # kiracı markası / paleti
│       └── overrides/                # bileşen geçersiz kılmaları (opsiyonel)
│
├── features/                         # iş modülleri (domain odaklı)
│   └── <feature>/
│       ├── components/               # yalnız bu özelliğe ait bileşenler
│       ├── pages/                    # sayfa düzeyi bileşenler
│       ├── hooks/                    # özelliğe özel hook'lar
│       ├── services/                 # API çağrıları
│       ├── slices/                   # durum dilimleri (redux/zustand vs.)
│       ├── guards/                   # route veya politika koruması
│       └── types.ts                  # özellik tip tanımları
│
├── shared/                           # uygulama geneline ait ortak katman
│   ├── components/                   # Modal, Table, Sidebar gibi yeniden kullanılanlar
│   ├── layout/                       # AdminLayout, PublicLayout vs.
│   ├── hooks/                        # useDebounce, useAuth vs.
│   ├── utils/                        # tarih, metin, biçim yardımcıları
│   ├── constants/                    # roller, izinler, route sabitleri
│   ├── icons/                        # tüm ikonlar
│   └── types/                        # ortak interface ve tip tanımları
│
├── styles/                           # Tailwind / SCSS / değişken dosyaları
├── assets/                           # görseller, fontlar
└── main.tsx                          # uygulama giriş noktası
```

---

## 2. Nerede ne durur

| Yapı | Kural |
|---|---|
| `app/` | Router, provider, global durum ve uygulama düzeyi yapılandırma. Özellik mantığı **buraya girmez.** |
| `features/<feature>/` | Bir özelliğin **tamamı** tek klasörde: UI, durum, API ve yardımcılar. Başka modüllerden bağımsız olmalı. |
| `features/*/components/` | Yalnız o özelliğe ait bileşenler |
| `shared/components/` | **Yeniden kullanılabilir** her bileşen. Bir kez kullanılıyorsa `shared/` değil, `features/` altında kalır. |
| `shared/hooks/` | Birden çok özellikte kullanılan hook'lar |
| `features/*/services/` | Yalnız o özelliğin API çağrıları. Dış dünyayla iletişim bu katmandan yapılır. |
| `shared/types/` | Birden çok özellikte kullanılan tipler |
| `styles/` | Global stil yapılandırması |

**Taşıma kuralı:** bir bileşen ikinci bir yerde kullanılmaya başlarsa
`features/*/components` → `shared/components` taşınır. Kullanılmıyorsa
`features/` altında kalır.

---

## 3. Router

- Tüm route tanımları **tek dosyada** merkezî olarak yönetilir (`app/router.tsx`).
- Route koruması (auth + rol + kiracı) burada tanımlanır; sayfa bileşeninin
  içine gömülmez.
- Lazy loading ve kod bölme **zorunludur** (bkz.
  [`rules/frontend-bundle-limits.md`](../../../rules/frontend-bundle-limits.md)).
- Sayfa, arama ve sıralama URL'e yansıtılır (paylaşılabilirlik + geri tuşu).

---

## 4. Durum yönetimi

| Kapsam | Araç |
|---|---|
| Sunucu verisi (liste, detay, cache) | Sorgu kütüphanesi — `musgoku-api-data-layer.md` |
| Bileşen içi yerel durum | `useState` / `useReducer` |
| Paylaşılan istemci durumu | Context |
| Uygulama geneli istemci durumu | Redux toolkit · Zustand · benzeri |

- Her özellik kendi durum dilimine sahip olmalı, diğer modüllerden bağımsız
  çalışmalı.
- Durum mümkün olduğunca **kullanıldığı yere yakın** tutulur; prop zinciri
  (prop drilling) önlenir.
- Durum kütüphanesi **yalnız gerçekten gerekli olduğunda** eklenir.

---

## 5. Component kuralları

- Küçük, saf (pure) ve yeniden kullanılabilir olacak şekilde tasarlanır.
- Kalıtım yerine **bileşim** kullanılır.
- Büyük bileşenler sorumluluklarına göre bölünür → [`references/clean-code-conventions.md`](./clean-code-conventions.md)
- Stil bileşene yakın durur; global stil yalnız `styles/` altında

## 6. Hook kuralları

- Tüm özel hook'lar `shared/hooks` veya `features/<feature>/hooks` altında tanımlanır.
- `use` ön ekiyle başlar ve **tek başına test edilebilir** (ağ çağrısı yapmaz,
  yalnız mantık yürütür).
- Hook kuralları ihlal edilmez; iç içe hook yazılmaz.

## 7. API ve servisler

- Tüm API çağrıları `services/` altındadır; dış dünya ile iletişim **bu katmandan**
  yapılır.
- Ortak HTTP istemcisi yapılandırması tek yerde toplanır.

## 8. Tip ve isimlendirme

| Öğe | Kural |
|---|---|
| Tip tanımları | `features/<f>/types.ts` veya `shared/types` |
| Bileşen dosyası | PascalCase — `UserProfile.tsx` |
| Hook dosyası | `useX.ts` |
| Sayfa bileşeni | `<Feature>Page.tsx` |
| Dizin adı | Küçük harf, tireli (`components/auth-wizard`) |
| Tip güvenliği | Tüm kodda strict mod açık |

## 9. Çok kiracılı katman

Çok kiracılı projelerde kiracıya özel görünüm/etiket gerekiyorsa `tenants/<kod>/`
altına ayrılır. **Tek kiracılı projede bu katman kurulmaz** — boş klasör
ihtiyacı yoktur.

## 10. Lint ve biçimlendirme

- Lint + biçimlendirme aracı birlikte kullanılır.
- Commit öncesi lint kontrolü **kanca (hook)** ile zorunlu hale getirilir.
  (Araç seçimi projeye aittir; kural, kontrolün **otomatik** olmasıdır.)
- Bu kurallar araç adına değil, **davranışa** bağlıdır; araç değişse de kural
  geçerlidir.

## 11. Test

- Her özellik veya bileşen için en az bir birim test bulunmalıdır.
- Test dosyaları ya `__tests__` klasöründe ya da dosya yanında `.test.tsx`
  olarak durur.
- Test konumu ve çalıştırma komutu projeye özeldir; `package.json` okunur.

## 12. Sık yapılan hatalar

| Hata | Doğrusu |
|---|---|
| `shared/components` içinde tek kullanımlık bileşen | `features/<f>/components` altında kalmalı |
| Özellik mantığını `app/` altına yazmak | `features/` altına taşı |
| Aynı route tanımını iki yerde tutmak | `app/router.tsx` tek kaynak |
| Özelliğe özel bir bileşeni `shared/` altına koymak | Paylaşılıyorsa `shared/`, paylaşılmıyorsa `features/` |
| Hook'un içinde doğrudan API çağrısı | Servis katmanına taşı; hook mantık yürütsün |
| Dizin adlarında `PascalCase` veya `kebab-case` yerine karışık kullanım | Küçük harf + tire |
| Aynı dosyanın hem `shared/` hem `features/` altında olması | Bir yer seç |

## 13. Doğrulama

- [ ] Her route `app/router.tsx` içinde mi?
- [ ] Her özelliğin kendi klasörü tam mı?
- [ ] `shared/` altında tek kullanımlık bileşen var mı?
- [ ] API çağrısı `services/` dışında mı kalmış?
- [ ] Aynı tip iki yerde tanımlı mı?
- [ ] Dizin adları tutarlı mı?
- [ ] Çok kiracılı katman gerçekten gerekiyor mu?
- [ ] En az bir test var mı?
- [ ] Bundle bütçesi ölçüldü mü?