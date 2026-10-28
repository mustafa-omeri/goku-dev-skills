---
title: "[SLUG] Proje Özeti & Konsolide Dokümantasyon"
project_slug: "[SLUG]"
mode: "[MODE]" # short | long
version: "v1.0"
last_updated: "[YYYY-MM-DD HH:mm:ss]"
updated_by: "[KULLANICI_VEYA_AJAN]"
language: "[TR_VEYA_EN]"
sources_ingested:
  prds:
    - "[ORNEK: docs/mobile-prd.md]"
  architecture: "PROJECT_BRIEF.md"
  product: "PRODUCT.md"
  glossary: "GLOSSARY.md"
  database: "DB_MIGRATIONS.md"
  design: "DESIGN.md"
  handoff: "HANDOFF.md"
  decisions: "knowledge-base.md"
---

# [PROJE_ADI] — Proje Konsolide Özeti ([MODE])

> 📌 **Versiyonlama Damgası:** v1.0 · **Tarih:** [YYYY-MM-DD] · **Saat:** [HH:mm:ss] · **Güncelleyen:** [KULLANICI_VEYA_AJAN] · **Mod:** [SHORT/LONG]

---

## 📜 Revizyon Geçmişi (Revision History)

| Versiyon | Tarih | Saat | Güncelleyen | Mod | Kapsam / Değişiklik Özeti |
|---|---|---|---|---|---|
| v1.0 | [YYYY-MM-DD] | [HH:mm:ss] | [KULLANICI_VEYA_AJAN] | [MODE] | İlk konsolide özet oluşturuldu (PRD ve referans dokümanlar sentezlendi). |

---

<!-- SHORT MOD BÖLÜMÜ (mode == 'short' ise aşağıdaki 5 ana başlık kullanılır) -->

## 1. Yönetici Özeti & Ürün Amacı
- **Projenin Amacı:** [Bu yazılım hangi temel problemi çözer?]
- **Hedef Kitle & Kullanıcı Rolleri:** [Sistemi kimler kullanır?]
- **Temel Değer Önerisi:** [Kullanıcıya ve işletmeye sağlanan ana fayda.]

## 2. Çekirdek Teknoloji Yığını & Altyapı
- **Dil & Çalışma Zamanı:** [Java 21 / Node 20 / Python 3.12 vb.]
- **Framework & Kütüphaneler:** [Spring Boot 3 / React 19 / Vite / Tailwind vb.]
- **Veritabanı & Kalıcılık:** [PostgreSQL / Supabase / Redis / Prisma vb.]
- **Dağıtım & Konteyner:** [Docker / Cloud / Serverless Worker vb.]

## 3. Canlı Kilometre Taşı & Yaşayan Durum
- **Mevcut Sürüm / Sprint:** [Örn: v1.12.0 / Sprint 24]
- **Tamamlanan Temel Yetenekler:** [Özet başarımlar]
- **Açık / Devam Eden İşler:** [Aktif öncelikler]

---

<!-- LONG MOD BÖLÜMÜ (mode == 'long' ise aşağıdaki kapsamlı sentez başlıkları kullanılır) -->

## 1. Ürün Vizyonu, Hedef Kitle & Kısıtlar (PRODUCT.md & PRD)
- **Vizyon:** [Ürünün nihai vizyonu ve pazardaki yeri]
- **Kullanıcı Personaları & Senaryolar:** [Personalar ve kullanım amaçları]
- **MVP & Sürüm Kapsam Sınırları:** [Kapsam içi ve kapsam dışı bırakılan sınır noktaları]

## 2. İş Alanı Modeli & Terimler Sözlüğü (GLOSSARY.md Sentezi)
- **İş Alanı Kavramları (Ubiquitous Language):**
  - `[Terim 1]`: [Açıklama ve sistemdeki karşılığı]
  - `[Terim 2]`: [Açıklama ve sistemdeki karşılığı]

## 3. Canlı Sistem Mimarisi & Teknoloji Yığını (PROJECT_BRIEF.md)
- **Mimari Katmanlar:** [Frontend, Backend, View/RPC, Edge Functions]
- **Dizin & Modül Haritası:** [Temel klasörler ve sorumlulukları]
- **Bağlayıcı Mimari Kararlar:** [Altyapıyı bağlayan ana prensipler]

## 4. Veritabanı Şeması & Veri Modeli (DB_MIGRATIONS.md)
- **Çekirdek Varlıklar / Tablolar:** [Tablo adları ve temel sorumlulukları]
- **İlişkiler & İndeksler:** [Bire-çok, çoka-çok ilişkiler ve performans stratejileri]
- **Güvenlik & Yetkilendirme (RLS):** [Veritabanı seviyesi erişim politikaları]

## 5. Tasarım Dili, Token'lar & Arayüz Standartları (DESIGN.md)
- **Tasarım Felsefesi & Karakter:** [Seçilen tema yönü, tipografi ve estetik manifestosu]
- **Token Mimarisi:** [Primitive -> Semantic -> Component token yapısı]
- **Erişilebilirlik (A11y):** [WCAG 2.2 AA kontrast ve klavye etkileşim kuralları]

## 6. Fonksiyonel & Teknik Şartname Sentezi (PRD Dokümanları)
> *Not: Projede tespit edilen tüm PRD dokümanlarından (`docs/*prd*.md`, `PRD.md`) çıkarılan gereksinimler aşağıda tek bir matriste birleştirilmiştir.*

### 6.1 Fonksiyonel Gereksinimler (Functional Requirements)
| ID | Başlık | Kaynak PRD | Açıklama | Canlı Durum |
|---|---|---|---|---|
| FR-001 | [Gereksinim Adı] | [Örn: docs/mobile-prd.md] | [Detaylı kabul kriteri] | ✅ Tamamlandı / ⏳ Devam Ediyor |

### 6.2 Fonksiyonel Olmayan Gereksinimler (Non-Functional Requirements)
- **Performans & Bundle Bütçesi:** [Yüklenme hızı, chunk limitleri]
- **Güvenlik (Halka 2 Kalkanı):** [OWASP, Turnstile, Rate limiting, CSRF]
- **i18n & Çoklu Dil:** [Desteklenen yereller ve çeviri mimarisi]

## 7. Yaşayan Durum, Tamamlanan Dilimler & Sıradaki Yol Haritası (HANDOFF.md)
- **Tamamlanan Dikey Dilimler (5-Layer Slice):** [DB, View, API, UI, Form katmanları doğrulanmış özellikler]
- **Sıradaki Öncelikli Görevler:** [Planlanan sıradaki adımlar]

## 8. Mimari Karar Kayıtları & Alınan Dersler (knowledge-base.md & docs/adr/)
- **Kalıcı Kararlar (ADR):** [Önemli kararlar ve gerekçeleri]
- **Bu Projede Düşülen Tuzaklar & Çözümleri:** [Geliştiricilerin dikkat etmesi gereken noktalar]
