# Kardeş Uygulama (Cross-Repo Sibling) Planlama, HANDOFF.md Senkronizasyonu ve Yürütme Sahipliği Karar Kapısı Uygulama Planı
<!--
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2
-->

> **Hedef Dal / Sürüm:** `main / skillSetWorks v1.37.0` · **Tarih:** `2026-11-17`  
> **Görevlendirilen Skill'ler:** `musgoku`, `tdd`, `council`, `feature-architect`, `spec-reconciler`, `doc-coauthoring`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`, `search`), `sequential-thinking`  
> **İlgili Görev Kimlikleri:** `GSW-XREPO-001`, `GSW-XREPO-002`, `GSW-XREPO-003`  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. Goal Description (Mevcut Durum Tespiti, Amaç & Kapsam)

### Mevcut Durum Analizi ("Bu yapı bizde var mı?")
Depoda yapılan inceleme sonucunda **kısmi** bir yapı bulunduğu, ancak talep edilen iki zorunlu mekanizmanın **eksik olduğu** tespit edilmiştir:

1. **Var Olan (Yalnızca Okuma / Keşif Katmanı):**
   - `feature-architect` (`fa_engine/discovery.py`) ve `spec-reconciler` (`reconcile_scanner.py`) araçları kardeş uygulamayı (sibling peer repo) `.code-workspace`, `PROJECT_BRIEF.md`, `docker-compose`, üst dizin ve API yolu örtüşmesi üzerinden `CONFIRMED` olarak keşfedebiliyor.
   - `archive_plan.py` (`musgoku`) ve `development-workflow.md` Adım 2.2 Faz 0, onaylanan planı **yalnızca mevcut çalışılan reponun** `docs/plans/` ve `HANDOFF.md` §3 canlı panosuna mühürlüyor.
2. **Eksik Olan (İstenen 2 Zorunlu Kapı):**
   - **Eksik 1 — Kardeş Uygulamanın `HANDOFF.md` Dosyasına Yazma:** Mevcut kurallar (`AGENTS.md`, `handoff-session-continuity.md`, `development-workflow.md`, `sprint-delivery-workflow.md`) yalnızca mevcut repo kökündeki `HANDOFF.md`'yi kapsıyor. Plan (`/plan`, `/feature-architect`, `/spec-reconcile`, `/council` vb.) sonucunda kardeş uygulamada da geliştirme çıkarsa, kardeş uygulamanın `HANDOFF.md` dosyasına kaynak plan referansı, kontrat özeti ve `[DOM]-[TIP]-[NO]` görevlerini yazan kural ve deterministik script bulunmuyor.
   - **Eksik 2 — Yürütme Sahipliği Karar Kapısı (Execution Ownership Gate):** Kardeş uygulamada geliştirme gerektiğinde kodlamaya geçmeden önce kullanıcıya *"Geliştirmeyi ben mi yapayım, yoksa kardeş uygulamadaki AI (Antigravity/Cursor/Claude) ajanı ile mi devam etmek istersiniz?"* sorusunu zorunlu kılan hiçbir kural, şablon veya onay kapısı yok.

### Amaç
Herhangi bir projede `/plan` veya diğer planlama/denetim yapıları (`/feature-architect`, `/spec-reconcile`, `/council`, Adım 2.1 planlaması) sonucunda **kardeş uygulamada da geliştirme yapılması gerekiyorsa**:
1. Kardeş uygulamanın `HANDOFF.md` dosyasına (yoksa `HANDOFF.template.md` omurgasıyla oluşturarak) kaynak plan referansı, API/DTO sözleşme özeti ve deterministik görev satırlarının eksiksiz yazılmasını sağlamak,
2. Kardeş uygulamada tek satır kod değiştirmeden önce kullanıcıya **Yürütme Sahipliği Karar Kapısını** (*"Bu oturumdaki ajan mı geliştirsin, yoksa kardeş uygulamadaki AI ajanı ile mi devam edilsin?"*) zorunlu olarak sordurmak ve seçime göre ya kardeş repoda devam etmek ya da kardeş repoda kod yazmadan devri tamamlamak.

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: Kardeş Uygulama (Cross-Repo) Plan Devri ve Yürütme Sahipliği Kapısı
  Scenario: Plan sonucunda kardeş uygulamada geliştirme gerektiğinde HANDOFF.md mühürlenir ve sahiplik sorulur
    Given Bir projede "/plan", "/feature-architect", "/spec-reconcile" veya "/council" ile plan hazırlanmıştır
    And Planın uygulanması kardeş uygulamada (peer repo) da kod veya şema geliştirmesi gerektirmektedir
    When Plan kullanıcı tarafından onaylanır ("Proceed" / "Onayla")
    Then Önce "sync_sibling_handoff.py" ile kardeş uygulamanın "HANDOFF.md" §3 canlı panosuna kaynak plan referansı, sözleşme özeti ve görev satırları yazılır
    And Kardeş uygulamada tek satır kod yazılmadan önce kullanıcıya "Geliştirmeyi ben mi yapayım yoksa kardeş uygulamadaki AI agent ile mi devam etmek istersiniz?" sorusu yöneltilir
    And Kullanıcı "kardeş uygulamadaki AI agent" seçerse mevcut ajan kardeş reponun koduna dokunmaz ve devri tamamlar
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Sadece Kural Metni)** | Yalnızca `.agent/rules/*.md` ve `PLAN.template.md` içine metin talimatı eklemek; yeni script yazmamak | Hızlı değişiklik, ekstra Python dosyası yok | `TUTUM` sınıfında kalır; ajan kardeş `HANDOFF.md`'yi elle düzenlerken format/tablo bozabilir, tekrarlı satır ekleyebilir, yer tutucu bırakabilir | `1.4` |
| **Option B (Mevcut Kurallara Entegrasyon + Deterministik CLI Köprüsü — ÖNERİLEN)** | Mevcut anayasal kurallara (`AGENTS.md`, `handoff-session-continuity.md`, `development-workflow.md`, `sprint-delivery-workflow.md`) ve ilgili skill'lere Cross-Repo Protokolü eklemek + TDD ile `sync_sibling_handoff.py` aracını yazmak | Mevcut `len(rules) == 22` kural sayısı bozulmaz; kardeş `HANDOFF.md` güncellemesi idempotent, şablon-uyumlu ve `check_handoff.py` ile doğrulanabilir olur | Yeni Python modülü + birim test bakımı gerekir | `2.8` |
| **Option C (Yeni 23. Kural Dosyası Açma)** | `cross-repo-handoff.md` diye ayrı bir kural dosyası oluşturup `rules_gates.py` kapsamına almak | Konular ayrık dosyada durur | `tests/test_rule_gates.py` L61 `len(rules) == 22` sabit kontrolünü etkiler; `handoff-session-continuity.md` ve `development-workflow.md` zaten bu alanın tek sahipleri olduğu için kural parçalanması yaratır | `1.8` |

- **Seçilen Yol & Gerekçe:** **Option B** seçilmiştir. Yeni kural dosyası açarak sorumluluğu bölmek yerine, zaten oturum devri (`handoff-session-continuity.md`) ve planlama (`development-workflow.md`, `sprint-delivery-workflow.md`, `PLAN.template.md`) kurallarının tek sahipleri olan dosyalara kuralı mühürlemek ve `archive_plan.py` yanına `sync_sibling_handoff.py` deterministik aracını eklemek en temiz, sade ve test edilebilir mimaridir.

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)

> [!IMPORTANT]
> **1. Çalışma Alanı Dışı Yazma Yetkisi Ayrımı (`HANDOFF.md` vs Kaynak Kod):**
> Global tercihlerde *"aktif çalışma alanı dışında silme ve değiştirme yapma, yapmak zorundaysan onay iste"* ilkesi bulunur. Önerilen akışta:
> - Plan onaylandığında (`Proceed` / `onay`), kardeş uygulamanın **yalnızca `HANDOFF.md`** dosyasına (ve istenirse `docs/plans/cross_repo_plan_*.md` referans kopyasına) yazma işlemi otomatik Faz 0 mühürlemesi olarak tanımlanacaktır.
> - Kardeş uygulamanın **kaynak koduna** dokunmadan önce ise 2. gereksinim olan **Yürütme Sahipliği Karar Kapısı** kullanıcıya mutlaka sorulacaktır (*"Ben mi yapayım, kardeş uygulamadaki AI agent ile mi devam edilsin?"*).

> [!NOTE]
> **Kullanıcı Kararlarıyla Kilitlenen Noktalar:**
> 1. **Terim:** Kardeş uygulamadaki ajan ifadesi **AI Agent** olarak standartlaştırılmıştır.
> 2. **Referans Formatı:** Kardeş `HANDOFF.md` içine plan dosyası kopyalanmaz; **`<kaynak-proje> projesindeki <plan-dosya-yolu> plan dosyası referansına göre`** formatında açık referans + görev/sözleşme özeti yazılır.
> 3. **Dağıtım Kapsamı:** `skillSetWorks` üzerinde tüm testler ve kapılar geçildikten sonra `python delivery.py --keep 1` ve `python delivery.py --verify` ile aktif hedef projelere (`ocai`, `FEProjectv1`, `bookmarkManagerProject`, `kalansure`) dağıtım yapılacaktır.

---

## 4. Open Questions (Açık Sorular)
- Tüm açık sorular kullanıcı yanıtlarıyla çözümlenmiştir (`AI Agent`, kaynak plan referansı formatı ve `delivery.py` dağıtımı onaylandı). Plan icra onayına hazırdır.

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)

| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / Modül |
|---|---|---|---|
| `GSW-XREPO-001` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3) | `.agent/skills/musgoku/scripts/sync_sibling_handoff.py` + TDD testleri (`tests/test_sync_sibling_handoff.py`) |
| `GSW-XREPO-002` | `Bekliyor` | `Bekliyor` | Anayasal Kurallar & Şablonlar (`AGENTS.md`, `handoff-session-continuity.md`, `development-workflow.md`, `sprint-delivery-workflow.md`, `PLAN.template.md`, `skill-trigger-routing.md`) |
| `GSW-XREPO-003` | `Bekliyor` | `Bekliyor` | Planlama Skill'leri (`feature-architect`, `spec-reconciler`, `council`, `deployment-architect`) & Katalog (`generate_skills_catalog.py` → `skills-catalog.html`) + `tests/run_all.py` |

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi & Mimari Akış

Bu depo (`skillSetWorks`) uygulama kodu değil kural, CLI script ve şablon deposudur. Bu nedenle 5 katmanlı mimari CLI/Skill ekosistemine uyarlanmıştır:

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Şablon** | `PLAN.template.md` içine `Kardeş Uygulama Etkisi & Yürütme Sahipliği` bölümü eklenmesi | `.agent/templates/PLAN.template.md` |
| **2. Çekirdek Motor (CLI)** | `sync_sibling_handoff.py`: Sibling repo doğrulama, `HANDOFF.md` yoksa `HANDOFF.template.md`'den güvenli başlatma, §3 canlı panosuna idempotent görev + kaynak plan/kontrat özeti yazma, `check_handoff.py` ile doğrulama | `.agent/skills/musgoku/scripts/sync_sibling_handoff.py` |
| **3. Kural & Orkestrasyon** | Faz 0 (Onay Sonrası Mühürleme) akışına `Cross-Repo Handoff Bridge` ve kodlama öncesi zorunlu `Yürütme Sahipliği Karar Kapısı` eklenmesi | `.agent/AGENTS.md`, `.agent/rules/handoff-session-continuity.md`, `development-workflow.md`, `sprint-delivery-workflow.md`, `skill-trigger-routing.md` |
| **4. Planlama Skill Entegrasyonu** | `/feature-architect`, `/spec-reconcile`, `/council`, `/deploy-plan` çıktılarının kardeş uygulama etki kontrolü ve 2 seçenekli sahiplik sorusunu içermesi | `.agent/skills/feature-architect/SKILL.md`, `references/report-template.md`, `spec-reconciler/SKILL.md`, `council/SKILL.md`, `deployment-architect/SKILL.md` |
| **5. Katalog & Doğrulama** | `skills-catalog.html` yeniden derlenmesi, `tests/run_all.py` ve tüm doğrulama kapılarının geçirilmesi | `scripts/generate_skills_catalog.py`, `.agent/skills-catalog.html`, `tests/test_sync_sibling_handoff.py`, `tests/run_all.py` |

### Karar Akışı (Proceed Sonrası Cross-Repo Akışı)
```ascii
[/plan, /feature-architect, /spec-reconcile, /council Onayı]
                          │
                          ▼
     [Kardeş Uygulamada Geliştirme Var mı?]
         ├── HAYIR ──▶ Standart Tek-Repo Faz 0 (archive_plan.py + aktif HANDOFF.md)
         └── EVET  ──▶ Faz 0.A: Aktif repo archive_plan.py + HANDOFF.md §3 mühürle
                          │
                          ▼
                       Faz 0.B: sync_sibling_handoff.py ile KARDEŞ REPO HANDOFF.md
                       içine "<X> projesindeki <Y> plan dosyası referansına göre"
                       ibaresi, sözleşme ve görevleri yaz + check_handoff.py doğrula
                          │
                          ▼
                       🛑 YÜRÜTME SAHİPLİĞİ KARAR KAPISI (DUR VE SOR):
                       "Geliştirmeyi ben mi yapayım yoksa kardeş uygulamadaki
                        AI agent ile mi devam etmek istersiniz?"
                          ├── Seçenek 1 (Mevcut Ajan) ──▶ Kardeş repoda TDD ile kodla
                          └── Seçenek 2 (Kardeş AI Agent) ──▶ Kardeş koda DOKUNMA;
                                                              devri raporla & dur
```

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi
- `Salt CLI / Kural / Markdown Şablonu — UI Kapsam Dışı` (Yalnız `generate_skills_catalog.py` mevcut Obsidian Command Deck yapısında metin/protokol güncellemesi alır; yeni UI bileşeni eklenmez.)

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları

### 📌 Faz 0: Onay Sonrası Mühürleme
1. Plan onaylandığında bu plan `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug cross-repo-sibling-handoff` ile `docs/plans/` altına arşivlenir.
2. `HANDOFF.md` §3 canlı görev panosuna `GSW-XREPO-001..003` maddeleri işlenir.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
- **Test Dosyası:** `tests/test_sync_sibling_handoff.py`
- **Test Edilen Dikiş Noktaları (`sync_sibling_handoff` public API & CLI):**
  1. Geçersiz/var olmayan veya aktif repoyla aynı (`self_root == sibling_root`) kardeş yol verilince `ValueError` / `exit 1` döndürmesi.
  2. Kardeş repoda `HANDOFF.md` yoksa `.agent/templates/HANDOFF.template.md` üzerinden temiz (sıfır placeholder) `HANDOFF.md` oluşturup `check_handoff.validate_handoff(sibling_root, ignore_git_diff=True)` kapısından `0` hata ile geçmesi.
  3. Kardeş repoda mevcut `HANDOFF.md` varsa mevcut tuzakları/kararları ezmeden `§3` canlı görev panosuna `<kaynak-proje> projesindeki <plan-yolu> plan dosyası referansına göre` ibaresini, sözleşme özetini ve görev satırlarını eklemesi.
  4. Aynı görev ID'si (`BE-API-001`) ile ikinci kez çalıştırıldığında idempotent davranması (mükerrer satır eklememesi).
- **Beklenen Başarısızlık Kanıtı:** `python tests/test_sync_sibling_handoff.py` ilk çalıştırmada `ModuleNotFoundError` / `FAIL` ile kırmızıya düşer.

### 🟢 Faz 2: Minimal Geçiş Kodu (`sync_sibling_handoff.py`)
- **Üretim Kod Dosyası:** `.agent/skills/musgoku/scripts/sync_sibling_handoff.py`
- **Kapsam:** Yalnızca yukarıdaki 4 dikiş noktası sözleşmesini karşılayan temiz, bağımlılıksız Python CLI ve modül fonksiyonları yazılır (`validate_sibling_root`, `sync_sibling_handoff`, CLI `--sibling-root`, `--source-root`, `--plan`, `--task-id`, `--task-title`, `--summary`).
- **Beklenen Başarı Kanıtı:** `python tests/test_sync_sibling_handoff.py` tüm testlerde `PASS` döner.

### 🧩 Faz 3: Kurallar, Şablonlar, Skill'ler ve Katalog Senkronu
- Kurallar, `PLAN.template.md`, skill dokümanları ve `generate_skills_catalog.py` güncellenir; `python scripts/generate_skills_catalog.py` ile `.agent/skills-catalog.html` yeniden üretilir.

### 🧹 Faz 4: Refactor, Birleşik Kapılar, Dağıtım & Kapanış
- `tests/run_all.py` içine `Test Sync Sibling Handoff` eklenir.
- Tüm doğrulama kapıları (`tests/run_all.py`, `run_all_gates.py`, `rules_gates.py --strict`, `test_skills_catalog.py`, `test_py_design_audit.py`) çalıştırılır.
- `python delivery.py --keep 1` ve `python delivery.py --verify` ile 4 aktif projeye (`ocai`, `FEProjectv1`, `bookmarkManagerProject`, `kalansure`) dağıtım ve byte-byte parite doğrulaması yapılır.
- `HANDOFF.md` ve `knowledge-base.md` güncellenir, commit onayı istenir.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### 1. CLI Senkronizasyon Motoru & Testleri
#### [NEW] `.agent/skills/musgoku/scripts/sync_sibling_handoff.py`
- Kardeş uygulamanın kök dizinini doğrular (`PROJECT_INDICATORS` veya `.git`, `source_root != sibling_root`).
- Kardeş uygulamada `HANDOFF.md` yoksa şablondan (placeholder'sız) oluşturur; varsa korur.
- `§3` (`Sıradaki işler` / `Aktif Sprint` tablosu) altına `<kaynak-proje> projesindeki <plan-yolu> plan dosyası referansına göre` ibaresini, kontrat özetini ve görev satırlarını idempotent yazar; sonunda kardeş repoda `check_handoff.validate_handoff` doğrular.

#### [NEW] `tests/test_sync_sibling_handoff.py`
- Geçersiz/aynı repo koruması, sıfırdan oluşturma, mevcut `HANDOFF.md` koruma, idempotency ve `check_handoff` uyumluluk testleri.

#### [MODIFY] `tests/run_all.py`
- `TEST_SCRIPTS` listesine `("Test Sync Sibling Handoff", HERE / "test_sync_sibling_handoff.py")` eklenmesi.

---

### 2. Anayasal Kurallar & Şablonlar
#### [MODIFY] `.agent/rules/handoff-session-continuity.md`
- `## Çapraz-Proje (Kardeş Uygulama) Handoff & Yürütme Sahipliği Protokolü` bölümü eklenmesi:
  1. Kardeş uygulamada geliştirme gerektiren her planda `sync_sibling_handoff.py` ile kardeş `HANDOFF.md` yazımı zorunludur.
  2. Kardeş reponun kaynak koduna dokunmadan önce kullanıcıya Yürütme Sahipliği sorulur.

#### [MODIFY] `.agent/rules/development-workflow.md`
- Adım 2.1 ve Adım 2.2 Faz 0 altına **"Kardeş Uygulama (Cross-Repo) Etkisi ve Yürütme Sahipliği Karar Kapısı"** eklenmesi.

#### [MODIFY] `.agent/rules/sprint-delivery-workflow.md`
- §2.1.1 Faz 0.2 altına kardeş repo varsa kardeş `HANDOFF.md` mühürleme ve 2 seçenekli sahiplik sorusu eklenmesi.

#### [MODIFY] `.agent/AGENTS.md`
- §0.1 veya §2 / §4 altında `/plan` ve planlama sonrası kardeş uygulama protokolünün özet referansı (mevcut yapı ve kural tablosu korunarak).

#### [MODIFY] `.agent/templates/PLAN.template.md`
- Yeni bölüm: `## 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği` (kardeş repo yolu, kardeş `HANDOFF.md`'ye işlenecek görevler/sözleşme, ve **"Geliştirmeyi ben mi yapayım yoksa kardeş uygulamadaki AI agent ile mi devam etmek istersiniz?"** karar kapısı alanı).

---

### 3. Planlama Skill'leri & Katalog
#### [MODIFY] `.agent/skills/feature-architect/SKILL.md` ve `.agent/skills/feature-architect/references/report-template.md`
- `--peer` veya otomatik keşfedilen kardeş repoda backend/frontend değişikliği çıktığında, raporun sonundaki Onay Kapısı sorularına **kardeş `HANDOFF.md` senkronu** ve **Yürütme Sahipliği sorusunun** eklenmesi.

#### [MODIFY] `.agent/skills/spec-reconciler/SKILL.md`
- Aşama 4 (Otonom İcra) içine backend/frontend ayrık kardeş repolar varsa ilgili kardeş reponun `HANDOFF.md`'sine kod işlerinin yazılması ve sahiplik sorusunun yöneltilmesi.

#### [MODIFY] `.agent/skills/council/SKILL.md` ve `.agent/skills/deployment-architect/SKILL.md`
- Çapraz-proje mimari/dağıtım planları kardeş uygulamayı etkiliyorsa aynı Cross-Repo Handoff & Ownership kapısına atıf eklenmesi.

#### [MODIFY] `.agent/rules/skill-trigger-routing.md`, `scripts/generate_skills_catalog.py`, `.agent/skills-catalog.html`
- `/plan` ansamble açıklamasının ve slash katalog metadata'sının kardeş uygulama adımıyla güncellenip `skills-catalog.html`'in yeniden derlenmesi.

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
# 1. Yeni modül birim testleri (Faz 1 Kırmızı -> Faz 2 Yeşil)
python tests/test_sync_sibling_handoff.py

# 2. Kural & tablo senkron kapısı
python .agent/skills/musgoku/scripts/rules_gates.py --strict

# 3. Birleşik kapı koşturucu
python .agent/skills/musgoku/scripts/run_all_gates.py

# 4. Tam regresyon test paketi (28/28 hedef)
python tests/run_all.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - Kardeş Handoff Testi]:** Geçici veya örnek bir kardeş repo dizininde `python .agent/skills/musgoku/scripts/sync_sibling_handoff.py --sibling-root <kardes-yol> --source-root . --plan docs/plans/<plan>.md --task-id BE-API-001 --task-title "Yeni endpoint ekle" --summary "POST /api/v1/x sözleşmesi"` komutunu çalıştırın -> **Beklenen Çıktı:** `[OK] Kardeş HANDOFF.md güncellendi` mesajı ve kardeş `HANDOFF.md` §3 içinde `BE-API-001` satırının görünmesi.
2. **[Adım 2 - Katalog Kontrolü]:** `.agent/skills-catalog.html` dosyasını tarayıcıda açıp `/plan` kartını inceleyin -> **Beklenen Çıktı:** Kardeş uygulama `HANDOFF.md` ve yürütme sahipliği adımının güncel görünmesi.
3. **[Adım 3 - Gerçek Senaryo Sınaması]:** Bir projede `/plan` çalıştırıp kardeş uygulamayı etkileyen bir geliştirme onayladığınızda -> **Beklenen Çıktı:** Ajan önce kardeş `HANDOFF.md`'yi yazar, ardından kodlamaya geçmeden *"Geliştirmeyi ben mi yapayım yoksa kardeş uygulamadaki AI agent ile mi devam etmek istersiniz?"* sorusunu sorar.

---

## 11. 🚨 Ditching & Emergency Exit (Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `test_rule_gates.py` `len(rules) == 22` hatası | Yeni `.agent/rules/*.md` dosyası açılmış | Yeni kural dosyası açma; Option B gereği mevcut kural dosyalarını güncelle |
| `test_skills_catalog.py` FRESHNESS hatası | `generate_skills_catalog.py` sonrası HTML derlenmedi | `python scripts/generate_skills_catalog.py` çalıştır |
| Kardeş `HANDOFF.md` içinde mükerrer görev satırı | Aynı `--task-id` için güncelleme yerine ekleme yapıldı | `sync_sibling_handoff.py` içindeki idempotent ID eşleştiricisini kontrol et |
| Kardeş repoda `check_handoff.py` `E4` hatası | Şablondan üretilen `HANDOFF.md`'de `[YYYY-MM-DD]` kalıntısı | Şablon oluşturucunun tarih, proje adı ve ajan yer tutucularını doldurduğunu doğrula |
