# 🍞 Sileo Toast Sistemi & /ui-toast Sözleşmesi (Cerrahi Entegrasyon)

> **Kaynak Depo:** `hiaaryan/sileo` ([GitHub](https://github.com/hiaaryan/sileo))  
> **Scout ID:** `23`  
> **Hedef Yetenek:** `.agent/skills/ui-polish/` (Master Design Orchestrator)  
> **Varsayılan Toast Sağlayıcısı:** Bu bileşen, projelerde aksi açıkça talep edilmedikçe **standart ve varsayılan bildirim bileşenidir**.

---

## 1. Kullanıcı Direktifleri & Komut Sözleşmesi

Kullanıcı arayüz tasarımlarında veya toast bildirim taleplerinde aşağıdaki kural ve komut biçimleri bağlayıcıdır:

### 1.1 Varsayılan Bildirim Sağlayıcısı İlkesi
- Projede özel bir toast kütüphanesi (Sonner, React-Toastify vb.) istenmediği sürece **Sileo Toast** mimarisi varsayılan olarak uygulanır.
- UI geliştirilirken kullanıcıya konum tercihi sorulabilir veya komut parametresiyle seçtirilir:
  * `"top-left"`
  * `"top-center"`
  * `"top-right"` (varsayılan)
  * `"bottom-left"`
  * `"bottom-center"`
  * `"bottom-right"`

### 1.2 `/ui-toast` Komut Grameri
Ajan aşağıdaki komut çağrılarını cerrahi olarak tanır ve uygular:

| Komut Örneği | Açıklama |
|---|---|
| `/ui-toast --top-left` | Tüm bildirimleri sol üstte (`top-left`) konuşlandırır. |
| `/ui-toast --warning --top-left` | Sol üstte sarı/uyarı durumunda Sileo bildirim şablonu üretir. |
| `/ui-toast --success --bottom-center` | Alt ortada (`bottom-center`) yeşil/başarı bildirim şablonu üretir. |
| `/ui-toast --sileo --warning --top-left` | Kütüphane adını (`--sileo`) belirterek sol üstte uyarı bildirimi üretir. |
| `/ui-toast --info --bottom-right` | Sağ altta bilgilendirme toast'ı üretir. |
| `/ui-toast --error --top-center` | Üst ortada hata bildirim şablonu üretir. |

---

## 2. Çekirdek Mimari & Yay Fiziği (Spring Mechanics)

Sileo'yu sıradan toast'lardan ayıran en temel özellik, doğrusal (linear) zaman aşımı veya soluklaşma (fade) yerine **iOS benzeri fiziksel yay (spring) dinamiği** ve **kart destesi (stacking deck)** matematiğidir:

### 2.1 Fizik ve Geometri Parametreleri
```typescript
/* Geometri */
export const HEIGHT = 40;
export const WIDTH = 350;
export const DEFAULT_ROUNDNESS = 16;

/* Zamanlama & Yay Mekaniği */
export const DURATION_MS = 600;
export const DURATION_S = DURATION_MS / 1000;
export const DEFAULT_TOAST_DURATION = 5000;

export const SPRING = {
  type: "spring" as const,
  bounce: 0.25,
  duration: DURATION_S,
  stiffness: 380,
  damping: 28,
};

/* Mikro-Genişleme & Katmanlar */
export const BLUR_RATIO = 0.5;
export const PILL_PADDING = 10;
export const MIN_EXPAND_RATIO = 2.25;
export const SWAP_COLLAPSE_MS = 200;
```

### 2.2 6 Konum Eksen Matrisi
```typescript
export const SILEO_POSITIONS = [
  "top-left",
  "top-center",
  "top-right",
  "bottom-left",
  "bottom-center",
  "bottom-right",
] as const;

export type SileoPosition = (typeof SILEO_POSITIONS)[number];

export const getPositionStyles = (pos: SileoPosition): React.CSSProperties => {
  const isTop = pos.startsWith("top");
  const isCenter = pos.includes("center");
  const isLeft = pos.includes("left");

  return {
    position: "fixed",
    zIndex: 9999,
    pointerEvents: "none",
    display: "flex",
    flexDirection: isTop ? "column" : "column-reverse",
    gap: "10px",
    padding: "16px",
    top: isTop ? 0 : "auto",
    bottom: isTop ? "auto" : 0,
    left: isCenter ? "50%" : isLeft ? 0 : "auto",
    right: isCenter ? "auto" : isLeft ? "auto" : 0,
    transform: isCenter ? "translateX(-50%)" : "none",
    alignItems: isCenter ? "center" : isLeft ? "flex-start" : "flex-end",
  };
};
```

---

## 3. Üretim Kalitesinde Taşınabilir Bileşen Şablonu

Projelerde harici paket bağımlılığına (`bun`, monorepo yüküne) girmeden, doğrudan React + Tailwind / CSS değişkenleri ile çalışabilen tek dosyalık taşınabilir Sileo motoru:

### 3.1 `components/ui/sileo-toaster.tsx`
```tsx
import React, { createContext, useContext, useState, useCallback, useEffect } from "react";

export type SileoType = "success" | "error" | "warning" | "info" | "loading" | "action";
export type SileoPosition = "top-left" | "top-center" | "top-right" | "bottom-left" | "bottom-center" | "bottom-right";

export interface SileoToastItem {
  id: string;
  title: string;
  description?: string;
  type?: SileoType;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface SileoContextType {
  toast: (item: Omit<SileoToastItem, "id">) => string;
  success: (title: string, desc?: string) => string;
  error: (title: string, desc?: string) => string;
  warning: (title: string, desc?: string) => string;
  info: (title: string, desc?: string) => string;
  dismiss: (id: string) => void;
}

const SileoContext = createContext<SileoContextType | null>(null);

export const SileoProvider: React.FC<{
  children: React.ReactNode;
  defaultPosition?: SileoPosition;
}> = ({ children, defaultPosition = "top-right" }) => {
  const [toasts, setToasts] = useState<SileoToastItem[]>([]);
  const [position] = useState<SileoPosition>(defaultPosition);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    (item: Omit<SileoToastItem, "id">) => {
      const id = Math.random().toString(36).substring(2, 9);
      const newItem: SileoToastItem = { ...item, id };
      setToasts((prev) => [newItem, ...prev.slice(0, 4)]); // Maksimum 5 toast kaseti

      const dur = item.duration ?? 5000;
      if (dur > 0) {
        setTimeout(() => dismiss(id), dur);
      }
      return id;
    },
    [dismiss]
  );

  const success = useCallback((t: string, d?: string) => toast({ title: t, description: d, type: "success" }), [toast]);
  const error = useCallback((t: string, d?: string) => toast({ title: t, description: d, type: "error" }), [toast]);
  const warning = useCallback((t: string, d?: string) => toast({ title: t, description: d, type: "warning" }), [toast]);
  const info = useCallback((t: string, d?: string) => toast({ title: t, description: d, type: "info" }), [toast]);

  return (
    <SileoContext.Provider value={{ toast, success, error, warning, info, dismiss }}>
      {children}
      <aside aria-label="Bildirimler" className={`sileo-portal sileo-pos-${position}`}>
        {toasts.map((t, idx) => (
          <div
            key={t.id}
            role="status"
            aria-live="polite"
            className={`sileo-card sileo-${t.type || "info"}`}
            style={{
              "--stack-index": idx,
              transform: `scale(${1 - idx * 0.04}) translateY(${idx * (position.startsWith("top") ? 6 : -6)}px)`,
              opacity: 1 - idx * 0.15,
            } as React.CSSProperties}
            onClick={() => dismiss(t.id)}
          >
            <div className="sileo-pill-header">
              <span className="sileo-icon">
                {t.type === "success" && "✓"}
                {t.type === "error" && "✕"}
                {t.type === "warning" && "!"}
                {t.type === "info" && "ℹ"}
              </span>
              <strong className="sileo-title">{t.title}</strong>
              <button
                type="button"
                className="sileo-close"
                onClick={(e) => {
                  e.stopPropagation();
                  dismiss(t.id);
                }}
              >
                &times;
              </button>
            </div>
            {t.description && <p className="sileo-desc">{t.description}</p>}
            {t.action && (
              <button
                type="button"
                className="sileo-action-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  t.action?.onClick();
                  dismiss(t.id);
                }}
              >
                {t.action.label}
              </button>
            )}
          </div>
        ))}
      </aside>
    </SileoContext.Provider>
  );
};

export const useSileo = () => {
  const ctx = useContext(SileoContext);
  if (!ctx) throw new Error("useSileo must be used within SileoProvider");
  return ctx;
};
```

### 3.2 Donanım Hızlandırmalı CSS Kuralları
```css
/* Sileo Portal Konumları */
.sileo-portal {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
  display: flex;
  gap: 8px;
  padding: 16px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.sileo-pos-top-left      { top: 0; left: 0; flex-direction: column; align-items: flex-start; }
.sileo-pos-top-center    { top: 0; left: 50%; transform: translateX(-50%); flex-direction: column; align-items: center; }
.sileo-pos-top-right     { top: 0; right: 0; flex-direction: column; align-items: flex-end; }
.sileo-pos-bottom-left   { bottom: 0; left: 0; flex-direction: column-reverse; align-items: flex-start; }
.sileo-pos-bottom-center { bottom: 0; left: 50%; transform: translateX(-50%); flex-direction: column-reverse; align-items: center; }
.sileo-pos-bottom-right  { bottom: 0; right: 0; flex-direction: column-reverse; align-items: flex-end; }

/* Sileo Kart Mimarisi (Fizik & Yay) */
.sileo-card {
  pointer-events: auto;
  min-width: 280px;
  max-width: 380px;
  border-radius: 16px;
  padding: 12px 16px;
  background: var(--bg-surface, rgba(17, 24, 39, 0.94));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.12));
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
  color: var(--text-primary, #f9fafb);
  cursor: pointer;
  user-select: none;
  transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.3s ease;
  animation: sileoEnter 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes sileoEnter {
  from {
    opacity: 0;
    transform: translateY(-16px) scale(0.92);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.sileo-pill-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sileo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
}

.sileo-success .sileo-icon { background: #10b981; color: #fff; }
.sileo-error   .sileo-icon { background: #ef4444; color: #fff; }
.sileo-warning .sileo-icon { background: #f59e0b; color: #fff; }
.sileo-info    .sileo-icon { background: #3b82f6; color: #fff; }

.sileo-title {
  flex: 1;
  font-size: 13.5px;
  font-weight: 600;
}

.sileo-close {
  background: none;
  border: none;
  color: inherit;
  opacity: 0.6;
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
}
.sileo-close:hover { opacity: 1; }

.sileo-desc {
  margin: 6px 0 0 32px;
  font-size: 12px;
  line-height: 1.4;
  opacity: 0.85;
}

.sileo-action-btn {
  margin: 8px 0 0 32px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
  background: var(--accent-primary, #6366f1);
  color: #fff;
  border: none;
  cursor: pointer;
}
```

---

## 4. Kullanım Örnekleri

```tsx
import { useSileo } from "@/components/ui/sileo-toaster";

export function SettingsForm() {
  const toast = useSileo();

  const handleSave = async () => {
    try {
      await saveUserData();
      toast.success("Ayarlar Kaydedildi", "Tercihleriniz başarıyla güncellendi.");
    } catch (err) {
      toast.error("Kaydetme Başarısız", "Lütfen internet bağlantınızı kontrol edin.");
    }
  };

  return <button onClick={handleSave}>Kaydet</button>;
}
```

---

## 5. Doğrulama ve Entegrasyon Kanıtı
- Dosya Yolu: `.agent/skills/ui-polish/references/transferred_sileo.md`
- Hedef Skill: `ui-polish`
- Komut: `/ui-toast`
- Desteklenen Pozisyonlar: 6 konum (`top-left`, `top-center`, `top-right`, `bottom-left`, `bottom-center`, `bottom-right`)
- Yay Fiziği (Spring): Stiffness: 380, Damping: 28, Bounce: 0.25
