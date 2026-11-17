# 2-Modlu Plan Onay Kapısı (`/seal-plan` — Mühürle & Backlog'a Al vs `Proceed`) Uygulama Planı
<!--
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2
-->

> **Hedef Dal / Sürüm:** `main / skillSetWorks v1.39.0` · **Tarih:** `2026-11-17`  
> **Görevlendirilen Skill'ler:** `musgoku`, `tdd`, `doc-coauthoring`  
> **Kullanılan MCP'ler:** `sequential-thinking`  
> **İlgili Görev Kimlikleri:** `GSW-PLAN-003`, `GSW-PLAN-004`  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. Goal Description (Sorun, Amaç & Kapsam)

### Mevcut Sorun
`/plan` ile üretilen plan onaylandığında (`Proceed`), `development-workflow.md` Adım 2.2 şu an tek bir akışa sahiptir: **Faz 0 (Plan arşivi + `HANDOFF.md` §3 + `KANBAN.md`) → hemen ardından Faz 1..4 (Kodlama)**.
Ancak kullanıcı bazen planı beğenip **yapıya dağıtmak** (`docs/plans/`, `HANDOFF.md` §3 Gelecek Fazlar / Sıradaki İşler, `KANBAN.md` `Bekliyor`, varsa kardeş `HANDOFF.md`), fakat **araya başka bir sprint/iş alacağı için kodlamayı hemen başlatmamak** istemektedir. Mevcut sistemde bu niyeti tek komutla karşılayan resmi bir **"Yalnızca Faz 0'ı çalıştır ve kodlamadan dur (`/seal-plan`)"** kapısı bulunmadığından plan `brain/` klasöründe kalma riski taşır.

### Amaç
1. Plan sunumunda (`PLAN.template.md`) ve `development-workflow.md` Adım 2.2'de **2 Modlu Onay Kapısı** tanımlamak:
   - **Mod A — Mühürle & Sıraya Al (`/seal-plan`, `"planı mühürle"`, `"backlog'a al"`, `"kodlama yapma, dağıt"`):** Yalnızca **Faz 0** yürütülür (`archive_plan.py` → `docs/plans/`, `HANDOFF.md` §3 `Gelecek Fazlar` / `Sıradaki işler` tablosu, `KANBAN.md` `Bekliyor`, varsa `sync_sibling_handoff.py` ile kardeş `HANDOFF.md`). Üretim koduna, migration'a veya doküman dışı dosyalara **kesinlikle dokunulmaz** ve ajan durur.
   - **Mod B — Onayla & Başla (`Proceed`, `"geliştir"`, `"başla"`):** Faz 0 → Faz 1 (TDD Kırmızı Test) → Faz 2..5 kesintisiz yürütülür.
2. **Sonradan Tetikleme (Deferred Resume):** Kullanıcı istediği zaman *"Sprint 21'i başlat"* veya *"`<ID>` görevini başlat"* dediğinde ajan `HANDOFF.md` §3 ve `docs/plans/plan_*.md` referansından planı okuyup doğrudan Faz 1'den yürütmeyi başlatır.

### Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: 2-Modlu Plan Onay Kapısı (/seal-plan vs Proceed)
  Scenario: Kullanıcı planı kodlamadan yalnızca yapıya mühürlemek ister
    Given Bir projede "/plan" ile uygulama planı artifact'ı hazırlanmıştır
    When Kullanıcı "/seal-plan" veya "planı mühürle, kodlama yapma" der
    Then Ajan "archive_plan.py" ile planı "docs/plans/" altına arşivler
    And Görevleri "HANDOFF.md" §3 Gelecek Fazlar / Sıradaki İşler panosuna ve "KANBAN.md" Bekliyor sütununa işler
    And Varsa kardeş uygulamanın "HANDOFF.md" dosyasına plan referansını yazar
    And Üretim kodunda ("src/**", migration vb.) tek bir satır dahi değiştirmeden durur
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar
- **Tek yol / Konsey eşiği altında:** Yeni skill klasörü açmadan mevcut `/plan` ansamble protokolünün içine **Faz 0-Only (`/seal-plan`)** modu ve `check_handoff.py` W3 regresyon testi eklenmektedir.

---

## 3. User Review Required & 4. Open Questions
> [!IMPORTANT]
> **Onay Bekleyen Karar:**
> 1. Bu 2-Modlu Onay Kapısını (`/seal-plan` — Mühürle & Sıraya Al) `skillSetWorks` kurallarına, `PLAN.template.md` şablonuna, kataloğa (`v1.39.0`) ve 4 hedef projeye ekleyelim mi?

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu

| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / Modül |
|---|---|---|---|
| `GSW-PLAN-003` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3) | `tests/test_check_handoff.py` (Gelecek Fazlar'da mühürlenen plan için `W3` 0 uyarı doğrulaması) |
| `GSW-PLAN-004` | `Bekliyor` | `Bekliyor` | `development-workflow.md`, `sprint-delivery-workflow.md`, `handoff-session-continuity.md`, `AGENTS.md`, `PLAN.template.md`, `skill-trigger-routing.md`, `generate_skills_catalog.py` & `delivery.py` |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- `Tek Repo / Kardeş Uygulama Etkisi Yok` *(Kuralın kendisi hedef projelerde kardeş repo `HANDOFF.md`'sinin de `/seal-plan` anında mühürlenmesini güvenceye alır.)*

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim & Proposed Changes

- #### [MODIFY] `.agent/rules/development-workflow.md` (Adım 2.2 — `2-Modlu Plan Onay Kapısı: /seal-plan vs Proceed`)
- #### [MODIFY] `.agent/rules/sprint-delivery-workflow.md` (§2.1.1 — `Mühürle & Sıraya Al` akışı)
- #### [MODIFY] `.agent/rules/handoff-session-continuity.md` (`Gelecek Fazlar` tablosuna mühürlenen ertelenmiş planların sonradan tetiklenmesi)
- #### [MODIFY] `.agent/AGENTS.md` (§4 `/plan` ve `/seal-plan` özeti)
- #### [MODIFY] `.agent/templates/PLAN.template.md` (Plan sonuna `Onay Seçenekleri: [Seçenek A: /seal-plan (Mühürle, Kodlama Yapma)] vs [Seçenek B: Proceed (Onayla & Başla)]` bloğu)
- #### [MODIFY] `.agent/rules/skill-trigger-routing.md`, `scripts/generate_skills_catalog.py`, `.agent/skills-catalog.html` (`/seal-plan` komutu & `/plan` açıklaması)
- #### [MODIFY] `tests/test_check_handoff.py` (Gelecek Fazlar tablosunda plan ID'leri olan ertelenmiş planın `W3` uyarısı üretmediğini doğrulayan regresyon testi)

---

## 7. Verification Plan
```bash
python tests/test_check_handoff.py
python tests/test_skills_catalog.py
python .agent/skills/musgoku/scripts/run_all_gates.py
python tests/run_all.py
python delivery.py --keep 1 && python delivery.py --verify
```
