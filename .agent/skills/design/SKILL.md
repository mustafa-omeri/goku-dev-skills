---
name: design
description: Tasarım yönlendiricisi ve çevrimdışı brief üreticisi. İstek birden fazla tasarım alanını kapsıyorsa doğru sahibi bulur; logo (55 stil, 30 palet, 25 sektör) ve kurumsal kimlik (50+ teslimat) için yazılı brief, ayrıca sosyal medya görseli akışı. Tetikleyiciler: "logo brief", "logo fikri", "kartvizit", "kurumsal kimlik", "CIP", "sosyal medya görseli", "logo brief", "corporate identity". Tetiklenmez: hazır banner ölçüsü `banner-design`'e aittir. Bu set görsel üretmez. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
argument-hint: "[design-type] [context]"
license: MIT
metadata:
  author: claudekit
  version: "2.1.0-set"
---

# Design

Design **yönlendiricisi** ve **brief üreticisi**. Bu skill ürün üretmez; işi doğru
sahibine yollar ve logo/CIP işleri için çevrimdışı yazılı brief üretir.

## Ne zaman devrede

- İstek **birden fazla tasarım alanını** kapsıyorsa (marka + token + UI + sunum)
- Logo veya CIP teslimatı için **yazılı brief** gerekiyorsa
- Hangi skill'in sahibi olduğu belli değilse

Tek bir konu varsa doğrudan o sahip skill'i aç — yönlendirme gereksiz.

## Yönlendirme tablosu (tek sahip)

| İstek | Sahip skill | Not |
|-------|-------------|-----|
| Marka kimliği, ton, guideline, varlık | `brand` | İçerik standardı |
| Doküman yazma süreci (PRD, spec, karar) | `doc-coauthoring` | Yazım iş akışı |
| Renk/font paleti (hazır tema seçimi) | `theme-factory` | Palet ve font sağlayıcısı |
| Tasarım yönü, stil, UX, stack önerisi | `ui-ux-pro-max` | Aranabilir referans veritabanı |
| Token üretimi (primitive → semantic → component) | `design-system` | Token mimarisi |
| Tailwind / shadcn / CSS değişkeni uygulaması | `ui-styling` | Kod katmanı |
| Estetik yönelim, AI-slop kaçınma, UI kodu | `frontend-design` | Uygulama disiplini |
| Poster, manifesto, ölçüsüz görsel sanat | `canvas-design` | Sanat nesnesi |
| Sunum / pitch deck | `slides` | Strateji + metin |
| Sunum/slayt **üretimi** (token + script) | `design-system` | Render sahibi |
| Banner, kapak görseli, reklam görseli | `banner-design` | Sabit px ölçüler |
| IDE benzeri uygulama arayüzü | `web-ide-ux-architect` | Kapsam dışı bildirimi yapar |

**Bu skill'in sahibi olduğu tek alan:** logo/CIP brief'i ve sosyal medya görseli akışı.

## Logo Brief (çevrimdışı)

55+ stil, 30 renk paleti, 25 sektör rehberi — hepsi yerel CSV'den, API gerekmez.

```bash
python .agent/skills/design/scripts/logo/search.py "tech startup modern" --design-brief -p "BrandName"
python .agent/skills/design/scripts/logo/search.py "minimalist clean" --domain style
python .agent/skills/design/scripts/logo/search.py "tech professional" --domain color
python .agent/skills/design/scripts/logo/search.py "healthcare medical" --domain industry
```

`references/logo-design.md` · `logo-style-guide.md` · `logo-color-psychology.md` ·
`logo-prompt-engineering.md`

> ⛔ **Bu pakette AI görsel üretimi yoktur.** Brief'i çıkar, sonra kullanıcının elinde
> bulunan görsel üretim aracına (ya da manuel tasarıma) ver. Ücretli bir görsel API'si
> çağrılmaz; anahtar istenmez.

## CIP Brief (kurumsal kimlik programı — çevrimdışı)

50+ teslimat, 20 stil, 20 sektör.

```bash
python .agent/skills/design/scripts/cip/search.py "tech startup" --cip-brief -b "BrandName"
python .agent/skills/design/scripts/cip/search.py "business card letterhead" --domain deliverable
python .agent/skills/design/scripts/cip/search.py "luxury premium elegant" --domain style
python .agent/skills/design/scripts/cip/search.py "hospitality hotel" --domain industry
python .agent/skills/design/scripts/cip/search.py "office reception" --domain mockup
```

Teslimat görselleri elle hazırlandıktan sonra HTML sunuma çevrilebilir:

```bash
python .agent/skills/design/scripts/cip/render-html.py --brand "TopGroup" --industry "consulting" --images <görsel-klasörü>
```

`references/cip-design.md` · `cip-deliverable-guide.md` · `cip-style-guide.md` ·
`cip-prompt-engineering.md`

## İkon (manuel yönlendirme)

15 stil, 12 kategori — `references/icon-design.md` ve `data/icon/styles.csv`.
Baskı vektörel SVG üretimi **elle** yapılır; SVG metin tabanlıdır, üretim script'i yoktur.
İkon seçimi gerekiyorsa önce `ui-ux-pro-max --domain icons` sorgusunu çalıştır.

## Sosyal Medya Görseli

Çok platformlu görsel tasarım: HTML/CSS → ekran görüntüsü. Sahip skill'ler:
`brand` → `design-system` → `ui-ux-pro-max`; dışa aktarım tarayıcı üzerinden yapılır.

`references/social-photos-design.md` boyutlar, şablonlar ve pratikler için tek kaynaktır.

### Akış

1. **Analiz** — Konu, platformlar, stil, marka bağlamı
2. **Konsept** — 3-5 fikir; kullanıcıya sor, seçim al
3. **Tasarım** — `brand` → `design-system` → `ui-ux-pro-max`; her fikir × boyut için HTML
4. **Dışa aktarım** — Tarayıcı/headless ile tam pikselde PNG (destekleniyorsa 2x)
5. **Doğrula** — PNG'leri aç, yerleşim sorunlarını düzelt, yeniden dışa aktar
6. **Raporla** — Tasarım kararlarıyla birlikte proje rapor dizinine yaz

### Ana boyutlar

| Platform | Boyut (px) | Platform | Boyut (px) |
|----------|-----------|----------|-----------|
| IG Post | 1080×1080 | FB Post | 1200×630 |
| IG Story | 1080×1920 | X Post | 1200×675 |
| IG Carousel | 1080×1350 | LinkedIn | 1200×627 |
| YT Thumb | 1280×720 | Pinterest | 1000×1500 |

## Prerequisites

Python 3, harici paket yok (yalnız standart kütüphane).

**Windows:** `python` kullan — `python3` yok.
**macOS/Linux:** `python3` kullan.

```bash
python --version || python3 --version
```

## Bileşen akışları

### Marka paketi

1. **Logo** → `scripts/logo/search.py --design-brief` → brief → görsel üretim aracı
2. **Marka** → `brand` skill → renk, font, ton, guideline
3. **Token** → `design-system` skill → semantik token katmanları
4. **Sunum** → `slides` skill → deck + `design-system` render

### Yeni tasarım sistemi

1. **Marka** (`brand`) → renk, tipografi, ton
2. **Token** (`design-system`) → primitive → semantic → component
3. **Uygulama** (`ui-styling`) → Tailwind / shadcn yapılandırma
4. **Yön** (`ui-ux-pro-max`) → stil, palet, UX doğrulaması

## Script yolu

Script yolları bu SKILL.md'nin bulunduğu dizine görelidir, proje dizinine göre
değildir: `.agent/skills/design/scripts/<dosya>`. Çalışma dizini proje kökü olmalıdır —
script'ler `docs/brand-guidelines.md`, `assets/design-tokens.json` gibi proje dosyalarını
çalışma dizinine göre okur/yazar. Sibling skill'e erişirken `../<skill>/scripts/<dosya>`
kullan.

## Scriptler

| Script | İşlev |
|--------|-------|
| `scripts/logo/search.py` | Logo stil/palet/sektör araması ve brief üretimi |
| `scripts/logo/core.py` | Logo verisi için BM25 arama motoru |
| `scripts/cip/search.py` | CIP teslimat/stil/sektör/mockup araması ve brief |
| `scripts/cip/core.py` | CIP verisi için BM25 arama motoru |
| `scripts/cip/render-html.py` | CIP görsellerinden HTML sunum üretimi |

## Referanslar

| Konu | Dosya |
|------|-------|
| Yönlendirme | `references/design-routing.md` |
| Logo rehberi | `references/logo-design.md` |
| Logo stilleri | `references/logo-style-guide.md` |
| Logo renkleri | `references/logo-color-psychology.md` |
| Logo promptları | `references/logo-prompt-engineering.md` |
| CIP rehberi | `references/cip-design.md` |
| CIP teslimatları | `references/cip-deliverable-guide.md` |
| CIP stilleri | `references/cip-style-guide.md` |
| CIP promptları | `references/cip-prompt-engineering.md` |
| Sosyal görsel rehberi | `references/social-photos-design.md` |
| İkon tasarımı | `references/icon-design.md` |

## Entegrasyon

Bu setteki diğer skill'ler: `brand`, `design-system`, `ui-styling`, `ui-ux-pro-max`,
`canvas-design`, `frontend-design`, `theme-factory`, `slides`, `banner-design`.
