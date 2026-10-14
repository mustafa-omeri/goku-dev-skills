# Expandable Summary & Detail Metric Card

> **Theme Identifier:** `expandable-summary-metric-card`  
> **Category:** `cards`  
> **Original Source:** `cards/card-10`  
> **Aesthetic Tone:** Analytical Modern / Interactive Summary  
> **Layout Pattern:** Accordion-Style Interactive Summary Card Flipping or Expanding into Detail Mode  
> **Complexity Level:** Medium  

---

## 1. Visual Essence & Aesthetic Direction

Dual front/back content toggle, clean neutral styling with vivid blue and coral accents (#3b82f6, #e56363), header action trigger.

- **Color Palette:** `#f7f7f7`, `#1a1c22`, `#2d2e40`, `#3b82f6`, `#e56363`, `#fea`
- **Typography & Font Pairing:** "Euclid Circular B", "Poppins"
- **Craftsmanship & Aesthetics:** Avoids generic AI design cliches (such as plain purple gradients on stark white cards or unstyled system fonts). Every element is balanced with intentional negative space, clear visual hierarchy, and tactile feedback.

---

## 2. When to Choose This Theme (Agent Selection Guide)

A coding agent should select `expandable-summary-metric-card` when encountering the following scenarios:

### Primary Triggers & Scenarios
- Financial statement cards, order summaries, and metric inspection panels.

### Ideal Product Types
- Financial summaries
- Order tracking cards
- Health/fitness activity metrics
- Subscription overview

### When NOT to Choose (Anti-Patterns)
- Simple static hero banners
- Image-only galleries

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
