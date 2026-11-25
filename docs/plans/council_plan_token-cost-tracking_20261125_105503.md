# Görev ve Sprint Bazlı Multi-IDE Token / Maliyet Takibi (`GSW-FEAT-023`)

> **Hedef Dal / Sürüm:** `main / v1.48.0 (Planlandı — Bekliyor)` · **Tarih:** `2026-11-25`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `council`, `karpathy-guidelines`, `doc-coauthoring`, `musgoku`, `tdd`  
> **Kullanılan MCP'ler:** `second-brain-vault`, `sequential-thinking`  
> **İlgili KANBAN Kartı:** `S2-23` (`GSW-FEAT-023` — `Bekliyor`)  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Cursor`

---

## 1. [Goal Description] (Amaç & Kapsam)

Her görev tamamlandığında o işin gerçek girdi (`input_tokens`), önbellek okuma (`cache_read_tokens`), çıktı (`output_tokens`) ve hesaplanmış maliyetini görüntüleyip proje dosyalarına kaydetmek; sprint kapandığında ise tüm sprint toplamını ve madde (`KANBAN.md` kartı) bazlı token/maliyet dökümünü deterministik olarak hesaplayıp eklemek.

### Onaylanan Kullanıcı Kararları (2026-11-25)

1. **Git İzleme:** Ham telemetri ve attribution defteri (`.agent/metrics/token_ledger.json`) **git içinde tutulacak** (projeler arası ortak geçmiş ve audit izi için `.gitignore` edilmeyecek).
2. **Çoklu IDE / CLI Kapsamı (`Hepsi İçin`):** Tek araca kilitlenilmeyecek; `token_ledger.py` modüler adaptörlerle **Antigravity CLI/IDE** (`transcript.jsonl` + `invoke_subagent` alt konuşmaları), **Claude Code** (`~/.claude/projects/**/*.jsonl`) ve **OpenCode** (yerel oturum veritabanı/JSON kayıtları) telemetrisini okuyacak; **Cursor** veya telemetri sunmayan ortamlarda ise tahmin yürütmeden `TELEMETRY_UNAVAILABLE` durumunu kaydedecek.
3. **Sıfır Tahmin & Son-Dönüş Gerçeği:** Ajanın elle token uydurması yasaktır. Antigravity'de yanıt bitmeden son dönüşün `output_tokens`'ı henüz `transcript.jsonl`'e yazılmadığı için görev kapanışında `measured_so_far` etiketi kullanılır; sonraki turda veya sprint kapanışında konuşma yeniden okunarak kesinleşen final değerle güncellenir (reconciliation).

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)

```gherkin
Feature: Görev ve Sprint Bazlı Multi-IDE Telemetriyle Token Takibi
  Scenario: Antigravity oturumunda tamamlanan görev için token kaydı
    Given aktif konuşma için step bazlı input_tokens, cache_read_tokens ve output_tokens içeren transcript.jsonl mevcuttur
    When "python .agent/skills/musgoku/scripts/token_ledger.py record --task GSW-FEAT-023 --card S2-23" çalıştırılır
    Then script üst konuşma ve invoke_subagent alt konuşmalarını okuyarak gerçek toplamları git-takipli .agent/metrics/token_ledger.json dosyasına kaydeder
    And henüz diske yazılmamış son dönüş için tahmin üretmez, "measured_so_far" sınırını açıkça etiketler

  Scenario: Claude Code veya OpenCode yerel oturumundan token kaydı
    Given ortamda Claude Code JSONL veya OpenCode yerel oturum verisi mevcuttur
    When "python .agent/skills/musgoku/scripts/token_ledger.py record --provider auto --task GSW-FEAT-023" çalıştırılır
    Then uygun adaptör oturumdaki gerçek token toplamlarını ayrıştırır ve aynı standart şemayla .agent/metrics/token_ledger.json içine yazar

  Scenario: Telemetri sunmayan IDE (Cursor vb.) ortamında güvenli geri çekiliş
    Given ortamda yerel token telemetri logu bulunmamaktadır
    When token_ledger.py record çalıştırılır
    Then araç exit 0 ile "TELEMETRY_UNAVAILABLE" kaydı düşer ve check_sprint_board.py ile check_handoff.py kapılarını kırmaz

  Scenario: Sprint kapanışında madde bazlı ve toplam maliyet özeti
    Given sprint boyunca kart ID'lerine bağlanmış kayıtlar .agent/metrics/token_ledger.json içinde birikmiştir
    When "python .agent/skills/musgoku/scripts/token_ledger.py sprint-summary --sprint S2 --write-sprint-plan" çalıştırılır
    Then sprint içindeki her maddenin token/maliyet kırılımı ve genel toplamı SPRINT_PLAN.md içine deterministik olarak işlenir
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (3 Aşamalı Kör Hakemlik)

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Sıfır-Script Markdown)** | Ajanın elle `token_maliyeti` yazması. | Sıfır Python kodu. | LLM kendi tokenını göremediği için %100 halüsinasyon üretir. | `2.67` |
| **Option B (Zorunlu Exit-1 Kapılı Motor)** | Tüm IDE'ler + `check_sprint_board.py` içinde `exit 1` kilidi. | Sıkı zorunluluk. | Cursor'ı, mevcut `Yapıldı` kartlarını ve son-dönüş akışını deadlock ile kilitler. | `2.33` |
| **Option C (Telemetri-Öncelikli Opt-In Defter + Dürüst `UNAVAILABLE`)** | Odaklı tek script (`token_ledger.py`), çoklu IDE adaptörleri (Antigravity, Claude Code, OpenCode), sıfır tahmin, opsiyonel fiyatlandırma, non-blocking kapı uyumu. | Sıfır halüsinasyon, geriye tam uyumlu, son-dönüş paradoksunu `measured_so_far` + sprint-sonu mutabakatla çözer. | Cursor gibi telemetrisiz araçlarda `TELEMETRY_UNAVAILABLE` yazar; görev adımı sınırı işaretlemesi ister. | **`1.00`** |

- **Seçilen Yol & Gerekçe:** 3 kör hakemin tamamı (`16d0c485`, `1482a075`, `246e58bf`) ve `council_ranker.py` konsensüsüyle **Option C** (`1.00`, 3/3 birincilik) seçildi. Kullanıcı kararıyla `.agent/metrics/token_ledger.json` git'te tutulacak ve çoklu-IDE adaptörleri (`antigravity`, `claude-code`, `opencode`, fallback `unavailable`) kapsama alınacaktır.
- **Birleşik Planlama Ekosistemi Bağlantısı:** Fikir (`my-idea`) -> Şartname (`doc-coauthoring`) -> Konsey Hakemliği (`council`) -> Görev Kartı (`KANBAN.md`) -> TDD Dikiş Noktası (`development-workflow.md` Adım 2.2).

---

## 3. User Review Required (Kullanıcı İncelemesi & Mühürleme Durumu)

> [!NOTE]
> **Mühürleme Modu (Mod A — `/seal-plan` / `"mühürle, kodlama yapma"`):**
> Kullanıcı `1. git'de tutulsun` ve `2. hepsi için olsun` kararlarını verip **Mod A (Kodlamadan Mühürle)** talimatını seçti. Bu plan `docs/plans/` altına arşivlenir; `HANDOFF.md`, `KANBAN.md`, `SPRINT_PLAN.md` ve `RELEASE_PLAN.md` backlog'una alınır; kullanıcı `"GSW-FEAT-023'ü başlat"` diyene kadar üretim kodu yazılmaz.

## 4. Open Questions (Açık Sorular)

Açık soru bulunmamaktadır; tüm kararlar kullanıcı tarafından netleştirilmiştir.

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)

| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Mühür Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-FEAT-023` | `Bekliyor` | `⬜ Bekliyor` (`HANDOFF.md` §3 Gelecek Fazlar + `KANBAN.md` `Bekliyor`) | `S2-23 · Multi-IDE Token/Maliyet Telemetri Defteri & Sprint Özeti` |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği

Tek Repo / Kardeş Uygulama Etkisi Yok (yalnızca `skillSetWorks` dağıtım katmanı `delivery.py` ve `sync_agy_global.py` üzerinden hedef projelere script/şablon olarak dağıtılır).

### 5.2 🛡️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Matrisi (Pre-Seal Conflict Check)

| Hedef / Yüzey | Sınıflandırma | İlgili Canlı Dosya / Bekleyen Plan | Alınacak Önlem |
|---|---|---|---|
| `.agent/skills/musgoku/scripts/token_ledger.py` | `NEW_CLEAN` | Yok | Saf Python 3.11 stdlib (`json`, `sqlite3`, `pathlib`, `argparse`) |
| `.agent/templates/HANDOFF.template.md`, `SPRINT_PLAN.template.md` | `MODIFY_CLEAN` | Mevcut şablonlar | Opsiyonel `Token & Maliyet Özeti` bölümü eklenir |
| `.agent/skills/musgoku/scripts/check_sprint_board.py` | `NO_BREAKING_CHANGE` | Mevcut 7 zorunlu alan | Mevcut `REQUIRED_FIELDS` korunur, legacy kartlar bozulmaz |

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Salt CLI / Kural Aracı)

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | Git-takipli JSON defter ve opsiyonel fiyatlandırma sözleşmesi | `.agent/metrics/token_ledger.json`, `.agent/metrics/model_pricing.json` |
| **2. Backend / Parser / CLI** | `antigravity`, `claude-code`, `opencode` adaptörleri + `invoke_subagent` özyineleme + `reconcile` + `sprint-summary` | `.agent/skills/musgoku/scripts/token_ledger.py` |
| **3. İstemci / Kural Entegrasyonu** | `HANDOFF.template.md`, `SPRINT_PLAN.template.md`, `knowledge-base-management.md` entegrasyonu | `.agent/templates/*.template.md`, `.agent/rules/knowledge-base-management.md` |
| **4. UI / UX & Eylemler** | Salt CLI / Markdown çıktı (Türkçe + `/caveman` kompakt maliyet tablosu) | Terminal & Markdown özeti |
| **5. Döngü Kapanışı** | `delivery.py` + `sync_agy_global.py` dağıtım uyumu & `tests/test_token_ledger.py` doğrulama paketi | `delivery.py`, `tests/test_token_ledger.py` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi

Tier 0: Salt Backend / CLI & Kural Aracı (UI Kapsam Dışı).

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Mühürleme (`docs/plans/`, `HANDOFF.md` §3, `KANBAN.md`)
1. **[Adım 1 - Ön-Mühürleme Çakışma & Arşivleme]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug token-cost-tracking --prefix council_plan --seal-handoff --sprint-label "S2 Backlog"` -> **Beklenen Çıktı:** `docs/plans/council_plan_token-cost-tracking_<TIMESTAMP>.md` arşivlenir ve `GSW-FEAT-023` `HANDOFF.md` §3 Gelecek Fazlar'a `⬜ Bekliyor` olarak işlenir.
2. **[Adım 2 - Sprint Tahtası Backlog Kaydı]:** `KANBAN.md` (`Bekliyor` sütunu `S2-23`), `SPRINT_PLAN.md` (`Kapsam Dışı`) ve `RELEASE_PLAN.md` (`Taşınan Açık İşler`) güncellenir -> **Beklenen Çıktı:** `check_sprint_board.py` ve `check_handoff.py` `0 hata` döner.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop — Tetiklendiğinde)
1. **[Adım 1 - Kırmızı Test Yaz & Koştur]:** `tests/test_token_ledger.py` içinde Antigravity (`transcript.jsonl` + `invoke_subagent`), Claude Code (`.jsonl`), OpenCode (SQLite/JSON), `TELEMETRY_UNAVAILABLE`, `measured_so_far` mutabakatı ve `sprint-summary` testlerini yazıp `python -m unittest tests/test_token_ledger.py -v` çalıştır -> **Beklenen Çıktı:** Testler **KIRMIZI (FAIL)** döner.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop — Tetiklendiğinde)
1. **[Adım 1 - `token_ledger.py` Yaz & Test Et]:** `.agent/skills/musgoku/scripts/token_ledger.py` içinde adaptörleri ve `record` / `reconcile` / `sprint-summary` alt komutlarını implemente edip `python -m unittest tests/test_token_ledger.py -v` çalıştır -> **Beklenen Çıktı:** Tüm testler **YEŞİL (PASS)** döner.

### 🧩 Faz 3: Şablon, Kural & Dağıtım Entegrasyonu (Tetiklendiğinde)
1. **[Adım 1 - Şablon & Kural Entegrasyonu]:** `.agent/templates/HANDOFF.template.md`, `.agent/templates/SPRINT_PLAN.template.md` ve `.agent/rules/knowledge-base-management.md` güncellenir -> **Beklenen Çıktı:** `check_sprint_board.py`, `check_handoff.py` ve `rules_gates.py --strict` yeşil geçer.

### 🧹 Faz 4: Refactor, Kapılar & Kapanış (Tetiklendiğinde)
1. **[Adım 1 - Tüm Kapıları Koştur]:** `python .agent/skills/musgoku/scripts/run_all_gates.py` ve `python tests/run_all.py` çalıştır -> **Beklenen Çıktı:** Tüm test paketleri ve kapılar `[OK]` döner.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### Telemetri & Defter Motoru
#### [NEW] `.agent/skills/musgoku/scripts/token_ledger.py`
- Multi-IDE adaptörleri (`AntigravityAdapter`, `ClaudeCodeAdapter`, `OpenCodeAdapter`, `UnavailableAdapter`), `invoke_subagent` alt konuşma toplayıcısı, git-takipli `.agent/metrics/token_ledger.json` okuyucu/yazıcısı, opsiyonel `.agent/metrics/model_pricing.json` maliyet hesaplayıcısı ve `HANDOFF.md` / `SPRINT_PLAN.md` özet üreteci.

#### [NEW] `tests/test_token_ledger.py`
- Antigravity + alt ajan, Claude Code, OpenCode, `TELEMETRY_UNAVAILABLE`, `reconcile` ve `sprint-summary` regresyon testleri.

### Şablon ve Kurallar
#### [MODIFY] `.agent/templates/HANDOFF.template.md`
- `§2 Güncellik Kanıtı` altına opsiyonel telemetri tablosu/özeti alanı eklenmesi.

#### [MODIFY] `.agent/templates/SPRINT_PLAN.template.md`
- Sprint sonu `## Token & Maliyet Özeti` (toplam + madde bazlı kırılım) bölümünün eklenmesi.

#### [MODIFY] `.agent/rules/knowledge-base-management.md`
- Görev/sprint kapanışında `token_ledger.py` çağrısı ve sıfır-tahmin kuralının tanımlanması.

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests
```bash
python -m unittest tests/test_token_ledger.py -v
python .agent/skills/musgoku/scripts/run_all_gates.py
python tests/run_all.py
```

### Manual Verification (FAA AC 121-24C)
1. **[Adım 1 - Görev Kaydı]:** `python .agent/skills/musgoku/scripts/token_ledger.py record --task GSW-FEAT-023 --card S2-23` -> **Beklenen Çıktı:** Gerçek `input / cache_read / output` toplamları basılır ve `.agent/metrics/token_ledger.json` güncellenir.
2. **[Adım 2 - Sprint Özeti]:** `python .agent/skills/musgoku/scripts/token_ledger.py sprint-summary --sprint S2 --write-sprint-plan` -> **Beklenen Çıktı:** `SPRINT_PLAN.md` içinde sprint toplamı ve her maddenin ayrı maliyeti listelenir.

---

## 11. 🚨 Ditching & Emergency Exit (Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `TELEMETRY_UNAVAILABLE` dönüyor | Cursor veya telemetri logu üretmeyen bir araç kullanılıyor | Normal çalışma devam eder; ek kaynak varsa `--transcript <yol>` ile gösterin |
| Aynı oturumdaki iki işin tokenı birleşiyor | Adım aralığı belirtilmemiş | `record --from-step <N>` ile görevin başlangıç adımını ayırın |
| Eski projelerde `check_sprint_board.py` kırılıyor | Yeni alan zorunlu işaretlenmiş | Token bölümünü zorunlu değil opsiyonel tutun (`check_sprint_board.py` sözleşmesini koruyun) |
