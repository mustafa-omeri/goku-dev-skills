# 🔭 Scout & Council İnceleme Planı: 6 Popüler AI Code Review & Mühendislik Skill Deposu

> **Hedef Dal / Sürüm:** `main` / `goku-dev-skills v1.42.0 -> v1.43.0` · **Tarih:** `2026-11-23`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `council`, `karpathy-guidelines`, `code-review`, `tdd`, `verify-last`, `musgoku`, `doc-coauthoring`  
> **Kullanılan MCP'ler:** `second-brain-vault`, `sequential-thinking`  
> **İlgili KANBAN Kartı:** `GSW-SCOUT-028..033` (Yeni Scout & Kalite Kapısı Dilimi)  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. [Goal Description] (Amaç & Kapsam)

Kullanıcının paylaştığı 6 yüksek popülariteli AI ajan / kod inceleme deposunun (`obra/superpowers`, `mattpocock/skills`, `addyosmani/agent-skills`, `The-PR-Agent/pr-agent`, `awesome-skills/code-review-skill`, `alibaba/open-code-review`) `scout/engine.py` parmak izi + doğrudan kaynak dosya okumaları üzerinden mevcut `.agent/` (`skillSetWorks`) yapısıyla kıyaslanması; çakışmaların elenmesi, benzersiz mühendislik katma değerlerinin Borda Konsey hakemliğiyle seçilip sıfır şişkinlik (zero-bloat) ve sıfır dış-runtime ilkesiyle `scout/` kataloğuna ve `.agent/skills/` ekosistemine cerrahi olarak entegre edilmesidir.

### 1.1. 6 Depo Scout Delta Matrisi (Kanıtlı Karşılaştırma)

| # | Depo & Katman | Parmak İzi (Ölçülen) | `skillSetWorks` Mevcut Karşılığı | Tespit Edilen Gerçek Delta (Bizde Eksik Olan) | Scout Kararı |
|---|---|---|---|---|---|
| 1 | **`obra/superpowers`** (`Tooling / Agentic`) | 230 dosya · 1.55 MB (`skills/`, `hooks/`, `tests/antigravity/`) | `development-workflow.md`, `tdd`, `diagnosing-bugs`, `verify-last`, `git-release-workflow`, `council` (5-Katmanlı Dikey Dilim & Python kapılarımız daha sıkı) | 1) **`receiving-code-review`**: Dış/hakem geri bildirimine karşı yaranmacılık-karşıtı teknik doğrulama + geri itme (`pushback`) protokolü.<br>2) **`verification-before-completion` (Iron Law)**: Taze komut çıktısı olmadan başarı beyanı yasağı, "Fix'i geri al -> kırmızı gör -> geri koy" regresyon ispatı, rasyonalizasyon önleme tablosu.<br>3) **`subagent-driven-development`**: Görev başına model kademelendirme (`fast` mekanik / `top` final review & stuck loop). | **`KISMEN_ALINABILIR`** (`PLANNED` -> `TRANSFERRED`) |
| 2 | **`mattpocock/skills`** (`Tooling / Agentic`) | 180 dosya · 780 KB (`skills/engineering/`, `skills/productivity/`) | `code-review` (birebir 2 eksenli Standards+Spec + Fowler smells), `tdd`, `codebase-design`, `domain-modeling`, `diagnosing-bugs`, `/grill-me` zaten bizde var | Çekirdek yapılarımız zaten daha kapsamlı ve kapılı (`run_all_gates.py`, 5 katman, Ponytail 5.3); doğrudan ekleme yapılmaz.<br>*(Not: `scout/plans/skills.md` zaten `jakubkrehel/skills` için kullanıldığından plan dosyası `plans/mattpocock-skills.md` olmalıdır — `E5_COLLIDING_PLAN_FILE` önlemi).* | **`BIZ_DAHA_IYIYIZ` (`REJECTED`)** |
| 3 | **`addyosmani/agent-skills`** (`Frontend + Tooling`) | 260 dosya · 1.22 MB (`skills/`, `agents/`, `commands/`, `evals/`) | `code-review`, `security-audit`, `prelaunch-audit`, `react-best-practices`, `musgoku` | 1) **`code-review-and-quality`**: Değişiklik boyutu eşiği (`~100 / ~300 / ~1000` + toplam dosya sınırı), **Mutasyon Testi Doğrulaması** (bir koşulu ters çevir, suite koştur, yeşil kalırsa bulgu!), **Structural Remedies & Presumptive Blockers**, **Bağımlılık Yükseltme Hijyeni** (tek paket + changelog + lockfile diff).<br>2) **`doubt-driven-development`**: Kör-bağlam adversarial doğrulama (`ARTIFACT + CONTRACT` ver, `CLAIM` verme!) + yüksek riskte cross-model ikinci görüş teklifi.<br>3) **`constraint-driven-development`**: Diff'te sessiz zemin düşürme avı (yeni `@ts-ignore`, `eslint-disable`, `# noqa`, `# type: ignore`, silinen/skip test, stub `throw NotImplemented`). | **`ZENGINLESTIR`** (`PLANNED` -> `TRANSFERRED`) |
| 4 | **`awesome-skills/code-review-skill`** (`Tooling / Agentic`) | 50 dosya · 827 KB (`SKILL.md`, 24 dil kılavuzu ~21k satır, `scripts/pr-analyzer.py`) | `musgoku/references/` (Java/Spring, React/TS), `security-audit`, `code-review` | 1) **`scripts/pr-analyzer.py`**: Sıfır bağımlılıklı Python diff karmaşıklık/boyut (`XS..XL`), tahmini review süresi ve otomatik risk sinyali (`NO_TEST_CHANGES`, `<20%` test oranı, security/migration/config dosya tespiti).<br>2) **`code-quality-universal.md`**: TOCTOU yarış koşulu, no-op state update, parameter sprawl (`>=4` arg), stringly-typed enum eksikleri.<br>*(21.000 satır statik dil markdown'ı token şişkinliği nedeniyle elenir).* | **`KISMEN_ALINABILIR`** (`PLANNED` -> `TRANSFERRED`) |
| 5 | **`alibaba/open-code-review`** (`Frontend + Backend Go + Tooling`) | 1.295 dosya · 17.5 MB (Go `ocr` CLI, `skills/open-code-review-delegate/`) | `code-review`, `run_all_gates.py` (Ancak bizde dosya kapsam muhasebesi ve diff manifest mekanizması yok) | 1) **Deterministik Mühendislik × Ajan Hibriti**: LLM'in büyük diff'te dosya atlamasını ("cutting corners") engelleyen **Kapsam Muhasebesi (`total_files`, `reviewed_files`, `skipped_files` + sebep, `coverage_rate`)**.<br>2) **Akıllı Dosya Demetleme (Smart Bundling)**: İlişkili dosyaları (`tr.json` + `en.json` i18n çifti, kod + test dosyası) aynı inceleme birimine bağlama.<br>3) **Davranışsal Etki Analizi (Behavior/Workflow Impact)**: Sıfır hata olsa bile arayüz/flag/silinen dosya kaynaklı workflow değişimini ayrı raporlama.<br>*(Go CLI zorunlu yapılmaz; desenler saf Python stdlib script'e uyarlanır).* | **`KISMEN_ALINABILIR`** (`PLANNED` -> `TRANSFERRED`) |
| 6 | **`The-PR-Agent/pr-agent`** (`Frontend + Backend Python + Tooling`) | 816 dosya · 16.3 MB (FastAPI/Docker/Lambda/Webhook botu) | Lokal CLI/IDE ajan orkestratörü (`.agent/`); CI PR botu kapsam dışıdır | Kod ajanı `.agent/` skill mimarisi için fazla ağır ve sunucu/webhook tabanlıdır. Yalnız **GitHub Actions üzerinde harici PR botu** istenirse opsiyonel CI referansı olur; `.agent/` içine aktarılmaz. | **`BIZ_DAHA_IYIYIZ` / Kapsam Dışı (`REJECTED`)** |

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)

```gherkin
Feature: 6 Popüler AI Code Review Deposunun Scout & Cerrahi Skill Entegrasyonu
  Scenario: Sıfır Dış Bağımlılıkla Deterministik Diff Triajı ve Kapsam Muhasebesi
    Given geliştirici çalışma ağacında veya branch diff'inde kod değişikliği yapmıştır
    When `python .agent/skills/code-review/scripts/diff_triage.py` çalıştırıldığında
    Then boyut/karmaşıklık skoru, i18n+test dosya demetleri, kapsanacak dosya manifesti ve zemin ihlalleri (`@ts-ignore`, `eslint-disable`, `pytest.mark.skip`, stub) deterministik JSON/özet olarak raporlanır

  Scenario: Scout Katalog ve Kalite Kapılarının Tam Paritesi
    Given 6 repo `scout/repos.json` ve `scout/plans/` altına kaydedilmiştir
    When `python scout/check_scout_integration.py --strict` ve `python tests/run_all.py` çalıştırıldığında
    Then 0 hata, 0 uyarı ve %100 test başarısı döner
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (3 Aşamalı Kör Hakemlik)

`karpathy-guidelines/scripts/council_ranker.py` ile 4 bağımsız perspektif (`Judge_Arch`, `Judge_QA`, `Judge_PO`, `Judge_Simplicity`) üzerinden körleştirilmiş değerlendirme çalıştırıldı:

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Ortalama Derece (1 = En İyi) |
|---|---|---|---|:---:|
| **Option A (Yalın Markdown)** | Sadece seçili kavramları `code-review/references/` altına Markdown notu olarak ekle, script yazma | Sıfır kod bakım maliyeti, hızlı teslim | LLM büyük diff'te dosya atlamaya ve `@ts-ignore`/stub zemin düşürmesini kaçırmaya devam eder | `1.75` (1 birincilik) |
| **Option B (Cerrahi Hibrit — KAZANAN)** | `scout/` kaydı + saf Python stdlib `diff_triage.py` (triage + manifest/demetleme + floor-weakening lint) + 3 hedefli Markdown referansı (`code-review`, `verify-last`, `karpathy-guidelines`/`tdd`) | Deterministik kapsam garantisi, sıfır dış binary/API bağımlılığı, `delivery.py` ile tüm projelere taşınabilirlik | 1 yeni Python modülü + birim test bakımı | **`1.25` (3 birincilik)** |
| **Option C (Ağır Dış CLI & Tam Paket)** | Go `ocr` CLI + Python `pr-agent` + 21k satır dil rehberini doğrudan bağımlılık yap | Hazır harici motorlar | `delivery.py` / `npx` taşınabilirliği bozulur, token şişkinliği ve harici API key zorunluluğu doğar | `3.00` (0 birincilik) |

- **Seçilen Yol & Gerekçe:** **Option B (Cerrahi Hibrit)** seçildi (`1.25` ortalama derece). `alibaba/open-code-review`'in kapsama/demetleme disiplinini, `awesome-skills`'in karmaşıklık triajını ve `addyosmani`'nin zemin korumasını tek bir sıfır-bağımlılıklı Python stdlib aracında (`diff_triage.py`) birleştirir; `obra/superpowers` ve `addyosmani` protokollerini ise şişkinlik yaratmadan mevcut skill referanslarına işler. `Option C` aşırı karmaşıklık ve taşınabilirlik kaybı nedeniyle elendi.
- **Birleşik Planlama Ekosistemi Bağlantısı:** Dış Repo Keşfi (`scout/engine.py`) → Konsey Hakemliği (`council_ranker.py`) → Görev Tahtası (`KANBAN.md`) → TDD Dikiş Noktası (`tests/test_diff_triage.py` & `tests/test_scout_integration.py`) → Kapı Doğrulaması (`check_scout_integration.py` & `rules_gates.py`).

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)
> [!IMPORTANT]
> **Kullanıcı Onayı Alındı (2026-11-23 — `Proceed`):**
> 1. `mattpocock/skills` -> **`REJECTED` (`BIZ_DAHA_IYIYIZ`)** (ekleme yapılmaz).
> 2. `The-PR-Agent/pr-agent` -> **`REJECTED` (`BIZ_DAHA_IYIYIZ` / Harici CI Botu)** (ekleme yapılmaz).
> 3. **Çekirdek İlke:** Hiçbir dış repo doğrudan eklenmez; yalnız seçili 4 repodan (`obra/superpowers`, `addyosmani/agent-skills`, `awesome-skills/code-review-skill`, `alibaba/open-code-review`) cerrahi kavramlar ve saf Python stdlib `diff_triage.py` motoru çıkarılarak mevcut `.agent/skills/` zenginleştirilir.

## 4. Open Questions (Açık Sorular)
Açık soru bulunmamaktadır (Kullanıcı 1 ve 2. kararları netleştirip `proceed` verdi).

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)

| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-SCOUT-028` | `Bekliyor` | `Yapılıyor` (`WIP 1/3`) | `diff_triage.py` (Python stdlib: Diff Triage + Coverage Manifest + Smart Bundling + Floor-Weakening Scan) + `test_diff_triage.py` |
| `GSW-SCOUT-029` | `Bekliyor` | `Yapılıyor` (`WIP 2/3`) | `code-review` + `karpathy-guidelines` + `verify-last` + `tdd` cerrahi referans aktarımları (`receiving-code-review`, `verification-iron-law`, `doubt-driven`, `structural-remedies`, `transferred_*.md`) |
| `GSW-SCOUT-030` | `Bekliyor` | `Yapılıyor` (`WIP 3/3`) | 6 Repo için `scout/plans/*.md` + `scout/repos.json` + `scout-catalog.html` güncellemesi & `check_scout_integration.py --strict` / `rules_gates.py` / `tests/run_all.py` doğrulaması |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- **Tek Repo / Kardeş Uygulama Etkisi Yok** (`skillSetWorks` çekirdek skill/kural deposudur; bu değişiklikler onay ve doğrulama sonrasında kullanıcı isterse `delivery.py` ile hedef projelere dağıtılabilir).

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (`skillSetWorks` Tooling Uyarlaması)

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. Veri / Envanter Şeması** | 6 repo kaydını (canonical key, unique `plan_file`, `target_skill`, `transferred_to`, `history`) ekle | `scout/repos.json`, `scout/plans/{superpowers,mattpocock-skills,agent-skills,code-review-skill,open-code-review,pr-agent}.md` |
| **2. Python Motor / Analiz Katmanı** | Saf stdlib diff triaj, dosya manifesti, i18n/test demetleme ve zemin düşürme tarayıcısı | `.agent/skills/code-review/scripts/diff_triage.py` |
| **3. Skill & Kural Sözleşmesi** | İlgili skill gövdelerini ve aktarım referanslarını bağla | `.agent/skills/code-review/{SKILL.md,references/transferred_*.md}`, `.agent/skills/verify-last/SKILL.md`, `.agent/skills/karpathy-guidelines/SKILL.md`, `.agent/skills/tdd/SKILL.md` |
| **4. Katalog & Arayüz Çıktısı** | Scout HTML kataloğunu ve gerekirse skill kataloğunu yeniden derle | `scout/scout-catalog.html` (`python scout/generate_scout_catalog.py`) |
| **5. Döngü Kapanışı & Kapılar** | Tüm entegrasyon, parite ve regresyon testlerini koştur; `HANDOFF.md` + `knowledge-base.md` + `KULLANICI_TEST_REHBERI.md` güncelle | `scout/check_scout_integration.py --strict`, `rules_gates.py --strict`, `tests/run_all.py` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi (Theme & Component Skeleton Contract)
- **Salt Backend / CLI & Tooling — UI Kapsam Dışı:** Yeni kullanıcı arayüzü bileşeni geliştirilmeyecektir; mevcut `scout/scout-catalog.html` derleme şablonu korunur.

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 & Sprint Açılışı)
1. **[Adım 1 - Planı Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan "<plan-yolu>" --slug "scout-code-review-repos"` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_scout-code-review-repos_<YYYYMMDD_HHMMSS>.md`
2. **[Adım 2 - `HANDOFF.md` §3 & `KANBAN.md` İşle]:** `GSW-SCOUT-028..030` kartlarını arşivlenen plan referansıyla `HANDOFF.md` §3 ve `KANBAN.md` içine işle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0 hata, 0 W3 uyarısı` döner.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
- **Seam (`analyze_diff(diff_text: str) -> dict`):** Ham `git diff` metnini girdi alır; JSON/dataclass çıktısında `files`, `bundles`, `coverage_manifest`, `complexity_score`, `risk_flags`, `floor_violations` (`@ts-ignore`, `eslint-disable`, `# noqa`, `# type: ignore`, skipped test, stub) döndürür. İç parser fonksiyonlarına değil yalnız `analyze_diff` / CLI `--json` arayüzüne test bağlanır.
1. **[Adım 1 - Kırmızı Test Yaz & Koştur]:** `tests/test_diff_triage.py` içinde boş/küçük/büyük diff, i18n+test demetleme, `NO_TEST_CHANGES` ve `+ // @ts-ignore` zemin ihlali yakalama testlerini yaz; `python -m unittest tests/test_diff_triage.py` çalıştır -> **Beklenen Çıktı:** `ModuleNotFoundError` / `FAIL` (Kırmızı kanıt).

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
1. **[Adım 1 - `diff_triage.py` İnşa Et & Test Et]:** `.agent/skills/code-review/scripts/diff_triage.py` dosyasını yaz ve `python -m unittest tests/test_diff_triage.py` çalıştır -> **Beklenen Çıktı:** Tüm birim testler `OK` (Yeşil kanıt).

### 🧩 Faz 3: Cerrahi Skill Zenginleştirme & Scout Kayıtları
1. **[Adım 1 - 4 Aktarım Referans Dosyasını Oluştur]:** `.agent/skills/code-review/references/` altına seçilen 4 repodan cerrahi referansları ekle (kısa, token-dostu, sıfır şişkinlik):
   - `transferred_superpowers.md` (`receiving-code-review` pushback protokolü + `verification-before-completion` Iron Law + subagent model-tiering).
   - `transferred_agent_skills.md` (`code-review-and-quality` mutasyon testi + sizing + Structural Remedies / Presumptive Blockers + Dependency Hygiene + `doubt-driven` kör `ARTIFACT+CONTRACT` şablonu + `constraint-driven` anti-floor-weakening).
   - `transferred_code_review_skill.md` (`pr-analyzer` risk skorlaması + TOCTOU / no-op update / parameter sprawl).
   - `transferred_open_code_review.md` (`coverage_rate` kapsam muhasebesi + akıllı dosya demetleme + davranış etki özeti + opsiyonel `ocr delegate` notu).
   -> **Beklenen Çıktı:** Referans dosyaları `SKILL.md` gövdelerine bağlanır; `code-review`, `verify-last`, `tdd`, `karpathy-guidelines` güncellenir.
2. **[Adım 2 - `scout/plans/*.md` & `scout/repos.json` & HTML Katalog Güncelle]:** 6 repo için `scout/plans/` raporlarını yaz, `scout/repos.json` içine ekle ve `python scout/generate_scout_catalog.py` çalıştır -> **Beklenen Çıktı:** `scout-catalog.html` hatasız yeniden derlenir.

### 🧹 Faz 4: Kalite Kapıları, Parite & Kapanış
1. **[Adım 1 - Tüm Kapıları Koştur]:** `python scout/check_scout_integration.py --strict && python .agent/skills/musgoku/scripts/rules_gates.py --strict && python tests/run_all.py` -> **Beklenen Çıktı:** Tüm kapılar ve test paketleri `0` hatayla `PASS` döner.
2. **[Adım 2 - Doküman Kapanışı]:** `PROJECT_BRIEF.md` (50+ skill/script envanteri), `knowledge-base.md` (Council kararı), `HANDOFF.md` ve `docs/KULLANICI_TEST_REHBERI.md` güncelle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/run_all_gates.py` `[OK]` döner.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### Scout Kataloğu ve Planları
#### [NEW] `scout/plans/superpowers.md`
#### [NEW] `scout/plans/mattpocock-skills.md`
#### [NEW] `scout/plans/agent-skills.md`
#### [NEW] `scout/plans/code-review-skill.md`
#### [NEW] `scout/plans/open-code-review.md`
#### [NEW] `scout/plans/pr-agent.md`
- Her repo için parmak izi, delta analizi, Scout kararı ve entegrasyon kapsamı.

#### [MODIFY] `scout/repos.json` & `scout/scout-catalog.html`
- 6 reponun canonical kayıtları (`id: 28..33`), `history` izleri ve derlenen HTML kataloğu.

---

### Deterministik Diff Triaj & Kapsam Muhasebesi
#### [NEW] `.agent/skills/code-review/scripts/diff_triage.py`
- Saf Python stdlib modülü: `git diff` üzerinden boyut (`XS..XL`), karmaşıklık skoru, akıllı dosya demetleme (`i18n` çiftleri, kaynak+test), kapsam muhasebesi manifesti (`total_files`, `reviewed`, `skipped`), ve zemin düşürme taraması (`+` satırlarında `@ts-ignore`, `eslint-disable`, `# noqa`, `# type: ignore`, `skip`, `NotImplemented`).

#### [NEW] `tests/test_diff_triage.py`
- `diff_triage.py` için birim test paketi (yalnız genel `analyze_diff` / CLI dikiş noktası üzerinden).

---

### Skill Referansları & Orkestrasyon Zenginleştirmesi
#### [NEW] `.agent/skills/code-review/references/transferred_superpowers.md`
#### [NEW] `.agent/skills/code-review/references/transferred_agent_skills.md`
#### [NEW] `.agent/skills/code-review/references/transferred_code_review_skill.md`
#### [NEW] `.agent/skills/code-review/references/transferred_open_code_review.md`
- *(Not: `check_scout_integration.py` `E6_ORPHANED_TRANSFERRED_FILE` kuralı gereği her `transferred_*.md` dosyası `repos.json`'da ilgili tekil repoya 1:1 `transferred_to` olarak bağlanacaktır; `mattpocock/skills` ve `The-PR-Agent/pr-agent` için `REJECTED` kaydı açılıp aktarım dosyası üretilmez).*

#### [MODIFY] `.agent/skills/code-review/SKILL.md`
- `diff_triage.py` ön-triaj adımı, Kapsam Muhasebesi (`coverage_rate`), Davranışsal Etki Analizi, Structural Remedies / Presumptive Blockers, Mutasyon Testi adımı ve `receiving-code-review` geri bildirim protokolü bağlantısı.

#### [MODIFY] `.agent/skills/verify-last/SKILL.md` & `.agent/skills/tdd/SKILL.md` & `.agent/skills/karpathy-guidelines/SKILL.md`
- `verify-last`: Verification Iron Law + Rasyonalizasyon Önleme tablosu + zemin düşürme kontrolü.
- `tdd`: Regresyon testi red-green ispatı ("fix'i geri al -> kırmızı gör") + mutasyon kontrolü notu.
- `karpathy-guidelines`: `doubt-driven` kör `ARTIFACT+CONTRACT` (CLAIM gizleme) + `subagent` model kademelendirme notu.

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
# 1. Yeni diff_triage birim testleri
python -m unittest tests/test_diff_triage.py

# 2. Scout iki yönlü bütünlük kapısı (E1-E6, W1-W2)
python scout/check_scout_integration.py --strict

# 3. Kural kapıları ve havacılık dokümantasyon standardı
python .agent/skills/musgoku/scripts/rules_gates.py --strict

# 4. Tüm depo test paketi (30+ paket)
python tests/run_all.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - CLI Diff Triajı]:** `git diff HEAD~1..HEAD | python .agent/skills/code-review/scripts/diff_triage.py --stats` -> **Beklenen Çıktı:** Dosya manifesti, demetler, karmaşıklık skoru ve risk faktörleri hatasız basılır.
2. **[Adım 2 - Scout Katalog Görünümü]:** `scout/scout-catalog.html` dosyasını tarayıcıda açın -> **Beklenen Çıktı:** 6 yeni repo doğru statü (`TRANSFERRED`/`REJECTED`), katman ve önizleme planlarıyla görünür.

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `E5_COLLIDING_PLAN_FILE` (`skills.md`) | `mattpocock/skills` ile `jakubkrehel/skills` aynı plan adını kullandı | `plan_file` değerini `plans/mattpocock-skills.md` yap ve `python scout/check_scout_integration.py --strict` koştur |
| `E6_ORPHANED_TRANSFERRED_FILE` | `transferred_*.md` dosyası `repos.json` içindeki `transferred_to` ile eşleşmedi | İlgili `repos.json` kaydında `transferred_to` yolunu birebir güncelle ve `--strict` tekrar çalıştır |
| `check_design_slop.py` veya `rules_gates.py` uyarısı | Yeni referans dosyasında `TODO` / placeholder kalıntısı | Placeholder ifadelerini somut örnekle değiştirip `python .agent/skills/musgoku/scripts/rules_gates.py --strict` koştur |
