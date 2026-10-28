---
title: Project Brief — skillSetWorks
type: project-brief
project: skillSetWorks
status: active
created: 2026-10-27
updated: 2026-10-28
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
---

# 🚀 skillSetWorks — Project Brief & Architecture Matrix

> Bu dosya skillSetWorks deposunun güncel teknolojilerini, dizin haritasını, dağıtım hedeflerini ve bağlayıcı kararlarını özetleyen canlı mimari belgedir.
> AI Kod Geliştirme Ajanları tarafından yaşayan kod gerçekliğine göre taze tutulur.

---

## 1. Teknoloji Yığını & Altyapı
- **Proje Adı / Slug:** skillSetWorks (`skillSetWorks`)
- **Paket / Sürüm:** `goku-dev-skills` v1.16.1 (`package.json`)
- **Birincil Dil:** Python 3.11 / Node.js 18+ / Markdown
- **Frameworkler & Kütüphaneler:** Python `unittest`, `pytest`, `pytest-cov`, `argparse`, Node.js CLI runtime
- **Veritabanı / Altyapı:** Yok (Uygulama kodu içermez; kural, skill ve dağıtım motorudur)
- **Build / Yönetim Araçları:** `delivery.py` (Projelere dağıtım aracı), `rules_gates.py` (Kural denetleyicisi), `run_all_gates.py` (Birleşik kapı koşturucu), `check_handoff.py` (Oturum devri kapısı), `bin/cli.js` (CLI paketi)

---

## 2. Dizin Ağacı & Modül Sorumlulukları
| Dizin / Modül | Sorumluluk & Kapsam | Kritik Notlar |
|---|---|---|
| `.agent/` | Tüm projelerin tek gerçek kaynak (single source of truth) kural ve skill ağacı | Dağıtım kaynağıdır |
| `.agent/skills/` | Ajan beceri paketleri (musgoku, ui-ux-pro-max, tdd, council, seo-growth vb.) | 42 skill |
| `.agent/rules/` | Ajan kuralları ve anayasal sözleşmeler (sinif: OLCULEBILIR/TUTUM/SUREC) | 20 kural (11 ölçülebilir) |
| `.agent/templates/` | Projelerde açılacak living markdown şablonları | Kök şablonları |
| `bin/` | `goku-dev-skills` npm CLI paket yürütücüsü (`cli.js`) | CLI arabirimi |
| `tests/` | Depo bütünlüğü, drift, sızıntı ve kural kapısı regresyon testleri | 16 test paketi |
| `scripts/` | Skill kataloğu ve yardımcı üretim betikleri | Otomasyon araçları |

---

## 3. Bağlayıcı Kararlar & Dış Referanslar (Decisions & References)

> Projeyi etkileyen veya bu projede hayata geçirilen temel anayasal ve yerel kararlar:

| Karar / Standart | Konum / Link | İlişki Tipi | Etki Alanı |
|---|---|---|---|
| Kod Ajanı Vault'a Yazmaz | `[[projects/_STANDARTLAR/decisions/kod-ajani-vaulta-yazmaz]]` | `implements` | Dokümantasyon & Ingest |
| CamelCase Proje İsimlendirmesi | `[[projects/_STANDARTLAR/decisions/proje-isimlendirmesi-camelcase]]` | `implements` | Klasör & Repo Standartları |
| Proje İçi Kararlar | `knowledge-base.md` | `contains` | Mimari & Hata Çözümleri |
| Dağıtım Yapılandırması | `delivery.md` | `contains` | Dağıtım Hedefleri ve Kuralları |

---

## 4. Veritabanı Modeli & Migration Politikası
- **Altyapı:** Yok / Uygulama veritabanı bulunmamaktadır.
- **Şema & Tablolar:** Kapsam dışı.
- **Migration Konumu:** Kapsam dışı.

---

## 5. Yaşatma ve Senkronizasyon Kuralı
⛔ **Bu dosya asla bayat bırakılamaz.** Yeni bir skill veya kural eklendiğinde, bağımlılık manifestosu (`package.json`) veya dağıtım yapısı güncellendiğinde senkronize edilmelidir (Bkz: `.agent/rules/project-brief-maintenance.md`).
