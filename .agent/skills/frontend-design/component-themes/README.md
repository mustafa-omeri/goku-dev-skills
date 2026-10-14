# Component Themes — Visual Reference & Production Library

> **Single Source of Truth for Web UI Components**  
> Under `frontend-design` Skill (`.agent/skills/frontend-design/component-themes/`).  
> Contains **55 curated, production-grade HTML/CSS component themes** across 8 core UI categories.

---

## ⛔ Agent Mandate: Inspect Here First!

Whenever a user requests a frontend component (such as a **sidebar**, **navbar**, **login**, **footer**, **card**, **accordion**, **menu**, or **parallax**):
1. **DO NOT invent generic, AI-slop layouts** or fall back to default, repetitive templates.
2. **ALWAYS inspect this directory first** (`.agent/skills/frontend-design/component-themes/`).
3. Select the theme whose aesthetic direction and interaction model best fit the project requirements.
4. Read that theme's dedicated design document (`<theme-name>.design.md`) to extract palette, layout model, and micro-interactions.
5. Port the CSS and semantic DOM into the user's technology stack (Tailwind CSS, shadcn/ui, React, Vite SPA).

---

## Component Themes Directory Index

| Category | Title | Count | Description |
| :--- | :--- | :--- | :--- |
| [`sidebars/`](./sidebars/) | **Sidebar Navigation Themes** | 8 themes | Curated collection of 8 production-grade sidebar navigation themes. When a coding agent is asked to build or refactor a sidebar, navigation drawer, or application shell, it must inspect this catalog first. |
| [`navbars/`](./navbars/) | **Navbar & Top/Bottom Bar Themes** | 1 themes | Modern navbar and floating pill navigation themes with active kinetic sliding markers. |
| [`menus/`](./menus/) | **Menu & Navigation Overlay Themes** | 1 themes | Fullscreen overlay menus, mobile drawer menus, and staggered animation navigation themes. |
| [`parallax/`](./parallax/) | **Parallax & Scrolling Depth Themes** | 2 themes | Pure CSS depth and storytelling parallax layouts with multi-layer background effects. |
| [`accordions/`](./accordions/) | **Accordion & Expandable Feature Themes** | 2 themes | Horizontal and interactive expandable accordion galleries for team rosters, feature comparisons, and portfolio showcases. |
| [`cards/`](./cards/) | **Card Component Themes** | 10 themes | 10 curated card component themes covering pricing grids, interactive 3D flip metrics, job listings, bio widgets, travel cards, and article previews. |
| [`logins/`](./logins/) | **Login & Authentication Themes** | 16 themes | 16 diverse authentication screen themes ranging from minimalist glassmorphic cards and split-screen hero layouts to Web3 neon and dual-mode sliding auth switchers. |
| [`footers/`](./footers/) | **Footer & CTA Closing Themes** | 15 themes | 15 distinctive footer themes featuring animated SVG waves, SaaS conversion CTA banners, lead-gen consultation forms, and enterprise sitemaps. |

---

## Design Document Architecture (`<theme-name>.design.md`)

Each theme directory contains its complete, standalone HTML/CSS code and assets, alongside a dedicated design document named `<theme-name>.design.md`:

```
component-themes/
├── sidebars/
│   ├── violet-minimal-sidebar/
│   │   ├── index.html
│   │   ├── styles.css
│   │   ├── logo.svg
│   │   └── violet-minimal-sidebar.design.md  <-- Read this!
│   └── README.md
├── logins/
│   ├── floating-orb-minimal-login/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── floating-orb-minimal-login.design.md
│   └── README.md
└── README.md
```

Each design document provides:
- **Visual Essence & Aesthetic Direction:** Color tokens, font pairings, negative space balance.
- **Agent Selection Guide:** Exact prompts, triggers, ideal product types, and anti-patterns.
- **Structural Anatomy:** Semantic DOM structure and CSS Flexbox/Grid model.
- **Interactions & States:** Hover, active, focus states, and animation timings.
- **Framework Adaptation:** Mapping to React, Tailwind utility classes, and shadcn primitives.
