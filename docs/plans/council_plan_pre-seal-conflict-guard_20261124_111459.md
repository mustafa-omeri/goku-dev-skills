# Ön-Mühürleme (`/seal-plan`) ve Sprint/Kanban Plan Çakışma, Tekrar & Ezme (Clobber) Tespit Motoru Uygulama Planı
<!-- 
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2 · .agent/rules/aviation-documentation-standard.md (FAA AC 121-24C + /caveman)
-->

> **Hedef Dal / Sürüm:** `main / v1.43.0` · **Tarih:** `2026-11-24`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `council`, `karpathy-guidelines`, `musgoku`, `tdd`, `doc-coauthoring`, `sprint-delivery-workflow`, `cognitive-counsel-framework`  
> **Kullanılan MCP'ler:** `second-brain-vault`, `sequential-thinking`  
> **İlgili KANBAN Kartı:** `S2-20 · GSW-PLAN-005..007`  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`  

---

## 1. [Goal Description] (Amaç & Kapsam — Mevcut Durum & Gereklilik Analizi)

### 1.1. Mevcut Durum Tespiti ("Böyle bir yapımız var mı?")
Mevcut `skillSetWorks` (`v1.42.0`) kod tabanında **plan mühürlerken (`/seal-plan`) veya `SPRINT_PLAN.md` / `KANBAN.md` / `HANDOFF.md` içine yeni maddeler eklenirken çalışan bir çakışma, tekrar ve sıralı plan ezme (clobber) tespit motoru YOKTUR**:

| Mevcut Araç | Şu An Ne Yapıyor? | Kaçırdığı Kör Nokta (Gap) |
|---|---|---|
| `archive_plan.py` (`--seal-handoff`) | Yalnızca `^\|\s*<TASK_ID>\s*\|` regex'i ile birebir aynı görev ID'si `HANDOFF.md` içinde var mı diye bakar. | Farklı ID ile yazılmış aynı işi, canlı kodda zaten var olan özelliği, zenginleştirme/sadeleştirme farkını ve bekleyen diğer planlarla dosya/endpoint çakışmasını **göremez**. |
| `check_handoff.py` (`W3`) | `docs/plans/*.md` içindeki görev ID'leri `HANDOFF.md`'den silinmiş mi (**Task Eviction**) diye bakar. | Bekleyen iki planın (`Plan A` ve `Plan B`) aynı dosyayı/tabloyu/endpoint'i birbirini ezecek şekilde değiştirdiğini **denetlemez**. |
| `check_sprint_board.py` (`E4`, `E10`) | `KANBAN.md` içinde aynı `S<n>-<nn>` kart numarasının iki kez yazılmasını ve açık kartların `RELEASE_PLAN.md`'de unutulmasını engeller. | `S2-01` ile `S3-04` kartlarının aynı bileşeni/API'yi çelişkili şekilde değiştirdiğini veya kartın zaten `Yapıldı`/canlı kodda var olduğunu **tespit edemez**. |
| `review-prd` (`prd_review_helper.py`) | Yalnızca dışarıdan bir PRD dokümanı `/review-prd` ile incelenirken çalışır. | `/plan`, `/council`, `/seal-plan` veya Sprint/Kanban kartı ekleme akışına **bağlı değildir**. |

### 1.2. Gereklilik ve 6 Şapka (`/6HAT` + `/PUSHBACK`) Analizi ("Gerçekten gerekli mi?")
Çoklu plan üretip `/seal-plan` ile kuyruğa (`docs/plans/` + `HANDOFF.md` §3 + `KANBAN.md`) atarak **sırayla geliştirme** iş akışında bu mekanizma **lüks değil, regresyon ve emek kaybını önleyen kritik bir güvenlik sübabıdır**:
1. **Risk 1 — Canlıdaki Zengin Kodu Sade Planla Ezme (`SIMPLIFIED_SUBSET_REGRESSION`):** Canlı kodda daha önce 5 katmanlı (RLS, Turnstile, Rate-limit, Zero-CLS Skeleton, `@Version` optimistic lock) geliştirilmiş bir özellik varken, sonradan yapılan bir planda aynı dosya/endpoint için daha sade/naif bir `[NEW]` veya `[MODIFY]` yazılması canlıdaki güvenlik ve UX katmanlarını **sessizce ezer ve geriye götürür**.
2. **Risk 2 — Bekleyen Sıralı Planların Birbirini Ezmesi (`QUEUED_PLAN_CLOBBER`):** Kullanıcı `Plan 1`'i mühürledi (`⬜ Bekliyor`, henüz kodlamadı), ardından `Plan 2` ve `Plan 3`'ü mühürledi. İki plan da aynı dosyayı (`src/services/user.ts`), aynı API uç noktasını (`POST /api/v1/users/update`) veya aynı DB tablosunu farklı varsayımlarla değiştiriyorsa; sırayla kodlanırken **`Plan 2`, `Plan 1`'in yaptığı geliştirmeyi ezer** veya `Plan 2`, henüz kodlanmamış `Plan 1`'in oluşturacağı `[NEW]` dosyayı `[MODIFY]` etmeye çalışarak sıralama hatasına düşer.
3. **Risk 3 — Zaten Yapılmış İşi Sıfırdan Kodlama (`ALREADY_DONE_EXACT` vs `ENRICHED_SUPERSET`):** Özellik zaten canlı kodda veya `KANBAN.md` (`Yapıldı`) içinde varsa; birebir aynısıysa (`EXACT`) uyarılıp elenmeli, zenginleştirilmiş üst kümesiyse (`ENRICHED_SUPERSET`) plandaki `[NEW]` etiketi `[MODIFY]` (mevcut dosya üzerine cerrahi genişletme) olarak düzeltilmelidir.

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: Ön-Mühürleme (/seal-plan) ve Sprint/Kanban Çakışma, Tekrar ve Ezme Kalkanı
  Scenario: Yeni planın canlı kod, tamamlanan işler ve bekleyen sıralı planlarla karşılaştırılması
    Given projede canlı kod tabanı, HANDOFF.md, KANBAN.md ve docs/plans/ altında bekleyen mühürlü planlar mevcuttur
    When kullanıcı "/seal-plan" (archive_plan.py) veya "plan_conflict_guard.py" ile yeni bir planı/kartı mühürlemek ister
    Then motor plandaki her görevi ve hedef yüzeyi (dosya, API endpoint, rota, DB tablosu) şu 6 sınıftan biriyle etiketler: "NEW_CLEAN", "ALREADY_DONE_EXACT", "ENRICHED_SUPERSET", "SIMPLIFIED_SUBSET_REGRESSION", "QUEUED_PLAN_CLOBBER", "SEQUENTIAL_ORDER_DEPENDENCY"
    And birbirini ezen bekleyen planlar veya canlı kodu geriye götüren sadeleştirmeler varsa mühürleme öncesinde erken uyarı matrisi ve çözüm önerisi basılır
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (2+ Seçenek İncelemesi)

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Salt ID & Dosya Adı Regex)** | Mevcut `archive_plan.py` içine yalnız `[DOM]-[TIP]-[NO]` ID ve düz dosya adı kontrolü eklemek | Çok az kod (~40 satır), sıfır ek script | Canlı koda bakmaz; `Birebir / Zenginleştirilmiş / Sadeleştirilmiş` ayrımı yapamaz; endpoint ve DB tablo ezmesini kaçırır | **2.00** (0 birincilik) |
| **Option B (Deterministik Çok-Katmanlı Plan, Canlı Kod & Sıralı Kuyruk Çakışma/Ezme Kalkanı — `plan_conflict_guard.py`)** | Saf Python stdlib ile Plan Parmak İzi (Dosya `[NEW/MODIFY/DELETE]`, API Endpoint, UI Rota, DB Tablo, 5-Katman Derinlik Skoru, Başlık Jaccard Benzerliği) çıkarıp **1) Canlı Kod + Biten İşler** ve **2) Bekleyen Sıralı Planlar (`docs/plans/` + `HANDOFF.md` §3 + `KANBAN.md`)** ile çapraz kıyaslayan deterministik motor | Sıfır dış bağımlılık, <200ms çalışma süresi; `Birebir / Zenginleştirilmiş / Sadeleştirilmiş` ayrımını ve `Plan 1 vs Plan 2` ezmesini (Clobber & Sıra Bağımlılığı) %100 deterministik yakalar; `/seal-plan`, `check_handoff.py` ve `check_sprint_board.py`'ye doğrudan bağlanır | ~350 satırlık yeni standart script ve test paketi gerektirir | **1.00 — KAZANAN** (3/3 birincilik) |
| **Option C (Vektör DB / LLM Embedding Servisi)** | Planları ve kodu embedding modelinden geçirip vektör benzerliğiyle aramak | Serbest metin benzerliğinde esnek | Ağır bağımlılık, yavaş, API key gerektirir, offline CLI kapılarında çalışmaz, kesin dosya/endpoint çakışmalarında halüsinasyon riski taşır | **3.00** (0 birincilik) |

- **Seçilen Yol & Gerekçe:** **Option B (`1.00` tam konsensüs skoru)** seçildi. `skillSetWorks` ekosisteminin **Sıfır-Şişkinlik (Zero-Bloat)** ve **Ölçülebilir Deterministik Kapı** ilkelerine tam uyar; hem canlı kodla kıyaslamayı (`EXACT` / `ENRICHED_SUPERSET` / `SIMPLIFIED_SUBSET_REGRESSION`) hem de bekleyen planlar arası birbirini ezme (`QUEUED_PLAN_CLOBBER` & `SEQUENTIAL_ORDER_DEPENDENCY`) analizini milisaniyeler içinde deterministik olarak üretir.
- **Birleşik Planlama Ekosistemi Bağlantısı:** Fikir (`my-idea`) → Şartname/PRD (`doc-coauthoring` / `review-prd`) → Açık Denetimi (`feature-architect`) → Konsey Hakemliği (`council`) → **Ön-Mühürleme Çakışma & Ezme Kalkanı (`plan_conflict_guard.py`)** → Görev Kartı (`KANBAN.md` / `HANDOFF.md` §3) → TDD Dikiş Noktası & 5 Katmanlı Dikey Dilim (`development-workflow.md` Adım 2.2).

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)
> [!IMPORTANT]
> **Önerilen Mimari (`plan_conflict_guard.py` + `/seal-plan` & Sprint/Kanban Entegrasyonu) Neleri Yakalayacak?**
> 1. **Canlı Kod & Tamamlanan İşlerle Kıyas (`Live Code & Done History`):**
>    - 🟢 **`ALREADY_DONE_EXACT` (Birebir Aynısı):** Plandaki hedef dosyalar, API endpoint'leri, rotalar ve kapsam canlı kodda veya `KANBAN.md` (`Yapıldı`) / `HANDOFF.md` §1 içinde zaten mevcut. *(Öneri: Mükerrer geliştirmeyi atla).*
>    - 🔵 **`ENRICHED_SUPERSET` (Zenginleştirilmiş / Üst Küme):** Hedef dosya/endpoint/tablo canlıda var ama yeni plan ek katmanlar (örn. yeni DB kolonu, RLS, pagination, yeni Gherkin senaryosu, Zero-CLS skeleton) ekliyor. *(Öneri: Planda `[NEW]` yazıldıysa `[MODIFY]`'a çevir; mevcut kodu silmeden/ezmeden genişlet).*
>    - 🔴 **`SIMPLIFIED_SUBSET_REGRESSION` (Sadeleştirilmiş / Alt Küme — Regresyon Tehlikesi!):** Canlı kodda zaten daha zengin (5 katmanlı, güvenlikli, testli) bir yapı varken yeni plan aynı dosya/endpoint üzerinde daha sade/eksik bir yapı öneriyor veya mevcut dosyayı `[NEW]` ile sıfırdan basitçe yeniden yazmaya kalkıyor. *(Öneri: Canlıdaki mevcut özellikleri ezme!)*
> 2. **Bekleyen Sıralı Planlar & Kuyruk Çakışması (`Queued Plan-vs-Plan & Backlog Clobber`):**
>    - 🔴 **`DOUBLE_NEW_OR_DELETE_CLOBBER`:** Bekleyen `Plan A` (`⬜ Bekliyor`) bir dosyayı/tabloyu/endpoint'i `[NEW]` veya `[MODIFY]` yaparken, yeni eklenen `Plan B` aynı hedefi `[NEW]` (çift oluşturma) veya `[DELETE]` yapıyor.
>    - 🟠 **`SHARED_SURFACE_OVERWRITE`:** Bekleyen iki plan aynı dosyayı (`src/...`), aynı API uç noktasını (`POST /api/v1/...`), aynı UI rotasını veya aynı DB tablosunu değiştiriyor. Sırayla geliştirilirken `Plan B`'nin `Plan 1`'i ezmemesi için **"Sıralı Birleştirme (Merge Order) Uyarısı"** üretir.
>    - 🟡 **`SEQUENTIAL_DEPENDENCY_ORDER` (Sıra Bağımlılığı):** Yeni plan, henüz kodlanmamış ama kuyrukta bekleyen `Plan A`'nın `[NEW]` olarak oluşturacağı bir dosyayı `[MODIFY]` ediyor -> *"Uyarı: Bu plan, henüz geliştirilmemiş `Plan A`'ya bağımlıdır; geliştirme sırasında önce `Plan A` tamamlanmalıdır."*
>    - 🟡 **`BACKLOG_SEMANTIC_DUPLICATE`:** `HANDOFF.md` §3 veya `KANBAN.md` (`Bekliyor`/`Yapılıyor`) içinde farklı ID taşısa bile aynı işi/yüzeyi hedefleyen bekleyen kart var.
>
> **2-Modlu Onay Seçenekleri (Planı Nasıl İlerletelim?):**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan` / `"planı mühürle, kodlama yapma"`):** Planı `docs/plans/` altına arşivler, `HANDOFF.md` §3 Gelecek Fazlar (`⬜ Bekliyor`) ve `KANBAN.md` `Bekliyor` sütununa dağıtır; **kod yazmadan durur**.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onayla ve başla"`):** Faz 0 mühürlemesini yapıp hemen Faz 1 (TDD Kırmızı Test) ile `plan_conflict_guard.py` ve kural/kapı entegrasyonlarını geliştirmeye başlar.

## 4. Open Questions (Açık Sorular)
1. **Bloklama Davranışı Tercihi:** `/seal-plan` (`archive_plan.py`) çalıştırıldığında `🔴 CRITICAL` (Canlı kodu sadeleştirerek ezme veya bekleyen başka bir planla aynı dosyayı/endpoint'i doğrudan ezme) tespit edilirse:
   - **Varsayılan Öneri (Hibrit Güvenli Mod):** `archive_plan.py` varsayılan olarak kritik ezmede `exit 1` ile durup kullanıcıyı uyarsın (kullanıcı bilerek devam etmek isterse `--allow-conflicts` bayrağıyla mühürlesin ve planın içine `## ⚠️ Ön-Mühürleme Çakışma & Sıralı İcra Notları` tablosunu otomatik gömsün). Bu davranış uygun mudur?

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-PLAN-005` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3 + `KANBAN.md`) | `S2-20` · `plan_conflict_guard.py` çekirdek parmak izi, canlı kod (`EXACT`/`ENRICHED`/`SIMPLIFIED`) ve sıralı plan ezme (`CLOBBER`) motoru |
| `GSW-PLAN-006` | `Bekliyor` | `Bekliyor` (`HANDOFF.md` §3 + `KANBAN.md`) | `S2-20` · `archive_plan.py` (`/seal-plan`), `check_handoff.py` (`W4`) ve `check_sprint_board.py` (`W5`) ön-mühürleme çakışma kapısı entegrasyonu |
| `GSW-PLAN-007` | `Bekliyor` | `Bekliyor` (`HANDOFF.md` §3 + `KANBAN.md`) | `S2-20` · `.agent/rules/development-workflow.md`, `handoff-session-continuity.md`, `sprint-delivery-workflow.md`, `PLAN.template.md` ve regresyon test paketi (`tests/test_plan_conflict_guard.py`) |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- **Etkilenen Kardeş Uygulama, Yol & Topoloji:** `'Tek Repo / Kardeş Uygulama Etkisi Yok'` (`skillSetWorks` küresel kural ve araç deposudur; tamamlandığında `delivery.py` ile 4 aktif hedef projeye dağıtılır).
- **Kardeş `HANDOFF.md` + Süreç Dosyalarına Yazılacak Görevler & Sözleşme Özeti:** `Yok (Dağıtım hedefi)`.
- **Yürütme Sahipliği Sorusu (Farklı Dizinde Zorunlu):** `Tek repo olduğu için kapsam dışı.`

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Full-Stack Vertical Slice)

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | Kapsam dışı (Statik/dinamik Markdown plan, KANBAN, HANDOFF ve kaynak kod AST/yüzey okuyucu) | `Kapsam dışı / Dosya Sistemi` |
| **2. Backend / View / RPC** | Plan Parmak İzi Çıkarıcı (`extract_plan_footprint`), Canlı Kod & Bitmiş İş Kıyaslayıcı (`compare_with_live_code_and_done`), Sıralı Bekleyen Planlar & Kanban Ezme Dedektörü (`detect_queued_plan_conflicts`) | `.agent/skills/musgoku/scripts/plan_conflict_guard.py` |
| **3. İstemci API Entegrasyonu** | `archive_plan.py` (`--check-conflicts`, `--allow-conflicts`), `check_handoff.py` (`W4` bekleyen planlar arası yüzey ezmesi) ve `check_sprint_board.py` (`W5` kartlar arası yüzey/hedef çakışması) CLI entegrasyonu | `.agent/skills/musgoku/scripts/archive_plan.py`, `check_handoff.py`, `check_sprint_board.py` |
| **4. Arayüz / UX & Eylemler** | FAA AC 121-24C uyumlu konsol çakışma matrisi + arşivlenen plan içine otomatik gömülen `## ⚠️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Analizi` Markdown raporu + `.agent/skills-catalog.html` güncellemesi | `PLAN.template.md`, `.agent/skills-catalog.html` |
| **5. Döngü Kapanışı (Admin)** | `tests/test_plan_conflict_guard.py` birim testleri + `tests/run_all.py` + `delivery.py` ile 4 hedef projeye dağıtım döngüsü | `tests/test_plan_conflict_guard.py`, `tests/run_all.py` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi (Theme & Component Skeleton Contract)

| İskelet Boyutu | Seçilen Şablon / Kaset / Token | Kaynak / CLI Komutu |
|---|---|---|
| **1. Yaşayan Yüzey & 16 Kilitli Tema + 88 İlham Paleti** | `'Salt Backend / CLI & Kural Motoru — UI Kapsam Dışı'` (Katalog derlemesinde mevcut Obsidian Command Deck korunur) | `python scripts/generate_skills_catalog.py` |
| **2. 55+ Doğrulanmış Bileşen Teması** | `'Salt Backend / UI Kapsam Dışı'` | `Kapsam Dışı` |
| **3. 18 Doğrulanmış Dashboard Şablonu** | `'Dashboard Kapsam Dışı'` | `Kapsam Dışı` |
| **4. Zero-CLS Skeleton Kaseti & 4 UX Durumu** | `'Salt Backend / CLI Rapor Çıktısı'` | `Kapsam Dışı` |
| **5. Görsel Varlık & Karşılama Turu** | `'Gerekmiyor'` | `Kapsam Dışı` |

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 & Sprint Açılışı — Koda Dokunmadan Önce Zorunlu)
1. **[Adım 1 - Planı `docs/plans/` Altına Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan "C:/Users/Mustafa/.gemini/antigravity-cli/brain/cf4c9670-8f87-47f1-80ab-8ca9794cec55/council_plan_pre_seal_conflict_guard.md" --slug pre-seal-conflict-guard` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_pre_seal_conflict_guard_<YYYYMMDD_HHMMSS>.md`
2. **[Adım 2 - `HANDOFF.md` §3 Canlı Panosuna İşle]:** `GSW-PLAN-005..007` görevlerini ve arşivlenen plan referansını `HANDOFF.md` §3 panosuna işle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0 hata, 0 uyarı` döner.
3. **[Adım 3 - Sprint & KANBAN Kartını Aç]:** `SPRINT_PLAN.md`, `KANBAN.md` ve `RELEASE_PLAN.md` içine `S2-20` kartını ve `specs/S2-20.feature` Gherkin dosyasını ekle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_sprint_board.py` `[OK]` döner.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - Kırmızı Test Paketi Yaz & Koştur]:** `tests/test_plan_conflict_guard.py` içinde 6 temel senaryoyu (`ALREADY_DONE_EXACT`, `ENRICHED_SUPERSET`, `SIMPLIFIED_SUBSET_REGRESSION`, `QUEUED_PLAN_CLOBBER`, `SEQUENTIAL_ORDER_DEPENDENCY`, `BACKLOG_SEMANTIC_DUPLICATE`) test eden birim testlerini yaz ve `python -m unittest tests/test_plan_conflict_guard.py` komutunu çalıştır -> **Beklenen Çıktı:** `ModuleNotFoundError: No module named 'plan_conflict_guard'` ile testin **KIRMIZI (FAIL)** olduğu kanıtlanır.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
1. **[Adım 1 - `plan_conflict_guard.py` Çekirdek Motorunu Yaz]:** `.agent/skills/musgoku/scripts/plan_conflict_guard.py` dosyasını oluştur; plan parmak izi çıkarıcı (`extract_plan_footprint`), canlı kod/tamamlanan iş kıyaslayıcı (`analyze_live_and_done_overlap`) ve bekleyen planlar/kanban ezme dedektörünü (`analyze_queued_plan_clobber`) kodla -> **Beklenen Çıktı:** `python -m unittest tests/test_plan_conflict_guard.py` çalıştırıldığında tüm testler **YEŞİL (PASS)** döner.

### 🧩 Faz 3: `/seal-plan` (`archive_plan.py`), `check_handoff.py`, `check_sprint_board.py` ve Kural Entegrasyonu
1. **[Adım 1 - `archive_plan.py` Ön-Mühürleme Kalkanını Bağla]:** `archive_plan.py` içine `plan_conflict_guard` entegrasyonunu, `--allow-conflicts` ve `--skip-conflict-check` bayraklarını ekle; mühürlenen planlarda çakışma/zenginleştirme/sıra bağımlılığı varsa raporu konsola ve plan sonuna işle -> **Beklenen Çıktı:** Çakışmalı plan mühürlenirken erken uyarı tablosu üretilir ve testler yeşil geçer.
2. **[Adım 2 - `check_handoff.py` (`W4`) ve `check_sprint_board.py` (`W5`) Uyarılarını Bağla]:** Bekleyen planlar ve açık Kanban kartları arasındaki dosya/endpoint ezme risklerini `W4` ve `W5` uyarı koduyla raporla -> **Beklenen Çıktı:** `check_handoff.py` ve `check_sprint_board.py` çakışmasız repoda `0 hata, 0 uyarı`, sentetik çakışmalı repoda `W4`/`W5` döner.
3. **[Adım 3 - Kuralları ve Şablonu Güncelle]:** `.agent/rules/development-workflow.md` (Adım 2.1 & 2.2 Faz 0), `handoff-session-continuity.md`, `sprint-delivery-workflow.md` ve `.agent/templates/PLAN.template.md` dosyalarına **Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Kalkanı** kurallarını işle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/rules_gates.py --strict` ve `check_aviation_docs.py` `[OK]` döner.

### 🧹 Faz 4: Refactor, Kapılar & Kapanış
1. **[Adım 1 - Birleşik Kapılar ve Regresyon Koşumu]:** `python tests/run_all.py` ve `python .agent/skills/musgoku/scripts/run_all_gates.py` çalıştır, `docs/KULLANICI_TEST_REHBERI.md` güncelle ve `KANBAN.md` `S2-20` kartını `Yapıldı`'ya taşı -> **Beklenen Çıktı:** `32/32` test paketi ve tüm kapılar `[OK]` döner.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### 1. Çekirdek Çakışma, Tekrar ve Ezme Tespit Motoru (`.agent/skills/musgoku/scripts/`)
#### [NEW] `.agent/skills/musgoku/scripts/plan_conflict_guard.py`
- **`PlanFootprint` Veri Modeli:**
  - `task_ids`: Plandaki `[DOM]-[TIP]-[NO]` ve `S<n>-<nn>` kimlikleri.
  - `file_actions`: `{"NEW": set(), "MODIFY": set(), "DELETE": set()}` (`#### [NEW/MODIFY/DELETE] <path>` ve tablo hücrelerinden).
  - `endpoints`: `(METHOD, normalized_path)` çiftleri (`POST /api/v1/...`).
  - `routes`: Frontend sayfa rotaları (`/dashboard/...`).
  - `db_objects`: Tablo/migration/kolon hedefleri (`CREATE TABLE`, `ALTER TABLE`, `supabase/migrations/...`, `@Entity`).
  - `layer_richness`: 5 katmanlı dilim doluluk oranı + güvenlik/RLS/Turnstile/Skeleton/Test sinyalleri (`score: 1..10`, `signals: set[str]`).
  - `title_tokens`: Stop-word arındırılmış normalize anahtar kelime kümesi (Jaccard benzerliği için).
- **`compare_against_live_and_done(footprint, project_root)`:**
  - Canlı kodda hedef dosya/endpoint/tablo var mı ve `HANDOFF.md` §1 / `KANBAN.md` `Yapıldı` içinde tamamlanmış mı kontrol eder:
    * **`ALREADY_DONE_EXACT`:** Dosya/endpoint canlıda var, plan `[NEW]` diyor veya zenginlik skoru canlı koddan yüksek değil ve yeni yüzey eklemiyor.
    * **`ENRICHED_SUPERSET`:** Dosya/endpoint canlıda var ama plan yeni endpoint/kolon/güvenlik/UX halkası ekliyor (`plan_richness > live_richness` veya yeni alt yüzeyler var). Planda `[NEW]` işaretlendiyse `ACTION_MISMATCH_NEW_SHOULD_BE_MODIFY` uyarısı verir.
    * **`SIMPLIFIED_SUBSET_REGRESSION`:** Canlı kodda mevcut dosya/özellik zengin sinyallere (RLS, validation, skeleton, test, `@Version` vb.) sahipken, yeni plan aynı yüzeyi daha düşük zenginlik skoruyla tanımlıyor veya mevcut dosyayı `[NEW]` ile sıfırdan basitçe ezmeye çalışıyor (`🔴 CRITICAL`).
- **`compare_against_queued_plans_and_board(footprint, project_root)`:**
  - `HANDOFF.md` §3 (`⬜ Bekliyor`, `⏭️`), `KANBAN.md` (`Bekliyor`, `Yapılıyor`) ve bunlara bağlı `docs/plans/*.md` + `.agent/plans/*.md` dosyalarını kronolojik sırayla tarar:
    * **`DOUBLE_NEW_COLLISION` (`🔴 CRITICAL`):** Bekleyen `Plan A` ile `Yeni Plan` aynı dosyayı/tabloyu/endpoint'i `[NEW]` olarak oluşturuyor.
    * **`MODIFY_DELETE_CLOBBER` (`🔴 CRITICAL`):** Bekleyen bir plan dosyayı `[MODIFY]` ederken diğeri `[DELETE]` ediyor.
    * **`SHARED_SURFACE_OVERWRITE` (`🟠 WARNING`):** Bekleyen iki plan aynı dosyayı, endpoint'i veya DB tablosunu değiştiriyor -> **"Sıralı Geliştirme Ezme Riski: `Plan B` geliştirilirken `Plan A`'nın değişiklikleri korunmalı / birleştirilmelidir."**
    * **`SEQUENTIAL_ORDER_DEPENDENCY` (`🟡 INFO/WARNING`):** `Yeni Plan` içinde `[MODIFY] <dosya>` var, ancak `<dosya>` henüz canlı kodda yok ve bekleyen `Plan A` içinde `[NEW] <dosya>` olarak tanımlı -> **"Zorunlu Sıra Bağımlılığı: `Yeni Plan`, `Plan A`'dan SONRA geliştirilmelidir."**
    * **`BACKLOG_SEMANTIC_DUPLICATE` (`🟠 WARNING`):** `KANBAN.md` veya `HANDOFF.md` §3 içinde farklı görev ID'siyle aynı dosya/endpoint/başlık (`Jaccard >= 0.65`) zaten bekliyor.

---

### 2. Arşivleme ve Süreç Kapıları (`.agent/skills/musgoku/scripts/`)
#### [MODIFY] `.agent/skills/musgoku/scripts/archive_plan.py`
- `archive_plan()` ve CLI içerisine ön-mühürleme çakışma taraması (`run_pre_seal_conflict_check`) entegre edilir.
- `--allow-conflicts` ve `--skip-conflict-check` parametreleri eklenir.
- Tespit edilen bulgular konsola FAA AC 121-24C özet tablosu olarak basılır ve arşivlenen planın sonuna (`## 11. 🚨 Ditching` öncesine) `## ⚠️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Analizi (Pre-Seal Conflict Audit)` bölümü olarak otomatik mühürlenir.

#### [MODIFY] `.agent/skills/musgoku/scripts/check_handoff.py`
- `W4` uyarı kodu eklenir: `HANDOFF.md` §3'te bekleyen (`⬜ Bekliyor` / `⏭️`) çoklu onaylı planlar arasında birbirini ezen (`DOUBLE_NEW_COLLISION` / `MODIFY_DELETE_CLOBBER` / `SHARED_SURFACE_OVERWRITE`) hedefler varsa uyarır.

#### [MODIFY] `.agent/skills/musgoku/scripts/check_sprint_board.py`
- `W5` uyarı kodu eklenir: `KANBAN.md` (`Bekliyor` / `Yapılıyor`) kartları arasında yüksek semantik/yüzey örtüşmesi veya `Yapıldı` sütunundaki bir kartın birebir tekrarı varsa uyarır.

---

### 3. Kurallar, Şablon ve Regresyon Testleri
#### [MODIFY] `.agent/rules/development-workflow.md` & `.agent/rules/handoff-session-continuity.md` & `.agent/rules/sprint-delivery-workflow.md`
- Faz 0 (`/seal-plan` & `Proceed`) ve Sprint/Kanban kart açılışı öncesinde `plan_conflict_guard.py` çalıştırma ve `Birebir / Zenginleştirilmiş / Sadeleştirilmiş / Sıralı Plan Ezmesi` sınıflandırma kuralı eklenir.

#### [MODIFY] `.agent/templates/PLAN.template.md`
- Bölüm 5 (`Sprint, HANDOFF & KANBAN Durumu`) altına `### 5.2 🛡️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Matrisi (Pre-Seal Conflict Check)` tablosu ve Faz 0'a `plan_conflict_guard.py` doğrulama adımı eklenir.

#### [NEW] `tests/test_plan_conflict_guard.py`
- Sentetik proje dizininde canlı kod, `HANDOFF.md`, `KANBAN.md` ve sıralı `Plan 1 -> Plan 2 -> Plan 3` senaryolarını (`ALREADY_DONE_EXACT`, `ENRICHED_SUPERSET`, `SIMPLIFIED_SUBSET_REGRESSION`, `DOUBLE_NEW_COLLISION`, `SHARED_SURFACE_OVERWRITE`, `SEQUENTIAL_ORDER_DEPENDENCY`, `BACKLOG_SEMANTIC_DUPLICATE`) doğrulayan kapsamlı birim test paketi.

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
# 1. Yeni çakışma ve sıralı plan ezme kalkanı birim testleri
python -m unittest tests/test_plan_conflict_guard.py -v

# 2. Council ve iş akışı entegrasyon testleri
python -m unittest tests/test_council_workflow_integration.py -v

# 3. Tüm depo regresyon paketleri ve birleşik kalite kapıları
python tests/run_all.py
python .agent/skills/musgoku/scripts/run_all_gates.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - Tekil Plan Çakışma Taraması]:** `python .agent/skills/musgoku/scripts/plan_conflict_guard.py --root . --plan <plan-dosya-yolu>` -> **Beklenen Çıktı:** Terminalde canlı kod (`EXACT / ENRICHED / SIMPLIFIED`) ve bekleyen planlar (`CLOBBER / ORDER_DEPENDENCY`) için sıfır-lakırdılı çakışma matrisi listelenir.
2. **[Adım 2 - Bekleyen Tüm Plan Kuyruğu Taraması]:** `python .agent/skills/musgoku/scripts/plan_conflict_guard.py --root . --check-queue` -> **Beklenen Çıktı:** `docs/plans/` ve `HANDOFF.md` §3 içinde sırada bekleyen tüm planların birbirleriyle olan dosya/endpoint/tablo kesişimleri ve önerilen geliştirme sırası raporlanır.
3. **[Adım 3 - `/seal-plan` Ön-Mühürleme Koruması]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug <slug> --seal-handoff` -> **Beklenen Çıktı:** Mühürleme öncesinde çakışma kontrolü otomatik çalışır; kritik ezme varsa uyarır, temizse planı `docs/plans/` ve `HANDOFF.md` §3 içine mühürler.

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `[BLOCKED] CRITICAL plan conflict detected during archive_plan.py` | Yeni plan canlıdaki zengin bir özelliği sadeleştirerek eziyor (`SIMPLIFIED_SUBSET_REGRESSION`) veya bekleyen başka bir planla aynı dosyayı `[NEW]` olarak çakıştırıyor | Plandaki `[NEW]` etiketini `[MODIFY]` yapın veya bilinçli ezme ise `python .agent/skills/musgoku/scripts/archive_plan.py --plan <yol> --slug <slug> --seal-handoff --allow-conflicts` çalıştırın |
| `[WARN] [W4] Queued plans share mutable surface` | `HANDOFF.md` §3'te bekleyen iki ayrı plan aynı dosya veya endpoint'i değiştiriyor | `python .agent/skills/musgoku/scripts/plan_conflict_guard.py --root . --check-queue` çalıştırarak hangi planın önce kodlanacağını ve birleştirilecek satırları doğrulayın |
| `[WARN] [SEQUENTIAL_ORDER_DEPENDENCY]` | Yeni planın `[MODIFY]` ettiği dosya canlı kodda henüz yok, bekleyen önceki bir planda `[NEW]` olarak tanımlı | Geliştirmeye başlarken önce bağımlı olunan önceki planı (`Plan #1`) Faz 1'den başlatın |
