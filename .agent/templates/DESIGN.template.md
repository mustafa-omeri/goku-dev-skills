---
name: "<doldur: Tasarım Sistemi Adı>"
description: "<doldur: Görsel dünyanın 1-2 cümlelik özeti; kreatif kuzey yıldızı ve renk karakteri>"
mode: "<doldur: baseline | crafted | redesign>"
last_reviewed: "<doldur: YYYY-MM-DD>"

colors:
  # Brand anchors (Marka Çapaları — OKLCH veya HEX)
  primary: "<doldur: birincil marka vurgusu / ana CTA; şablondan kopyalama>"
  secondary: "<doldur: ikincil vurgu / onay ve canlı durum>"
  accent: "<doldur: uyarı / dikkat çekici kritik an>"

  # Surfaces (Zemin & Katmanlar — Asla saf #000000 veya #ffffff kullanılmaz)
  surface-ground: "<doldur: sayfa ana zemini>"
  surface-inset: "<doldur: en derin oyuk zemin (inputlar, kod kutuları)>"
  surface-raised: "<doldur: yükseltilmiş paneller, kartlar>"
  surface-overlay: "<doldur: modal, popover, aktif durum pencereleri>"

  # Text & Content (Metin Rampası — Zemin tonuyla hafif renklenmiş; WCAG AA zorunlu)
  text-primary: "<doldur: başlıklar, güçlü vurgular (kontrast >= 7:1)>"
  text-body: "<doldur: gövde metni, okunabilir netlik (kontrast >= 4.5:1)>"
  text-muted: "<doldur: ikincil metin, meta veriler (kontrast >= 3.0:1)>"
  text-faint: "<doldur: arka plan etiketleri>"
  text-disabled: "<doldur: devre dışı durumlar>"

  # Borders & Rules (Çizgiler — Hairline First ilkesi)
  border-subtle: "<doldur: varsayılan 1px nötr ayırıcı çizgi>"
  border-strong: "<doldur: aktif / odaklanmış marka kenarlığı>"

typography:
  scale:
    "12": "0.75rem"      # Meta satırları, rozetler, kod parçaları
    "14": "0.875rem"     # Yoğun gövde metni, kontroller, liste satırları
    "16": "1rem"         # Standart gövde metni (root 16px)
    "18": "1.125rem"     # Giriş paragrafları, kart başlıkları
    "20": "1.25rem"      # Panel ve alt bölüm başlıkları
    "24": "1.5rem"       # Bölüm başlıkları (h3)
    "28": "1.75rem"      # Büyük bölüm başlıkları (h2)
    "36": "2.25rem"      # Sayfa ana başlıkları (h1)
    "48": "3rem"         # Display başlıklar
  display:
    fontFamily: "<doldur: Display Font, Fallback Sans, sans-serif>"
    fontSize: "clamp(2.25rem, 4vw, 3.75rem)"
    fontWeight: 600
    letterSpacing: "-0.02em"
    lineHeight: 1.1
  body:
    fontFamily: "<doldur: Body Sans Font, system-ui, sans-serif>"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  code:
    fontFamily: "<doldur: Mono Font, monospace>"
    fontSize: "0.8125rem"
    fontWeight: 500
    allowedSelectors: ["code", "pre", "kbd", "samp"]

rounded:
  none: "0"
  xs: "<doldur: ör. 4px>"
  sm: "<doldur: ör. 6px>"
  md: "<doldur: ör. 8px>"
  lg: "<doldur: ör. 12px>"
  pill: "999px"

spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "32px"
  xl: "48px"
  "2xl": "80px"

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface-ground}"
    rounded: "{rounded.sm}"
    padding: "0 20px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.text-primary}"
    borderColor: "{colors.border-strong}"
    rounded: "{rounded.sm}"
    padding: "0 20px"
  card:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.text-body}"
    borderColor: "{colors.border-subtle}"
    rounded: "{rounded.lg}"
    padding: "24px"
  input-text:
    backgroundColor: "{colors.surface-inset}"
    textColor: "{colors.text-primary}"
    borderColor: "{colors.border-subtle}"
    rounded: "{rounded.sm}"
    padding: "10px 14px"
---

# Design System & Görsel Sözleşme: <doldur: Proje Adı>

> ⛔ **Mod Seçimi ve Mevcut Projeleri Koruma Kuralı (Brownfield vs Greenfield):**
> - **`mode: baseline` (Mevcut Projeler):** Halihazırda çalışan bir arayüzü olan projede `DESIGN.md` ilk kez oluşturulurken **mevcut tasarım ASLA değiştirilmez**. Önce projenin mevcut renkleri, fontları, yüzeyleri ve bileşenleri olduğu gibi analiz edilerek bu dosyaya kayıt altına alınır. Tasarımın değiştirilmesi yalnızca kullanıcı açıkça talep ettiğinde (`--redesign`, `[OVERDRIVE]`, `"tasarımı değiştir / yeniden tasarla"`) yapılır.
> - **`mode: crafted` / `mode: redesign`:** Sıfırdan kurulan projelerde veya kullanıcının açıkça tasarım yenilemesi istediği durumlarda F1 Keşif → F2 3 Alternatif Yön Seçimi → F3 Token Üretimi zinciriyle doldurulur.

## 0. Proje Kanıtı (Project Evidence)

- **Ürün & Hedef Kitle Özeti:** `<doldur: PRODUCT.md veya README.md'den çıkarılan gerçek kullanıcı ve kullanım senaryosu>`
- **Teknoloji & Stil Yığını:** `<doldur: ör. React + Vite + Tailwind v4 / Saf HTML+CSS>`
- **Ekran Envanteri & Yüzey Modu Sınıflaması:**
  | Ekran / Rota | Yüzey Modu (`Persuade` / `Operate` / `Read` / `Experience`) | Birincil Kullanıcı Görevi |
  |---|---|---|
  | `<doldur: ekran>` | `<doldur: mod>` | `<doldur: görev>` |
- **Mevcut Token / CSS Envanteri Özeti:** `<doldur: kod tabanında tespit edilen mevcut renkler, fontlar, yarıçaplar>`
- **Görsel Kanıt (Screenshots):** `<doldur: incelenen 1440 / 834 / 390 ekran görüntüsü referansları>`

## 1. Genel Bakış & Kreatif Kuzey Yıldızı (Creative North Star)

**Kreatif Kuzey Yıldızı:** `<doldur: Projenin iş alanına özgü kreatif yön adı ve 1 paragraflık tasarım felsefesi (canvas-design disipliniyle)>`

### Temel Karakteristikler:
- **Zemin ve Yüzey Yaklaşımı:** `<doldur>`
- **Vurgu Renkleri ve Hiyerarşi:** `<doldur>`
- **Tipografi Sesi ve Ağırlık Dengeleri:** `<doldur>`
- **Kenarlıklar, Derinlik ve Malzeme Felsefesi:** `<doldur>`

## 2. Değerlendirilen Yönler (veya Mevcut Baseline Özeti)

> `mode: baseline` ise burada mevcut tasarımın karakteristik özeti yazılır. `mode: crafted` veya `mode: redesign` ise F2 aşamasında değerlendirilen 3 alternatif yön ve seçilen yönün gerekçesi belgelenir.

| Yön | Felsefe & Atmosfer | Aday Palet & Font Çifti | Karar & Gerekçe |
|---|---|---|---|
| **Yön A** | `<doldur>` | `<doldur>` | `<doldur: Seçildi / Elendi — neden?>` |
| **Yön B** | `<doldur>` | `<doldur>` | `<doldur: Seçildi / Elendi — neden?>` |
| **Yön C** | `<doldur>` | `<doldur>` | `<doldur: Seçildi / Elendi — neden?>` |

## 3. Reddedilen Varsayılanlar (Rejected Defaults)

> ⛔ Araçların (`ui-ux-pro-max`, `get_palette.py` vb.) veya LLM eğitim ortalamasının önerdiği jenerik kalıplardan hangilerinin bu proje için neden reddedildiği aşağıda kayıt altına alınır:

| Reddedilen Aday / Varsayılan | Kaynak | Neden Reddedildi? | Yerine Ne Seçildi? |
|---|---|---|---|
| `<doldur: ör. Slate #0f172a + Sky #38bdf8>` | `<doldur: LLM / search.py>` | `<doldur: Jenerik AI dashboard klişesi>` | `<doldur: Seçilen karakterli alternatif>` |
| `<doldur: ör. Etiketlerde JetBrains Mono>` | `<doldur: Mevcut kod / varsayılan>` | `<doldur: Mono yalnızca kod bloklarında kullanılır>` | `<doldur: Gövde sans fontu + ağırlık kontrastı>` |

## 4. Seçilen Yüzey Modu (Surface Mode)

Bu projenin temel yüzey modu: **`<doldur: Persuade | Operate | Read | Experience>`**

- **Mod Hedefi:** `<doldur: Ziyaretçinin temel başarısı ve odak noktası>`
- **Kısıtlar & Kurallar:**
  - *Operate modundaysa:* Tek bir kurumsal Sans-serif ailesi (artı yalnızca kod/komut için Mono) kullanılır; form ve tablo etiketlerinde süslü display font yasaktır. 150–250ms hızlı geçişler uygulanır, yavaş giriş koreografileri (fade-in) yasaktır. Yüksek bilgi yoğunluğu esastır.
  - *Persuade modundaysa:* Display ve body font kontrastı, tek ve amaca yönelik giriş koreografisi, ferah negatif alan.
  - *Read modundaysa:* 65–75ch okuma satır genişliği, net h1-h6 ritmi, yapışkan içindekiler tablosu (TOC).

## 5. Primitif Kiti Sözleşmesi (The Kit: Primitives First)

Her sayfa veya bileşen için sıfırdan rastgele CSS sınıfları icat etmek YASAKTIR. Önce kitteki ortak primitifler kullanılır:

- **Butonlar:** `.btn` + `.btn-primary` / `.btn-secondary` / `.btn-ghost` / `[disabled]`
- **İçerik Gruplama (Bento / Grid):** İç içe kart yuvalama (nested cards) kesinlikle yasaktır; hiyerarşi yüzey tonu ve negatif alanla kurulur.
- **Bölüm İskeleti:** Başlıkların üzerine ezbere süs etiketleri (`eyebrow/kicker`) konulmaz.
- **Durum ve Geri Bildirim:** `.badge`, `.tag`, `.toast`, `.modal`, `.skeleton`, `.empty-state`.

## 6. Renk & Zemin Sözleşmesi

- **Ground & Surfaces:** Sayfa zemini mineral veya sıcak/soğuk tonludur; saf kömür siyahı (`#000000`) veya saf beyaz (`#ffffff`) kullanılmaz.
- **Primary Accent:** Markayı ve temel aksiyonu temsil eder.
- **Secondary Accent:** İkincil durumları, canlılığı (live state) veya onay durumunu temsil eder.
- **Metin Kontrastı:** WCAG AA (min 4.5:1 normal metin, min 3.0:1 ikincil/muted metin). Renkli zeminlerde saf nötr gri metin YASAKTIR; metin rengi zemin renginin hafif tonunu (hue tint) almalıdır.

## 7. Tipografi & Ritim

- **En Fazla 2 Font Ailesi (+ Kod için Mono):** Display ve Body (veya tek bir Sans ailesi) dışında sayfa genelinde üçüncü bir yazı tipi kullanılamaz. Monospace font yalnızca gerçek kod, terminal komutu, kısayol (`code`, `pre`, `kbd`, `samp`) ve frontmatter'da açıkça izin verilen teknik seçicilerde kullanılır.
- **Okuma Genişliği:** Gövde metin blokları her zaman 65–75ch genişliğinde sınırlandırılır.

## 8. Derinlik, Malzeme ve Tarayıcı Yüzeyleri

- **Hairline First:** Derinlik için ağır gölgeler yerine önce 1px net kenarlıklar (`border`) ve ton kontrastı kullanılır.
- **0-Blur Blok Gölge Yasağı:** `box-shadow: 4px 4px 0 ...` gibi neobrutalist blok gölgeler yasaktır.
- **Tarayıcı Yüzeyleri (Themed Browser Surfaces):**
  - `::selection`: Marka rengi ve zemin kontrastı ile uyumlu seçim arka planı ve metin rengi.
  - `caret-color`: Input odaklandığında marka aksan rengi.
  - `::-webkit-scrollbar`: Sayfa ve panel temasıyla bütünleşik özel kaydırma çubuğu.
  - `:focus-visible`: 2px marka vurgulu outline ve 2-4px ofset.
  - `font-variant-numeric: tabular-nums`: Tablolar, sayaçlar ve sayısal veriler için hizalı rakamlar.

## 9. Bileşen Durum Matrisi (4 UX States)

| Bileşen / Görünüm | Default | Hover / Focus | Loading / Active | Empty / Error |
|---|---|---|---|---|
| `<doldur: ör. Arama & Filtre>` | `<doldur>` | `<doldur: 2px focus ring>` | `<doldur>` | `<doldur: Sıfır sonuç + Filtreyi Temizle CTA>` |
| `<doldur: ör. Kart / Satır>` | `<doldur>` | `<doldur>` | `<doldur>` | `<doldur>` |

## 10. Responsive Davranış (390 / 834 / 1440)

| Kırılım (Viewport) | Düzen & Kolon Yapısı | Navigasyon & Filtre Ergonomisi | Dokunma Hedefi & Taşma Koruması |
|---|---|---|---|
| **Mobil (`390px`)** | `<doldur: tek sütun / kart görünümü>` | `<doldur: yatay kaydırılabilir çipler / alt bar>` | `<doldur: min 44x44px dokunma hedefi>` |
| **Tablet (`834px`)** | `<doldur: 2 sütun dengeli ızgara>` | `<doldur: hover-bağımsız kontroller>` | `<doldur>` |
| **Masaüstü (`1440px`)** | `<doldur: 3+ sütun yoğun ızgara + tablo>` | `<doldur: klavye kısayolları + sticky bar>` | `<doldur>` |

## 11. Karar Günlüğü & Kesin Yasaklar (Decision Log & Redlines)

### Karar Günlüğü
| Tarih | Karar Özeti | Kanıt / Gerekçe | Etkilenen Token / Seçici |
|---|---|---|---|
| `<doldur: YYYY-MM-DD>` | `<doldur: İlk sözleşme oluşturuldu>` | `<doldur>` | `<doldur: Tüm tokenlar>` |

### Kesin Yasaklar (Do Not)
- Do Not: Kart içinde kart (nested cards) kullanma.
- Do Not: Başlıkların üzerine ezbere büyük harfli süs hapları (eyebrow/kicker) ekleme.
- Do Not: Metinlerde veya başlıklarda gradyan (`bg-clip-text`) kullanma.
- Do Not: Kart kenarlarına 3-4px dikey renk şeritleri (`border-l-4`) koyma.
- Do Not: Kod/komut (`code`, `pre`, `kbd`) dışındaki başlık, rozet veya etiketlerde monospace font kullanma.
- Do Not: İkon yerine emoji veya Unicode karakteri kullanma; standart SVG ikon kütüphanesi kullan.
- Do Not: Sözleşmede (`DESIGN.md`) tanımlı olmayan ham hex/rgb renkleri CSS veya bileşen içine gömme.
