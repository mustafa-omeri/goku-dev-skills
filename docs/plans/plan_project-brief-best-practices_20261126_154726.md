# PROJECT_BRIEF.md Best-Practice (Zero-Scan AI Memory) Uygulama Planı

> **Hedef Dal / Sürüm:** `main` · **Tarih:** `2026-11-26`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `council`, `karpathy-guidelines`, `musgoku`, `tdd`  
> **Kullanılan MCP'ler:** `context7` (`/websites/agents_md`, `/answerdotai/llms-txt`), `second-brain-vault` (`bootstrap`), `sequential-thinking`  
> **İlgili KANBAN Kartı:** `SKL-ARCH-PB01` (Yeni Kart)  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. [Goal Description] (Amaç & Kapsam)

Mevcut `PROJECT_BRIEF.md` mimarisi (`project-brief-maintenance.md` + `PROJECT_BRIEF.template.md`), AI kod ajanına makro teknoloji yığınını ve dizin yapısını veriyor; ancak endüstri standartları (`AGENTS.md` ve `llms.txt`) açısından ajanın projeyi taramadan (zero-scan) doğrudan çalışmaya başlaması için kritik operasyonel bilgileri (**çalıştırma/test/build komutları**, **giriş noktaları / ana rotalar**, **ortam değişkeni anahtarları & güvenlik sınırları**) standart olarak içermiyor.

Bu plan, `PROJECT_BRIEF.md`'yi changelog şişkinliğine düşürmeden **AGENTS.md + llms.txt Hibriti (Zero-Scan Operasyonel Brief)** standardına yükseltir ve `check_project_brief.py` kapısını buna göre günceller.

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: Zero-Scan Operational Project Brief
  Scenario: AI ajanı yalnızca PROJECT_BRIEF.md okuyarak projeyi başlatabilir ve doğrulayabilir
    Given yeni bir AI kod ajanı oturumu açılmıştır
    When ajan yalnızca kök dizindeki PROJECT_BRIEF.md dosyasını okur
    Then ajanın tüm repoyu taramadan dev/build/test/gate komutlarını, ana giriş noktalarını, env anahtarlarını ve doküman indeksini bilmesi gerekir
    And python .agent/skills/musgoku/scripts/check_project_brief.py kapısı exit 0 dönmelidir
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (3 Seçenek İncelemesi)

`context7` üzerinden alınan `AGENTS.md` ve `llms.txt` best practice'leri temelinde 3 körleştirilmiş alternatif `council_ranker.py` ile oylandı:

| Sıra | Aday | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Ortalama Derece | 1.lik Oyu |
|:---:|---|---|---|---|---:|:---:|
| **#1** | **Option B (Kazanan)** | **Zero-Scan Operasyonel Brief (`AGENTS.md` + `llms.txt` Hibriti)** | Komutlar, entry point'ler, env anahtarları (değersiz), makro omurga ve detay linkleri tek kompakt belgede (`<150` satır); rutin UI/iş mantığında drift üretmez | Şablon ve `check_project_brief.py` `W2` bölüm listesi güncellemesi gerektirir | **1.00** | **3 / 3** |
| **#2** | **Option A** | **Minimalist İndeks (`llms.txt` tarzı)** | Sıfır şişkinlik, en düşük bakım maliyeti | Ajan yine `package.json`, `.env.example` ve giriş dosyalarını taramak zorunda kalır | **2.33** | 0 / 3 |
| **#3** | **Option C** | **Monolitik Tam Bellek Dökümü** | İlk okumada tüm sembol ve payload'lar hazır | Context penceresini şişirir, her commit'te bayatlar ve `git diff` gürültüsü yaratır | **2.67** | 0 / 3 |

- **Chairman Nihai Kararı & Gerekçesi:** **Option B** oybirliğiyle (3/3 birincilik, `1.00` ortalama derece) seçildi. `AGENTS.md` standardının **komut + test + güvenlik sınırları** kuralını ve `llms.txt` standardının **kısa indeks + detay doküman linki** disiplinini birleştirir; `Option C`'deki token şişkinliğinden ve `Option A`'daki kör tarama maliyetinden kaçınır.

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)

> [!IMPORTANT]
> **Mimari Karar:** `PROJECT_BRIEF.md` içinde `.env` **değerleri** asla tutulmaz; yalnızca **anahtar adları ve amacı** (örn. `DATABASE_URL` — PostgreSQL bağlantısı) listelenir. Aksi halde gizli anahtar sızıntısı oluşur.
>
> **Geriye Dönük Uyumluluk:** `check_project_brief.py` yeni operasyonel bölümü (`Komutlar & Giriş Noktaları`) ilk aşamada **uyarı (`W2`)** olarak denetleyecek; mevcut projelerin `exit 1` ile kırılmasını önleyecektir.
>
> **2-Modlu Onay Seçenekleri:**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan` / `"planı mühürle, kodlama yapma"`):** Planı `docs/plans/` altına arşivler, `HANDOFF.md` §3 ve `KANBAN.md`'ye ekler; kod yazmadan durur.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onayla ve başla"`):** Faz 1 (TDD kırmızı test) ile uygulamaya geçer.

## 4. Open Questions (Açık Sorular)
Açık soru bulunmamaktadır (mevcut `skillSetWorks` kapı mimarisi ve `context7` standartları net).

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu

| Görev ID | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `SKL-ARCH-PB01` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3 + `KANBAN.md`) | `PROJECT_BRIEF` Best-Practice Yükseltmesi |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi
Tek Repo / Kardeş Uygulama Etkisi Yok (`delivery.py` şablon güncellemesini sonraki dağıtımda projelere taşır).

---

## 6. Proposed Changes (Uygulanacak Değişiklikler)

> ⚠️ CRITICAL: Mevcut `check_project_brief.py` `STANDARD_SECTIONS` listesi değiştirildiğinde tüm `tests/test_project_brief.py` fixture'ları eşzamanlı güncellenmelidir; aksi halde mevcut projelerde yanlış `W2` uyarısı üretilir.

### Bileşen 1: Şablon ve Kural Katmanı (`.agent/`)

#### [MODIFY] [PROJECT_BRIEF.template.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/templates/PROJECT_BRIEF.template.md)
- Mevcut 5 bölüme ek olarak `AGENTS.md` + `llms.txt` uyumlu **2 kompakt operasyonel bölüm** eklenir (`§2` sonrası ve `§5` öncesi):
  - **`## 2.1. Komut Haritası & Giriş Noktaları (Zero-Scan Cockpit)`**:
    - Kurulum / Dev / Build / Test / Lint / Gate komutları tablosu
    - Ana giriş noktaları (`entry_points`) ve temel API/CLI yüzeyleri
    - Zorunlu `.env` anahtar adları (değer yasak!)
  - **`## 3. Bağlayıcı Kararlar & Detay İndeksi (llms.txt Pattern)`**:
    - `HANDOFF.md`, `knowledge-base.md`, `DB_MIGRATIONS.md`, `docs/kullanici-rehberi.html` için kısa "ne zaman oku" açıklamalı indeks.

#### [MODIFY] [project-brief-maintenance.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/project-brief-maintenance.md)
- `§1.1 (5 Anayasal Koşul)` içine **6. Koşul** olarak `Giriş Noktası, Build/Test Komutu veya .env.example Anahtar Değişikliği` eklenir.
- "Gizli anahtar değeri yazma yasağı (yalnızca env key adı)" açıkça kurala bağlanır.

---

### Bileşen 2: Deterministik Doğrulama Kapısı & Testler (`scripts/` & `tests/`)

#### [MODIFY] [check_project_brief.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/scripts/check_project_brief.py)
- `STANDARD_SECTIONS` listesine `"Komut Haritası"` eklenir (`W2` uyarısı).
- Opsiyonel güvenlik kontrolü: `PROJECT_BRIEF.md` içinde açık API key / token deseni (`sk-...`, `ghp_...`, `AKIA...`) varsa `E8` veya uyarı verilmesi için `SECRET_PATTERNS` kontrolü eklenir.
- `INFRA_EDGE_FILES` içine `.env.example` eklenir (değiştiğinde `PROJECT_BRIEF.md` env anahtarları senkronize edilsin).

#### [MODIFY] [test_project_brief.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/tests/test_project_brief.py)
- `VALID_BRIEF` fixture'ına `## Komut Haritası & Giriş Noktaları` bölümü eklenir.
- Yeni testler:
  1. `Komut Haritası` eksikse `W2` uyarısı tetiklenir.
  2. `.env.example` değiştiğinde `E6` drift yakalanır (mocked git status ile).
  3. Sahte secret token yazılırsa güvenlik uyarısı/hatası tetiklenir.

---

### Bileşen 3: Kök `PROJECT_BRIEF.md` Senkronizasyonu

#### [MODIFY] [PROJECT_BRIEF.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/PROJECT_BRIEF.md)
- `skillSetWorks` kök `PROJECT_BRIEF.md` dosyasına `Komut Haritası & Giriş Noktaları` (`tests/run_all.py`, `rules_gates.py`, `delivery.py`, `bin/cli.js`) ve `llms.txt` tarzı detay indeksi eklenir.

---

## 7. Verification Plan (Doğrulama Planı)

### Automated Tests
1. [Adım 1]. `python tests/test_project_brief.py` -> Tüm `PASS`, `failures == []`, `exit 0`.
2. [Adım 2]. `python .agent/skills/musgoku/scripts/check_project_brief.py` -> `[OK] PROJECT_BRIEF.md doğrulandı`, `exit 0`.
3. [Adım 3]. `python tests/run_all.py` -> 40+ test paketinin tamamı `PASS`, `exit 0`.

### Manual Verification
1. [Adım 1]. [PROJECT_BRIEF.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/PROJECT_BRIEF.md) dosyasını aç -> Dosyanın `150` satır altında kaldığını ve `Komut Haritası` tablosunun kopyala-yapıştır çalışır komutlar içerdiğini doğrula.

---

## Acil Durum / Kurtarma Tablosu (FAA AC 121-24C)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `W2: Standart mimari bölümü eksik` | Eski `PROJECT_BRIEF.md` dosyalarında `Komut Haritası` başlığı yok | `## 2.1. Komut Haritası & Giriş Noktaları` bölümünü ekle |
| `E6: Altyapı/Env sapması` | `.env.example` güncellendi ama `PROJECT_BRIEF.md` güncellenmedi | Env anahtar adını (değersiz) `PROJECT_BRIEF.md` tablosuna işle |
| `tests/run_all.py` içinde fixture hatası | `test_project_brief.py` içindeki `VALID_BRIEF` güncellenmedi | `VALID_BRIEF` içine yeni zorunlu başlığı ekle |
