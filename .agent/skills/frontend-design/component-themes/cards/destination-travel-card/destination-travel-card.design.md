# Destination Travel & Experience Card

> **Theme Identifier:** `destination-travel-card`  
> **Category:** `cards`  
> **Original Source:** `cards/card-8`  
> **Aesthetic Tone:** Warm Editorial / Lifestyle Exploration  
> **Layout Pattern:** Editorial Image Header Card with Category Badge, Location Headline & Action Button  
> **Complexity Level:** Low-to-Medium  

---

## 1. Visual Essence & Aesthetic Direction

Warm cream accent background (#ffe7ce), full-bleed cover image header, pill tags ('Economy'), Material Symbols action buttons, high readability body copy.

- **Color Palette:** `#ffe7ce`, `#a4a4a4`, `#2b2d29`, `#ffffff`, `rgb(0 0 0 / 8%)`, `rgb(0 0 0 / 0%)`
- **Typography & Font Pairing:** "Euclid Circular B", "Poppins", inherit
- **Craftsmanship & Aesthetics:** Avoids generic AI design cliches (such as plain purple gradients on stark white cards or unstyled system fonts). Every element is balanced with intentional negative space, clear visual hierarchy, and tactile feedback.

---

## 2. When to Choose This Theme (Agent Selection Guide)

A coding agent should select `destination-travel-card` when encountering the following scenarios:

### Primary Triggers & Scenarios
- Travel booking platforms, real estate discovery, city guides, and lifestyle blog cards.

### Ideal Product Types
- Travel discovery sites
- Real estate listings
- Experience bookings
- Lifestyle magazines

### When NOT to Choose (Anti-Patterns)
- Technical code snippets
- Financial statement tables

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
