---
name: musgoku-api-data-layer
description: >
  API entegrasyonu, data fetching, caching ve state yönetimi için best practices.
  TanStack Query v5 + Axios + TypeScript ile uyumlu.
---

# 🔌 MuSGoKu — API & Data Layer Best Practices

## TanStack Query v5 Kullanımı

### Query Key Conventions
```tsx
// ✅ Feature-based hierarchical key yapısı
const queryKeys = {
  users: {
    all: ['users'] as const,
    lists: () => [...queryKeys.users.all, 'list'] as const,
    list: (filters: UserFilters) => [...queryKeys.users.lists(), filters] as const,
    details: () => [...queryKeys.users.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.users.details(), id] as const,
  },
  companies: {
    all: ['companies'] as const,
    list: (filters?: CompanyFilters) => [...queryKeys.companies.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.companies.all, 'detail', id] as const,
  },
} as const;
```

### useQuery Pattern
```tsx
import { useQuery } from '@tanstack/react-query';
import { userService } from '../services/userService';
import type { UserFilters } from '../types';

export function useUsers(filters: UserFilters) {
  return useQuery({
    queryKey: queryKeys.users.list(filters),
    queryFn: () => userService.getUsers(filters),
    staleTime: 5 * 60 * 1000,        // 5 dakika stale olmaz
    gcTime: 10 * 60 * 1000,          // 10 dakika garbage collection
    refetchOnWindowFocus: false,      // Tab geçişlerinde refetch yapma
    retry: 2,                          // Max 2 retry
  });
}

// List view polling zorunluluğu (15sn aralıklı)
export function useUsersWithPolling(filters: UserFilters) {
  return useQuery({
    queryKey: queryKeys.users.list(filters),
    queryFn: () => userService.getUsers(filters),
    refetchInterval: POLL_INTERVAL,       // yapılandırmadan okunur
    refetchIntervalInBackground: false,   // Tab arka plandayken durdur
    refetchOnWindowFocus: true,          // Odağa dönünce tazele
  });
}
```

### useMutation Pattern
```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services/userService';
import type { CreateUserDto } from '../types';

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserDto) => userService.createUser(data),
    onSuccess: () => {
      // İlgili query'leri invalidate et
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
    onError: (error) => {
      // Error handling — toast notification vb.
      console.error('User creation failed:', error);
    },
  });
}
```

### Optimistic Updates (v5 Pattern)
```tsx
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateUserDto) => userService.updateUser(data),
    onMutate: async (newData) => {
      // Devam eden query'leri iptal et
      await queryClient.cancelQueries({ queryKey: queryKeys.users.detail(newData.id) });
      
      // Önceki veriyi kaydet
      const previousUser = queryClient.getQueryData(queryKeys.users.detail(newData.id));
      
      // Optimistic update
      queryClient.setQueryData(queryKeys.users.detail(newData.id), (old: User) => ({
        ...old,
        ...newData,
      }));
      
      return { previousUser };
    },
    onError: (_err, _newData, context) => {
      // Hata durumunda geri al
      if (context?.previousUser) {
        queryClient.setQueryData(
          queryKeys.users.detail(_newData.id),
          context.previousUser
        );
      }
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.detail(variables.id) });
    },
  });
}
```

## Axios Service Layer

### Base HTTP Client Setup
```tsx
// src/services/http.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const httpClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — JWT token ekleme
httpClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — Error handling
httpClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired — logout ve login sayfasına yönlendir
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    // User-friendly error mesajı fırlat (TanStack Query tarafından yakalanır)
    const message = error.response?.data?.message || 'Bir hata oluştu';
    return Promise.reject(new Error(message));
  }
);
```

### Feature Service Pattern
```tsx
// src/features/user-management/services/userService.ts
import { httpClient } from '@/services/http';
import type { User, CreateUserDto, UpdateUserDto, PaginatedResponse } from '../types';

export const userService = {
  getUsers: async (filters?: UserFilters): Promise<PaginatedResponse<User>> => {
    const { data } = await httpClient.get('/api/users', { params: filters });
    return data;
  },

  getUserById: async (id: string): Promise<User> => {
    const { data } = await httpClient.get(`/api/users/${id}`);
    return data;
  },

  createUser: async (dto: CreateUserDto): Promise<User> => {
    const { data } = await httpClient.post('/api/users', dto);
    return data;
  },

  updateUser: async (dto: UpdateUserDto): Promise<User> => {
    const { data } = await httpClient.put(`/api/users/${dto.id}`, dto);
    return data;
  },

  deleteUser: async (id: string): Promise<void> => {
    await httpClient.delete(`/api/users/${id}`);
  },
};
```

## Kurallar

1. **API çağrıları sadece `services/` katmanında** yapılır, bileşen içinde doğrudan Axios çağrısı yapılmaz.
2. **TanStack Query her zaman kullanılır** — Manuel `useEffect` + `useState` ile data fetching yasaktır.
3. **Query key'ler hiyerarşik ve tutarlı** olmalıdır.
4. **Error handling user-friendly** olmalı — Servisler anlamlı hata mesajları fırlatmalı.
5. **Liste verisi her zaman otomatik tazelenir** — aşağıdaki hiyerarşiye göre.
6. **Type safety** — Tüm API yanıtları TypeScript ile tiplendirilmeli.
7. **`import.meta.env`** kullanılır (`process.env` değil).

---

## Liste verisinin tazelenmesi — zorunlu

Bir liste ekranında veri **elle yenileme düğmesine** bırakılmaz. Yöntem
şu hiyerarşiyle seçilir:

| Durum | Yöntem |
|---|---|
| Sunucu gerçek zamanlı olay yayınlıyorsa | **Olay aboneliği** — gelen olayla cache doğrudan güncellenir |
| Gerçek zamanlı kanal yoksa | **Polling** — düzenli aralıkla yeniden çekme |
| Kritik doğrulama gerekiyorsa | Elle yenileme **ek olarak** bulunabilir; tek yöntem olamaz |

### Olay geliyorsa polling yazılmaz

Sunucu tarafında gerçek zamanlı olay yayını varsa (bkz.
[`references/websocket.md`](../references/websocket.md)) liste polling'e
bağlanmaz. Olay, ilgili kaydı doğrudan sorgu cache'ine yazar.

**Gerekçe:** polling + olay birlikte çalışırsa aynı kayıt hem olayla hem
zamanlayıcıyla gelir; liste titrer, sayaçlar kayar ve hangi kaynağın
güncel olduğu anlaşılamaz.

### Polling nasıl ayarlanır

| Kural | Açıklama |
|---|---|
| Aralık koda gömülmez | Yapılandırmadan okunur; varsayılan değer projeye aittir |
| Sekme görünür değilken duraklatılır | Arka plandaki sekmede gereksiz istek atılmaz |
| Pencerenin dışındayken duraklatılır | `refetchIntervalInBackground` kapatılır |
| Odaklanınca tazelenir | Kullanıcı geri döndüğünde bayat veriyle karşılaşmaz |
| Arama değişince sayaç sıfırlanır | Her aramada yeni sayaç kurulur |

Aralık projeye özeldir ve `AGENTS.md` → *Proje Bazlı Ek Kurallar* altında
yazılır. Burada sabit değer **yoktur**.

---

## Anti-Patterns

- ❌ Bileşen içinde doğrudan `axios.get()` çağrısı
- ❌ `useEffect` ile data fetching
- ❌ `process.env` kullanımı (Vite'ta `import.meta.env` kullanılır)
- ❌ Global state'te API yanıtı saklama (sorgu cache'i yeterli)
- ❌ API adreslerinin kod içinde sabit yazılması
- ❌ Gerçek zamanlı olay varken polling yazılması
- ❌ Polling aralığının bileşene gömülmesi
- ❌ Liste verisinin yalnız elle yenileme düğmesine bırakılması
