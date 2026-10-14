# Icon Design Reference

SVG icon design: 15 styles, 12 categories. Bu dosya **rehberdir** — SVG metin
tabanlıdır ve elle (veya kullanıcının kendi araç zinciriyle) yazılır.

> ⛔ Bu pakette ikon üretim script'i yoktur.

## Kaynak Veriler

| Dosya | İçerik |
|-------|--------|
| `data/icon/styles.csv` | 15 stil için stil/kullanım rehberi |

Hazır ikon seti arıyorsan önce `ui-ux-pro-max --domain icons` sorgusunu çalıştır.

## Üretim

1. **İkon seç** — Önce mevcut bir set kullan: Phosphor (birincil) / Heroicons
   (yedek) / Lucide / Simple Icons. Kaynak: `ui-ux-pro-max --domain icons`.
2. **Özel ikon gerekiyorsa** — SVG'yi elle yaz veya harici bir kod üretim aracına
   istediğin stili tarif et.
3. **Doğrula** — Aşağıdaki SVG kurallarına uy.

### Stil Seçimi

| Style | Stroke | Fill | Best For |
|-------|--------|------|----------|
| outlined | 2px | none | UI interfaces, web apps |
| filled | 0 | solid | Mobile apps, nav bars |
| duotone | 0 | dual | Marketing, landing pages |
| thin | 1-1.5px | none | Luxury brands, editorial |
| bold | 3px | none | Headers, hero sections |
| rounded | 2px | none | Friendly apps, health |
| sharp | 2px | none | Tech, fintech, enterprise |
| flat | 0 | solid | Material design, Google-style |
| gradient | 0 | gradient | Modern brands, SaaS |
| glassmorphism | 1px | semi | Modern UI, overlays |
| pixel | 0 | solid | Gaming, retro |
| hand-drawn | varies | none | Artisan, creative |
| isometric | 1-2px | partial | Tech docs, infographics |
| glyph | 0 | solid | System UI, compact |
| animated-ready | 2px | varies | Interactive UI, onboarding |

### Kategoriler

| Category | Icons |
|----------|-------|
| navigation | arrows, menus, home, chevrons |
| action | edit, delete, save, download, upload |
| communication | email, chat, phone, notification |
| media | play, pause, volume, camera |
| file | document, folder, archive, cloud |
| user | person, group, profile, settings |
| commerce | cart, bag, wallet, credit card |
| data | chart, graph, analytics, dashboard |
| development | code, terminal, bug, git, API |
| social | heart, star, bookmark, trophy |
| weather | sun, moon, cloud, rain |
| map | pin, location, compass, globe |

### Çıktı Ayarları

| Ayar | Değer |
|------|-------|
| `viewBox` | `0 0 24 24` (standart) veya `0 0 16 16` (kompakt) |
| `color` | `currentColor` (CSS mirası için) |
| `width`/`height` | 24 px varsayılan, sabit ölçek |
| Toplu çıktı dizini | `./icons` |

## SVG Best Practices

- **ViewBox**: Use `0 0 24 24` (standard) or `0 0 16 16` (compact)
- **Colors**: Use `currentColor` for CSS inheritance, avoid hardcoded colors
- **Accessibility**: Always include `<title>` element
- **Optimization**: Minimal path nodes, no embedded fonts or raster images
- **Sizing**: Design at 24px, test at 16px and 48px for clarity
- **Stroke**: Use `stroke-linecap="round"` and `stroke-linejoin="round"` for outlined styles

## Prerequisites

Yok — bu rehber saf metindir, script çalıştırmaz.
