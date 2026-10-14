---
name: brand
description: Marka içeriğinin sahibi: ton, görsel kimlik, mesaj çerçevesi, renk/font spesifikasyonu, varlık kuralları, tutarlılık denetimi; `docs/brand-guidelines.md` üretir ve token'a senkronlar. Tetikleyiciler: "marka", "marka tonu", "görsel kimlik", "marka kılavuzu", "brand voice", "brand guidelines", "visual identity", "style guide". Tetiklenmez: dokümanın yazma süreci `doc-coauthoring`'e, PRD `musgoku-prd`'ye aittir. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
argument-hint: "[update|review|create] [args]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# Brand

Brand identity, voice, messaging, asset management, and consistency frameworks.

## When to Use

- Brand voice definition and content tone guidance
- Visual identity standards and style guide development
- Messaging framework creation
- Brand consistency review and audit
- Asset organization, naming, and approval
- Color palette management and typography specs

## Kapsam Sınırı

| Konu | Sahip |
|------|-------|
| Marka içeriği: ton, görsel kimlik, mesaj, varlık kuralları | **bu skill** |
| Dokümanın *yazılma süreci* (yapı, iterasyon, okur testi) | `doc-coauthoring` |
| Hazır renk/font paleti seçimi (artifact teması) | `theme-factory` |
| Marka paletinden **token** üretimi (primitive → semantic → component) | `design-system` |
| Token'ın Tailwind/shadcn tarafına bağlanması | `ui-styling` |

Bu skill guideline'ın **içeriğini** üretir; `doc-coauthoring` dokümanı **nasıl yazacağını**
yönetir. İkisi birlikte çalışır, birbirinin yerine geçmez.

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `.agent/skills/brand/scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Resolve the full path from that directory and keep the working directory at the project root — the scripts read and write project files such as `docs/brand-guidelines.md`, `assets/design-tokens.json` or `src/` relative to it.

## Quick Start

**Inject brand context into prompts:**
```bash
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json
```

**Validate an asset:**
```bash
node scripts/validate-asset.cjs <asset-path>
```

**Extract/compare colors:**
```bash
node scripts/extract-colors.cjs --palette
node scripts/extract-colors.cjs <image-path>
```

## Brand Sync Workflow

```bash
# 1. Edit docs/brand-guidelines.md (or use the `update` reference below)
# 2. Sync to design tokens
node scripts/sync-brand-to-tokens.cjs
# 3. Verify
node scripts/inject-brand-context.cjs --json | head -20    # macOS/Linux
node scripts/inject-brand-context.cjs --json | Select-Object -First 20   # PowerShell
```

The sync stops when it detects existing token files, `:root` custom properties
or Tailwind v4 `@theme` variables in common CSS entry points and their local
CSS imports, or Tailwind theme colors and presets. Review the reported source
before proceeding. If the detected files are the managed
`assets/design-tokens.*` outputs from an earlier sync and replacing them is
intentional, re-run with `--force`.

**Files synced:**
- `docs/brand-guidelines.md` → Source of truth
- `assets/design-tokens.json` → Token definitions
- `assets/design-tokens.css` → CSS variables

## Subcommands

Kullanıcı isteğinin ilk kelimesi bir alt komut olabilir (`update`, `review`, `create`).
Alt komut tanınmıyorsa doğrudan bu SKILL.md akışını uygula.

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `update` | Update brand identity and sync to all design systems | `references/update.md` |

## References

| Topic | File |
|-------|------|
| Voice Framework | `references/voice-framework.md` |
| Visual Identity | `references/visual-identity.md` |
| Messaging | `references/messaging-framework.md` |
| Consistency | `references/consistency-checklist.md` |
| Guidelines Template | `references/brand-guideline-template.md` |
| Asset Organization | `references/asset-organization.md` |
| Color Management | `references/color-palette-management.md` |
| Typography | `references/typography-specifications.md` |
| Logo Usage | `references/logo-usage-rules.md` |
| Approval Checklist | `references/approval-checklist.md` |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/inject-brand-context.cjs` | Extract brand context for prompt injection |
| `scripts/sync-brand-to-tokens.cjs` | Sync brand-guidelines.md → design-tokens.json/css |
| `scripts/validate-asset.cjs` | Validate asset naming, size, format |
| `scripts/extract-colors.cjs` | Extract and compare colors against palette |

## Templates

| Template | Purpose |
|----------|---------|
| `templates/brand-guidelines-starter.md` | Complete starter template for new brands |

## Routing

1. İsteğin ilk kelimesi bir alt komutsa (`update`/`review`/`create`) ilgili
   `references/<alt-komut>.md` dosyasını yükle.
2. Alt komut yoksa bu dosyadaki akışı uygula.
3. Kalan argümanları bağlama uygula.
