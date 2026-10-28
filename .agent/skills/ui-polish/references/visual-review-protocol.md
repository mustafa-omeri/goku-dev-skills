# F7 — Çoklu Çözünürlük Görsel Eleştiri ve Skor Kartı Protokolü (Visual Review & Scorecard)

Otomasyon kapılarının (`check_design_contract.py`, `check_design_slop.py`, `check_theme_contrast.py`) yeşil dönmesi tek başına yeterli değildir. Ajan, çalışan arayüzü tarayıcıda açıp görsel olarak denetlemek zorundadır.

---

## 1. Altı Görüntülü Çözünürlük × Tema Matrisi (`chrome-devtools-mcp`)

Ajan `resize_page` ve `take_screenshot` araçlarıyla aşağıdaki 6 temel durumu yakalar ve inceler:

| # | Çözünürlük (Viewport) | Tema | Kontrol Edilecek Ergonomik Kriter |
|---|---|---|---|
| 1 | `1440 × 900` (Masaüstü) | Koyu (`dark`) | Çok sütunlu yoğunluk, sticky başlıklar, klavye kısayol ipuçları |
| 2 | `1440 × 900` (Masaüstü) | Açık (`light`) | Yüzey ayrımı (1px hairline border), badge ve vurgu kontrastı (≥ 4.5:1) |
| 3 | `834 × 1112` (Tablet) | Koyu (`dark`) | 2 sütunlu dengeli ızgara, fare hover'ına bağımlı olmayan kontroller |
| 4 | `834 × 1112` (Tablet) | Açık (`light`) | Filtre ve sekme barının taşmadan sarılması veya kaydırılması |
| 5 | `390 × 844` (Mobil) | Koyu (`dark`) | Tek sütun akış, yatay kaydırılabilir filtre çipleri, ≥ 44×44px dokunma hedefleri |
| 6 | `390 × 844` (Mobil) | Açık (`light`) | Yatay taşma (`horizontal overflow = 0`), okunabilir metin boyutu |

Ayrıca etkileşimli durumlar (**Hover**, **Focus-visible**, **Boş Arama Sonucu / Empty State**) bizzat tetiklenerek doğrulanır.

---

## 2. On Maddelik Görsel Zanaat Skor Kartı (0–20 Puan)

Her madde `0` (Kusurlu / P0), `1` (Kabul Edilebilir / P1) veya `2` (Üretim Kalitesi) olarak puanlanır:

| # | Kriter | 2 Puan Standardı |
|---|---|---|
| 1 | **Görsel Hiyerarşi & İlk Bakış** | İlk 2 saniyede ana başlık, birincil arama/aksiyon ve içerik grupları net ayrışıyor |
| 2 | **Boşluk Ritmi (Spacing Rhythm)** | İç boşluklar (padding) dış ayrımlardan küçük; başlık üstü boşluk (`mt`) alt boşluktan (`mb`) büyük |
| 3 | **WCAG 2.2 AA Kontrast** | Açık ve koyu temada gövde metni ≥ 4.5:1, ikincil metin ≥ 3.0:1; soluk/okunaksız rozet yok |
| 4 | **Yüzey Modu Sadakati** | `Operate`/`Read` modunda gereksiz süs animasyonu yok; taranabilirlik ve bilgi yoğunluğu yüksek |
| 5 | **Tipografi Disiplini** | En fazla 2 font ailesi (+ yalnızca kod/komut için Mono); aşırı UPPERCASE etiket kirliliği yok |
| 6 | **4 UX Durumu (States)** | Default, Hover/Focus, Active/Filtered ve Empty State (+ Sıfırla CTA) eksiksiz çalışıyor |
| 7 | **3 Viewport Ergonomisi** | 390px, 834px ve 1440px'te yatay taşma yok; mobilde dokunma hedefleri ≥ 44px |
| 8 | **`DESIGN.md` Sözleşme Uyumu** | Kodda kullanılan tüm renkler ve fontlar `DESIGN.md` frontmatter token'larıyla birebir uyumlu |
| 9 | **Tarayıcı Yüzeyleri & Mikro-Etkileşim** | `::selection`, `caret-color`, `:focus-visible`, `tabular-nums` ve `prefers-reduced-motion` tam |
| 10 | **Sıfır Konsol & Mekanik Hata** | Tarayıcı konsolunda 0 JS hatası; 3 tasarım kapısı (`contract`, `slop`, `contrast`) 0 hata |

---

## 3. Teslimat Kapısı (Release Gate)

- **P0 (Bloklayıcı Kusur):** Skor kartında `0` puan alan herhangi bir madde veya mekanik kapılarda `E*` hatası varsa iş **teslim edilemez**; F5 adımına dönülüp düzeltilir.
- **Kabul Eşiği:** `P0 = 0` ve toplam puan **≥ 18 / 20**.
