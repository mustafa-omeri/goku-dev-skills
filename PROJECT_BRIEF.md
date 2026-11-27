---
title: Project Brief — skillSetWorks
type: project-brief
project: skillSetWorks
status: active
created: 2026-10-27
updated: 2026-11-27
primary_language: Python 3.11 / Node.js / Markdown
frameworks: ["pytest", "unittest", "node-cli"]
database: ["Yok / Kural ve Dağıtım Deposu"]
depends_on:
  - [[projects/_STANDARTLAR/decisions/kod-ajani-vaulta-yazmaz]]
  - [[projects/_STANDARTLAR/decisions/proje-isimlendirmesi-camelcase]]
related_docs:
  - knowledge-base.md
  - HANDOFF.md
  - delivery.md
  - README.md
  - docs/KULLANICI_TEST_REHBERI.md
---

# 🚀 skillSetWorks — Project Brief & Architecture Matrix

> Bu dosya skillSetWorks deposunun güncel teknolojilerini, dizin haritasını, dağıtım hedeflerini ve bağlayıcı kararlarını özetleyen canlı mimari belgedir.
> AI Kod Geliştirme Ajanları tarafından yaşayan kod gerçekliğine göre taze tutulur.

---

## 1. Teknoloji Yığını & Altyapı
- **Proje Adı / Slug:** skillSetWorks (`skillSetWorks`)
- **Paket / Sürüm:** `goku-dev-skills` v1.51.1 (`package.json`)
- **Birincil Dil:** Python 3.11 / Node.js 18+ / Markdown
- **Frameworkler & Kütüphaneler:** Python `unittest`, `pytest`, `pytest-cov`, `argparse`, Node.js CLI runtime
- **Veritabanı / Altyapı:** Yok (Uygulama kodu içermez; kural, skill ve dağıtım motorudur)
- **Build / Yönetim Araçları:** `delivery.py` (Projelere dağıtım aracı), `rules_gates.py` (Kural denetleyicisi), `run_all_gates.py` (Birleşik kapı koşturucu), `check_handoff.py` (Oturum devri kapısı), `archive_plan.py` (`/plan` & `/seal-plan` onay sonrası `docs/plans/` arşivleyici, `--seal-handoff` backlog mühürleyici ve UI planlarında `check_ui_predesign_plan` / `--allow-no-wireframe` wireframe kapısı), `plan_conflict_guard.py` (Ön-mühürleme & Sprint/Kanban canlı kod `EXACT`/`ENRICHED`/`SIMPLIFIED` ve bekleyen sıralı plan ezme `CLOBBER` tespit kalkanı), `sync_sibling_handoff.py` (Kardeş uygulama `HANDOFF.md` cross-repo devir ve `--ui-wireframe-expected` UI ön-tasarım beklentisi aktarım motoru), `prd_review_helper.py` (`/review-prd` bağlam & analiz yardımcısı), `test_spec_scanner.py` / `test_spec_tracker.py` / `testsprite_bridge.py` / `check_test_spec.py` (`test-spec-generator` / `/test-spec` & `/test-spec-run` v2 artımlı kod+doküman envanter çıkarıcı, TestSprite MCP köprüsü + kardeş repo hata adresleme, Major/Minor çift-hash takip, PASS referans defteri, cerrahi yama, `export-delta` ve tek-dosya Gherkin+AC kapsama kapısı), `impact_mapper.py` / `smoke_runner.py` (`/smoke-test`, `/verify-last`, `/verify-sprint` etki-odaklı blast-radius API+ekran smoke motoru — Seçenek A Hibrit + Seçenek B Canlı E2E & TestSprite Kota Fallback), `fa_scan.py` / `kg_query.py` / `review_units.py` / `fa_engine` (`discovery`, `graph`, `snapshot`, `intelligence`, `runtime`, `evolution`, `cache`) / `gap_scanner.py` / `engine_advisor.py` / `council_merger.py` (Feature Architect v2.1 deterministik tam-yığın mimari zeka, kanonik bilgi grafiği, V1-V10 kanıt yönetişimli Defect-First Council v3, L3 runtime doğrulayıcı ve artımlı önbellek motoru), `bin/cli.js` (CLI paketi)

---

## 2. Dizin Ağacı & Modül Sorumlulukları
| Dizin / Modül | Sorumluluk & Kapsam | Kritik Notlar |
|---|---|---|
| `.agent/` | Tüm projelerin tek gerçek kaynak (single source of truth) kural ve skill ağacı | Dağıtım kaynağıdır |
| `.agent/skills/` | Ajan beceri paketleri (musgoku, feature-architect, review-prd, test-spec-generator, test-spec-run, smoke-test, project-summary, ui-ux-pro-max, tdd, council, seal-plan, tr-app-compliance vb.) | 53 skill |
| `.agent/rules/` | Ajan kuralları ve anayasal sözleşmeler (sinif: OLCULEBILIR/TUTUM/SUREC) | 22 kural (12 ölçülebilir, 10 kapısız) |
| `.agent/templates/` | Projelerde açılacak living markdown ve HTML şablonları | Kök şablonları (`PROJECT_SUMMARY`, `ACCEPTANCE_TEST_SPEC` ve `KULLANICI_REHBERI.html` dahil) |
| `bin/` | `goku-dev-skills` npm CLI paket yürütücüsü (`cli.js`) | `init`, `update`, `add`, `sync-agy` |
| `tests/` | Depo bütünlüğü, drift, sızıntı, altın benchmark ve kural kapısı regresyon testleri | 40 test paketi (`test_smoke_runner.py`, `test_sprint_auditor.py`, `test_gsap_init.py` ve `test_skill_pytest_suites.py` dahil) |
| `scripts/` | Skill kataloğu (`generate_skills_catalog.py`) ve global Antigravity plugin senkronu (`sync_agy_global.py`) | Otomasyon araçları |

---

## 2.1. Komut Haritası & Giriş Noktaları (Zero-Scan Cockpit)

| Eylem | Komut | Not |
|---|---|---|
| **Tam Test Paketi** | `python tests/run_all.py` | 40 regresyon paketi |
| **Birleşik Kural Kapıları** | `python .agent/skills/musgoku/scripts/run_all_gates.py` | Tüm teslimat kapıları |
| **Brief Kapısı** | `python .agent/skills/musgoku/scripts/check_project_brief.py` | Mimari & diff drift denetimi |
| **Projelere Dağıtım** | `python delivery.py` | Hedef repolara `.agent/` dağıtımı |
| **Global Plugin Senkronu** | `python scripts/sync_agy_global.py` | Antigravity plugin & skill kataloğu |

- **Ana Giriş Noktaları (Entry Points):** `delivery.py`, `bin/cli.js`, `.agent/skills/musgoku/scripts/run_all_gates.py`, `tests/run_all.py`
- **Ortam Değişkeni Anahtarları (⚠️ Değer yazılmaz):** `AGENTS_PROJECT_ROOT` (Opsiyonel kapı hedef kök dizini)

---

## 3. Bağlayıcı Kararlar & Detay İndeksi (llms.txt Pattern)

> Projeyi etkileyen veya bu projede hayata geçirilen temel anayasal ve yerel kararlar:

| Karar / Standart | Konum / Link | İlişki Tipi | Etki Alanı |
|---|---|---|---|
| Kod Ajanı Vault'a Yazmaz | `[[projects/_STANDARTLAR/decisions/kod-ajani-vaulta-yazmaz]]` | `implements` | Dokümantasyon & Ingest |
| CamelCase Proje İsimlendirmesi | `[[projects/_STANDARTLAR/decisions/proje-isimlendirmesi-camelcase]]` | `implements` | Klasör & Repo Standartları |
| Proje İçi Kararlar | `knowledge-base.md` | `contains` | Mimari & Hata Çözümleri |
| Dağıtım Yapılandırması | `delivery.md` | `contains` | Dağıtım Hedefleri ve Kuralları |

---

## 4. Veritabanı Modeli & Veri Mimarisi
- **Model / DB:** Yok (Bu repo uygulama kodu içermez; kural, skill ve dağıtım motorudur).
- **Migration Takibi:** Kapsam dışı (`DB_MIGRATIONS.md` gerektirmez).

---

## 5. Yaşatma & Operasyonel Döngü
- **Kapsam İçi Kapılar:** `rules_gates.py`, `check_handoff.py`, `check_project_brief.py`, `check_design_skills.py`, `check_test_spec.py`, `plan_conflict_guard.py`, `archive_plan.py`, `diff_triage.py`, `impact_mapper.py`, `smoke_runner.py`, `test_skills_catalog.py`, `test_project_summary.py`, `test_feature_architect.py`, `test_feature_architect_council.py`, `test_feature_architect_bench.py`, `test_council_workflow_integration.py`, `test_theme_skeleton_integration.py`, `test_prelaunch_security.py`, `test_clean_url_routing.py`, `test_cognitive_counsel.py`, `test_test_spec_generator.py`, `test_plan_conflict_guard.py`, `test_ui_predesign_gate.py`, `test_walkthrough_archive.py`, `test_smoke_runner.py`
- **Son Başarılı Doğrulama:** 2026-11-27 · 40/40 test paketi (`tests/run_all.py`) · `test_check_theme_contrast.py` 14/14 PASS · Birleşik kapılar `[OK]` · Skill kataloğu (52 skill, 24 slash komutu) PASS
