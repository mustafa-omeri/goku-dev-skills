# Dış / Yeni PRD Değerlendirme Orkestratörü (`/review-prd`) Uygulama Planı
<!--
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2
-->

> **Hedef Dal / Sürüm:** `main / skillSetWorks v1.38.0` · **Tarih:** `2026-11-17`  
> **Görevlendirilen Skill'ler:** `feature-architect`, `council`, `doc-coauthoring`, `musgoku`, `tdd`  
> **Kullanılan MCP'ler:** `second-brain-vault`, `sequential-thinking`  
> **İlgili Görev Kimlikleri:** `GSW-PRDR-001`, `GSW-PRDR-002`, `GSW-PRDR-003`  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. Goal Description (Mevcut Durum Tespiti, Amaç & Kapsam)

### Mevcut Durum Analizi
Skillset'te şu an PRD ve konsey değerlendirmesiyle ilgili bileşenler **ayrı adalar** halinde bulunmaktadır:
- `cognitive-counsel-framework.md` (`/6HAT`, `/PO`, `/ARCH`, `/UX`, `/SEO`, `/GRW`, `/QA`, `/PUSHBACK`): Metni/fikri 6 uzman perspektifi ve Anti-Sycophancy filtreleriyle (`REDTEAM`, `80/20`, `KILLCRITIC`, `TRUTHMODE`, `LINDYMODE`, `ELI5`) sınar; fakat proje kod tabanını deterministik taramaz, kalıcı rapor üretmez ve `/plan`'a otomatik bağlanmaz.
- `council` (`/council` + `council_ranker.py`): 2+ alternatifli mimari ikilemleri Borda skoruyla oylar ve `knowledge-base.md` / `docs/adr/` yazar; tüm PRD'nin uçtan uca denetimini yapmaz.
- `feature-architect` (`/feature-architect --mode=council` + `fa_scan.py` + `council_merger.py`): Mevcut koddaki stub/404/yetim eksikleri 6 şapkayla denetler; dışarıdan verilen yeni bir taslak PRD'yi girdi olarak alıp mevcut projeyle çarpıştırmaz.
- `verify-prd` (`/verify-prd`): Zaten **geliştirilmiş** özelliklerin retrospektif 5 katman denetimidir (geliştirme öncesi PRD eleştirisi değildir).
- `doc-coauthoring`: Sıfırdan doküman yazma akışıdır.

### Amaç
Kullanıcının elindeki bir PRD'yi (`docs/...-prd.md` veya sohbete yapıştırılan metin) verip hedef projeye göre:
1. Mevcut kod tabanı, `PROJECT_BRIEF.md`, `PRODUCT.md`, `DESIGN.md` ve varsa kardeş uygulama (`--peer`) ile deterministik çarpıştırma (`fa_scan.py` + PRD gereksinim matrisi),
2. **6 Şapkalı Konsey (`PO`, `ARCH`, `UX`, `SEO`, `GRW`, `QA`)** + **Anti-Sycophancy (`PUSHBACK`)** + **Borda Hakemliği (`council_ranker.py`)** ile derin fizibilite, eksik Gherkin, OWASP güvenlik ve tema/iskelet uyumu değerlendirmesi,
3. **GO / CONDITIONAL GO / REWORK** kararıyla kalıcı rapor (`docs/plans/prd-review-<slug>-<YYYYMMDD_HHMMSS>.md`) üretip kullanıcı onayı sonrası `/plan` → `HANDOFF.md` §3 → (varsa) kardeş `HANDOFF.md` akışına bağlayan **tek komutlu `/review-prd`** orkestrasyonunu kurmak.

### Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: Dış / Yeni PRD Değerlendirme Orkestratörü (/review-prd)
  Scenario: Verilen PRD mevcut proje kod tabanı ve 6 Şapkalı Konsey ile değerlendirilir
    Given Kullanıcı "/review-prd <prd-dosyasi>" komutuyla veya sohbet metniyle bir PRD sunar
    When Orkestratör "prd_context_scanner.py" ve "fa_scan.py" ile mevcut kod/API/DB/kardeş-repo gerçekliğini toplar
    Then 6 Şapka (PO, ARCH, UX, SEO, GRW, QA), Anti-Sycophancy ve Council Borda oylamasıyla PRD değerlendirme raporu üretilir
    And Rapor kod geliştirmeye başlamadan önce kullanıcı onayına (Strict Approval Gate) sunulur
    And Onay sonrası yalnızca seçilen/revize edilen maddeler "/plan" ve "HANDOFF.md" §3 akışına aktarılır
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Müstakil `review-prd` Skill + `prd_review_helper.py` — ÖNERİLEN)** | `.agent/skills/review-prd/` altında odaklı orkestratör skill (`SKILL.md` + `prd-review-template.md` + `prd_review_helper.py`) açıp `council`, `feature-architect` (`fa_scan.py` + 6 şapka), `cognitive-counsel-framework` ve `doc-coauthoring`'i zincirlemek; `/review-prd` slash komutunu eklemek | `verify-prd` (retrospektif kod denetimi) ile sıfır kavram kargaşası; net slash komutu (`/review-prd`); mevcut `fa_scan.py` ve `council_ranker.py` araçlarını yeniden kullanır (sıfır kod tekrarı) | `bin/cli.js` (`SKILLS_MANIFEST`, `PROFILES`), `generate_skills_catalog.py` (`CATEGORIES`, `CONFIG_METADATA`, `SLASH_COMMANDS`) ve `skills-catalog.html` senkronu gerektirir (mevcut `test_skills_catalog.py` ve `test_cli_profiles.py` ile otomatik doğrulanır) | `2.7` |
| **Option B (`feature-architect` içine `--prd` bayrağı eklemek)** | Yeni skill açmadan `feature-architect` içine `--prd <yol>` modu ve `/review-prd` alias'ı eklemek | Skill sayısı 48'de kalır, `bin/cli.js` profil güncellemesi gerekmez | `feature-architect` zaten 6 şapka JSON sözleşmesi ve kod boşluğu taramasıyla çok yüklü; yeni PRD eleştirisi/puanlama mantığı bağlamı şişirir | `2.0` |

- **Seçilen Yol & Gerekçe:** **Option A** önerilmektedir; çünkü geliştirme **öncesi** PRD fizibilite & konsey incelemesi (`/review-prd`) ile geliştirme **sonrası** kod doğrulaması (`/verify-prd`) farklı yaşam döngüsü adımlarıdır ve ayrı net bir giriş noktası kullanıcı için sürtünmeyi sıfırlar. (Ancak kullanıcı daha sade tek-skill yaklaşımını isterse Option B seçilebilir.)

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)

> [!IMPORTANT]
> **1. Strict Approval Gate (Değerlendirme Sırasında Koda Dokunma Yasağı):**
> `/review-prd` yalnızca mevcut kod tabanını okur, PRD'yi 6 şapka ve Borda hakemliğiyle değerlendirir, eksikleri/çelişkileri/alternatifleri ve **GO / CONDITIONAL GO / REWORK** kararını raporlar. Kullanıcı onaylayıp `/plan`'a geçirmedikçe hiçbir üretim koduna dokunmaz.

> [!NOTE]
> **Kardeş Uygulama Köprüsü:** Değerlendirilen PRD kardeş uygulamayı da etkiliyorsa (`v1.37.0` kuralı gereği) onay sonrası kardeş `HANDOFF.md` mühürleme ve AI Agent sahiplik sorusu otomatik devreye girer.

---

## 4. Open Questions (Açık Sorular)
1. **Mimari Tercih:** Yeni bir `review-prd` skill'i + `/review-prd` komutu (**Option A — Önerilen**) mı kuralım, yoksa mevcut `feature-architect` içine `--prd` modu (**Option B**) olarak mı ekleyelim?
2. **Mevcut bir PRD'niz şu an hazır mı?** Eğer hemen şu an değerlendirmek istediğiniz bir PRD dosyası/metni varsa paylaşabilirsiniz — dilerseniz önce elinizdeki PRD'yi mevcut yapıyla hemen değerlendirip, ardından `/review-prd` altyapısını kalıcı olarak sisteme ekleyebiliriz.

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)

| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / Modül |
|---|---|---|---|
| `GSW-PRDR-001` | `Bekliyor` | `Yapılıyor` (`HANDOFF.md` §3) | `.agent/skills/review-prd/scripts/prd_review_helper.py` + TDD testleri (`tests/test_review_prd.py`) |
| `GSW-PRDR-002` | `Bekliyor` | `Bekliyor` | `.agent/skills/review-prd/SKILL.md`, `references/prd-review-template.md`, `skill-trigger-routing.md`, `AGENTS.md` |
| `GSW-PRDR-003` | `Bekliyor` | `Bekliyor` | `bin/cli.js`, `scripts/generate_skills_catalog.py`, `.agent/skills-catalog.html`, `tests/run_all.py`, `delivery.py` dağıtımı |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- `Tek Repo / Kardeş Uygulama Etkisi Yok` *(Bu çalışma `skillSetWorks` üzerinde skillset orkestrasyonunu ekler; üretilen `/review-prd` yapısı ise hedef projelerde kardeş repo etkisini otomatik kontrol eder.)*

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. Şablon & Sözleşme** | PRD Değerlendirme Rapor şablonu (`GO / CONDITIONAL GO / REWORK`, 6 Şapka Matrisi, Mevcut Kod Çakışma/Hazırlık Matrisi, 5 Katman Fizibilite, Borda Seçenekleri) | `.agent/skills/review-prd/references/prd-review-template.md` |
| **2. Deterministik Yardımcı (CLI)** | `prd_review_helper.py`: PRD başlık/FR/US/Gherkin ayrıştırma, eksik kabul kriteri / belirsiz ifade tespiti, mevcut proje dokümanları (`PRODUCT.md`, `PROJECT_BRIEF.md`, `DESIGN.md`) ve `fa_scan.py` özetiyle bağlam paketi üretimi + rapor arşivleme | `.agent/skills/review-prd/scripts/prd_review_helper.py` |
| **3. Skill & Kural Yönlendirmesi** | `review-prd/SKILL.md` orkestratörü, `skill-trigger-routing.md` (§0, §A4, §A5 `/review-prd`), `verify-prd` ile sınır ayrımı | `.agent/skills/review-prd/SKILL.md`, `.agent/rules/skill-trigger-routing.md` |
| **4. Katalog & CLI Dağıtım** | `bin/cli.js` (`SKILLS_MANIFEST`, `PROFILES`), `scripts/generate_skills_catalog.py` (`/review-prd` + `review-prd` metadata), `.agent/skills-catalog.html` | `bin/cli.js`, `scripts/generate_skills_catalog.py`, `.agent/skills-catalog.html` |
| **5. Doğrulama & Dağıtım** | `tests/test_review_prd.py`, `tests/run_all.py`, `run_all_gates.py`, `delivery.py --keep 1` & `--verify` | `tests/test_review_prd.py`, `tests/run_all.py` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi
- `Salt CLI / Kural / Markdown Şablonu — UI Kapsam Dışı`

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams)

### 📌 Faz 0: Onay Sonrası Mühürleme
- `archive_plan.py` ile plan `docs/plans/` altına arşivlenir, `HANDOFF.md` §3 panosuna `GSW-PRDR-001..003` işlenir.

### 🔴 Faz 1: Kırmızı Test (`tests/test_review_prd.py`)
1. PRD markdown içinden gereksinim (`FR`/`US`/başlık), Gherkin eksikliği ve belirsiz ifadelerin ("hızlı", "kullanıcı dostu", "vb.") çıkarılması.
2. Proje kökünden `PROJECT_BRIEF.md`, `PRODUCT.md`, `DESIGN.md` ve `fa_scan` özetinin okunup bağlam JSON'una dönüştürülmesi.
3. Değerlendirme raporunun `docs/plans/prd_review_<slug>_<YYYYMMDD_HHMMSS>.md` olarak arşivlenmesi.
4. `test_skill_contracts.py`, `test_skills_catalog.py`, `test_cli_profiles.py` bütünlük kontrolleri.

### 🟢 Faz 2..4: Minimal Yeşil Kod → Kurallar/Katalog/CLI → Tam Test & `delivery.py` Dağıtımı

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)
- #### [NEW] `.agent/skills/review-prd/SKILL.md`
- #### [NEW] `.agent/skills/review-prd/references/prd-review-template.md`
- #### [NEW] `.agent/skills/review-prd/scripts/prd_review_helper.py`
- #### [NEW] `tests/test_review_prd.py`
- #### [MODIFY] `.agent/rules/skill-trigger-routing.md`, `.agent/skills/verify-prd/SKILL.md`
- #### [MODIFY] `bin/cli.js`, `scripts/generate_skills_catalog.py`, `.agent/skills-catalog.html`, `tests/run_all.py`

---

## 10. Verification Plan (Doğrulama Planı)
```bash
python tests/test_review_prd.py
python tests/test_skills_catalog.py
python tests/test_cli_profiles.py
python .agent/skills/musgoku/scripts/run_all_gates.py
python tests/run_all.py
python delivery.py --keep 1 && python delivery.py --verify
```

---

## 11. 🚨 Ditching & Emergency Exit
| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `test_cli_profiles.py` başarısız | Yeni skill `bin/cli.js` profillerine eklenmedi | `SKILLS_MANIFEST` ve `PROFILES.fullstack` içine `review-prd` ekle |
| `test_skills_catalog.py` başarısız | `CATEGORIES` veya `CONFIG_METADATA` eksik | `scripts/generate_skills_catalog.py` güncelle ve yeniden derle |
| `test_skill_contracts.py` başarısız | `SKILL.md` description kelime/tetikleyici sınırı | `SKILL.md` `description` alanını sözleşmeye göre ayarla |
