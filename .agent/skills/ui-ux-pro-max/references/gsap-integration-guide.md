# GSAP & ScrollSmoother Entegrasyon ve Yaşam Döngüsü Kılavuzu

> **Kapsam:** GSAP 3.x, ScrollTrigger, ScrollSmoother, `@gsap/react`, React 18+ Strict Mode Uyumu, Vite Önbellek Yönetimi ve Pürüzsüz / Otomatik Kaydırma (Autoscroll) Standartları.  
> **Konum:** `.agent/skills/ui-ux-pro-max/references/gsap-integration-guide.md`

---

## 1. Mimari İlke: Sıfır Repo Kirliliği ve Koşullu Entegrasyon

GSAP, kütüphane/araç setimizin (`skillSetWorks`) kendi doğrudan bağımlılıkları arasına eklenmez. Yalnızca hedef projede pürüzsüz kaydırma (smooth scroll), autoscroll veya karmaşık animasyon gerektiğinde ve hedef proje bir web/DOM projesi olduğunda cerrahi olarak projeye dahil edilir:

- **Web Frontend Tespiti:** Proje kökünde `package.json` ve web bağımlılıkları (React, Vue, Svelte, Next.js, Vite vb.) aranır.
- **Backend Yalıtımı:** Salt Java (Spring), Python (FastAPI/Django) veya CLI projelerinde GSAP entegrasyonu otomatik olarak atlanır.

---

## 2. Vite & Bağımlılık Önbelleği Sorun Giderme

Vite projelerinde yeni paket kurulduğunda sıklıkla karşılaşılan `Failed to resolve import "gsap"` hatası, Vite'ın `node_modules/.vite` altındaki ön-derlenmiş (pre-bundled) bağımlılık önbelleğinden kaynaklanır.

### Çözüm Adımları:
1. **Paket Yöneticisine Göre Kurulum:**
   ```bash
   # pnpm (Önerilen)
   pnpm add gsap @gsap/react

   # npm
   npm install gsap @gsap/react

   # yarn
   yarn add gsap @gsap/react

   # bun
   bun add gsap @gsap/react
   ```

2. **Önbelleği Temizleyerek Başlatma:**
   ```bash
   # npm
   npm run dev -- --force

   # pnpm
   pnpm dev --force
   ```
   *Alternatif olarak `node_modules/.vite` dizini doğrudan silinebilir.*

---

## 3. Merkezi Başlatıcı Singleton Mimarisi (`src/lib/gsap.ts`)

Her bileşende dağınık `import` ve mükerrer `registerPlugin` çağrıları yapmak yerine, tüm eklenti kayıtları ve SSR kontrolleri tek bir merkezden (`src/lib/gsap.ts`) yönetilir:

```typescript
// src/lib/gsap.ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// SSR ve DOM Güvenliği
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);

  // Club GSAP ScrollSmoother dinamik kontrolü (Hata önleme)
  try {
    // @ts-ignore
    const maybeSmoother = (gsap as any).ScrollSmoother;
    if (maybeSmoother) {
      gsap.registerPlugin(maybeSmoother);
    }
  } catch (e) {
    // ScrollSmoother lisansı yoksa hata vermez, sessizce devam eder
  }
}

/**
 * Kullanıcının hareket azaltma tercihini doğrular
 */
export const prefersReducedMotion = (): boolean => {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
};

/**
 * Programatik yumuşak kaydırma yardımcısı
 */
export const autoScrollTo = (
  target: string | HTMLElement | number,
  options?: { duration?: number; offset?: number; ease?: string }
) => {
  if (typeof window === "undefined") return;
  const { duration = 1, offset = 0, ease = "power2.inOut" } = options || {};

  if (prefersReducedMotion()) {
    if (typeof target === "number") {
      window.scrollTo(0, target);
    } else {
      const el = typeof target === "string" ? document.querySelector(target) : target;
      el?.scrollIntoView();
    }
    return;
  }

  let targetY = 0;
  if (typeof target === "number") {
    targetY = target;
  } else {
    const el = typeof target === "string" ? document.querySelector(target) : target;
    if (el) {
      const rect = el.getBoundingClientRect();
      targetY = window.pageYOffset + rect.top + offset;
    }
  }

  gsap.to(window, {
    duration,
    scrollTo: { y: targetY, autoKill: true },
    ease,
  });
};

export { gsap, ScrollTrigger };
export default gsap;
```

---

## 4. ScrollSmoother DOM Kapsayıcı Sözleşmesi

[ScrollSmoother](https://gsap.com/docs/v3/Plugins/ScrollSmoother/), sayfa gövdesini fiziksel olarak GPU katmanında `matrix3d` ile kaydırdığı için **kesin bir DOM hiyerarşisi** gerektirir:

### Zorunlu Katmanlar:
1. `#smooth-wrapper`:
   - `position: fixed; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden;`
2. `#smooth-content`:
   - `width: 100%; min-height: 100vh; overflow: visible;`
3. **Sabit Elemanlar Kuralı:** `position: fixed` olan navbar veya footer gibi elemanlar asla `#smooth-content` içine konulmaz; `#smooth-wrapper` dışına veya doğrudan `body` seviyesine yerleştirilir.

### React 18+ Strict Mode ve `useGSAP` Entegrasyonu:

React 18 ve 19'da geliştirme modunda (`StrictMode`) bileşenler iki kez mount edilir (`mount -> unmount -> mount`). Temizlenmeyen GSAP animasyonları bellek sızıntısına, çift kaydırma dinleyicisine ve donmalara yol açar. Bu yüzden `@gsap/react` içindeki `useGSAP` kancası veya `gsap.context()` zorunludur:

```tsx
// src/components/SmoothScroll.tsx
import React, { useRef } from "react";
import { useGSAP } from "@gsap/react";
import { gsap, prefersReducedMotion } from "../lib/gsap";

export const SmoothScroll: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (typeof window === "undefined" || prefersReducedMotion()) return;

      // @ts-ignore
      const ScrollSmoother = (gsap as any).ScrollSmoother;
      let smootherInstance: any = null;

      if (ScrollSmoother && wrapperRef.current && contentRef.current) {
        smootherInstance = ScrollSmoother.create({
          wrapper: wrapperRef.current,
          content: contentRef.current,
          smooth: 1.2,
          effects: true,
          smoothTouch: 0.1,
          normalizeScroll: true,
        });
      } else {
        // Fallback: Native yumuşak kaydırma
        document.documentElement.style.scrollBehavior = "smooth";
      }

      return () => {
        if (smootherInstance) smootherInstance.kill();
        document.documentElement.style.scrollBehavior = "";
      };
    },
    { scope: wrapperRef }
  );

  return (
    <div id="smooth-wrapper" ref={wrapperRef} className="fixed inset-0 overflow-hidden">
      <div id="smooth-content" ref={contentRef} className="w-full min-h-screen overflow-visible">
        {children}
      </div>
    </div>
  );
};
```

---

## 5. Otomatik Kaydırma (Autoscroll & Marquee Ticker) Kalıpları

### Kesintisiz Kayan Şerit (Infinite Marquee):
```typescript
import { useGSAP } from "@gsap/react";
import gsap from "../lib/gsap";

export const useMarquee = (trackRef: React.RefObject<HTMLElement>, speed = 25) => {
  useGSAP(() => {
    if (!trackRef.current || prefersReducedMotion()) return;

    const tween = gsap.to(trackRef.current, {
      xPercent: -50,
      repeat: -1,
      duration: speed,
      ease: "none",
    });

    return () => tween.kill();
  }, { scope: trackRef });
};
```

---

## 6. Club GSAP vs. Açık Kaynak Fallback Matrisi

| Senaryo | ScrollSmoother Mevcut mu? | Uygulanan Mimari | Davranış Sonucu |
|---|---|---|---|
| **Club Token Var** | Evet (`gsap-bonus`) | Tam donanımlı ScrollSmoother (smooth, effects, data-speed, data-lag) | Kusursuz ivmelenmeli GPU kaydırma |
| **Açık Kaynak / Standart Paket** | Hayır (Standart `gsap`) | Otomatik Fallback (`ScrollTrigger` + `scroll-behavior: smooth`) | Sıfır hata, sıfır çökme, standart akıcı kaydırma |
| **prefers-reduced-motion: reduce** | - | Bütün animasyonlar durdurulur, doğrudan erişilebilir atlama | WCAG 2.2 AA erişilebilirlik uyumu |
