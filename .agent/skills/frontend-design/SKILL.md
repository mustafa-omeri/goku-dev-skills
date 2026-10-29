---
name: frontend-design
description: Karakterli, üretim kalitesinde web arayüzü kodu üretir; tipografi, renk, kompozisyon ve "generic AI tasarımı" kalıplarından kaçınma disiplini. `./themes/`, `./dashboard-theme/` ve `./component-themes/` (sidebar, login, navbar, card, footer) ile hazır referans sağlar. Tetikleyiciler: "/ui-polish", "arayüz yap", "sayfa tasarla", "şu daha iyi görünsün", "amatör görünüyor", "UI polish", "tasarımı düzelt", "[DESIGN-REFRESH]", "landing page", "dashboard tasarımı", "build a component", "looks generic". Tetiklenmez: veri katmanı ve mimari `musgoku`'ya aittir. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## The 4 Surface Modes: Match Ambition to Function

Scale design ambition to what visitor success looks like on the target surface:

- **Persuade (Landing Pages, Marketing, Campaigns, Pricing):** The visitor decides and acts; design is the product. Commit to a distinct visual world, rich typography (display + refined body pairing), real imagery, and one authored entrance moment. Generous negative space.
- **Operate (App UI, Dashboards, Tables, Settings, Tools):** The visitor completes a task. The tool must disappear into the workflow. Scanability, native expectations, and high information density outrank expression.
  * *Typography:* A single well-tuned Sans family across headings, buttons, and labels (never use display fonts in UI chrome). Fixed rem scale, tight ratio (1.125–1.2).
  * *Color:* Restrained palette with clear semantic status tokens (`hover`, `focus`, `active`, `disabled`, `loading`, `error`, `success`).
  * *Motion:* Quick transitions (150–250ms); NEVER use slow orchestrated page-load sequences.
  * *Interactions:* No reinventing standard affordances; modals only when disruption is strictly necessary.
- **Read (Docs, Guides, Technical Specs, Changelogs):** The visitor understands something. Structure for comprehension: 65–75ch prose line length, clear heading hierarchy, sticky table of contents (TOC), crisp code blocks with copy ergonomics.
- **Experience (Portfolios, Galleries, Showcases):** The visitor is inside the work itself. Minimal UI chrome; let the artifact lead from the first viewport.

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. **IMPORTANT: Use curated design themes and distinct color/component combinations. Search and inspect the `./themes` directory for palettes, `./dashboard-theme/` for dashboards, and `./component-themes/` for sidebars, navbars, menus, logins, footers, cards, accordions, and parallax. Regardless of the component or page, avoiding generic AI aesthetics is non-negotiable.**
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Responsive Viewport & Device Context**: Never treat mobile as merely a squeezed desktop. Design intentionally for 3 distinct ergonomic form factors: **Mobile** (< 768px: Thumb-Zone ergonomics, bottom action bar, min 44×44px touch targets, card lists, and adaptive bottom-sheet drawers instead of desktop modals), **Tablet** (768px–1024px: balanced 2-column grids, master-detail split-views, collapsible rail sidebars, touch-friendly hit areas without hover dependencies), and **Desktop** (> 1024px: multi-column dense information layouts, permanent sidebars, rich data tables, and hover micro-interactions).
- **The 4 Essential UX States**: Never ship an interface in only its static happy path. Always craft distinct, thoughtful treatments for **Loading** (MANDATORY Skeleton Screen UI mimicking the exact wireframe/cassette structure with zero layout shift; full-page/container spinners for data loading are strictly forbidden), **Empty** (clear iconography, engaging copy, and explicit CTA buttons like *"Create your first project"*), **Error** (inline actionable messaging with clear retry capabilities), and **Feedback** (immediate contextual confirmation toasts and optimistic updates).
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

## Curated Themes & Palette Selection (`./themes` Directory)

Similar to searching `./canvas-fonts` in `canvas-design` for typographic depth, **always search and inspect `./themes` directory for color combinations and aesthetic direction before styling any UI:**

> **Sahiplik:** Bu bölüm **düz HEX palet** için sahiptir (hızlı seçim, doğrudan
> Tailwind/CSS değişkeni). Üç katmanlı **token** üretimi gerekiyorsa sahibi
> `design-system`'dir; Tailwind/shadcn kurulumu `ui-styling`'in işidir. Aynı işi
> üç yerde yapma.

- **Curated Palette Cards**: The `./themes/` folder contains curated high-contrast color cards (`frontend-design-skill-theme-*.jpg`) providing intentional, masterfully paired HEX color palettes (e.g., Tiffany `#21F1A8` & Dark Gray `#171717`, True Pink `#FD1843` & Chill White `#FFF9FA`, Lime Sprout `#E4FD97` & Fresh Canopy `#2D3E2C`, etc.).
- **Dashboard Layout References**: The `./dashboard-theme/` folder contains 18 curated dashboard screenshots (`dashboard-theme-01.webp` → `dashboard-theme-18.webp`) plus a `README.md` guide. **When the user asks for a dashboard, always inspect this folder first** and borrow layout patterns (sidebar + topbar + card grid, KPI cards, tables, progress rings) instead of inventing a generic admin layout.
- **Curated Component Themes**: The `./component-themes/` folder contains 55 production-ready HTML/CSS themes across 8 core categories (sidebars, navbars, menus, parallax, logins, footers, cards, accordions). **When the user asks for a sidebar, navbar, login, footer, card, accordion, menu, or parallax, always inspect `./component-themes/` first.** Each theme folder contains its standalone working code and a dedicated `<theme-name>.design.md` detailing aesthetic tone, layout anatomy, agent selection criteria, and framework adaptation.
- **Zero-Friction CLI Bridges:**
  * Component Picker: `python .agent/skills/frontend-design/scripts/get_component.py --list` (or `--theme <name> --html` / `--type sidebars`)
  * Palette Picker: `python .agent/skills/frontend-design/scripts/get_palette.py --list` (or `--id <1-10> --format css`)

- **Zero-Friction CLI Bridges:**

  * Component Picker: `python .agent/skills/frontend-design/scripts/get_component.py --list` (or `--theme <name> --html` / `--type sidebars`)

  * Palette Picker: `python .agent/skills/frontend-design/scripts/get_palette.py --list` (or `--id <1-10> --format css`)
- **How to Use**:
  1. Before picking random colors or falling back to generic blues/purples, inspect the `./themes` folder.
  2. Select a theme card that matches the tone, mood, and brand requirements of the interface.
  3. Extract and map the exact primary, secondary, background, and accent colors into Tailwind classes or CSS variables (`--primary`, `--background`, `--foreground`, etc.).
  4. Ensure sharp contrast, readability, and WCAG accessibility standards across all components.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

# Frontend Design

Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the client. You can come up with one concrete subject, the design's audience, and the design's primary job, as a proposal. If there's any information in your memory about the client's preferences or context about what they're building, use that as a hint. The subject's industry, subject matter, materials, and vernacular are where distinctive visual choices come from — a design for a toy for girls aged 8–11 will be very aesthetically different from a dashboard for financial analysts. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is the first thing viewers will see. Open with the most characteristic thing in the subject's world, in the form that is most appropriate: a headline, an image, an animation, a live demo, an interactive moment, or other treatments. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the default treatment, so only use it if that's truly the best option.

Typography carries the personality of the page. You don't need a different typeface for display or headline text and body content: use one family or two, and if two, make them clearly distinct.

Choose your typefaces deliberately, not the default families you would reach for on any other project, and set a clear type scale following the default guidance of The Elements of Typographic Style with intentional weights, widths, and spacing. When type is used as a headline or visual element, use the type treatment itself as an active part of the design, not a neutral delivery vehicle for the content.

Default to line lengths of less than 80 characters. Serif typefaces can have slightly longer line lengths; give serif body text slightly more line-height than a sans-serif.

Avoid these default typographic treatments; they are the commonest tells of a generated page:

- Accenting just a single word or phrase in a headline, like putting one word in italic/bold or a different color.
- Using all caps for labels.
- Adding unnecessary typographic labels above content.

Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode useful information about the content rather than decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence — like a stepped process or a timeline. Before adding numbered markers, check the content really is a sequence.

Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment — one page-load sequence or one reveal — lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance.

## Process: plan, review against the brief, build, critique

### The Three Waves of AI Slop & The "Avoidance Aesthetic" Trap

AI-generated design clusters around recurring defaults that read as generic or synthetic:

1. **First Wave (2023–2024):** Violet/indigo gradients on buttons and hero glows, gradient-filled text, glassmorphism panels (backdrop-blur), emoji bullets, and rows of three identical icon-topped cards.
2. **Second Wave (2025):** Tiny tracked uppercase eyebrow labels above every heading, pill badges ("New", "Beta"), bento grids with uniform border-radius, near-black backgrounds with neon accents, and floating pill navigations.
3. **Third Wave (2025–2026 — The "Editorial Cosplay" Trap):** The remedy published for earlier waves was "warm it up and make it editorial." This became the newest tell:
   - Yellow-cream background (near `#F4F1EA`) paired with terracotta/rust/clay accents (near `#D97757` — the AI assistant brand look).
   - Oversized italic serif display text used as an artificial shortcut to "premium."
   - Broadsheet cosplay: hairline rules (1px borders everywhere), zero border-radius, and dense newspaper-like columns.
   - Performative micro-labels: "Field notes", "Quietly trusted by", "On our desks", coordinates, or local time widgets.

> **⛔ The "Avoidance Aesthetic" Danger:** Removing ornaments, cards, and rules is only half the job. A page that has lost its cards and gained nothing in return reads as empty, cold, and underbuilt. Never fill empty space with another ornament; fill it with **scale** (type set larger), **flat fields of tone**, **real cultural pictures of the subject's world**, and **complete, uncompressed content**.

### Laws of Visual Craft & Copywriting

1. **Two-Line Headline Rule:** Every headline (`h1`–`h6` and the main hero line) must fit in **two lines or fewer at every viewport width** (desktop, tablet, mobile). Median headline length on top-tier gallery sites is ~5 words and ~32 characters. Cut words first; widen measure second; reduce font size only as a last resort.
2. **Statements vs. Headlines:** Large intro sentences or quotes are marked up as `<p>` or `<blockquote>`, stay at statement size (desktop ≤36px, mobile ≤24px), and run to about 25–30 words (3 lines). Larger than that, it reads as a bloated headline.
3. **Typeface Ceiling:** Two font families at most (one display, one body); often one family is enough. **Monospace is strictly forbidden outside real code blocks** (`<pre>/<code>`).
4. **Surfaces & Separation:** No box-shadows on elements at rest (shadows belong only on floating layers: dialogs, menus, sticky bars). No hairline divider lines; separate sections using generous vertical space (120–220px on desktop), filled shapes, or subtle tone steps.
5. **Section Variety & Claim-Proof Flow:** Break the stock template sequence (*hero → logos → 3 feature cards → testimonial → pricing → CTA*). Order sections by claims with their proof. Neighbouring sections must not share the same layout geometry.
6. **No Eyebrows or Gimmicks:** Do not place small uppercase labels or pill chips above titles. Say the message directly in the headline or the supporting sentence.

## Craft Floor: Mechanical Checks & Hard Refusals

Apply these mechanical checks on every built render. When building, commit to these non-negotiables:

### 1. Hard Refusals (Anti-Slop Redlines)
- **No Nested Cards:** Cards inside cards are strictly prohibited. Structure hierarchy with flat surface tones, generous whitespace, or subtle dividers.
- **No Gradient Text:** Text with background clip gradients (`bg-clip-text text-transparent`) is prohibited. Emphasis must come from typography scale, weight, or sharp contrast.
- **No Eyebrow / Kicker Labels:** Small tracked uppercase labels or pill chips above titles ("WHY CHOOSE US", "FEATURE") are banned. Let the headline speak for itself.
- **No Colored Side-Stripe Borders:** 3-4px thick colored borders (`border-l-4`) on cards, list items, or alerts are banned.
- **No Hard Offset Shadows:** Zero-blur block shadows (`box-shadow: 4px 4px 0`) are banned unless the project explicitly commits to neobrutalism. Shadows must carry soft blur and natural offset.
- **Single Elevation Source:** Declare elevation once: either a subtle border OR a soft shadow. A 1px border under a wide soft shadow is a "ghost card". Card radius stays between 12–16px (`rounded-xl` to `rounded-2xl`).
- **No Unicode Glyphs as Icons:** Never substitute emojis or raw Unicode characters for iconography. Use consistent SVG icons from a single library (e.g., Lucide).
- **No Sketchy / Doodle SVGs:** SVG scenes pretending to be hand-drawn doodles (`feTurbulence`, sketchy outlines) look amateurish. Use crisp vector geometry or authentic photography.

### 2. Mechanical Checks (Verify On Render)
- **Contrast & Hue Tinting:** Body/placeholder text ≥ 4.5:1, large headings ≥ 3:1. On colored backgrounds, secondary text must be tinted with that surface's hue; never use raw, un-tinted gray.
- **Themed Browser Surfaces:** The parts you didn't draw still carry the brand. Theme them from the palette:
  - Text selection: `::selection { background: var(--accent); color: var(--accent-foreground); }`
  - Caret color: `caret-color: var(--primary);`
  - Scrollbars: `scrollbar-color: var(--border) transparent;`
  - Keyboard focus: visible `focus-visible:ring-2` with `ring-offset-2`
  - Tabular figures: `font-variant-numeric: tabular-nums` for all stats, timestamps, prices, and tables.
  - Underline offset: `underline-offset-4` on text links.
- **Spacing Rhythm:** Tight groups, generous separation (`gap-2` inside items, `gap-8` to `gap-16` between sections). Headings always have more margin above than below (`mt-8 mb-3`).
- **Typography Floor:** Body measure constrained to 65–75ch (`max-w-prose` / `max-w-2xl`), display max 6rem, tracking floor clamped at -0.04em, and balanced heading wraps (`text-wrap: balance`).

### Real Cultural Imagery & Open Collections (`assets.mjs`)

Real pictures of the subject's world beat generic placeholders, icon cards, or abstract blobs. When a project lacks its own photography, do not default to empty boxes or stock photos of smiling people at laptops. Use open museum and archival collections (Openverse, Wikimedia Commons, The Met Museum, Art Institute of Chicago, NASA, Prelinger Archives).

Use the integrated zero-dependency asset discovery engine:

```bash
# Search open collections for commercial-safe (CC0, Public Domain, CC BY, CC BY-SA) imagery:
node .agent/skills/frontend-design/scripts/assets.mjs "<sorgu>" [--orientation landscape|portrait|square] [--limit 5]

# Download selected asset into project and record attribution:
node .agent/skills/frontend-design/scripts/assets.mjs --get <ref> --to assets

# Print required credit lines for the page footer and handoff report:
node .agent/skills/frontend-design/scripts/assets.mjs --credits --to assets
```

- **Quality floor for public pages:** At least 4 real pictures or genuine interface fragments (`data-ui`). Archival maps, architectural photos, engravings, material textures, or historical postcards ground the page in reality.
- All found pictures must carry transparent attribution in the footer via `--credits`.

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected, visually accessible, harmonious color palettes. Critique your own work as you build, taking screenshots to review if your environment supports it — a picture is worth 1000 tokens (see `references/vision-to-component-patterns.md` for translating screenshots/mockups to components). Consider Chanel's advice: before leaving the house, take a look in the mirror and remove one accessory.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand and use. They are design content, not decoration. Bring the same intentionality and minimalism to copywriting that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's perspective. Name things by what users will understand in simple language, not by how the system is built. A user manages notifications, not webhook config. Describe what something is or does in plain terms rather than selling it. Being specific and legible to new users is always better than being clever.

Use active voice as default. A CTA says exactly what happens when it is used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the tone conversational: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each written element do exactly one job.