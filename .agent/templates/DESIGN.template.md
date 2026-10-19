---
name: [Tasarım Sistemi Adı]
description: [Görsel dünyanın 1-2 cümlelik özeti; kreatif kuzey yıldızı ve renk karakteri.]

colors:
  # Brand anchors (Marka Çapaları)
  primary: "oklch(84% 0.19 80)"             # Birincil marka vurgusu / ana CTA
  secondary: "oklch(70% 0.12 188)"          # İkincil vurgu / onay ve canlı durum
  accent: "oklch(60% 0.15 35)"              # Uyarı / dikkat çekici kritik an

  # Surfaces (Zemin & Katmanlar - Asla saf #000 veya #fff kullanılmaz)
  surface-ground: "oklch(7% 0.006 95)"      # Sayfa ana zemini (mineral/sıcak koyu veya kağıt açık)
  surface-inset: "oklch(4% 0.004 95)"       # En derin oyuk zemin (inputlar, alt bilgi derinliği)
  surface-raised: "oklch(11% 0.006 95)"     # Yükseltilmiş paneller, kartlar
  surface-overlay: "oklch(15% 0.008 95)"    # Modal, popover, aktif durum pencereleri

  # Text & Content (Metin Rampası - Zemin tonuyla hafif renklenmiş veya nötr; asla jenerik soluk gri değil)
  text-primary: "oklch(91% 0 0)"            # Başlıklar, güçlü vurgular (contrast >= 7:1)
  text-body: "oklch(88% 0 0)"               # Gövde metni, okunabilir netlik (contrast >= 4.5:1)
  text-muted: "oklch(72% 0 0)"              # İkincil metin, meta veriler
  text-faint: "oklch(62% 0 0)"              # Arka plan etiketleri
  text-disabled: "oklch(52% 0 0)"           # Devre dışı durumlar

  # Borders & Rules (Çizgiler - Hairline First ilkesi)
  border-subtle: "oklch(78% 0 0 / 0.16)"    # Varsayılan 1px nötr ayırıcı çizgi
  border-strong: "oklch(74% 0.09 82 / 0.6)" # Aktif / odaklanmış marka kenarlığı

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
    fontFamily: "[Display Font], [Fallback Sans], sans-serif"
    fontSize: "clamp(2.5rem, 5vw, 4.5rem)"
    fontWeight: 300
    letterSpacing: "-0.01em"
    lineHeight: 1.05
  headline:
    fontFamily: "[Display Font / Sans], sans-serif"
    fontSize: "clamp(1.75rem, 3.5vw, 2.75rem)"
    fontWeight: 400
    lineHeight: 1.15
  body:
    fontFamily: "[Body Sans Font], system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.65
  mono:
    fontFamily: "[Mono Font], monospace"
    fontSize: "0.8125rem"
    fontWeight: 500
    letterSpacing: "0.05em"

rounded:
  none: "0"
  xs: "2px"
  sm: "4px"
  md: "6px"
  lg: "8px"
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
    rounded: "{rounded.xs}"
    padding: "0 28px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    borderColor: "{colors.border-strong}"
    rounded: "{rounded.xs}"
    padding: "0 28px"
  card:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.text-body}"
    borderColor: "{colors.border-subtle}"
    rounded: "{rounded.sm}"
    padding: "24px"
  input-text:
    backgroundColor: "{colors.surface-inset}"
    textColor: "{colors.text-primary}"
    borderColor: "{colors.border-subtle}"
    rounded: "{rounded.xs}"
    padding: "10px 14px"
---

# Design System: [Proje Adı]

## 1. Genel Bakış & Kreatif Kuzey Yıldızı (Creative North Star)

**Kreatif Kuzey Yıldızı:** "[Örn: Neo Kinpaku, Precision Industrial, Swiss Editorial, Dark Glass Minimalist vb.]"

[Tasarım felsefesinin, atmosferinin ve hissiyatının 2-3 paragraflık detaylı tanımı. Hangi klişelerden kaçınıldığı, ne tür bir fiziksel veya editoryal deneyim hedeflendiği.]

### Temel Karakteristikler:
- [Karakteristik 1: Zemin ve yüzey yaklaşımı]
- [Karakteristik 2: Vurgu renkleri ve hiyerarşi]
- [Karakteristik 3: Tipografi sesi ve ağırlık dengeleri]
- [Karakteristik 4: Kenarlıklar, derinlik ve malzeme felsefesi]

## 2. Seçilen Yüzey Modu (Surface Mode)

Bu projenin/ekranın temel yüzey modu: **[`Persuade` / `Operate` / `Read` / `Experience`]**

- **Mod Hedefi:** [Ziyaretçinin temel başarısı ve odak noktası]
- **Kısıtlar & Kurallar:**
  - *Operate modundaysa:* Tek bir kurumsal Sans-serif ailesi kullanılır, form ve tablo etiketlerinde süslü display font yasaktır. 150–250ms hızlı geçişler uygulanır, yavaş giriş koreografileri (fade-in) yasaktır. Yüksek bilgi yoğunluğu esastır.
  - *Persuade modundaysa:* Display ve body font kontrastı, tek ve amaca yönelik giriş koreografisi, ferah negatif alan.
  - *Read modundaysa:* 65–75ch okuma satır genişliği, net h1-h6 ritmi, yapışkan içindekiler tablosu (TOC).

## 3. Primitif Kiti Sözleşmesi (The Kit: Primitives First)

Her sayfa veya bileşen için sıfırdan rastgele CSS sınıfları icat etmek YASAKTIR. Önce kitteki ortak primitifler kullanılır:

- **Butonlar:** `.btn` + `.btn-primary` / `.btn-secondary` / `.btn-ghost` / `[disabled]`
- **İçerik Gruplama (Bento Grid):** `.bento-grid` + `.bento-tile` (`--span-4`, `--span-6`, `--span-8`). İç içe kart yuvalama (nested cards) kesinlikle yasaktır; hiyerarşi bento düzeniyle kurulur.
- **Bölüm İskeleti:** `.section-container`, `.section-head`, `.section-sub`. Başlıkların üzerine ezbere süs etiketleri (`eyebrow/kicker`) konulmaz.
- **Durum ve Geri Bildirim:** `.badge`, `.tag`, `.toast`, `.modal`, `.skeleton`, `.empty-state`.

## 4. Renk & Zemin Sözleşmesi

- **Ground & Surfaces:** Sayfa zemini mineral veya sıcak tonludur; saf kömür siyahı (`#000000`) veya saf beyaz (`#ffffff`) kullanılmaz.
- **Primary Accent:** Markayı ve temel aksiyonu temsil eder.
- **Secondary Accent:** İkincil durumları, canlılığı (live state) veya onay durumunu temsil eder. Süsleme amacıyla her yere dağıtılamaz.
- **Metin Kontrastı:** WCAG AA (min 4.5:1 normal metin, min 3:1 büyük metin). Renkli zeminlerde saf nötr gri metin YASAKTIR; metin rengi zemin renginin hafif tonunu (hue tint) almalıdır.
- **OKLCH Standardı:** Tüm renkler ve ton rampaları OKLCH cinsinden tanımlanır.

## 5. Tipografi & Ritim

- **Display vs Body:** Display font büyük başlıklarda (`h1`, `h2`), Body font ise gövde ve kontrollerde (`h3-h6`, `body`, butonlar, inputlar) kullanılır. Gövde fontu asla küçük boyutta display font olamaz.
- **Ağırlık Dengesi (Weight Inversion):** Hero h1 ince ve nefes alan (örn. 300), alt bölüm h2 başlıkları ise bölümü yere sabitleyen tok ağırlıkta (örn. 400-500) kurgulanabilir.
- **Okuma Genişliği:** Gövde metin blokları her zaman 65–75ch genişliğinde sınırlandırılır.

## 6. Derinlik, Malzeme ve Çizgi (Elevation & Material)

- **Hairline First:** Derinlik için ağır gölgeler yerine önce 1px net kenarlıklar (`border`) ve ton kontrastı kullanılır.
- **Tek Işık Kaynağı & No Ghost Cards:** Zemin rengi olmayan ama havada duran gölgeli kartlar yasaktır. Her yükseltinin gerçek bir yüzey zemini olmalıdır.
- **0-Blur Blok Gölge Yasağı:** `box-shadow: 4px 4px 0 ...` gibi neobrutalist blok gölgeler veya yapay zeka klişesi renkli gölgeler yasaktır.
- **No-Glass:** Zorunlu olmayan süs amaçlı cam/buzlu panel (`backdrop-blur`) ve parlayan neon parçacıklar kullanılmaz.

## 7. Tarayıcı Yüzeyleri (Themed Browser Surfaces)

- `::selection`: Marka rengi ve zemin kontrastı ile uyumlu seçim arka planı ve metin rengi.
- `caret-color`: Input odaklandığında parlayan marka aksan rengi.
- `::-webkit-scrollbar`: Sayfa ve panel temasıyla bütünleşik özel kaydırma çubuğu.
- `:focus-visible`: 2px marka vurgulu outline ve 2-4px ofset.
- `font-variant-numeric: tabular-nums`: Tablolar, sayaçlar ve sayısal veriler için hizalı rakamlar.

## 8. Kesin Yasaklar ve Kurallar (Do & Do Not)

### Do (Yapılacaklar)
- Do: Tüm renk tanımlarında OKLCH kullan.
- Do: Gölgelerden önce 1px net çizgi sınırları (`border`) kullan.
- Do: Tablo ve sayısal verilerde `tabular-nums` uygula.
- Do: Renkli zeminlerdeki metinlere zemin tonundan hafif hue kat.
- Do: Düğme ve geçişlerde `prefers-reduced-motion` kuralına tam uy.

### Do Not (Kesinlikle Yasaklar)
- Do Not: Kart içinde kart (nested cards) kullanma.
- Do Not: Başlıkların üzerine ezbere büyük harfli süs hapları (eyebrow/kicker) ekleme.
- Do Not: Metinlerde veya başlıklarda gradyan (`bg-clip-text`) kullanma.
- Do Not: Kart kenarlarına 3-4px dikey renk şeritleri (`border-l-4`) koyma.
- Do Not: 0-blur ofset blok gölgeler (`box-shadow: 4px 4px 0`) uygulama.
- Do Not: Yüzey zemini olmayan hayalet kartlara gölge verme.
- Do Not: İkon yerine emoji veya Unicode karakteri kullanma; standart SVG ikon kütüphanesi kullan.
- Do Not: Sahte süs SVG karalamaları veya rastgele noktalar ekleme.
