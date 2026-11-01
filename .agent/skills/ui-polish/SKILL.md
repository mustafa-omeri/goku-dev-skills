---
name: ui-polish
description: Master Design Orchestrator & UI Sözleşmesi; 16 resmi kilitli temayı, 55 hazır bileşen şablonunu ve 16 UI/UX tasarım becerisini koordine ederek sıfır AI-slop, geometry-matched skeleton ve 375px responsive ergonomisiyle üretim kalitesinde arayüz inşa eder ve doğrular. Tetikleyiciler: "/ui-polish", "ui polish", "[UI-POLISH]", "/ui-polish --skeleton", "arayüz parlat", "polish ui", "skeleton kasetlerini entegre et". Tetiklenmez: sıfırdan backend API ve veritabanı `musgoku`'ya aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# UI Polish & Master Design Orchestrator (`/ui-polish`)

Bu yetenek, web ve mobil arayüzlerin yüzeysel CSS rötuşlarıyla değil; `.agent/skills/` altındaki **tüm 16 UI & UX tasarım becerisini** deterministik bir sırayla orkestre eden, **16 resmi kilitli temayı**, geometry-matched skeleton ekranlarını ve standart kullanıcı rehberini (`rehber_design.md` -> `kullanici_rehberi.html`) hayata geçiren **Baş Tasarım Mühendisi ve Skillset Orkestratörü (Master Orchestrator)** protokolüdür.

---

## 0. Çalışma Modu Tespiti ve Brownfield İstisnası

Ajan tek satır CSS veya bileşen kodu değiştirmeden önce projenin çalışma modunu belirler:

| Durum | Aktif Mod | Zorunlu Davranış |
|---|---|---|
| Proje kökünde `DESIGN.md` **yok** VE projede çalışan mevcut arayüz **var** (Brownfield) | **1. Hızlı Baseline & Dönüşüm Modu (`mode: baseline`)** | 💡 **Karar A1 İstisnası:** Kullanıcının açıkça `/ui-polish` çağırması tasarıma dokunma onayıdır. Ajan önce 1 dakikalık hızlı analizle mevcut durumu `<repo-kök>/DESIGN.md` (`mode: baseline`) olarak çıkarıp anti-referans yapar, ardından **duraksamadan doğrudan dönüşüm ve iyileştirme adımlarına (Faz 1–9) geçer**. (Dokunmama kuralı yalnızca rutin özellik geliştirme oturumlarında geçerlidir). |
| Proje kökünde `DESIGN.md` **yok** VE proje sıfırdan kuruluyor (Greenfield) | **2. Keşif & Tasarım Modu (`mode: crafted`)** | Faz 1 Keşif → Faz 2 Kreatif Yön (1 birincil + 2 alternatif tema) → Faz 3–9 tam icra akışı. |
| Proje kökünde `DESIGN.md` **var** VE normal `/ui-polish` çağrıldı | **3. İyileştirme Modu (`Refinement`)** | Mevcut `DESIGN.md` sözleşmesine sadık kalınır. Token'lar korunarak zanaat tabanı, 4 UX durumu, 375px mobil dönüşümü ve 10-noktalı canlı düzeltme döngüsü uygulanır. |
| Proje kökünde `DESIGN.md` **var** VE kullanıcı açıkça `"tasarımı değiştir / yeniden tasarla"` dedi | **4. Yeniden Tasarım Modu (`mode: redesign`)** | `PRODUCT.md` korunur; eski `DESIGN.md` anti-referans kabul edilerek yeni yön seçilir ve tüm arayüz dönüştürülür. |
| Kullanıcı açıkça `"/ui-polish --skeleton"` veya `"skeleton entegre et"` dedi | **5. Cerrahi Skeleton Kaset Modu (`mode: skeleton-only`)** | Tüm sayfayı yeniden tasarlamak yerine doğrudan hedef bileşenin kaset yapısını (geometry-matched skeleton) kurar; sıfır CLS, semantik tema token'ları ve themes.css shimmer motorunu bağlar. |

---

## 1. ZORUNLU ÖN UÇUŞ MAKBUZU (MANDATORY EXECUTION RECEIPT)

Ajan, kod yazmaya başlamadan önce ekrana aşağıdaki **6 satırlık bağlayıcı makbuzu** basmak zorundadır:

```markdown
### 🚀 UI-POLISH MASTER ORCHESTRATION RECEIPT
1. **Detected Project Archetype:** [SaaS Analytics / Logistics & BI / FinTech / EdTech / E-Commerce / Docs & Tools]
2. **Selected Locked Theme:** [1 Birincil Tema (Örn: #08 MARITIME AMBER) + 2 Alternatif Aday + 1 cümlelik gerekçe]
3. **Selected Component Themes (frontend-design):** [Sidebar: dark-slate-dock, Cards: expandable-summary-metric, Nav: floating-pill, Footer: clean-dark-compact]
4. **Invoked UI/UX Skills:** [canvas-design (manifesto & font), ui-ux-pro-max (icons & motion), design-system (tokens), mock-asset-provider (avatars)]
5. **Viewport-Native Mobile Transformations (375px):** [Desktop Sidebar -> Bottom Tab Bar + Sheet Drawer; Data Table -> Stacked Summary Cards]
6. **Top 10 High-Impact UI Flaws Targeted:** [1..10 somut zanaat ve UX kusuru listesi]
```

Bu makbuz basılmadan koda dokunulması zanaat ihlali sayılır.

---

## 2. BİLEŞEN, ARAYÜZ KATMANI VE SKILL SORUMLULUK MATRİSİ (16 Skill)

Bir arayüz geliştirilirken veya parlatılırken her bileşenin sahibi tek bir skill'dir:

| Arayüz Katmanı / Bileşen | Yetkili Skill | Kullanılacak Somut Varlık / Script / Referans | Çıktı & Sorumluluk |
| :--- | :--- | :--- | :--- |
| **Estetik Vizyon & Kreatif Kuzey Yıldızı** | `canvas-design` | `SKILL.md` (Design Philosophy & Manifesto) | Projenin ruhunu yansıtan 1 paragraflık tasarım felsefesi ve manifestosu; aşırı süsleme yerine zanaat tabanı (craft floor). |
| **Fontlar & Tipografi Çiftleri** | `canvas-design` + `ui-ux-pro-max` | `.agent/skills/canvas-design/canvas-fonts/` (29 küratörlü aile, 81 dosya) + `ui-ux-pro-max/data/typography.csv` (74 font eşleşmesi) + `google-fonts.csv` | Display + Body font çiftinin seçimi (Space Grotesk, Plus Jakarta Sans, Instrument Serif, Bricolage Grotesque, Newsreader vb.); kod blokları haricinde mono font yasağı. |
| **3-Tier Token Mimarisi & Renkler** | `design-system` + `ui-polish` | `design-system/scripts/generate-tokens.cjs`, `tokens.json` + `ui-polish/references/themes.css` | Primitive -> Semantic -> Component 3 katmanlı CSS değişkenleri (`--bg-base`, `--bg-surface`, `--text-primary`, `--accent-primary`); 16 Kilitli Tema bağlayıcılığı. |
| **Header, Üst Navigasyon & Menüler** | `frontend-design` | `.agent/skills/frontend-design/component-themes/navbars/` (`floating-pill-marker-navbar`) + `component-themes/menus/` (`adaptive-overflow-card-hub`, `fullscreen-overlay-stagger-menu`) | Yüzen hap veya yapışkan üst bar; "100 Öğe Sorusu" (Rule B.9) ile yatay taşmayan, dinamik sığma hesaplı kart tabanlı adaptif menü hub'ı. |
| **Sidebar & Navigasyon Kabuğu** | `frontend-design` + `ui-styling` | `.agent/skills/frontend-design/component-themes/sidebars/` (8 hazır tema: `collapsible-expandable`, `compact-dock`, `dark-slate-dock`, `dual-column-indigo`, `light-saas-dual-rail`, `window-chrome` vb.) | Proje arketipine göre (SaaS, BI, Docs, FinTech) otomatik sidebar seçimi; mobilde (375px) Bottom Navigation Bar + Drawer'a dönüşüm. |
| **İskelet Ekranlar (Skeleton Screens)** | `ui-polish` + `design-system` | `ui-polish/references/themes.css` (`.skeleton` shimmer motoru) + `design-system/references/states-and-variants.md` | Veri yüklenirken jenerik spinner yasağı; kaset yapısını (wireframe) birebir taklit eden geometry-matched skeleton katmanı. |
| **Kartlar, Metrik Panoları & Listeler** | `frontend-design` + `ui-ux-pro-max` | `.agent/skills/frontend-design/component-themes/cards/` (10 hazır tema: `expandable-summary-metric`, `interactive-flip-metric`, `dark-user-profile-widget`, `pricing-tier-grid`, `destination-travel` vb.) + `tabular-nums` | Eşit boyutlu kart sözleşmesi (Equal Dimensions Card Contract); sayısal verilerde sağa hizalı `tabular-nums`; hover ve focus durumları. |
| **Giriş, Kimlik Doğrulama & Modallar** | `frontend-design` + `ui-styling` | `.agent/skills/frontend-design/component-themes/logins/` (16 hazır tema: `split-hero-cloud-storage`, `fintech-secure-split`, `compact-dark-credentials`, `sliding-dual-auth-toggle` vb.) | Bölünmüş ekran (split-screen), animasyonlu arka plan veya minimalist auth formları; WCAG uyumlu form girdileri. |
| **Footer & Sayfa Altı Aksiyonları** | `frontend-design` | `.agent/skills/frontend-design/component-themes/footers/` (15 hazır tema: `saas-cta-conversion`, `agency-consultative-dark`, `clean-dark-compact`, `ocean-corporate-directory` vb.) | Marka kimliğini tamamlayan, eylem odaklı veya kurumsal dizin altlıkları. |
| **Dashboard Mimari Yerleşimi** | `frontend-design` | `.agent/skills/frontend-design/dashboard-theme/` (18 referans mimari şablonu: `dashboard-theme-01.webp` -> `18.webp`) | SaaS KPI kartları, veri tabloları, filtre rayı ve analitik panolarının profesyonel ızgara yerleşimi. |
| **Akordeon & İçerik Genişleticiler** | `frontend-design` | `.agent/skills/frontend-design/component-themes/accordions/` (`horizontal-expand-dark`, `horizontal-expand-plum`) | SSS, detay panelleri ve kademeli açıklama (progressive disclosure) alanları. |
| **Parallaks & Hikaye Anlatımı** | `frontend-design` | `.agent/skills/frontend-design/component-themes/parallax/` (`multi-layer-pure-css`, `split-section-story`) | Landing ve pazarlama sayfalarında derinlik ve akıcı katman geçişleri. |
| **İkonografi Standartları** | `ui-ux-pro-max` | `ui-ux-pro-max/data/icons.csv` (105 Phosphor/Lucide SVG ikon haritası) | Ham emoji veya rastgele Unicode sembollerin yasaklanması; tutarlı çizgi kalınlığında SVG ikon entegrasyonu. |
| **Hareket, Geçişler & Yay Fiziği** | `ui-ux-pro-max` | `ui-ux-pro-max/references/emil-kowalski-motion-playbook.md` + `data/motion.csv` (17 GSAP önayarı) | Yay mekaniği (spring physics), kesintiye uğrayabilir hareketler; `Operate` modunda 150-250ms hızlı geçişler; yavaş fade-in slop yasağı. |
| **3D & WebGL Performans Kuralları** | `ui-ux-pro-max` | `ui-ux-pro-max/references/three-r3f-performance-rubric.md` | R3F / Three.js içeren sayfalarda useFrame bütçesi, VRAM dispose ve GPU yük kontrolü. |
| **Form UX & Girdi Doğrulama** | `ui-ux-pro-max` | `ui-ux-pro-max/data/ux-guidelines.csv` (Öncelik 8: Forms & Feedback) | Alan içi gerçek zamanlı doğrulama (inline validation), net hata mesajı, görünür etiketler; tek baskın CTA butonu. |
| **Tailwind & shadcn/ui Kod Katmanı** | `ui-styling` | `ui-styling/scripts/shadcn_add.py`, `tailwind_config_gen.py`, `references/base-ui-tailwind-v4.md` | Tailwind CSS utility sınıfları, semantic token eşlemeleri (`theme.extend`), erişilebilir shadcn/ui bileşenleri. |
| **Gerçekçi Mock Varlıklar & Görseller** | `mock-asset-provider` + `frontend-design` | `mock-asset-provider/scripts/fetch_assets.py` + `frontend-design/scripts/assets.mjs` | Gri kutular yerine yüksek kaliteli profil avatarları, ürün resimleri ve açık arşiv (Met Museum, Openverse, NASA) kültürel fotoğrafları. |
| **Banner, Hero & Reklam Kreatifleri** | `banner-design` | `banner-design/references/banner-design-system.md` | Sabit piksel hero banner'lar (1500x500 X, 1584x396 LinkedIn vb.), güvenli alan ve platform tipografi kuralları. |
| **Rehberli Ürün Turu & Coachmark'lar** | `onboarding-tour` | `onboarding-tour/scripts/scaffold_tour.py` | İlk kullanımda Driver.js veya Joyride ile kalıcı durum kontrollü adım adım onboarding turu. |
| **Logo & Kurumsal Kimlik Brief'i** | `design` | `design/references/logo-design.md`, `cip-style-guide.md` | Logo renk psikolojisi, favicon ve kurumsal kimlik yönergeleri. |
| **Sunum / Slayt Stratejisi & Üretimi** | `slides` + `design-system` | `slides/references/` (Duarte sparkline) + `design-system/scripts/generate-slide.py` | Sunum metin formülleri (PAS, AIDA) ve token uyumlu HTML slayt üretimi. |
| **Geliştirici Odaklı IDE Arayüzleri** | `web-ide-ux-architect` | `web-ide-ux-architect/SKILL.md` | Split pane, Command Palette (Ctrl+K), dosya ağacı ve terminal pencereleri. |
| **React Performans & Re-render Koruması** | `react-best-practices` | `react-best-practices/references/state-and-routing-antipatterns.md` | Gereksiz re-render'ları önleme, Zustand `useShallow`, cascading waterfall ve memoization disiplini. |
| **Çok Dilli Arayüz & Çeviri Denetimi** | `i18n-localization` | `i18n-localization/scripts/i18n_checker.py` | UI üzerinde hardcoded metin kalmasını engelleme, `t()` anahtarlarını JSON sözlükleriyle eşleme. |
| **Standart Kullanıcı Rehberi** | `ui-polish` | `ui-polish/references/rehber_design.md` -> `kullanici_rehberi.html` | `skills-catalog.html` seviyesinde 5 katmanlı dikey dilim, playbook ve skeleton önizlemeli interaktif HTML rehberi. |

---

## 2.1 Cerrahi Skeleton Kaset Entegrasyonu Protokolü (`/ui-polish --skeleton`)

Kullanıcı doğrudan `/ui-polish --skeleton [Bileşen]` veya `skeleton kasetlerini entegre et` dediğinde ajan tüm sayfayı veya temayı değiştirmekle vakit kaybetmez; doğrudan aşağıdaki 5 cerrahi adımı işletir:

1. **Geometri & Düzen Analizi (Kaset Sadakati):**
   - Hedef bileşenin (kart, liste, profil, tablo satırı vb.) gerçek DOM yapısını inceler.
   - Dış genişlik (`width`), yükseklik (`height` / `min-height`), iç boşluklar (`padding`) ve aralıklar (`gap`, `space-y`) pikseli pikseline tespit edilir.
2. **Themes.css Shimmer & Hazır Kaset Seçimi:**
   - `.agent/skills/ui-polish/references/themes.css` içindeki donanım hızlandırmalı `.skeleton` shimmer motoru projeye dahil edilir (veya import edilir).
   - Profil, Kart veya Tablo ise `.agent/skills/ui-styling/references/shadcn-components.md` içindeki hazır kaset şablonları uyarlanır.
3. **Sıfır Düzen Sıçraması (Zero CLS Guarantee):**
   - Kaset bileşeni, gerçek veri yüklendiğinde düzenin zıplamasını (Cumulative Layout Shift) %0 yapacak şekilde kapsayıcı elementle birebir aynı ölçülere kilitlenir.
4. **Semantik Tema Token'ları & A11y:**
   - Flat/sabit `bg-gray-200` gibi renkler KESİNLİKLE YASAKTIR. Temanın semantik `--bg-surface`, `--bg-card` ve `--border-subtle` değişkenleri kullanılır.
   - Erişilebilirlik için kapsayıcıya `aria-busy="true"`, `aria-live="polite"` ve `<span className="sr-only">Yükleniyor...</span>` eklenir.
5. **Mekanik Doğrulama:**
   - `python .agent/skills/musgoku/scripts/check_design_slop.py` çalıştırılarak veri yükleme anında spinner kalıntısı (`W4`) kalmadığı kanıtlanır.

---

## 3. DOKUZ AŞAMALI MASTER İCRA AKIŞI (FAZ 1 – FAZ 9)

### Faz 1: Keşif & Analiz (`ui-polish` + `brand`)
1. `PRODUCT.md`, `PROJECT_BRIEF.md`, `README.md` ve mevcut kodları tara.
2. Varsa `docs/brand-guidelines.md` kurumsal kimlik tonunu ve renklerini oku.
3. Brownfield projede 1 dakikalık hızlı analizle `DESIGN.md (mode: baseline)` çıkar ve anti-referans yap.

### Faz 2: Kreatif Yön, Felsefe & Tipografi (`canvas-design` + `ui-ux-pro-max`)
1. `canvas-design` ile projeye özgü 1 paragraflık estetik manifestosunu (Kuzey Yıldızı) oluştur.
2. `canvas-fonts/` altındaki 29 küratörlü yazı tipi ailesinden ve `typography.csv`'den Display + Body font çiftini seç. Kod blokları haricinde mono font kullanımını kesinlikle engelle.

### Faz 3: Token Mimarisi & 16 Kilitli Tema (`design-system` + `ui-polish`)
1. `ui-polish/references/themes.css` içindeki 16 resmi kilitli temadan arketipe en uygun 1 birincil tema ve 2 alternatif aday belirle.
2. `design-system` 3 katmanlı token mimarisini (`primitive` -> `semantic` -> `component`) projeye bağla.
3. Koddaki tüm sabit HEX/RGB ve generic Tailwind sınıflarını temizle; semantik CSS değişkenlerine eşle.
4. Geliştirme anında canlı test için `skill-routing-matrix.md` içindeki Sıfır-Token Tema Seçici kancasını (`systemThemeSwitcherPill`) enjekte et.

### Faz 4: Navigasyon Kabuğu & Zorunlu Sidebar (`frontend-design` + `ui-styling`)
1. `component-themes/sidebars/` altındaki 8 hazır temayı incele; arketipe uygun sidebar'ı entegre et.
2. Masaüstündeki sidebar'ı mobilde (`375px`) **Bottom Navigation Bar (ilk 4-5 aksiyon) + Hamburger Drawer** yapısına dönüştür.

### Faz 5: Hazır Bileşen Enjeksiyonu (`frontend-design` + `ui-ux-pro-max`)
1. `component-themes/` altındaki hazır şablonları (`navbars`, `menus`, `cards`, `logins`, `footers`) `get_component.py` ile koda uyarla.
2. Veri tablolarına `tabular-nums` ve sağa hizalama ver; mobilde yatay scroll'u yasaklayarak özet kart listesine dönüştür.
3. Tüm asenkron veri kaplarına `themes.css` içindeki `.skeleton` shimmer motorunu entegre et (spinner yasaktır).

### Faz 6: Mikro-Etkileşim, İkon & Performans (`ui-ux-pro-max` + `react-best-practices`)
1. Emil Kowalski yay mekaniği (150-250ms hızlı geçişler) ve `icons.csv` SVG ikon standartlarını uygula.
2. `react-best-practices` kurallarıyla re-render döngülerini ve waterfall veri çekmelerini temizle.

### Faz 7: Görseller, Banner & Onboarding (`mock-asset-provider` + `banner-design` + `onboarding-tour`)
1. `fetch_assets.py` veya `assets.mjs` ile kartlar için gerçekçi görselleri çek.
2. Varsa sabit ölçülü hero banner ve OG kapaklarını `banner-design` safe-zone kurallarıyla ayarla.
3. Gerekirse `scaffold_tour.py` ile rehberli ürün turu kurgula.

### Faz 8: Standart Kullanıcı Rehberi (`ui-polish`)
1. `rehber_design.md` spesifikasyonuna sadık kalarak `docs/kullanici_rehberi.html` dosyasını üret veya güncelle.
2. 5 Katmanlı dikey dilim mimari kartlarını, playbook adımlarını ve Skeleton ekran simülatörünü eksiksiz doldur.

### Faz 9: Mekanik Doğrulama & 10 Noktalı Canlı Düzeltme Döngüsü
1. Üç zorunlu kapıyı çalıştır (`0 hata` şarttır):
   - `python .agent/skills/musgoku/scripts/check_design_contract.py --include-agent --strict`
   - `python .agent/skills/musgoku/scripts/check_design_slop.py --include-agent`
   - `python .agent/skills/musgoku/scripts/check_theme_contrast.py --include-agent`
2. Canlı DOM'da en yüksek etkili **10 somut tasarım kusurunu** tespit et, doğrudan kodda düzelt ve doğrulamasını raporla.
