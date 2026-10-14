# Parallax & Scrolling Depth Themes

Pure CSS depth and storytelling parallax layouts with multi-layer background effects.

## Decision Matrix & Selection Catalog

When requested to create or update a **parallax**, match the user's intent to one of the themes below:

| Theme Identifier | Design Document | Aesthetic Tone | Complexity | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| [`split-section-story-parallax`](./split-section-story-parallax/index.html) | [Split-Section Storytelling Parallax](./split-section-story-parallax/split-section-story-parallax.design.md) | Editorial Storytelling / Showcase Presentation | Medium | Product introduction pages, company mission manifestos, and portfolio case studies that guide readers through alternating visual chapters. |
| [`multi-layer-pure-css-parallax`](./multi-layer-pure-css-parallax/index.html) | [Multi-Layer Pure CSS Depth Parallax](./multi-layer-pure-css-parallax/multi-layer-pure-css-parallax.design.md) | High-Impact Cinematic / Bold Visual Experience | Medium | Event pages, immersive landing pages, and creative showcases needing high-impact visual depth without JavaScript performance overhead. |

## How an Agent Uses This Directory

1. **Understand Intent:** Clarify product tone, density requirements, and brand character.
2. **Review Design Doc:** Open the corresponding `<theme-name>.design.md` file to inspect color variables, typography, and layout anatomy.
3. **Inspect Working Code:** Check `index.html` and `styles.css` inside the theme folder to examine exact classes, flex/grid properties, and keyframe transitions.
4. **Adapt to Framework:** Port the CSS patterns and semantic DOM into React / Vite / Tailwind / shadcn as outlined in Section 5 of the design doc.
