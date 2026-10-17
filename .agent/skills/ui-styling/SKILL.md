---
name: ui-styling
description: Tailwind CSS ve shadcn/ui'nin kod katmanı: bileşen ekleme, utility sınıfları, responsive düzen, dark mode, erişilebilir bileşen deseni, `tailwind.config` üretimi. Tetikleyiciler: "tailwind", "shadcn", "dark mode ekle", "responsive yap", "bileşen stili", "tailwind config", "shadcn component", "accessible dialog". Tetiklenmez: token üretimi `design-system`, estetik yönelim `frontend-design`, ölçüsüz görsel sanat `canvas-design` aittir. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
argument-hint: "[component or layout]"
license: MIT
metadata:
  author: claudekit
  version: "1.0.0"
---

# UI Styling Skill

Comprehensive skill for the code layer of beautiful, accessible user interfaces: shadcn/ui components and Tailwind CSS utility styling. Visual art (canvas/poster) and design-token generation belong to other skills.

## Reference

- shadcn/ui: https://ui.shadcn.com/llms.txt
- Tailwind CSS: https://tailwindcss.com/docs

## When to Use This Skill

Use when:
- Building UI with React-based frameworks (Next.js, Vite, Remix, Astro)
- Implementing accessible components (dialogs, forms, tables, navigation)
- Styling with utility-first CSS approach
- Creating responsive, mobile-first layouts
- Implementing dark mode and theme customization
- Building design systems with consistent tokens
- Generating visual designs, posters, or brand materials
- Rapid prototyping with immediate visual feedback
- Adding complex UI patterns (data tables, charts, command palettes)

## Core Stack

### Component Layer: shadcn/ui
- Pre-built accessible components via Radix UI primitives
- Copy-paste distribution model (components live in your codebase)
- TypeScript-first with full type safety
- Composable primitives for complex UIs
- CLI-based installation and management

### Styling Layer: Tailwind CSS
- Utility-first CSS framework
- Build-time processing with zero runtime overhead
- Mobile-first responsive design
- Consistent design tokens (colors, spacing, typography)
- Automatic dead code elimination

### Visual Design Layer: Canvas

Canvas felsefesinin sahibi bu skill **değildir**. Ölçüsüz görsel sanat (poster,
manifesto, `.png`/`.pdf` çıktı) ve font seti için `canvas-design` skill'ini aç.

## Kapsam Sınırı

| Konu | Sahip |
|------|-------|
| Tailwind/shadcn yardımı, dark mode, responsive, a11y deseni | **bu skill** |
| Estetik yönelim, AI-slop kaçınma, kod disiplini | `frontend-design` |
| Token üretimi (primitive → semantic → component) | `design-system` |
| Stil/palet/UX önerisi (aranabilir veri) | `ui-ux-pro-max` |
| Ölçüsüz görsel sanat + font seti | `canvas-design` |

Bu skill **token üretmez** — yalnızca tüketir ve Tailwind/shadcn tarafını kurar.

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `.agent/skills/ui-styling/scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Resolve the full path from that directory and keep the working directory at the project root — the scripts read and write project files such as `tailwind.config.js`, `src/index.css` or `components.json` relative to it.

## Quick Start

### Component + Styling Setup

**Install shadcn/ui with Tailwind:**
```bash
npx shadcn@latest init
```

CLI prompts for framework, TypeScript, paths, and theme preferences. This configures both shadcn/ui and Tailwind CSS.

**Add components:**
```bash
npx shadcn@latest add button card dialog form
```

**Use components with utility styling:**
```tsx
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export function Dashboard() {
  return (
    <div className="container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Analytics</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">View your metrics</p>
          <Button variant="default" className="w-full">
            View Details
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
```

### Alternative: Tailwind-Only Setup

**Vite projects:**
```bash
npm install -D tailwindcss @tailwindcss/vite
```

```javascript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default { plugins: [tailwindcss()] }
```

```css
/* src/index.css */
@import "tailwindcss";
```

## Component Library Guide

**Comprehensive component catalog with usage patterns, installation, and composition examples.**

See: `references/shadcn-components.md`

Covers:
- Form & input components (Button, Input, Select, Checkbox, Date Picker, Form validation)
- Layout & navigation (Card, Tabs, Accordion, Navigation Menu)
- Overlays & dialogs (Dialog, Drawer, Popover, Toast, Command)
- Feedback & status (Alert, Progress, Skeleton)
- Display components (Table, Data Table, Avatar, Badge)

## Theme & Customization

**Theme configuration, CSS variables, dark mode implementation, and component customization.**

See: `references/shadcn-theming.md`

Covers:
- Dark mode setup with next-themes
- CSS variable system
- Color customization and palettes
- Component variant customization
- Theme toggle implementation

## Accessibility Patterns

**ARIA patterns, keyboard navigation, screen reader support, and accessible component usage.**

See: `references/shadcn-accessibility.md`

Covers:
- Radix UI accessibility features
- Keyboard navigation patterns
- Focus management
- Screen reader announcements
- Form validation accessibility

## Tailwind Utilities

**Core utility classes for layout, spacing, typography, colors, borders, and shadows.**

See: `references/tailwind-utilities.md`

Covers:
- Layout utilities (Flexbox, Grid, positioning)
- Spacing system (padding, margin, gap)
- Typography (font sizes, weights, alignment, line height)
- Colors and backgrounds
- Borders and shadows
- Arbitrary values for custom styling

## Responsive Design

**Mobile-first breakpoints, responsive utilities, and adaptive layouts.**

See: `references/tailwind-responsive.md`

Covers:
- Mobile-first approach
- Breakpoint system (sm, md, lg, xl, 2xl)
- Responsive utility patterns
- Container queries
- Max-width queries
- Custom breakpoints

## Tailwind Customization

**Config file structure, custom utilities, plugins, and theme extensions.**

See: `references/tailwind-customization.md`

Covers:
- @theme directive for custom tokens
- Custom colors and fonts
- Spacing and breakpoint extensions
- Custom utility creation
- Custom variants
- Layer organization (@layer base, components, utilities)
- Apply directive for component extraction

## Visual Design System

Canvas felsefesi bu skill'in kapsamı dışındadır — sahibi `canvas-design`'dır
(`references/canvas-design-system.md` burada **kopyalanmaz**).

Bu skill'in görsel tarafta durduğu yer: Tailwind/shadcn ile ekranda nasıl
görüneceği. Felsefe ve ölçüsüz kompozisyon isteniyorsa `canvas-design`'i aç.

## Utility Scripts

**Python automation for component installation and configuration generation.**

### shadcn_add.py
Add shadcn/ui components with dependency handling:
```bash
python scripts/shadcn_add.py button card dialog
```

### tailwind_config_gen.py
Generate tailwind.config.js with custom theme:
```bash
python scripts/tailwind_config_gen.py --colors brand:blue --fonts display:Inter
```

The generator refuses to create or replace a config when any sibling
`tailwind.config.js`, `.cjs`, `.mjs`, or `.ts` file already exists. Review the
reported config first, then pass `--force` only when the competing output is
intentional:
```bash
python scripts/tailwind_config_gen.py --colors brand:blue --force
```

## Best Practices

1. **Component Composition**: Build complex UIs from simple, composable primitives
2. **Utility-First Styling**: Use Tailwind classes directly; extract components only for true repetition
3. **Mobile-First Responsive**: Start with mobile styles, layer responsive variants
4. **Accessibility-First**: Leverage Radix UI primitives, add focus states, use semantic HTML
5. **Design Tokens**: Use consistent spacing scale, color palettes, typography system
6. **Dark Mode Consistency**: Apply dark variants to all themed elements
7. **Performance**: Leverage automatic CSS purging, avoid dynamic class names
8. **TypeScript**: Use full type safety for better DX
9. **Visual Hierarchy**: Let composition guide attention, use spacing and color intentionally
10. **Expert Craftsmanship**: Every detail matters - treat UI as a craft

## Reference Navigation

**Component Library**
- `references/shadcn-components.md` - Complete component catalog
- `references/shadcn-theming.md` - Theming and customization
- `references/shadcn-accessibility.md` - Accessibility patterns

**Styling System**
- `references/tailwind-utilities.md` - Core utility classes
- `references/tailwind-responsive.md` - Responsive design
- `references/tailwind-customization.md` - Configuration and extensions

**Visual Design** (farklı skill — `canvas-design`)
- `canvas-design/SKILL.md` - Design philosophy, manifesto ve canvas üretimi

**Automation**
- `scripts/shadcn_add.py` - Component installation
- `scripts/tailwind_config_gen.py` - Config generation

## Common Patterns

**Form with validation:**
```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export function LoginForm() {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" }
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-6">
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" className="w-full">Sign In</Button>
      </form>
    </Form>
  )
}
```

**Responsive layout with dark mode:**
```tsx
<div className="min-h-screen bg-white dark:bg-gray-900">
  <div className="container mx-auto px-4 py-8">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Content
          </h3>
        </CardContent>
      </Card>
    </div>
  </div>
</div>
```

**Adaptive Responsive Dialog (Desktop: Dialog ↔ Mobile: Bottom Sheet / Drawer):**
```tsx
import * as React from "react"
import { useMediaQuery } from "@/hooks/use-media-query" // window.matchMedia('(min-width: 768px)')
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerTrigger } from "@/components/ui/drawer"
import { Button } from "@/components/ui/button"

export function AdaptiveModal({ children, title, triggerText }: { children: React.ReactNode, title: string, triggerText: string }) {
  const [open, setOpen] = React.useState(false)
  const isDesktop = useMediaQuery("(min-width: 768px)")

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild><Button>{triggerText}</Button></DialogTrigger>
        <DialogContent className="sm:max-w-lg rounded-2xl max-h-[85dvh] overflow-y-auto">
          <DialogHeader><DialogTitle>{title}</DialogTitle></DialogHeader>
          <div className="py-2">{children}</div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Drawer open={open} onOpenChange={setOpen}>
      <DrawerTrigger asChild><Button className="w-full min-h-[44px]">{triggerText}</Button></DrawerTrigger>
      <DrawerContent className="max-h-[90dvh] rounded-t-2xl pb-safe">
        <DrawerHeader className="text-left"><DrawerTitle>{title}</DrawerTitle></DrawerHeader>
        <div className="px-4 pb-6 overflow-y-auto overscroll-contain">{children}</div>
      </DrawerContent>
    </Drawer>
  )
}
```

**Tablet & Desktop Split-View Pattern (Master-Detail):**
```tsx
export function SplitViewLayout({ list, detail }: { list: React.ReactNode, detail: React.ReactNode }) {
  return (
    <div className="flex flex-col md:grid md:grid-cols-12 min-h-[calc(100vh-4rem)] gap-4 p-4">
      {/* Sol Liste: Mobilde tam genişlik, Tablette 5 kolon, Masaüstünde 4 kolon */}
      <div className="w-full md:col-span-5 lg:col-span-4 border-b md:border-b-0 md:border-r border-border pr-0 md:pr-4 overflow-y-auto">
        {list}
      </div>
      {/* Sağ Detay: Mobilde akış devamı, Tablette 7 kolon, Masaüstünde 8 kolon */}
      <div className="w-full md:col-span-7 lg:col-span-8 pl-0 md:pl-4 overflow-y-auto">
        {detail}
      </div>
    </div>
  )
}
```

## Resources

- shadcn/ui Docs: https://ui.shadcn.com
- Tailwind CSS Docs: https://tailwindcss.com
- Radix UI: https://radix-ui.com
- Tailwind UI: https://tailwindui.com
- Headless UI: https://headlessui.com
- v0 (AI UI Generator): https://v0.dev
