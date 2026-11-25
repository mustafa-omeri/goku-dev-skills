# Java / Spring Boot Kullanılmayan Kod & `@Autowired` Kalıntıları Kök Neden Analizi ve Uygulama Planı

> **Hedef Dal / Sürüm:** `skillSetWorks` (`main`) + `ocai` (hedef repo) · **Tarih:** `2026-11-25`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `musgoku`, `tdd`, `commitx`, `verify-last`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`, `get_project_state`), `sequential-thinking`  
> **İlgili KANBAN Kartı:** `GSW-GATE-001` (Skillset Kapı Güçlendirme) & `OCAI-CLEAN-001` (Kardeş/Hedef Repo Temizliği)  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`  

---

## 1. [Goal Description] (Amaç & Kapsam)

`ocai` (Spring Boot 3.5.16 / Java 21) projesinde `04b079e` commit'i sonrasında VS Code Java (Eclipse JDT) `Problems` sekmesinde kalan kullanılmayan `import` ve kullanılmayan `@Autowired` alan hatalarının kök nedenini gidermek ve benzer kalıntıların (`import`, gereksiz `@Autowired`, kullanılmayan değişken ve ölü sınıflar) bir daha commit aşamasına sızmasını mekanik olarak engellemek.

### Gözlenen Kök Nedenler (Kanıtlı Teşhis)
1. **`check-unused.ps1` zaten tüm 5 hatayı yakalıyor, ancak çalıştırılmamış:**
   `ocai` üzerinde salt okunur çalıştırılan `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` denetimi tam olarak yapıştırılan 5 bulguyu `[FAIL]` (`exit 1`) olarak raporladı (`617` dosya tarandı):
   - `src/test/java/com/performinds/ocai/integration/TenantRlsIsolationIT.java:3` (`JsonNode` import)
   - `src/test/java/com/performinds/ocai/modules/assessment/OcaiScoreParityGoldenMasterIT.java:39` (`private JdbcTemplate jdbcTemplate`)
   - `src/test/java/com/performinds/ocai/modules/assessment/UnifiedAttemptAndKvkkIT.java:41` (`private AttemptEngineService attemptEngineService`)
   - `src/test/java/com/performinds/ocai/modules/assessment/UnifiedAttemptAndKvkkIT.java:44` (`private ComplianceService complianceService`)
   - `src/test/java/com/performinds/ocai/modules/report/ComplementarySuppressionAndReportIT.java:3` (`JsonNode` import)
2. **`run_all_gates.py` Java kapılarını hiç koşturmuyor (Orkestrasyon Körlüğü):**
   `commitx`, `verify-last` ve Faz 4/5 tek komut olarak `python .agent/skills/musgoku/scripts/run_all_gates.py` çağırıyor. Ancak `run_all_gates.py` yalnızca 15 Python doküman/tasarım kapısını çalıştırıyor; `--include-slow` bayrağında bile sadece Frontend `check_bundle_limits.py` var — **`check-unused.ps1` ve `mvn clean test-compile` hiç yok!**
3. **Kural ve skill dosyalarında `src/test/java` atlanıyor:**
   `no-unused-code.md` front matter `kapi:` alanı, `development-workflow.md` `GATE-TABLE` tablosu ve `commitx/SKILL.md` satır 24 `mvn clean compile -DskipTests` yazıyor. `compile` komutu `src/test/java` dizinini derlemez; 5 hatanın tamamı `src/test/java` içindedir.
4. **`check-unused.ps1` tespit kör noktaları (Spring `@Autowired` & ölü sınıflar):**
   Mevcut ECJ bayrakları (`-warn:unusedImport,unusedLocal,unusedPrivate,warningToken,unchecked`) şunları yakalamıyor:
   - Tek constructor'lı Spring bean veya constructor parametresindeki gereksiz `@Autowired` (`WebSocketConfig.java:39-40` içindeki `@Autowired JwtTokenProvider`, `@Autowired UserDetailsService`).
   - `private` olmayan (`package-private` / `protected`) kullanılmayan `@Autowired` test alanları.
   - Hiçbir yerden referans edilmeyen ölü sınıflar / DTO'lar / yardımcı sınıflar (`ocai` içinde taramada yalnızca kendi dosyasında geçen 11 aday tespit edildi; örn. `ActivationVerifyRequest`, `AssignDepartmentSectionRequest`, `AssignDepartmentSectionV2Request`, `BulkUpdateUserStatusRequest`, `BulkUpdateUserStatusResponse`, `UpdateUserStatusRequest`, `UserCategoryStatsDTO`, `PasswordGenerator`, `PasswordResetUtil`, `EmbeddingModelRegistry`, `AssessmentPlanRepository`).

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: Java ve Spring Boot Kullanılmayan Kod & Autowired Kapı Koruması
  Scenario: Java projesinde commit öncesi birleşik kapı koşturulduğunda
    Given projede pom.xml vardır ve src/main/java veya src/test/java altında kullanılmayan import, değişken, gereksiz @Autowired veya ölü sınıf bulunur
    When ajan "python .agent/skills/musgoku/scripts/run_all_gates.py" veya "check-unused.ps1" çalıştırır
    Then Java kullanılmayan kod kapısı otomatik tetiklenir ve [FAIL] (exit 1) ile tam dosya:satır listesi döner

  Scenario: ocai projesi temizlendikten sonra Problems sekmesi ve kapı kontrolü
    Given ocai içindeki 5 ECJ bulgusu, gereksiz constructor @Autowired ekleri ve onaylanan ölü sınıflar temizlenmiştir
    When "mvn clean test-compile" ve "pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1" koşturulur
    Then her iki komut exit 0 ([OK]) döner ve IDE Problems sekmesinde bu kalıntılar görünmez
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (2+ Seçenek İncelemesi)

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Yalın — Yerel ECJ + Hafif AST/Regex Genişletmesi + `run_all_gates.py` Entegrasyonu)** | Mevcut `check-unused.ps1` (ECJ) içine ek statik kontroller (gereksiz `@Autowired`, package-private test `@Autowired`, ölü sınıf adayı taraması) ekleyip `run_all_gates.py` içine `pom.xml` algıladığında `check-unused.ps1` + `--include-slow` için `mvn clean test-compile` bağlamak | Sıfır yeni Maven plugin/bağımlılık riski; hedef projelerin `pom.xml`'ine dokunmadan `delivery.py` ile tüm Java projelerine (`ocai`, `kalansure`) dağılır; deterministik exit code | Ölü sınıf taraması Spring reflection / `@Configuration` / `@RestController` / `@Scheduled` gibi dolaylı bileşenleri hariç tutmazsa yanlış pozitif üretebilir (whitelist/annotation filtresi şart) | **2.8** |
| **Option B (Ağır Maven Plugin — Spotless / PMD / ErrorProne / SonarLint)** | Her hedef Java projesinin `pom.xml` dosyasına `maven-pmd-plugin`, `spotless-maven-plugin` veya Google ErrorProne eklemek | Çok derin veri akışı analizi | Her hedef projenin `pom.xml` ve build süresini değiştirir; mevcut legacy kodlarda yüzlerce eski uyarı patlatıp `build`'i kilitler; `skillSetWorks` merkezî dağıtım kapsamını aşar | **1.4** |

- **Seçilen Yol & Gerekçe:** **Option A**. Hem `skillSetWorks` içindeki tüm Java projelerine (`ocai`, `kalansure`) sıfır `pom.xml` müdahalesiyle `delivery.py` üzerinden anında dağılır, hem de `run_all_gates.py` kör noktasını kapatır.
- **Birleşik Planlama Ekosistemi Bağlantısı:** Kök neden tespiti → Konsey hakemliği (Option A) → Görev kimlikleri (`GSW-GATE-*`, `OCAI-CLEAN-*`) → TDD Kırmızı-Yeşil dikiş noktaları (`tests/test_check_unused_java.py` + `check-unused.ps1` canary).

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)

> [!IMPORTANT]
> **1. Hedef Proje Topolojisi (`skillSetWorks` vs `ocai`):**
> Şu anki çalışma dizini `skillSetWorks`'tür (`C:\devtools\myProjectsAreaWS\toolsWS\skillSetWorks`). `ocai` (`C:\devtools\vscodeWS\peopleside-culture\ocai`) farklı dizinde bulunan bir hedef/kardeş projedir.
> - **Soru 1:** `skillSetWorks` kurallarını ve kapılarını güncelledikten sonra `python delivery.py --only ocai` ile `ocai/.agent/` güncellemesini yapıp, `ocai` içindeki kod kalıntılarını da **ben mi temizleyeyim**, yoksa `ocai` temizliğini `ocai`'ın kendi kod ajanı mı yapsın?
>
> **2. `ocai` İçindeki 11 Referanssız Sınıf Adayı ve `@Slf4j` Politikası:**
> - **Ölü sınıf adayları:** `AssessmentPlanRepository` `04b079e` commit'inde yeni eklenmiş (muhtemelen Faz 1b için hazırlanmış); diğer 10 sınıf (`ActivationVerifyRequest`, `AssignDepartmentSectionRequest`, `AssignDepartmentSectionV2Request`, `BulkUpdateUserStatusRequest`, `BulkUpdateUserStatusResponse`, `UpdateUserStatusRequest`, `UserCategoryStatsDTO`, `PasswordGenerator`, `PasswordResetUtil`, `EmbeddingModelRegistry`) legacy/ölü görünüyor. Silmeden önce her biri için tek tek onay veya `--warn-only` raporu gerekir.
> - **`@Slf4j` unused `log`:** `ocai`'da 12 sınıfta `@Slf4j` var ama `log` kullanılmıyor (`OcaiApplication`, `CategoryController`, `RetentionPurgeJob`, vb.). `check-unused.ps1` satır 113 bunu kasıtlı bastırıyor; bunların da bulgu sayılmasını istiyor musunuz?
>
> **2-Modlu Onay Seçenekleri:**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan`):** Planı `docs/plans/` altına arşivler, `HANDOFF.md` §3'e ekler, kod yazmadan durur.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed`):** Faz 0 arşivleme sonrası Faz 1 (TDD Kırmızı Test) ile uygulamaya geçer.

## 4. Open Questions (Açık Sorular)
> [!CAUTION]
> 1. `ocai` içindeki **5 ECJ bulgusu + `WebSocketConfig` gereksiz `@Autowired`** dışındaki **11 referanssız sınıf adayından** (`AssessmentPlanRepository` hariç) hangileri silinsin, hangileri `Faz 1b` için korunsun?
> 2. `check-unused.ps1` içinde `@Slf4j` ama `log` kullanmayan sınıflar (`12` adet) `[FAIL]` mı sayılsın yoksa `[uyarı]` olarak mı raporlansın?
> 3. `run_all_gates.py` çalıştırıldığında `pom.xml` olan projelerde `check-unused.ps1` **varsayılan hızlı akışta** mı koşsun (ECJ `~4-6 sn` sürüyor), yoksa yalnızca `--include-slow` / `--with-java` ile mi? *(Öneri: Varsayılan akışta koşsun — aksi halde `commitx` ve `verify-last` yine atlar.)*

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-GATE-001` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3) | `run_all_gates.py` içine Java (`check-unused.ps1` + opsiyonel `mvn clean test-compile`) entegrasyonu ve `no-unused-code.md` / `commitx` / `development-workflow.md` `test-compile` hizalaması |
| `GSW-GATE-002` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3) | `check-unused.ps1` genişletmesi: gereksiz `@Autowired` denetimi, package-private test `@Autowired` alanı yakalama ve ölü (referanssız) Java sınıfı uyarı/raporlama |
| `GSW-REL-003` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3) | `python delivery.py --only ocai --verify` ile `ocai` (ve istenirse `kalansure`) `.agent/` dağıtımı ve parite doğrulaması |
| `OCAI-CLEAN-001` | `Bekliyor` | `Onaya Bağlı` | `ocai` içindeki 5 ECJ bulgusu, `WebSocketConfig` gereksiz `@Autowired` ekleri ve onaylanan ölü sınıfların temizliği + `mvn clean test-compile` doğrulaması |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- **Etkilenen Kardeş Uygulama, Yol & Topoloji:** `C:\devtools\vscodeWS\peopleside-culture\ocai` (Farklı Dizin — `ASK_USER_PREFER_SIBLING_AGENT`)
- **Kardeş `HANDOFF.md` + Süreç Dosyalarına Yazılacak Görevler & Sözleşme Özeti:** `OCAI-CLEAN-001` — `skillSetWorks` planına göre 5 ECJ bulgusunun (`TenantRlsIsolationIT`, `OcaiScoreParityGoldenMasterIT`, `UnifiedAttemptAndKvkkIT`, `ComplementarySuppressionAndReportIT`), `WebSocketConfig` gereksiz `@Autowired` parametrelerinin ve onaylanan ölü sınıfların temizlenmesi.
- **Kardeş UI Wireframe Beklentisi:** `UI Kapsam Dışı (Salt Backend / Tooling)`
- **Yürütme Sahipliği Sorusu (Farklı Dizinde Zorunlu):** *"Kardeş proje farklı dizinde yer alıyor; öncelik kardeş projenin kendi kod ajanındadır. `ocai` içindeki temizliği kendi kod ajanı mı yapsın, yoksa `skillSetWorks` güncellemesinden sonra ben mi devralayım?"*

### 5.2 🛡️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Matrisi (Pre-Seal Conflict Check)
| Hedef / Yüzey | Sınıflandırma | İlgili Canlı Dosya / Bekleyen Plan | Alınacak Önlem |
|---|---|---|---|
| `.agent/skills/musgoku/scripts/run_all_gates.py` | `MODIFY` | Canlı dosya (mevcut Python kapı orkestratörü) | Mevcut 15 Python kapısına dokunmadan Java algılama (`pom.xml`) ekle |
| `.agent/skills/musgoku/scripts/check-unused.ps1` | `MODIFY` | Canlı dosya (mevcut ECJ denetleyicisi) | Mevcut Canary + ECJ mantığını koruyarak ek Spring/`@Autowired`/ölü sınıf kontrollerini ekle |
| `.agent/rules/no-unused-code.md`, `development-workflow.md`, `commitx/SKILL.md` | `MODIFY` | Canlı dosyalar | `mvn clean compile -DskipTests` -> `mvn clean test-compile` düzeltmesi + `rules_gates.py --strict` yenilemesi |

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Full-Stack Vertical Slice)
`Salt Backend / Dev-Tooling & Kalite Kapısı (UI ve DB Kapsam Dışı)`

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi (Theme & Component Skeleton Contract)
`Salt Backend / CLI / Skillset — UI Kapsam Dışı`

### 7.1 🖼️ UI/UX Ön-Tasarım Önizlemesi
`Tier 0: Salt Backend / UI Kapsam Dışı`

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 — Koda Dokunmadan Önce Zorunlu)
1. **[Adım 1 - Plan Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug java-unused-code-gates` çalıştır -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_java-unused-code-gates_<TIMESTAMP>.md` basılır.
2. **[Adım 2 - `HANDOFF.md` §3 Panosuna İşle]:** `GSW-GATE-001`, `GSW-GATE-002`, `GSW-REL-003` görevlerini `skillSetWorks/HANDOFF.md` §3'e yaz ve `python .agent/skills/musgoku/scripts/check_handoff.py` çalıştır -> **Beklenen Çıktı:** `0 hata` döner.
3. **[Adım 3 - Kardeş Handoff Senkronu (Onaylandıysa)]:** `python .agent/skills/musgoku/scripts/sync_sibling_handoff.py --sibling-root C:/devtools/vscodeWS/peopleside-culture/ocai --source-root . --plan <arşivlenen-plan> --task-id OCAI-CLEAN-001 --task-title "Java unused import, gereksiz Autowired ve ölü sınıf temizliği" --summary "5 ECJ bulgusu + WebSocketConfig redundant @Autowired + onaylı ölü sınıflar"` çalıştır -> **Beklenen Çıktı:** `ocai/HANDOFF.md` içine görev kaydı işlenir.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - `run_all_gates.py` Java Kapısı Kırmızı Testi]:** `tests/test_java_unused_gates.py` içinde sahte `pom.xml` + başarısız `check-unused.ps1` (veya `check_java_unused` köprüsü) simüle eden `unittest` yaz ve `python -m unittest tests/test_java_unused_gates.py` çalıştır -> **Beklenen Çıktı:** `run_all_gates.py` Java kapısını çağırmadığı için test **KIRMIZI (FAIL)** döner.
2. **[Adım 2 - `check-unused.ps1` Canary & `@Autowired` Kırmızı Testi]:** Geçici bir fixture Java dosyasında (tek constructor'da `@Autowired` parametresi, package-private kullanılmayan `@Autowired` alanı, kullanılmayan import) mevcut `check-unused.ps1` mantığını sına -> **Beklenen Çıktı:** Gereksiz `@Autowired` ve package-private alan yakalanmadığı için test **KIRMIZI (FAIL)** döner.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
1. **[Adım 1 - `run_all_gates.py` İçine Java Kapısı Bağla]:** `run_all_gates.py` içinde `(root / "pom.xml").is_file()` kontrolü ekle; `check-unused.ps1` (varsayılan hızlı/standart akışta, `pwsh` mevcutsa) ve `--include-slow` verildiğinde `mvn clean test-compile` çalıştırıp sonuç tablosuna `PASS`/`FAIL`/`SKIPPED` ekle -> **Beklenen Çıktı:** `tests/test_java_unused_gates.py` **YEŞİL (PASS)** döner.
2. **[Adım 2 - `check-unused.ps1` Genişletmesi]:**
   - ECJ çıktısına ek olarak Spring/Java statik taraması ekle:
     a) Tek constructor'lı sınıfta `@Autowired` (yalnız `@Autowired(required = false)` hariç; parametrede veya constructor üzerinde yalın `@Autowired` yasak — `no-unused-code.md` §4.3).
     b) Test sınıflarında package-private / protected `@Autowired` alanlarının dosya içinde kullanılmaması (alan adı dosyada yalnızca 1 kez geçiyorsa `[FAIL]`).
     c) Referanssız ölü sınıf adayı taraması (`@SpringBootApplication`, `@Configuration`, `@RestController`, `@Controller`, `@Service`, `@Repository`, `@Component`, `@Entity`, `@Aspect`, `*Test`, `*IT` hariç; yalnızca 1 dosyada geçen DTO/Util sınıflarını `[uyarı]` veya `--FailOnDeadClass` ile raporlama).
     d) Canary dosyasına gereksiz `@Autowired` senaryosu ekleyip sahte geçişi önle.
   -> **Beklenen Çıktı:** Canary ve birim testleri **YEŞİL (PASS)** döner.
3. **[Adım 3 - Kural & Skill Dokümantasyonu Hizalama]:**
   - `.agent/rules/no-unused-code.md` (`kapi:` satırı) ve `.agent/rules/development-workflow.md` (`GATE-TABLE`) üzerinde `mvn clean compile -DskipTests` -> `mvn clean test-compile` güncelle (global `rules_gates.py --strict` uyumuyla).
   - `.agent/skills/commitx/SKILL.md` ve `.agent/skills/verify-last/SKILL.md` içine Java projelerinde `mvn clean test-compile` ve `check-unused.ps1` zorunluluğunu ekle.
   -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/rules_gates.py --strict` ve `python tests/run_all.py` **YEŞİL (PASS)** döner.

### 🧩 Faz 3: Dağıtım & Hedef Proje (`ocai`) Temizliği (Kullanıcı Onayına Bağlı)
1. **[Adım 1 - Skillset Dağıtımı]:** `python delivery.py --only ocai` (ve `python delivery.py --only ocai --verify`) çalıştır -> **Beklenen Çıktı:** Güncel `check-unused.ps1`, `run_all_gates.py` ve kurallar `ocai/.agent/` altına byte-byte eşit kopyalanır.
2. **[Adım 2 - `ocai` Test Dosyalarındaki 5 ECJ Bulgusunu Temizle]:**
   - `TenantRlsIsolationIT.java:3` → kullanılmayan `JsonNode` import'unu sil.
   - `ComplementarySuppressionAndReportIT.java:3` → kullanılmayan `JsonNode` import'unu sil.
   - `OcaiScoreParityGoldenMasterIT.java:39` → kullanılmayan `@Autowired private JdbcTemplate jdbcTemplate;` (ve varsa yalnızca onun kullandığı `JdbcTemplate` import'unu) sil.
   - `UnifiedAttemptAndKvkkIT.java:41,44` → kullanılmayan `@Autowired private AttemptEngineService attemptEngineService;` ve `@Autowired private ComplianceService complianceService;` alanlarını + kullanılmayan import'larını sil.
3. **[Adım 3 - `WebSocketConfig.java` Gereksiz `@Autowired` Temizliği]:** `WebSocketConfig.java:39-40` içindeki `@Autowired JwtTokenProvider` ve `@Autowired UserDetailsService` eklerini kaldır (`@Autowired(required = false) OcaiWebSocketHandler` korunur).
4. **[Adım 4 - Onaylanan Ölü Sınıfların Temizliği]:**
   ⚠️ CRITICAL: Sınıf silmeden önce `git log` / test referansları tekrar doğrulanır ve **yalnızca kullanıcının Açık Soru #1'de onayladığı** ölü sınıflar silinir (`AssessmentPlanRepository` gibi Faz 1b için tutulanlara dokunulmaz).

### 🧹 Faz 4: Refactor, Kapılar & Kapanış
1. **[Adım 1 - Tüm Kapıları Koştur]:** `skillSetWorks` içinde `python tests/run_all.py` ve `python .agent/skills/musgoku/scripts/run_all_gates.py`; `ocai` içinde `mvn clean test-compile`, `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` ve `python .agent/skills/musgoku/scripts/run_all_gates.py` çalıştır -> **Beklenen Çıktı:** Tüm kapılar `[OK]` / `PASS` döner.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### `skillSetWorks` — Kalite Kapısı & Kural Güncellemeleri
#### [MODIFY] `.agent/skills/musgoku/scripts/run_all_gates.py`
- `pom.xml` varlığında `check-unused.ps1` kapısını çalıştırma (`pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1`); `--include-slow` ile `mvn clean test-compile` ekleme.

#### [MODIFY] `.agent/skills/musgoku/scripts/check-unused.ps1`
- Mevcut ECJ (`unusedImport,unusedLocal,unusedPrivate,warningToken,unchecked`) taramasına ek olarak:
  - Gereksiz `@Autowired` tarayıcısı (`@Autowired(required = false)` hariç tek constructor/parametre `@Autowired`).
  - Test sınıflarında package-private/protected kullanılmayan `@Autowired` alan tespiti.
  - Referanssız ölü sınıf adayı raporu (`[uyarı]` varsayılan, `-FailOnDeadClass` ile sert kapı).
  - Canary testine yeni kontrollerin eklenmesi.

#### [MODIFY] `.agent/rules/no-unused-code.md` & `.agent/rules/development-workflow.md` & `.agent/AGENTS.md`
- `mvn clean compile -DskipTests` -> `mvn clean test-compile` güncellemesi (`rules_gates.py --emit-table` ile senkronize).

#### [MODIFY] `.agent/skills/commitx/SKILL.md` & `.agent/skills/verify-last/SKILL.md`
- Java projelerinde `mvn clean test-compile` ve `check-unused.ps1` adımlarının açıkça şart koşulması.

#### [NEW] `tests/test_java_unused_gates.py`
- `run_all_gates.py` Java kapısı entegrasyonu ve `@Autowired` / test-scope tespiti için birim testler.

---

### `ocai` (Onay Sonrası) — Kod Temizliği
#### [MODIFY] `src/test/java/com/performinds/ocai/integration/TenantRlsIsolationIT.java`
```diff
-import com.fasterxml.jackson.databind.JsonNode;
 import com.fasterxml.jackson.databind.ObjectMapper;
```

#### [MODIFY] `src/test/java/com/performinds/ocai/modules/report/ComplementarySuppressionAndReportIT.java`
```diff
-import com.fasterxml.jackson.databind.JsonNode;
 import com.fasterxml.jackson.databind.ObjectMapper;
```

#### [MODIFY] `src/test/java/com/performinds/ocai/modules/assessment/OcaiScoreParityGoldenMasterIT.java`
```diff
 import org.springframework.beans.factory.annotation.Autowired;
-import org.springframework.jdbc.core.JdbcTemplate;
...
     @Autowired
     private CultureAssessmentAdapter cultureAssessmentAdapter;
-
-    @Autowired
-    private JdbcTemplate jdbcTemplate;
```

#### [MODIFY] `src/test/java/com/performinds/ocai/modules/assessment/UnifiedAttemptAndKvkkIT.java`
```diff
-import com.performinds.ocai.modules.assessment.engine.AttemptEngineService;
 import com.performinds.ocai.modules.assessment.proctoring.ProctoringProviderPort;
 import com.performinds.ocai.modules.compliance.job.RetentionPurgeJob;
-import com.performinds.ocai.modules.compliance.service.ComplianceService;
...
-    @Autowired
-    private AttemptEngineService attemptEngineService;
-
-    @Autowired
-    private ComplianceService complianceService;
-
     @Autowired
     private RetentionPurgeJob retentionPurgeJob;
```

#### [MODIFY] `src/main/java/com/performinds/ocai/core/config/WebSocketConfig.java`
```diff
     public WebSocketConfig(@Autowired(required = false) OcaiWebSocketHandler ocaiWebSocketHandler,
-                           @Autowired JwtTokenProvider jwtTokenProvider,
-                           @Autowired UserDetailsService userDetailsService) {
+                           JwtTokenProvider jwtTokenProvider,
+                           UserDetailsService userDetailsService) {
```

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```powershell
# 1. skillSetWorks tüm kural ve kapı testleri
python tests/run_all.py
python .agent/skills/musgoku/scripts/rules_gates.py --strict
python .agent/skills/musgoku/scripts/run_all_gates.py

# 2. ocai üzerinde dağıtım sonrası doğrulama
Push-Location "C:\devtools\vscodeWS\peopleside-culture\ocai"
mvn clean test-compile
pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1
python .agent/skills/musgoku/scripts/run_all_gates.py
Pop-Location
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - VS Code Java Language Server Yenileme]:** `ocai` penceresinde `Ctrl+Shift+P` -> `Java: Clean Java Language Server Workspace` çalıştır -> **Beklenen Çıktı:** `Problems` sekmesinde `TenantRlsIsolationIT.java`, `OcaiScoreParityGoldenMasterIT.java`, `UnifiedAttemptAndKvkkIT.java`, `ComplementarySuppressionAndReportIT.java` uyarıları `0` olur.
2. **[Adım 2 - Kapı Çıktısı Doğrulama]:** `ocai` kökünde `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` çalıştır -> **Beklenen Çıktı:** `[OK] Kullanilmayan import/local degisken ve gereksiz @SuppressWarnings yok.` basılır (`exit 0`).

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `check-unused.ps1` Canary `exit 3` dönüyor | `JAVA_HOME` Java 8'e bakıyor veya ECJ/Lombok sürümü uyumsuz | `$env:JAVA_HOME` değişkenini JDK 21 yoluna ayarlayıp komutu yeniden çalıştırın. |
| Ölü sınıf taraması Spring bileşeninde yanlış pozitif veriyor | Sınıf reflection, `@Bean` dönüşü veya AOP ile dolaylı çağrılıyor | Sınıfı silmeyin; `git checkout -- <dosya>` ile geri alın ve annotation muafiyet listesine ekleyin. |
| `run_all_gates.py` `pwsh` bulunamadı hatası veriyor | Ortamda PowerShell Core (`pwsh`) kurulu değil | `pwsh` yoksa `[SKIP]` (veya Windows `powershell.exe` fallback'i) ile güvenli geçiş sağlayın. |
| `ocai` test derlemesi bozuldu | Kullanıldığı sanılmayan bir alan/sınıf aslında test veya reflection ile kullanılıyordu | `git restore <dosya>` ile geri alıp `mvn clean test-compile` ile doğrulayın. |
