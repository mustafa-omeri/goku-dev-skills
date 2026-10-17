---
name: mock-asset-provider
description: >
  Web ve mobil arayüz kartları, profiller, etkinlikler ve ürünler için gerçekçi mock görsel ve veri varlıkları sağlar; GitHub deposu, API anahtarı veya sıfır-ayar CDN fallback ile yerel indirme yönetir. Tetikleyiciler: "mock görsel", "gerçekçi resim", "kart görseli", "profil resmi", "etkinlik afişi", "mock images", "placeholder images", "realistic avatars". Tetiklenmez: banner tasarımı `banner-design`'e, afiş/poster sanatı `canvas-design`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
argument-hint: "[category] [gender] [seed] [count]"
license: MIT
metadata:
  author: antikit
  version: "1.0.0"
---

# Mock Asset Provider — Realistic Visual Mock Data System

Web ve mobil uygulama arayüzlerinde (kartlar, kullanıcı listeleri, eşleşme/profil kartları, etkinlikler, ürün ızgaraları) boş gri kutu (`placeholder`) veya kırık harici linkler yerine; gerçekçi, deterministik ve yüksek kaliteli görsel varlıkları temin eden ve yöneten sistemdir.

## 🎯 Ne Zaman Devreye Girer? (Tetikleyiciler)

- Kullanıcı arayüzünde (UI kartı, profil, ürün listesi, etkinlik akışı) gerçekçi görsel veya mock resim gerektiğinde.
- Boş gri placeholder yerine gerçek fotoğraflarla test ve demo yapılmak istendiğinde.
- Projeye özel bir GitHub asset deposundan veya API'den görsel varlık paketi indirilmek istendiğinde.
- Kadın/erkek profil portreleri, SVG avatarlar, festival/konser/etkinlik afişleri veya e-ticaret görselleri gerektiğinde.

## ⛔ Kapsam Sınırı (Tetiklenmez)

- Sabit piksel ölçülü sosyal medya ve reklam banner'ları tasarlamak `banner-design` skill'ine aittir.
- Ölçüsüz görsel sanat, manifesto, baskı posteri üretmek `canvas-design` skill'ine aittir.
- Arayüzün bileşen kodu, hiyerarşisi ve CSS yerleşimi `frontend-design` ve `ui-styling` skill'lerine aittir.
- Bu skill görsel yerleşimi tasarlamaz; tasarımın içine **canlı, gerçekçi görsel URL'leri ve yerel dosyaları** enjekte eder.

---

## 🛠️ Mimari ve 3 Kademeli Çözümleme Hattı (Fallback Pipeline)

Ajan görsel ihtiyacında aşağıdaki öncelik sırasını izler:

```
[UI Kartı / Görsel İhtiyacı]
            │
            ▼
┌───────────────────────────────────────────────┐
│ 1. Proje Config'i (.agent/config/assets.json) │ ──► Varsa GitHub deposu veya API
└───────────────────────────────────────────────┘
            │ (Yoksa veya tanımlanmadıysa)
            ▼
┌───────────────────────────────────────────────┐
│ 2. Sıfır-Ayar Deterministik Public CDN        │ ──► RandomUser, Picsum, DiceBear
└───────────────────────────────────────────────┘
            │ (İnternetsiz / Kalıcı Ön Bellek)
            ▼
┌───────────────────────────────────────────────┐
│ 3. Yerel İndirme (Local Caching)              │ ──► public/mock-assets/ altına kaydet
└───────────────────────────────────────────────┘
```

---

## 📋 Konfigürasyon Dosyası (`.agent/config/assets.json`)

Projelerde görsel kaynaklarını özelleştirmek için kullanılır:

```json
{
  "enabled": true,
  "storage_dir": "public/mock-assets",
  "download_locally": true,
  "sources": {
    "github": {
      "enabled": false,
      "repo_url": "https://github.com/ornek/etkinlik-gorselleri-paketi",
      "branch": "main",
      "sub_path": "images"
    },
    "api": {
      "unsplash_access_key": "",
      "pexels_api_key": ""
    },
    "default_fallbacks": {
      "portraits": "randomuser",
      "events": "picsum",
      "products": "dummyjson",
      "general": "picsum"
    }
  }
}
```

---

## 🚀 Komut Satırı ve Script Kullanımı

Tedarik aracı `.agent/skills/mock-asset-provider/scripts/fetch_assets.py` üzerinden çalıştırılır:

### 1. Kadın / Erkek Profil Portreleri Üretme
```bash
# 3 adet kadın portresi URL'i üret (JSON formatında)
python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --category portraits --gender women --count 3 --json

# 5 adet erkek portresi URL'i üret
python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --category portraits --gender men --count 5
```

### 2. Etkinlik / Konser / Festival Kart Görselleri
```bash
# Belirli bir etkinlik için deterministik görsel (her çalıştırmada aynı sabit görsel)
python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --category events --seed "rock-festival-2025" --width 800 --height 600

# Görselleri yerel proje klasörüne indirme
python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --category events --seed "new-year-party" --download --output public/mock-assets/events
```

### 3. Vektörel / Modern Avatarlar (DiceBear)
```bash
python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --category avatars --style avataaars --count 4 --seed "user-team"
```

### 4. Proje Config'ini Yürütme (GitHub Varlık Deposunu İndirme)
```bash
python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --from-config
```

---

## 🎨 UI Bileşenlerinde Kullanım Örnekleri (React / HTML)

### Örnek 1: Eşleşme veya Kullanıcı Profil Kartı
```tsx
const mockUsers = [
  { id: 1, name: "Elif Kaya", age: 26, avatar: "https://randomuser.me/api/portraits/women/44.jpg" },
  { id: 2, name: "Can Demir", age: 29, avatar: "https://randomuser.me/api/portraits/men/32.jpg" }
];
```

### Örnek 2: Geri Sayım / Etkinlik Kartı
```tsx
const mockEvents = [
  {
    id: "ev-1",
    title: "Yaz Caz Festivali",
    image: "https://picsum.photos/seed/jazz-fest-2025/800/600",
    date: "2025-07-15"
  },
  {
    id: "ev-2",
    title: "Teknoloji Zirvesi",
    image: "https://picsum.photos/seed/tech-summit-2025/800/600",
    date: "2025-09-20"
  }
];
```

---

## 🛡️ Kalite ve Güvenilirlik İlkeleri

1. **Kırık Link Yasağı:** Kapanmış veya yavaş servislere (`via.placeholder.com`, `lorempixel.com`) bağımlı kalınmaz.
2. **CORS ve Hız:** Kullanılan tüm public CDN'ler (RandomUser, Picsum, DiceBear) CORS-free ve global CDN önbelleklidir.
3. **Determinizm (Seed İlkesi):** Kartlarda her render'da rastgele değişen resim yerine, `seed` parametresiyle sabitlenen görseller tercih edilir.
