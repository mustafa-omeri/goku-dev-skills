# Three.js & React Three Fiber (R3F) Performans ve Bellek Rubriği

> **Kaynak:** `millionco/react-doctor` Cerrahi Entegrasyonu (`plans/react-doctor.md`)  
> **Kapsam:** WebGL, Canvas ve 3D arayüz bileşenleri için bellek sızıntısı (memory leak) ve 60 FPS akıcılık teşhis rubriği.

---

## 1. `useFrame` Döngüsü Kuralları (60/120 FPS Koruması)

`useFrame` saniyede 60 ila 120 kez çağrılır. Bu kanca (hook) içindeki en ufak bir fazlalık kare hızını anında düşürür.

### ⛔ Kural 1.1: `useFrame` İçinde Kesinlikle `setState` Çağırmama
```tsx
// ❌ YANLIŞ: Her karede (saniyede 60 kez!) React state güncellemesi tetikler, React render ağacını kilitler
useFrame(() => {
  setRotation((r) => r + 0.01);
});

// ✅ DOĞRU: Doğrudan Three.js nesne referansını mutate edin (React re-render'ı sıfır)
const meshRef = useRef<THREE.Mesh>(null!);
useFrame((state, delta) => {
  meshRef.current.rotation.y += delta * 0.5;
});
```

### 💡 Kural 1.2: Delta Değerini Sınırlandırma (Delta Capping)
Kullanıcı sekme değiştirdiğinde tarayıcı `requestAnimationFrame`'i duraklatır; kullanıcı sekmeye geri döndüğünde `delta` devasa bir sayı (örn. 5.0 saniye) olarak gelebilir ve nesnelerin fırlamasına yol açar:
```tsx
useFrame((state, delta) => {
  const safeDelta = Math.min(delta, 0.1); // 100ms tavanı
  meshRef.current.position.x += safeDelta * speed;
});
```

---

## 2. Bellek Yönetimi ve Temizlik (Disposal Protocol)

Three.js nesneleri (geometriler, materyaller, dokular) JavaScript Garbage Collector (GC) tarafından otomatik temizlenemez; GPU belleğinde kalır (`VRAM Leak`).

### ⛔ Kural 2.1: Bileşen Unmount Olduğunda Kaynakları İmha Etme
```tsx
useEffect(() => {
  return () => {
    geometry.dispose();
    material.dispose();
    texture.dispose();
  };
}, [geometry, material, texture]);
```
*Not: R3F standart JSX deklaratif nesnelerinde (`<mesh><boxGeometry /><meshStandardMaterial /></mesh>`) unmount anında otomatik dispose uygular; ancak `useMemo` veya imperatif `new THREE.*` ile üretilen kaynaklar manuel dispose edilmelidir.*

### 🚀 Kural 2.2: Geometri ve Materyal Havuzlama (Instance Pooling)
- Döngü (`map`) içinde 100 mesh üretiliyorsa, her mesh için ayrı `new THREE.BoxGeometry()` ve `new THREE.MeshStandardMaterial()` üretilmemelidir.
- Geometri ve materyal tekil bir örnek (`shared instance`) olarak oluşturulmalı veya yüzlerce benzer nesne için `InstancedMesh` kullanılmalıdır.

---

## 3. Canvas & GPU Optimizasyonları

### 💡 Kural 3.1: Ekran Çözünürlüğü Tavanı (`dpr={[1, 2]}`)
Retina ve modern mobil ekranlar 3x veya 4x piksel yoğunluğuna sahiptir. Sınırlama yapılmazsa 4K çözünürlükte GPU aşırı ısınır ve pil tüketimi fırlar:
```tsx
// ✅ DOĞRU: Maksimum 2x DPR tavanı
<Canvas dpr={[1, 2]} frameloop="demand">
```

### 🔋 Kural 3.2: Talep Üzerine Render (`frameloop="demand"`)
Sürekli dönen bir animasyon yoksa (yalnızca kullanıcı fareyle döndürdüğünde veya prop değiştiğinde hareket eden modellerde), `frameloop="demand"` kullanılmalıdır. Statik durumlarda GPU kullanımı %0'a iner.
