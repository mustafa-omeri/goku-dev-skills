# POST-Only Mutasyon (PUT/DELETE Yasağı) ve Soft-Delete Mimari Standartları Uygulama Planı
<!-- 
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2 · .agent/rules/aviation-documentation-standard.md (FAA AC 121-24C + /caveman)
-->

> **Hedef Dal / Sürüm:** `main / v1.43.0` · **Tarih:** `2026-11-23`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `musgoku`, `tdd`, `codebase-design`, `doc-coauthoring`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`, `get_project_state`, `search`, `get_decision`), `context7` (`Hibernate ORM`, `Prisma`, `Spring Boot`), `sequential-thinking`, `myFilesystem` (`grep`)  
> **İlgili KANBAN Kartı:** `S2-17 ([GSW]-API-001)`  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`  

---

## 1. Goal Description (Amaç & Mevcut Durum Denetimi)

### 🔍 Mevcut Skillset Denetimi: "Asla PUT, DELETE Kullanma" Kuralı Var mı?
`second-brain-vault` MCP (`DEV_BRIEF §3-A`, `api-mutasyonlarinda-post-kullanimi`, `silme-standardi-soft-delete`) üzerinde **"Mutasyonlar yalnız POST ile yapılır, PUT/DELETE yasaktır"** kararı kayıtlı olmasına rağmen, `.agent/` skillset dosyalarında **3 kritik açık ve çelişki** tespit edildi:

1. **Yumuşak/Opsiyonel İfade (`spring-boot-api.md` §1.2):** Yalnızca *"POST varsayılandır. Farklı HTTP metotları kullanılan bir API sözleşmesi varsa o sözleşme esas alınır"* yazıyor; `⛔ PUT, DELETE ve PATCH kullanımı KESİNLİKLE YASAKTIR` hükmü, RPC isimlendirme standardı, Idempotency/Optimistic Lock ve Manuel Cache Invalidation kuralları bulunmuyor.
2. **Skillset İçi Doğrudan Çelişki (`musgoku-api-data-layer.md` L185-193):** Frontend Axios servis katmanı şablonunda `httpClient.put('/api/users/${dto.id}', dto)` ve `httpClient.delete('/api/users/${id}')` örnekleri yer alıyor. Ajan bu dosyayı okuduğunda doğrudan `PUT` ve `DELETE` üretiyor.
3. **Eksik Mekanik Kapı & Soft-Delete Boşluğu (`check_api_docs.py` & `data-layer.md`):**
   - `check_api_docs.py` kapısı `@PutMapping`, `@DeleteMapping`, `@PatchMapping`, Next.js `PUT/DELETE/PATCH` ve FastAPI `.put/.delete/.patch` uçlarını ayrıştırıyor ancak yasaklı metot kullanımı için hiçbir hata/uyarı (`E4`) üretmiyor.
   - `data-layer.md` ve `db-migration-enforcement.md` içinde Soft-Delete için 4 kritik mimari pratik (**1. Fiil Tabanlı RPC Endpoint**, **2. Global Query Filters & Native SQL Alt Sorgu Kalkanı**, **3. Partial Unique Index ile Unique Çakışma Önleme**, **4. Kaskad İlişkili Veri Yönetimi: `deleted_by_parent` vs `409 Conflict`**) yer almıyor.

### 🧠 MCP Best-Practice Sentezi & Teknik Değerlendirme (`second-brain-vault` + `context7`)

| Mimari Boyut | Kullanıcının Verdiği Kural & Ödünleşim | MCP Doğrulaması (`context7` & `second-brain-vault`) + Eklenecek Kesin Standart |
|---|---|---|
| **Ödünleşim 1: REST Anlamsallığı & Idempotency** | `POST` idempotent değildir; ağ kopması ve istemci retry'larında mükerrer işlem riski oluşur. `Idempotency-Key` veya `Optimistic Locking` şarttır. | ✅ **Vault (`api-mutasyonlarinda-post-kullanimi`) + Context7 (`Hibernate @Version`):**<br>1. Kritik yazma uçlarında (ödeme, sipariş, kayıt, durum geçişi) `Idempotency-Key` HTTP başlığı veya DTO alanı zorunludur.<br>2. JPA/ORM varlıklarında `@Version private Long version;` ile Optimistic Locking zorunludur; çakışmada `409 Conflict` dönülür.<br>3. Zaten `DELETED` olan kayda tekrar silme/iptal `POST` isteği gelirse idempotent olarak aynı başarılı sonuç dönülür (`silme-standardi-soft-delete`). |
| **Ödünleşim 2: Önbellekleme (Caching) & CDN** | `PUT/DELETE` GET önbelleğini otomatik düşürür; `POST` kullanımında önbellek temizliği manuel yönetilmelidir. | ✅ **Context7 (`Spring Boot @CacheEvict`) + `TanStack Query v5`:**<br>1. Backend `POST` mutasyonlarında `@CacheEvict` / `@Caching(evict = ...)` ile hem tekil detay hem liste cache'i manuel temizlenir.<br>2. Frontend `useMutation` `onSuccess`/`onSettled` içinde `queryClient.invalidateQueries()` ve Next.js'te `revalidateTag()` / `revalidatePath()` zorunludur. |
| **Pratik 1: Fiil Tabanlı (RPC) Endpoint İsimlendirmesi** | `DELETE /orders/123` yerine `POST /api/v1/orders/123/cancel` veya `POST /api/v1/users/45/archive` alt kaynak (sub-resource) yolları kullanılmalı. | ✅ **Tam Uyum:** Tüm mutasyonlar `POST /api/v1/<resource>/{id}/<action>` (veya `/api/v1/<resource>/<action>`) formatında tanımlanır. Request body (`@Valid @RequestBody`) içinde `reason`, `actorId`, `version` gibi zengin iş/denetim bağlamı taşınır. |
| **Pratik 2: Veritabanı Seviyesinde İzolasyon (Global Query Filters)** | `WHERE is_deleted = false` unutulursa silinmiş veri sızar; ORM global filtresi aktif edilmelidir. | ✅ **Context7 (`Hibernate 6.4+` & `Prisma 6+`) + Vault (`native-sql-soft-delete-iki-tuzak`):**<br>1. **Hibernate 6.4+:** `@Where` kaldırıldığı için `@SQLRestriction("status <> 'DELETED'")` veya `@SoftDelete` kullanılır (Entity + COUNT sorgularına otomatik uygulanır).<br>2. **Prisma 6+:** `$use` middleware yerine `prisma.$extends({ query: { $allModels: { $allOperations(...) } } })` kullanılır.<br>3. ⚠️ **Kritik Ek (Vault Dersi):** ORM global filtreleri **Native SQL (`nativeQuery = true`) ve alt sorgularda (`EXISTS`, `IN`, `JOIN`) ÇALIŞMAZ!** Native SQL'de ana sorgu + tüm alt sorgularda büyük harf kanonik `AND t.status != 'DELETED'` kontrolü zorunludur. |
| **Pratik 3: Unique Kısıtlama Çakışmalarını Önleme** | Silinen `ali@ornek.com` tekrar kayıt olmak istediğinde standart `UNIQUE(email)` patlar. Partial Index veya Timestamp kullanılmalıdır. | ✅ **Context7 (`Prisma @@index where/unique`) + PostgreSQL/MySQL:**<br>1. **PostgreSQL / SQL Server / SQLite (Altın Standart — Partial Unique Index):** `CREATE UNIQUE INDEX CONCURRENTLY idx_users_active_email ON users(email) WHERE status != 'DELETED';` (veya `WHERE is_deleted = false` / `WHERE deleted_at IS NULL`). Prisma'da: `@@index([email], where: "deleted_at IS NULL", unique: true)`.<br>2. ⚠️ **Kritik SQL NULL Tuzağı Uyarısı:** Standart SQL'de `NULL != NULL` olduğu için `(email, deleted_at)` composite unique indeksinde `deleted_at IS NULL` iken aynı e-postayla **birden fazla aktif kayıt** açılabilir! Bu nedenle PostgreSQL 15+ / MySQL'de composite indeks kurulacaksa `deleted_at` yerine aktifte `0`, silinende `id` / epoch tutan `active_unique_token` veya Partial Index zorunludur. |
| **Pratik 4: Kaskad (İlişkili) Veri Yönetimi** | Ana kayıt soft-delete edildiğinde alt kayıtlar için Seçenek A (`deleted_by_parent` ile otomatik soft-delete) veya Seçenek B (`409 Conflict` ile red) seçilmelidir. | ✅ **Tam Uyum (`silme-standardi-soft-delete`):**<br>Mimari/plan aşamasında tablo bazında karar verilir:<br>- **Seçenek A (Cascade Soft-Delete):** Alt kayıtlar `deleted_by_parent = true` ile işaretlenir; ana kayıt `restore` edildiğinde yalnız `deleted_by_parent = true` olanlar geri getirilir (daha önce tekil silinmiş alt kayıtlar kirlenmez).<br>- **Seçenek B (Strict Guard):** Aktif alt kayıt varsa `409 Conflict` (`ACTIVE_CHILDREN_EXIST`) dönülür. |

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: POST-Only Mutasyon Zorunluluğu ve 4 Kritik Soft-Delete Mimari Standardı
  Scenario: Skillset kurallarında ve kod kapısında PUT/DELETE/PATCH kullanımının engellenmesi
    Given Ajan backend veya frontend API katmanında yeni bir mutasyon (create, update, status transition, soft-delete) geliştirmektedir
    When İlgili skillset referanslarını (spring-boot-api.md, data-layer.md, musgoku-api-data-layer.md) okuduğunda ve check_api_docs.py kapısını çalıştırdığında
    Then PUT, DELETE ve PATCH metotlarının kesinlikle yasak olduğunu, yalnız GET ve fiil tabanlı POST (/cancel, /archive, /update) kullanılacağını görür
    And check_api_docs.py kapısı kodda @PutMapping, @DeleteMapping, @PatchMapping veya PUT/DELETE/PATCH route handler tespit ettiğinde E4 hatası (exit 1) üretir
    And Soft-delete mimarisinde Idempotency-Key/Optimistic Lock, Manuel Cache Invalidation, Global Query Filter (+ Native SQL alt sorgu filtresi), Partial Unique Index ve Kaskad (deleted_by_parent / 409 Conflict) kuralları eksiksiz uygulanır
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (2+ Seçenek İncelemesi)

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Salt Metinsel Kural)** | Yalnızca Markdown referanslarına (`spring-boot-api.md`, `data-layer.md`) PUT/DELETE yasağını ve 4 soft-delete kuralını yazmak; kapı scriptine dokunmamak. | Hızlıdır, sıfır Python kodu değişikliği gerektirir. | `HANDOFF.md` Tuzak #21 & #22: "Kural var ama doğrulama kapısı yok". Ajan alışkanlıkla `@DeleteMapping` veya `httpClient.delete` yazdığında kapı `[OK]` döner. | 1.4 |
| **Option B (Anayasal Kural + Anti-Pattern Temizliği + `check_api_docs.py` E4 Mekanik Kapısı)** | 1) Tüm backend/frontend referanslarını günceller ve `musgoku-api-data-layer.md` içindeki `httpClient.put/delete` anti-pattern'ini temizler;<br>2) `check_api_docs.py` içine `E4 (Forbidden HTTP Method: PUT/DELETE/PATCH)` mekanik denetimini (brownfield/legacy istisna etiketi desteğiyle) ekler. | Hem kuralı hem de ölçülebilir doğrulama kapısını (`OLCULEBILIR`) kilitler; yeni yazılan hiçbir `PUT/DELETE/PATCH` uç noktası kapıdan geçemez. | Legacy projelerde mevcut `PUT/DELETE` uçları için `api-documentation-enforcement.md` içinde izinli istisna deklarasyonu (`<!-- ALLOW-HTTP-METHODS: PUT,DELETE -->` veya `--allow-legacy-methods`) desteği gerektirir. | **2.9** |

- **Seçilen Yol & Gerekçe:** **Option B** seçildi. `skillSetWorks` anayasasında (`Tuzak #21`) mekanik kapısı olmayan yasaklar ajanlar tarafından eğitim refleksiyle delinmektedir. `check_api_docs.py` içinde zaten tüm Java/Next.js/FastAPI HTTP metotları taranmaktadır; buraya `E4` kontrolü eklemek sıfır ek tarama maliyetiyle %100 deterministik koruma sağlar.
- **Birleşik Planlama Ekosistemi Bağlantısı:** Kullanıcı Mimari Direktifi → Second Brain Vault & Context7 Doğrulaması → Konsey Hakemliği (`Option B`) → Görev Kartı (`S2-17` / `[GSW]-API-001`) → TDD Dikiş Noktası (`tests/test_rule_gates.py` → `check_api_docs.py`).

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)
> [!IMPORTANT]
> 1. **Kesin `PUT / DELETE / PATCH` Yasağı ve `E4` Kapısı:** `spring-boot-api.md`, `musgoku-api-data-layer.md`, `api-documentation-enforcement.md` ve `musgoku/SKILL.md` içinde yalnızca `GET` (okuma) ve `POST` (tüm mutasyonlar ve durum geçişleri) izinli olacak; `check_api_docs.py` kapısı kodda `PUT`, `DELETE` veya `PATCH` gördüğünde `E4` hatası (`exit 1`) verecektir (dış/legacy sözleşme zorunluluğu olan projelerde `docs/APIs/` içinde açık istisna deklarasyonu varsa uyarıya düşer).
> 2. **Composite `(email, deleted_at)` NULL Tuzağı Düzeltmesi:** Standart SQL'de (PostgreSQL, MySQL) `NULL != NULL` kabul edildiği için `UNIQUE(email, deleted_at)` indeksinde `deleted_at IS NULL` olan (aktif) kayıtlar birbirini engellemez ve aynı e-posta ile birden fazla aktif kayıt açılabilir. Bu nedenle kuralda **Çözüm 1 (Partial Unique Index: `WHERE status != 'DELETED'` veya `WHERE deleted_at IS NULL`)** birincil altın standart olarak; Partial Index desteklemeyen eski MySQL sürümleri için ise **Çözüm 2 (`deleted_at` yanında aktifte `0`, silinende `id`/timestamp değerini alan `deleted_token` ile `UNIQUE(email, deleted_token)`)** doğruluk garantili desen olarak yazılacaktır.
>
> **2-Modlu Onay Seçenekleri (Planı Nasıl İlerletelim?):**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan` / `"planı mühürle, kodlama yapma"`):** Planı `docs/plans/` altına arşivler, `HANDOFF.md` §3 Gelecek Fazlar (`⬜ Bekliyor`) ve `KANBAN.md` `Bekliyor` sütununa dağıtır; **kod yazmadan durur**.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onayla ve başla"`):** Faz 0 mühürlemesini yapıp hemen Faz 1 (TDD Kırmızı Test) ile geliştirmeye başlar.

## 4. Open Questions (Açık Sorular)
Açık soru bulunmamaktadır. Onayınızla birlikte yürütmeye hazırdır.

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-API-001` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3 + `KANBAN.md`) | `S2-17` — Kesin `POST-Only` (`PUT/DELETE/PATCH` Yasağı) & `check_api_docs.py` `E4` Kapısı |
| `GSW-API-002` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3 + `KANBAN.md`) | `S2-17` — Soft-Delete 4 Kritik Mimari Pratik + 2 Ödünleşim Kuralı (`spring-boot-api.md`, `data-layer.md`, `db-migration-enforcement.md`, `musgoku-api-data-layer.md`) |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- **Etkilenen Kardeş Uygulama, Yol & Topoloji:** `Tek Repo / Kardeş Uygulama Etkisi Yok` (Bu depo küresel kural ve skill kaynağıdır; tamamlandığında `delivery.py` ile 4 hedef projeye standart olarak dağıtılır).

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Full-Stack Vertical Slice)

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | Soft-Delete DB İzolasyonu (`@SQLRestriction`, `@SoftDelete`, Prisma `$extends`, Native SQL alt sorgu kalkanı), Partial Unique Index (`WHERE status != 'DELETED'`) ve Kaskad Veri Yönetimi (`deleted_by_parent` vs `409 Conflict`) kurallarının veri katmanı anayasasına işlenmesi | `.agent/skills/musgoku/references/data-layer.md`<br>`.agent/rules/db-migration-enforcement.md` |
| **2. Backend / View / RPC** | Kesin `PUT/DELETE/PATCH` yasağı, Fiil Tabanlı RPC Endpoint isimlendirmesi (`POST /api/v1/orders/{id}/cancel`), `Idempotency-Key` + `@Version` Optimistic Locking ve `@CacheEvict` manuel önbellek temizleme standartlarının backend anayasasına eklenmesi | `.agent/skills/musgoku/references/spring-boot-api.md`<br>`.agent/rules/api-documentation-enforcement.md`<br>`.agent/skills/musgoku/SKILL.md` |
| **3. İstemci API Entegrasyonu** | Frontend Axios şablonundaki `httpClient.put` ve `httpClient.delete` anti-pattern örneklerinin `httpClient.post('/api/v1/users/${dto.id}/update', dto)` ve `httpClient.post('/api/v1/users/${id}/archive', { reason })` RPC desenine dönüştürülmesi + `Idempotency-Key` ve `invalidateQueries` zorunluluğu | `.agent/skills/musgoku/skills/musgoku-api-data-layer.md` |
| **4. Arayüz / UX & Eylemler** | `check_api_docs.py` CLI doğrulama kapısına `E4` (`PUT/DELETE/PATCH` yasaklı HTTP metodu tespiti) eklenmesi ve yetenek kataloğunun (`skills-catalog.html`) güncellenmesi | `.agent/skills/musgoku/scripts/check_api_docs.py`<br>`.agent/skills-catalog.html` |
| **5. Döngü Kapanışı (Admin)** | Regresyon testlerinin (`tests/test_rule_gates.py`), kullanıcı test rehberinin (`docs/KULLANICI_TEST_REHBERI.md`), `HANDOFF.md` ve `knowledge-base.md` kayıtlarının mühürlenmesi | `tests/test_rule_gates.py`<br>`docs/KULLANICI_TEST_REHBERI.md`<br>`HANDOFF.md` · `knowledge-base.md` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi (Theme & Component Skeleton Contract)
- `Salt Backend / Kural & CLI Kapısı (UI Kapsam Dışı)`

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 & Sprint Açılışı — Koda Dokunmadan Önce Zorunlu)
1. **[Adım 1 - Planı `docs/plans/` Altına Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan C:\Users\Mustafa\.gemini\antigravity-cli\brain\cce6add0-0194-402f-8c61-af965e9ca5dc\plan_post_only_soft_delete_architecture.md --slug post-only-soft-delete-architecture` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_post-only-soft-delete-architecture_<YYYYMMDD_HHMMSS>.md`
2. **[Adım 2 - `HANDOFF.md` §3 ve `KANBAN.md` Panosuna İşle]:** `GSW-API-001` ve `GSW-API-002` görevlerini (`S2-17`) `HANDOFF.md` §3 ve `KANBAN.md` içine işle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0 hata, 0 uyarı` döner.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - `test_rule_gates.py` İçinde `E4` Yasaklı HTTP Metodu Kırmızı Testini Yaz & Koştur]:** `tests/test_rule_gates.py` içerisindeki `test_api_docs_violations()` fonksiyonuna `@PutMapping`, `@DeleteMapping` ve Next.js `DELETE` route handler içeren bir fixture için `E4` hatası bekleyen test senaryolarını ekle ve `python tests/test_rule_gates.py` komutunu çalıştır -> **Beklenen Çıktı:** Terminalde `FAIL E4 yasakli HTTP metodu (PUT/DELETE) yakalandi` çıktısıyla testin **KIRMIZI (FAIL)** olduğu görülür.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
1. **[Adım 1 - `check_api_docs.py` İçine `E4` Yasaklı HTTP Metodu Denetimini Ekle & Test Et]:** `.agent/skills/musgoku/scripts/check_api_docs.py` içinde tespit edilen `PUT`, `DELETE`, `PATCH` uç noktaları için (dokümanda açık `ALLOW-HTTP-METHODS` istisnası yoksa) `E4` hatası üretecek minimal geçiş kodunu yaz ve `python tests/test_rule_gates.py` çalıştır -> **Beklenen Çıktı:** Terminalde `SONUC: tum testler gecti` çıktısıyla testin **YEŞİL (PASS)** olduğu görülür.

### 🧩 Faz 3: 5 Katman Tamamlama — Anayasal Kurallar, 4 Soft-Delete Pratiği & Anti-Pattern Temizliği
1. **[Adım 1 - Backend API Standardını Güncelle (`spring-boot-api.md` & `api-documentation-enforcement.md` & `musgoku/SKILL.md`)]:** `spring-boot-api.md` §1.2'yi **"Kesin GET/POST Standardı ve PUT/DELETE/PATCH Yasağı"** olarak yeniden yapılandır; **Fiil Tabanlı (RPC) Endpoint İsimlendirmesi** (`POST /api/v1/orders/{id}/cancel`), **Idempotency-Key & `@Version` Optimistic Locking**, **Manuel Cache Invalidation (`@CacheEvict`)** ve **Kaskad Silme HTTP `409 Conflict`** kurallarını kod örnekleriyle ekle -> **Beklenen Çıktı:** Dosyalarda `PUT/DELETE/PATCH` yasağı ve `E4` kapısı tam senkronize olur.
2. **[Adım 2 - Veri Katmanı ve Migration Standardını Güncelle (`data-layer.md` & `db-migration-enforcement.md`)]:** `data-layer.md` içine yeni `## 9. Soft-Delete Mimarisi ve 4 Kritik Veri Katmanı Pratiği` bölümünü ekle (1. Durum Geçişi `status = 'DELETED'` & İdempotent Silme, 2. Global Query Filters: Hibernate 6.4+ `@SQLRestriction` / `@SoftDelete`, Prisma 6+ `$extends` ve **Native SQL Alt Sorgu Kalkanı**, 3. Unique Çakışma Önleme: **Partial Unique Index** vs **`deleted_token` Composite Unique & SQL NULL Tuzağı**, 4. Kaskad Veri Yönetimi: **`deleted_by_parent` İzolasyonlu Cascade** vs **`409 Conflict`**) -> **Beklenen Çıktı:** Veri katmanı ve `db-migration-enforcement.md` kuralları eksiksiz güncellenir.
3. **[Adım 3 - Frontend Axios Anti-Pattern Temizliği (`musgoku-api-data-layer.md`)]:** `musgoku-api-data-layer.md` L185-193'teki `httpClient.put` ve `httpClient.delete` çağrılarını `httpClient.post('/api/v1/users/${dto.id}/update', dto)` ve `httpClient.post('/api/v1/users/${id}/archive', { reason })` RPC desenine çevir; `Anti-Patterns` listesine `❌ httpClient.put() / httpClient.delete() / httpClient.patch() kullanımı` maddesini ve `Idempotency-Key` + `queryClient.invalidateQueries()` zorunluluğunu ekle -> **Beklenen Çıktı:** Skillset içinde tek bir `httpClient.put` veya `httpClient.delete` örneği kalmaz.

### 🧹 Faz 4: Refactor, Kapılar & Kapanış
1. **[Adım 1 - Katalog Derleme, Birleşik Kapılar & Regresyon Testleri]:** `python scripts/generate_skills_catalog.py`, `python tests/run_all.py` ve `python .agent/skills/musgoku/scripts/run_all_gates.py` komutlarını çalıştır; `docs/KULLANICI_TEST_REHBERI.md`, `HANDOFF.md` ve `knowledge-base.md` dosyalarını güncelle -> **Beklenen Çıktı:** 30/30 test paketi ve tüm ölçülebilir kapılar `[OK]` döner.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### 1. Backend & API Kuralları (`musgoku` & `rules`)

#### [MODIFY] [.agent/skills/musgoku/references/spring-boot-api.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/references/spring-boot-api.md)
- **§1.2 HTTP metotları ve POST-Only RPC Mimarisi (Kesin Kural):**
  - ✅ **GET** — Yalnızca yan etkisiz okuma/sorgulama işlemleri.
  - ✅ **POST** — Tüm yazma, güncelleme, durum değiştirme (state transition) ve soft-delete işlemleri.
  - ⛔ **PUT, DELETE, PATCH Kesinlikle Yasaktır:** Proxy/WAF engelleri, CORS preflight maliyeti ve soft-delete durum geçişi anlamsallığı nedeniyle hiçbir ajan `@PutMapping`, `@DeleteMapping`, `@PatchMapping` (veya Next.js/FastAPI eşdeğerlerini) **ASLA kullanamaz** (`check_api_docs.py` `E4` kapısı ile bloklanır).
  - **1. Fiil Tabanlı (RPC / Sub-Resource) Endpoint İsimlendirmesi:**
    - Silme/Arşivleme/İptal: `POST /api/v1/orders/{id}/cancel`, `POST /api/v1/users/{id}/archive`, `POST /api/v1/categories/{id}/delete` (Request body içinde `reason`, `version`, `confirmationCode` taşınır).
    - Güncelleme/Durum Geçişi: `POST /api/v1/users/{id}/update`, `POST /api/v1/companies/assign-company`, `POST /api/v1/orders/{id}/approve`.
  - **2. POST Ödünleşimi #1 — Idempotency & Optimistic Locking (`@Version`):**
    - Kritik mutasyonlarda `Idempotency-Key` header/alan kontrolü ve Entity üzerinde `@Version private Long version;` ile Optimistic Locking zorunludur. Eşzamanlı güncelleme veya versiyon uyuşmazlığında `409 Conflict` dönülür.
    - Zaten `DELETED` / `CANCELLED` olan kayda tekrar aynı istek gelirse sistem hata fırlatmaz, idempotent olarak `200 OK` döner.
  - **3. POST Ödünleşimi #2 — Manuel Önbellek Temizliği (`@CacheEvict`):**
    - Standart HTTP ara katmanları `POST` isteğinde `GET` önbelleğini otomatik silmediği için, mutasyon servis metotlarında `@CacheEvict` / `@Caching(evict = ...)` ile hem detay hem liste önbellekleri açıkça geçersiz kılınır.
  - **§3.4 Durum → HTTP Eşlemesi:** `409 Conflict` (Optimistic lock çakışması, aktif alt kayıt varken silme engeli `ACTIVE_CHILDREN_EXIST` veya mükerrer kısıt) tabloya eklenir.

#### [MODIFY] [.agent/skills/musgoku/references/data-layer.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/references/data-layer.md)
- **§9 Soft-Delete Mimarisi ve 4 Kritik Veri Katmanı Pratiği (Yeni Bölüm):**
  1. **Varsayılan Soft-Delete Anayasası (`status = 'DELETED'`):** Fiziksel `DELETE FROM` yasaktır (mimari/plan aşamasında kullanıcı tarafından açıkça hard-delete kararlaştırılan geçici/log tabloları hariç).
  2. **Veritabanı Seviyesinde İzolasyon (Global Query Filters) & Native SQL Alt Sorgu Kalkanı:**
     - *Hibernate 6.4+:* `@SQLRestriction("status <> 'DELETED'")` veya `@SoftDelete` anotasyonu.
     - *Prisma 6+:* `prisma.$extends` (`$allModels.$allOperations`) query extension.
     - *⚠️ Native SQL & Alt Sorgu Kalkanı:* Global ORM filtreleri `nativeQuery = true` sorgularda ve alt sorgularda (`EXISTS`, `IN`, `JOIN`) devreye girmez! Native SQL yazıldığında hem ana sorguda hem tüm alt sorgularda `AND t.status != 'DELETED'` (büyük harf kanonik enum değeri) zorunludur.
  3. **Unique (Benzersiz) Kısıtlama Çakışmalarını Önleme:**
     - *Çözüm 1 (Partial Unique Index — PostgreSQL / SQL Server / SQLite / Prisma `@@index`):*
       ```sql
       CREATE UNIQUE INDEX CONCURRENTLY idx_users_active_email
       ON users(email)
       WHERE status != 'DELETED';
       ```
     - *Çözüm 2 (Partial Index Olmayan Motorlar — MySQL vb. & SQL NULL Tuzağı Uyarısı):* Standart SQL'de `NULL != NULL` olduğu için `UNIQUE(email, deleted_at)` aktif kayıtları (`deleted_at IS NULL`) koruyamaz! Bunun yerine aktif kayıtta `0`, silinen kayıtta `id` (veya epoch) değerini alan `deleted_token BIGINT NOT NULL DEFAULT 0` kolonu ile `UNIQUE(email, deleted_token)` kullanılır.
  4. **Kaskad (İlişkili) Veri Yönetimi (`deleted_by_parent` vs `409 Conflict`):**
     - *Seçenek A (Otomatik Kaskad Soft-Delete):* Alt kayıtlar da soft-delete yapılır ve `deleted_by_parent = true` atanır; ana kayıt restore edildiğinde yalnız `deleted_by_parent = true` olan alt kayıtlar geri yüklenir.
     - *Seçenek B (Aktif Alt Kayıt Engeli):* Altında aktif kayıt (`status = 'ACTIVE'`) varsa silme işlemi `409 Conflict` (`ACTIVE_CHILDREN_EXIST`) ile reddedilir.

#### [MODIFY] [.agent/skills/musgoku/skills/musgoku-api-data-layer.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/skills/musgoku-api-data-layer.md)
- L185-193 arasındaki `httpClient.put` ve `httpClient.delete` metotları kaldırılarak:
  ```tsx
  updateUser: async (dto: UpdateUserDto): Promise<User> => {
    const { data } = await httpClient.post(`/api/v1/users/${dto.id}/update`, dto);
    return data;
  },

  archiveUser: async (id: string, payload: ArchiveUserDto): Promise<void> => {
    await httpClient.post(`/api/v1/users/${id}/archive`, payload);
  },
  ```
  olarak güncellenir.
- **POST-Only Mutasyon, Manuel Cache Invalidation & Idempotency Kuralları** bölümü ve `Anti-Patterns` altına `❌ httpClient.put() / httpClient.delete() / httpClient.patch() kullanımı` eklenir.

#### [MODIFY] [.agent/rules/api-documentation-enforcement.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/api-documentation-enforcement.md)
- §4 Zorunlu İçerik ve §10 Yapılacak/Yapılmayacak bölümlerine:
  - Yalnızca `GET` ve fiil tabanlı `POST` (`/cancel`, `/archive`, `/update`) metotlarının kullanılabileceği, `PUT / DELETE / PATCH` kullanımının `check_api_docs.py` `E4` kapısıyla engellendiği,
  - Hata yanıtlarına `409 Conflict` (Optimistic Lock / Aktif Alt Kayıt Engeli / Mükerrer İşlem) eklendiği işlenir.

#### [MODIFY] [.agent/rules/db-migration-enforcement.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/db-migration-enforcement.md)
- §4 Geriye Uyumluluk ve Güvenlik İlkeleri altına **Soft-Delete Partial Unique Index & Kaskad Veri Koruması** maddesi eklenir.

#### [MODIFY] [.agent/skills/musgoku/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/SKILL.md)
- Adım 2 ve Adım 4 Backend & Frontend kontrol listelerine kesin `PUT/DELETE/PATCH` yasağı, RPC isimlendirme, `@Version` / `Idempotency-Key`, Global Query Filter ve Manuel Cache Eviction maddeleri eklenir.

---

### 2. Ölçülebilir Doğrulama Kapısı & Testler (`check_api_docs.py` & `test_rule_gates.py`)

#### [MODIFY] [.agent/skills/musgoku/scripts/check_api_docs.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/scripts/check_api_docs.py)
- **`E4` (`yasakli HTTP metodu — PUT/DELETE/PATCH kullanildi`) Kontrolü:**
  - `FORBIDDEN_HTTP_METHODS = {"PUT", "DELETE", "PATCH"}` sabiti tanımlanır.
  - `code_index` içinde yer alan her `(method, api_path, source)` üçlüsünde `method in FORBIDDEN_HTTP_METHODS` ise:
    - Eğer `docs/APIs/` içinde açıkça `<!-- ALLOW-HTTP-METHODS: PUT,DELETE -->` gibi bir legacy sözleşme istisnası tanımlanmamışsa `("E4", source, f"Yasakli HTTP metodu kullanildi: {method} {api_path} (Yalniz GET ve fiil tabanli POST kullanilmalidir)")` hatası (`exit 1`) üretilir.

#### [MODIFY] [tests/test_rule_gates.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/tests/test_rule_gates.py)
- `test_api_docs_violations()` içine:
  - `@PutMapping` ve `@DeleteMapping` kullanan bir Java Controller ile Next.js `DELETE` route handler için `E4` hatasının tetiklendiğini doğrulayan test,
  - `<!-- ALLOW-HTTP-METHODS: PUT,DELETE -->` istisna deklarasyonu olduğunda `E4` üretilmediğini doğrulayan false-positive koruma testi eklenir.

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
# 1. Kural ve API Dokümantasyonu Kapısı (E4) birim testleri
python tests/test_rule_gates.py

# 2. Skill sözleşmesi ve katalog tazelik derlemesi
python scripts/generate_skills_catalog.py
python tests/test_skills_catalog.py

# 3. Tüm depo regresyon test paketi (30/30 paket)
python tests/run_all.py

# 4. Birleşik doğrulama kapıları
python .agent/skills/musgoku/scripts/run_all_gates.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - Kural & Kapı Testi]:** `python tests/test_rule_gates.py` komutunu çalıştırın -> **Beklenen Çıktı:** `TEST 6: API dokumantasyonu kapisi` altında `PASS E4 yasakli HTTP metodu (PUT/DELETE) yakalandi` ve `SONUC: tum testler gecti` görünür.
2. **[Adım 2 - Anti-Pattern Taraması]:** `python -c "import pathlib; t=pathlib.Path('.agent/skills/musgoku/skills/musgoku-api-data-layer.md').read_text(encoding='utf-8'); assert 'httpClient.put' not in t and 'httpClient.delete' not in t; print('TEMIZ: PUT/DELETE anti-pattern yok')"` komutunu çalıştırın -> **Beklenen Çıktı:** `TEMIZ: PUT/DELETE anti-pattern yok` mesajı döner.
3. **[Adım 3 - Birleşik Kapı Kontrolü]:** `python .agent/skills/musgoku/scripts/run_all_gates.py` komutunu çalıştırın -> **Beklenen Çıktı:** `0 başarısız` ile tüm ölçülebilir kapılar yeşil (`[OK]`) tamamlanır.

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `[HATA] E4 ThingController.java: Yasakli HTTP metodu kullanildi: DELETE /v1/thing/{id}` | Controller veya Route Handler içinde `@DeleteMapping`, `@PutMapping` veya `@PatchMapping` kullanılmış | Uç noktayı fiil tabanlı `POST` metoduna (`@PostMapping("/{id}/delete")` veya `@PostMapping("/{id}/cancel")`) dönüştürün ve `docs/APIs/` dokümanını güncelleyin |
| `Soft-delete sonrası aynı e-posta ile yeni kayıtta Unique Constraint hatası` | Tabloda tam `UNIQUE(email)` kısıtı kalmış, silinmiş (`status = 'DELETED'`) satırlar indekse dahil ediliyor | PostgreSQL'de `CREATE UNIQUE INDEX CONCURRENTLY idx_active_email ON users(email) WHERE status != 'DELETED';` partial unique indeksine geçin |
| `Native SQL rapor sorgusunda silinmiş (DELETED) kayıtlar listeye sızıyor` | Hibernate `@SQLRestriction` / `@SoftDelete` yalnız JPQL/Entity sorgularında çalışır, `nativeQuery = true` ve alt sorgularda çalışmaz | Native SQL içindeki ana sorguya ve tüm `JOIN` / `EXISTS` / `IN` alt sorgularına `AND t.status != 'DELETED'` filtresini ekleyin |
