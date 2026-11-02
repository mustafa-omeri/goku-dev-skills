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


---

## 4. Reaktif İki Yönlü Geri Besleme Döngüleri ve Sonsuz Re-Render Yasağı (Infinite Loop & Maximum Update Depth Exceeded - OCAI Case Study)

React uygulamalarında en sık rastlanan ve tüm sekmenin kilitlenmesine yol açan ölümcül tuzak: `Warning: Maximum update depth exceeded`. Bu hata, üst ve alt bileşen arasında birbirini tetikleyen reaktif bir geri besleme döngüsü (reactive feedback loop) oluştuğunda meydana gelir.

### ⛔ Somut Vaka İncelemesi (OCAI Hatası)
```tsx
// ❌ YANLIŞ: Categories.tsx (Parent)
export function Categories() {
  const [companyList, setCompanyList] = useState([]);

  return (
    // TUZAK 1: Her render'da yeni bir arrow fonksiyon referansı üretilir!
    <CompanyBar onCompanyListChange={(companies: any) => setCompanyList(companies)} />
  );
}

// ❌ YANLIŞ: CompanyBar.tsx (Child)
export function CompanyBar({ isCompanyAuthorised, companyName, onCompanyListChange, user }) {
  useEffect(() => {
    // TUZAK 2: Her render'da yeni bir dizi referansı üretilip parent'a bildirilir!
    onCompanyListChange([{ id: 1, companyName }]);
    // TUZAK 3: onCompanyListChange bağımlılık dizisindedir!
  }, [isCompanyAuthorised, companyName, onCompanyListChange, user]);
}
```

### 💥 Ölümcül Döngü Nasıl Oluşur?
1. `Categories` render edilir → Yeni bir `onCompanyListChange` fonksiyon referansı oluşur.
2. `CompanyBar` mount olur → `useEffect` çalışır ve `onCompanyListChange([{ id, companyName }])` çağrılır.
3. `Categories` içinde `setCompanyList` tetiklenir → `Categories` YENİDEN RENDER OLUR.
4. `Categories` render olunca YEPYENİ bir `onCompanyListChange` fonksiyon referansı üretilir.
5. `CompanyBar`'daki `useEffect`, `onCompanyListChange` referansının değiştiğini görür ve TEKRAR ÇALIŞIR!
6. `onCompanyListChange` tekrar çağrılır → Adım 3'e dönülür.
7. React kısa sürede 50+ derinliğe ulaşır ve `Warning: Maximum update depth exceeded` ile çöker!

---

### 🛡️ 5 Katmanlı Mimari Çözüm ve Önlem Kataloğu

#### ✅ Çözüm 1: Doğrudan State Setter Referansı Geçirme (En Temiz & En Hızlı)
React'in `useState`'ten dönen `setCompanyList` fonksiyonu, bileşenin tüm yaşam döngüsü boyunca **bellekte sabit ve kimliksel olarak kararlıdır (identity-stable)**. Asla yeni referans üretmez.
```tsx
// ✅ DOĞRU: Ekstra arrow fonksiyon sarmalayıcısı AÇMAYIN!
<CompanyBar onCompanyListChange={setCompanyList} />
```

#### ✅ Çözüm 2: useCallback ile Callback Referansını Sabitleme
Eğer callback içinde ek mantık yürütülecekse mutlaka `useCallback` ile sabitlenmelidir:
```tsx
// ✅ DOĞRU: Boş veya kararlı bağımlılık dizisiyle fonksiyon referansı dondurulur
const handleCompanyListChange = useCallback((companies: any) => {
  setCompanyList(companies);
}, []);

<CompanyBar onCompanyListChange={handleCompanyListChange} />
```

#### ✅ Çözüm 3: "You Might Not Need an Effect" (Veri Bildirimini Event Handler'a Taşıma)
React resmi dokümantasyonuna göre alt bileşenin üst bileşene veri bildirmesi bir "reaktif senkronizasyon (effect)" değil, bir **olay (event)** sonucudur. Kullanıcı butona bastığında veya API isteği tamamlandığında bildirim yapılmalıdır; `useEffect` içinde sürekli üst bileşeni dürtmek anti-pattern'dir:
```tsx
// ✅ DOĞRU: Effect yerine verinin geldiği anda (fetch callback veya user event) çağırın
const handleCompanySelect = (newCompany) => {
  onCompanyListChange(newCompany);
};
```

#### ✅ Çözüm 4: useRef ile Callback'i useEffect Bağımlılığından Kurtarma (useLatest Deseni)
Eğer bir `useEffect` zorunlu olarak dışarıdan gelen bir callback'i çağırmak zorundaysa, callback referansını `useRef` ile tutarak `useEffect`'in gereksiz tetiklenmesi engellenmelidir:
```tsx
// ✅ DOĞRU: Callback referans değişimleri effect'i tetiklemez
const onCompanyListChangeRef = useRef(onCompanyListChange);
useEffect(() => {
  onCompanyListChangeRef.current = onCompanyListChange;
});

useEffect(() => {
  if (isCompanyAuthorised) {
    onCompanyListChangeRef.current([{ id: 1, companyName }]);
  }
}, [isCompanyAuthorised, companyName]); // onCompanyListChange bağımlılıkta YOK!
```

#### ✅ Çözüm 5: Değer Karşılaştırma Koruması (Ref Guard)
State güncellemesinden önce üretilen verinin eski veriyle aynı olup olmadığını kontrol edin:
```tsx
// ✅ DOĞRU: Aynı veriyle tekrar çağrı yapılmaz
const prevCompaniesRef = useRef<string>("");
useEffect(() => {
  const payload = JSON.stringify([{ id: 1, companyName }]);
  if (prevCompaniesRef.current !== payload) {
    prevCompaniesRef.current = payload;
    onCompanyListChange([{ id: 1, companyName }]);
  }
}, [isCompanyAuthorised, companyName]);
```
