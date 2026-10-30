# Base UI Primitives & Tailwind CSS v4 Entegrasyon Rehberi

> **Kaynak:** `ibelick/ui-skills` Cerrahi Entegrasyonu (`plans/ui-skills.md`)  
> **Kapsam:** `@base-ui/react` erişilebilir unstyled primitifler, Tailwind v4 CSS-first mimarisi ve zanaatkar mikro-bileşen desenleri.

---

## 1. Neden Base UI + Tailwind CSS v4?

Modern frontend mimarisinde Radix UI ve shadcn standart olsa da, `@base-ui/react` (Material UI ekibinin yeni nesil headless kütüphanesi) sıfır CSS çalışma zamanı, yerleşik animasyon durumları (`data-starting-style`, `data-ending-style`) ve DOM seviyesinde erişilebilirlik sunar.

Tailwind CSS v4'ün CSS-first mimarisi (`@theme`, `@utility`) ile birleştiğinde JS bundle boyutu küçülür ve render performansı artar.

---

## 2. Tailwind v4 Temel Kurulum ve Değişkenler

Tailwind v4'te `tailwind.config.js` yerine doğrudan CSS dosyası içinde `@theme` bloğu kullanılır:

```css
@import "tailwindcss";

@theme {
  --color-brand-primary: oklch(58% 0.22 260);
  --color-surface-card: oklch(98% 0.01 260);
  --radius-subtle: 6px;
  --radius-pill: 9999px;
  --font-sans: 'Inter', system-ui, sans-serif;
}
```

---

## 3. Örnek Bileşen: Base UI Popover & Dialog (CSS-Only Transition)

Base UI primitifleri, açılış ve kapanış durumlarını HTML veri öznitelikleri (`[data-popup-open]`, `[data-starting-style]`) ile yönetir. Bu sayede harici bir framer-motion bağımlılığına gerek kalmadan saf CSS ile pürüzsüz animasyon elde edilir:

```tsx
import { Popover } from '@base-ui/react/popover';

export function ModernPopover() {
  return (
    <Popover.Root>
      <Popover.Trigger className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm font-medium hover:bg-neutral-50 active:scale-97 transition">
        Seçenekler
      </Popover.Trigger>
      
      <Popover.Portal>
        <Popover.Positioner sideOffset={8}>
          <Popover.Popup className="w-64 rounded-xl border border-neutral-200/80 bg-white/90 p-4 shadow-xl backdrop-blur-md transition-all duration-200 ease-out data-[starting-style]:scale-95 data-[starting-style]:opacity-0 data-[ending-style]:scale-95 data-[ending-style]:opacity-0">
            <Popover.Arrow className="fill-white stroke-neutral-200" />
            <h4 className="font-semibold text-neutral-900 text-sm">Hızlı Eylemler</h4>
            <p className="mt-1 text-xs text-neutral-500">
              Klavye ile tam erişilebilir, sıfır runtime maliyetli headless açılır panel.
            </p>
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
```

---

## 4. Dokunsal Buton ve Gesture Playbook (@ibelick Desenleri)

### Yaylı Switch (Spring Switch)
```tsx
import { Switch } from '@base-ui/react/switch';

export function SmoothSwitch() {
  return (
    <Switch.Root className="group relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent bg-neutral-200 transition-colors duration-200 ease-in-out data-[checked]:bg-emerald-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500">
      <Switch.Thumb className="pointer-events-none block h-5 w-5 rounded-full bg-white shadow-md ring-0 transition-transform duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] group-data-[checked]:translate-x-5" />
    </Switch.Root>
  );
}
```

### Tasarım İlkeleri:
1. **İnce Çerçeve & Yüzey Ayrımı:** Kenarlıklar için `border-neutral-200/80`, yüzeyler için hafif yarı-saydam `bg-white/90 backdrop-blur-md` zanaatkar bir derinlik verir.
2. **Klavye Erişilebilirliği:** Her etkileşimli primitif `focus-visible:ring-2` ile belirginleştirilmelidir.
