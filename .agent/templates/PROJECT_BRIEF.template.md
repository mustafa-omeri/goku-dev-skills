---
title: Project Brief — [PROJE_ADI]
type: project-brief
project: [proje-slug]
status: active
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
primary_language: [Birincil Dil ve Sürüm, örn: TypeScript (React 19, Vite 6) veya Java 21 (Spring Boot 3.5)]
frameworks: ["[Framework 1]", "[Kütüphane 2]"]
database: ["[Veritabanı Servisi, örn: PostgreSQL / Supabase / Redis / Yok]"]
depends_on:
  - [[projects/_STANDARTLAR/decisions/kod-ajani-vaulta-yazmaz]]
  - [[projects/_STANDARTLAR/decisions/proje-isimlendirmesi-camelcase]]
related_docs:
  - knowledge-base.md
  - HANDOFF.md
  - docs/KULLANICI_TEST_REHBERI.md
---

# 🚀 [PROJE_ADI] — Project Brief & Architecture Matrix

> Bu dosya [PROJE_ADI] projesinin güncel teknolojilerini, veritabanı şemasını, dizin haritasını ve bağlayıcı kararlarını özetleyen canlı mimari belgedir.
> AI Kod Geliştirme Ajanları tarafından yaşayan kod gerçekliğine göre taze tutulur.

---

## 1. Teknoloji Yığını & Altyapı
- **Proje Adı / Slug:** [PROJE_ADI] (`[proje-slug]`)
- **Birincil Dil:** [Örn: TypeScript / Java 21 / Python 3.11]
- **Frameworkler & Kütüphaneler:** [Örn: React 19, Vite 6, Tailwind CSS v4, Zustand 5, TanStack Query 5]
- **Veritabanı / Altyapı:** [Örn: Supabase PostgreSQL, Cloudflare R2 / S3]
- **Build / Yönetim Araçları:** [Örn: pnpm, Vite, Vitest 3, Playwright / Maven 3]

---

## 2. Dizin Ağacı & Modül Sorumlulukları
| Dizin / Modül | Sorumluluk & Kapsam | Kritik Notlar |
|---|---|---|
| `src/` | Ana uygulama kodları, bileşenler ve iş mantığı | Modüler kaynak dizini |
| `docs/` | PRD, mimari planlar ve kullanıcı test rehberi | Dokümantasyon alanı |
| `scripts/` | Otonom doğrulama ve altyapı kontrol betikleri | Doğrulama kapıları |

---

## 3. Bağlayıcı Kararlar & Dış Referanslar (Decisions & References)

> Projeyi etkileyen veya bu projede hayata geçirilen temel anayasal ve yerel kararlar:

| Karar / Standart | Konum / Link | İlişki Tipi | Etki Alanı |
|---|---|---|---|
| Kod Ajanı Vault'a Yazmaz | `[[projects/_STANDARTLAR/decisions/kod-ajani-vaulta-yazmaz]]` | `implements` | Dokümantasyon & Ingest |
| CamelCase Proje İsimlendirmesi | `[[projects/_STANDARTLAR/decisions/proje-isimlendirmesi-camelcase]]` | `implements` | Klasör & Repo Standartları |
| Proje İçi Kararlar | `knowledge-base.md` | `contains` | Mimari & Hata Çözümleri |

---

## 4. Veritabanı Modeli & Migration Politikası
- **Altyapı:** [Veritabanı servisi ve sürümü]
- **Şema & Tablolar:** [Ana veri modelleri ve ilişkiler]
- **Migration Konumu:** [Repo içi migration dizini, örn: supabase/migrations veya src/main/resources/db/migration]

---

## 5. Yaşatma ve Senkronizasyon Kuralı
⛔ **Bu dosya projenin makro mimari omurgasıdır; özellik changelog'u DEĞİLDİR.**
- **Ne Zaman Güncellenir:** Yeni bir kütüphane/paket eklendiğinde, veritabanı şeması/migration'ı değiştiğinde, yeni bir altyapı/Edge servisi kurulduğunda veya yeni bir modül dizini (`§2`) açıldığında güncellenir.
- **Ne Zaman Stabil Kalır:** Yeni paket veya DB tablosu gerektirmeyen salt iş mantığı (business logic), arayüz bileşeni veya birim test geliştirmelerinde mimari omurga stabil kalır (özellik detayları `docs/kullanici-rehberi.html` ve `knowledge-base.md` içinde tutulur).
- Ayrıntılı kural ve kapı: `.agent/rules/project-brief-maintenance.md` ve `readme-help.md`.
