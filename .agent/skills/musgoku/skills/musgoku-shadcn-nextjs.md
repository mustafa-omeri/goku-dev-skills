---
name: musgoku-shadcn-nextjs
description: >
  Next.js App Router ve React 19 ortamında Shadcn UI kullanımı standartları.
  Server Component / Client Component sınırları, next-themes entegrasyonu ve Next.js Image optimizasyonları.
---

# 🎨 MuSGoKu — Shadcn UI in Next.js & App Router

> **Kullanım Amacı:** Bu skill, gelecekte Next.js ve React 19 mimarisine geçildiğinde Shadcn UI bileşenlerinin Server Component ve Client Component sınırlarına uygun şekilde yapılandırılmasını sağlar.

---

## 🏛️ 1. Shadcn UI Bileşenleri ve `'use client'` Kuralları

Shadcn UI bileşenleri temel olarak Radix UI primitiflerini kullanır. Radix UI bileşenleri event listener ve DOM state'i gerektirdiğinden genelde client component'tir:

| Bileşen Grubu | Component Tipi | Açıklama |
| :--- | :--- | :--- |
| **Statik UI** (`Badge`, `Card`, `Separator`, `Skeleton`) | **Server Component (RSC)** | `'use client'` gerektirmez. Doğrudan sunucuda render edilir. |
| **Etkileşimli UI** (`Dialog`, `DropdownMenu`, `Popover`, `Tabs`, `Accordion`, `Select`, `Tooltip`) | **Client Component** | Başında `'use client'` bulunmalıdır. |
| **Form Kontrolleri** (`Button`, `Input`, `Checkbox`, `Switch`, `Textarea`) | **Client Component** | Form state ve event handling nedeniyle `'use client'` içerir. |

### RSC Sayfasında Shadcn Kullanım Deseni:
```tsx
// app/dashboard/page.tsx (Server Component - no 'use client')
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CompanyActionDropdown } from "./CompanyActionDropdown"; // 'use client'

export default async function DashboardPage() {
  const company = await fetchCompanyData();

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row justify-between items-center">
        <CardTitle>{company.name}</CardTitle>
        <Badge variant={company.isActive ? "default" : "secondary"}>
          {company.status}
        </Badge>
        {/* Yalnızca etkileşimli dropdown client component olarak yüklenir */}
        <CompanyActionDropdown companyId={company.id} />
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">{company.description}</p>
      </CardContent>
    </Card>
  );
}
```

---

## 🌓 2. Next.js Dark Mode & ThemeProvider (`next-themes`)

Next.js App Router'da FOUC (Flash of Unstyled Content) yaşamamak için `next-themes` doğru entegre edilmelidir:

```tsx
// components/theme-provider.tsx
"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { type ThemeProviderProps } from "next-themes/dist/types";

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
```

```tsx
// app/layout.tsx (Server Component)
import { ThemeProvider } from "@/components/theme-provider";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr" suppressHydrationWarning>
      <head />
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

---

## 🖼️ 3. Shadcn `Avatar` ve Görsel Bileşenlerinde `next/image` Entegrasyonu

Shadcn'in varsayılan `AvatarImage` bileşeni yerine Next.js'in optimize edilmiş `next/image` kullanımı:

```tsx
// components/ui/optimized-avatar.tsx
import Image from "next/image";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

interface Props {
  src?: string | null;
  name: string;
  size?: number;
}

export function OptimizedAvatar({ src, name, size = 40 }: Props) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <Avatar className={`w-[${size}px] h-[${size}px]`}>
      {src ? (
        <Image
          src={src}
          alt={name}
          width={size}
          height={size}
          className="aspect-square object-cover"
        />
      ) : (
        <AvatarFallback>{initials}</AvatarFallback>
      )}
    </Avatar>
  );
}
```

---

## ⚠️ 4. Error Boundary ve Suspense Entegrasyonu

Shadcn `Skeleton` bileşenleri `loading.tsx` dosyalarında Suspense fallback olarak kullanılmalıdır:

```tsx
// app/dashboard/loading.tsx
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardLoading() {
  return (
    <div className="space-y-4 p-6">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Skeleton className="h-32 w-full rounded-xl" />
        <Skeleton className="h-32 w-full rounded-xl" />
        <Skeleton className="h-32 w-full rounded-xl" />
      </div>
    </div>
  );
}
```
