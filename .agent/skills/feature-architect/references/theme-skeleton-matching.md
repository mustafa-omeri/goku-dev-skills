# Feature Architect & /plan — Birleşik Tema ve Bileşen İskeleti Eşleştirme Protokolü

Bu referans, herhangi bir geliştirme ortamında (**Antigravity IDE**, **Antigravity CLI (`agy`)**, **Claude Code (`claude`)**, **OpenCode (`opencode`)** veya **Genel Terminal/CLI**) `/plan` veya `/feature-architect` çalıştırıldığında; tespit edilen eksik sayfaların, 404 rotalarının, yetim backend uçlarının ve yeni özelliklerin **yalnızca dashboard şablonlarıyla değil, tüm tema ve bileşen iskeletimizle** nasıl eşleştirileceğini tanımlar.

---

## 0. Çoklu Araç ve CLI Agnostik Çalışma İlkeleri (Multi-Tool Parity)

Bu protokol hiçbir özel IDE arayüzüne bağımlı değildir; tüm ajan ve CLI araçlarında birebir aynı deterministik çıktıyı üretir:

| Ortam / Araç | Plan & Rapor Çıktı Konumu | Bileşen ve Tema Sorgulama | İcra Onayı (Proceed) |
| :--- | :--- | :--- | :--- |
| **Antigravity IDE** | `<artifact-dir>/<plan_name>.md` | `python .agent/skills/frontend-design/scripts/get_component.py` | Görsel **"Proceed"** butonu veya sohbet onayı |
| **Antigravity CLI (`agy`)** | `<artifact-dir>/<plan_name>.md` veya `.agent/plans/` | `python .agent/skills/frontend-design/scripts/get_component.py` | Terminalde `"proceed"`, `"onay"`, `"uygula"` |
| **Claude Code (`claude`)** | `.agent/plans/<plan_name>.md` (veya `docs/plans/`) | `python .agent/skills/frontend-design/scripts/get_component.py` | Terminalde `"proceed"`, `"onay"`, `"uygula"` |
| **OpenCode (`opencode`)** | `.agent/plans/<plan_name>.md` (veya `docs/plans/`) | `python .agent/skills/frontend-design/scripts/get_component.py` | Terminalde `"proceed"`, `"onay"`, `"uygula"` |
| **Genel Terminal / CLI** | `.agent/plans/<plan_name>.md` (veya `docs/plans/`) | `python .agent/skills/frontend-design/scripts/get_component.py` | Standart girdi / komut satırı onayı |

---

## 1. Boyut 1: 16 Resmi Kilitli Tema ve Yaşayan Yüzey Önceliği (`Living Surface`)

Hiçbir ekran veya bileşen keyfi hex kodlarıyla veya rastgele siyah arka planlarla (`#000000`) boyanamaz. Her plan ve özellik önerisi `.agent/skills/frontend-design/themes/themes.css` (ve `themes.md`) içindeki **16 Resmi Kilitli Tema** ve projenin **Yaşayan Yüzey (`Living Surface`)** moduyla eşleştirilir:

1. **Yaşayan Yüzey Önceliği (`Living Surface Supremacy`):**
   - Projenin mevcut `DESIGN.md` veya CSS kök değişkenleri açık zeminli (`Light Mode`) ise, karanlık bir bileşen şablonu seçilse dahi projenin açık yüzey token'larına (`--bg-surface`, `--bg-card`, `--text-primary`, `--border-subtle`) uyarlanır.
   - Koyu zeminli (`Dark Mode`) projelerde ise derin katmanlı yüzey hiyerarşisi (`surface-0` < `surface-1` < `surface-2`) korunur.
2. **16 Resmi Kilitli Tema Kataloğu:**
   - `#01 Obsidian Velvet` (Derin kadife koyu, kurumsal SaaS & AI)
   - `#02 Cyber Neon` (Yüksek kontrast siber telemetri & geliştirici araçları)
   - `#03 Swiss Modernist` (Keskin tipografik ızgara, yüksek okunabilirlik)
   - `#04 Bauhaus Industrial` (Geometrik bloklar ve fonksiyonel vurgu)
   - `#05 Neo-Brutalist High-Contrast` (Belirgin sınırlar, cesur aksiyon dili)
   - `#06 Nordic Frost Minimal` (Ferah açık zemin, buz mavisi/gri nötr denge)
   - `#07 Corporate Clean Slate` (Kurumsal B2B, finans ve yönetim panelleri)
   - `#08 Japanese Zen Minimalist` (Sakin, dingin boşluklu içerik ve okuma deneyimi)
   - `#09 Sunset Amber Editorial` (Sıcak editoryal içerik, medya ve hikaye anlatımı)
   - `#10 Deep Forest Emerald` (Sürdürülebilirlik, sağlık, finansal büyüme)
   - `#11 Midnight Navy Executive` (Üst düzey yönetici, güvenlik ve bulut altyapısı)
   - `#12 Warm Terracotta Clay` (İnsan odaklı topluluk, İK ve eğitim)
   - `#13 Retro Terminal Amber` (Monospace, CLI, DevOps ve sistem izleme)
   - `#14 Pastel Aesthetic Candy` (Yaratıcı stüdyo, tüketici uygulaması)
   - `#15 Dark Glassmorphic Aurora` (Buzlu cam katmanları, modern fin-tech/kripto)
   - `#16 Warm Alabaster` (Göz yormayan sıcak fildişi/kağıt dokulu uzun kullanım)

---

## 2. Boyut 2: 55+ Doğrulanmış Bileşen Teması (8 Kategori & `get_component.py`)

`gap_scanner.py` tarafından tespit edilen her eksik sayfa, kırık rota veya zayıf bileşen için sıfırdan "AI-slop" arayüz uydurmak yasaktır. Ajan, CLI köprüsünü çalıştırarak **8 kategorideki 55+ doğrulanmış bileşen şablonundan** uygun olanı seçer:

```bash
# Tüm kategorileri ve 55+ bileşen şablonunu listele
python .agent/skills/frontend-design/scripts/get_component.py --list

# Belirli bir kategorideki şablonları gör (accordions, cards, footers, logins, menus, navbars, parallax, sidebars)
python .agent/skills/frontend-design/scripts/get_component.py --type logins

# Seçilen şablonun tam HTML ve CSS kodunu çek
python .agent/skills/frontend-design/scripts/get_component.py --theme sliding-hero-auth-switcher-login
```

### Boşluk Türüne Göre 8 Bileşen Kategorisi Eşleştirme Matrisi

| Kategori (`component-themes/`) | Adet | Hangi Boşluk / İhtiyaç İçin Kullanılır? | Öne Çıkan Doğrulanmış Şablon Örnekleri |
| :--- | :---: | :--- | :--- |
| **`logins`** | 16 | Eksik veya stub `/login`, `/register`, `/forgot-password`, SSO ve kimlik doğrulama ekranları | `sliding-hero-auth-switcher-login`, `split-hero-cloud-storage-login`, `fintech-secure-split-login`, `clean-light-card-login`, `dark-luxury-glass-login` |
| **`sidebars`** | 8 | 404'e düşen sol menü bağlantıları, eksik uygulama kabuğu (App Shell), çalışma alanı gezgini | `collapsible-expandable-sidebar`, `workspace-profile-sidebar`, `light-saas-dual-rail-sidebar`, `compact-dock-sidebar`, `dual-column-indigo-sidebar` |
| **`navbars`** | 1 | Eksik üst gezinme çubuğu, aktif sekme işaretçili başlık | `floating-pill-marker-navbar` |
| **`menus`** | 2 | Mobil/tablet taşma menüleri, çoklu eylem merkezi, tam ekran navigasyon | `adaptive-overflow-card-hub`, `fullscreen-overlay-stagger-menu` |
| **`cards`** | 10 | Zayıf Profil (`Profile`) ekranları, özet metrik kartları, fiyatlandırma paketleri, içerik/iş ilanları | `dark-profile-bio-card`, `dark-user-profile-widget-card`, `expandable-summary-metric-card`, `interactive-flip-metric-card`, `pricing-tier-grid-cards`, `portfolio-creator-profile-card` |
| **`accordions`** | 2 | Zayıf Ayarlar (`Settings`) bölümleri, SSS, daraltılabilir detay panelleri | `horizontal-expand-dark-accordion`, `horizontal-expand-plum-accordion` |
| **`footers`** | 15 | Eksik sayfa altı, kurumsal site haritası, bülten aboneliği ve dönüşüm CTA alanı | `saas-cta-conversion-footer`, `ocean-corporate-directory-footer`, `clean-dark-compact-footer`, `newsletter-community-light-footer`, `teal-enterprise-action-footer` |
| **`parallax`** | 2 | Eksik karşılama sayfası (Landing Page), ürün hikayesi ve görsel vitrin | `multi-layer-pure-css-parallax`, `split-section-story-parallax` |

> ⛔ **Auth / Login Özel Kuralı:** `logins` kategorisinden bir şablon uygulanırken şablondaki demo görsel kopyalanmaz (`generate_auth_hero.py` ile projeye uygun üretilir) ve projede karşılığı olmayan hayali giriş yöntemleri ("Magic Link" vb.) veya mükerrer geçiş butonları eklenmez.

---

## 3. Boyut 3: 18 Doğrulanmış Dashboard Mimarisi (`catalog.json`)

Projede bir genel bakış, analitik panel veya yetim backend verilerini (`orphan_endpoints`) görselleştirecek bir yönetim ekranı planlanıyorsa:
- `.agent/skills/frontend-design/dashboard-theme/catalog.json` içindeki **18 doğrulanmış dashboard şablonu** (`dashboard-theme-01` .. `dashboard-theme-18`) taranır.
- Detaylı eşleştirme kuralları için [`dashboard-matching.md`](./dashboard-matching.md) protokolü işletilir ve en uygun 2-3 aday kullanıcıya sunulur.

---

## 4. Boyut 4: Zorunlu Geometri-Uyumlu İskelet Ekranlar (`Zero-CLS Skeleton Cassettes`)

Veri çeken veya asenkron yüklenen hiçbir sayfa/bileşende jenerik dönen spinner (`Loading...`) kullanılamaz (spinner yalnızca form submit butonlarının içinde serbesttir). Planlanan her ekran için hedef bileşenin geometrisini birebir taklit eden (`Zero-CLS` — sıfır düzen kayması) **5 İskelet Kasetinden** biri seçilmelidir:

1. **Profil & Kullanıcı Kaseti (`Profile Cassette`):** Dairesel/yuvarlatılmış avatar bloğu + isim/unvan çubukları + istatistik rozetleri iskeleti.
2. **Kart & KPI Metrik Kaseti (`Metric Card Cassette`):** İkon + başlık + büyük metrik değeri + alt trend/sparkline çizgisi iskeleti.
3. **Tablo & Veri Izgarası Kaseti (`Table Row Cassette`):** Filtre/arama üst çubuğu + sütun başlıkları + 5-10 adet çok sütunlu satır iskeleti.
4. **Dashboard & Analitik Kaseti (`Dashboard Split Cassette`):** Üstte 3-4'lü KPI kart iskeleti + ortada grafik konteyneri + yanda son aktiviteler listesi iskeleti.
5. **Form & Ayarlar Kaseti (`Form Section Cassette`):** Bölüm başlığı + etiket/input kutusu çiftleri + alt aksiyon barı iskeleti.

Her ekran aynı zamanda **4 Zorunlu UX Durumunu** (1. Geometry-Matched Skeleton, 2. Açıklayıcı + CTA butonlu Empty State, 3. Yeniden dene aksiyonlu Error State, 4. Dolu/Başarılı Durum) içermek zorundadır.

---

## 5. Boyut 5: Mock Asset, Auth Hero ve Rehberli Tur (`onboarding-tour`)

Planlanan özellik görsel varlık veya ilk kullanım yönlendirmesi gerektiriyorsa:
- **Auth & Vitrin Görselleri:** `python .agent/skills/mock-asset-provider/scripts/generate_auth_hero.py` CLI aracıyla projenin iş alanına ve renk paletine uygun yüksek çözünürlüklü görsel üretilir (`mock-asset-provider` küratörlü Unsplash arketipleri yedek olarak kullanılır).
- **Kullanıcı Karşılama Turu:** Yeni eklenen karmaşık özellikler veya dashboard'lar için `onboarding-tour` (Driver.js / React Joyride) ile adım adım rehberli tur planlanır.
