# Emil Kowalski Motion & Micro-Interactions Playbook

> **Kaynak:** `emilkowalski/skills` Cerrahi Entegrasyonu (`plans/skills.md`)  
> **Kapsam:** Pürüzsüz animasyonlar, yay mekaniği (spring physics), kesintiye uğrayabilir hareketler (interruptible motion) ve dokunsal mikro etkileşimler.

---

## 1. Yay Fiziği (Springs) vs. Süre Bazlı Eğriler (Durations)

### Ne Zaman Yay Fiziği (Spring)?
- **Kullanıcı etkileşimi içeren durumlar:** Çekmeceler (drawers/sheets), sürükleme (drag), toggle anahtarları, modal açılışları ve buton tıklamaları.
- **Kesintiye uğrayabilir eylemler (Interruptible):** Kullanıcı bir animasyon tamamlanmadan ters yöne tıkladığında veya parmağını çektiğinde, animasyon sıfırlanmamalı; mevcut hız ve momentumunu koruyarak yön değiştirmelidir.

### Ne Zaman Süre Bazlı Eğri (Duration + Easing)?
- **Pasif durumlar:** Sayfa rotası geçişleri, arka plan kararması (backdrop fade), veri yükleme çubuğu ve tek yönlü görünürlük değişimleri.
- **Standart Eğri:** Doğal yavaşlama için `cubic-bezier(0.16, 1, 0.3, 1)` (expo-out benzeri).

---

## 2. Akıcı Arayüzün 3 Temel İlkesi (Fluid UI)

### 1. Kesintisizlik ve Hız Korunumu (Interruptibility)
- Kullanıcı arayüzü hiçbir zaman animasyonun bitmesini beklemek zorunda kalmamalıdır (`pointer-events: none` gereksiz yere kilitlenmemelidir).
- Yay mekaniğinde `stiffness: 400`, `damping: 30`, `mass: 0.8` aralığı, tepki veren (snappy) ve aşırı salınım (overshoot) yapmayan altın standarttır.

### 2. Mekansal Tutarlılık (Spatial Awareness)
- Bir kart tıklandığında modal olarak açılıyorsa, ekranın ortasından sıfırdan belirmemeli; tıklandığı kartın koordinatlarından genişlemelidir (`shared layout / layoutId`).
- Kapatıldığında da tekrar orijinal yerine küçülmelidir.

### 3. Düzen Kayması Yokluğu (No Layout Thrashing)
- `width`, `height`, `top`, `left` gibi tarayıcı reflow'unu tetikleyen özellikleri asla anime etmeyin.
- Yalnızca GPU hızlandırmalı iki özelliği kullanın: `transform` (`scale`, `translate`) ve `opacity`.

---

## 3. Dokunsal Mikro Etkileşimler (Tactile Feedback)

### 🔘 Buton Basma Hissi (Scale Feedback)
Kullanıcı butona bastığı anda anlık dokunsal geri bildirim almalıdır:
```css
/* Tailwind ile dokunsal mikro sıkışma */
.btn-tactile {
  transition: transform 0.12s cubic-bezier(0.16, 1, 0.3, 1);
}
.btn-tactile:active {
  transform: scale(0.97);
}
```

### 📋 Çekmece ve Sheet Etkileşimi
- Aşağı çekildiğinde sürükleme mesafesi arttıkça direnç (rubber banding / friction) katsayısı artmalıdır.
- Bırakıldığında eşik değer aşılmışsa (%30 sürükleme), çekmece yumuşakça aşağı kapanmalı; aşılmamışsa orijinal yüksekliğine zıplamalıdır.

---

## 4. Erişilebilirlik (prefers-reduced-motion)

Kullanıcının sisteminde hareket hassasiyeti açıksa, tüm transform hareketleri devre dışı bırakılmalı, yalnızca yumuşak opaklık geçişi (`opacity fade`) sunulmalıdır:
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
