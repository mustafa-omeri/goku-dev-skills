---
name: ui-polish
description: Tasarım sözleşmesi (DESIGN.md), zanaat tabanı ve anti-slop orkestratörü; mevcut projelerde baseline çıkarır, yeni tasarımda 11 tasarım becerisini koordine edip token, tipografi ve WCAG 2.2 AA kontrastını doğrular. Tetikleyiciler: "/ui-polish", "ui polish", "[UI-POLISH]", "arayüz parlat", "polish ui". Tetiklenmez: sıfırdan backend API ve veritabanı `musgoku`'ya aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# UI Polish & DESIGN.md Sözleşme Orkestratörü (`/ui-polish`)

Bu yetenek, web ve mobil arayüzlerin ezbere şablonlarla değil, projeye özgü **`<repo-kök>/DESIGN.md`** sözleşmesi üzerinden kanıta dayalı, production-ready ve kullanıcı dostu biçimde tasarlanmasını ve doğrulanmasını yönetir.

---

## 0. Çalışma Modu Tespiti (İlk ve Zorunlu Adım)

Tek satır CSS veya bileşen kodu değiştirmeden önce [references/discovery-protocol.md](references/discovery-protocol.md) uyarınca projenin modunu belirle:

| Durum | Aktif Mod | Zorunlu Davranış |
|---|---|---|
| Proje kökünde `DESIGN.md` **yok** VE projede mevcut çalışan arayüz **var** (Brownfield) | **1. Baseline Çıkarma Modu (`mode: baseline`)** | ⛔ **Mevcut tasarımı ve UI kodunu DEĞİŞTİRME!** Önce projenin mevcut renklerini, fontlarını, yüzeylerini ve bileşenlerini analiz ederek `.agent/templates/DESIGN.template.md` şablonundan `<repo-kök>/DESIGN.md` (`mode: baseline`) oluştur. Tasarımın değiştirilmesi yalnızca kullanıcı açıkça zorladığında (`--redesign`, `[OVERDRIVE]`, `"tasarımı değiştir / yeniden tasarla"`) yapılır. |
| Proje kökünde `DESIGN.md` **yok** VE proje sıfırdan kuruluyor (veya kullanıcı yeni tasarım istedi) | **2. Keşif & Tasarım Modu (`mode: crafted`)** | F1 Keşif → F2 3 Alternatif Yön Sunumu (**kullanıcı seçimi için dur**) → F3 Token Sözleşmesi → F4-F7 Uygulama ve Doğrulama akışını işlet. |
| Proje kökünde `DESIGN.md` **var** VE normal `/ui-polish` çağrıldı | **3. İyileştirme Modu (`Refinement`)** | Mevcut `DESIGN.md` sözleşmesine sadık kal. Token'ları ve kreatif yönü bozmadan kontrast, tipografi, 4 UX durumu, 3 viewport ergonomisi ve anti-slop kusurlarını gider (F4–F7). |
| Proje kökünde `DESIGN.md` **var** VE kullanıcı açıkça `"tasarımı değiştir / yeniden tasarla"` dedi | **4. Yeniden Tasarım Modu (`mode: redesign`)** | `PRODUCT.md` dokunulmazdır. Eski `DESIGN.md` anti-referans alınarak F1 → F2 (3 yeni yön) → Kullanıcı Seçimi → F3–F7 akışı işletilir. |

---

## 1. Tasarım Ekosistemi Rol ve Yönlendirme Tablosu (11 Skill)

`/ui-polish` tek başına karar vermez; projenin ihtiyacına göre aşağıdaki becerileri ilgili fazda devreye alır:

| Skill | `/ui-polish` İçindeki Rolü | Ne Zaman Devreye Girer? |
|---|---|---|
| `frontend-design` | Yüzey modu (`Persuade`/`Operate`/`Read`/`Experience`), 55 hazır bileşen referansı (`component-themes/`), 10 ölçülmüş palet ve zanaat tabanı | **Her zaman** |
| `ui-ux-pro-max` | Stil, palet, font eşleşmesi ve UX kuralları için **aday üretici** (çıktısı ham adaydır, elenerek kullanılır) | **Her zaman** |
| `canvas-design` | **F2 Kreatif Kuzey Yıldızı:** 1 paragraflık tasarım felsefesi kurgusu ve `canvas-fonts/` (29 küratörlü font ailesi) tipografi seçimi (UI işinde PNG/poster üretmez) | **Her zaman (F2)** |
| `design-system` | **F3 Token Mimarisi:** 3 katmanlı (`primitive` → `semantic` → `component`) token üretimi ve sabit değer doğrulaması | **Her zaman (F3)** |
| `ui-styling` | **F4–F5 Kodlama:** Tailwind CSS / shadcn/ui bileşen inşası, dark mode ve erişilebilirlik | Stack Tailwind/shadcn ise |
| `brand` | Projede `docs/brand-guidelines.md` veya kurumsal kimlik varsa renk/ton çapalarını sağlar | Marka kılavuzu varsa |
| `theme-factory` | Kullanıcı hızlı hazır palet/font teması istediğinde 10 küratörlü tema sağlar | Kullanıcı talep ettiğinde |
| `banner-design` | Arayüzde sabit ölçülü hero banner, OG kapak görseli veya reklam alanı varsa güvenli alan ve art-direction kurallarını uygular | Hero / kapak görseli varsa (F6) |
| `mock-asset-provider` | Kart, profil, ürün veya etkinlik listelerinde gri kutu yerine gerçekçi görsel varlık sağlar | Görsel içeren kart/liste varsa (F6) |
| `onboarding-tour` | Çok adımlı/karmaşık arayüzlerde Driver.js veya Joyride ile ilk kullanım rehberi kurar | Karmaşık iş akışı varsa (F6) |
| `i18n-localization` | Çok dilli arayüzlerde yeni metinlerin çeviri sözlüklerine eklenmesini denetler | Çok dilli projede (F5) |

---

## 2. Yedi Fazlı İcra Protokolü (F1 – F7)

### Faz F1 — Proje Keşfi ve Kanıt Toplama
Ayrıntı: [references/discovery-protocol.md](references/discovery-protocol.md)
1. `PRODUCT.md`, `PROJECT_BRIEF.md`, `README.md` ve mevcut CSS/bileşen dosyalarını oku.
2. Mevcut durumu mekanik kapılarla ölç:
   - `python .agent/skills/musgoku/scripts/check_design_contract.py --include-agent`
   - `python .agent/skills/musgoku/scripts/check_design_slop.py --include-agent`
   - `python .agent/skills/musgoku/scripts/check_theme_contrast.py --include-agent`
3. Çalışan arayüzün `1440px`, `834px` ve `390px` ekran görüntülerini al.
4. Mevcut bir projede ilk kez çalışılıyorsa (`mode: baseline`), mevcut tasarımı değiştirmeden `<repo-kök>/DESIGN.md` olarak belgele ve kullanıcıya raporla.

### Faz F2 — Kreatif Yön ve Reddedilen Varsayılanlar (`crafted` / `redesign` modlarında)
Ayrıntı: [references/creative-direction-protocol.md](references/creative-direction-protocol.md)
1. Hazır varlık ve aday havuzunu tara:
   - `python .agent/skills/frontend-design/scripts/get_component.py --list`
   - `python .agent/skills/frontend-design/scripts/get_palette.py --list`
   - `python .agent/skills/ui-ux-pro-max/scripts/search.py "<ürün alanı>" --design-system`
2. `canvas-design` felsefe disiplini ve `canvas-fonts/` yazı tipi setiyle projeye özgü **3 alternatif kreatif yön** hazırla.
3. Araçların önerdiği jenerik/düşük kontrastlı varsayılanları neden elediğini **Reddedilen Varsayılanlar** tablosuna yaz.
4. ⛔ **DURMA NOKTASI:** 3 yönü kullanıcıya sun ve seçimi iste. Kullanıcı yön seçmeden F3'e geçme.

### Faz F2.5 — Bilgi Mimarisi (IA) ve Yerleşim Arketipi Dönüşümü (`crafted` / `redesign`)
⛔ **Token Boyama Yanılgısı Yasağı (No Token-Only Repainting):**
Yeniden tasarım (`mode: redesign`) veya yeni tasarım (`mode: crafted`) süreçlerinde yalnızca CSS renk ve font token'larını değiştirmek KESİNLİKLE YASAKTIR. Mevcut HTML DOM yapısı korunarak yapılan yüzeysel renk değişiklikleri "AI Slop" kabul edilir. Aşağıdaki 5 Yerleşim Arketipinden en az biri seçilerek sayfa iskeleti dönüştürülmelidir:
1. **App Shell & Collapsible Dock / Sidebar** (Linear / VS Code / Raycast): Sol menü rayı, katlanabilir kategori ağacı, istatistikler ve tema anahtarı.
2. **Split-Pane & Master-Detail Slide-over Inspector** (Notion / macOS Finder): Kart/satır tıklandığında sağdan açılan detay çekmecesi/inspector.
3. **Command Bar & Quick Shortcuts Hub** (`/` veya `Ctrl+K` ile odaklanan komut arama, `ESC` ile kapatma, klavye kısayolları).
4. **Multi-Density View Switcher** (Izgara ⊞ vs Kompakt Liste ☰ vs Tablo).
5. **Bento Grid & Modüler Veri Panosu** (Veri yoğunluklu operasyonel ekranlar).
6. **Adaptive Action Hub & Bottom-Sheet Pattern** (10+ eylem veya komut içeren alanlarda yatay scroll veya dağınık hap dizilimi yerine 100 öğeye ölçeklenebilen `panel-only` ve `preview-and-panel` alttan açılan kart hub'ı mimarisi).
*Hazır Bileşen Enjeksiyonu:* `python .agent/skills/frontend-design/scripts/get_component.py --type sidebars` ve `--type cards` komutlarıyla diske sorulup hazır test edilmiş şablonlar koda uyarlanmalıdır.

### Faz F3 — Token Sözleşmesi ve `DESIGN.md` Mühürleme (`design-system`)
1. Seçilen yönü (veya mevcut baseline'ı) `<repo-kök>/DESIGN.md` YAML frontmatter (`colors`, `typography`, `rounded`, `spacing`, `components`) ve 12 standart bölüm olarak yaz.
2. Projede `tokens.json` kullanılıyorsa CSS/Tailwind çıktısını üret ve doğrula:
   - `node .agent/skills/design-system/scripts/generate-tokens.cjs --config tokens.json -o tokens.css`
   - `node .agent/skills/design-system/scripts/validate-tokens.cjs --dir src`

### Faz F4 — Bileşen Kiti, Etkileşim Envanteri ve UX Durumu (`frontend-design` + `ui-styling`)
1. **Etkileşim Envanteri ve İşlevsel Tamamlanma (Kural A):** Sayfadaki her tıklanabilir/etkileşimli kontrolün (görünüm butonları, sekmeler, arama/filtre, açılır menüler) olay bağlayıcısını, görünüm durumu (`aria-pressed`, `aria-selected`) ve DOM render döngüsünü eşleştir. Desteklenmeyen bağlamlarda sahte/ölü buton bırakma.
2. İlgili bileşen şablonlarını incele:
   - `python .agent/skills/frontend-design/scripts/get_component.py --category cards`
3. Her bileşen için **4 UX Durumunu** (`Default`, `Hover/Focus`, `Loading/Active`, `Empty/Error + Sıfırla CTA`) ve **3 Viewport Ergonomisini** (`390px` mobil 44px dokunma hedefi ve responsive sarma/açılır komut paleti — A.13 anti-scroll slop, `834px` tablet akıcı sütun, `1440px` masaüstü yoğun görünüm) tasarla. Eylem/komut gruplarında "100 Öğe Sorusu" (B.9) ve Eşit Boyutlu Kart Sözleşmesini (Equal Dimensions Card Contract) uygula.

### Faz F5 — Cerrahi Kod Uygulaması
1. Tüm renkleri ve yazı tiplerini `DESIGN.md` token'larına bağla; kural içi ham hex (`E9`) ve kod dışı mono font (`E6`/`E10`) sızıntılarını temizle.
2. Tarayıcı yüzeylerini (`::selection`, `caret-color`, `:focus-visible`, `::-webkit-scrollbar`, `tabular-nums`, `prefers-reduced-motion`) eksiksiz uygula.

### Faz F6 — Koşullu Varlıklar (`banner-design`, `mock-asset-provider`, `onboarding-tour`)
- Görsel kart/liste varsa: `python .agent/skills/mock-asset-provider/scripts/fetch_assets.py --help`
- Hero/kapak alanı varsa `banner-design` güvenli alan kurallarını uygula.

### Faz F7 — Mekanik Doğrulama ve Görsel Skor Kartı
Ayrıntı: [references/visual-review-protocol.md](references/visual-review-protocol.md)
1. Üç zorunlu mekanik kapıyı çalıştır (`0 hata` zorunlu):
   - `python .agent/skills/musgoku/scripts/check_design_contract.py --include-agent --strict`
   - `python .agent/skills/musgoku/scripts/check_design_slop.py --include-agent`
   - `python .agent/skills/musgoku/scripts/check_theme_contrast.py --include-agent`
2. `chrome-devtools-mcp` ile `1440px`, `834px`, `390px` × `Açık/Koyu` (6 görüntü) yakala ve **10 Maddelik Görsel Zanaat Skor Kartını** doldur (`P0 = 0` ve skor `≥ 18/20` olmadan işi tamamlandı sayma).
