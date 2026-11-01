# DETERMINISTIC SKILL ROUTING & ARCHITECTURE MATRIX (`skill-routing-matrix.md`)

Bu doküman, `/ui-polish` Master Orchestrator komutu çağrıldığında ajanın ezbere CSS/HTML yazmasını ve token israf etmesini engelleyen; `.agent/skills/` altındaki **tüm 16 UI & UX tasarım becerisini** deterministik bir sırayla göreve koşan anayasal yönlendirme protokolüdür.

---

## 1. MANDATORY PRE-FLIGHT EXECUTION RECEIPT

Ajan, projede tek bir satır CSS/HTML/JSX değiştirmeden önce aşağıdaki 6 satırlık makbuzu terminale basmak **ZORUNDADIR**:

```markdown
### 🚀 UI-POLISH MASTER ORCHESTRATION RECEIPT
1. **Detected Project Archetype:** [SaaS Analytics / Logistics & BI / FinTech / EdTech / E-Commerce / Docs & Tools]
2. **Selected Locked Theme:** [1 Birincil Tema (Örn: #08 MARITIME AMBER) + 2 Alternatif Aday + 1 cümlelik gerekçe]
3. **Selected Component Themes (frontend-design):** [Sidebar: dark-slate-dock, Cards: expandable-summary-metric, Nav: floating-pill, Footer: clean-dark-compact]
4. **Invoked UI/UX Skills:** [canvas-design (manifesto & font), ui-ux-pro-max (icons & motion), design-system (tokens), mock-asset-provider (avatars)]
5. **Viewport-Native Mobile Transformations (375px):** [Desktop Sidebar -> Bottom Tab Bar + Sheet Drawer; Data Table -> Stacked Summary Cards]
6. **Top 10 High-Impact UI Flaws Targeted:** [1..10 somut zanaat ve UX kusuru listesi]
```

Bu makbuz basılmadan koda dokunulması kural ihlali sayılır.

---

## 2. BİLEŞEN, ARAYÜZ KATMANI VE SKILL SORUMLULUK MATRİSİ

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

## 3. PROJE ARKETİPİ -> TEMA, SİDEBAR VE BİLEŞEN EŞLEME TABLOSU

| Proje Arketipi | Birincil Kilitli Tema Adayları | Zorunlu Sidebar Şablonu (`frontend-design`) | Kart & Liste Şablonları (`frontend-design`) | Default Skeleton Deseni |
| :--- | :--- | :--- | :--- | :--- |
| **B2B SaaS, DevTools, AI Workspaces** | `obsidian-velvet`, `nordic-slate`, `graphite-pulse` | `dark-slate-dock-sidebar` (64px daralan dock + kısayollar) veya `collapsible-expandable-sidebar` | `expandable-summary-metric-card`, `pricing-tier-grid-cards` | Metrik Kartı Satırı + Tablo Satır Shimmer |
| **Lojistik, Tedarik Zinciri, BI, Kontrol Kulesi** | `maritime-amber`, `aegean-copper`, `umber-monolith` | `window-chrome-team-sidebar` (Çalışma alanı değiştirici ve sabit altlık) | `interactive-flip-metric-card`, `expandable-summary-metric-card` | Çift Bölmeli Harita/Grafik + Yoğun Izgara Shimmer |
| **FinTech, Yönetici Portalları, Danışmanlık** | `forest-gild`, `verdant-abyss`, `nordic-slate` | `dual-column-indigo-sidebar` veya `light-saas-dual-rail-sidebar` | `dark-user-profile-widget-card`, `career-job-listing-card` | KPI Özeti + Sağa Hizalı Tabular Shimmer |
| **EdTech, Oyunlaştırılmış Platformlar, Üretkenlik** | `indigo-solar`, `digital-fresh`, `moss-botanical` | `workspace-profile-sidebar` (Masaüstü) -> **4 Sekmeli Bottom Bar** (Mobil) | `vibrant-social-creator-card`, `horizontal-expand-dark-accordion` | İnteraktif Kart Izgarası + İlerleme Çubuğu Shimmer |
| **Yaratıcı Stüdyolar, Medya, Girişimler** | `plum-lime` (Editoryal), `royal-amethyst`, `magenta-dusk` | `violet-minimal-sidebar` veya `compact-dock-sidebar` | `portfolio-creator-profile-card`, `destination-travel-card` | Masonry / Asimetrik Bento Shimmer |
| **E-Ticaret, Yaşam Tarzı, Gastronomi** | `espresso-terracotta`, `earthy-energy` (Editoryal), `moss-botanical` | `clean-light-card-login` + Kategori Yan Menüsü (Masaüstü) -> **Slide-Up Filter Sheet** (Mobil) | `editorial-article-preview-card`, `pricing-tier-grid-cards` | Görsel Orantılı Medya Kartı + Fiyat Rozeti Shimmer |

---

## 4. SIRALI VE PARALEL İCRA AKIŞI

Token israfını ve CSS çatışmalarını engellemek için icra 3 ana evrede yürütülür:

### Evre A: Yapısal Temel (Sıralı - Önce Çalıştırılır)
1. **Tema ve Token Enjeksiyonu (`themes.css` + `design-system`):** Seçilen temanın semantik değişkenleri (`--bg-base`, `--bg-surface`, `--text-primary`, `--accent-primary` vb.) kilitlenir. Koddaki tüm sabit HEX/RGB ve generic Tailwind renkleri temizlenir.
2. **Navigasyon Kabuğu ve Sidebar:** `frontend-design/component-themes/sidebars/` taranarak dış uygulama kabuğu (Sidebar + Top Bar + İçerik Kanvası) kurulur. Mobilde (`375px`) alt gezinme çubuğuna (Bottom Navigation Bar) ve Drawer'a dönüşümü bağlanır.

### Evre B: Bileşen Dönüşümü (Paralel - Eşzamanlı Yürütülür)
1. **Veri Tabloları ve Listeler:** Sayısal sütunlara `font-variant-numeric: tabular-nums` ve sağa hizalama verilir; `375px` mobilde yatay scroll tamamen kaldırılarak özet kart listesine (`cards/`) dönüştürülür.
2. **Skeleton Screen Enjeksiyonu:** Her asenkron veri kabına, karta ve tabloya geometry-matched `.skeleton` shimmer katmanı eklenir (spinner kesinlikle yasaktır).
3. **Formlar, Butonlar ve CTA Hiyerarşisi:** Viewport başına tek birincil dominant CTA (`--accent-primary`) tanımlanır. Mobildeki yatay filtre şeritleri sarılan çip ızgarasına veya alttan açılan bottom sheet paneline dönüştürülür.
4. **İkon ve Görsel Standartları:** `ui-ux-pro-max/data/icons.csv` uyarınca SVG ikonlar bağlanır; ham emoji temizlenir. Kartlar için `mock-asset-provider/scripts/fetch_assets.py` ile gerçekçi avatarlar çekilir.

### Evre C: Doğrulama ve Kullanıcı Rehberi (Sıralı - Son Adım)
1. **Standart Kullanıcı Rehberi (`rehber_design.md` -> `kullanici_rehberi.html`):** Projenin `docs/kullanici_rehberi.html` dosyası sistem standart şablonu üzerinden üretilir veya güncellenir.
2. **10 Noktalı Canlı İnceleme ve Düzeltme Döngüsü:** Render edilen sayfa 1440px ve 375px'te incelenir; Pre-Flight Receipt'teki 10 kritik kusur bizzat kodda düzeltilir.

---

## 5. SIFIR TOKEN CANLI TEMA SEÇİCİ KANCASI (THEME SWITCHER PILL)

Kullanıcının farklı temaları canlı olarak test edebilmesi veya tema kararsızlığı durumunda kodun tekrar tekrar baştan üretilmesini (token israfını) önlemek için sayfanın sağ altına şu hafif kanca enjekte edilir:

```html
<!-- Zero-Token Live Theme Switcher (Drop into any page referencing themes.css) -->
<div id="systemThemeSwitcherPill" style="position:fixed; bottom:20px; right:20px; z-index:99999; background:var(--bg-surface); border:1px solid var(--border-subtle); padding:6px 12px; border-radius:999px; display:flex; align-items:center; gap:8px; box-shadow:0 8px 32px rgba(0,0,0,0.45); backdrop-filter:blur(8px);">
  <label for="systemThemeSelector" style="font-size:11px; font-weight:700; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.05em;">Tema:</label>
  <select id="systemThemeSelector" onchange="document.documentElement.setAttribute('data-theme', this.value)" style="background:var(--bg-elevated); color:var(--text-primary); border:1px solid var(--border-subtle); border-radius:6px; padding:3px 8px; font-size:12px; cursor:pointer; outline:none;">
    <option value="obsidian-velvet">01. Obsidian Velvet</option>
    <option value="espresso-terracotta">02. Espresso Terracotta</option>
    <option value="nordic-slate">03. Nordic Slate</option>
    <option value="verdant-abyss">04. Verdant Abyss</option>
    <option value="umber-monolith">05. Umber Monolith</option>
    <option value="royal-amethyst">06. Royal Amethyst</option>
    <option value="moss-botanical">07. Moss Botanical</option>
    <option value="maritime-amber">08. Maritime Amber</option>
    <option value="graphite-pulse">09. Graphite Pulse</option>
    <option value="aegean-copper">10. Aegean Copper</option>
    <option value="magenta-dusk">11. Magenta Dusk</option>
    <option value="indigo-solar">12. Indigo Solar</option>
    <option value="forest-gild">13. Forest Gild</option>
    <option value="plum-lime">14. Plum + Lime (Editorial)</option>
    <option value="digital-fresh">15. Digital Fresh (Editorial)</option>
    <option value="earthy-energy">16. Earthy Energy (Editorial)</option>
  </select>
  <button type="button" onclick="const m = document.documentElement.getAttribute('data-mode') === 'light' ? 'dark' : 'light'; document.documentElement.setAttribute('data-mode', m); this.innerText = m === 'light' ? '☀️' : '🌙';" style="background:var(--bg-elevated); border:1px solid var(--border-subtle); color:var(--text-primary); border-radius:6px; padding:3px 8px; font-size:12px; cursor:pointer;" title="Koyu / Açık Mod Değiştir">🌙</button>
</div>
```

Teslimat tamamlandığında veya kullanıcı nihai temayı onayladığında bu seçici sayfadan kolayca kaldırılabilir.
