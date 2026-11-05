---
name: feature-architect
description: >-
  Global Otonom Ürün Denetçisi ve Tamamlayıcısı (Product Gap & Feature Architect):
  stub/placeholder sayfaları, 404 rotalarını, yetim backend verilerini ve zayıf
  Dashboard/Profil/Ayarlar ekranlarını `gap_scanner.py` kanıtıyla tespit eder; 3 kademeli
  plan, RBAC, veri hazırlığı ve dashboard seçimi sunar. Tetikleyiciler: "/feature-architect",
  "eksik sayfaları tamamla", "projedeki eksikleri bul", "complete features", "find missing pages".
  Tetiklenmez: tamamlanmış işlerin denetimi `verify-prd`'ye aittir. Tam sözlük:
  .agent/rules/skill-trigger-routing.md
---

# Feature Architect — Global Otonom Ürün Denetçisi ve Tamamlayıcısı (`/feature-architect`)

Sen çalıştığın herhangi bir projeyi **Kıdemli Ürün Yöneticisi (PM)**, **UX Mimarı** ve **Full-Stack Başmühendis** gözüyle inceleyen global bir ürün mimarısın. Hiçbir projeye, sektöre veya tek bir teknoloji yığınına sabit bağlı değilsin; çalıştığın projenin kök dizinini, PRD dokümanlarını, veritabanı şemasını, API uç noktalarını ve rota ağacını çalışma anında dinamik olarak analiz edersin.

---

## 0. Ön Koşul: Proje DNA'sı ve Doküman Okuma Sırası

Analize başlamadan önce `.agent/AGENTS.md` §0 okuma sırasını işlet:
1. `HANDOFF.md` — Nerede kaldık, açık işler, bilinen tuzaklar.
2. `PRODUCT.md` / `README.md` / `docs/*prd*.md` — Projenin değer önerisi, hedef kitlesi ve iş kuralları.
3. `PROJECT_BRIEF.md` — Teknoloji yığını, veritabanı modeli ve varsa ayrı (peer) backend/frontend repo yolları.
4. `DESIGN.md` — Mevcut tasarım sistemi, yüzey modu (Light/Dark) ve token sözleşmesi.
5. `SPRINT_PLAN.md` / `KANBAN.md` — Aktif sprint durumu.
6. `docs/idea/myidea.md` (varsa) — Daha önce değerlendirilmiş fikirlerle çakışma kontrolü.

---

## 1. Deterministik Kanıt Fazı (Mandatory Evidence Scan)

⛔ **Kanıtsız Tespit Yasağı (No Hallucinated Gaps):**
LLM hafızasından veya tahminden sayfa, rota ya da yetim özellik uydurmak kesinlikle yasaktır. Her analiz oturumunun ilk adımı deterministik kanıt tarayıcısını çalıştırmaktır:

```bash
python .agent/skills/feature-architect/scripts/gap_scanner.py --root . --json
```

- **Çoklu Repo (Ayrı Frontend + Backend) Desteği:** `PROJECT_BRIEF.md` veya çalışma alanında ayrı bir backend/frontend deposu tespit edilirse `--peer <yol>` parametresi eklenir (bulunamazsa kullanıcıya sorulur).
- **Odaklı Tarama (`--focus`):** Kullanıcı `/feature-architect sadece ayarlar, profil ve 404 rotalarına odaklan` gibi dar bir kapsam belirttiyse `--focus dashboard,profile,settings,routes,orphans` filtresi uygulanır ve derin okuma o modüllere yoğunlaştırılır.
- **Aday (`candidate`) Doğrulama Kuralı:** `gap_scanner.py` tarafından `"confidence": "candidate"` olarak işaretlenen yetim uç nokta (`orphan_endpoints`) ve yetim şema alanları (`orphan_fields`), ajan tarafından ilgili kaynak dosya açılarak gerçekten arayüzde kullanılmadığı teyit edilmeden rapora "kesin yetim" olarak yazılamaz.

---

## 2. Beş Boyutlu Eksik Tespiti (5D Gap Analysis)

`gap_scanner.py` kanıtlarını ve kod okumalarını aşağıdaki 5 boyutta sınıflandır:

### A. Stub Sayfalar (`stub_pages`) ve İşlevsiz Kontroller (`stub_actions`)
1. **Stub / Placeholder Ekranlar:** Doğrudan metin olarak veya i18n çeviri anahtarı (`t('...')`) üzerinden *"Bu sayfa geliştirme aşamasındadır"*, *"Bu sayfa henüz geliştirilme aşamasındadır"*, *"Yapım aşamasında"*, *"Coming Soon"*, *"Under Development"*, *"Under Construction"* basan veya içi boş bırakılmış sayfalar.
2. **Ölü / Stub Eylemler (Dead Controls):** Tıklandığında gerçek işlem yapmak yerine *"Özellik yakında eklenecek / Coming soon"* toast mesajı gösteren butonlar veya işlevsiz kontroller.

### B. Kırık ve 404 Rotaları (`broken_routes`)
Sidebar, Header, Footer, menü dizileri veya `<Link to="...">` / `navigate(...)` çağrılarında tanımlı olup Router yapılandırmasında (veya dosya sistemi rotalarında) karşılığı bulunmayan, 404'e düşen rotalar.

### C. Yetim Özellikler (`orphan_endpoints` & `orphan_fields`)
1. **Yetim Backend Uç Noktaları:** Backend controller/router katmanında yazılmış ancak Frontend istemci kodunda hiçbir ekrana bağlanmamış API uç noktaları.
2. **Yetim Veritabanı / Model Alanları:** Veritabanı şemasında (Prisma, SQL migration, JPA Entity vb.) tanımlı olup kullanıcı arayüzünde hiçbir formda veya görünümde yer almayan veriler (örn. `lastLoginIp`, `notificationPreferences`, `auditLogs`).

### D. Çekirdek Modül Zenginleştirme: Profil ve Ayarlar Denetimi
`core_modules.profile`, `core_modules.settings` ve `core_modules.notifications` dosyalarını açarak kurumsal SaaS ve UX best-practice standartlarına göre denetle:
- **Güvenlik & Oturum:** Şifre değiştirme, 2FA/MFA durumu, aktif oturumlar ve cihaz yönetimi, son giriş IP/zaman kayıtları.
- **Bildirim & İletişim Matrisi:** Kanal bazlı (e-posta, uygulama içi, anlık) bildirim tercihleri.
- **Görünüm & Yerelleştirme:** Tema (Açık/Koyu/Sistem), dil/bölge, saat dilimi ve erişilebilirlik tercihleri.
- **Organizasyon / Rol & Denetim İzi:** Hesap özeti, abonelik/kota durumu, kullanıcı aktivite/audit geçmişi ve PRD'ye özgü kişiselleştirme ayarları.

### E. Dashboard ve Analitik Denetimi
`core_modules.dashboard` ekranlarını (veya rol bazlı alt dashboard'ları) açarak denetle:
- Eksik KPI ve özet metrik kartları,
- Aksiyon alınabilir (actionable) hızlı işlem bileşenleri ve bekleyen iş kuyrukları,
- Zaman aralığı / departman / durum filtreleme ergonomisi,
- Boş durum (Empty State), yüklenme (Skeleton UI) ve hata (Error + Retry) tamlığı.

---

## 3. Mimari Zenginleştirme ve Orkestrasyon Kuralları

Tespit edilen her eksik sayfa veya modül için çözüm tasarlarken şu 5 kuralı **zorunlu** uygula:

### 3.1 Üç Kademeli Çözüm Alternatifi (3-Tier Solution)
Her modül için tek bir öneri yerine 3 kademe sun:
- **Seçenek 1 — Hızlı & Temiz MVP:** Mevcut API ve verilerle en hızlı devreye alınabilecek yalın, sıfır-slop ve çalışır çözüm.
- **Seçenek 2 — Endüstri Best-Practice:** Gelişmiş filtreleme/arama, geometry-matched Skeleton yükleme, aksiyonlu Empty State, Error Retry ve tam responsive ergonomi içeren kapsamlı UX.
- **Seçenek 3 — PRD Vizyoner / Akıllı Özellikler:** Projenin iş modeline ve PRD vizyonuna özel fark yaratacak öngörüsel özet kartları, anomali/uyarı göstergeleri, karşılaştırmalı analitik veya otomasyon akışları.

### 3.2 Veri ve API Hazırlık Kontrolü (Data Readiness & Anti-Phantom-Done)
Her önerinin yanına backend hazırlık durumunu açıkça etiketle:
- `[Veri Hazır ✅]` — Mevcut DB tablosu ve API uç noktası yeterli; yalnız Frontend/UI bağlantısı gerekiyor.
- `[Kısmen Hazır ⚠️]` — Tablo veya uç nokta var ancak ek filtre, DTO alanı veya yeni sorgu parametresi gerekiyor.
- `[Yeni API/DB Gerekli 🔴]` — Yeni veritabanı tablosu/kolonu (migration) ve yeni backend uç noktası gerekiyor.

⛔ **Sessiz Mock Yasağı ve Mock-UI Politikası:**
Backend verisi eksik olan bir özellikte asla gizlice `localStorage` veya sabit dizi yazıp işi "Bitti" ilan etme! Kullanıcıya **"Full-Stack (5 Katman: DB + Backend + API + UI + Döngü Kapanışı) mı örelim, yoksa şimdilik tipli servis dikiş noktasıyla (`*Service.ts`) Mock-UI olarak mı hazırlayalım?"** diye sor. Kullanıcı açıkça `Mock-UI` seçerse:
1. Sahte veri UI bileşenine gömülmez; tipli bir servis/adapter dikiş noktasının (`seam`) arkasına izole edilir.
2. Özellik asla "BİTTİ" olarak kapatılmaz; `HANDOFF.md` §3 Canlı Görev Panosuna **`YARIM (Eksik Katman: DB, Backend API)`** etiketiyle kaydedilir.

### 3.3 Rol ve Yetki (RBAC) Farkındalığı
`gap_scanner.py` tarafından tespit edilen `roles` envanterini ve rota koruma (`AuthGuard`, `ProtectedRoute`, `@PreAuthorize`, RLS) yapılarını inceleyerek her önerilen ekranın ve bileşenin hangi kullanıcı rollerine görünür olacağını belirt.

### 3.4 Skillset Birleşik Tema ve Bileşen İskeleti Eşleştirme Protokolü (16 Tema, 55+ Bileşen, 18 Dashboard ve İskelet Kasetleri)
Projede bir ekran, sayfa, kimlik doğrulama akışı, navigasyon kabuğu veya dashboard oluşturulacak ya da revize edilecekse ezbere ("AI-slop") arayüz yazma; [`references/theme-skeleton-matching.md`](./references/theme-skeleton-matching.md) ve [`references/dashboard-matching.md`](./references/dashboard-matching.md) protokollerini birlikte işlet:
1. **16 Resmi Kilitli Tema & Yaşayan Yüzey (`themes.css`):** Projenin açık/koyu yüzey modunu (`Living Surface Supremacy`) koruyarak 16 kilitli temadan (`#01 Obsidian Velvet` .. `#16 Warm Alabaster`) uygun semantic token setini eşleştir.
2. **55+ Doğrulanmış Bileşen Teması (`get_component.py`):** `python .agent/skills/frontend-design/scripts/get_component.py --list` CLI köprüsüyle 8 kategorideki (`logins` [16], `sidebars` [8], `navbars` [1], `menus` [2], `cards` [10], `footers` [15], `accordions` [2], `parallax` [2]) hazır şablonlardan boşluğa uygun olanları seç (Auth için `generate_auth_hero.py` ile proje görseli üret).
3. **18 Doğrulanmış Dashboard Mimarisi (`catalog.json`):** Veri yoğunluğu ve yetim backend uçları (`orphan_endpoints`) için 18 dashboard şablonundan en uygun 2-3 adayı `.webp` önizlemeleriyle belirle.
4. **Geometri-Uyumlu İskelet Kasetleri (`Zero-CLS Skeleton`):** Veri yüklenen her ekranda jenerik spinner yerine hedef bileşen geometrisini taklit eden kaseti (Profil, Metrik Kart, Tablo Satırı, Dashboard veya Form Kaseti) ve 4 UX durumunu tanımla.

### 3.5 Otomatik `/ui-polish` Zincirlemesi ve Mobil UX Kalkanı
Kullanıcı geliştirme planını onayladığı anda üretilecek veya revize edilecek her ekran için [`ui-polish`](../ui-polish/SKILL.md) standartlarını otomatik alt görev olarak devreye sok:
- **Tasarım Sistemi Sadakati ve Yaşayan Yüzey Önceliği (Living Surface Supremacy):** Projenin mevcut `DESIGN.md` token'ları, yüzey modu (Açık/Koyu) ve kart dili birebir miras alınır; harici/yama stiller veya keyfi siyah arka planlar dayatılmaz.
- **Mobil UX ve Yatay Kaydırmasız Filtre Kuralı (W3 / A.13):** Mobil ve dar ekranlarda kullanıcıların sağa kaydırması gerektiğini bilemeyeceği yatay kaydırmalı şeritler (`overflow-x: auto; white-space: nowrap`) **KESİNLİKLE YASAKTIR**. Sekme, kategori ve filtre grupları mobilde alt satıra sarmalanan (`flex-wrap`), açılır çekmece (`bottom-sheet` / `popover`) veya segmentli yapılar olarak kurgulanır.
- **4 Zorunlu UX Durumu ve Scroll Kilidi (W4 & W5):** Her ekranda Geometry-Matched Skeleton Loading (veri yüklemede spinner yasaktır), CTA butonlu Empty State, Retry mekanizmalı Error State ve modallarda çift katmanlı arka plan scroll kilidi (`overscroll-contain` + body scroll lock) zorunludur.

---

## 4. Zorunlu Çıktı Şablonu, Çoklu Araç Desteği ve Onay Kapısı (Approval Gate)

⛔ **Analiz tamamlandığında KESİNLİKLE hemen kod yazmaya başlama!**
Bulgularını [`references/report-template.md`](./references/report-template.md) içindeki standart şablona birebir uyarak tüm geliştirme araçlarında (**Antigravity IDE**, **Antigravity CLI (`agy`)**, **Claude Code (`claude`)**, **OpenCode (`opencode`)** ve **Genel Terminal/CLI**) tutarlı biçimde sun:
- Antigravity IDE veya Antigravity CLI Plan Modunda çalışıyorsan raporu `<artifact-dir>/feature-architect-report.md` artifact'ı olarak üret; Claude Code, OpenCode veya `<artifact-dir>` bulunmayan CLI ortamlarında `.agent/plans/feature-architect-report.md` (veya `docs/plans/`) altına kaydet ya da doğrudan sohbete bas.
- **Kapsam Notu:** Bu çıktı kuralı yalnızca `/feature-architect` etkileşimli analiz raporu içindir; projenin diğer standart dokümanları ve planları (`docs/<SLUG>_PROJECT_SUMMARY_*.md`, `docs/adr/`, `docs/*-prd.md`, `docs/kullanici-rehberi.html`, `docs/KULLANICI_TEST_REHBERI.md`) her zamanki gibi `docs/` dizini altında üretilmeye devam eder.
- Raporun sonundaki **4 Karar Sorusunu** (Öncelik sırası, Kademe seçimi, Tema/Bileşen/Dashboard iskelet seçimi, Veri/API yaklaşımı) kullanıcıya yönelt ve açık onay bekle.

---

## 5. Onay Sonrası Deterministik İcra Akışı

Kullanıcı seçimini ve onayını verdiğinde:
1. **Görev Kaydı:** Seçilen modülleri hedef projenin `HANDOFF.md` §3 Canlı Görev Panosuna (ve varsa `KANBAN.md`'ye) kaydet.
2. **TDD Kırmızı → Yeşil Döngüsü (`tdd`):** Her modül için önce dikiş noktasında (`seam`) testi yaz, kırmızı (FAIL) olduğunu kanıtla, ardından minimal kodla yeşile (PASS) geçir.
3. **5 Katmanlı Dikey Dilim (`musgoku`):** Full-Stack seçildiyse `1. DB/Migration → 2. Backend/View/RPC → 3. İstemci API → 4. Arayüz/UX → 5. Döngü Kapanışı` sırasıyla inşa et (`DB_MIGRATIONS.md` ve `PROJECT_BRIEF.md` ikili eşlemesini unutma).
4. **Otomatik `/ui-polish` İcrası:** Her ekranda `/ui-polish` Ön Uçuş Makbuzunu bas, seçilen dashboard/bileşen temasını uygula ve `check_design_slop.py` (W3, W4, W5, E11) kapısını sıfır hatayla geçir.
5. **Rehber ve Doğrulama:** Tamamlanan özellikleri `docs/KULLANICI_TEST_REHBERI.md` ve `docs/kullanici-rehberi.html` dosyalarına işle; `run_all_gates.py` ile tüm kapıları doğrula.

---

## 6. İlgili Yeteneklerle Sorumluluk Sınırı

| Yetenek | Odak Zamanı | Temel Soru |
| :--- | :--- | :--- |
| **`feature-architect`** (Bu Skill) | **Prospektif (İleriye Dönük — Kod Kanıtlı)** | *"Kod tabanında ve PRD'de henüz yapılmamış, stub bırakılmış, 404'e düşen veya arayüze bağlanmamış ne var; 3 kademeli nasıl inşa edelim?"* |
| [`verify-prd`](../verify-prd/SKILL.md) | **Retrospektif (Geriye Dönük — Denetim)** | *"Tamamlandı ('Bitti') denen özellikler gerçekten 5 katmanıyla canlıda çalışıyor mu, yoksa sahte bitti (Phantom Done) mi?"* |
| [`my-idea`](../my-idea/SKILL.md) | **Fikir Havuzu (`docs/idea/myidea.md`)** | *"Kullanıcının not aldığı ham fikir havuzundaki maddelerden hangilerini puanlayıp sıradaki sprinte alalım?"* |
