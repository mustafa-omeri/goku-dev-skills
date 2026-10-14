# Horizontal Expandable Dark Slate Accordion

> **Theme Identifier:** `horizontal-expand-dark-accordion`  
> **Category:** `accordions`  
> **Original Source:** `accordions/accordion-2`  
> **Aesthetic Tone:** Sleek Dark Tech / Modern Corporate  
> **Layout Pattern:** Horizontal Flex Accordion on Deep Slate/Black Canvas with Translucent PNG Artwork  
> **Complexity Level:** Low-to-Medium  

---

## 1. Visual Essence & Aesthetic Direction

Deep slate background (#0a0f14), clean border styling, transparent PNG image support, smooth 0.3s CSS easing, typography overlay.

- **Color Palette:** `#0a0f14`, `#fff`, `#02022e`, `rgb(0 0 0 / 70%)`, `rgb(255 255 255 / 0%)`
- **Typography & Font Pairing:** "Euclid Circular A", "Poppins"
- **Craftsmanship & Aesthetics:** Avoids generic AI design cliches (such as plain purple gradients on stark white cards or unstyled system fonts). Every element is balanced with intentional negative space, clear visual hierarchy, and tactile feedback.

---

## 2. When to Choose This Theme (Agent Selection Guide)

A coding agent should select `horizontal-expand-dark-accordion` when encountering the following scenarios:

### Primary Triggers & Scenarios
- Tech company leadership showcases, digital art collections, and dark-themed feature comparisons.

### Ideal Product Types
- Tech leadership galleries
- Gaming character rosters
- Service pillar displays
- Dark-mode feature walkthroughs

### When NOT to Choose (Anti-Patterns)
- FAQ question/answer text lists
- Vertical document accordions

---

## 3. Structural Anatomy & Layout

### DOM Architecture
The component is structured with semantic HTML5 elements:
- Root container: `.page`, `.card`, or semantic tags (`<aside>`, `<nav>`, `<footer>`, `<main>`).
- Primary interaction area: structured flexbox/grid containers housing navigation links, action triggers, or media slots.
- Informational & metadata section: profile cards, badges, and secondary breadcrumbs.

### CSS Box Model & Grid
- Uses modern CSS Flexbox and CSS Grid layout techniques.
- Container sizing and spacing follow proportional rem/px scale with careful attention to touch targets (minimum 44x44px for action items).
- Fully responsive across desktop, tablet, and mobile viewports.

---

## 4. Interaction, States & Micro-Animations

- **Hover States:** Subtle background shifts, transform scaling, and border color adjustments provide tactile feedback.
- **Active / Focus Indicators:** Keyboard-accessible focus rings and active indicator pills or markers clarify spatial orientation.
- **Motion & Easing:** Transitions use smooth easing curves (0.2s - 0.4s ease-in-out) to deliver a polished, production-grade feel without distracting latency.

---

## 5. Modern Framework Adaptation Guide

### React / Vite SPA Porting
1. Convert the static HTML into a reusable React functional component.
2. Replace static attributes (`class` → `className`, `onclick` → `onClick`).
3. Convert inline SVG elements into React SVG components or standard Lucide / Phosphor icons.
4. Extract colors and borders into Tailwind CSS utility classes or CSS variables (`--primary`, `--background`, `--card`).

### Shadcn / Tailwind Integration
- **Container:** Map wrapper classes to Tailwind equivalents (e.g. `bg-background text-foreground rounded-2xl shadow-sm border border-border`).
- **Typography:** Map font sizes and weights to Tailwind classes (`text-sm font-medium text-muted-foreground`).
- **Interactive Buttons:** Utilize shadcn `Button` or custom button variants (`variant="ghost"`, `variant="outline"`).

### Accessibility (a11y)
- Ensure all icon buttons have accessible `aria-label` attributes.
- Maintain a minimum WCAG AA contrast ratio of 4.5:1 between text and background surfaces.
- Support standard keyboard navigation (`Tab`, `Enter`, `Space`, `Escape`).
