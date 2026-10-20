# Goku Dev Skills (goku-dev-skills)

> **Universal, Agent-Agnostic Intelligence & Production Workflow System for AI Coding Assistants**  
> Compatible with **Google Antigravity**, **Claude Code**, **Cursor**, **Windsurf**, and **OpenCode**.  
> Distributed from a single source of truth (`.agent/`) to multiple downstream microservices and web applications.

---

## 🌟 Overview

**Goku Dev Skills** is a battle-tested engineering and design intelligence system designed to elevate autonomous AI coding assistants into senior architects and meticulous craftspeople. It enforces strict architectural patterns, deterministic verification gates, rich design libraries, and zero-tolerance policies for code rot, AI-slop, and undocumented APIs.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          GOKU DEV SKILLS ECOSYSTEM                              │
├──────────────────────────────┬─────────────────────────────┬────────────────────┤
│   27 PRODUCTION SKILLS       │   19 QUALITY RULES          │ 55 COMPONENT THEMES│
│  Architecture · Design · QA  │  11 Deterministic Gates     │ Standalone HTML/CSS│
│  TDD · Backlog Ideas · Docker│  WCAG AA · i18n · Slop-Free │ Bespoke Design Docs│
└──────────────────────────────┴─────────────────────────────┴────────────────────┘
```

### Core Pillars
1. **27 Production-Grade Skills:** Spanning Spring Boot/Java backend architecture, Next.js / Vite SPA frontend engineering, WCAG-compliant design intelligence, Docker containerization, backlog idea evaluation (`my-idea`), and rigorous software engineering practices (TDD, deep module design, two-axis code reviews, systematic bug diagnosis).
2. **19 Enforced Quality Rules & 11 Verification Gates:** 11 deterministic Python test gates (API documentation, DB migrations, design anti-slop, theme contrast & WCAG AA, bundle budgets, unused imports, i18n key consistency) preventing code regression, plus the strict red feedback loop rule (`bug-diagnosis-enforcement.md`).
3. **Autonomous Backlog Idea Engine (`my-idea`):** Free-form idea backlog (`docs/idea/myidea.md`), autonomous re-rating against live project state, filtering of obsolete items, and zero-hallucination pipeline handoff to PRD/Sprint/TDD.
4. **Surgical Update Engine (`update`):** Updates *only* currently installed skills and rules. Never downloads uninstalled skills or unwanted component themes.
5. **Modular Profile-Based Architecture:** Install only what your tech stack needs — from ultra-lightweight backend setups (~2.5 MB) to minimal frontend (~5 MB) or fullstack architectures (~65 MB).
6. **55 Curated Component Themes:** Standalone, production-ready HTML/CSS UI components (sidebars, navbars, menus, parallax, logins, footers, cards, accordions) equipped with bespoke design rationale documents (`<theme-name>.design.md`).
7. **Automated Multi-Project Delivery Engine (`delivery.py`):** Propagates upstream changes downstream while preserving project-specific custom rules and validating SHA-256 integrity.

---

## ⚡ Quick Start & Installation

Install only the skills and rules tailored to your project's stack, avoiding unnecessary bloat:

### 1. Profile-Based Installation via `npx`

```bash
# ☕ Backend Profile (Java, Spring Boot, .NET, APIs, DB Migrations) — Ultra-lightweight (~2.5 MB, zero UI clutter)
npx goku-dev-skills init -p backend

# 🎨 Minimal Frontend Profile (React, Vite, Next.js, Tailwind, Zanaat Anti-slop) — Excludes 55 heavy themes (~5 MB)
npx goku-dev-skills init -p frontend -m

# 🌟 Full Frontend Profile (Includes all 55 HTML/CSS component themes) (~60 MB)
npx goku-dev-skills init -p frontend

# 🚀 Fullstack / All Profile (All 27 skills, 55 themes, 19 rules & 11 verification gates) (~65 MB)
npx goku-dev-skills init -p fullstack

# 🔍 Auto-Detect Stack (Inspects pom.xml, package.json, csproj and selects appropriate profile)
npx goku-dev-skills init --detect
```

### 2. Surgical Updates for Existing Workspaces (Zero-Bloat Sync)

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

### 3. Granular Skill & Theme Addition

```bash
# List all 27 available skills, profiles and 55 component themes
npx goku-dev-skills list

# Add a single skill into current workspace
npx goku-dev-skills add frontend-design

# Add a single component theme directly into your components folder
npx goku-dev-skills add theme sidebars/violet-minimal-sidebar
```

### 4. Multi-Agent & Platform Adaptation

Different AI coding assistants store rules and skills in different workspace locations. Use the `--agent` flag to target your preferred environment:

| AI Assistant / Tool | Command Example | Target Workspace Location |
| :--- | :--- | :--- |
| **Google Antigravity / OpenCode** | `npx goku-dev-skills init` | `.agent/skills/` & `.agent/rules/` |
| **Cursor** | `npx goku-dev-skills add <skill> --agent cursor` | `.cursor/rules/<skill>/` |
| **Claude Code** | `npx goku-dev-skills add <skill> --agent claude` | `.claude/skills/<skill>/` |
| **Windsurf** | `npx goku-dev-skills add <skill> --agent windsurf` | `.windsurf/rules/<skill>/` |
| **Custom Path** | `npx goku-dev-skills init --dest <path>` | Custom target directory |

---

## 💡 Autonomous Idea Backlog & Re-Rating (`my-idea`)

Developers frequently have creative, experimental, or visionary ideas that fall outside the active sprint or PRD scope. Storing them haphazardly causes scope creep or lost context. The **`my-idea`** skill provides a structured yet lightweight pool (`docs/idea/myidea.md`) where ideas live, get dynamically re-rated against live project state, and get seamlessly handed off to production.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MY-IDEA WORKFLOW LIFECYCLE                            │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │
                         [Developer / User Free-form Idea]
                         (Added to docs/idea/myidea.md)
                                       │
               ┌───────────────────────┴───────────────────────┐
               ▼                                               ▼
     [Autonomous Trigger]                             [User Explicit Prompt]
(Major sprint finished / No WIP)               ("fikirlerime bak", "review ideas")
               │                                               │
               └───────────────────────┬───────────────────────┘
                                       │
                        [Scan Current Project State]
                   (PRODUCT.md · SPRINT_PLAN · Live Code)
                                       │
                      [Re-Rating & Obsolete Elimination]
                   Formula: (Impact*0.4)+(Effort*0.3)+(Fit*0.3)
                   Obsolete marked: ⛔ [ELENDI - Neden]
                                       │
                         [Propose Top 3 Ranked Picks]
                         ("Hangisiyle ilerlemek istersin?")
                                       │
                        [Zero-Hallucination Pipeline]
                 1. PRD Sync        ──► `doc-coauthoring` / PRODUCT.md
                 2. Sprint Card     ──► `sprint-delivery-workflow` / SPRINT_PLAN.md
                 3. TDD Loop        ──► `tdd` (Red -> Green -> Refactor)
                 4. Clean Code      ──► `musgoku`, `codebase-design`
                 5. Pool Complete   ──► `docs/idea/myidea.md` marked ✅ [UYGULANDI]
```

### Simple Idea Format (`docs/idea/myidea.md`)

```markdown
### IDEA-001: Command Palette Quick Actions (Ctrl+K)
- **Durum:** 🎯 `[ONERILEN]`
- **Rating:** `8.5/10` (Etki: 9 | Efor: 8 | Uyum: 8)
- **Açıklama:** Top 5 frequent actions accessible via keyboard shortcut.
- **Değer / Gerekçe:** Speeds up power-user navigation by 2x.
- **Ajan Değerlendirmesi:** Ready to build using existing web-ide-ux-architect dialog.
```

### Status Badges
- 💡 `[YENI]` : Newly added raw idea awaiting assessment.
- 🎯 `[ONERILEN]` : High-scoring idea recommended for the next sprint.
- ⏳ `[ERTELENDI]` : Good idea, but deferred due to dependencies or early stage.
- ⛔ `[ELENDI - Reason]` : Obsolete, duplicated, or superseded (never deleted, archived with reason).
- ✅ `[UYGULANDI - Sprint/Date]` : Shipped and verified in the codebase.

### Automation Helper Script (`idea_manager.py`)

```bash
# List all ideas formatted in terminal
python .agent/skills/my-idea/scripts/idea_manager.py --list

# Filter active ideas and output top 3 ranked picks
python .agent/skills/my-idea/scripts/idea_manager.py --top 3

# Export machine-readable JSON for agents/CI
python .agent/skills/my-idea/scripts/idea_manager.py --top 3 --json

# Initialize docs/idea/myidea.md from template if missing
python .agent/skills/my-idea/scripts/idea_manager.py --init
```

---

## 🛠️ The 27 Shipped Skills

> [!TIP]
> ### 📑 Interactive Visual Skills Catalog (`skills-catalog.html`)
> For an interactive, searchable, and comprehensive visual guide of all 27 skills, prompt templates, trigger keywords, and configuration blueprints, open the included offline HTML catalog:
> - 🌐 **Direct File:** [`.agent/skills-catalog.html`](.agent/skills-catalog.html)
> - 🚀 **Quick Open (Browser):**
>   ```bash
>   # Windows
>   start .agent/skills-catalog.html
>   # macOS
>   open .agent/skills-catalog.html
>   # Linux
>   xdg-open .agent/skills-catalog.html
>   ```
> Includes dual view modes (**Card Grid** & **Compact Trackable Table** via `V`), instant fuzzy search (`/` or `Ctrl+K`), one-click prompt copying, and dark/light theme toggle (`T`).

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
| **`design`** | Creative Brief | Creative direction router, brand brief synthesis, and logo design specifications. |
| **`task-observer`** | Meta / Evolution| Observation logging, methodology distillation, continuous skill set refinement. |
| **`react-best-practices`** | React / Next | React 19 / Next.js performance optimizations, waterfall elimination, composition. |
| **`mock-asset-provider`** | UI Assets | Realistic placeholder assets, developer avatars, event imagery, CDN fallback pipeline. |
| **`onboarding-tour`** | Walkthrough | Guided interactive product tours and coachmarks (Driver.js / React Joyride). |
| **`diagnosing-bugs`** | Debugging / QA | 6-phase systematic debugging, falsifiable hypotheses, red verification loop, regression tests. |
| **`tdd`** | Code Quality | Test-driven development, red-before-green loop, tracer bullets, vertical slices, pre-agreed seams. |
| **`codebase-design`** | Architecture | Deep modules, narrow interfaces, complexity containment, deletion testing, architectural seams. |
| **`code-review`** | Code Quality | Two-axis review discipline: Martin Fowler code smells baseline vs spec fidelity & scope creep. |
| **`domain-modeling`** | Domain / Arch | Ubiquitous language, GLOSSARY.md domain dictionary maintenance, strict 3-criteria ADR threshold. |
| **`my-idea`** | Product / Ideas| Backlog idea pool evaluator (`docs/idea/myidea.md`), autonomous re-rating, top-3 picks & TDD/Sprint handoff. |

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
# Run 11/11 master distribution & regression test suite
python tests/run_all.py

# Run skill contract verification suite (11/11 OK)
cd .agent/skills/ui-ux-pro-max/scripts/tests
python -m unittest test_skill_contracts.py

# Run strict rule validation gate (19 rules, 11 gates)
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
