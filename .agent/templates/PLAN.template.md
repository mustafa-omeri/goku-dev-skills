# [Özellik / Görev Başlığı] Uygulama Planı
<!-- 
  Bu dosya Antigravity IDE, Antigravity CLI (agy), Claude Code (claude), OpenCode (opencode) ve Genel CLI planlama modları (/plan, /council) ve standart geliştirme planları için zorunlu şablondur.
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2 · .agent/rules/aviation-documentation-standard.md (FAA AC 121-24C + /caveman)
  UYARI: Planlar sohbet çıktısı olarak verilemez; her plan ayrı bir fiziksel .md dosyasında üretilir ve tüm plan yönergeleri FAA AC 121-24C standardındadır.
-->

> **Hedef Dal / Sürüm:** `<doldur: örn. main / v1.19.0>` · **Tarih:** `<doldur: YYYY-MM-DD>`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `<doldur: örn. musgoku, tdd, frontend-design, ui-ux-pro-max, diagram-design, security-audit>`  
> **Kullanılan MCP'ler:** `<doldur: context7, sequential-thinking veya kullanılmadı>`  
> **İlgili KANBAN Kartı:** `<doldur: örn. [SPRINT-XX]-[KART-ID] veya Yeni Kart>`  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`  

---

## 1. [Goal Description] (Amaç & Kapsam)
<doldur: Problemin kısa tanımı, arka plan bağlamı ve bu değişikliğin neyi başardığı.>

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: <doldur: Özellik Adı>
  Scenario: <doldur: Başarılı Senaryo Tanımı>
    Given <doldur: Başlangıç durumu>
    When <doldur: Kullanıcının veya sistemin yaptığı eylem>
    Then <doldur: Beklenen somut ve gözlenebilir sonuç>
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (2+ Seçenek İncelemesi)
> [!NOTE] Tek alternatifli basit işlerde 'Doğrudan tek yol / Konsey eşiği altında' yazılır.
> 2+ alternatifli mimari/teknoloji tercihlerinde Option A vs Option B körlemesi zorunludur.

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Yalın/Karpathy)** | <doldur: Sıfır bağımlılık, yalın çözüm> | <doldur> | <doldur> | <doldur: örn. 2.5> |
| **Option B (Genişletilebilir)** | <doldur: Modüler, esnek soyutlama> | <doldur> | <doldur> | <doldur: örn. 1.8> |

- **Seçilen Yol & Gerekçe:** <doldur: Kazanan seçenek ve elenen seçeneğin neden tercih edilmediği>
- **Birleşik Planlama Ekosistemi Bağlantısı:** Fikir (`my-idea`) → Şartname/PRD (`doc-coauthoring`) → Açık Denetimi & Tema İskeleti (`feature-architect` / `theme-skeleton-matching.md`) → Konsey Hakemliği (`council`) → Görev Kartı (`KANBAN.md`) → TDD Dikiş Noktası & 5 Katmanlı Dikey Dilim (`development-workflow.md` Adım 2.2).

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)
> [!IMPORTANT]
> <doldur: Kullanıcının onaylaması gereken mimari kararlar, breaking change'ler veya UX tercihleri.>
>
> **2-Modlu Onay Seçenekleri (Planı Nasıl İlerletelim?):**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan` / `"planı mühürle, kodlama yapma"`):** Planı `docs/plans/` altına arşivler, `HANDOFF.md` §3 Gelecek Fazlar (`⬜ Bekliyor`), `KANBAN.md` `Bekliyor` ve (varsa) kardeş `HANDOFF.md` dosyasına dağıtır; **kod yazmadan durur** (araya başka sprint/iş alabilirsiniz, istediğinizde tetiklersiniz).
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onayla ve başla"`):** Faz 0 mühürlemesini yapıp hemen Faz 1 (TDD Kırmızı Test) ile geliştirmeye başlar.

## 4. Open Questions (Açık Sorular)
<doldur: Varsa kullanıcıya sorulacak netleştirme soruları; yoksa 'Açık soru bulunmamaktadır.'>

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `<doldur: örn. PRJ-TASK-001>` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3 + `KANBAN.md`) | `<doldur: S1-01 / WIP maks 3>` |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
> ⛔ Kardeş uygulamada geliştirme gerekmiyorsa yalnızca `'Tek Repo / Kardeş Uygulama Etkisi Yok'` yazın.
> **Kardeş Proje Kuralları (Topoloji + Süreç Senkronu):**
> - **Dizin Fark Etmeksizin:** `sync_sibling_handoff.py` ile kardeş projenin kendi `HANDOFF.md` dosyasına **ve süreçlerine (`KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md`)** `<kaynak-proje> projesindeki <plan-yolu> plan dosyası referansına göre` geliştirme maddeleri eklenir.
> - **Aynı Dizin / Çalışma Alanında (`SAME_AGENT_ALLOWED`):** Skill'ler projelere göre yüklendiği için aynı kod ajanı süreci ilerletebilir.
> - **Farklı Dizinde (`ASK_USER_PREFER_SIBLING_AGENT`):** Öncelik her projenin kendi kod ajanının ilgili geliştirmeyi yapmasıdır; koda dokunmadan önce kullanıcıya mutlaka sorulmalıdır.

- **Etkilenen Kardeş Uygulama, Yol & Topoloji:** `<doldur: örn. ../backend-repo (Aynı Dizin) / C:/.../other-repo (Farklı Dizin) veya 'Tek Repo / Kardeş Uygulama Etkisi Yok'>`
- **Kardeş `HANDOFF.md` + Süreç Dosyalarına Yazılacak Görevler & Sözleşme Özeti:** `<doldur: Görev ID, başlık ve API/DTO/şema kontrat özeti>`
- **Yürütme Sahipliği Sorusu (Farklı Dizinde Zorunlu):** *"Kardeş proje farklı dizinde yer alıyor; öncelik kardeş projenin kendi kod ajanındadır. Kardeş uygulamadaki geliştirmeyi kendi kod ajanı mı yapsın, yoksa ben mi devralayım?"* (`[Seçenek 1: Kardeş Projenin Kendi AI Agent'ı (Öncelikli) / Seçenek 2: Mevcut Ajan]`)

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Full-Stack Vertical Slice)
> ⛔ Bir katman dahi eksikse Sahte Bitti (Phantom Done) sayılır.
> 💡 **Teknik Mimari & Diyagram Sözleşmesi (`diagram-design`):** Karmaşık sistem topolojisi, C4 mimari katmanları, mikroservis/servis etkileşimleri, ER veri modelleri, sequence mesajlaşmaları veya durum makineleri gereken planlarda; generic Mermaid yerine `diagram-design` motoru (`skills/diagram-design/SKILL.md`) kullanılarak `docs/architecture/` veya `<artifact-dir>/` altında bağımsız, editoryal HTML/SVG şemaları üretilebilir.

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | <doldur: Yeni tablo, kolon, RLS veya 'Kapsam dışı / Salt UI'> | `<doldur>` |
| **2. Backend / View / RPC** | <doldur: Endpoint, DTO, servis, controller veya 'Kapsam dışı'> | `<doldur>` |
| **3. İstemci API Entegrasyonu** | <doldur: Fetch/Axios istemcisi, tip tanımları, API fonksiyonu> | `<doldur>` |
| **4. Arayüz / UX & Eylemler** | <doldur: Bileşen, form, 4 UX Durumu + Zorunlu Skeleton Screens UI> | `<doldur>` |
| **5. Döngü Kapanışı (Admin)** | <doldur: Verinin tüketim/onay ekranı, moderasyon veya 'Kullanıcı döngüsü'> | `<doldur>` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi (Theme & Component Skeleton Contract)
> ⛔ **SIFIR AI-SLOP KURALI:** Arayüz içeren her planda ezbere bileşen veya keyfi renk yazmak yasaktır; `.agent/skills/feature-architect/references/theme-skeleton-matching.md` omurgasıyla eşleştirme zorunludur (Salt backend/CLI işlerinde `'Salt Backend / UI Kapsam Dışı'` yazılır):

| İskelet Boyutu | Seçilen Şablon / Kaset / Token | Kaynak / CLI Komutu |
|---|---|---|
| **1. Yaşayan Yüzey & 16 Kilitli Tema** | `<doldur: Light/Dark Living Surface + #01 Obsidian Velvet .. #16 Warm Alabaster>` | `.agent/skills/frontend-design/themes/themes.css` |
| **2. 55+ Doğrulanmış Bileşen Teması** | `<doldur: logins / sidebars / navbars / menus / cards / footers / accordions / parallax şablon ID'si>` | `python .agent/skills/frontend-design/scripts/get_component.py --list` |
| **3. 18 Doğrulanmış Dashboard Şablonu** | `<doldur: dashboard-theme-01 .. 18 veya 'Dashboard Kapsam Dışı'>` | `.agent/skills/frontend-design/dashboard-theme/catalog.json` |
| **4. Zero-CLS Skeleton Kaseti & 4 UX Durumu** | `<doldur: Profil / Metrik Kart / Tablo Satırı / Dashboard / Form Kaseti + Empty/Error State>` | `ui-polish` & `check_design_slop.py` |
| **5. Görsel Varlık & Karşılama Turu** | `<doldur: generate_auth_hero.py / mock-asset-provider / onboarding-tour veya 'Gerekmiyor'>` | `generate_auth_hero.py` & `onboarding-tour` |

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)
> ⛔ **PROCEED İCRA KURALI (MANDATORY — Çoklu Araç Uyumlu):** Tüm plan yönergeleri FAA AC 121-24C standardına uygun `[Adım N]. [Eylem / Komut] -> [Beklenen Çıktı]` sözdiziminde yazılır. Kullanıcı `"proceed"`, `"onay"`, `"uygula"` verdiğinde önce **Faz 0**, ardından **Faz 1..4** icra edilir.

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 & Sprint Açılışı — Koda Dokunmadan Önce Zorunlu)
1. **[Adım 1 - Planı `docs/plans/` Altına Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug <slug>` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_<slug>_<YYYYMMDD_HHMMSS>.md`
2. **[Adım 2 - `HANDOFF.md` §3 Canlı Panosuna İşle]:** Bölüm 5'teki tüm `[DOM]-[TIP]-[NO]` görevlerini ve arşivlenen plan referansını `HANDOFF.md` §3 panosuna işle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0 hata, 0 W3 uyarısı` döner.
3. **[Adım 3 - Sprint & Kardeş Süreç Senkronu]:** `SPRINT_PLAN.md`, `KANBAN.md`, `RELEASE_PLAN.md` yoksa şablondan aç; kardeş proje varsa `sync_sibling_handoff.py` çalıştır -> **Beklenen Çıktı:** Aktif kart `Yapılıyor`'a taşınır ve kardeş `HANDOFF.md` + süreçler güncellenir.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - Kırmızı Test Yaz & Koştur]:** `<doldur: tests/.../feature.test.ts>` dosyasında `<doldur: genel dikiş noktası>` testini yaz ve `<doldur: test komutu>` çalıştır -> **Beklenen Çıktı:** Terminalde testin **KIRMIZI (FAIL)** olduğu görülür.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
1. **[Adım 1 - Minimal Üretim Kodunu Yaz & Test Et]:** `<doldur: src/.../FeatureService.ts>` içine yalnız Faz 1 testini geçecek minimal kodu yaz ve `<doldur: test komutu>` çalıştır -> **Beklenen Çıktı:** Terminalde testin **YEŞİL (PASS)** olduğu görülür.

### 🧩 Faz 3: 5 Katman Tamamlama, Tema İskeleti & UX Durumları
1. **[Adım 1 - 5 Katman & Zero-CLS Skeleton Bağlantısı]:** DB, API, UI, seçilen tema/bileşen şablonunu (`component-themes/` / `dashboard-theme/`) ve Zero-CLS Skeleton Screens UI kasetini uygula -> **Beklenen Çıktı:** 3 cihaz ergonomisinde (Mobil/Tablet/Masaüstü) veri akışı ve skeleton durumu eksiksiz çalışır.

### 🧹 Faz 4: Refactor, Kapılar & Kapanış
1. **[Adım 1 - Kalite Kapıları & Kullanıcı Test Rehberi]:** `python .agent/skills/musgoku/scripts/run_all_gates.py` çalıştır, `docs/KULLANICI_TEST_REHBERI.md` güncelle ve `KANBAN.md` kartını `Yapıldı`'ya taşı -> **Beklenen Çıktı:** Tüm kapılar `[OK]` döner; sprint bitiminde kullanıcıya `"/verify-sprint çalıştırayım mı?"` sorulur.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### [Bileşen / Modül Adı]
#### [NEW] `yol/yeni_dosya.ext`
- <doldur: Dosyanın amacı ve içereceği temel fonksiyonlar/tipler>

#### [MODIFY] `yol/mevcut_dosya.ext`
- <doldur: Yapılacak somut değişiklikler ve patlama yarıçapı analizi>

#### [DELETE] `yol/silinecek_dosya.ext`
- <doldur: Varsa silinecek dosya gerekçesi>

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
# 1. Kırmızı test doğrulama (Faz 1)
<doldur: test komutu>

# 2. Yeşil test doğrulama (Faz 2)
<doldur: test komutu>

# 3. Birleşik doğrulama kapıları
python .agent/skills/musgoku/scripts/run_all_gates.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - UI/Konsol]:** `<doldur: Eylem>` -> **Beklenen Çıktı:** `<doldur: Görsel sonuç / kanıt>`
2. **[Adım 2 - Veri/Ağ]:** `<doldur: Eylem>` -> **Beklenen Çıktı:** `<doldur: HTTP 200/201 veya DB kaydı>`
3. **[Adım 3 - UX Durumu]:** `<doldur: Eylem>` -> **Beklenen Çıktı:** `<doldur: Skeleton animasyonu -> dolu durum>`

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `<doldur: Olası regresyon / hata>` | `<doldur: Kök neden>` | `<doldur: Rollback veya cerrahi düzeltme komutu>` |
