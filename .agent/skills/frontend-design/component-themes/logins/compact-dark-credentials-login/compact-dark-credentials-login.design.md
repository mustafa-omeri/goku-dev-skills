# Compact Dark Credentials Authentication Card

> **Theme Identifier:** `compact-dark-credentials-login`  
> **Category:** `logins`  
> **Original Source:** `logins/login-2`  
> **Aesthetic Tone:** Technical Dark / Focused Minimalist  
> **Layout Pattern:** Compact Centered Dark Box with High-Contrast Typography & Credentials Input  
> **Complexity Level:** Low  

---

## 1. Visual Essence & Aesthetic Direction

High-contrast dark canvas, minimal borders, subtle focus rings, straightforward username/password fields.

- **Color Palette:** `#5d0dde`, `#f9f9f9`, `rgb(0 0 0 / 35%)`, `rgb(24 14 56 / 44%)`, `rgb(255 255 255 / 38%)`, `rgb(255 255 255 / 96%)`
- **Typography & Font Pairing:** "Euclid Circular A", inherit
- **Craftsmanship & Aesthetics:** Avoids generic AI design cliches (such as plain purple gradients on stark white cards or unstyled system fonts). Every element is balanced with intentional negative space, clear visual hierarchy, and tactile feedback.

---

## 2. When to Choose This Theme (Agent Selection Guide)

A coding agent should select `compact-dark-credentials-login` when encountering the following scenarios:

### Primary Triggers & Scenarios
- Developer consoles, CLI companion web portals, and dark-theme admin dashboards.

### Ideal Product Types
- Developer portals
- Admin console login
- Internal tools
- Dark UI systems

### When NOT to Choose (Anti-Patterns)
- Consumer retail apps with social logins
- Warm playful brands

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
