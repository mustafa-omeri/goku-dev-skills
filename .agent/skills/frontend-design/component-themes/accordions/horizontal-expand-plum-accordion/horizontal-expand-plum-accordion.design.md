# Horizontal Expandable Plum Team Accordion

> **Theme Identifier:** `horizontal-expand-plum-accordion`  
> **Category:** `accordions`  
> **Original Source:** `accordions/accordion-1`  
> **Aesthetic Tone:** Rich Plum Creative / Vibrant Team Showcase  
> **Layout Pattern:** Horizontal Flex Accordion (Hovering expands card width from slim slit to full portrait)  
> **Complexity Level:** Low-to-Medium  

---

## 1. Visual Essence & Aesthetic Direction

Deep plum backdrop (#412868), smooth flex-basis / flex-grow expansion, overlay caption revealing role and name with subtle opacity delay, high-resolution portrait imagery.

- **Color Palette:** `#412868`, `#fff`, `#02022e`, `rgb(0 0 0 / 70%)`, `rgb(255 255 255 / 0%)`
- **Typography & Font Pairing:** "Euclid Circular A", "Poppins"
- **Craftsmanship & Aesthetics:** Avoids generic AI design cliches (such as plain purple gradients on stark white cards or unstyled system fonts). Every element is balanced with intentional negative space, clear visual hierarchy, and tactile feedback.

---

## 2. When to Choose This Theme (Agent Selection Guide)

A coding agent should select `horizontal-expand-plum-accordion` when encountering the following scenarios:

### Primary Triggers & Scenarios
- Team member galleries, portfolio project showcases, and feature highlights requiring high visual engagement on desktop.

### Ideal Product Types
- About Us team rosters
- Creative agency feature cards
- Customer testimonial showcases
- Product collection previews

### When NOT to Choose (Anti-Patterns)
- Standard FAQ text accordions
- Mobile devices without horizontal touch scroll / tap support

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
