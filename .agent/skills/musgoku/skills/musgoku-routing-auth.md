---
name: musgoku-routing-auth
description: >
  React Router DOM v7 routing, RBAC guard, lazy loading ve protected routes için best practices.
---

# 🛤️ MuSGoKu — Routing & Auth Best Practices

## React Router DOM v7 Kullanımı

> **⛔ Yığın kontrolü:** Bu sub-skill **yalnız React Router** içindir.
> Next.js App Router kullanılmaz — Next.js projesinde
> `musgoku-nextjs-fullstack` ve `musgoku-routing-auth` yerine o geçerlidir.
>
> **⛔ Sürüm notu:** React Router ana sürümleri arasında **paket adı değişti.**
> v6–v7'de import kaynağı `react-router-dom`; daha yeni sürümlerde paket
> kaldırılıp import kaynakları `react-router` ve `react-router/dom` olur.
> **Kod yazmadan önce `package.json` içindeki sürümü oku** ve import kaynağını
> oradan doğrula. Sürüm değişikliği toplu import göçü gerektirir; ayrı bir iş
> adımı olarak yapılır, kararı `knowledge-base.md`'ye yaz.

### Route Konfigürasyonu
```tsx
// src/App.tsx veya src/app/router.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { lazy, Suspense } from 'react';

// Lazy loaded page imports
const LoginPage = lazy(() => import('./features/auth/pages/LoginPage'));
const DashboardPage = lazy(() => import('./features/dashboard/pages/DashboardPage'));
const UserListPage = lazy(() => import('./features/user-management/pages/UserListPage'));

const router = createBrowserRouter([
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'forgot-password', element: <ForgotPasswordPage /> },
    ],
  },
  {
    path: '/dashboard',
    element: <AuthGuard><AdminLayout /></AuthGuard>,
    children: [
      { index: true, element: <DashboardPage /> },
      {
        path: 'users',
        element: <RoleGuard roles={['admin', 'manager']}><UserListPage /></RoleGuard>,
      },
    ],
  },
]);

function App() {
  return (
    <Suspense fallback={<FullPageLoader />}>
      <RouterProvider router={router} />
    </Suspense>
  );
}
```

### Auth Guard Pattern
```tsx
// src/context/AuthGuard.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <FullPageLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
```

### Role-Based Guard (RBAC)
```tsx
// src/context/RoleGuard.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface RoleGuardProps {
  children: React.ReactNode;
  roles: string[];
  fallback?: string;
}

export function RoleGuard({ children, roles, fallback = '/dashboard' }: RoleGuardProps) {
  const { user } = useAuth();

  if (!user || !roles.includes(user.role)) {
    return <Navigate to={fallback} replace />;
  }

  return <>{children}</>;
}
```

### Navigation Patterns
```tsx
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

function UserDetailPage() {
  const navigate = useNavigate();
  const { userId } = useParams<{ userId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();

  const handleBack = () => navigate(-1);
  const handleGoToEdit = () => navigate(`/dashboard/users/${userId}/edit`);
  
  // Query param ile filtreleme
  const page = Number(searchParams.get('page') || '1');
  const handlePageChange = (newPage: number) => {
    setSearchParams({ page: String(newPage) });
  };

  return (/* ... */);
}
```

### Route Yapısı Kuralları

```
/                              → Public layout
├── /login                     → Login sayfası
├── /forgot-password           → Şifre sıfırlama
│
/dashboard                     → Auth Guard → Admin layout
├── /dashboard                 → Dashboard (role-based)
├── /dashboard/users           → Kullanıcı listesi (admin/manager)
├── /dashboard/users/:id       → Kullanıcı detay
├── /dashboard/companies       → Şirket yönetimi (admin)
├── /dashboard/settings        → Ayarlar
├── /dashboard/reports         → Raporlar
└── /dashboard/exams           → Sınav yönetimi
```

## Kurallar

1. **Route tanımları merkezi** — Tüm route'lar `App.tsx` veya `app/router.tsx` içinde tanımlanır.
2. **Lazy loading zorunlu** — Her sayfa `lazy(() => import(...))` ile yüklenir.
3. **Suspense ile sarmalama** — Lazy loaded bileşenler `<Suspense>` ile sarılır.
4. **Auth Guard** — Protected route'lar `<AuthGuard>` ile korunur.
5. **Role Guard** — Rol bazlı sayfalar `<RoleGuard roles={[...]}/>` ile korunur.
6. **Route parametreleri typed** — `useParams<{ id: string }>()` ile tip güvenli erişim.
7. **Query params** — Filtreleme ve pagination için `useSearchParams` kullanılır.

## React Router v7 Middleware (İleri Seviye)

React Router v7, route seviyesinde middleware desteği sunar:

```tsx
// Auth middleware
async function authMiddleware({ context }) {
  const user = await getUser();
  if (!user) {
    throw redirect('/login');
  }
  context.set(userContext, user);
}

// Route config'de kullanım
const routes = [
  {
    path: '/dashboard',
    middleware: [authMiddleware],
    Component: Dashboard,
  },
];
```

> **Not:** Middleware pattern projenin mevcut guard yapısıyla uyumlu olacak şekilde kademeli olarak geçilebilir.

## Anti-Patterns

- ❌ `window.location.href` ile navigation (React Router `useNavigate` kullan)
- ❌ Her bileşende auth kontrolü (Guard component'ler kullan)
- ❌ Route string'lerinin hardcode edilmesi (sabit dosyasından al)
- ❌ Sayfa seviyesinde doğrudan import (lazy loading kullan)
