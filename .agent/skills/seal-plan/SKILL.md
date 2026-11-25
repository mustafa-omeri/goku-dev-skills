---
name: seal-plan
description: Planı kod yazmadan çakışma kalkanından geçirip backlog'a mühürler ve HANDOFF, KANBAN ile kardeş süreçleri günceller. Tetikleyiciler: "/seal-plan", "seal plan", "planı mühürle", "mühürle", "todo olarak ekle", "listeye ekle", "sıraya al", "backlog'a al", "add to backlog". Tetiklenmez: hemen kodlama başlatan Proceed onayları musgoku kapsamındadır. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Seal Plan — Kodlamadan Backlog'a Mühürleme Orkestratörü (`/seal-plan`)

Bu yetenek, `/plan` veya `/council` sonrası üretilen fiziksel `.md` planını **tek satır üretim kodu yazmadan** ön-mühürleme çakışma taramasından geçirir, `docs/plans/` altına arşivler ve `HANDOFF.md` + `KANBAN.md` + `SPRINT_PLAN.md` + `RELEASE_PLAN.md` (varsa kardeş proje süreçleri) backlog'una `⬜ Bekliyor` olarak mühürler.

## Bağlı Kurallar ve Araçlar

- **Kurallar:** `.agent/rules/development-workflow.md` (§2.2 Mod A), `.agent/rules/handoff-session-continuity.md`, `.agent/rules/sprint-delivery-workflow.md` (§2.1.1)
- **Ön-Mühürleme Çakışma Kalkanı:** `.agent/skills/musgoku/scripts/plan_conflict_guard.py`
- **Arşivleyici & Mühürleyici:** `.agent/skills/musgoku/scripts/archive_plan.py`
- **Kardeş Süreç Senkronu:** `.agent/skills/musgoku/scripts/sync_sibling_handoff.py`

## Zorunlu İcra Akışı (Mod A — Kodlama Yapma)

1. **Ön-Mühürleme Çakışma & Ezme Taraması (`plan_conflict_guard.py`):**
   - Canlı kodda tekrar (`ALREADY_DONE_EXACT` / `ENRICHED_SUPERSET` / `SIMPLIFIED_SUBSET_REGRESSION`) ve bekleyen sıralı planlar arası ezme (`DOUBLE_NEW_COLLISION` / `SHARED_SURFACE_OVERWRITE`) taraması yapılır:
   ```bash
   python .agent/skills/musgoku/scripts/plan_conflict_guard.py --root . --plan <plan-yolu>
   ```
   - `CRITICAL` bulguda dur; yalnızca kullanıcı açıkça onaylarsa `--allow-conflicts` ekle.
2. **Arşivleme ve `HANDOFF.md` §3 Mühürleme (`archive_plan.py --seal-handoff`):**
   ```bash
   python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug <slug> --seal-handoff --sprint-label "<Sprint>"
   ```
   - UI planında kasıtlı wireframe istisnası gerekiyorsa `--allow-no-wireframe` ekle.
3. **Sprint Tahtası & Kardeş Proje Backlog Senkronu:**
   - Proje sprint açmışsa (`KANBAN.md` / `SPRINT_PLAN.md` / `RELEASE_PLAN.md`), yeni kartı `Bekliyor` sütununa (`durum: Bekliyor`) işle; `SPRINT_PLAN.md` ve `RELEASE_PLAN.md` eşlemesini tamamla.
   - Kardeş repo gereksinimi varsa:
   ```bash
   python .agent/skills/musgoku/scripts/sync_sibling_handoff.py --sibling-root <kardeş-yol> --source-root . --plan <arşivli-plan-yolu> --task-id <ID> --task-title "<Başlık>" --summary "<Özet>"
   ```
4. **Doğrulama ve Temiz Durma (Tek Satır Üretim Kodu Yazılmaz):**
   ```bash
   python .agent/skills/musgoku/scripts/check_handoff.py
   python .agent/skills/musgoku/scripts/check_sprint_board.py
   ```
   - `0` hata alındıktan sonra arşiv/pano dosya bağlantılarını raporla ve dur.
