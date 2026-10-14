---
name: musgoku-typescript-quality
description: >
  TypeScript strict mode, tip güvenliği, build compliance ve kod kalitesi
  standartları. Production Docker build uyumu için kritik kurallar.
---

# 🔐 MuSGoKu — TypeScript & Code Quality Best Practices

## TypeScript Strict Mode Kuralları

### ⚠️ KRİTİK: Build Uyumluluğu
```
Production Docker build komutu: tsc -b && vite build
TS6133 (unused variable/import) → Build FAIL (Exit Code 2)
```

**Her geliştirmeden sonra çalıştır:**
```bash
npx tsc --noEmit
```

### Type-Only Imports
```tsx
// ✅ DOĞRU: type-only import (bundle'a dahil olmaz)
import type { User, UserRole } from './types';
import type { AxiosResponse } from 'axios';

// ❌ YANLIŞ: gereksiz runtime import
import { User } from './types';  // Sadece tip olarak kullanılıyorsa
```

### Interface vs Type

```tsx
// ✅ Interface — Object shape tanımları için tercih et
interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
}

// ✅ Type — Union types, intersection types, mapped types için
type UserRole = 'admin' | 'manager' | 'employee';
type ApiResponse<T> = { data: T; message: string; success: boolean };
type Nullable<T> = T | null;

// ✅ Interface extension
interface CreateUserDto extends Omit<User, 'id' | 'createdAt'> {
  password: string;
}
```

### Generic Types
```tsx
// Paginated response generic
interface PaginatedResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
  first: boolean;
  last: boolean;
}

// API service generic
async function fetchPaginated<T>(
  url: string,
  params?: Record<string, unknown>
): Promise<PaginatedResponse<T>> {
  const { data } = await httpClient.get(url, { params });
  return data;
}
```

### Strict Null Checks
```tsx
// ✅ Guard clause pattern
function getUserName(user: User | null): string {
  if (!user) {
    return 'Unknown User';
  }
  return `${user.firstName} ${user.lastName}`;
}

// ✅ Optional chaining
const roleName = user?.role?.name ?? 'N/A';

// ❌ Non-null assertion (kaçınılmalı)
const name = user!.name; // Tehlikeli!
```

### Enum Alternatives
```tsx
// ✅ DOĞRU: const object + typeof (tree-shakeable)
export const UserRole = {
  ADMIN: 'admin',
  MANAGER: 'manager',
  EMPLOYEE: 'employee',
} as const;

export type UserRole = typeof UserRole[keyof typeof UserRole];

// ❌ YANLIŞ: TypeScript enum (tree-shake edilemez)
enum UserRole {
  Admin = 'admin',
  Manager = 'manager',
}
```

### Type Guard
```tsx
function isApiError(error: unknown): error is { message: string; status: number } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'status' in error
  );
}

// Kullanım
try {
  await userService.createUser(data);
} catch (error) {
  if (isApiError(error)) {
    toast.error(error.message);
  } else {
    toast.error('Bilinmeyen hata');
  }
}
```

## Kod Kalitesi Standartları

### Guard Clauses / Early Return
```tsx
// ✅ DOĞRU: Guard clause pattern
function processUser(user: User | null, role: string): string {
  if (!user) return 'No user';
  if (!user.isActive) return 'User inactive';
  if (role !== 'admin') return 'Unauthorized';
  
  // Happy path en sonda
  return `Welcome, ${user.name}!`;
}

// ❌ YANLIŞ: Nested if
function processUser(user: User | null, role: string): string {
  if (user) {
    if (user.isActive) {
      if (role === 'admin') {
        return `Welcome, ${user.name}!`;
      } else {
        return 'Unauthorized';
      }
    } else {
      return 'User inactive';
    }
  } else {
    return 'No user';
  }
}
```

### Descriptive Variable Names
```tsx
// ✅ DOĞRU: Auxiliary verb'li isimler
const isLoading = query.isPending;
const hasError = !!query.error;
const canEdit = user.role === 'admin' || user.role === 'manager';
const shouldShowBanner = !isDismissed && hasNewFeature;

// ❌ YANLIŞ
const loading = true;
const error = false;
const edit = true;
```

### Constants
```tsx
// src/shared/constants/routes.ts
export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  USERS: '/dashboard/users',
  USER_DETAIL: (id: string) => `/dashboard/users/${id}`,
  SETTINGS: '/dashboard/settings',
} as const;

// src/shared/constants/api.ts
export const API_ENDPOINTS = {
  USERS: '/api/users',
  USER_BY_ID: (id: string) => `/api/users/${id}`,
  COMPANIES: '/api/companies',
  AUTH_LOGIN: '/api/auth/login',
} as const;
```

### JSDoc Comments
```tsx
/**
 * Kullanıcı listesini filtreli olarak getirir.
 * 
 * @param filters - Filtreleme parametreleri
 * @param filters.role - Kullanıcı rolü filtresi
 * @param filters.isActive - Aktif/pasif filtresi
 * @returns Paginated kullanıcı listesi
 * 
 * @example
 * const { data } = useUsers({ role: 'admin', isActive: true });
 */
export function useUsers(filters: UserFilters) {
  // ...
}
```

## Checklist (Her PR/Commit Öncesi)

- [ ] `npx tsc --noEmit` hatasız geçiyor mu?
- [ ] Kullanılmayan import/variable var mı?
- [ ] `any` tipi kullanılmış mı? (alternatif bul)
- [ ] Hardcoded string var mı? (i18n'e taşı)
- [ ] 200+ satırlık dosya var mı? (parçala)
- [ ] Guard clauses kullanılmış mı?
- [ ] Type-only import'lar `import type` ile mi?
