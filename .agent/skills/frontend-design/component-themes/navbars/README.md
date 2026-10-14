# Navbar & Top/Bottom Bar Themes

Modern navbar and floating pill navigation themes with active kinetic sliding markers.

## Decision Matrix & Selection Catalog

When requested to create or update a **navbar**, match the user's intent to one of the themes below:

| Theme Identifier | Design Document | Aesthetic Tone | Complexity | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| [`floating-pill-marker-navbar`](./floating-pill-marker-navbar/index.html) | [Floating Pill Navbar with Sliding Active Marker](./floating-pill-marker-navbar/floating-pill-marker-navbar.design.md) | Modern Minimalist / Fluid Interactive | Medium | Top or bottom floating app navigation, mobile web app tabs, and modern minimalist web products. |

## How an Agent Uses This Directory

1. **Understand Intent:** Clarify product tone, density requirements, and brand character.
2. **Review Design Doc:** Open the corresponding `<theme-name>.design.md` file to inspect color variables, typography, and layout anatomy.
3. **Inspect Working Code:** Check `index.html` and `styles.css` inside the theme folder to examine exact classes, flex/grid properties, and keyframe transitions.
4. **Adapt to Framework:** Port the CSS patterns and semantic DOM into React / Vite / Tailwind / shadcn as outlined in Section 5 of the design doc.
