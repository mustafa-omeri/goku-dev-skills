---
name: "Goku Dev Skills Catalog — Obsidian Command Deck (Redesign)"
description: "Linear ve Raycast ilhamlı; ultra-derin OLED karbon (#090a0f), elektrik indigo (#6366f1) vurgular ve Space Grotesk display tipografisiyle güçlendirilmiş komut istasyonu."
mode: "redesign"
last_reviewed: "2026-10-28"

colors:
  primary: "#6366f1"
  secondary: "#818cf8"
  accent: "#f43f5e"
  surface-ground: "#090a0f"
  surface-inset: "#06070a"
  surface-raised: "#10121b"
  surface-overlay: "#161926"
  text-primary: "#f8fafc"
  text-body: "#e2e8f0"
  text-muted: "#94a3b8"
  text-faint: "#64748b"
  text-disabled: "#475569"
  border-subtle: "rgba(255, 255, 255, 0.08)"
  border-strong: "rgba(99, 102, 241, 0.4)"

typography:
  scale:
    "12": "0.75rem"
    "14": "0.875rem"
    "16": "1rem"
    "18": "1.125rem"
    "20": "1.25rem"
    "24": "1.5rem"
    "28": "1.75rem"
    "36": "2.25rem"
    "48": "3rem"
  display:
    fontFamily: "'Space Grotesk', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    letterSpacing: "-0.025em"
    lineHeight: 1.2
  body:
    fontFamily: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "0.94rem"
    fontWeight: 400
    lineHeight: 1.55
  code:
    fontFamily: "'JetBrains Mono', SFMono-Regular, Consolas, monospace"
    fontSize: "0.78rem"
    fontWeight: 600
    allowedSelectors: ["code", "pre", "kbd", "samp", ".kbd-shortcut", ".hero-command-box", ".quick-slash-pill", ".skill-name", ".trigger-pill", ".config-file-name", ".slash-command-title", ".table-skill-name", ".btn-header-cmd", ".nav-badge", ".stat-val", ".drawer-cli-code", ".drawer-file-name", ".list-skill-name", ".version-tag", ".chip-count", ".cat-count", ".card-index", ".drawer-cli-box", ".chain-pill"]

rounded:
  none: "0"
  xs: "4px"
  sm: "6px"
  md: "10px"
  lg: "14px"
  pill: "9999px"

spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "32px"
  xl: "48px"
  "2xl": "64px"

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.xs}"
    padding: "0.42rem 0.8rem"
  button-secondary:
    backgroundColor: "{colors.surface-overlay}"
    textColor: "{colors.text-primary}"
    borderColor: "{colors.border-subtle}"
    rounded: "{rounded.xs}"
    padding: "0.42rem 0.8rem"
  card:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.text-primary}"
    borderColor: "{colors.border-subtle}"
    rounded: "{rounded.md}"
    padding: "1.35rem"
  input-text:
    backgroundColor: "{colors.surface-inset}"
    textColor: "{colors.text-primary}"
    borderColor: "{colors.border-subtle}"
    rounded: "{rounded.sm}"
    padding: "0.75rem 2.6rem"
---

# Design System & Görsel Sözleşme: Goku Dev Skills Kataloğu (`.agent/skills-catalog.html`)

> **Aktif Mod:** `mode: redesign` — Kullanıcının `/ui-polish --redesign dark tema` talimatı uyarınca değerlendirilen 3 kreatif yön arasından **Yön B — Obsidian Command Deck (Linear / Raycast stili)** kullanıcı tarafından seçilmiş, koyu tema token'ları ve tipografi hiyerarşisi yeniden tasarlanmıştır.

## 0. Proje Kanıtı (Project Evidence)

- **Ürün & Hedef Kitle Özeti:** `skillSetWorks` ekosistemindeki 42 ajan becerisini, 20 kuralını ve 12 bağlayıcı oturum slash komutunu geliştiricilerin anında araması, tetikleyici veya örnek prompt kopyalaması için üretilen tek dosyalık interaktif HTML referans kataloğu.
- **Teknoloji & Stil Yığını:** `scripts/generate_skills_catalog.py` tarafından derlenen bağımlılıksız HTML5 + 3 Katmanlı CSS Custom Properties (`:root` Koyu ve `[data-theme="light"]` Açık tema) + Vanilla JS.
- **Ekran Envanteri & Yüzey Modu Sınıflaması:**
  | Ekran / Sekme | Yüzey Modu | Birincil Kullanıcı Görevi |
  |---|---|---|
  | **Beceriler (Grid)** | `Operate` + `Read` | 42 beceriyi kategori/konfigürasyona göre filtreleme, tetikleyici ve örnek prompt kopyalama |
  | **Slash Komutları** | `Operate` | 12 oturum slash komutunun (`/ui-polish`, `/verify-prd`, `/commitx` vb.) zincirlerini inceleme ve kopyalama |
  | **Takip Tablosu** | `Operate` | Tüm becerileri yoğun satır düzeninde (`tabular-nums`) karşılaştırma |
- **Mevcut Token / CSS Envanteri Özeti:** Koyu temada `#090a0f` karbon zemin, `#10121b` kart yüzeyi, `#161926` açılır çekmece panelleri, `#6366f1` elektrik indigo birincil vurgu, `#f43f5e` neon gül slash vurgusu, `#818cf8` menekşe ensemble vurgusu.
- **Görsel Kanıt (Screenshots):** Chrome DevTools MCP ile `1440px`, `834px` ve `390px` çözünürlüklerde Açık/Koyu tema görünümleri incelenmiştir.

## 1. Genel Bakış & Kreatif Kuzey Yıldızı (Creative North Star)

**Kreatif Kuzey Yıldızı:** **"Obsidian Command Deck"** — Linear ve Raycast hızında, ultra-derin OLED karbon zemin üzerinde sıfır dikkat dağıtıcı, yüksek kontrastlı elektrik indigo ve fütüristik geometrik tipografiyle zenginleştirilmiş komut istasyonu.

### Temel Karakteristikler:
- **Zemin ve Yüzey Yaklaşımı:** Ultra-derin OLED karbon (`#090a0f` → `#10121b` → `#161926`) ve İsviçre temizliğinde açık (`#f8fafc` → `#ffffff`) çift tema.
- **Vurgu Renkleri ve Hiyerarşi:** Elektrik İndigo (`#6366f1`), Menekşe (`#818cf8`), Neon Gül (`#f43f5e`), Zümrüt (`#10b981`) ve Kehribar (`#f59e0b`).
- **Tipografi Sesi ve Ağırlık Dengeleri:** Başlıklarda geometrik `Space Grotesk`, açıklama ve gövde metinlerinde `Plus Jakarta Sans`, yalnızca gerçek teknik tanımlayıcılar ve CLI komutlarında `JetBrains Mono`.
- **Kenarlıklar, Derinlik ve Malzeme Felsefesi:** 1px ince sınırlar (`--border-subtle`), kartların üst kenarında mikro-ortam ışıması (`box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06)`), 150ms yaylı geçişler.

## 2. Değerlendirilen Yönler (Seçim Kararı & Alternatifler)

| Yön | Felsefe & Atmosfer | Aday Palet & Font Çifti | Karar & Gerekçe |
|---|---|---|---|
| **Yön B — Obsidian Command Deck (Seçildi)** | Linear / Raycast stili; ultra-derin OLED karbon zemin, elektrik indigo vurgular, geometrik başlıklar ve cam derinliği | Karbon `#090A0F` / `#10121B` + İndigo `#6366F1` + Gül `#F43F5E` · `Space Grotesk` + `Plus Jakarta Sans` + `JetBrains Mono` | **SEÇİLDİ (Kullanıcı Tercihi)** — Geliştirici odaklı, modern, yüksek kontrastlı ve göz yormayan karanlık istasyon |
| **Yön A — Industrial Field Manual** | Dieter Rams / Teknik Saha El Kitabı; sıcak taş kağıdı ve derin grafit yüzeyler, yüksek bilgi yoğunluğu | Koyu Grafit `#111315` / Açık Sıcak Kağıt `#F5F3EF` + Bakır Turuncu `#D95D39` · `Bricolage Grotesque` + `IBM Plex Sans` + `IBM Plex Mono` | Alternatif 1 (Elendi) |
| **Yön C — Swiss Archival Index** | Basel/Zürih Editoryal İndeks; keskin 1px cetvel ızgarası, editoryal serif başlık ve ultra-net tablo | Koyu Mürekkep `#0C0F14` / Fildişi `#FAF8F5` + Kobalt `#1D4ED8` · `Instrument Serif` + `Plus Jakarta Sans` + `JetBrains Mono` | Alternatif 2 (Elendi) |

## 3. Reddedilen Varsayılanlar (Rejected Defaults)

| Reddedilen Aday / Varsayılan | Kaynak | Neden Reddedildi? | Yerine Ne Seçildi? |
|---|---|---|---|
| `Slate #0F172A + Neon Green #22C55E` | `ui-ux-pro-max/scripts/search.py --design-system` | Jenerik "matrix/hacker terminal" AI klişesi ve bayat görünüm | Ultra-derin `#090A0F` karbon + `#6366F1` elektrik indigo + `#f43f5e` neon gül |
| Sayaç, versiyon etiketi ve kategori rozetlerinde `JetBrains Mono` | Eski katalog CSS'i | `E6`/`E10` ihlali; mono font kod/komut dışı UI etiketlerinde okunabilirliği düşürür | Sayaç ve rozetlerde `Plus Jakarta Sans` + `font-variant-numeric: tabular-nums`; mono yalnızca komut ve teknik ID'lerde |
| Kart kenarlarında `border-l-4` renkli şeritler ve 0-blur gölgeler | Eski dashboard kalıpları | `E3` ve `E5` anti-slop kuralı ihlali | 1px tam çevre `border` + üst iç ortam ışıması (`inset 0 1px 0 rgba(255,255,255,0.06)`) |

## 4. Seçilen Yüzey Modu (Surface Mode)

Bu projenin temel yüzey modu: **`Operate` + `Read` (Hibrit)**

- **Mod Hedefi:** Geliştiricinin aradığı beceriyi veya slash komutunu < 3 saniyede bulup tek tıkla kopyalaması.
- **Kısıtlar & Kurallar:**
  - Yavaş sayfa giriş animasyonları yasaktır; tüm geçişler `150–200ms` aralığındadır.
  - Tüm sayaç ve tablolarda `font-variant-numeric: tabular-nums` zorunludur.

## 5. Primitif Kiti Sözleşmesi (The Kit: Primitives First)

- **Butonlar & Eylemler:** `.btn-action`, `.btn-action-slash`, `.tab-btn`, `.theme-toggle-btn`
- **Filtre & Etiketler:** `.chip`, `.quick-slash-pill`, `.trigger-pill`, `.badge`, `.cat-badge`
- **Kartlar & Tablo:** `.skill-card`, `.slash-card`, `.skills-table` (iç içe kart yuvalama yasaktır)

## 6. Renk & Zemin Sözleşmesi

- **Koyu Tema (Obsidian Command Deck):**
  - `--bg-canvas: #090a0f`
  - `--bg-surface: #10121b`
  - `--bg-surface-elevated: #161926`
  - `--text-primary: #f8fafc` (> 17:1 kontrast)
  - `--text-secondary: #94a3b8` (> 7:1 kontrast)
  - `--accent-primary: #6366f1`
  - `--accent-secondary: #818cf8`
  - `--accent-slash: #f43f5e`
- **Açık Tema:** `--bg-canvas: #f8fafc`, `--bg-surface: #ffffff`, `--bg-surface-elevated: #f1f5f9`, `--text-primary: #0f172a`, `--text-secondary: #475569`
- **Kontrast Güvencesi:** Açık temada `--accent-slash: #be123c` (>5.5:1) ve `--status-danger: #9f1239` (>7:1) ile WCAG AA/AAA standardı sağlanır.

## 7. Tipografi & Ritim

- **Display Başlık Yazı Tipi (`--font-display`):** `'Space Grotesk', 'Plus Jakarta Sans', -apple-system, sans-serif` — `h1`, `h2`, `.hero-title`, `.section-title`, `.skill-card-name`.
- **Gövde Yazı Tipi (`--font-sans`):** `'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif` — tüm gövde metinleri, butonlar, sayaç rozetleri ve tablo başlıkları.
- **Teknik/Komut Yazı Tipi (`--font-mono`):** `'JetBrains Mono', SFMono-Regular, Consolas, monospace` — yalnızca `code`, `pre`, `kbd`, `.kbd-shortcut`, `.hero-command-box`, `.quick-slash-pill`, `.skill-name`, `.trigger-pill`, `.config-file-name`, `.slash-command-title`, `.table-skill-name`.

## 8. Derinlik, Malzeme ve Tarayıcı Yüzeyleri

- `::selection`: `background: rgba(99, 102, 241, 0.3); color: #f8fafc;`
- `caret-color`: `#6366f1`
- `::-webkit-scrollbar`: `width: 8px; background: #090a0f; thumb: #161926;`
- `:focus-visible`: `2px solid #6366f1; outline-offset: 2px;`
- `font-variant-numeric: tabular-nums`

## 9. Bileşen Durum Matrisi (4 UX States)

| Bileşen / Görünüm | Default | Hover / Focus | Loading / Active | Empty / Error |
|---|---|---|---|---|
| **Arama & Kategori Çipleri** | Nötr 1px sınır + sayaç | `-1px` yükselme + vurgu kenarlığı, `:focus-visible` halka | `.active` semantik dolgu + `--text-on-accent` | `.no-results` kutusu + "Filtreleri Sıfırla" eylemi |
| **Beceri & Slash Kartı** | `--card-bg` + `--card-border` + üst mikro ortam ışıması | `-2px` yükselme + `--shadow-md` + süptil indigo ışıma | JSON çekmecesi `.open` durumu | Toast geri bildirimi (`.toast.show`) |

## 10. Responsive Davranış (390 / 834 / 1440)

| Kırılım (Viewport) | Düzen & Kolon Yapısı | Navigasyon & Filtre Ergonomisi | Dokunma Hedefi & Taşma Koruması |
|---|---|---|---|
| **Mobil (`390px`)** | Tek sütun (`grid-template-columns: 1fr`) | Yatay kaydırılabilir/sarılabilir çipler, dikey başlık | Buton ve çiplerde rahat dokunma alanı, `overflow-x: auto` tablo sarmalayıcı |
| **Tablet (`834px`)** | Tek/iki sütun adaptif ızgara | Hover-bağımsız tıklanabilir kopyalama butonları | Kart içi kod çekmecelerinde yatay kaydırma koruması |
| **Masaüstü (`1440px`)** | 3 sütun (`minmax(420px, 1fr)`) + yapışkan tablo | Klavye kısayolları (`/`, `T`, `1`, `2`, `3`, `Esc`) | `max-width: 1440px` ortalanmış konteyner |

## 11. Karar Günlüğü & Kesin Yasaklar (Decision Log & Redlines)

### Karar Günlüğü
| Tarih | Karar Özeti | Kanıt / Gerekçe | Etkilenen Token / Seçici |
|---|---|---|---|
| 2026-10-27 | Kullanıcı `/ui-polish --redesign dark tema` talebiyle Yön B — Obsidian Command Deck (Linear/Raycast) seçildi; koyu tema ultra-derin karbon zemin, elektrik indigo vurgu ve Space Grotesk display tipografisine yükseltildi | Kullanıcı seçimi + F2 Alternatif Yön Protokolü | `colors.*`, `typography.display`, `--bg-canvas`, `--accent-primary` |

### Kesin Yasaklar (Do Not)
- Do Not: Kart içinde kart (nested cards) kullanma.
- Do Not: İkon yerine emoji veya Unicode karakteri kullanma.
- Do Not: CSS kuralları içinde `var(--...)` dışında ham hex kodu (`#090d16`, `#ffffff`) kullanma.
- Do Not: `allowedSelectors` dışındaki rozet veya sayaçlarda `var(--font-mono)` kullanma.
