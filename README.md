# Goku Dev Skills (goku-dev-skills)

> **Universal, Agent-Agnostic Intelligence & Production Workflow System for AI Coding Assistants**  
> Compatible with **Google Antigravity**, **Claude Code**, **Cursor**, **Windsurf**, and **OpenCode**.  
> Distributed from single source of truth (`.agent/`) to multiple production microservices and web apps.

---

## 🌟 Overview

**Goku Dev Skills** is a battle-tested engineering and design skill repository designed to transform autonomous AI coding agents into senior architects and meticulous craftspeople. It enforces strict architectural patterns, deterministic verification gates, rich design libraries, and zero-tolerance policies for code rot, AI-slop, and undocumented APIs.

### Core Pillars
1. **18 Production-Grade Skills:** Spanning Spring Boot/Java backend architecture, Next.js / Vite SPA frontend engineering, WCAG-compliant design intelligence, Docker containerization, and semantic git release flows.
2. **16 Enforced Quality Rules & Verification Gates:** 7 measurable Python test gates (API documentation, bundle size budgets, unused imports, i18n key consistency) preventing code regression before completion.
3. **55 Curated Component Themes:** Standalone, production-ready HTML/CSS UI components (sidebars, navbars, menus, parallax, logins, footers, cards, accordions) equipped with bespoke design rationale documents (`<theme-name>.design.md`).
4. **Automated Multi-Project Delivery Engine (`delivery.py`):** Distributes the `.agent/` architecture to connected downstream projects while preserving project-specific custom rules and validating SHA-256 integrity.
5. **260+ Automated Tests:** 173 unittest contract tests and 87 pytest suites running on every modification.

---

## ⚡ Quick Start: Add Skills to Any Project / AI Agent

Any AI coding assistant or developer can install individual skills or component themes directly into their project without cloning this entire repository.

### 1. Zero-Install Execution via `npx`

```bash
# List all 18 available skills and 55 component themes
npx github:mustafa-omeri/goku-dev-skills list

# Add a specific skill to your current project (e.g. frontend-design or ui-ux-pro-max)
npx github:mustafa-omeri/goku-dev-skills add frontend-design

# Add multiple skills with companion validation rules
npx github:mustafa-omeri/goku-dev-skills add frontend-design ui-ux-pro-max --with-rules

# Add a standalone HTML/CSS component theme into your project
npx github:mustafa-omeri/goku-dev-skills add theme sidebars/violet-minimal-sidebar

# Initialize the complete .agent/ architecture for your project
npx github:mustafa-omeri/goku-dev-skills init
```

### 2. Multi-Agent & Platform Adaptation

Different AI coding assistants store rules and skills in different workspace locations. Use the `--agent` flag to target your preferred environment:

| AI Assistant / Tool | Command Example | Target Workspace Location |
| :--- | :--- | :--- |
| **Google Antigravity / OpenCode** | `npx github:mustafa-omeri/goku-dev-skills add <skill>` | `.agent/skills/<skill>/` |
| **Cursor** | `npx github:mustafa-omeri/goku-dev-skills add <skill> --agent cursor` | `.cursor/rules/<skill>/` |
| **Claude Code** | `npx github:mustafa-omeri/goku-dev-skills add <skill> --agent claude` | `.claude/skills/<skill>/` |
| **Windsurf** | `npx github:mustafa-omeri/goku-dev-skills add <skill> --agent windsurf` | `.windsurf/rules/<skill>/` |
| **Custom Path** | `npx github:mustafa-omeri/goku-dev-skills add <skill> --dest <path>` | Custom directory |

### 3. Cross-Platform Support (Windows, macOS, Linux)
Works everywhere Node.js (>= 18) is available:
- **Windows:** PowerShell, CMD, Git Bash
- **macOS:** zsh, bash
- **Linux:** bash, sh
Zero external dependencies, instant execution.

---

## 📁 Repository Structure

```
goku-dev-skills/
├── .agent/                             # Single Source of Truth for all connected projects
│   ├── AGENTS.md                       # Global agent contract, reading order & validation gates
│   ├── rules/                          # 16 Canonical Rules (measurable gates & behavioral contracts)
│   │   ├── trigger-rule-action.md      # Master rule entrypoint & router
│   │   ├── skill-trigger-routing.md    # Trigger dictionary & keyword resolution
│   │   ├── design-skills-enforcement.md# 12-skill UI/UX ownership map & trio mandate
│   │   ├── no-unused-code.md           # Dead code & unused imports gate (Java & TypeScript)
│   │   ├── api-documentation-enforcement.md # REST endpoint documentation enforcement
│   │   ├── vite-spa-enforcement.md     # Pure SPA vs SSR boundary checks
│   │   ├── frontend-bundle-limits.md   # JS/CSS chunk budget gate
│   │   ├── i18n-enforcement.md         # Hardcoded UI string prevention
│   │   └── no-unauthorized-commit.md   # Strict git commit user confirmation rule
│   ├── templates/                      # Standard HANDOFF.md and knowledge-base.md templates
│   └── skills/                         # 18 Modular Production Skills
│       ├── musgoku/                    # Global orchestrator (Spring Boot 3 + React/TypeScript)
│       ├── ui-ux-pro-max/              # Searchable design intelligence (79 styles, 192 palettes, 119 UX rules)
│       ├── frontend-design/            # Distinctive web UI code, anti-AI-slop & component themes
│       │   ├── themes/                 # High-contrast curated color palette cards
│       │   ├── dashboard-theme/        # 18 Visual reference dashboard layouts
│       │   └── component-themes/       # 55 Curated UI component themes across 8 categories
│       ├── canvas-design/              # Visual art, generative posters & typography
│       ├── design-system/              # Primitive -> Semantic -> Component token generation & slide render
│       ├── ui-styling/                 # Tailwind CSS & shadcn/ui code implementation
│       ├── brand/                      # Brand tone, visual identity and communication assets
│       ├── slides/                     # Presentation narrative, strategy & slide structure
│       ├── banner-design/              # Fixed-pixel web & social media banners
│       ├── theme-factory/              # Preset 10 curated color & font pairings
│       ├── git-release-workflow/       # Autonomous semantic release and version tagging
│       ├── i18n-localization/          # Multi-language translation integrity checker
│       ├── production-docker-architect/# Multi-stage Docker, health checks & container security
│       ├── doc-coauthoring/            # Collaborative RFC, PRD & architectural decision records
│       ├── karpathy-guidelines/        # Code clarity, zero bloat, and minimal abstraction principles
│       └── web-ide-ux-architect/       # Browser-based IDE, code editor & terminal UI architecture
├── tests/                              # Integration & distribution regression test suite
├── delivery.md                         # Multi-project distribution config and sync guide
├── delivery.py                         # 7-step zero-downtime distribution engine
├── HANDOFF.md                          # Session state continuity, proven pitfalls & metrics
├── knowledge-base.md                   # Append-only architectural decision log & solved bugs
├── readme-help.md                      # Agent token optimization and report trigger policy
└── .gitignore                          # Excludes secrets (.env), backups and build artifacts
```

---

## 🛠️ The 18 Shipped Skills

| Skill | Category | Primary Focus & Capabilities |
| :--- | :--- | :--- |
| **`musgoku`** | Orchestrator | Java 21, Spring Boot 3, REST APIs, JPA queries, WebSocket, TypeScript & React routing. |
| **`ui-ux-pro-max`** | Design Intel | Searchable engine: 79 styles, 192 product palettes, 74 font pairings, 119 UX heuristics. |
| **`frontend-design`** | UI Code | Distinctive web UI code, avoiding generic AI templates, hosts 55 component themes. |
| **`canvas-design`** | Visual Art | Unbounded graphic design, editorial posters, manifestos, visual weight and spatial tension. |
| **`design-system`** | Token Engine | Token pipeline (primitive → semantic → component), slide generation and contrast verification. |
| **`ui-styling`** | Tailwind/shadcn | Accessible Radix primitives, utility classes, mobile-first layouts and dark mode. |
| **`git-release-workflow`** | DevOps/Git | User-approved semantic tagging, changelog generation, atomic commit & push flow. |
| **`i18n-localization`** | i18n/L10n | Translation key parity, missing key detection, elimination of hardcoded default values. |
| **`production-docker-architect`**| Containers | Optimized multi-stage Dockerfiles, non-root users, CVE minimization, compose stacks. |
| **`brand`** | Identity | Brand voice, archetype definitions, color psychology, and corporate identity guidelines. |
| **`slides`** | Presentations | Narrative structure, executive summaries, pacing and slide layout strategy. |
| **`banner-design`** | Marketing | Fixed-dimension marketing banners, display advertising, OpenGraph previews. |
| **`theme-factory`** | Palette Library| 10 curated turnkey color palettes and paired Google Fonts for slides and documents. |
| **`web-ide-ux-architect`** | Developer UX | High-density split-pane layouts, code editors, command palettes, and terminal interfaces. |
| **`doc-coauthoring`** | Documentation | Structured PRD drafting, RFC formulation, and technical specification reviews. |
| **`karpathy-guidelines`** | Code Standards | Radical simplification, elimination of speculative generality, readable architectures. |
| **`musgoku-prd`** | Compliance | Product requirement documents with integrated KVKK / GDPR privacy audits. |
| **`design`** | Creative Brief | Creative direction router, brand brief synthesis, and logo design specifications. |

---

## 🎨 Component Themes Library (`component-themes/`)

Located at `.agent/skills/frontend-design/component-themes/`, this directory provides **55 production-grade HTML/CSS component themes**. Coding agents are instructed to inspect this library before creating UI components from scratch.

Each theme contains:
- Complete standalone working code (`index.html`, `styles.css`, SVG icons, assets).
- A dedicated `<theme-name>.design.md` document covering:
  - **Visual Essence & Palette:** Exact HEX color codes, font pairings, negative space balance.
  - **Agent Decision Matrix:** Triggers, ideal product types, and anti-patterns (when NOT to choose).
  - **Structural Anatomy:** Semantic HTML5 DOM and CSS Flexbox/Grid architecture.
  - **Interactions & Micro-Animations:** Transition curves, hover elevations, and active indicator pills.
  - **Framework Porting:** Modern adaptation recipes for React, Vite SPA, Tailwind CSS, and shadcn/ui.

### Component Summary by Category
- **Sidebars (8 Themes):** Minimal dark violet (`violet-minimal-sidebar`), dual-column indigo drawer (`dual-column-indigo-sidebar`), clean light SaaS rail (`light-saas-dual-rail-sidebar`), dark slate dock (`dark-slate-dock-sidebar`), CSS-toggle collapsible (`collapsible-expandable-sidebar`), compact developer dock (`compact-dock-sidebar`), workspace & profile switcher (`workspace-profile-sidebar`), and macOS window-chrome team sidebar (`window-chrome-team-sidebar`).
- **Navbars & Menus (2 Themes):** Floating island pill navbar with kinetic sliding active marker (`floating-pill-marker-navbar`), and fullscreen overlay menu with staggered link animations (`fullscreen-overlay-stagger-menu`).
- **Parallax (2 Themes):** Alternating narrative chapter parallax (`split-section-story-parallax`), and pure CSS multi-layer depth parallax (`multi-layer-pure-css-parallax`).
- **Accordions (2 Themes):** Horizontal expandable plum team gallery (`horizontal-expand-plum-accordion`), and dark slate artwork accordion (`horizontal-expand-dark-accordion`).
- **Cards (10 Themes):** Pricing tier comparison grid, 3D interactive flip KPI card, vibrant social creator profile, career job listing, destination travel preview, dark account toolbar, expandable summary metric, editorial story preview, and portfolio member card.
- **Logins (16 Themes):** Minimalist floating orb, compact dark credentials, clean B2B light card, Web3 crypto neon, orbiting blob security, animated SVG wave header, split-screen value hero, conversational sign-in, cosmic orbit, geometric split banner, fintech payment security, dark luxury glassmorphic, sliding dual-state auth toggle, and photo hero switcher.
- **Footers (15 Themes):** Animated SVG wave footers, SaaS conversion CTA banners, minimal community pills, cyan electric split footers, consultative meeting schedulers ("Schedule a Call"), midnight newsletter captures, and enterprise compliance directories.

---

## 🚀 Multi-Project Distribution (`delivery.py`)

`goku-dev-skills` acts as the upstream authority. Changes made in `.agent/` are propagated downstream across target repositories using `delivery.py`:

```bash
# 1. Preview changes without touching files
python delivery.py --dry-run

# 2. Distribute to all configured projects (creates backup and retains newest 1)
python delivery.py --keep 1

# 3. Verify SHA-256 byte-for-byte parity across all target projects
python delivery.py --verify

# 4. Target a specific project
python delivery.py --only ocai
```

### Safety Features
- **Project Rule Preservation:** Automatically detects and preserves the target project's `## Proje Bazlı Ek Kurallar` block inside `AGENTS.md`.
- **Automated Rolling Backups:** Safely backs up existing target `.agent/` trees to `yedekler/` prior to replacement.
- **Prune Policy:** Automatically prunes older backups via `--keep N` to prevent disk bloat.
- **Zero Git Side-Effects:** Does not execute git commits or pushes on target repositories.

---

## 🧪 Testing & Verification Gates

```bash
# Run 173-test contract & distribution verification suite
cd .agent/skills/ui-ux-pro-max/scripts/tests
python -m unittest discover -p "test_*.py"

# Run 87-test pytest suite for styling, design system and brand skills
python -m pytest .agent/skills/ui-styling/scripts/tests .agent/skills/design-system/scripts/tests .agent/skills/brand/scripts/tests -q

# Run strict rule validation gate
python .agent/skills/musgoku/scripts/rules_gates.py --strict
```

---

## 📜 Global Agent Contract

Every agent interacting with a project governed by `goku-dev-skills` adheres to the strict protocol defined in `AGENTS.md`:
1. **Mandatory Reading Order:** `HANDOFF.md` → `DEV_BRIEF.md` → Rules & Decisions.
2. **Deterministic Evidence:** Never claim "it works" or "rule followed" without running measurable verification gates (`rules_gates.py`, `i18n_checker.py`, `check_api_docs.py`).
3. **Strict Commit Approval:** Agents never invoke `git commit` or `git push` without explicit user review of changed files and proposed commit messages.
4. **Session Continuity:** Every session concludes with updating `knowledge-base.md` and the standardized `HANDOFF.md` transition report.

---

## 📄 License

Individual components, skills, and templates preserve their respective open-source licenses (MIT / Apache 2.0 / Creative Commons). Review `LICENSE.txt` inside respective skill directories for specifics.