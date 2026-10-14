# Multi-Tier SaaS Pricing Table Cards

> **Theme Identifier:** `pricing-tier-grid-cards`  
> **Category:** `cards`  
> **Original Source:** `cards/card-2`  
> **Aesthetic Tone:** High-Conversion SaaS / Transparent B2B  
> **Layout Pattern:** Responsive 3-Column Pricing Grid with Highlighted Featured Plan & SVG Checkmarks  
> **Complexity Level:** Medium  

---

## 1. Visual Essence & Aesthetic Direction

Clean light palette with bold blue accents (#4f97ff, #4087ed), prominent monthly billing typography, SVG checkmark list items, primary CTA button.

- **Color Palette:** `#f7f7f7`, `#121212`, `#4f97ff`, `#1e1e1e`, `#4087ed`
- **Typography & Font Pairing:** "Euclid Circular A", "Poppins", inherit
- **Craftsmanship & Aesthetics:** Avoids generic AI design cliches (such as plain purple gradients on stark white cards or unstyled system fonts). Every element is balanced with intentional negative space, clear visual hierarchy, and tactile feedback.

---

## 2. When to Choose This Theme (Agent Selection Guide)

A coding agent should select `pricing-tier-grid-cards` when encountering the following scenarios:

### Primary Triggers & Scenarios
- Pricing pages, upgrade paywalls, subscription tier selection for SaaS products.

### Ideal Product Types
- SaaS pricing pages
- Subscription checkout flows
- Membership tier selection
- Feature tier comparison

### When NOT to Choose (Anti-Patterns)
- User bio summaries
- Single product e-commerce cart items

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
