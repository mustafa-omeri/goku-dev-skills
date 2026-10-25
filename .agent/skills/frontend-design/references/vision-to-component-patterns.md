# Vision-to-Component Engineering Patterns

> Kaynak: [abi/screenshot-to-code](https://github.com/abi/screenshot-to-code) · Scout Değerlendirme Raporu ID: 8
> Amaç: Ekran görüntüsü, UI mockup, Figma çizimi veya video kaydı girdilerinden üretim kalitesinde React/Tailwind bileşenleri türetirken görsel doğruluğu ve kod mimarisini güvenceye alan zanaat ilkeleri.

---

## 1. Temel İlke ve Yaklaşım

Bir görselden veya tasarımdan kod üretirken (Vision-to-Code), LLM'ler çoğunlukla tek parçalı, hardcode stiller içeren, erişilebilirlikten yoksun ve monolitik kodlar üretmeye meyillidir (AI Slop).

Bu rehber, görsel girdiyi parçalara ayırarak modüler, responsive ve zanaatkar bir React+Tailwind bileşenine dönüştürme adımlarını tanımlar.

---

## 2. 5 Aşamalı Görsel Çözümleme Döngüsü

```
[Görsel Girdi] 
      ↓
1. Kutu Modeli & Düzen Haritası (Flex / Grid Sezgisi)
      ↓
2. Tipografi ve Hiyerarşik Metin Katmanı
      ↓
3. Renk & Kontrast Çıkarma (Tailwind Semantik Eşleme)
      ↓
4. Varlık Ayrıştırma (İkonlar / Mock Asset Provider)
      ↓
5. Görsel Regresyon & Boşluk Dengeleme (Visual Diff)
```

---

## 3. Ayrıntılı Zanaat İlkeleri

### 3.1 Bounding Box & Konteyner Düzeni (Flex vs Grid)
- **Kural:** Görseldeki öğeleri mutlak koordinatlarla (`absolute`, `top-[120px]`) ASLA bağlama.
- Görseli yatay ve dikey akış bölgelerine ayır:
  * 1 boyutlu düzenler (navbar, buton grubu, kart başlığı): `flex flex-row items-center justify-between gap-4`.
  * 2 boyutlu düzenler (ürün kartları, dashboard widget'ları): `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`.
- Sayfa sınırları ve merkezleme: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`.

### 3.2 Tipografi ve Metin Katmanı (OCR Hiyerarşisi)
- Görseldeki font stillerini doğrudan sistemdeki küratörlü fontlarla eşle:
  * **Display / Hero Başlık:** Karakterli bir display/serif fontu (ör: `Syne`, `Cinzel`, `Clash Display`).
  * **Gövde Metni / Veri:** Okunaklı sans/mono (ör: `Plus Jakarta Sans`, `Geist`, `Fira Code`).
  * **İstatistik ve Rakamlar:** Her zaman `font-variant-numeric: tabular-nums` (veya `tabular-nums` sınıfı).
- Font boyutları: Keyfi `text-[17px]` yerine Tailwind ölçeğine sadık kal (`text-sm`, `text-base`, `text-lg`, `text-xl`).

### 3.3 Renk & Kontrast Çıkarma (Color Extraction)
- Görseldeki dominant renkleri tespit et ve rastgele hex kodları yerine semantic token'lara bağla:
  * Arka plan: `bg-background` veya `bg-slate-900`
  * Kart zemini: `bg-card` veya `bg-slate-800/50 backdrop-blur-md`
  * Vurgu (Accent): `text-primary` veya tek bir cesur renk (ör: `#21F1A8`)
- **WCAG AA Kontrast Kontrolü:** Metin ile arka plan kontrastı minimum 4.5:1 (büyük başlıklar için 3:1) olmalıdır.

### 3.4 Varlık İzolasyonu ve İkon Eşleştirme (Asset Extraction)
- Görseldeki logolar, avatarlar ve çizimler için:
  * **İkonlar:** Görseldeki ikonları asla bulanık resim olarak alma; `@phosphor-icons/react` veya `lucide-react` vektör bileşenlerine dönüştür.
  * **Resimler:** `mock-asset-provider` yeteneğinden gerçekçi fotoğraf / avatar URLs veya yerel SVG yer tutucular kullan.

### 3.5 Görsel Regresyon ve Kendi Kendini Denetleme (Visual Diffing)
- Kod üretildikten sonra ajanın kendine sorması gereken 4 soru:
  1. *Boşluk Ritmim (Padding/Margin) görselle uyumlu mu?* (İç grup `gap-2`, kart içi `p-6`, bölümler arası `py-16`).
  2. *Border Radius ve Gölgeler aşırıya mı kaçtı?* (Hafif `ring-1 ring-white/10` ve `shadow-sm` çoğu zaman aşırı `shadow-2xl`'den daha zanaatkardır).
  3. *Mobil Görünüm Ne Durumda?* (Masaüstü görseli küçülünce mobilde yatay scroll oluşuyor mu? Minimum touch target 44×44px mi?).
  4. *4 Temel Durum Yazıldı mı?* (Loading skeleton, Empty state, Error state, Feedback).
