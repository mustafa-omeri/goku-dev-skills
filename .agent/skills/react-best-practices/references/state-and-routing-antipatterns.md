# State & Routing Anti-Patterns (Zustand, MobX & React Router)

> **Kaynak:** `millionco/react-doctor` Cerrahi Entegrasyonu (`plans/react-doctor.md`)  
> **Kapsam:** React mimarisi, global durum yönetimi (Zustand/MobX) ve yönlendirme (React Router/Next.js) performans teşhis rubrikleri.

---

## 1. Zustand Anti-Patterns & Teşhis Rubriği

Zustand hafif ve esnek bir state yöneticisidir; ancak yanlış selector ve subscription desenleri sessizce tüm ağacı yeniden render eden devasa performans darboğazlarına yol açar.

### ⛔ Kural 1.1: Nesne Selector'larında `useShallow` Kullanmama Tuzağı
```tsx
// ❌ YANLIŞ: Herhangi bir state değiştiğinde yeni nesne referansı üretilir ve bileşen gereksiz re-render olur!
const { user, theme } = useAppStore((state) => ({ user: state.user, theme: state.theme }));

// ✅ DOĞRU (Seçenek A - useShallow):
import { useShallow } from 'zustand/react/shallow';
const { user, theme } = useAppStore(
  useShallow((state) => ({ user: state.user, theme: state.theme }))
);

// ✅ DOĞRU (Seçenek B - Atomik Seçiciler):
const user = useAppStore((state) => state.user);
const theme = useAppStore((state) => state.theme);
```

### ⛔ Kural 1.2: Tüm Store'a Abone Olma (Whole Store Subscription)
```tsx
// ❌ YANLIŞ: Store'daki alakasız bir sayaç bile güncellense bu bileşen yeniden çizilir
const store = useAppStore();
return <div>{store.title}</div>;

// ✅ DOĞRU: Yalnızca ihtiyaç duyulan ilkel alana abone olun
const title = useAppStore((state) => state.title);
return <div>{title}</div>;
```

### 💡 Kural 1.3: Yalnızca Eylem Çağıran Bileşenlerde State Dinlememe
```tsx
// ❌ YANLIŞ: Sadece butona tıklandığında reset yapan bileşen state'e abone edilmemeli
const { reset } = useAppStore();

// ✅ DOĞRU: Yalnızca aksiyon fonksiyonunu seçin (aksiyonlar kararlı referanstır, re-render tetiklemez)
const reset = useAppStore((state) => state.reset);
```

### 🚀 Kural 1.4: Transient (Re-render Gerektirmeyen) State Okumaları
Animasyon döngüleri (`requestAnimationFrame`), event handler'lar veya callback'ler içinde re-render gerektirmeyen anlık değer okumalarında hook yerine store API'si kullanılmalıdır:
```tsx
// ✅ DOĞRU: Re-render sıfır
const handleClick = () => {
  const currentToken = useAppStore.getState().token;
  sendAnalytics(currentToken);
};
```

---

## 2. React Router & Layout Render Cascades

### ⛔ Kural 2.1: Kök Layout'larda Unmemoized Context Provider
```tsx
// ❌ YANLIŞ: URL her değiştiğinde RootLayout yeniden değerlendirilir, Provider value'su yeni referans alır ve altındaki tüm sayfa ağacı (Outlet) zorla yeniden render edilir!
export function RootLayout() {
  const [theme, setTheme] = useState('dark');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Outlet />
    </ThemeContext.Provider>
  );
}

// ✅ DOĞRU: Provider değerini useMemo ile sabitleyin veya Zustand gibi dış store'a taşıyın
export function RootLayout() {
  const [theme, setTheme] = useState('dark');
  const value = useMemo(() => ({ theme, setTheme }), [theme]);
  return (
    <ThemeContext.Provider value={value}>
      <Outlet />
    </ThemeContext.Provider>
  );
}
```

### ⛔ Kural 2.2: Waterfall Loader & Component-Level Fetching
- Sayfa ve alt bileşenlerin kendi `useEffect`'lerinde sıralı veri çekmesi (`waterfall`) layout sıçramalarına (CLS) yol açar.
- Veri çekme işlemleri `loader` fonksiyonunda paralel (`Promise.all`) yürütülmeli veya React 19 / Suspense sınırlarıyla eşzamanlı başlatılmalıdır.

---

## 3. MobX Observable Re-render Tuzakları

### ⛔ Kural 3.1: Observer Olmayan Bileşende Observable Erişimi
- MobX observable özelliklerine erişen her bileşen mutlaka `observer` HOC'u ile sarmalanmalıdır.
- Observer ile sarmalanmamış bir ebeveyn bileşen observable bir değeri okursa, o değer değiştiğinde MobX re-render tetikleyemez ve arayüz bayat kalır.

### ⛔ Kural 3.2: Computed Cache İhlali
- `@computed` özellikleri içinde `Date.now()`, `Math.random()` gibi saf olmayan (impure) değerler veya observable olmayan global değişkenler okunmamalıdır; aksi takdirde memoization önbelleği sürekli geçersiz kılınır.
