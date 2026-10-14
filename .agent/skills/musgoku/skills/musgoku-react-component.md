---
name: musgoku-react-component
description: >
  React bileşen oluşturma, düzenleme ve refactoring için best practice kuralları.
  Hook'lar, durum, performans, hata sınırı, erişilebilirlik ve test konularını kapsar.
  React + TypeScript + Shadcn UI + Radix UI + Tailwind CSS ile uyumlu.
  Proje dizin yapısı için `references/frontend-project-structure.md`.
---

# 🧩 MuSGoKu — React Component Best Practices

## Bileşen Oluşturma Standartları

### Nereye yazılır

Bu dosya **nasıl yazılır** sorusunu yanıtlar. **Nereye yazılır** sorusu için:
[`references/frontend-project-structure.md`](../references/frontend-project-structure.md).

| Ne | Nerede |
|---|---|
| Yalnız bir özellikte kullanılan bileşen | `features/<feature>/components/` |
| Birden çok yerde kullanılan bileşen | `shared/components/` |
| Sayfa düzeyi bileşen | `features/<feature>/pages/` |
| Yeniden kullanılan hook | `shared/hooks/` veya `features/<feature>/hooks/` |

### Dosya Yapısı
```tsx
// 1. Import'lar (sıralı)
import { useState, useCallback, useMemo } from 'react';       // React core
import { useTranslation } from 'react-i18next';               // i18n
import { useQuery } from '@tanstack/react-query';              // Data
import { Button } from '@/components/ui/button';               // UI
import type { SomeType } from './types';                       // Types (type-only import)

// 2. Type/Interface tanımları
interface ComponentNameProps {
  title: string;
  onAction: (id: string) => void;
  isLoading?: boolean;
}

// 3. Ana bileşen (named export)
export function ComponentName({ title, onAction, isLoading = false }: ComponentNameProps) {
  const { t } = useTranslation();
  
  // State
  const [isOpen, setIsOpen] = useState(false);
  
  // Memoized values
  const computedValue = useMemo(() => /* ... */, [dependency]);
  
  // Callbacks
  const handleClick = useCallback(() => {
    onAction('id');
  }, [onAction]);
  
  // Guard clauses / Early returns
  if (isLoading) {
    return <LoadingSkeleton />;
  }
  
  // Render
  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-lg font-semibold">{t('component.title')}</h2>
      <Button onClick={handleClick}>{t('common.action')}</Button>
    </div>
  );
}
```

### Kurallar

1. **Functional Components Only** — Class component kullanılmaz.
2. **Named Export** — `export default` yerine `export function ComponentName` kullanılır.
3. **Props Interface** — Her bileşenin prop'ları TypeScript interface ile tanımlanır.
4. **Type-only Imports** — `import type { X }` kullanılır (bundle size optimizasyonu).
5. **Küçük ve Odaklı** — 200 satırı aşan bileşenler alt bileşenlere bölünür.
6. **Composition over Inheritance** — Bileşen kompozisyonu tercih edilir.

### Shadcn UI Kullanımı

```tsx
// ✅ DOĞRU: Shadcn UI bileşenlerini kullan
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';

// ❌ YANLIŞ: Ham HTML elemanları ile form/dialog oluşturma
<button className="bg-blue-500">Click</button>
<input type="text" className="border p-2" />
```

### Radix UI Entegrasyonu

- Shadcn UI bileşenleri Radix primitives üzerine kuruludur.
- Accessibility (ARIA) ve focus management otomatik sağlanır.
- Kontrollü state için Radix state management API'sini kullan.

### Performance Optimizasyonları

```tsx
// React.memo — Sık render olan ama prop'ları değişmeyen bileşenler
export const ExpensiveList = React.memo(function ExpensiveList({ items }: Props) {
  return items.map(item => <ListItem key={item.id} {...item} />);
});

// useMemo — Pahalı hesaplamalar
const filteredData = useMemo(
  () => data.filter(item => item.status === activeFilter),
  [data, activeFilter]
);

// useCallback — Child component'lere geçilen fonksiyonlar
const handleSort = useCallback((column: string) => {
  setSortBy(column);
}, []);
```

### Lazy Loading

```tsx
import { lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <HeavyChart data={chartData} />
    </Suspense>
  );
}
```

### Error Boundary Pattern

```tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';

function FeaturePage() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <FeatureContent />
    </ErrorBoundary>
  );
}
```

### Naming Conventions

| Tür | Format | Örnek |
|-----|--------|-------|
| Bileşen dosyası | PascalCase | `UserProfile.tsx` |
| Hook dosyası | camelCase `use` prefix | `useAuth.ts` |
| Sayfa bileşeni | PascalCase + Page suffix | `DashboardPage.tsx` |
| Utility dosyası | camelCase | `formatDate.ts` |
| Type dosyası | camelCase veya `types.ts` | `types.ts` |
| CSS module | camelCase | `userProfile.module.css` |

### Anti-Patterns (Kaçınılması Gerekenler)

- ❌ `useEffect` içinde doğrudan API çağrısı (TanStack Query kullan)
- ❌ Prop drilling (Context API veya state management kullan)
- ❌ Inline style (Tailwind class kullan)
- ❌ Hardcoded string (i18n key kullan)
- ❌ `any` type kullanımı (doğru tip tanımla)
- ❌ `index.tsx` içinde multiple export (tek dosya tek sorumluluk)
- ❌ Listede indeks anahtarı (`id` veya kalıcı bir anahtar kullan)
- ❌ Koşullu hook çağrısı veya iç içe hook
- ❌ Sayfa bileşeninde doğrudan API çağrısı (servis katmanına taşı)
- ❌ Tıklanabilir `div`/`span` (düğme/bağlantı öğesi kullan)

---

## Erişilebilirlik

Erişilebilirlik sonradan "eklenen" bir şey değildir; bileşen yazılırken yapılır.

| Konu | Kural |
|---|---|
| Anlamsal HTML | Düğme için `<button>`, bağlantı için `<a>`. Tıklanabilir `div` **yazılmaz.** |
| Etiket | Her form alanının `<label>` bağlantısı (`htmlFor` ↔ `id`) |
| Alternatif metin | Anlamlı görsellerde `alt`; dekoratif görsellerde boş `alt` |
| Klavye | Tüm etkileşim klavyeyle yapılabilir; `tabIndex` doğal sırayı bozmaz |
| Odak | Odak halkası **görünür** kalmalı; klavye kullanıcısı için `outline: none` yazılmaz |
| Odak tuzağı | Modal açıldığında odak içeri alınır, kapanınca tetikleyiciye döner |
| Canlı bölge | Dinamik olarak beliren hata/başarı mesajları ekran okuyucuya duyurulur |
| Renk tek başına anlam taşımaz | Durum yalnız renkle bildirilmez; ikon veya metinle de bildirilir |

Bileşen kitaplığı (Shadcn / Radix) kullanılıyorsa odak yönetimi ve klavye
desteği genelde hazırdır — **kapatma.** Hazır davranışı elle bozma.

---

## Test

| Konu | Kural |
|---|---|
| Kapsam | Her özellik veya bileşen için en az bir birim test |
| Konum | `__tests__` klasörü veya dosya yanında `.test.tsx` |
| Kütüphane | Projenin test kütüphanesi kullanılır; `package.json` okunur |
| Odağ | Kullanıcı davranışı test edilir, iç yapı değil |
| Zorunlu senaryolar | boş durum · hata durumu · yükleme durumu · sınır değerleri |
| Erişilebilirlik | Klavye ile gezinme ve odak testi |

**Zorunlu senaryolar atlanmaz.** "Test yazmaya vaktim yok" gerekçesi kuralı
geçersiz kılmaz; eksikse `knowledge-base.md`'ye geçici çözüm olarak yazılır.

---

## Bileşen teslim kontrol listesi

- [ ] Doğru klasöre konuldu mu (tek kullanımlık mı, paylaşılan mı)?
- [ ] 200 satır sınırı aşılmadı mı?
- [ ] Tüm görünür metinler i18n anahtarından mı geliyor?
- [ ] Yükleme · boş · hata durumları var mı?
- [ ] Anlamsal HTML ve etiketler doğru mu?
- [ ] Klavyeyle tam kullanılabiliyor mu?
- [ ] Liste anahtarları kalıcı mı?
- [ ] Hook sırası doğru mu; erken return öncesi tüm hook'lar çağrılıyor mu?
- [ ] En az bir test var mı?
