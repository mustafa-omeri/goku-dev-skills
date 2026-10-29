---
name: Vite SPA Enforcement
description: React + Vite SPA projelerinde Next.js konseptlerinin ve sunucu tarafı kalıplarının kullanılmamasını zorunlu kılar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Frontend / Vite SPA"
    komut: "python .agent/skills/musgoku/scripts/check_vite_spa.py"
---

# ⛔ Bu proje Vite SPA'dır — Next.js konseptleri kullanılmaz

> Bu kural **yalnız frontend projesinde** geçerlidir ve dağıtımda proje
> yığını doğrulanmadan varsayılan olarak uygulanır. Yığın Next.js ise bu kural
> **geçersizdir** ve `musgoku-nextjs-fullstack` · `musgoku-next-safe-action` ·
> `musgoku-shadcn-nextjs` sub-skill'leri devreye girer.

## Yığını tespit et

Kod yazmadan önce yığını doğrula: `package.json` → `dependencies`.
`next` varsa bu kural geçersizdir; `react-router-dom` varsa uygulanır.

## Yasaklı kavramlar ve yerine kullanılacaklar

| Yasak | Yerine |
|---|---|
| `"use client"` / `"use server"` | Gerek yok — her bileşen client-side |
| Server Components (RSC) | TanStack Query ile client-side veri çekme |
| SSR / SSG / ISR | SPA; ilk veri isteğini `useQuery` yapar |
| App Router / file-based routing | `react-router-dom` ile deklaratif routing |
| `next/image` | Standart `<img>` veya optimize edilmiş public dosyası |
| `next/link` | React Router `<Link>` / `<NavLink>` |
| `next/font` | Yerel font dosyası veya linklenmiş font ailesi |
| `next-safe-action` | Doğrudan Axios + Zod doğrulama |
| `next/headers`, `next/cookies` | `localStorage` / uygun istemci depolaması |
| Middleware (Next.js) | React Router guard / layout bileşenleri |
| `getServerSideProps` / `getStaticProps` | `useQuery` |

## Doğru SPA kalıpları

- Ortam değişkeni: `import.meta.env.VITE_*` (`process.env` **değil**)
- Build: projenin production build komutu
- Dev sunucusu: `npm run dev`
- Path alias: `@/` — `vite.config.js` içinde tanımlıdır
- Kod bölme: `React.lazy()` + `import()` (bkz. `frontend-bundle-limits.md`)
- Asenkron veri ve lazy loading: `React.Suspense` fallback veya query loading durumlarında jenerik spinner yerine hedef sayfa/bileşenin wireframe kaset yapısını taklit eden Skeleton ekranı render edilmelidir (bkz. `design-skills-enforcement.md` §2.2.1).

## İhlal kontrolü — her kod üretiminde

```powershell
python .agent/skills/musgoku/scripts/check_vite_spa.py
```

| Exit | Anlam | Ne yap |
|---|---|---|
| 0 | Next.js izi yok | Devam |
| 1 | `E1`-`E4`: Next.js paketi / yapılandırması / import / `use client` | Bulgu adıyla birlikte düzelt |
| 0 | Proje Next.js veya frontend değil | Kural bu projede geçersiz |

Kontrol listesi (gözle, script taradıktan sonra):

1. `"use client"` / `"use server"` var mı? → kaldır
2. `next/` import'u var mı? → kaldır, karşılığını kullan
3. `process.env` kullanılmış mı? → `import.meta.env` ile değiştir
4. Sunucu tarafı veri getirme deseni var mı? → TanStack Query'ye geç

Bulgu varsa düzelt ve `knowledge-base.md`'ye yaz. Sessizce geçme.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir SPA istisnası veya hibrit yapı kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_