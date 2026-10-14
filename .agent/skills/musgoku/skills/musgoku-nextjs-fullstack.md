---
name: musgoku-nextjs-fullstack
description: >
  Next.js 15/16 App Router mimarisi, Server Components (RSC), SSR, Suspense,
  Route Handlers, önbellekleme stratejileri ve gelecekteki Next.js geçişi için standartlar.
---

# ⚡ MuSGoKu — Next.js Fullstack & App Router Architecture

> **Kullanım Amacı:** Bu skill, projenin gelecekte **Next.js**'e geçirilmesi veya Next.js tabanlı modüller/projeler geliştirilmesi durumunda devreye alınır.
> Mevcut Vite SPA yapısında Next.js direktifleri (`'use client'`, SSR vb.) kullanılmaz; ancak Next.js moduna geçildiğinde bu rehber birincil kılavuzdur.

---

## 🏗️ 1. Proje Yapısı (App Router Standartları)

```
app/
├── (auth)/                    # Route groups (URL'yi etkilemez)
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
├── (dashboard)/
│   ├── layout.tsx             # Ortak dashboard layout (RSC)
│   └── dashboard/
│       ├── page.tsx           # Ana dashboard sayfası (RSC)
│       ├── loading.tsx        # Suspense fallback
│       └── error.tsx          # Error boundary ('use client')
├── api/                       # Route handlers (REST endpoints)
│   └── webhooks/
│       └── route.ts
├── layout.tsx                 # Root layout (Html, Body, Global providers)
├── not-found.tsx              # 404 sayfası
└── global-error.tsx           # Root error boundary
components/
├── ui/                        # Shadcn primitifleri
└── shared/                    # Proje geneli ortak bileşenler
lib/
├── safe-action.ts             # next-safe-action client
├── db.ts                      # Veritabanı istemcisi
└── utils.ts                   # cn ve yardımcı fonksiyonlar
```

---

## 🧩 2. Server Components (RSC) vs Client Components Kuralları

### Altın Kural: Varsayılan Olarak Server Component Kullan!
1. **Server Components (RSC) — Varsayılan:**
   - Veri tabanına veya güvenli API'lara doğrudan erişim.
   - Hassas bilgileri (API key, token) sunucuda tutma.
   - Büyük bağımlılıkları (bundle size) client'a indirmeme.
   - Direktif içermez (varsayılandır).

2. **Client Components (`'use client'`) — Yalnızca İhtiyaç Halinde:**
   - `useState`, `useEffect`, `useReducer` gibi React hook'ları gerektiğinde.
   - `onClick`, `onChange`, `onSubmit` gibi DOM event listener'ları.
   - Tarayıcı API'ları (`window`, `localStorage`, `navigator`).
   - Framer Motion gibi animasyon kütüphaneleri.

### Boundary (Sınır) Deseni:
```tsx
// ❌ KÖTÜ: Tüm sayfayı client component yapmak
'use client';
export default function DashboardPage() {
  const data = useFetchData();
  return <div><HeavyDataChart data={data} /><InteractiveButton /></div>;
}

// ✅ İYİ: Veriyi RSC'de çek, sadece etkileşimli parçaya 'use client' koy
// app/dashboard/page.tsx (Server Component)
import { Suspense } from 'react';
import { InteractiveFilter } from './components/InteractiveFilter';
import { DataList } from './components/DataList';

export default async function DashboardPage() {
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <InteractiveFilter />
      <Suspense fallback={<div>Yükleniyor...</div>}>
        <DataList />
      </Suspense>
    </div>
  );
}
```

---

## ⚡ 3. Veri Çekme (Data Fetching) ve Caching

### Modern Fetch & Caching:
```tsx
// Server Component içinde doğrudan async/await
async function getCompanyMetrics(companyId: string) {
  const res = await fetch(`https://api.example.com/companies/${companyId}/metrics`, {
    next: { 
      revalidate: 60, // ISR: 60 saniyede bir yeniden doğrula
      tags: [`company-${companyId}`] // On-demand revalidation için etiket
    }
  });

  if (!res.ok) {
    throw new Error('Metrikler alınamadı');
  }

  return res.json();
}
```

### Mutasyon Sonrası Yenileme:
```ts
import { revalidateTag, revalidatePath } from 'next/cache';

export async function mutateData() {
  // işlem...
  revalidateTag('company-123'); // veya revalidatePath('/dashboard');
}
```

---

## 🖼️ 4. Performans ve Optimizasyon

1. **`next/image` Zorunluluğu:**
   ```tsx
   import Image from 'next/image';

   <Image
     src="/images/logo.png"
     alt="Company Logo"
     width={120}
     height={40}
     priority // Above-the-fold görseller için LCP optimizasyonu
     placeholder="blur"
     blurDataURL="data:image/svg+xml;base64,..."
   />
   ```
2. **`next/font` Kullanımı:**
   - Web fontları derleme zamanında indirilir ve self-host edilir (sıfır layout shift / CLS).
3. **Dynamic Import (Lazy Loading):**
   ```tsx
   import dynamic from 'next/dynamic';

   const HeavyEditor = dynamic(() => import('@/components/HeavyEditor'), {
     loading: () => <p>Editör yükleniyor...</p>,
     ssr: false // Yalnızca client-side çalışacaksa
   });
   ```

---

## 🛡️ 5. Error Boundaries & Loading States

- Her route segmentinde `loading.tsx` (Suspense) tanımlanmalıdır.
- Her modülde `error.tsx` (`'use client'`) ve `reset()` butonu bulunmalıdır.
- En üstte `app/global-error.tsx` mutlaka yer almalıdır.
