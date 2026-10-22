# ⚡ Goku Dev Skills (`goku-dev-skills`)

<div align="center">

[![Version](https://img.shields.io/badge/version-1.11.5-blue.svg?style=for-the-badge&logo=npm)](https://www.npmjs.com/package/goku-dev-skills)
[![Skills](https://img.shields.io/badge/skills-29%20battle--tested-8A2BE2.svg?style=for-the-badge&logo=expertsexchange)](./.agent/skills/)
[![Rules](https://img.shields.io/badge/rules-19%20enforced-orange.svg?style=for-the-badge&logo=codereview)](./.agent/rules/)
[![Gates](https://img.shields.io/badge/gates-11%20deterministic-success.svg?style=for-the-badge&logo=checkmarx)](./.agent/skills/musgoku/scripts/)
[![Tests](https://img.shields.io/badge/tests-100%25%20green-brightgreen.svg?style=for-the-badge&logo=pytest)](./tests/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](./LICENSE)

**Universal, Agent-Agnostic Intelligence & Production Workflow Engine for AI Coding Assistants**  
*Turning stochastic language models into senior software architects, meticulous UI/UX craftspeople, and disciplined QA sentinels.*

[Overview](#-overview) • [Why Goku?](#-why-goku-dev-skills-anti-slop-matrix) • [Developer Archetypes](#-the-29-production-skills--developer-archetypes) • [Quickstart](#-quick-start--installation) • [Interactive Catalog](#-interactive-visual-skills-catalog) • [Verification Gates](#-the-11-deterministic-verification-gates)

</div>

---

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              GOKU DEV SKILLS ECOSYSTEM v1.11.5                         │
├──────────────────────────────┬─────────────────────────────┬───────────────────────────┤
│    29 PRODUCTION SKILLS      │     19 ENFORCED RULES       │   55 COMPONENT THEMES     │
│ Architecture · Design · TDD  │ 11 Deterministic Gates      │ Standalone HTML/CSS/JS    │
│ Security · SEO · Backlog AI  │ Full-Stack Vertical Slice   │ Bespoke Rationale Docs    │
│ LLM Council · Docker · i18n  │ Zero-Slop · WCAG AA Parity  │ Micro-Interactions        │
└──────────────────────────────┴─────────────────────────────┴───────────────────────────┘
```

---

## 🌟 Overview

**Goku Dev Skills** is an open-source, battle-tested software engineering and design operating system for autonomous AI coding agents (**Google Antigravity**, **Cursor**, **Claude Code**, **Windsurf**, and **OpenCode**).

Most AI coding assistants produce **"Skin-Deep Code"**: they scaffold quick React components, pass tests with shallow mocks, declare tasks *"Done"*, and abandon missing verifications, empty databases, unhandled network states, and generic, uninspired UI styling.

**Goku Dev Skills eliminates this failure mode.** By injecting structured skills, behavioral contracts, 11 deterministic Python verification gates, and the mandatory **5-Layer Full-Stack Vertical Slice Protocol**, it transforms autonomous assistants into seasoned engineering partners that verify every layer from SQL migration to responsive viewport ergonomics before declaring any task finished.

---

## ⚡ Why Goku Dev Skills? (Anti-Slop Matrix)

| Engineering Dimension | Standard AI Coding Assistant | With Goku Dev Skills (`goku-dev-skills`) |
| :--- | :--- | :--- |
| **Definition of Done (DoD)** | ❌ **Phantom Done:** Marks tasks completed after unit mock tests pass; ignores missing DB migrations and unmounted views. | ✅ **5-Layer Vertical Slice:** Mandatory proof across DB/Migration, Backend View/RPC, Client API, End-User UX, and Admin Management Form. |
| **UI/UX Aesthetics** | ❌ **AI Slop:** Generic `bg-white p-4 border rounded` boxes, flat typography, unaligned numeric tables, zero visual hierarchy. | ✅ **Zanaat Anti-Slop & 55 Component Themes:** 79 curated styles, 192 product palettes, tabular numbers, contrast verification (`check_design_slop.py`). |
| **Bug Fixing & Debugging** | ❌ **Guess & Patch:** Edits code blindly, often breaking existing logic and creating silent regressions. | ✅ **Red Feedback Loop (`diagnosing-bugs`):** Mandatory red test proving the bug before writing a single line of production code. |
| **Complexity Management** | ❌ **Speculative Bloat:** Premature abstraction, unnecessary interfaces, over-engineered utility functions. | ✅ **Karpathy Guidelines & Deep Modules:** Radical simplicity, narrow interfaces, complexity containment, deletion testing. |
| **Architectural Decisions** | ❌ **Sycophantic Agreement:** Agrees with any user prompt, even flawed designs. | ✅ **3-Stage LLM Council (`karpathy-guidelines`):** Blind peer review deliberation (Stage 1 Proposals → Stage 2 Blind Review → Stage 3 Synthesis). |
| **Security & Vulnerabilities** | ❌ **Blind Inserts:** Misses RLS policies, rate limits, honeypots, and input sanitization on public forms. | ✅ **Security Sentinel (`security-audit`):** Guidance & Full-Audit modes, OWASP checks, strict blind insert policies, safe POSIX shell execution. |
| **SEO & AI Search** | ❌ **Blank Metadata:** Basic title tags, ignores modern AI crawlers and search engine answer blocks. | ✅ **Agentic SEO (`seo-growth`):** AI crawler matrix (`/llms.txt`), competitive gap briefs, JSON-LD schemas, robots.txt bot directives. |
| **Verification & Integrity** | ❌ **Self-Claimed Green:** "I tested it and it works" with no verifiable metrics. | ✅ **11 Deterministic Gates:** Measured exit codes for DB migrations, bundle budgets, unused imports, i18n key parity, and API docs. |

---

## 🧠 The 29 Production Skills & Developer Archetypes

The 29 production skills are organized into 5 cohesive **Developer Archetypes**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               DEVELOPER ARCHETYPE MODULES                              │
├───────────────────────┬───────────────────────┬────────────────────────────────────────┤
│ 🏗️ System Architect   │ 🎨 UI/UX Foundry      │ 🧪 QA & Reliability Guardian           │
│ 🛡️ Security Sentinel  │ 🚀 Product Catalyst   │ 📑 Interactive Offline Catalog         │
└───────────────────────┴───────────────────────┴────────────────────────────────────────┘
```

### 1. 🏗️ The System Architect & Backend Engine
*Core infrastructure, clean architecture, deep modules, containerization, and data contracts.*

- [`musgoku`](.agent/skills/musgoku/SKILL.md) — Master backend & frontend orchestrator (Java 21, Spring Boot 3, REST APIs, JPA queries, React architecture).
- [`codebase-design`](.agent/skills/codebase-design/SKILL.md) — Deep module engineering, narrow seams, complexity abstraction, and the deletion test.
- [`production-docker-architect`](.agent/skills/production-docker-architect/SKILL.md) — Hardened multi-stage Docker builds, non-root users, CVE minimization, and optimized Compose stacks.
- [`domain-modeling`](.agent/skills/domain-modeling/SKILL.md) — Ubiquitous language enforcement, `GLOSSARY.md` maintenance, and strict 3-criteria Architecture Decision Records (ADRs).

### 2. 🎨 The UI/UX & Design Systems Foundry
*Distinctive design, accessible primitives, token pipelines, marketing creatives, and developer workstations.*

- [`frontend-design`](.agent/skills/frontend-design/SKILL.md) — Production UI code avoiding generic AI slop; houses the 55 production component themes.
- [`ui-ux-pro-max`](.agent/skills/ui-ux-pro-max/SKILL.md) — Searchable design reference database: 79 styles, 192 product palettes, 74 font pairings, 119 UX heuristics.
- [`design-system`](.agent/skills/design-system/SKILL.md) — Multi-tier token pipeline (primitive → semantic → component), CSS variables, and HTML slide deck generator.
- [`ui-styling`](.agent/skills/ui-styling/SKILL.md) — Tailwind CSS and shadcn/ui code layer: accessible Radix primitives, dark mode, responsive layouts, and `tailwind.config`.
- [`theme-factory`](.agent/skills/theme-factory/SKILL.md) — 10 curated turnkey color palettes with paired Google Fonts and hex scales for zero-friction branding.
- [`banner-design`](.agent/skills/banner-design/SKILL.md) — Fixed-dimension marketing banners, social covers (X, LinkedIn, Facebook, YouTube), safe zones, and 22 art-direction styles.
- [`brand`](.agent/skills/brand/SKILL.md) — Brand voice, tone matrices, visual identity specs, and automated `docs/brand-guidelines.md` synthesis.
- [`web-ide-ux-architect`](.agent/skills/web-ide-ux-architect/SKILL.md) — High-density IDE interfaces: split panes, code editors, command palettes, and terminal docks.

### 3. 🧪 The Quality, TDD & Debugging Guardian
*Test-driven development, falsifiable hypotheses, smell detection, and multi-model consensus.*

- [`tdd`](.agent/skills/tdd/SKILL.md) — Strict Test-Driven Development: vertical slices, minimal passing code, and red-before-green verification.
- [`diagnosing-bugs`](.agent/skills/diagnosing-bugs/SKILL.md) — 6-phase systematic root-cause debugging: mandatory red feedback loop before editing production code.
- [`code-review`](.agent/skills/code-review/SKILL.md) — Parallel two-axis code review: Martin Fowler code smells baseline vs spec fidelity and scope creep.
- [`karpathy-guidelines`](.agent/skills/karpathy-guidelines/SKILL.md) — Radical code simplification, avoiding speculative generality, plus 3-Stage LLM Council Deliberation (`council_ranker.py`).
- [`react-best-practices`](.agent/skills/react-best-practices/SKILL.md) — React 19 & Next.js performance optimizations, waterfall elimination, and clean composition patterns.

### 4. 🛡️ The Security, SEO & Operations Sentinel
*Vulnerability hunting, AI crawler optimization, internationalization parity, and semantic releases.*

- [`security-audit`](.agent/skills/security-audit/SKILL.md) — Vulnerability scanning, penetration testing, exploit shielding (Honeypot/Rate-limiting/RLS), Guidance & Full-Audit modes.
- [`seo-growth`](.agent/skills/seo-growth/SKILL.md) — Technical SEO, Generative Engine Optimization (GEO/AI search), AI Crawler Matrix (`/llms.txt`), robots.txt directives, and GTM playbooks.
- [`i18n-localization`](.agent/skills/i18n-localization/SKILL.md) — Multi-language translation key parity, hardcoded text detection, and elimination of silent default-value fallbacks.
- [`git-release-workflow`](.agent/skills/git-release-workflow/SKILL.md) — User-approved atomic release workflow: semantic version tagging, commit generation, and remote push.

### 5. 🚀 The Product, Ideation & Growth Catalyst
*Autonomous backlog innovation, interactive user tours, creative direction, and technical documentation.*

- [`my-idea`](.agent/skills/my-idea/SKILL.md) — Autonomous backlog idea pool (`docs/idea/myidea.md`), project-aware re-rating, top-3 recommendation picks, and TDD handoff.
- [`doc-coauthoring`](.agent/skills/doc-coauthoring/SKILL.md) — Technical PRD drafting, RFC formulation, architecture decision docs, and context-free reader testing.
- [`onboarding-tour`](.agent/skills/onboarding-tour/SKILL.md) — Interactive guided product tours, walkthroughs, and coachmarks via Driver.js and React Joyride.
- [`slides`](.agent/skills/slides/SKILL.md) — Presentation narrative architecture, pacing, emotion arcs, 25 layout recipes, and copywriting formulas (PAS, AIDA, FAB).
- [`canvas-design`](.agent/skills/canvas-design/SKILL.md) — Unbounded graphic design: editorial posters, aesthetic manifestos, cover artwork, and static visual pieces (`.png`/`.pdf`).
- [`mock-asset-provider`](.agent/skills/mock-asset-provider/SKILL.md) — Realistic placeholder visuals, developer avatars, event imagery, and zero-config CDN fallback pipelines.
- [`design`](.agent/skills/design/SKILL.md) — Creative direction router, brand brief synthesizer, logo style explorer, and corporate identity specifications.
- [`task-observer`](.agent/skills/task-observer/SKILL.md) — Meta-skill that monitors execution workflows, distilling observations into reusable rules and skills.

---

## ⚡ Quick Start & Installation

Install only what your tech stack needs — from ultra-lightweight backend setups (~2.5 MB) to minimal frontend (~5 MB) or fullstack architectures (~65 MB):

### 1. Profile-Based Installation via `npx`

```bash
# ☕ Backend Profile (Java, Spring Boot, Python, APIs, DB Migrations) — Ultra-lightweight (~2.5 MB, zero UI clutter)
npx goku-dev-skills init -p backend

# 🎨 Minimal Frontend Profile (React, Vite, Next.js, Tailwind, Anti-slop) — Excludes 55 heavy themes (~5 MB)
npx goku-dev-skills init -p frontend -m

# 🌟 Full Frontend Profile (Includes all 55 HTML/CSS component themes) (~60 MB)
npx goku-dev-skills init -p frontend

# 🚀 Fullstack Profile (All 29 skills, 55 themes, 19 rules & 11 verification gates) (~65 MB)
npx goku-dev-skills init -p fullstack

# 🔍 Auto-Detect Stack (Inspects pom.xml, package.json, requirements.txt and selects optimal profile)
npx goku-dev-skills init --detect
```

### 2. Surgical Workspace Updates (Zero-Bloat Sync)

When upstream skills, rules, or scripts receive updates, sync **only what is already installed in your project**. It will **never** download uninstalled skills or re-introduce excluded heavy component themes:

```bash
# Preview pending updates without writing to disk (Dry-Run / Inspection)
npx goku-dev-skills update --check

# Surgically update only existing skills, rules, and templates in current workspace
npx goku-dev-skills update

# Force pulling latest updates directly from GitHub main repository
npx goku-dev-skills update --remote

# Target a specific downstream project directory
npx goku-dev-skills update --dest ./my-backend-service
```

> [!TIP]
> **Project Rule Preservation:** Custom rules inside `AGENTS.md` under `## Proje Bazlı Ek Kurallar` are automatically parsed, protected, and restored during updates.

> [!NOTE]
> **🤖 AI Agent Natural Language Triggers:**
> Instead of running terminal commands manually, you can tell your AI assistant directly in chat:
> - `"Goku skill güncelle"`, `"skill update"`, `"GS update"`, `"GS güncelle"`
> - `"goku update"`, `"skillset güncelle"`, `"skill'leri güncelle"`, `"sync skills"`
> The agent will autonomously execute the surgical update protocol, verify zero-clutter, ensure your project rules are protected, and present a status report.

### 3. Multi-Agent & Platform Support

Different AI coding assistants store rules and skills in different workspace locations. Use the `--agent` flag to target your preferred environment:

| AI Assistant / Tool | Command Example | Target Workspace Location |
| :--- | :--- | :--- |
| **Google Antigravity / OpenCode** | `npx goku-dev-skills init` | `.agent/skills/` & `.agent/rules/` |
| **Cursor** | `npx goku-dev-skills add <skill> --agent cursor` | `.cursor/rules/<skill>/` |
| **Claude Code** | `npx goku-dev-skills add <skill> --agent claude` | `.claude/skills/<skill>/` |
| **Windsurf** | `npx goku-dev-skills add <skill> --agent windsurf` | `.windsurf/rules/<skill>/` |
| **Custom Path** | `npx goku-dev-skills init --dest <path>` | Custom target directory |

---

## 📑 Interactive Visual Skills Catalog

Included with every full distribution is a standalone, offline, single-file interactive visual catalog (`skills-catalog.html`).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        OFFLINE VISUAL SKILLS CATALOG (HTML)                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Instant Fuzzy Search: Press `/` or `Ctrl+K` to search across all 29 skills           │
│ • Dual View Modes: Press `V` to toggle between rich Card Grid & Compact Table View     │
│ • Theme Switcher: Press `T` to toggle Dark / Light aesthetic                           │
│ • One-Click Copy: Instantly copy agent prompt triggers and execution commands          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

**Quick Open:**
```bash
# Windows
start .agent/skills-catalog.html

# macOS
open .agent/skills-catalog.html

# Linux
xdg-open .agent/skills-catalog.html
```

---

## 🛡️ The 5-Layer Full-Stack Vertical Slice Protocol

To prevent the **"Phantom Done"** failure mode (where an agent declares a feature *"BİTTİ / DONE"* simply because an isolated React component and mock unit tests passed, despite missing backend tables, views, and forms), Goku Dev Skills enforces the **5-Layer Vertical Slice Protocol**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        5-LAYER FULL-STACK VERTICAL SLICE (DoD)                         │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
  1. DB & PERSISTENCE  ──► Physical migration file, columns, constraints, RLS policies.
                                            │
  2. BACKEND & VIEWS   ──► SQL views, RPCs or REST endpoints returning real data fields.
                                            │
  3. CLIENT & API      ──► Frontend API hooks connecting to live views (no silent undefined).
                                            │
  4. UI/UX & ACTIONS   ──► Rendered states (loading, empty, error) & real tracking RPCs.
                                            │
  5. MANAGEMENT & LOOP ──► Admin form or ingestion UI ("How does data enter the system?").
```

> ⛔ **Strict Anti-Phantom Rule:** If ANY required layer is missing, the task CANNOT be marked *"Done"*. It must be declared *"YARIM (Incomplete: Missing Layer)"* and prioritized in `HANDOFF.md`.

---

## 🧪 The 11 Deterministic Verification Gates

Every measurable rule in Goku Dev Skills is backed by a standalone Python verification script with clear exit codes (`0` = pass, `1` = violation, `2` = tool error):

| Stack / Focus Area | Mandatory Verification Command | Enforced Rule |
| :--- | :--- | :--- |
| **Backend / API Documentation** | `python .agent/skills/musgoku/scripts/check_api_docs.py` | [`api-documentation-enforcement.md`](.agent/rules/api-documentation-enforcement.md) |
| **Backend / Database Migrations** | `python .agent/skills/musgoku/scripts/check_db_migrations.py` | [`db-migration-enforcement.md`](.agent/rules/db-migration-enforcement.md) |
| **Design / Skill Ownership** | `python .agent/skills/musgoku/scripts/check_design_skills.py` | [`design-skills-enforcement.md`](.agent/rules/design-skills-enforcement.md) |
| **Design / Anti-Slop & Craft Floor**| `python .agent/skills/musgoku/scripts/check_design_slop.py` | [`design-skills-enforcement.md`](.agent/rules/design-skills-enforcement.md) |
| **Design / Theme Contrast & WCAG**| `python .agent/skills/musgoku/scripts/check_theme_contrast.py` | [`design-skills-enforcement.md`](.agent/rules/design-skills-enforcement.md) |
| **Frontend / Bundle Budgets** | `python .agent/skills/musgoku/scripts/check_bundle_limits.py` | [`frontend-bundle-limits.md`](.agent/rules/frontend-bundle-limits.md) |
| **Frontend / i18n Key Parity** | `python .agent/skills/i18n-localization/scripts/i18n_checker.py` | [`i18n-enforcement.md`](.agent/rules/i18n-enforcement.md) |
| **TypeScript / React Compiles** | `npx tsc --noEmit` | [`no-unused-code.md`](.agent/rules/no-unused-code.md) |
| **Java / Spring Compiles** | `mvn clean compile -DskipTests` | [`no-unused-code.md`](.agent/rules/no-unused-code.md) |
| **Skill Contracts & Triggers** | `cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts` | [`skill-trigger-routing.md`](.agent/rules/skill-trigger-routing.md) |
| **Sprint / Kanban / MVP Board** | `python .agent/skills/musgoku/scripts/check_sprint_board.py` | [`sprint-delivery-workflow.md`](.agent/rules/sprint-delivery-workflow.md) |
| **Rule System Integrity** | `python .agent/skills/musgoku/scripts/rules_gates.py --strict` | [`rules_gates.py`](.agent/skills/musgoku/scripts/rules_gates.py) |

---

## 🎨 55 Production Component Themes (`component-themes/`)

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
- **Sidebars (8 Themes):** Minimal dark violet, dual-column indigo drawer, clean light SaaS rail, dark slate dock, CSS-toggle collapsible, compact developer dock, workspace switcher, and macOS window-chrome team sidebar.
- **Navbars & Menus (2 Themes):** Floating island pill navbar with kinetic sliding active marker, and fullscreen overlay menu with staggered link animations.
- **Parallax (2 Themes):** Alternating narrative chapter parallax, and pure CSS multi-layer depth parallax.
- **Accordions (2 Themes):** Horizontal expandable plum team gallery, and dark slate artwork accordion.
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

## 📜 Global Agent Contract

Every agent interacting with a project governed by `goku-dev-skills` adheres to the strict protocol defined in `AGENTS.md`:
1. **Mandatory Reading Order:** `HANDOFF.md` → `DEV_BRIEF.md` → Rules & Decisions.
2. **Deterministic Evidence:** Never claim "it works" or "rule followed" without running measurable verification gates (`rules_gates.py`, `i18n_checker.py`, `check_api_docs.py`).
3. **Strict Commit Approval:** Agents never invoke `git commit` or `git push` without explicit user review of changed files and proposed commit messages (or explicit `commitx` / `commitle` triggers).
4. **Session Continuity:** Every session concludes with updating `knowledge-base.md` and the standardized `HANDOFF.md` transition report.

---

## 📄 License

Individual components, skills, and templates preserve their respective open-source licenses (MIT / Apache 2.0 / Creative Commons). Review `LICENSE.txt` inside respective skill directories for specifics.
