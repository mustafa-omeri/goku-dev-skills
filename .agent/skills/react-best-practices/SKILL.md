---
name: react-best-practices
description: >-
  React ve Next.js kodlama standartları: re-render, veri çekme waterfall'ları, bundle boyutu,
  bileşen mimarisi (compound components) ve JavaScript mikro-optimizasyonları için kurallar.
  Tetikleyiciler: "react performans", "re-render", "waterfall", "useMemo", "compound component",
  "react best practices", "eliminate waterfalls", "composition patterns".
  Tetiklenmez: salt CSS ve Tailwind biçimlendirmesi `ui-styling`'e aittir.
  Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# React En İyi Pratikler ve Bileşen Mimarisi (React Best Practices)

Vercel Mühendisliği standartları ve modern React mimarisini birleştiren, yapay zekâ kodlama ajanları için optimize edilmiş kapsamlı performans ve tasarım rehberi. 78 kural ve 9 kategoriyi kapsar.

---

## ⛔ Bölüm 0 — Yığın ve Ortam İzolasyonu (Stack Isolation)

Ajanların en sık düştüğü hata, **Vite SPA** projelerinde Next.js Server Components (RSC) kurallarını çalıştırmaya kalkışmaktır. Kod yazmadan önce projenin yığınını kontrol et:

| Proje Türü | Örnekler | Kuralların Geçerliliği |
|---|---|---|
| **Vite SPA / Pure Client** | `kalansure`, `FEProjectv1`, `bookmarkManagerProject` | **`server-*` kuralları KESİNLİKLE GEÇERSİZDİR.** `React.cache`, `use server`, `next/dynamic` ASLA kullanılmaz. Dinamik yükleme için `React.lazy()` + `<Suspense>` kullanılır. |
| **Next.js App Router** | RSC / SSR / Fullstack projeler | Tüm kurallar (özellikle `server-*`) geçerlidir. |

---

## ⚡ Bölüm 1 — Altın Kurallar & Anti-Pattern Matrisi (Agent Cheatsheet)

Ajanların izole kuralları atlamasını önlemek için en kritik 10 kural ve anında uygulanabilir çözümleri aşağıdadır:

### 1. Waterfalls (Asenkron Şelale) Engelleme [CRITICAL]
Birbirinden bağımsız asenkron işlemleri sıralı `await` ile bekleme; `Promise.all` ile paralel koştur.

```tsx
// ❌ YANLIŞ: 2 saniye + 3 saniye = 5 saniye bekleme
const user = await fetchUser();
const posts = await fetchPosts();

// ✅ DOĞRU: Paralel çalışma = toplam 3 saniye
const [user, posts] = await Promise.all([fetchUser(), fetchPosts()]);
```

### 2. Barrel Imports Kaçınma [CRITICAL]
Geniş index/barrel dosyalarından import yapmak tree-shaking'i bozar ve bundle boyutunu şişirir.

```tsx
// ❌ YANLIŞ: Tüm paketi/bileşenleri belleğe çeker
import { Button, Input } from '@/components';
import { LucideIcon } from 'lucide-react';

// ✅ DOĞRU: Doğrudan dosya yolundan çek
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import ArrowRight from 'lucide-react/dist/esm/icons/arrow-right';
```

### 3. Türetilmiş State İçin `useEffect` Kullanmama [MEDIUM]
Mevcut state veya props'tan hesaplanabilen bir değer için yeni state açıp `useEffect` ile güncelleme. Doğrudan render sırasında hesapla.

```tsx
// ❌ YANLIŞ: Ekstra re-render döngüsü ve senkronizasyon hatası
const [items, setItems] = useState([]);
const [total, setTotal] = useState(0);
useEffect(() => {
  setTotal(items.reduce((acc, i) => acc + i.price, 0));
}, [items]);

// ✅ DOĞRU: Render anında anında hesaplanır (pahalıysa useMemo)
const total = items.reduce((acc, i) => acc + i.price, 0);
```

### 4. Fonksiyonel `setState` ile Kararlı Callback [MEDIUM]
Bir önceki state değerine bağımlı güncellemelerde closure değişkenini değil, fonksiyonel güncelleyiciyi kullan. Bu sayede `useCallback` bağımlılık dizisi boş kalabilir.

```tsx
// ❌ YANLIŞ: count her değiştiğinde handleClick yeniden üretilir
const handleClick = useCallback(() => {
  setCount(count + 1);
}, [count]);

// ✅ DOĞRU: Fonksiyon referansı her zaman kararlı kalır
const handleClick = useCallback(() => {
  setCount(prev => prev + 1);
}, []);
```

### 5. Tembel State Başlatma (Lazy State Init) [MEDIUM]
Hesaplaması pahalı olan başlangıç değerlerini doğrudan `useState` içine yazma; fonksiyon olarak ver.

```tsx
// ❌ YANLIŞ: parse işlemi HER render'da gereksiz yere baştan çalışır
const [config] = useState(JSON.parse(localStorage.getItem('cfg') || '{}'));

// ✅ DOĞRU: Yalnızca ilk mount anında tek bir kez çalışır
const [config] = useState(() => JSON.parse(localStorage.getItem('cfg') || '{}'));
```

### 6. Koşullu Render'da `&&` Yerine Ternary Kullanımı [MEDIUM]
Sayısal ifadelerde `count && <Component />` yazıldığında, `count = 0` ise ekrana `0` basılır.

```tsx
// ❌ YANLIŞ: items.length 0 olduğunda ekranda "0" görünür!
{items.length && <List items={items} />}

// ✅ DOĞRU: Güvenli ve açık koşullu render
{items.length > 0 ? <List items={items} /> : null}
```

### 7. Bileşen İçinde Bileşen Tanımlamama [MEDIUM]
Bir bileşenin gövdesi içinde başka bir fonksiyonel bileşen ASLA tanımlanmaz; her render'da yeni bir tip oluşur ve tüm DOM ağacı sıfırdan mount edilir.

```tsx
// ❌ YANLIŞ: Her parent render'ında Child unmount & remount olur (state uçar)
function Parent() {
  function Child() { return <div>Alt</div>; }
  return <Child />;
}

// ✅ DOĞRU: Dışarıda bağımsız bileşen olarak tanımla
function Child() { return <div>Alt</div>; }
function Parent() { return <Child />; }
```

### 8. Boolean Prop Patlaması Yerine Bileşen Kompozisyonu [HIGH]
Bileşene 10 farklı boolean prop (`isCompact`, `hasHeader`, `showFooter`, `withBorder`) eklemek yerine Compound Components deseni kur.

```tsx
// ❌ YANLIŞ: Katı ve yönetilemez boolean prop enflasyonu
<Card title="Başlık" isCompact hasFooter showBadge footerText="Kaydet" />

// ✅ DOĞRU: Esnek, genişletilebilir ve okunabilir kompozisyon
<Card>
  <Card.Header>
    <Card.Title>Başlık</Card.Title>
    <Badge>Yeni</Badge>
  </Card.Header>
  <Card.Content>İçerik</Card.Content>
  <Card.Footer><Button>Kaydet</Button></Card.Footer>
</Card>
```

### 9. Transient Değerler İçin `useRef` Kullanımı [MEDIUM]
Render tetiklemesi gerekmeyen (örneğin interval ID, önceki değer, animasyon frame'i, scroll pozisyonu) veriler için `useState` yerine `useRef` kullan.

```tsx
// ❌ YANLIŞ: Zamanlayıcı id değiştiğinde gereksiz re-render
const [timerId, setTimerId] = useState<number>();

// ✅ DOĞRU: Render tetiklemeden değeri tutar
const timerRef = useRef<number>();
```

### 10. Set/Map ile $O(1)$ Arama ve RegExp Hoisting [LOW-MEDIUM]
Döngü içinde `array.find()` veya `array.includes()` çalıştırmak $O(N \times M)$ karmaşıklık yaratır. Bir kez `Set` veya `Map` oluştur.

```tsx
// ❌ YANLIŞ: Her item için selectedIds listesi baştan taranır O(N^2)
items.map(item => ({ ...item, selected: selectedIds.includes(item.id) }));

// ✅ DOĞRU: Set ile O(1) anında arama O(N)
const selectedSet = new Set(selectedIds);
items.map(item => ({ ...item, selected: selectedSet.has(item.id) }));
```

---

## 📚 Bölüm 2 — Kural Kategorileri & Hiyerarşi (78 Kural Dizini)

Detaylı kural dosyaları `rules/` klasöründe yer alır. Tam birleşik referans için `AGENTS.md` dosyasına bakınız.

| Kategori | Öncelik | Önek | Kapsam |
|---|---|---|---|
| **1. Eliminating Waterfalls** | **CRITICAL** | `async-` | `async-parallel`, `async-defer-await`, `async-suspense-boundaries`, `async-cheap-condition-before-await` |
| **2. Bundle Size Optimization** | **CRITICAL** | `bundle-` | `bundle-barrel-imports`, `bundle-dynamic-imports`, `bundle-defer-third-party`, `bundle-conditional` |
| **3. Component Architecture** | **HIGH** | `architecture-`, `patterns-`, `state-` | `architecture-avoid-boolean-props`, `architecture-compound-components`, `patterns-explicit-variants`, `state-decouple-implementation`, `state-context-interface` |
| **4. Server-Side Performance** | **HIGH (Next.js)** | `server-` | *(Yalnızca Next.js)* `server-parallel-fetching`, `server-dedup-props`, `server-cache-react`, `server-auth-actions` |
| **5. Client-Side Data Fetching** | **MEDIUM-HIGH** | `client-` | `client-swr-dedup`, `client-event-listeners`, `client-passive-event-listeners`, `client-localstorage-schema` |
| **6. Re-render Optimization** | **MEDIUM** | `rerender-` | `rerender-functional-setstate`, `rerender-derived-state-no-effect`, `rerender-lazy-state-init`, `rerender-no-inline-components`, `rerender-use-ref-transient-values` |
| **7. Rendering Performance** | **MEDIUM** | `rendering-` | `rendering-conditional-render`, `rendering-content-visibility`, `rendering-hoist-jsx`, `rendering-usetransition-loading` |
| **8. JavaScript Performance** | **LOW-MEDIUM** | `js-` | `js-set-map-lookups`, `js-hoist-regexp`, `js-early-exit`, `js-combine-iterations`, `js-tosorted-immutable` |
| **9. Advanced Patterns & React 19** | **LOW** | `advanced-`, `react19-` | `advanced-use-latest`, `advanced-event-handler-refs`, `react19-no-forwardref` |

---

## 🔍 Bölüm 3 — Nasıl Uygulanır?

1. **Bileşen Geliştirirken:** Bölüm 1'deki Altın Kurallar Matrisini kontrol et.
2. **Mimari Tasarlarken:** `rules/architecture-compound-components.md` ve `rules/architecture-avoid-boolean-props.md` rehberlerini oku.
3. **Performans İyileştirmesinde:** `rules/rerender-*.md` ve `rules/bundle-*.md` kurallarındaki Before/After örneklerini referans al.
