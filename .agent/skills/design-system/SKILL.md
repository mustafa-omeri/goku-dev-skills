---
name: design-system
description: Design token üreticisi (primitive → semantic → component, CSS değişkenleri, spacing/tipografi ölçeği, bileşen şekilleri) ve sunum/slayt üretim sahibi (`generate-slide.py` ile HTML render + token denetimi). Tetikleyiciler: "design token", "token üret", "css değişkeni üret", "sunumu html'e dönüştür", "slayt üret", "design tokens", "token architecture", "render deck". Tetiklenmez: hazır palet seçimi `theme-factory`, Tailwind/shadcn kurulumu `ui-styling`, sunum içeriği `slides` aittir. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
argument-hint: "[component or token]"
license: MIT
metadata:
  author: claudekit
  version: "1.0.0"
---

# Design System

Token architecture, component specifications, systematic design, slide generation.

## When to Use

- Design token creation
- Component state definitions
- CSS variable systems
- Spacing/typography scales
- Design-to-code handoff
- Tailwind theme configuration
- **Slide/presentation generation**

## Token Architecture

Load: `references/token-architecture.md`

### Three-Layer Structure

```
Primitive (raw values)
       ↓
Semantic (purpose aliases)
       ↓
Component (component-specific)
```

**Example:**
```css
/* Primitive */
--color-blue-600: #2563EB;

/* Semantic */
--color-primary: var(--color-blue-600);

/* Component */
--button-bg: var(--color-primary);
```

## Kapsam Sınırı

| Konu | Sahip |
|------|-------|
| Token üretimi (primitive → semantic → component) | **bu skill** |
| Marka paletinden token türetme | `brand` (kaynak) → bu skill (türetme) |
| Token'ın Tailwind/shadcn tarafına bağlanması | `ui-styling` |
| Hazır palet/tema seçimi | `theme-factory` |
| Stil/palet/UX önerisi (aranabilir veri) | `ui-ux-pro-max` |
| Sunum **stratejisi, metni, düzeni** | `slides` |
| Sunum/slayt **üretimi** (HTML render + doğrulama) | **bu skill** |

Sunum işi ikiye bölünür: `slides` ne söyleneceğine karar verir, bu skill onun
HTML'e dönüşmesini ve token uyumunu doğrular.

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `.agent/skills/design-system/scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Resolve the full path from that directory and keep the working directory at the project root — the scripts read and write project files such as `docs/brand-guidelines.md`, `assets/design-tokens.json` or `src/` relative to it.

## Quick Start

**Generate tokens:**
```bash
node scripts/generate-tokens.cjs --config tokens.json -o tokens.css
```

**Validate usage:**
```bash
node scripts/validate-tokens.cjs --dir src/
```

## References

| Topic | File |
|-------|------|
| Token Architecture | `references/token-architecture.md` |
| Primitive Tokens | `references/primitive-tokens.md` |
| Semantic Tokens | `references/semantic-tokens.md` |
| Component Tokens | `references/component-tokens.md` |
| Component Specs | `references/component-specs.md` |
| States & Variants | `references/states-and-variants.md` |
| Tailwind Integration | `references/tailwind-integration.md` |

## Component Spec Pattern

| Property | Default | Hover | Active | Disabled |
|----------|---------|-------|--------|----------|
| Background | primary | primary-dark | primary-darker | muted |
| Text | white | white | white | muted-fg |
| Border | none | none | none | muted-border |
| Shadow | sm | md | none | none |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate-tokens.cjs` | Generate CSS from JSON token config |
| `scripts/embed-tokens.cjs` | Inline token values into an HTML file |
| `scripts/validate-tokens.cjs` | Check for hardcoded values in code |
| `scripts/search-slides.py` | BM25 search + contextual recommendations |
| `scripts/slide_search_core.py` | Slide search engine core |
| `scripts/generate-slide.py` | Generate slide HTML from tokens + search results |
| `scripts/slide-token-validator.py` | Validate slide HTML for token compliance |
| `scripts/html-token-validator.py` | Validate any HTML for token compliance |
| `scripts/fetch-background.py` | Fetch background images for slides |

**Prerequisites:** Node.js 18+ (`.cjs` scriptleri), Python 3 (`.py` scriptleri).
Harici Python paketi yoktur.

## Templates

| Template | Purpose |
|----------|---------|
| `design-tokens-starter.json` | Starter JSON with three-layer structure |

## Integration

**With brand:** Extract primitives from brand colors/typography (`brand` skill'i
`docs/brand-guidelines.md` kaynağını üretir, `sync-brand-to-tokens.cjs` ile
`assets/design-tokens.*` üretir; bu skill türetilen token'ı yönetir)
**With ui-styling:** Component tokens → Tailwind config
**With slides:** `slides` strateji/metni üretir, bu skill render + doğrulama yapar

**Skill Dependencies:** brand, ui-styling, slides

## Slide System

Brand-compliant presentations using design tokens + Chart.js + contextual decision system.

### Source of Truth

| File | Purpose |
|------|---------|
| `docs/brand-guidelines.md` | Brand identity, voice, colors |
| `assets/design-tokens.json` | Token definitions (primitive→semantic→component) |
| `assets/design-tokens.css` | CSS variables (import in slides) |
| `assets/css/slide-animations.css` | CSS animation library |

### Slide Search (BM25)

```bash
# Basic search (auto-detect domain)
python scripts/search-slides.py "investor pitch"

# Domain-specific search
python scripts/search-slides.py "problem agitation" -d copy
python scripts/search-slides.py "revenue growth" -d chart

# Contextual search (Premium System)
python scripts/search-slides.py "problem slide" --context --position 2 --total 9
python scripts/search-slides.py "cta" --context --position 9 --prev-emotion frustration
```

### Decision System CSVs

| File | Purpose |
|------|---------|
| `data/slide-strategies.csv` | 15 deck structures + emotion arcs + sparkline beats |
| `data/slide-layouts.csv` | 25 layouts + component variants + animations |
| `data/slide-layout-logic.csv` | Goal → Layout + break_pattern flag |
| `data/slide-typography.csv` | Content type → Typography scale |
| `data/slide-color-logic.csv` | Emotion → Color treatment |
| `data/slide-backgrounds.csv` | Slide type → Image category (Pexels/Unsplash) |
| `data/slide-copy.csv` | 25 copywriting formulas (PAS, AIDA, FAB) |
| `data/slide-charts.csv` | 25 chart types with Chart.js config |

### Contextual Decision Flow

```
1. Parse goal/context
        ↓
2. Search slide-strategies.csv → Get strategy + emotion beats
        ↓
3. For each slide:
   a. Query slide-layout-logic.csv → layout + break_pattern
   b. Query slide-typography.csv → type scale
   c. Query slide-color-logic.csv → color treatment
   d. Query slide-backgrounds.csv → image if needed
   e. Apply animation class from slide-animations.css
        ↓
4. Generate HTML with design tokens
        ↓
5. Validate with slide-token-validator.py
```

### Pattern Breaking (Duarte Sparkline)

Premium decks alternate between emotions for engagement:
```
"What Is" (frustration) ↔ "What Could Be" (hope)
```

System calculates pattern breaks at 1/3 and 2/3 positions.

### Slide Requirements

**ALL slides MUST:**
1. Import `assets/design-tokens.css` - single source of truth
2. Use CSS variables: `var(--color-primary)`, `var(--slide-bg)`, etc.
3. Use Chart.js for charts (NOT CSS-only bars)
4. Include navigation (keyboard arrows, click, progress bar)
5. Center align content
6. Focus on persuasion/conversion

### Chart.js Integration

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

<canvas id="revenueChart"></canvas>
<script>
new Chart(document.getElementById('revenueChart'), {
    type: 'line',
    data: {
        labels: ['Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            data: [5, 12, 28, 45],
            borderColor: '#FF6B6B',  // Use brand coral
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            fill: true,
            tension: 0.4
        }]
    }
});
</script>
```

### Token Compliance

```css
/* CORRECT - uses token */
background: var(--slide-bg);
color: var(--color-primary);
font-family: var(--typography-font-heading);

/* WRONG - hardcoded */
background: #0D0D0D;
color: #FF6B6B;
font-family: 'Space Grotesk';
```

### Reference Implementation

Tam özellikli çalışan örnek proje içinde `assets/designs/slides/` altında tutulur;
bu paket örnek dosya taşımaz.

### Slayt Üretimi (bu skill'in sahipliği)

Deck'in **içeriği** `slides` skill'inden gelir (strateji, metin formülleri, düzen
seçimi). Buradaki araçlar o içeriği token uyumlu HTML'e dönüştürür ve denetler:

```bash
# Karar desteği: hedefe göre düzen/tipografi/renk öner
python .agent/skills/design-system/scripts/search-slides.py "problem agitation" -d copy
python .agent/skills/design-system/scripts/search-slides.py "revenue growth" -d chart
python .agent/skills/design-system/scripts/search-slides.py "problem slide" --context --position 2 --total 9

# HTML üret
python .agent/skills/design-system/scripts/generate-slide.py --help

# Token uyumu denetle
python .agent/skills/design-system/scripts/slide-token-validator.py <dosya.html>
```

## Best Practices

1. Never use raw hex in components - always reference tokens
2. Semantic layer enables theme switching (light/dark)
3. Component tokens enable per-component customization
4. Use HSL format for opacity control
5. Document every token's purpose
6. **Slides must import design-tokens.css and use var() exclusively**
