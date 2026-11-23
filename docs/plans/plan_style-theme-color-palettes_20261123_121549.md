# Style Theme Color Palettes Entegrasyonu ve Renk Esinlenme Yönetişimi Uygulama Planı
<!--
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2 · .agent/rules/aviation-documentation-standard.md (FAA AC 121-24C + /caveman)
-->

> **Hedef Dal / Sürüm:** `main / v1.43.0` · **Tarih:** `2026-11-23`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `musgoku, tdd, ui-polish, frontend-design, ui-ux-pro-max, design-system, theme-factory, canvas-design, feature-architect`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`)  
> **İlgili KANBAN Kartı:** `S2-18 (GSW-UI-001 .. GSW-UI-004)`  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. [Goal Description] (Amaç & Kapsam)

`docs/plans/style_theme_color_palettes.md` dosyasında tanımlanan **88 yeni renk temasını** (6 Özel/Başlangıç, 10 Konsept, 72 Koleksiyon 01–18), `skillSetWorks` içindeki tüm dağıtılabilir UI/UX yapısına (`.agent/`) tanıtmak; `16 Resmi Kilitli Tema` (`themes.css`) omurgasını koruyarak bu 88 paleti **İlham & WCAG Türetim Kataloğu** olarak CLI köprülerine (`get_palette.py`, `search.py`) bağlamak ve tasarım kural setimize **Esinlenme + Tek-Taraflı Seçim Yasağı** hükmünü eklemek.

**Kapatılan Boşluklar:**
1. **Dağıtım Körü Noktası:** `docs/plans/` hedef projelere (`delivery.py`) dağıtılmaz; `.agent/` içine taşınmadıkça hedef projelerdeki ajanlar 88 paleti göremez.
2. **Keşif Sürtünmesi (Lesson #38):** CLI köprüsü (`get_palette.py` ve `ui-ux-pro-max/scripts/search.py`) yalnızca `palette-catalog.md` içindeki 10 paleti ve `colors.csv` (192 palet) verisini tarıyor; 88 yeni palet CLI aramasına bağlı değil.
3. **Kural & Süreç Boşluğu:** Ajanın eski + 88 yeni paletlerden esinlenerek ilerlemesi, tek başına *"ben projeye en uygun bu kombinasyonu seçtim ve ilerliyorum"* dememesi, jenerik/ezbere AI-slop sürecine düşmeden standart **F1 -> F2 (3 alternatif + palet esin kaynağı + eleme gerekçesi) -> Kullanıcı Onayı -> F3 Token -> WCAG Kapıları** akışını izlemesi açık kural olarak tüm temas noktalarında mühürlenmeli.

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: 88 Style Theme Color Palettes Entegrasyonu ve Anti-Unilateral Seçim Kuralı
  Scenario: CLI köprüleri 88 yeni paleti tarar ve WCAG AA uyumlu token önerisi üretir
    Given .agent/skills/frontend-design/themes/style-theme-palettes.md dosyası 88 paleti içerir
    When kullanıcı veya ajan get_palette.py --style-themes veya search.py "<anahtar-kelime>" çalıştırır
    Then 88 palet içinden eşleşen adaylar listelenir, --style "<tema>" --format css ile WCAG >= 4.5:1 rol eşlemesi üretilir ve parse_catalog() 10 palet sözleşmesi bozulmaz

  Scenario: Tasarım kuralları ve skiller tek-taraflı renk seçimini yasaklar
    Given design-skills-enforcement.md, ui-polish, frontend-design, creative-direction-protocol.md ve şablonlar güncellenmiştir
    When ajan F2 kreatif yön veya /ui-polish çalıştırır
    Then ajan "ben seçtim, ilerliyorum" diyemez; eski + 88 yeni paletlerden esinlenen 3 alternatifi, esin kaynağını, WCAG kontrastını ve Reddedilen Varsayılanlar gerekçesini sunup kullanıcı onayını bekler
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (2+ Seçenek İncelemesi)

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Sadece Doküman / Statik MD)** | `style_theme_color_palettes.md` dosyasını kopyala ve kurallara metin ekle | Minimum kod değişikliği, hızlı | CLI (`get_palette.py`, `search.py`) görmez; ham 3-4 renkli paletlerde WCAG kontrastı ölçülmeden hatalı CSS üretme riski; Discovery Friction (Lesson #38) | 1.4 |
| **Option B (Dağıtılabilir Katalog + WCAG CLI Köprüsü + Kural/Katalog Senkronu — Seçildi)** | `themes.css` 16 Kilitli Tema korunur; 88 palet `style-theme-palettes.md` olarak `.agent/`'a alınır; `get_palette.py` + `search.py` WCAG AA rol türetimi ekler; kural/skill/şablon/katalog tam senkronlanır | Sıfır sürtünmeli arama, otomatik WCAG >= 4.5:1 koruma, `parse_catalog()` 10 palet testi kırılmaz, `delivery.py` ile tüm projelere dağıtılır | `generate_skills_catalog.py` ve `test_theme_bridge.py` / `test_skill_contracts.py` güncelliği zorunlu | **2.8** |

- **Seçilen Yol & Gerekçe:** **Option B** (Kullanıcı A2 tercihi + Lesson #38 uyumu). `16 Kilitli Tema (themes.css)` omurgası bozulmaz; 88 palet CLI + WCAG matematiksel rol çözümlemesiyle doğrudan kullanılabilir ve denetlenebilir hale gelir.
- **Birleşik Planlama Ekosistemi Bağlantısı:** `style_theme_color_palettes.md` -> `theme-skeleton-matching.md` & `design-skills-enforcement.md` -> `KANBAN.md` (`S2-18`) -> TDD Kırmızı/Yeşil (`test_theme_bridge.py` & `test_theme_skeleton_integration.py`) -> `run_all_gates.py`.

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)

> [!IMPORTANT]
> **Kullanıcı Onaylı Mimari Kararlar (Netleştirildi):**
> 1. **Kural Davranışı (A1):** Ajan tek başına *"ben projeye en uygun bu kombinasyonu seçtim ve ilerliyorum"* **DEMEMELİ** ve ezbere/jenerik AI-slop süreciyle **ilerlememeli**. Standart F1 -> F2 (3 alternatif + kullanıcı onayı) kapısından geçerken, her adayda hangi paletten esinlendiğini, neden uygun olduğunu ve elenen alternatiflerin/varsayılanların neden reddedildiğini (`Reddedilen Varsayılanlar`) açıkça beyan eder.
> 2. **Katalog Mimarisi (A2):** `themes.css` içindeki `16 Kilitli Tema` omurgası korunur; 88 palet `.agent/skills/frontend-design/themes/style-theme-palettes.md` olarak dağıtılan **"İlham & Türetim Kataloğu"** rolünde eklenir; `get_palette.py` + `search.py` üzerinden WCAG AA rol eşlemesiyle `DESIGN.md` / CSS değişkenlerine türetilir.
> 3. **Çift Katmanlı Güvenlik:** `palette-catalog.md` (10 ölçülmüş palet) ve `colors.csv` (192 satır) sözleşmeleri aynen korunur; mevcut `test_theme_bridge.py` (`len == 10`) ve `test_data_contracts.py` (`No 1-192`) kırılmaz.
>
> **2-Modlu Onay Seçenekleri (Planı Nasıl İlerletelim?):**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan` / `"planı mühürle, kodlama yapma"`):** Planı `docs/plans/` altına arşivler, `HANDOFF.md` §3 Gelecek Fazlar (`⬜ Bekliyor`) ve `KANBAN.md` `Bekliyor` sütununa işler; **kod yazmadan durur**.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onayla ve başla"`):** Faz 0 mühürlemesini yapıp hemen Faz 1 (TDD Kırmızı Test) ile geliştirmeye başlar.

## 4. Open Questions (Açık Sorular)
Açık soru bulunmamaktadır (A1 ve A2 kullanıcı yanıtlarıyla netleştirilmiştir).

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)

| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-UI-001` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3 + `KANBAN.md`) | `S2-18` · 88 Style Theme kataloğunun `.agent/`'a taşınması ve `get_palette.py` + `search.py` WCAG rol türetim köprüsü |
| `GSW-UI-002` | `Bekliyor` | `Yapılıyor` | `S2-18` · `design-skills-enforcement.md`, `ui-polish`, `creative-direction-protocol.md`, `skill-routing-matrix.md` içine Esinlenme + Tek-Taraflı Seçim Yasağı kuralı |
| `GSW-UI-003` | `Bekliyor` | `Yapılıyor` | `S2-18` · Kardeş skiller (`frontend-design`, `ui-ux-pro-max`, `theme-factory`, `design-system`), `theme-skeleton-matching.md`, `PLAN.template.md`, `DESIGN.template.md` ve `skills-catalog.html` senkronu |
| `GSW-UI-004` | `Bekliyor` | `Yapılıyor` | `S2-18` · Regresyon testleri (`test_theme_bridge.py`, `test_theme_skeleton_integration.py`), `run_all_gates.py`, `test_skills_catalog.py` ve `docs/KULLANICI_TEST_REHBERI.md` güncellemesi |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
`Tek Repo / Kardeş Uygulama Etkisi Yok` (Değişiklikler kaynak repo `skillSetWorks/.agent/` içinde hazırlanır; hedef projelere dağıtım yalnız kullanıcının açık `delivery.py` komutu ile yapılır).

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Skillset & CLI Eşlemesi)

> 💡 Bu depo uygulama/DB kodu yerine kural, skill ve Python CLI köprüleri içerdiğinden 5 katman bu mimarinin gerçek katmanlarına eşlenir:

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. Veri & Katalog Kaynağı** | 88 paleti `.agent/` dağıtım ağacına alma; `Özel (6)`, `Konsept (10)`, `Koleksiyon 01-18 (72)` ayrıştırma formatı + `themes.css` eşleme notu | `.agent/skills/frontend-design/themes/style-theme-palettes.md` (`[NEW]`) |
| **2. CLI Motoru & WCAG Türetim** | `get_palette.py` içine `parse_style_themes()`, `search_style_themes()`, `derive_style_theme_roles()` (sRGB relative luminance + WCAG >= 4.5:1 otomatik ton ayarı) ve `--style-themes`, `--style`, `--mode`, `--format design-md` bayrakları | `.agent/skills/frontend-design/scripts/get_palette.py` (`[MODIFY]`) |
| **3. Merkezi Arama Köprüsü** | `ui-ux-pro-max/scripts/search.py` `get_local_recommendations()` içine 88 style theme eşleşmesi ve `get_palette.py --style` komutu enjeksiyonu | `.agent/skills/ui-ux-pro-max/scripts/search.py` (`[MODIFY]`) |
| **4. Kural, Skill, Şablon & Katalog** | Esinlenme + Tek-Taraflı Seçim Yasağı kuralı + F2 3 alternatif zorunluluğu + `generate_skills_catalog.py` / `.agent/skills-catalog.html` yeniden derleme | `.agent/rules/design-skills-enforcement.md`, `.agent/skills/*/SKILL.md`, `.agent/templates/*.md`, `scripts/generate_skills_catalog.py` |
| **5. Doğrulama & Kullanıcı Test Rehberi** | Regresyon testleri + birleşik kalite kapıları (`run_all_gates.py`, `test_skill_contracts`, `test_skills_catalog.py`) + `docs/KULLANICI_TEST_REHBERI.md` adımları | `tests/test_theme_bridge.py`, `tests/test_theme_skeleton_integration.py`, `docs/KULLANICI_TEST_REHBERI.md` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi (Theme & Component Skeleton Contract)

| İskelet Boyutu | Seçilen Şablon / Kaset / Token | Kaynak / CLI Komutu |
|---|---|---|
| **1. Yaşayan Yüzey & 16 Kilitli Tema + 88 İlham Paleti** | Mevcut `Obsidian Command Deck` (`DESIGN.md`) korunur; 16 Kilitli Tema (`themes.css`) + **88 Style Theme Palettes** (`style-theme-palettes.md`) + 10 Ölçülmüş Palet + 192 `colors.csv` | `.agent/skills/ui-polish/references/themes.css` & `python .agent/skills/frontend-design/scripts/get_palette.py --style-themes` |
| **2. 55+ Doğrulanmış Bileşen Teması** | Katalog UI bileşeni değişmez (`scripts/generate_skills_catalog.py` metadata güncellemesi) | `python .agent/skills/frontend-design/scripts/get_component.py --list` |
| **3. 18 Doğrulanmış Dashboard Şablonu** | Dashboard Kapsam Dışı | `.agent/skills/frontend-design/dashboard-theme/catalog.json` |
| **4. Zero-CLS Skeleton Kaseti & 4 UX Durumu** | Kural ve şablonlarda 4 UX durumu + Zero-CLS Skeleton sözleşmesi aynen korunur | `ui-polish` & `check_design_slop.py` |
| **5. Görsel Varlık & Karşılama Turu** | Gerekmiyor | — |

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 & Sprint Açılışı)
1. **[Adım 1 - Planı `docs/plans/` Altına Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug style-theme-color-palettes` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_style-theme-color-palettes_<YYYYMMDD_HHMMSS>.md`
2. **[Adım 2 - `HANDOFF.md` §3 & `KANBAN.md` Güncelle]:** `GSW-UI-001..004` görevlerini `HANDOFF.md` §3 canlı panosuna ve `S2-18` kartını `KANBAN.md` `Yapılıyor` sütununa işle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0 hata, 0 W3 uyarısı` ve `check_sprint_board.py` `[OK]` döner.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - `test_theme_bridge.py` Kırmızı Testleri Yaz]:** `tests/test_theme_bridge.py` içine `parse_style_themes()` (88 tema: 6 Özel, 10 Konsept, 72 Koleksiyon), `search_style_themes()`, `derive_style_theme_roles()` (WCAG AA >= 4.5:1 kontrast garantisi), `get_palette.py --style-themes` / `--style "NORDIC NEON" --format css` ve `search.py "neon"` testlerini ekle -> **Beklenen Çıktı:** `python -m unittest tests.test_theme_bridge` **KIRMIZI (FAIL)** döner (`parse_style_themes` henüz yok).
2. **[Adım 2 - `test_theme_skeleton_integration.py` Kırmızı Testleri Yaz]:** `tests/test_theme_skeleton_integration.py` içine `style-theme-palettes.md`, `design-skills-enforcement.md` ("Tek-Taraflı Seçim Yasağı", "88 Style Theme", "Reddedilen Varsayılanlar"), `creative-direction-protocol.md` ve `PLAN.template.md` kontrollerini ekle -> **Beklenen Çıktı:** `python tests/test_theme_skeleton_integration.py` **KIRMIZI (FAIL)** döner.

### 🟢 Faz 2: Katalog Taşıma & Minimal CLI Köprüsü (Green Loop)
1. **[Adım 1 - Katalog Dosyasını `.agent/` Altına Oluştur]:** `docs/plans/style_theme_color_palettes.md` içeriğini `.agent/skills/frontend-design/themes/style-theme-palettes.md` dosyasına başlık/kullanım notu ve `themes.css` #03/#04/#14/#15/#16 çapraz referansıyla kaydet (UTF-8 BOM'suz) -> **Beklenen Çıktı:** Dosya diskte 88 paletle mevcut ve `delivery.py` dağıtım kapsamındadır.
2. **[Adım 2 - `get_palette.py` Genişletmesini Uygula]:** `STYLE_THEMES_PATH` tanımla; `parse_style_themes()`, `search_style_themes()`, WCAG luminance/contrast tabanlı `derive_style_theme_roles(theme, mode)` (`>= 4.5:1` birincil metin garantisi; yetersizse luminance ayarı + `[WCAG AA Adjusted]` notu), `format_style_theme_css()` ve `--style-themes`, `--style`, `--mode`, `--format design-md` argümanlarını ekle (`parse_catalog()` 10 palet davranışı %100 korunur) -> **Beklenen Çıktı:** `python .agent/skills/frontend-design/scripts/get_palette.py --style-themes` 88 palet basar, `--style "NORDIC NEON" --format css` geçerli CSS değişkenleri ve WCAG oranı üretir.
3. **[Adım 3 - `ui-ux-pro-max/scripts/search.py` Köprüsünü Bağla]:** `get_local_recommendations()` fonksiyonuna `get_palette.search_style_themes()` sonuçlarını ekle -> **Beklenen Çıktı:** `python -m unittest tests.test_theme_bridge` **YEŞİL (PASS)** döner.

### 🧩 Faz 3: Kural, Skill, Şablon ve Katalog Senkronizasyonu
1. **[Adım 1 - `design-skills-enforcement.md` Kuralını Güncelle]:** §2.5 ve §2.6 C altına **"2.5.1 Çok-Kaynaklı Renk Esinlenmesi, Kombinasyon Sentezi ve Tek-Taraflı Seçim Yasağı"** alt bölümünü ekle:
   - Renk havuzu: `themes.css` (16 Kilitli Tema) + `style-theme-palettes.md` (88 Style Theme) + `palette-catalog.md` (10 WCAG Paleti) + `colors.csv` (192 Sektörel Palet) + `theme-factory` (10 Artifact Teması).
   - **Zorunlu Esinlenme:** Rastgele HEX uydurma yasağı; yeni kombinasyonlar bu havuzdan esinlenilerek ve WCAG AA/AAA ile doğrulanarak üretilir.
   - **Tek-Taraflı Seçim Yasağı:** Ajan *"ben projeye en uygun bu kombinasyonu seçtim ve ilerliyorum"* diyemez; jenerik/standart AI-slop sürecine düşemez. Standart **F1 Keşif -> F2 3 Alternatif Sunumu -> Kullanıcı Onayı -> F3 Token -> Kapılar** sürecini işletir (Brownfield rutin işlerde `Living Surface Supremacy` korunur).
   - **3 Alternatifte Esin & Ret Şeffaflığı:** Her adayda esinlenilen palet/tema adı, yüzey modu, WCAG kontrastı ve `Reddedilen Varsayılanlar` gerekçesi yazılır.
   -> **Beklenen Çıktı:** `rules_gates.py --strict` ve `check_design_skills.py` `[OK]` döner.
2. **[Adım 2 - `ui-polish` & `frontend-design` Dokümanlarını Güncelle]:** `ui-polish/SKILL.md`, `ui-polish/references/creative-direction-protocol.md`, `ui-polish/references/skill-routing-matrix.md` ve `frontend-design/SKILL.md` dosyalarını 88 palet CLI komutları, 7 satırlık makbuzdaki esin kaynağı zorunluluğu ve Anti-Unilateral Selection kuralıyla güncelle (dikkat: `check_design_skills.py` ve `test_skill_contracts.py` path kurallarına tam uyum) -> **Beklenen Çıktı:** `test_skill_contracts.py` 0 hata döner.
3. **[Adım 3 - Kardeş Skill & Şablon Senkronu]:** `theme-factory/SKILL.md`, `design-system/SKILL.md`, `ui-ux-pro-max/SKILL.md`, `feature-architect/references/theme-skeleton-matching.md`, `PLAN.template.md` (§7), `DESIGN.template.md` (§2) dosyalarını senkronla -> **Beklenen Çıktı:** `python tests/test_theme_skeleton_integration.py` **YEŞİL (PASS)** döner.
4. **[Adım 4 - Skill Kataloğunu Yeniden Derle]:** `scripts/generate_skills_catalog.py` içindeki `frontend-design` / `ui-polish` metadata ve snippet'lerini güncelle ve `python scripts/generate_skills_catalog.py` ile `.agent/skills-catalog.html` üret -> **Beklenen Çıktı:** `python tests/test_skills_catalog.py` tüm testlerde `PASS` döner.

### 🧹 Faz 4: Kalite Kapıları, Test Rehberi & Devir Kapanışı
1. **[Adım 1 - Tüm Kapı ve Test Paketlerini Koştur]:** `python .agent/skills/musgoku/scripts/run_all_gates.py` + `python tests/run_all.py` + `ui-ux-pro-max` testlerini çalıştır -> **Beklenen Çıktı:** Tüm kapılar `[OK]`, tüm test paketleri `PASS`.
2. **[Adım 2 - Yaşayan Belgeleri Güncelle]:** `docs/KULLANICI_TEST_REHBERI.md` (FAA AC 121-24C uyumlu doğrulama senaryoları), `knowledge-base.md`, `KANBAN.md` (`S2-18 -> Yapıldı`), `SPRINT_PLAN.md` ve `HANDOFF.md` dosyalarını güncelle -> **Beklenen Çıktı:** `check_handoff.py`, `check_sprint_board.py`, `check_aviation_docs.py` `[OK]` döner ve commit için kullanıcı onayı istenir.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### Veri Kataloğu & CLI Köprüsü (`GSW-UI-001`)
#### [NEW] `.agent/skills/frontend-design/themes/style-theme-palettes.md`
- `docs/plans/style_theme_color_palettes.md` içindeki 88 paletin (6 Özel/Başlangıç, 10 Konsept, 72 Koleksiyon 01–18) dağıtılabilir tek gerçek kaynağı + `themes.css` #03/#04/#14/#15/#16 eşleme tablosu.

#### [MODIFY] `.agent/skills/frontend-design/scripts/get_palette.py`
- `STYLE_THEMES_PATH` parser'ı (`parse_style_themes()`), arama (`search_style_themes()`), sRGB WCAG 2.1 kontrast tabanlı otomatik Dark/Light rol türetimi (`derive_style_theme_roles()`, `format_style_theme_css()`), `--style-themes`, `--style`, `--mode`, `--format design-md` bayrakları. Mevcut `parse_catalog()` (10 palet) arayüzü korunur.

#### [MODIFY] `.agent/skills/ui-ux-pro-max/scripts/search.py`
- `get_local_recommendations()` içinde 88 style theme eşleşmesini yüzeye çıkarma (`get_palette.py --style "<NAME>" --format css` komutuyla).

---

### Kurallar, Skiller & Şablonlar (`GSW-UI-002` & `GSW-UI-003`)
#### [MODIFY] `.agent/rules/design-skills-enforcement.md`
- §2.5 ve §2.6 C altına **88 Style Theme Color Palettes** referansı, **Esinlenme & Kombinasyon Sentezi** zorunluluğu, **Tek-Taraflı Seçim Yasağı** ("ben seçtim, ilerliyorum" yasağı) ve **3 Alternatif + Esin Kaynağı + Reddedilen Varsayılanlar** kuralı.

#### [MODIFY] `.agent/skills/ui-polish/SKILL.md`
#### [MODIFY] `.agent/skills/ui-polish/references/creative-direction-protocol.md`
#### [MODIFY] `.agent/skills/ui-polish/references/skill-routing-matrix.md`
- F2 zincirine `style-theme-palettes.md` ve `get_palette.py --style-themes` eklenmesi, tek-taraflı seçim yasağı ve 7 satırlık makbuzun 2. satırına esin kaynağı beyanı zorunluluğu.

#### [MODIFY] `.agent/skills/frontend-design/SKILL.md`
#### [MODIFY] `.agent/skills/theme-factory/SKILL.md`
#### [MODIFY] `.agent/skills/design-system/SKILL.md`
#### [MODIFY] `.agent/skills/ui-ux-pro-max/SKILL.md`
- Tek-sahip sınırları korunarak (`check_design_skills.py` D2 ihlali üretmeden) 88 Style Theme palet havuzunun tanıtılması ve geçerli CLI komutlarının (`test_skill_contracts.py` uyumlu) eklenmesi.

#### [MODIFY] `.agent/skills/feature-architect/references/theme-skeleton-matching.md`
#### [MODIFY] `.agent/templates/PLAN.template.md`
#### [MODIFY] `.agent/templates/DESIGN.template.md`
- Boyut 1 / §7 / §2 tablolarına 88 Style Theme İlham Kataloğu ve F2 3-alternatif / esin kaynağı / kullanıcı onayı kuralı eklenmesi (`test_theme_skeleton_integration.py` kontrolleri korunarak).

#### [MODIFY] `scripts/generate_skills_catalog.py` & `.agent/skills-catalog.html`
- `frontend-design` ve `ui-polish` metadata/snippet güncellemesi ve kataloğun yeniden derlenmesi.

---

### Testler & Dokümantasyon (`GSW-UI-004`)
#### [MODIFY] `tests/test_theme_bridge.py`
#### [MODIFY] `tests/test_theme_skeleton_integration.py`
#### [MODIFY] `docs/KULLANICI_TEST_REHBERI.md`

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
# 1. Tema & Palet Köprüsü Testleri (10 + 88 palet + WCAG rol türetimi + search.py)
python -m unittest tests.test_theme_bridge -v

# 2. Plan & Tema İskeleti Entegrasyon Testleri
python tests/test_theme_skeleton_integration.py

# 3. Skill Sözleşmeleri & Katalog Freshness Kapısı
cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest discover
python tests/test_skills_catalog.py

# 4. Birleşik Kalite Kapıları & Tüm Test Paketi
python .agent/skills/musgoku/scripts/rules_gates.py --strict
python .agent/skills/musgoku/scripts/check_design_skills.py
python .agent/skills/musgoku/scripts/check_aviation_docs.py --strict
python .agent/skills/musgoku/scripts/run_all_gates.py
python tests/run_all.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - 88 Palet CLI Listeleme]:** `python .agent/skills/frontend-design/scripts/get_palette.py --style-themes` çalıştır -> **Beklenen Çıktı:** 6 Özel, 10 Konsept ve 72 Koleksiyon olmak üzere toplam 88 tema tablosu listelenir.
2. **[Adım 2 - WCAG CSS Türetimi]:** `python .agent/skills/frontend-design/scripts/get_palette.py --style "NORDIC NEON" --mode dark --format css` çalıştır -> **Beklenen Çıktı:** `:root` CSS değişkenleri (`--bg-base`, `--text-primary`, `--accent-primary` vb.) ve `>= 4.5:1` ölçülmüş WCAG kontrast raporu basılır.
3. **[Adım 3 - Merkezi Arama]:** `python .agent/skills/ui-ux-pro-max/scripts/search.py "nordic neon"` çalıştır -> **Beklenen Çıktı:** `Ready-Made Local Assets` altında `NORDIC NEON` eşleşmesi ve `get_palette.py --style` komutu görünür.
4. **[Adım 4 - Katalog Görsel Kontrolü]:** `.agent/skills-catalog.html` dosyasını tarayıcıda açıp `frontend-design` / `ui-polish` kartlarını incele -> **Beklenen Çıktı:** 88 Style Theme Palettes + `get_palette.py --style-themes` komutu çekmecede görünür.

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `test_theme_bridge.py` içinde `len(palettes) == 10` hatası | `parse_catalog()` içine 88 tema karıştırılmış | `parse_catalog()` yalnız `palette-catalog.md`'yi okumaya devam etmeli; 88 tema için `parse_style_themes()` ayrı tutulmalı |
| `check_design_skills.py` `D2` mükerrer sahiplik hatası | İki skill aynı konu başlığıyla sahiplik tablosuna yazılmış | `design-skills-enforcement.md` §3 tablosunda tek sahip ilkesini koru (`frontend-design`: düz HEX + 88 ilham paleti; `design-system`: token türetimi; `theme-factory`: artifact temaları) |
| `test_skill_contracts.py` komut çözümleme hatası | `SKILL.md` içinde geçersiz relative script yolu yazılmış | Tüm komutları `python .agent/skills/<skill>/scripts/<file>.py ...` tam repo-relative biçiminde yaz |
| `test_skills_catalog.py` Freshness `FAIL` | `generate_skills_catalog.py` veya skill md güncellenip HTML yeniden derlenmemiş | `python scripts/generate_skills_catalog.py` çalıştırarak `.agent/skills-catalog.html` çıktısını yenile |
