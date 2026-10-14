# Renk Paleti Kataloğu — İlham ve Rol Önerileri

> Bu dosya `frontend-design` skill'inin **renk ilham kaynağıdır**.
> `./themes/` klasöründeki görsellerle birlikte kullanılır: görseller
> estetik yönü verir, bu dosya **HEX değerlerini, Türkçe renk
> adlarını ve ölçülmüş kontrast/rol önerilerini** verir.

## Ne zaman kullan

1. Kullanıcı ekran/arayüz tasarladığında **önce** bu dosyaya bak.
2. Kullanıcının ruh hâline/tonuna uygun 1-2 palet seç.
3. Rol tablosundaki HEX'leri CSS değişkenine koy
   (`--color-background`, `--color-accent` ...).
4. Vurgu rengi üzerine gelecek metin rengini **beyaz/siyah
   kontrastına göre** seç (tabloda her iki değer de var).

## Rol tablosu nasıl okunur

| Rol | Anlamı |
|---|---|
| **Zemin** | Sayfa arka planı. Tema yönüne göre en açık veya en koyu. |
| **Metin** | Birincil metin rengi. Zeminle kontrastı tabloda verilir. |
| **Vurgu** | CTA, aktif öğe, marka rengi. Zeminde görünür en doygun renk. |
| **İkincil** | Kart yüzeyi, ikincil buton, sınır. |
| **Yardımcı** | Soluk metin, ikon, ayırıcı. |

Kontrast değerleri **WCAG** formülüyle ölçülmüştür:
`>= 7:1 AAA` · `>= 4.5:1 AA` · `>= 3:1 AA (büyük metin)`.
Metin/zemin çifti hedefi **AA (4.5:1)**; bu altındaki çift
yalnızca büyük başlık veya dekoratif kullanılır.

## Palet özeti

| # | Palet | Tema | Zemin | Vurgu |
|---|---|---|---|---|
| 1 | Pembe, Turuncu ve Mavi Tonları | açık | `#F5E4C4` | `#C78997` |
| 2 | Mavi, Turkuaz ve Yeşil Tonları | açık | `#E1EDD4` | `#4E9CE8` |
| 3 | Koyu Lacivert ve Laci/Lila Tonları | karanlık | `#0E0D15` | `#3D5387` |
| 4 | Bordo, Koyu Pembe ve Mavi Tonları | karanlık | `#812D35` | `#B9689F` |
| 5 | Mor ve Pembe Tonları | açık | `#F5CDD0` | `#EB6E9B` |
| 6 | Okyanus Esintisi | açık | `#F8F9F8` | `#4A89A6` |
| 7 | Şehir Ormanı | açık | `#EDF1EF` | `#4A6B5C` |
| 8 | Gün Doğumu Pasteli | açık | `#FAF0E6` | `#FBCB96` |
| 9 | Yaban Mersini & Krem | açık | `#FFF8F0` | `#C4C6E2` |
| 10 | Kuru Çiçekler | açık | `#FDFCFB` | `#C4A4A9` |
## 1. Pembe, Turuncu ve Mavi Tonları

**Tema yönü:** açık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#C78997` | Pembemsi Gri |
| `#F5B297` | Açık Mercan |
| `#F5D6A2` | Açık Şeftali |
| `#F5E4C4` | Kırık Beyaz |
| `#8A99B1` | Soluk Mavi Gri |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#F5E4C4` | Kırık Beyaz |
| metin | `#8A99B1` | Soluk Mavi Gri |
| vurgu | `#C78997` | Pembemsi Gri |
| ikincil | `#F5D6A2` | Açık Şeftali |
| yardimci | `#F5B297` | Açık Mercan |

**Metin/zemin kontrastı:** `#8A99B1` üzerinde `#F5E4C4` → **2.31:1 (yetersiz)**

**Vurgu üzerine metin:** `#C78997` üzerinde beyaz = 2.82:1 · siyah = 7.45:1 → **önerilen: `#000000`**

---

## 2. Mavi, Turkuaz ve Yeşil Tonları

**Tema yönü:** açık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#4D52B4` | Koyu Çivit |
| `#4E9CE8` | Gökyüzü Mavisi |
| `#70D6C5` | Turkuaz |
| `#CAE5BC` | Açık Salata |
| `#E1EDD4` | Buz Yeşili |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#E1EDD4` | Buz Yeşili |
| metin | `#4D52B4` | Koyu Çivit |
| vurgu | `#4E9CE8` | Gökyüzü Mavisi |
| ikincil | `#CAE5BC` | Açık Salata |
| yardimci | `#70D6C5` | Turkuaz |

**Metin/zemin kontrastı:** `#4D52B4` üzerinde `#E1EDD4` → **5.43:1 (AA)**

**Vurgu üzerine metin:** `#4E9CE8` üzerinde beyaz = 2.90:1 · siyah = 7.24:1 → **önerilen: `#000000`**

---

## 3. Koyu Lacivert ve Laci/Lila Tonları

**Tema yönü:** karanlık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#0E0D15` | Gece Siyahı |
| `#182346` | Gece Laciverti |
| `#3D5387` | Koyu Mavi |
| `#7C83AD` | Soluk Çivit |
| `#BFA9BA` | Tozlu Lila |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#0E0D15` | Gece Siyahı |
| metin | `#BFA9BA` | Tozlu Lila |
| vurgu | `#3D5387` | Koyu Mavi |
| ikincil | `#182346` | Gece Laciverti |
| yardimci | `#7C83AD` | Soluk Çivit |

**Metin/zemin kontrastı:** `#BFA9BA` üzerinde `#0E0D15` → **8.83:1 (AAA)**

**Vurgu üzerine metin:** `#3D5387` üzerinde beyaz = 7.54:1 · siyah = 2.79:1 → **önerilen: `#FFFFFF`**

---

## 4. Bordo, Koyu Pembe ve Mavi Tonları

**Tema yönü:** karanlık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#812D35` | Bordo |
| `#934772` | Koyu Pembe |
| `#B9689F` | Orta Pembe |
| `#C388A9` | Açık Pembe |
| `#536CA5` | Kurşuni Mavi |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#812D35` | Bordo |
| metin | `#C388A9` | Açık Pembe |
| vurgu | `#B9689F` | Orta Pembe |
| ikincil | `#934772` | Koyu Pembe |
| yardimci | `#536CA5` | Kurşuni Mavi |

**Metin/zemin kontrastı:** `#C388A9` üzerinde `#812D35` → **3.14:1 (AA (büyük metin))**

**Vurgu üzerine metin:** `#B9689F` üzerinde beyaz = 3.79:1 · siyah = 5.54:1 → **önerilen: `#000000`**

---

## 5. Mor ve Pembe Tonları

**Tema yönü:** açık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#826E8B` | Koyu Mor |
| `#EB6E9B` | Canlı Pembe |
| `#E69CBA` | Orta Pembe |
| `#F4B3C7` | Açık Pembe |
| `#F5CDD0` | Kırık Pembe |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#F5CDD0` | Kırık Pembe |
| metin | `#826E8B` | Koyu Mor |
| vurgu | `#EB6E9B` | Canlı Pembe |
| ikincil | `#F4B3C7` | Açık Pembe |
| yardimci | `#E69CBA` | Orta Pembe |

**Metin/zemin kontrastı:** `#826E8B` üzerinde `#F5CDD0` → **3.19:1 (AA (büyük metin))**

**Vurgu üzerine metin:** `#EB6E9B` üzerinde beyaz = 2.90:1 · siyah = 7.24:1 → **önerilen: `#000000`**

---

## 6. Okyanus Esintisi

**Tema yönü:** açık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#125167` | Derin Deniz |
| `#4A89A6` | Sakin Deniz Mavisi |
| `#F3DDC0` | Kum Beji |
| `#C7C7C7` | Sis Grisi |
| `#F8F9F8` | Cool White |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#F8F9F8` | Cool White |
| metin | `#125167` | Derin Deniz |
| vurgu | `#4A89A6` | Sakin Deniz Mavisi |
| ikincil | `#F3DDC0` | Kum Beji |
| yardimci | `#C7C7C7` | Sis Grisi |

**Metin/zemin kontrastı:** `#125167` üzerinde `#F8F9F8` → **8.30:1 (AAA)**

**Vurgu üzerine metin:** `#4A89A6` üzerinde beyaz = 3.87:1 · siyah = 5.42:1 → **önerilen: `#000000`**

---

## 7. Şehir Ormanı

**Tema yönü:** açık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#1B3A2C` | Orman Yeşili |
| `#4A6B5C` | Kayagan Gri-Yeşil |
| `#A2B0A9` | Şehir Taşı |
| `#D9DFE0` | Beton Grisi |
| `#EDF1EF` | Soft Krem |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#EDF1EF` | Soft Krem |
| metin | `#1B3A2C` | Orman Yeşili |
| vurgu | `#4A6B5C` | Kayagan Gri-Yeşil |
| ikincil | `#D9DFE0` | Beton Grisi |
| yardimci | `#A2B0A9` | Şehir Taşı |

**Metin/zemin kontrastı:** `#1B3A2C` üzerinde `#EDF1EF` → **10.92:1 (AAA)**

**Vurgu üzerine metin:** `#4A6B5C` üzerinde beyaz = 5.92:1 · siyah = 3.55:1 → **önerilen: `#FFFFFF`**

---

## 8. Gün Doğumu Pasteli

**Tema yönü:** açık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#FBCB96` | Şeftali Tozu |
| `#F8A58D` | Yumuşak Mercan |
| `#F6CFCA` | Tan Pembesi |
| `#FAF0E6` | Vanilya Kremi |
| `#F5E9DC` | Açık Bej |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#FAF0E6` | Vanilya Kremi |
| metin | `#F8A58D` | Yumuşak Mercan |
| vurgu | `#FBCB96` | Şeftali Tozu |
| ikincil | `#F5E9DC` | Açık Bej |
| yardimci | `#F6CFCA` | Tan Pembesi |

**Metin/zemin kontrastı:** `#F8A58D` üzerinde `#FAF0E6` → **1.74:1 (yetersiz)**

**Vurgu üzerine metin:** `#FBCB96` üzerinde beyaz = 1.49:1 · siyah = 14.08:1 → **önerilen: `#000000`**

---

## 9. Yaban Mersini & Krem

**Tema yönü:** açık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#3E5F81` | Yaban Mersini Mavisi |
| `#7C86A7` | Tozlu Lavanta |
| `#C4C6E2` | Yumuşak Leylak |
| `#FFF8F0` | Krem Beyazı |
| `#F2E9DE` | Soluk Kum |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#FFF8F0` | Krem Beyazı |
| metin | `#3E5F81` | Yaban Mersini Mavisi |
| vurgu | `#C4C6E2` | Yumuşak Leylak |
| ikincil | `#F2E9DE` | Soluk Kum |
| yardimci | `#7C86A7` | Tozlu Lavanta |

**Metin/zemin kontrastı:** `#3E5F81` üzerinde `#FFF8F0` → **6.31:1 (AA)**

**Vurgu üzerine metin:** `#C4C6E2` üzerinde beyaz = 1.68:1 · siyah = 12.52:1 → **önerilen: `#000000`**

---

## 10. Kuru Çiçekler

**Tema yönü:** açık · **Renk sayısı:** 5

| HEX | Renk adı |
|---|---|
| `#AF8B96` | Kuru Gül |
| `#C4A4A9` | Mat Leylak/Mauve |
| `#DAD1D2` | Vizon Beji |
| `#F2F1EF` | Tebeşir Beyazı |
| `#FDFCFB` | Fildişi |

**Rol önerisi:**

| Rol | HEX | Renk adı |
|---|---|---|
| zemin | `#FDFCFB` | Fildişi |
| metin | `#AF8B96` | Kuru Gül |
| vurgu | `#C4A4A9` | Mat Leylak/Mauve |
| ikincil | `#F2F1EF` | Tebeşir Beyazı |
| yardimci | `#DAD1D2` | Vizon Beji |

**Metin/zemin kontrastı:** `#AF8B96` üzerinde `#FDFCFB` → **2.95:1 (yetersiz)**

**Vurgu üzerine metin:** `#C4A4A9` üzerinde beyaz = 2.28:1 · siyah = 9.23:1 → **önerilen: `#000000`**

---

## Kullanım notları

- **Açık tema paletleri** (1, 2, 5, 6, 7, 8, 9, 10): zemin açık,
  metin koyu. Dashboard ve form ağırlıklı ekranlarda okunabilirlik
  en yüksek olanlardır.
- **Karanlık tema paletleri** (3, 4): zemin koyu, metin açık.
  Uzun oturum gerektiren paneller için uygundur; vurgu rengi
  zeminden yeterince ayrışmalıdır (tabloda ölçülmüştür).
- **Doygunluk yüksek vurgular** (2, 5, 7): CTA ve aktif öğe için
  güçlüdür; zeminde tek vurgu kullan, ikincil vurgu ekleme.
- **Düşük doygunluklu paletler** (6, 9, 10): kurumsal, sakin,
  'AI slop' görünümünden kaçınmak için tipografi ve spacing
  öne çıkar; renk sessiz kalmalı.
- Paletler **kopyalanabilir değilse** `ui-ux-pro-max --domain colors`
  ile aranabilir katalogda benzer sistem paletlerine bak.
