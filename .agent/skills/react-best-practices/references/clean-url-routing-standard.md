# React Router v6 Clean URL (Temiz URL) ve Semantic Routing Mimarisi Standart Rehberi

> Bu doküman web projelerinde (özellikle React & Vite SPA portalları) karmaşık query string parametreleri (`?id=123&category=electronics`) yerine **Clean URL (Temiz/Semantik URL)** mimarisinin nasıl kurulacağını tarif eden bağlayıcı mühendislik rehberidir.

---

## 1. Mimari Genel Bakış ve İki Temel Senaryo

| Boyut | 1. Senaryo: SEO Dostu "Slug" / Dinamik Rota | 2. Senaryo: URL'den Gizli Parametre (State Yöntemi) |
|---|---|---|
| **Amaç** | Arama motorları, paylaşım, yer imleri ve okunabilirlik | Güvenlik, hassas token/ID gizleme, temiz adres çubuğu |
| **Örnek URL** | `/portal/haberler/:newsSlug` (Örn: `/portal/haberler/yapay-zekada-yeni-donem`) | Sabit `/portal/profil-ayarlari` (Query string yok) |
| **Veri Taşıma** | URL Path Segmenti (`useParams`) | `useNavigate({ state })` (Tarayıcı bellek durumu) |
| **Veri Çözümleme** | `const { newsSlug } = useParams<NewsDetailParams>()` | `const { state } = useLocation()` |
| **F5 / Yenileme** | URL segmentinden API doğrudan yeniden çağrılır | Tarayıcı `history.state` korur; doğrudan URL girişinde Graceful Fallback devreye girer |

---

## 2. Senaryo 1: SEO-Dostu Slug Rota Mimarisi

### 2.1 Türkçe Karakter Destekli Deterministik `slugify` Motoru (`src/utils/slugify.ts`)

```typescript
export function slugify(text: string): string {
  const trMap: Record<string, string> = {
    ç: 'c', Ç: 'c',
    ğ: 'g', Ğ: 'g',
    ı: 'i', I: 'i', İ: 'i',
    ö: 'o', Ö: 'o',
    ş: 's', Ş: 's',
    ü: 'u', Ü: 'u',
  };

  return text
    .replace(/[çÇğĞıIİöÖşŞüÜ]/g, (match) => trMap[match] || match)
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9 -]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');
}
```

### 2.2 Liste Ekranı ve Semantik Geçiş (`src/pages/news/NewsList.tsx`)

```tsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { NewsItem } from '../../types/routing';
import { fetchNewsList } from '../../services/mockNewsApi';

export const NewsList: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNewsList().then((data) => {
      setNews(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="animate-pulse p-6">Yükleniyor...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Portal Haberleri</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {news.map((item) => (
          <article key={item.id} className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
            <h2 className="text-lg font-semibold">{item.title}</h2>
            <p className="text-sm text-zinc-400 mt-2">{item.summary}</p>
            {/* Clean URL Geçişi */}
            <Link
              to={`/portal/haberler/${item.slug}`}
              className="mt-4 inline-block text-emerald-400 hover:underline text-sm font-medium"
            >
              Haberi Oku &rarr;
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
};
```

### 2.3 Detay Ekranı ve `useParams` ile Çözümleme (`src/pages/news/NewsDetail.tsx`)

```tsx
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { NewsItem, NewsDetailRouteParams } from '../../types/routing';
import { fetchNewsBySlug } from '../../services/mockNewsApi';

export const NewsDetail: React.FC = () => {
  const { newsSlug } = useParams<NewsDetailRouteParams>();
  const [news, setNews] = useState<NewsItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!newsSlug) return;
    setLoading(true);
    fetchNewsBySlug(newsSlug).then((data) => {
      setNews(data);
      setLoading(false);
    });
  }, [newsSlug]);

  if (loading) return <div className="p-6">Yükleniyor...</div>;
  if (!news) {
    return (
      <div className="p-8 text-center bg-zinc-900 border border-zinc-800 rounded-xl">
        <h2>Haber Bulunamadı (404)</h2>
        <Link to="/portal/haberler" className="text-emerald-400">Haber Listesine Dön</Link>
      </div>
    );
  }

  return (
    <article className="max-w-3xl mx-auto p-6 space-y-4">
      <h1 className="text-3xl font-bold">{news.title}</h1>
      <p className="text-zinc-300 leading-relaxed">{news.content}</p>
    </article>
  );
};
```

---

## 3. Senaryo 2: Parametreleri URL'den Tamamen Gizleme (State Yöntemi)

### 3.1 Yönlendirici Bileşen (`src/pages/profile/UserDashboard.tsx`)

```tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ProfileSettingsNavigationState } from '../../types/routing';

export const UserDashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleOpenSecuritySettings = () => {
    const payload: ProfileSettingsNavigationState = {
      accountId: 'acc_8849102',
      sensitiveSessionToken: 'tok_live_sec_99482',
      targetTab: 'security',
      timestamp: Date.now(),
    };

    // useNavigate ile state objesi aktarılır; URL sabit kalır
    navigate('/portal/profil-ayarlari', {
      state: payload,
    });
  };

  return (
    <button onClick={handleOpenSecuritySettings} className="btn-primary">
      Güvenlik Ayarlarını Aç (Gizli State)
    </button>
  );
};
```

### 3.2 Güvenli Okuma ve F5 / Doğrudan Erişim Fallback Ekranı (`src/pages/profile/ProfileSettings.tsx`)

```tsx
import React, { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { ProfileSettingsNavigationState } from '../../types/routing';

export const ProfileSettings: React.FC = () => {
  const location = useLocation();

  // useLocation üzerinden state güvenle okunur
  const navState = location.state as ProfileSettingsNavigationState | null;

  // F5 Yenileme / Doğrudan Sekme Girişi Koruması:
  // URL doğrudan tarayıcıya yapıştırıldığında navState null döner.
  // Uygulamanın çökmesini engellemek için zarif bir Fallback ekranı sunulur:
  if (!navState || !navState.accountId) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 text-center bg-zinc-900 border border-amber-500/30 rounded-2xl">
        <h2 className="text-xl font-bold text-zinc-100">Oturum Verisi Bulunamadı (Fallback)</h2>
        <p className="text-sm text-zinc-400 mt-2">
          Bu sayfaya doğrudan erişildi. Güvenliğiniz için hesap kimliği URL'de taşınmamaktadır.
        </p>
        <Link to="/portal/dashboard" className="mt-4 inline-block btn-primary">
          Panele Dön ve Hesap Seç
        </Link>
      </div>
    );
  }

  // Veri güvenle mevcut: Optional Chaining ile render
  return (
    <div className="p-6">
      <h1>Profil Ayarları (Sabit URL: /portal/profil-ayarlari)</h1>
      <p>Hesap ID: {navState?.accountId}</p>
      <p>Hedef Sekme: {navState?.targetTab}</p>
    </div>
  );
};
```

---

## 4. Modern createBrowserRouter & RouterProvider Mimarisi

```tsx
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { PortalLayout } from '../layouts/PortalLayout';
import { NewsList } from '../pages/news/NewsList';
import { NewsDetail } from '../pages/news/NewsDetail';
import { UserDashboard } from '../pages/profile/UserDashboard';
import { ProfileSettings } from '../pages/profile/ProfileSettings';

export const router = createBrowserRouter([
  {
    path: '/portal',
    element: <PortalLayout />,
    children: [
      { path: 'dashboard', element: <UserDashboard /> },
      // Senaryo 1: SEO Slug
      { path: 'haberler', element: <NewsList /> },
      { path: 'haberler/:newsSlug', element: <NewsDetail /> },
      // Senaryo 2: Gizli State
      { path: 'profil-ayarlari', element: <ProfileSettings /> },
    ],
  },
]);

export const AppRouter = () => <RouterProvider router={router} />;
```
