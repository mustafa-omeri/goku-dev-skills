# `/test-spec-run` Tam Otonom Kapalı Döngü (Auto-Triage + `fix-bug` + Bounded Re-Run) Uygulama Planı

> **Hedef Dal / Sürüm:** `main` (`v1.51.1` → `v1.52.0`) · **Tarih:** `2026-11-28`  
> **Standart:** `FAA AC 121-24C + /caveman`  
> **Görevlendirilen Skill'ler:** `test-spec-run`, `test-spec-generator`, `fix-bug`, `smoke-test`, `tdd`, `council`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`), `sequential-thinking`  
> **İlgili KANBAN / HANDOFF Kimlikleri:** `GSW-FEAT-028`, `GSW-DOCS-002`  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`

---

## 1. Goal Description (Kök Neden & Hedef)

### Neden `FEProjectv1`'de Manuel Adımla Durdu?
1. [test-spec-run/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/test-spec-run/SKILL.md#L41) satır 41 ve [test-spec-generator/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/test-spec-generator/SKILL.md#L115) satır 115, bir önceki plan ([plan_test_spec_run_20261127_233210.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/docs/plans/plan_test_spec_run_20261127_233210.md#L73)) kararı gereği **otonom kod düzenlemesini açıkça yasaklıyor**:
   - *"otonom kod düzenlemesi yapma, `/fix-bug` öner"*
2. Bu yüzden ajan TestSprite koşumu, `record` ve `triage` adımlarını başarıyla yaptıktan sonra kurala uyarak durdu ve `SC-ADM-02`, `SC-RPT-02`, `SC-RPT-03`, `SC-ORG-02`, `SC-AUTHZ-02`, `SC-ADM-04` için manuel `/fix-bug` adımı önerdi.

### Hedef & Gerçek Dünya Kısıtları (`FEProjectv1` Kanıtı)
`FEProjectv1` üzerinde oluşan gerçek `test-spec-state.json` (`PASS: 19, FAIL: 20, NEW: 20`) ve `raw_report.md` / `triage` çıktısı incelendiğinde tek tip bir "düzelt ve TestSprite'ı tekrar koş" döngüsü yetersizdir; 4 farklı hata sınıfı ortaya çıkmıştır:
1. **`FE_DEFECT` (Birincil Repo Hatası):** Örn. `SC-ADM-04` (boş soru formunda validasyon mesajı yok) → doğrudan `FEProjectv1` içinde `fix-bug` ile çözülüp TestSprite'ta tekrar koşulabilir.
2. **`BE_PEER_DEFECT` (Kardeş Backend Repo Hatası):** Örn. `SC-ORG-02`, `SC-SYS-01` (`/api/v1/health` 403), `ocai` reposundaki controller/security/seed hatası → `peers[0]` (`ocai`) tarafında çözüm + backend restart gerektirir.
3. **`ENV_AUTH_SEED` (Ortam / Seed / Yetki Ön Koşulu):** Örn. `goku.admin@test.local` hesabının `SC-ADM-02`, `SC-RPT-02`, `SC-RPT-03` üzerinde *"Bu işlemi yapmak için yetkiniz bulunmuyor"* alması → tek bir seed/RBAC/credential kök nedeni birden çok senaryoyu blokluyor; önce bu çözülmeden kalan senaryoları tekrar koşmak kredi yakar.
4. **`NON_UI_OBSERVABLE` (`TEST BLOCKED` / API-Only / RBAC-Hidden):** Örn. `SC-AUTH-05` (5 eşzamanlı 401 token yenileme), `SC-AUD-03` (`<300ms` latency göstergesi UI'da yok), `SC-DASH-03` (RBAC gereği buton UI'da gizli) → TestSprite tarayıcı ajanıyla tekrar koşulsa da **sonsuza kadar `BLOCKED/FAIL` döner**. Bunlar Playwright API/Vitest/JUnit ile doğrulanıp `test_spec_tracker.py record --runner vitest|playwright|junit` ile mühürlenmelidir.

```gherkin
Feature: /test-spec-run Tam Otonom Kapalı Döngü
  Scenario: Kök neden sınıflandırması ve otonom onarım sonrası hedefli yeniden koşum
    Given test-spec-state.json içinde FAIL veya NEW senaryolar vardır
    When kullanıcı "/test-spec-run" komutunu verdiğinde (varsayılan: otonom mod)
    Then testsprite_bridge.py triage her FAIL senaryoyu ENV_AUTH_SEED / NON_UI_OBSERVABLE / BE_PEER_DEFECT / FE_DEFECT olarak sınıflandırır
    And ajan ENV_AUTH_SEED ve FE_DEFECT (+ yetkiliyse BE_PEER_DEFECT) için ara onay sormadan fix-bug işletir
    And NON_UI_OBSERVABLE senaryoları TestSprite yerine hedef API/birim testiyle doğrulayıp record ile mühürler
    And yalnızca onarılan SC-* alt kümesi üzerinde (--scenarios) TestSprite kota kontrolüyle bounded re-run (maks 2 tur) yapılır
```

---

## 2. 🏛️ Council Deliberation (Seçenek Analizi)

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda |
|---|---|---|---|:---:|
| **Option A (Yalın Prompt)** | Yalnız `SKILL.md`'den "otonom düzeltme yapma" yasağını sil, `fix-bug` + yeniden koş yaz | 2 dosya değişir | `TEST BLOCKED` / `NON_UI_OBSERVABLE` senaryolarında **sonsuz TestSprite döngüsü ve kredi yanması**; `ENV_AUTH_SEED` önceliği yok; peer repo sınırı belirsiz | 2.50 |
| **Option B (Yapılandırılmış Kapalı Döngü)** ✅ | `testsprite_bridge.py` (`triage` `failure_class` + `to-plan --scenarios` hedefli alt küme) + `SKILL.md` otonom döngü (`ENV_AUTH_SEED` → `FE/BE` `fix-bug` → `NON_UI_OBSERVABLE` yerel test → maks 2 TestSprite re-run + `--no-fix` opt-out) | Sıfır kredi yanması, sahte UI düzeltmesi önlenir, mevcut `record`/`triage` kontratıyla %100 geriye uyumlu | Bridge script'inde ~70 satır ek sınıflandırma ve birim testi gerekir | **1.00** ✅ |
| **Option C (Python Orkestratör)** | Python içinden MCP/LLM alt ajan tetikleyen harici runner | Tam CLI izolasyonu | Python MCP araçlarını (`testsprite_generate_code_and_execute`) doğrudan çağıramaz; over-engineering | 2.50 |

- **Seçilen Yol:** **Option B.**
- **Elenenler:** Option A krediyi yakma ve sonsuz döngü riski taşır; Option C teknik olarak MCP katmanını Python'dan çağıramaz.

---

## 3. User Review Required & Open Questions

> [!IMPORTANT]
> **Kardeş Repo (`backend-peer`) Otonom Müdahale Sınırı & Devre Kesici:**
> Mevcut anayasal kural ([handoff-session-continuity.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/handoff-session-continuity.md#L82-L87)), kardeş repo farklı dizindeyse (`FEProjectv1` → `C:/devtools/vscodeWS/peopleside-culture/ocai`) `ASK_USER_PREFER_SIBLING_AGENT` gerektirir.
> Ayrıca IDE/CLI sandbox'ı farklı çalışma alanı dizinine yazmayı engelleyebilir.

### ❓ Açık Sorular (Onay Öncesi Netleştirme)
1. **Kardeş Backend Repo (`peer`, örn. `ocai`) Otonom Yetkisi:** `/test-spec-run` sırasında `BE_PEER_DEFECT` veya `ENV_AUTH_SEED` kök nedeni kardeş backend reposunda çıkarsa; ajan kardeş repo diskte erişilebilir olduğunda **kullanıcıya sormadan doğrudan `ocai` tarafında da `fix-bug` + backend test/restart yapabilsin mi**, yoksa sadece birincil repoyu otonom düzeltip kardeş repo için tek sorulu onay/handoff mu istesin? *(Öneri: `/test-spec-run` içinde dosya sistemi erişimi varsa **otonom düzelt + her iki reponun `HANDOFF.md` / `knowledge-base.md` dosyasını güncelle**; erişim/sandbox engeli varsa `sync_sibling_handoff.py` ile devret.)*
2. **Değişiklik Sonrası Dağıtım Kapsamı:** `skillSetWorks` üzerinde plan uygulandıktan sonra global Antigravity eklentisi (`scripts/sync_agy_global.py`) ve hedef proje (`python delivery.py --only FEProjectv1` veya tüm `enabled:true` projeler) de hemen güncellensin mi?

> **2-Modlu Onay Seçenekleri:**
> - **Seçenek A — Mühürle (`/seal-plan`):** Planı `docs/plans/`'a arşivler, koda dokunmadan durur.
> - **Seçenek B — Onayla & Başla (`Proceed`):** Faz 0 arşivlemesini yapıp Faz 1..4 TDD ve dokümantasyon/katalog güncellemesini icra eder.

---

## 4. 📋 Sprint, HANDOFF & Ön-Mühürleme Çakışma Özeti

| Görev ID | Mevcut | Hedef | Kapsam |
|---|---|---|---|
| `GSW-FEAT-028` | `Bekliyor` | `Yapılıyor` | `testsprite_bridge.py`: `failure_class` triajı + `to-plan --scenarios` alt küme desteği + TDD testleri |
| `GSW-DOCS-002` | `Bekliyor` | `Yapılıyor` | `test-spec-run`, `test-spec-generator`, `skill-trigger-routing.md`, `generate_skills_catalog.py`, `bin/cli.js` senkronu |

- **Kardeş Uygulama Etkisi (Planlama Kapsamı):** `skillSetWorks` içinde tek repo değişikliği. Yalnızca kurallar/skill güncellendikten sonra `delivery.py` ile `FEProjectv1` / `ocai` hedeflerine dağıtım yapılır.
- **Ön-Mühürleme Çakışma Kontrolü:**
  - `testsprite_bridge.py::triage_failed_scenarios` & `export_testsprite_plan` → `ENRICHED_SUPERSET` (mevcut JSON alanları ve varsayılan davranış %100 korunur).
  - `test-spec-run/SKILL.md` & `test-spec-generator/SKILL.md` → `SHARED_SURFACE_OVERWRITE` (yalnız otonom kapalı döngü ve devre kesici kuralları eklenir; `SkillDescriptionContract` 25–70 kelime sınırı korunur).

---

## 5. 🏗️ 5 Katmanlı Mimari & Hedef İş Akışı

`Tier 0: Salt CLI / Skill Ekosistemi İşi (UI Kapsam Dışı)`

```text
/test-spec-run [--no-fix] [--max-cycles 2]
  │
  ├─[1] test_spec_tracker.py status ──► delta == 0 ? ──► DUR ("Tümü PASS")
  │
  ├─[2] testsprite_check_account_info
  │        └─ kredi yok / Paused ──► smoke_runner.py --mode live --testsprite-status exhausted ──► DUR
  │
  ├─[3] Server/Build Kontrolü (5173/4173 + peer BE health) + export-delta + to-plan + MCP execute + record
  │
  ├─[4] Kalan FAIL/FLAKY var mı? ──► Yoksa ──► export-delta + Rapor ("0 FAIL") ──► BİTTİ
  │
  └─[5] Otonom Triaj & Kapalı Döngü (--no-fix yoksa, cycle <= 2):
         testsprite_bridge.py triage --json
           │
           ├─(A) ENV_AUTH_SEED (ör. goku.admin yetki reddi, kapalı servis)
           │       └─ Önce seed/auth/env sorununu fix-bug ile çöz (tek kök neden -> çoklu SC açılır)
           ├─(B) NON_UI_OBSERVABLE (TEST BLOCKED / API latency / concurrency / RBAC-hidden)
           │       └─ TestSprite'a GERİ YOLLAMA! Hedefli Vitest/Jest/JUnit/Playwright-API testi koş
           │          ve `test_spec_tracker.py record --result SC-...=PASS|FAIL --runner ...` mühürle
           ├─(C) FE_DEFECT (primary) ──► fix-bug (Red -> Fix -> Green -> FE build/tsc)
           └─(D) BE_PEER_DEFECT (backend-peer)
                   ├─ Peer repo yazılabilir (+ izinli) ──► fix-bug (Red -> Fix -> mvn/pytest -> BE restart) + sync_sibling_handoff
                   └─ Sandbox/erişim engeli ──► sync_sibling_handoff.py ile peer HANDOFF.md'ye yaz + durma nedeni raporla
           │
           └─► Yalnız onarılan & TestSprite'ta koşulabilir SC-* listesi için:
                 1) FE değiştiyse: npm run build && preview yenile
                 2) testsprite_check_account_info (kota bittiyse smoke_runner fallback)
                 3) testsprite_bridge.py to-plan --scenarios <onarılan_SC_listesi>
                 4) MCP testsprite_generate_code_and_execute -> record -> kalan FAIL varsa cycle+1 (maks 2)
```

---

## 6. 🧪 TDD Kırmızı-Yeşil Fazları (`FAA AC 121-24C`)

### 📌 Faz 0: Onay Sonrası Mühürleme
1. **[Adım 1 - Arşiv]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug test_spec_run_autonomous --allow-no-wireframe` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_test_spec_run_autonomous_<ts>.md`
2. **[Adım 2 - HANDOFF §3]:** `GSW-FEAT-028` ve `GSW-DOCS-002` görevlerini `HANDOFF.md` §3 panosuna işle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0` hata.

### 🔴 Faz 1: Kırmızı Testler (`test_testsprite_bridge.py`)
1. **[Adım 1 - Kırmızı Test Yaz]:** [.agent/skills/test-spec-generator/scripts/tests/test_testsprite_bridge.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/test-spec-generator/scripts/tests/test_testsprite_bridge.py) içine şu 5 test ekle:
   - `triage`: `ENV_AUTH_SEED` (ör. *"signed-in administrator is denied access"* / *"Bu işlemi yapmak için yetkiniz bulunmuyor"*).
   - `triage`: `NON_UI_OBSERVABLE` (ör. `TEST BLOCKED` + *"visible UI provides no way"* / *"response-time indicator"*).
   - `triage`: `BE_PEER_DEFECT` ve `FE_DEFECT` ayrımı + `fixable_by_agent` + `remediation_route`.
   - `to-plan --scenarios SC-PROJ-01`: yalnız belirtilen `SC-*` alt kümesini TestSprite planına yazar, diğer `NEW/FAIL` senaryoları atlar.
2. **[Adım 2 - Kırmızı Koşum]:** `python -m pytest .agent/skills/test-spec-generator/scripts/tests -q` -> **Beklenen Çıktı:** Yeni eklenen testler **FAIL (Kırmızı)** döner.

### 🟢 Faz 2: Minimal Üretim Kodu (`testsprite_bridge.py`)
1. **[Adım 1 - `failure_class` Sınıflandırıcısı]:** [.agent/skills/test-spec-generator/scripts/testsprite_bridge.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/test-spec-generator/scripts/testsprite_bridge.py) içine `_classify_failure(err_txt, repo_role, ep_refs)` ekle (`ENV_AUTH_SEED`, `NON_UI_OBSERVABLE`, `BE_PEER_DEFECT`, `FE_DEFECT`) ve triage JSON öğelerine `failure_class`, `verification_runner`, `remediation_route` alanlarını (geriye uyumlu) ekle.
2. **[Adım 2 - `--scenarios` Filtresi]:** `export_testsprite_plan` ve CLI `to-plan` alt komutuna `only_scenarios` / `--scenarios` (virgülle ayrılmış veya tekrarlı) parametresi ekle.
3. **[Adım 3 - Yeşil Koşum]:** `python -m pytest .agent/skills/test-spec-generator/scripts/tests -q` -> **Beklenen Çıktı:** Tüm testler **PASS (Yeşil)**.

### 🧩 Faz 3: Otonom Skill, Routing, Katalog & CLI Güncellemesi
1. **[Adım 1 - `test-spec-run/SKILL.md`]:** [SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/test-spec-run/SKILL.md) satır 41'deki *"otonom kod düzenlemesi yapma"* yasağını kaldır; yerine **Aşama 5–6 Otonom Kapalı Döngü + Devre Kesici (Maks 2 Tur) + `NON_UI_OBSERVABLE` Yerel Test Yönlendirmesi + `--no-fix` Opt-Out** protokolünü yaz (frontmatter `description` 25–70 kelime sözleşmesine uyumlu).
2. **[Adım 2 - `test-spec-generator/SKILL.md`]:** [SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/test-spec-generator/SKILL.md#L94-L116) Aşama 6'yı `test-spec-run/SKILL.md` ile tam senkronize et (çelişkili *"otomatik kod düzeltmesi yapılmaz"* cümlesini kaldır).
3. **[Adım 3 - Routing, Katalog & CLI]:** [skill-trigger-routing.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/skill-trigger-routing.md#L147), [generate_skills_catalog.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/scripts/generate_skills_catalog.py#L460-L485) (`+ 2464, 2598`) ve [bin/cli.js](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/bin/cli.js#L567-L571) metinlerini otonom döngüyü yansıtacak şekilde güncelle; `python scripts/generate_skills_catalog.py` çalıştır.

### 🧹 Faz 4: Kapılar, Dağıtım & Kapanış
1. **[Adım 1 - Sözleşme & Tam Test Paketi]:**
   - `python -m unittest tests/test_skill_contracts` (veya `cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts`)
   - `python tests/run_all.py`
   - `python .agent/skills/musgoku/scripts/run_all_gates.py`
   -> **Beklenen Çıktı:** Tüm test ve kapılar **PASS / [OK]**.
2. **[Adım 2 - Plugin & Hedef Dağıtım (Onaylı Kapsama Göre)]:**
   - `python scripts/sync_agy_global.py`
   - `python delivery.py --only FEProjectv1` (veya `python delivery.py`)
   -> **Beklenen Çıktı:** Hedef repoda ve global eklentide byte-byte senkron doğrulandı.

---

## 7. Proposed Changes (Önerilen Değişiklikler)

### TestSprite Köprüsü (`test-spec-generator`)
#### [MODIFY] `.agent/skills/test-spec-generator/scripts/testsprite_bridge.py`
- `triage_failed_scenarios` çıktısına geriye uyumlu `failure_class` (`ENV_AUTH_SEED` | `NON_UI_OBSERVABLE` | `BE_PEER_DEFECT` | `FE_DEFECT`), `verification_runner` (`testsprite` | `local_api_or_unit`) ve `remediation_route` alanları eklenir.
- `export_testsprite_plan` + CLI `to-plan` alt komutuna `--scenarios` filtresi eklenir (hedefli yeniden koşumda yalnız onarılan senaryolar seçilir).

#### [MODIFY] `.agent/skills/test-spec-generator/scripts/tests/test_testsprite_bridge.py`
- 4 hata sınıfı + `--scenarios` filtresi için dikiş noktası birim testleri eklenir.

---

### Skill Sözleşmeleri, Routing & Katalog
#### [MODIFY] `.agent/skills/test-spec-run/SKILL.md`
- Otonom kapalı döngü (Adım 1–7): `status` → kota kontrolü → TestSprite koşum & `record` → `triage` → kök neden sınıfına göre otonom `fix-bug` / yerel API-birim doğrulaması (`record`) → FE rebuild / BE restart → yalnız onarılan senaryolarda `--scenarios` ile bounded re-run (maks 2 tur) + `--no-fix` bayrağı desteği.

#### [MODIFY] `.agent/skills/test-spec-generator/SKILL.md`
- Aşama 6'daki çelişkili *"otomatik kod düzeltmesi yapılmaz"* ifadesi kaldırılıp `test-spec-run/SKILL.md` ile uyumlu hale getirilir.

#### [MODIFY] `.agent/rules/skill-trigger-routing.md`
- Satır 147 ve 178'deki `/test-spec-run` tanımları otonom `fix-bug` + hedefli TestSprite re-run döngüsünü belirtecek şekilde güncellenir.

#### [MODIFY] `scripts/generate_skills_catalog.py` · `.agent/skills-catalog.html` · `bin/cli.js`
- `/test-spec-run` protokol ve açıklama metinleri güncellenir; katalog HTML yeniden üretilir.

---

## 8. Verification Plan

### Automated Tests
```powershell
# 1. Köprü birim testleri
python -m pytest .agent/skills/test-spec-generator/scripts/tests -q

# 2. Skill sözleşme ve description kelime bütçesi testi
cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts

# 3. Depo tam regresyon & birleşik kapılar
python tests/run_all.py
python .agent/skills/musgoku/scripts/run_all_gates.py
```

### Manual Verification (`FEProjectv1` Üzerinde)
1. **[Adım 1 - Dağıtım Sonrası Koşum]:** `FEProjectv1` çalışma alanında `/test-spec-run` tetikle -> **Beklenen Çıktı:** Ajan `triage` sonucuna göre durmadan önce `ENV_AUTH_SEED` / `FE_DEFECT` (ve yetki verildiyse `BE_PEER_DEFECT`) için `fix-bug` uygular, `NON_UI_OBSERVABLE` senaryoları yerel API/unit testiyle `record` eder ve onarılan senaryoları `--scenarios` ile TestSprite'ta tekrar koşar.
2. **[Adım 2 - Defter Kontrolü]:** `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py status --state docs/testing/test-spec-state.json` -> **Beklenen Çıktı:** Onarılan senaryolar `PASS` durumuna geçer; bloklananlar sahte `PASS` yazılmadan gerekçesiyle raporlanır.

---

## 9. 🚨 Ditching & Emergency Exit

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| TestSprite re-run döngüsü kredi yaktı | `NON_UI_OBSERVABLE` (`TEST BLOCKED`) veya onarılmayan `SC-*` tekrar TestSprite'a yollandı | `--scenarios` ile yalnızca kodu değişen `SC-*`'ları koş; `cycle >= 2` devre kesicisini tetikle |
| `SkillDescriptionContract` FAIL | `SKILL.md` `description` 70 kelimeyi aştı veya `Tetiklenmez:` düştü | `description` alanını 35–55 kelime bandında tut, `test_skill_contracts` ile doğrula |
| `test_skills_catalog.py` FAIL | `generate_skills_catalog.py` düzenlendi ama `.agent/skills-catalog.html` üretilmedi | `python scripts/generate_skills_catalog.py` çalıştır |
| Kardeş backend (`ocai`) sandbox nedeniyle yazılamıyor | Araç çalışma alanı sınırı dışına yazmayı engelliyor | `sync_sibling_handoff.py` ile `ocai/HANDOFF.md`'ye hata kaydını yaz ve kullanıcıya raporla |
