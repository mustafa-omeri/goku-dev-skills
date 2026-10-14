---
name: slides
description: Sunumun **içeriğinin** sahibi: deck stratejisi, duygu yayı, slayt sıralaması, düzen seçimi (25 düzen) ve metin formülleri (PAS, AIDA, FAB). Tetikleyiciler: "sunum", "deck", "pitch deck", "slayt", "sunum içeriği", "sunum metni", "presentation", "slide content", "deck strategy". Tetiklenmez: HTML'e dönüştürme ve token denetimi `design-system`'e aittir; bu skill script çalıştırmaz. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
argument-hint: "[topic] [slide-count]"
metadata:
  author: claudekit
  version: "1.0.0-set"
---

# Slides

Stratejik HTML sunum tasarımı. Bu skill **deck'in ne söyleyeceğine** karar verir:
strateji, metin, düzen seçimi, sıralama. HTML'e dönüştürme ve token doğrulaması
`design-system` skill'inin işidir.

## Ne zaman devrede

- Pazarlama sunumu ve pitch deck
- Veri destekli slayt içeriği (Chart.js)
- Stratejik düzen seçimi
- Copywriting formülleriyle optimize edilmiş sunum metni
- Mevcut bir deck'in içeriğini yeniden yazma

## Kapsam Sınırı

| Konu | Sahip |
|------|-------|
| Deck stratejisi, metin, düzen, sıralama | **bu skill** |
| HTML render, `generate-slide.py`, token denetimi | `design-system` |
| Palet ve token değerleri | `design-system` / `theme-factory` |
| Slayt görseli / kapak görseli | `banner-design` |

**Bu skill script çalıştırmaz.** Üretim ve doğrulama komutları için
`.agent/skills/design-system/SKILL.md` → "Slayt Üretimi" bölümüne bak.

## Akış

1. **Deck stratejisi** → `references/slide-strategies.md` (15 deck yapısı + duygu yayı)
2. **Slayt sayısı ve sıra** → stratejiye göre belirle, duygu yayına göre diz
3. **Her slayt için düzen** → `references/layout-patterns.md` (25 düzen)
4. **Metin** → `references/copywriting-formulas.md` (PAS, AIDA, FAB …)
5. **HTML iskeleti** → `references/html-template.md`
6. **Render + doğrulama** → `design-system` skill'i:
   `generate-slide.py` → `slide-token-validator.py`

## Subcommands

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `create` | Create strategic presentation slides | `references/create.md` |

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project. This skill ships **no scripts**; the generation scripts live in the sibling `design-system` skill: `../design-system/scripts/<file>`. Keep the working directory at the project root — those scripts read and write `assets/design-tokens.css`, `assets/designs/slides/` and `docs/brand-guidelines.md` relative to it.

## References (Knowledge Base)

| Topic | File |
|-------|------|
| Layout Patterns | `references/layout-patterns.md` |
| HTML Template | `references/html-template.md` |
| Copywriting Formulas | `references/copywriting-formulas.md` |
| Slide Strategies | `references/slide-strategies.md` |
| Create subcommand | `references/create.md` |

## Routing

1. İsteğin ilk kelimesi `create` ise `references/create.md` dosyasını yükle.
2. Değilse yukarıdaki 6 adımlı akışı uygula.
3. Kalan argümanları (konu, slayt sayısı) bağlama uygula.
