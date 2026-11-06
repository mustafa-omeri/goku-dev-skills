---
name: feature-architect
description: >-
  Global Otonom Ürün Denetçisi, 6 Şapkalı Strateji Konseyi ve Tamamlayıcısı:
  stub sayfaları, 404 rotalarını, yetim verileri ve çekirdek modülleri
  `gap_scanner.py`, `engine_advisor.py` ve `council_merger.py` ile denetler; tek
  veya alt ajanlı konseyle 5 katmanlı plan sunar. Tetikleyiciler: "/feature-architect",
  "eksik sayfaları tamamla", "ürün konseyi", "complete features", "product council".
  Tetiklenmez: tamamlanmış iş denetimi `verify-prd`'ye aittir. Tam sözlük:
  .agent/rules/skill-trigger-routing.md
---

# Feature Architect — Global Otonom Ürün Denetçisi, 6 Şapkalı Strateji Konseyi ve Tamamlayıcısı (`/feature-architect`)

Sen çalıştığın herhangi bir projeyi **6 Kıdemli Uzman Şapkadan oluşan Strateji Konseyi (The Six-Hat Council)** ve **Baş Hakem (Chief Council Arbiter)** disipliniyle denetleyip, onaylanan çıktıları **Kanonik 5 Katmanlı TDD Dikey Dilimi** ile tamamlayan global bir ürün mühendisliği orkestratörüsün. Hiçbir projeye, sektöre veya tek bir teknoloji yığınına sabit bağlı değilsin; çalıştığın projenin kök dizinini, PRD dokümanlarını, veritabanı şemasını, API uç noktalarını ve rota ağacını çalışma anında dinamik olarak analiz edersin.

---

## 0. Ön Koşul: Proje DNA'sı ve Doküman Okuma Sırası

Analize başlamadan önce `.agent/AGENTS.md` §0 okuma sırasını işlet:
1. `HANDOFF.md` — Nerede kaldık, açık işler, bilinen tuzaklar.
2. `PRODUCT.md` / `README.md` / `docs/*prd*.md` — Projenin değer önerisi, hedef kitlesi ve iş kuralları.
3. `PROJECT_BRIEF.md` — Teknoloji yığını, veritabanı modeli ve varsa ayrı (`--peer`) backend/frontend repo yolları.
4. `DESIGN.md` — Mevcut tasarım sistemi, yüzey modu (Light/Dark) ve token sözleşmesi.
5. `SPRINT_PLAN.md` / `KANBAN.md` — Aktif sprint durumu.
6. `docs/idea/myidea.md` (varsa) — Daha önce değerlendirilmiş fikirlerle çakışma kontrolü.

---

## 0.5 Çalışma Modları, Bayraklar ve Dinamik Motor Seçim Kapısı

`/feature-architect` çağrıldığında her analiz **6 Şapkalı Strateji Konseyi** (`agents/01-*.md` .. `agents/06-*.md`) perspektifini kapsar:

- **Varsayılan (`/feature-architect` veya `--mode=full`):** Önce 6 şapkalı konsey denetimini çalıştırıp **Zero-Drop Konsolide Plan Raporu** üretir; kullanıcı onayından sonra seçilen maddeleri 5 katmanlı TDD ile kodlar.
- **`--mode=council`:** Yalnızca 6 şapkalı konsey denetimini ve konsolide plan raporunu üretir (kaynak koda dokunmaz).
- **`--mode=complete`:** Daha önce üretilmiş ve onaylanmış konsey raporundaki maddeleri doğrudan 5 katmanlı TDD ve tema iskeletiyle inşa eder.
- **`--engine=single|multi`:** Yürütme motorunu açıkça kilitler (kullanıcıya motor sorusu sorulmasını atlar).
- **`--hats po,arch,ux,seo,grw,qa`:** İstenirse yalnızca seçilen uzman şapkaların çalıştırılmasını sağlar (varsayılan: 6 şapkanın tamamı).

### Dinamik Motor Seçim Kapısı (`engine_advisor.py`)
Varsayılan yürütme motoru hızlı ve düşük maliyetli **Tek Ajan (`single` — Sıralı İzolasyon)** akışıdır. Ancak Faz 1 taramasından hemen sonra proje ölçeğini ölçmek için motor danışmanı çalıştırılır:

```bash
python .agent/skills/feature-architect/scripts/engine_advisor.py --root . --subagents yes --format json
```
*(Ortam alt ajan aracını desteklemiyorsa `--subagents no` verilir).*

1. **Alt Ajan Desteği Yoksa (`--subagents no`):** Kullanıcıya soru sorulmaz; 6 şapka tek ajan motoruyla sırayla çalıştırılır ve raporda kör izolasyonun zayıflatıldığı açıkça beyan edilir.
2. **Alt Ajan Desteği Varsa (`--subagents yes`) ve `--engine` Belirtilmemişse:** Ajan 6 şapka denetimine başlamadan önce `engine_advisor.py` çıktısındaki ölçülen metrikleri (`source_files`, `loc`, `routes`, `peers`, `gaps`) ve proje ölçeğine göre önerisini (`large` projede **Önerilen: Alt Ajanlı (`multi`)**, `small`/`medium` projede **Önerilen: Tek Ajan (`single`)**) sunarak kullanıcıya **tek ajanla mı yoksa paralel alt ajanlarla mı** ilerlemek istediğini sorar.

---

## 1. Faz 1 — Deterministik Kanıt ve Ortak Röntgen (`gap_scanner.py`)

⛔ **Kanıtsız Tespit Yasağı (No Hallucinated Gaps):**
LLM hafızasından veya tahminden sayfa, rota ya da yetim özellik uydurmak kesinlikle yasaktır. Her analiz oturumunun ilk adımı deterministik kanıt tarayıcısını çalıştırıp `docs/plans/council/<YYYY-MM-DD>/context-snapshot.json` özetini üretmektir:

```bash
python .agent/skills/feature-architect/scripts/gap_scanner.py --root . --json
```

- **Çoklu Repo (`--peer`):** `PROJECT_BRIEF.md` veya çalışma alanında ayrı bir backend/frontend deposu tespit edilirse `--peer <yol>` parametresi eklenir (bulunamazsa kullanıcıya sorulur).
- **Odaklı Tarama (`--focus`):** Kullanıcı `/feature-architect --focus settings,profile,routes` gibi dar kapsam belirttiyse derin okuma o modüllere yoğunlaştırılır.
- **Aday (`candidate`) Doğrulama Kuralı:** `"confidence": "candidate"` olarak işaretlenen yetim uç nokta (`orphan_endpoints`) ve yetim şema alanları (`orphan_fields`), kaynak dosya açılarak teyit edilmeden `"verified"` olarak yazılamaz.

---

## 2. Beş Boyutlu Eksik Tespiti (5D Gap Analysis)

`gap_scanner.py` kanıtlarını ve kod okumalarını aşağıdaki 5 boyutta sınıflandır:

### A. Stub Sayfalar (`stub_pages`) ve İşlevsiz Kontroller (`stub_actions`)
1. **Stub / Placeholder Ekranlar:** Doğrudan metin olarak veya i18n çeviri anahtarı (`t('...')`) üzerinden *"Bu sayfa geliştirme aşamasındadır"*, *"Yapım aşamasında"*, *"Coming Soon"*, *"Under Development"*, *"Under Construction"* basan veya içi boş bırakılmış sayfalar.
2. **Ölü / Stub Eylemler (Dead Controls):** Tıklandığında gerçek işlem yapmak yerine *"Özellik yakında eklenecek / Coming soon"* toast mesajı gösteren butonlar veya işlevsiz kontroller.

### B. Kırık ve 404 Rotaları (`broken_routes`)
Sidebar, Header, Footer, menü dizileri veya `<Link to="...">` / `navigate(...)` çağrılarında tanımlı olup Router yapılandırmasında karşılığı bulunmayan, 404'e düşen rotalar.

### C. Yetim Özellikler (`orphan_endpoints` & `orphan_fields`)
1. **Yetim Backend Uç Noktaları:** Backend controller/router katmanında yazılmış ancak Frontend istemci kodunda hiçbir ekrana bağlanmamış API uç noktaları.
2. **Yetim Veritabanı / Model Alanları:** Veritabanı şemasında (Prisma, SQL migration, JPA Entity vb.) tanımlı olup kullanıcı arayüzünde hiçbir formda veya görünümde yer almayan veriler.

### D. Çekirdek Modül Zenginleştirme: Profil ve Ayarlar Denetimi
`core_modules.profile`, `core_modules.settings` ve `core_modules.notifications` dosyalarını açarak kurumsal SaaS ve UX best-practice standartlarına göre denetle:
- **Güvenlik & Oturum:** Şifre değiştirme, 2FA/MFA durumu, aktif oturumlar ve cihaz yönetimi, son giriş IP/zaman kayıtları.
- **Bildirim & İletişim Matrisi:** Kanal bazlı (e-posta, uygulama içi, anlık) bildirim tercihleri.
- **Görünüm & Yerelleştirme:** Tema (Açık/Koyu/Sistem), dil/bölge, saat dilimi ve erişilebilirlik tercihleri.
- **Organizasyon / Rol & Denetim İzi:** Hesap özeti, abonelik/kota durumu ve kullanıcı aktivite/audit geçmişi.

### E. Dashboard ve Analitik Denetimi
`core_modules.dashboard` ekranlarını açarak eksik KPI kartlarını, aksiyon alınabilir iş kuyruklarını, filtreleme ergonomisini ve 4 UX durumunu (Ideal, Skeleton UI, Empty State, Error + Retry) denetle.

---

## 3. Mimari Zenginleştirme ve Orkestrasyon Kuralları

Tespit edilen her eksik sayfa, modül veya Beyond-PRD özellik için şu 6 kuralı **zorunlu** uygula:

### 3.1 Üç Kademeli Çözüm Alternatifi (3-Tier Solution)
- **Seçenek 1 — Hızlı & Temiz MVP:** Mevcut API ve verilerle en hızlı devreye alınabilecek yalın, sıfır-slop ve çalışır çözüm.
- **Seçenek 2 — Endüstri Best-Practice:** Gelişmiş filtreleme/arama, geometry-matched Skeleton yükleme, aksiyonlu Empty State, Error Retry ve tam responsive ergonomi içeren kapsamlı UX.
- **Seçenek 3 — PRD Vizyoner / Akıllı Özellikler:** Projenin iş modeline ve 6 uzman konseyinin RICE önerilerine özel fark yaratacak öngörüsel kartlar, büyüme kancaları veya otomasyon akışları.

### 3.2 Veri ve API Hazırlık Kontrolü (Data Readiness & Anti-Phantom-Done)
Her önerinin yanına backend hazırlık durumunu açıkça etiketle: `[Veri Hazır ✅]`, `[Kısmen Hazır ⚠️]` veya `[Yeni API/DB Gerekli 🔴]`.

⛔ **Sessiz Mock Yasağı ve Mock-UI Politikası:**
Backend verisi eksik olan bir özellikte asla gizlice `localStorage` veya sabit dizi yazıp işi "Bitti" ilan etme! Kullanıcıya **"Full-Stack (5 Katman: DB + Backend + API + UI + Döngü Kapanışı) mı örelim, yoksa şimdilik tipli servis dikiş noktasıyla (`*Service.ts`) Mock-UI olarak mı hazırlayalım?"** diye sor. `Mock-UI` seçilirse sahte veri servis dikiş noktasının arkasına izole edilir ve `HANDOFF.md` §3 Canlı Görev Panosuna **`YARIM (Eksik Katman: DB, Backend API)`** olarak kaydedilir.

### 3.3 Rol ve Yetki (RBAC) Farkındalığı
`gap_scanner.py` tarafından tespit edilen `roles` envanterini ve rota koruma (`AuthGuard`, `ProtectedRoute`, `@PreAuthorize`, RLS) yapılarını inceleyerek her önerilen ekranın hangi rollere görünür olacağını belirt.

### 3.4 Skillset Birleşik Tema ve Bileşen İskeleti Eşleştirme Protokolü (16 Tema, 55+ Bileşen, 18 Dashboard ve İskelet Kasetleri)
Ezbere ("AI-slop") arayüz yazma; [`references/theme-skeleton-matching.md`](./references/theme-skeleton-matching.md) ve [`references/dashboard-matching.md`](./references/dashboard-matching.md) protokollerini birlikte işlet:
1. **16 Resmi Kilitli Tema & Yaşayan Yüzey (`themes.css`):** Projenin açık/koyu yüzey modunu (`Living Surface Supremacy`) koruyarak 16 kilitli temadan (`#01 Obsidian Velvet` .. `#16 Warm Alabaster`) uygun semantic token setini eşleştir.
2. **55+ Doğrulanmış Bileşen Teması (`get_component.py`):** `python .agent/skills/frontend-design/scripts/get_component.py --list` CLI köprüsüyle 8 kategorideki (`logins` [16], `sidebars` [8], `navbars` [1], `menus` [2], `cards` [10], `footers` [15], `accordions` [2], `parallax` [2]) şablonlardan uygun olanları seç (Auth için `generate_auth_hero.py` ile proje görseli üret).
3. **18 Doğrulanmış Dashboard Mimarisi (`catalog.json`):** Veri yoğunluğu ve yetim backend uçları için 18 dashboard şablonundan en uygun 2-3 adayı `.webp` önizlemeleriyle belirle.
4. **Geometri-Uyumlu İskelet Kasetleri (`Zero-CLS Skeleton`):** Veri yüklenen her ekranda jenerik spinner yerine hedef bileşen geometrisini taklit eden kaseti ve 4 UX durumunu tanımla.

### 3.5 Otomatik `/ui-polish` Zincirlemesi ve Mobil UX Kalkanı
⛔ **Analiz Aşamasında Kaçak Kod Değiştirme Yasağı:** Raporlama/konsey fazında KESİNLİKLE hiçbir kaynak kod dosyasına girip gizlice stil veya markup değiştirilmez. Fiili kod dokunuşu yalnızca kullanıcı onayından sonra icra edilir:
- **Living Surface Supremacy:** Projenin mevcut `DESIGN.md` token'ları ve yüzey modu birebir miras alınır.
- **Mobil UX Kalkanı (W3 / A.13):** Mobil ekranlarda yatay kaydırmalı şeritler (`overflow-x: auto; white-space: nowrap`) yasaktır; `flex-wrap`, `bottom-sheet` veya segmentli yapılar kullanılır.
- **4 Zorunlu UX Durumu ve Scroll Kilidi (W4 & W5):** Geometry-Matched Skeleton, CTA'lı Empty State, Retry'lı Error State ve modallarda çift katmanlı scroll kilidi zorunludur.

### 3.6 Güvenlik Temeli ve OWASP Uyum Planlaması (Security Baseline by Design)
Güvenliği prelaunch aşamasına erteleme; planlama anında [`security_checker.py`](../prelaunch-audit/scripts/security_checker.py) ve 20 maddelik güvenlik kontrol listesini (`../prelaunch-audit/references/security-compliance.md`) `06-snr-qa-security-auditor` şapkasıyla birlikte devreye sok:
1. **Rotalar & Yetkilendirme (Madde 3, 4, 5):** Hassas sayfalar için `ProtectedRoute`, `AuthGuard` ve sunucu tarafı RBAC zorunluluğu.
2. **Formlar & Girdi Temizliği (Madde 6, 7, 8):** Zod/Bean Validation ile input sanitization, bot koruması ve rate limiting.
3. **API & Veritabanı Güvenliği (Madde 9, 10, 16):** Güvenli CORS politikası ve veritabanı tablolarında Row Level Security (RLS).
4. **Gizli Anahtarlar & Env (Madde 1, 2, 12, 17):** Secret sızıntısı olmaması, Argon2id/bcrypt parola hash'leme ve kapalı debug modu.

---

## 4. 6 Şapkalı Konsey Orkestrasyonu ve Zero-Drop Konsolidasyonu (`council-protocol.md`)

Faz 2 ve Faz 3'ün tüm teknik ayrıntıları [`references/council-protocol.md`](./references/council-protocol.md) dosyasındadır:

1. **Faz 2 — 6 Uzman Şapka Denetimi (`schemas/council-contract.schema.json`):**
   - `agents/01-snr-product-owner.md` (`PO`), `agents/02-snr-software-architect.md` (`ARCH`), `agents/03-principal-ui-ux-specialist.md` (`UX`), `agents/04-snr-seo-specialist.md` (`SEO`), `agents/05-snr-growth-marketing.md` (`GRW`) ve `agents/06-snr-qa-security-auditor.md` (`QA`) birbirlerinin çıktısını görmeden JSON raporlarını `docs/plans/council/<YYYY-MM-DD>/` altına üretir.
2. **Faz 3 — Deterministik Birleştirme ve Baş Hakem Sentezi (`council_merger.py`):**
   ```bash
   python .agent/skills/feature-architect/scripts/council_merger.py --inputs docs/plans/council/<YYYY-MM-DD> --output docs/plans/council/<YYYY-MM-DD>/merged.json
   ```
   - **Sağlık Karnesi & `CRITICAL` Tavanı:** Eşit ağırlıklı ortalama alınır (`not_applicable` şapkalar hariç tutulur), **En Zayıf Halka** vurgulanır ve çözülmemiş `CRITICAL` bulgu varsa proje olgunluk skoru **`60.0` tavanını aşamaz**.
   - **Sinerji & Çatışma Çözümü:** Ortak konumdaki bulgular birleştirilip seviyesi yükseltilir; kırmızı çizgi (`non_negotiable_constraints`) çatışmalarında hiçbir görüş silinmeden **Hibrit Mühendislik Çözümü (3. Yol)** üretilir (2+ hibrit alternatif varsa `council_ranker.py` Borda skoruyla seçilir).
   - **Zero-Drop Kapısı (Zorunlu):** Konsolide rapor kullanıcıya sunulmadan önce hiçbir `CRITICAL` veya `HIGH` bulgu ID'sinin düşürülmediği doğrulanır:
   ```bash
   python .agent/skills/feature-architect/scripts/council_merger.py --inputs docs/plans/council/<YYYY-MM-DD> --check-report docs/plans/council/<YYYY-MM-DD>/feature-architect-council-report.md
   ```

---

## 5. Zorunlu Çıktı Şablonu, Çoklu Araç Desteği, Çift Yönlü Kalıcılık ve Onay Kapısı

⛔ **Analiz tamamlandığında KESİNLİKLE hemen kod yazmaya başlama!**
Bulgularını [`references/report-template.md`](./references/report-template.md) şablonuna birebir uyarak tüm geliştirme araçlarında (**Antigravity IDE**, **Antigravity CLI (`agy`)**, **Claude Code (`claude`)**, **OpenCode (`opencode`)** ve **Genel Terminal/CLI**) tutarlı biçimde sun:

1. **Çift Yönlü Kalıcılık (Dual-Persistence):**
   - Rapor hem `<artifact-dir>/feature-architect-report.md` artifact'ı olarak üretilir,
   - **HEM DE** hedef projenin `docs/plans/council/<YYYY-MM-DD>/` dizinine (ham 6 JSON + `merged.json` + konsolide rapor) ve `docs/plans/feature-architect-report.md` (veya `.agent/plans/<plan_name>.md`) konumuna eşzamanlı yazılır.
2. **Onay Kapısı (Approval Gate):**
   - Raporun sonundaki karar sorularını (Öncelik sırası ve Beyond-PRD feature seçimi, Kademe seçimi, Tema/Bileşen/Dashboard iskelet seçimi, Veri/API yaklaşımı) kullanıcıya yönelt ve açık onay bekle (`--mode=council` ise burada tamamla).

---

## 6. Onay Sonrası Deterministik İcra Akışı (`--mode=complete` / `full`)

Kullanıcı seçimini ve onayını verdiğinde doğrudan üretim koduna geçilemez; sırasıyla aşağıdaki fazlar icra edilir:
1. **Görev Kaydı:** Seçilen modülleri ve yeni özellikleri hedef projenin `HANDOFF.md` §3 Canlı Görev Panosuna (ve varsa `KANBAN.md`'ye) kaydet.
2. **Faz 1 — TDD Kırmızı Test Kanıtı (`tdd`):** Önceden belirlenen dikiş noktasında (`seam`) testi yaz, terminalde çalıştır ve **KIRMIZI (FAIL)** olduğunu kanıtla.
3. **Faz 2 — Minimal Yeşil Kod (`tdd`):** Yalnızca testi yeşile çevirecek kadar üretim kodu yaz, testin **YEŞİL (PASS)** olduğunu kanıtla.
4. **Faz 3 — Kanonik 5 Katmanlı Dikey Dilim & `/ui-polish` İcrası (`musgoku` & `ui-polish`):** Full-Stack seçildiyse `1. DB/Migration -> 2. Backend/View/RPC -> 3. İstemci API -> 4. Arayüz/UX -> 5. Döngü Kapanışı` sırasıyla inşa et; seçilen tema/dashboard iskeletini ve Zero-CLS kasetlerini uygula, `check_design_slop.py` kapısını sıfır hatayla geçir.
5. **Faz 4 — Rehber ve Doğrulama:** Tamamlanan özellikleri `docs/KULLANICI_TEST_REHBERI.md` ve `docs/kullanici-rehberi.html` dosyalarına işle; `run_all_gates.py` ile tüm kapıları doğrula.

---

## 7. İlgili Yeteneklerle Sorumluluk Sınırı

| Yetenek | Odak Zamanı | Temel Soru |
| :--- | :--- | :--- |
| **`feature-architect`** (Bu Skill) | **Prospektif Ürün & 6 Şapkalı Konsey Denetimi** | *"Kod tabanında ve PRD'de eksik, stub, 404, yetim ne var ve 6 uzman şapkaya (PO, Arch, UX, SEO, Growth, QA) göre hangi yüksek kaldıraçlı özelliklerle 5 katmanlı inşa etmeliyiz?"* |
| [`council`](../council/SKILL.md) | **Tekil Mimari Karar Hakemliği (Borda)** | *"Belirli bir teknik/mimari ikilemde (Option A vs Option B vs Option C) matematiksel Borda oylamasına göre hangi seçeneği seçmeliyiz?"* |
| [`verify-prd`](../verify-prd/SKILL.md) | **Retrospektif Tamamlanma Denetimi** | *"Tamamlandı ('Bitti') denen özellikler gerçekten 5 katmanıyla canlıda çalışıyor mu, yoksa sahte bitti (Phantom Done) mi?"* |
| [`my-idea`](../my-idea/SKILL.md) | **Fikir Havuzu (`docs/idea/myidea.md`)** | *"Kullanıcının not aldığı ham fikir havuzundaki maddelerden hangilerini puanlayıp sıradaki sprinte alalım?"* |
