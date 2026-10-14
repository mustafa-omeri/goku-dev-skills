# Logo Design Reference

Logo design with 55+ styles, 30 color palettes, 25 industry guides. Brief üretimi ve
stil/palet/sektör araması **çevrimdışıdır** — API anahtarı gerekmez.

> ⛔ Bu pakette **AI görsel üretimi yoktur.** Brief çıkar, sonra kullanıcının elinde
> bulunan görsel üretim aracına ya da manuel tasarıma ver.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/logo/search.py` | Search styles, colors, industries; generate design briefs |
| `scripts/logo/core.py` | BM25 search engine for logo data |

## Commands

### Design Brief (Start Here)

```bash
python .agent/skills/design/scripts/logo/search.py "tech startup modern" --design-brief -p "BrandName"
```

### Search Domains

```bash
# Styles
python .agent/skills/design/scripts/logo/search.py "minimalist clean" --domain style

# Color palettes
python .agent/skills/design/scripts/logo/search.py "tech professional" --domain color

# Industry guidelines
python .agent/skills/design/scripts/logo/search.py "healthcare medical" --domain industry
```

### Logo Üretimi

Brief'teki stil, palet ve sektör yönergelerini harici bir görsel üretim aracına
prompt olarak aktar ya da elle uygula. Çıktı logoları **beyaz zemin** üzerinde
topla. Bu paketin `references/logo-prompt-engineering.md` dosyası, dışarıdan
kullanılacak araç için yazılacak prompt'un nasıl kurulacağını anlatır.

## Available Styles

| Category | Styles |
|----------|--------|
| General | Minimalist, Wordmark, Lettermark, Pictorial Mark, Abstract Mark, Mascot, Emblem, Combination Mark |
| Aesthetic | Vintage/Retro, Art Deco, Luxury, Playful, Corporate, Organic, Neon, Grunge, Watercolor |
| Modern | Gradient, Flat Design, 3D/Isometric, Geometric, Line Art, Duotone, Motion-Ready |
| Clever | Negative Space, Monoline, Split/Fragmented, Responsive/Adaptive |

## Color Psychology

| Color | Psychology | Best For |
|-------|------------|----------|
| Blue | Trust, stability | Finance, tech, healthcare |
| Green | Growth, natural | Eco, wellness, organic |
| Red | Energy, passion | Food, sports, entertainment |
| Gold | Luxury, premium | Fashion, jewelry, hotels |
| Purple | Creative, innovative | Beauty, creative, tech |

## Industry Defaults

| Industry | Style | Colors | Typography |
|----------|-------|--------|------------|
| Tech | Minimalist, Abstract | Blues, purples, gradients | Geometric sans |
| Healthcare | Professional, Line Art | Blues, greens, teals | Clean sans |
| Finance | Corporate, Emblem | Navy, gold | Serif or clean sans |
| Food | Vintage Badge, Mascot | Warm reds, oranges | Friendly, script |
| Fashion | Wordmark, Luxury | Black, gold, white | Elegant serif |

## Workflow

1. Generate design brief → `scripts/logo/search.py --design-brief`
2. Produce logo variations → **harici bir görsel üretim aracıyla** (bu pakette yok)
3. Ask the user whether an HTML preview is wanted
4. If yes, use the `ui-ux-pro-max` skill for the HTML gallery

## Detailed References

- `references/logo-style-guide.md` - Detailed style descriptions
- `references/logo-color-psychology.md` - Color meanings and combinations
- `references/logo-prompt-engineering.md` - Prompt engineering for whatever image tool is used

## Prerequisites

Python 3, harici paket yok.
