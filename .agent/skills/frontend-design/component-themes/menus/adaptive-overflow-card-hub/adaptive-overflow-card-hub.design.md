# Adaptive Action Hub & Bottom-Sheet Card Panel

> **Theme Identifier:** `adaptive-overflow-card-hub`  
> **Category:** `menus`  
> **Original Source:** `menus/adaptive-overflow-card-hub`  
> **Aesthetic Tone:** High-Density Operating Surface / Craft Modern  
> **Layout Pattern:** Dual-Mode Adaptive Trigger Strip (`panel-only` & `preview-and-panel`) with Slide-Up Bottom-Sheet Card Hub  
> **Complexity Level:** Medium-High  
> **Standard:** Kural B.9 (Ölçeklenebilir Eylem Grupları), Kural A.13 (Anti-Scroll Slop)

---

## 1. Visual Essence & Aesthetic Direction

Yatay kaydırma çubuğu (scroll slop) ve dağınık hap buton dizilimleri yerine; yüzey alanına göre kendini akıllıca ölçekleyen, 100 öğeye kadar UI bütünlüğünü kaybetmeyen iki aşamalı eylem merkezi mimarisidir.

- **Color Palette:** Semantic domain tonları (Plan: Blue `#2563eb`, Debug: Red `#dc2626`, Design: Amber `#d97706`, Release: Green `#059669`, Accept: Purple `#7c3aed`) ve nötr yüzey token'ları (`--hub-surface`, `--hub-border`, `--hub-text-primary`).
- **Typography & Font Pairing:** System sans-serif arayüz metni ve sadece komut isimlerinde monospace vurgusu.
- **Craftsmanship & Anti-Slop:** Drop-down listeler (`<select>`) kesinlikle reddedilir. Eşit Boyutlu Kart Sözleşmesi (Equal Dimensions Card Contract) sayesinde tek öğeli kategoriler bile satırı bozmaz, tüm kartlar eşit yükseklik ve genişlik grid'ine oturur.

---

## 2. When to Choose This Theme (Agent Selection Guide)

Bir ajan şu durumlarda `adaptive-overflow-card-hub` bileşenini seçmelidir:

### Primary Triggers & Scenarios
- Bir sayfada veya panelde 8'den fazla eylem, kısayol, slash komutu veya araç varsa.
- "100 Öğe Sorusu" sorulduğunda öğeler ekrana sığmıyor ve yatay scroll riski doğuyorsa.
- Mobil, tablet ve masaüstünde eylemlerin kaybolmadan erişilebilir ve düzenli kalması gerektiğinde.

### Two Presentation Modes (Çözüm 1 & Çözüm 2)
1. **`panel-only` (Çözüm 1):** Tek bir anlamlı grup butonu (`⚡ Oturum Komutları (12)`). Tıklanınca doğrudan alttan açılan kart hub'ı gelir.
2. **`preview-and-panel` (Çözüm 2):** Konteynerin genişliğini ölçer; sığan ilk N öğeyi çip olarak gösterir, kalanları `... (+K)` overflow butonu ile alttan karta aktarır.

### When NOT to Choose (Anti-Patterns)
- 3 veya daha az sabit eylem bulunan alanlar (burada doğrudan normal butonlar kullanılır).
- Salt dikey form veya ayarlar listesi (form alanları için `logins` veya `accordions` tercih edilir).

---

## 3. Structural Anatomy & Layout

### DOM Architecture
- Trigger Ribbon: `.hub-ribbon`
  - Hub Launcher: `.hub-btn-group-launcher`
  - Preview Strip: `.hub-preview-strip`
  - Overflow Button: `.hub-btn-more`
- Bottom-Sheet Modal:
  - Backdrop: `.hub-backdrop` (blur(8px))
  - Sheet: `.hub-sheet` (`transform: translate(-50%, 100%)` -> `translate(-50%, 0)`)
  - Header: Drag handle, Title, Item count badge, Real-time Search input, Close button.
  - Body: `.hub-sheet-body` (overflow-y auto)
  - Category Panels: `.hub-domain-panel`
  - Equal Dimension Grid: `.hub-card-grid` (`repeat(auto-fill, minmax(260px, 1fr))`)

### Accessibility & Focus Management
- Odak tuzağı (focus trap): Modal açıldığında odak arama kutusuna gider.
- Escape tuşu: Modalı kapatır.
- Odak İadesi: Modal kapandığında klavye odağı modalı tetikleyen asıl butona (grup butonu veya `... (+K)` butonu) döner.


## Kural B.10 ve A.14 Sözleşmesi (Framed Containment & Proportional Sizing)
- **Modal Genişlik Tavanı:** `.hub-sheet` genişliği 1100px gibi kontrolsüz boyutlara açılamaz; `max-width: min(94vw, 780px)` ile sınırlıdır.
- **Çerçeveli Kategori İzolasyonu:** Her kategori `.hub-domain-frame` kutusu içine alınır (`border: 1px solid var(--hub-border)`, `background-color: var(--hub-surface-subtle)`, `padding: 14px 16px`).
- **Simetrik 2-Kolon Izgara:** Masaüstünde `repeat(2, 1fr)`, mobilde tek kolon (`1fr`) ile kartlar çerçevenin içinde dengeli ve simetrik konumlandırılır.
