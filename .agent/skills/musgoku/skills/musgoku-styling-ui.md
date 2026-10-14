---
name: musgoku-styling-ui
description: >-
  Tailwind CSS, Shadcn UI theming, responsive design, dark mode ve animasyon
  konularında best practice'ler. Tailwind v3 ve v4 arasındaki yapısal farklar ve
  sürüm tespiti de kapsamdadır. Hareket kütüphanesi entegrasyonu dahil.
---

# 🎨 MuSGoKu — Styling & UI Best Practices

## ⛔ Önce sürümü doğrula

Tailwind **v3 ve v4 arasında yapısal olarak kırılmıştır.** Kod yazmadan önce
`package.json` içindeki `tailwindcss` sürümü okunur. **Projenin sürümü esas
alınır**; aşağıdaki desenler her ikisinde de geçerlidir. Fark yaratan noktalar
için aşağıdaki "Tailwind sürüm farkları" bölümüne bak.

### Temel İlkeler
- **Utility-first** yaklaşımı benimse.
- İnline style kullanma, Tailwind class'ları kullan.
- `@apply` kullanımını minimumda tut (sadece tekrarlanan çok uzun class zincirlerinde).
- Responsive design **mobile-first** yaklaşımla yapılır.

### Responsive Design Pattern
```tsx
<div className="
  px-4 py-2                    {/* Mobile (default) */}
  sm:px-6 sm:py-3              {/* ≥640px */}
  md:px-8 md:py-4              {/* ≥768px */}
  lg:px-12 lg:py-6             {/* ≥1024px */}
  xl:px-16                     {/* ≥1280px */}
">
  <h1 className="text-lg md:text-xl lg:text-2xl font-bold">
    {t('page.title')}
  </h1>
</div>
```

### Dark Mode
```tsx
// Tailwind dark mode class-based strategy
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
  <Card className="bg-gray-50 dark:bg-gray-800 border dark:border-gray-700">
    <CardContent>
      <p className="text-gray-600 dark:text-gray-400">İçerik</p>
    </CardContent>
  </Card>
</div>
```

### Shadcn UI Theme (CSS Variables)
```css
/* src/index.css — CSS Variables pattern */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --muted: 210 40% 96.1%;
    --accent: 210 40% 96.1%;
    --destructive: 0 84.2% 60.2%;
    --border: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    /* ... */
  }
}
```

### 🎨 Küratörlü Renk & Tema Kartları (`.agent/skills/frontend-design/themes/`)
Generic renkler veya sıradan AI renk şablonları yerine, `.agent/skills/frontend-design/themes/` klasöründeki görsel renk kartları (`frontend-design-skill-theme-*.jpg`) incelenmelidir. Tıpkı `canvas-design`'da `./canvas-fonts` taranarak tipografi zenginliği sağlandığı gibi, burada da yüksek kontrastlı, modern tonlar (Tiffany `#21F1A8` & Dark Gray `#171717`, True Pink `#FD1843` & Chill White `#FFF9FA`, Lime Sprout `#E4FD97` & Fresh Canopy `#2D3E2C` vb.) projeye veya ilgili bileşene uyarlanmalıdır.

## Shadcn UI Bileşen Kullanımı

### Doğru Bileşen Seçimi
| İhtiyaç | Shadcn Bileşeni |
|---------|----------------|
| Buton | `Button` (variant: default, destructive, outline, secondary, ghost, link) |
| Dialog/Modal | `Dialog` |
| Onay dialog | `AlertDialog` |
| Dropdown menü | `DropdownMenu` |
| Select/Combo | `Select` veya `Combobox` (cmdk) |
| Form elemanları | `Input`, `Textarea`, `Checkbox`, `Switch` |
| Tablo | `Table` (DataTable pattern) |
| Tooltip | `Tooltip` |
| Toast/Bildirim | `Toast` (sonner) |
| Accordion | `Accordion` |
| Progress | `Progress` |
| Tab | `Tabs` |

### DataTable Pattern (Listeleme Sayfaları)
```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

function UserTable({ users, isLoading }: UserTableProps) {
  const { t } = useTranslation();

  if (isLoading) {
    return <TableSkeleton columns={5} rows={10} />;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>{t('user.name')}</TableHead>
          <TableHead>{t('user.email')}</TableHead>
          <TableHead>{t('user.role')}</TableHead>
          <TableHead>{t('user.status')}</TableHead>
          <TableHead className="text-right">{t('common.actions')}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.map((user) => (
          <TableRow key={user.id}>
            <TableCell className="font-medium">{user.name}</TableCell>
            <TableCell>{user.email}</TableCell>
            <TableCell>
              <Badge variant={getRoleBadgeVariant(user.role)}>
                {t(`roles.${user.role}`)}
              </Badge>
            </TableCell>
            <TableCell>
              <StatusBadge active={user.isActive} />
            </TableCell>
            <TableCell className="text-right">
              <UserActions user={user} />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

## Framer Motion Animasyonlar

```tsx
import { motion, AnimatePresence } from 'framer-motion';

// Sayfa geçiş animasyonu
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  in: { opacity: 1, y: 0 },
  out: { opacity: 0, y: -20 },
};

function AnimatedPage({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}

// Staggered list animasyonu
function AnimatedList({ items }: { items: Item[] }) {
  return (
    <motion.ul>
      {items.map((item, i) => (
        <motion.li
          key={item.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
        >
          {item.name}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

## Utility Classes Pattern

### cn() Helper (tailwind-merge + clsx)
```tsx
// src/lib/utils.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Kullanım
<div className={cn(
  'flex items-center gap-2 p-4 rounded-lg',
  isActive && 'bg-primary text-primary-foreground',
  isDisabled && 'opacity-50 cursor-not-allowed',
  className // dışarıdan gelen class'lar
)} />
```

## Kurallar

1. **Tailwind utility-first** — Custom CSS yazmak yerine Tailwind class kullan.
2. **Shadcn UI öncelikli** — Yeni bileşen yaratmadan önce Shadcn'de var mı kontrol et.
3. **Dark mode desteği** — Her yeni bileşende `dark:` variant'ları ekle.
4. **Mobile-first** — Default style'lar mobile için, breakpoint'ler büyük ekranlar için.
5. **cn() kullan** — Dinamik class'lar için `cn()` helper'ı kullan.
6. **Semantic renk adları** — `bg-primary`, `text-muted-foreground` gibi semantic isimler.
7. **Tutarlı spacing** — Tailwind spacing scale kullan (gap-2, gap-4, p-4, etc.).

## Tailwind sürüm farkları

Projede hangi ana sürım kullanılıyorsa **o** uygulanır. Göç kararı ayrı bir iş
adımıdır; gereksiz yere yükseltme.

| Konu | v3 | v4 |
|---|---|---|
| Yapılandırma | `tailwind.config.js` (JS/TS) | CSS-first: CSS dosyasında `:theme { ... }` |
| Dahil etme | `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss";` |
| PostCSS eklentisi | `tailwindcss` | Ayrı paket: `@tailwindcss/postcss` |
| Ön işleyici / ön ek | `postcss-import` + `autoprefixer` gerekli | v4 otomatik halleder → ikisi de **kaldırılır** |
| Tema değerleri | `theme.extend` içinde JS nesnesi | CSS değişkenleri (`--color-*`, `--font-family-*`) |

Göç yapılacaksa:

- Resmî geçiş aracı kullanılır: `npx @tailwindcss/upgrade` (Node.js 20+ gerekir).
- Araç bağımlılıkları, yapılandırma geçişini ve şablon düzeltmelerini otomatik yapar.
- Göç **ayrı commit**'tir; işlevsel değişiklikle aynı adımda yapılmaz.
- Yükseltme kararı ve gerekçesi `knowledge-base.md`'ye yazılır.

## Context7 Kullanımı

Shadcn UI bileşenlerine ihtiyaç duyulduğunda:
1. `context7` → `resolve-library-id` ile `shadcn/ui` ID'sini çöz
2. `context7` → `query-docs` ile güncel kullanım bilgisini al
3. Projede eksik bileşenler varsa `npx shadcn@latest add <component>` ile ekle
