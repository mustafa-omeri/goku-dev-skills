# CIP Design Reference

Corporate Identity Program design with 50+ deliverables, 20 styles, 20 industries.
Brief üretimi ve arama **çevrimdışıdır** — API anahtarı gerekmez.

> ⛔ Bu pakette **mockup görsel üretimi yoktur.** Brief çıkar, teslimatları elle ya da
> harici bir görsel aracıyla hazırla, sonra HTML sunuma dönüştür.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/cip/search.py` | Search deliverables, styles, industries; generate CIP briefs |
| `scripts/cip/render-html.py` | Render HTML presentation from CIP mockups |
| `scripts/cip/core.py` | BM25 search engine for CIP data |

## Commands

### CIP Brief (Start Here)

```bash
python .agent/skills/design/scripts/cip/search.py "tech startup" --cip-brief -b "BrandName"
```

### Search Domains

```bash
# Deliverables
python .agent/skills/design/scripts/cip/search.py "business card letterhead" --domain deliverable

# Design styles
python .agent/skills/design/scripts/cip/search.py "luxury premium elegant" --domain style

# Industry guidelines
python .agent/skills/design/scripts/cip/search.py "hospitality hotel" --domain industry

# Mockup contexts
python .agent/skills/design/scripts/cip/search.py "office reception" --domain mockup
```

### Mockup Hazırlama

Brief'teki teslimat listesi, stilleri ve sektör bağlamını kullanarak mockup'ları
elle (tasarım aracında) hazırla ya da harici bir görsel üretim aracına prompt olarak
aktar. Logoyu referans görsel olarak ver, çıktıları tek klasörde topla
(`assets/brand/cip/`).

### Render HTML Presentation

```bash
python3 scripts/cip/render-html.py --brand "TopGroup" --industry "consulting" --images /path/to/cip-output
python .agent/skills/design/scripts/cip/render-html.py --brand "TopGroup" --industry "consulting" --images ./topgroup-cip --output presentation.html
```

## Deliverable Categories

| Category | Items |
|----------|-------|
| Core Identity | Logo, Logo Variations |
| Stationery | Business Card, Letterhead, Envelope, Folder, Notebook, Pen |
| Security/Access | ID Badge, Lanyard, Access Card |
| Office Environment | Reception Signage, Wayfinding, Meeting Room Signs, Wall Graphics |
| Apparel | Polo Shirt, T-Shirt, Cap, Jacket, Apron |
| Promotional | Tote Bag, Gift Box, USB Drive, Water Bottle, Mug, Umbrella |
| Vehicle | Car Sedan, Van, Truck |
| Digital | Social Media, Email Signature, PowerPoint, Document Templates |
| Product | Packaging Box, Labels, Tags, Retail Display |
| Events | Trade Show Booth, Banner Stand, Table Cover, Backdrop |

## Design Styles

| Style | Colors | Best For |
|-------|--------|----------|
| Corporate Minimal | Navy, White, Blue | Finance, Legal, Consulting |
| Modern Tech | Purple, Cyan, Green | Tech, Startups, SaaS |
| Luxury Premium | Black, Gold, White | Fashion, Jewelry, Hotels |
| Warm Organic | Brown, Green, Cream | Food, Organic, Artisan |
| Bold Dynamic | Red, Orange, Black | Sports, Entertainment |

## HTML Presentation Features

- Hero section with brand name, industry, style, mood
- Deliverable cards with mockup images
- Descriptions: concept, purpose, specifications
- Responsive desktop/mobile, dark theme
- Images embedded as base64 (single-file portable)

## Workflow

1. Generate CIP brief → `scripts/cip/search.py --cip-brief`
2. Prepare mockups (manuel veya harici görsel aracı) → `assets/brand/cip/`
3. Render HTML presentation → `scripts/cip/render-html.py --brand --industry --images`

**Tip:** Logo yoksa önce Logo Design bölümünde brief çıkar, logo'yu o brief'ten üret.

## Detailed References

- `references/cip-deliverable-guide.md` - Deliverable specifications
- `references/cip-style-guide.md` - Design style descriptions
- `references/cip-prompt-engineering.md` - Prompt engineering for external image tools

## Prerequisites

Python 3, harici paket yok (Pillow gerekmez).
