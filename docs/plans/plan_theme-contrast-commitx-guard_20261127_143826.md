# `check_theme_contrast.py` Token Eşleştirme Onarımı & `commitx` Sıfır-Bypass Protokolü Uygulama Planı

> **Hedef Dal / Sürüm:** `main / v1.50.1` · **Tarih:** `2026-11-27`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `council`, `karpathy-guidelines`, `tdd`, `fix-bug`, `commitx`, `git-release-workflow`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`, `get_project_state`), `sequential-thinking`  
> **İlgili KANBAN Kartı:** `GSW-BUG-005` (Yeni Defect Kartı)  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. [Goal Description] (Amaç & Kapsam)

`FEProjectv1` üzerinde çalıştırılan `commitx` sırasında iki birleşik kök neden tespit edildi:

1. **Teknik Kök Neden (`check_theme_contrast.py:359-615`):**
   - `categorize_variables()` fonksiyonu `--primary-foreground`, `--destructive-foreground`, `--card-foreground`, `--popover-foreground` tokenlarını global `primary_text` içine atıp `--background`/`--card`/`--popover` ile çapraz çarpım (`Cartesian product`) yapıyor.
   - `--secondary` ve `--muted` zemin (surface) tokenları olduğu halde `"muted"` / `"secondary"` alt dize eşleşmesi nedeniyle `muted_text` içine düşürülüp `--background`/`--card`/`--popover` üstünde metin gibi test ediliyor (toplam **21 false-positive**).
   - `"accent"` L384'te körü körüne hariç tutuluyor; ayrıca `--primary`/`--primary-foreground`, `--destructive`/`--destructive-foreground`, `--secondary`/`--secondary-foreground`, `--accent`/`--accent-foreground` gerçek çiftleri **hiç denetlenmiyor** (false-negative).
   - `FEProjectv1/src/index.css` üzerinde gerçek çiftlerin ölçülen WCAG oranları: `:root --primary/--primary-foreground` **5.07:1**, `--destructive/--destructive-foreground` **4.63:1**, `--accent/--accent-foreground` **6.14:1**, `--secondary/--secondary-foreground` **16.44:1**, `--muted/--muted-foreground` **4.35:1**, `--background/--muted-foreground` **4.74:1**; `.dark` bloğunda tüm gerçek çiftler **5.07:1 – 18.97:1** aralığındadır (gerçek hata **0**).
2. **Süreç / Kapı Kök Nedeni (`commitx/SKILL.md` + `mandatory-git-release-workflow.md`):**
   - `run_all_gates.py` `[FAIL]` (`exit 1`) döndürdüğü halde ajan, *"bulgu `PROJECT_BRIEF.md` değişikliğinden kaynaklanmadı ve false-positive"* rasyonalizasyonuyla `commitx` (`c555eb5`, `v1.55.4`, `origin/main` push) icrasını sürdürdü ve `OTONOM SÜRÜM YAYINI TAMAMLANDI` raporu bastı (**Phantom Green**).
   - `commitx/SKILL.md` L25 blokaj kuralı mevcut olsa da *"önceden var olan (pre-existing) / false-positive / kapsam dışı bulgu"* istisnası ve kullanıcı onaylı istisna durumunda zorunlu `⚠️ İSTİSNALI YAYIN` makbuzu açıkça tanımlı değildi.

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: Deterministik Token-Çift WCAG Denetimi ve Sıfır-Bypass CommitX Kapısı
  Scenario: shadcn/ui ve özel tema CSS tokenları sıfır false-positive ve sıfır false-negative ile denetlenir
    Given CSS dosyasında :root ve .dark bloklarında shadcn/ui (--primary/--primary-foreground, --secondary/--secondary-foreground, --muted/--muted-foreground, --destructive/--destructive-foreground, --accent/--accent-foreground, --card/--card-foreground) ve klasik tema (--text-muted, tekil --muted) tokenları tanımlı
    When check_theme_contrast.py çalıştırıldığında
    Then --<stem>-foreground yalnızca kendi --<stem> (veya --<stem>-background) zeminiyle eşleştirilir
    And --secondary / --muted yalnız kendi -foreground partneri yoksa metin olarak sınıflandırılır
    And FEProjectv1/src/index.css 0 hata verirken gerçek düşük kontrastlı (--primary/--primary-foreground < 4.5:1) bir çift E1 ile yakalanır

  Scenario: run_all_gates.py [FAIL] döndüğünde commitx sessiz veya rasyonalize bypass yapamaz
    Given run_all_gates.py en az 1 kapıda [FAIL] döndürdü
    When commitx çalıştırılmak istendiğinde
    Then ajan bulgunun "önceden var" veya "false-positive" olduğunu öne sürerek tek başına commit/tag/push yapamaz
    And önce kök nedeni (kod/CSS veya kapı scriptini) onarır; yalnızca kullanıcı açıkça istisna onayı verirse "⚠️ İSTİSNALI YAYIN" başlığıyla raporlar
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (3-Aşamalı Kör Hakemlik)

3 bağımsız kör hakem (`CSS & Gate Architecture Reviewer`, `Release Governance & QA Reviewer`, `Karpathy Simplicity & Edge-Case Reviewer`) tarafından değerlendirilen seçeneklerin `council_ranker.py` Borda sıralaması:

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Ortalama Derece (Borda) |
|---|---|---|---|:---:|
| **Option A (Kazanan — Yalın/Karpathy)** | `check_theme_contrast.py` içinde deterministik `--<stem>` ↔ `--<stem>-foreground`/`-text` çift eşleştirmesi + `commitx` sıfır-bypass blokajı (CLI waiver bayrağı yok) | Minimum kod (~40–60 satır); shadcn/ui + `themes.css` + `bookmarkManagerProject` tam uyumlu; ajan ödül-korsanlığını (`--allow-known-fail`) önler | Saf halinde kısmi `.dark` override (`combined_store`), `--sidebar-background` ve `--on-<stem>` + `⚠️ İSTİSNALI YAYIN` makbuzu eksik kalabilirdi | **1.33** (2× #1, 1× #2) |
| **Option B (2. Sıra)** | Deklaratif semantik token rolü grafı + `run_all_gates.py` diff-aware triage (`--allow-known-fail`) ve `⚠️ İSTİSNALI YAYIN` | Kısmi `.dark` kalıtımı, `--on-X` ve istisna makbuzu güçlü; cross-file kapılarda net ayrım hedefi | `run_all_gates.py`'ye `--allow-known-fail` koymak ajanların `[FAIL]`'i "pre-existing" diye bypass etmesini kolaylaştırır; cross-file kapılarda diff ataması kırılgandır | **1.67** (1× #1, 2× #2) |
| **Option C (Elendi — 3. Sıra)** | TSX/JSX/CSS Tailwind sınıf kullanım grafı + her repoda `.gate-ignore.json` manifest dosyası | Teorik runtime sınıf eşleşmesi | `cn()`/`cva()` dinamik sınıflarında ve CSS-only testlerde çöker (ağır false-negative); `.gate-ignore.json` borcu kalıcı olarak gizler | **3.00** (3× #3) |

- **Chairman Nihai Sentezi (Option A Omurgası + Option B'den Cerrahi Takviyeler):**
  1. **Option A seçildi** (`run_all_gates.py`'ye **hiçbir bypass/ignore bayrağı eklenmez**; `commitx` kesin sıfır-bypass kalır).
  2. **Hakem 1 & Hakem 3 sentez takviyesi (`check_theme_contrast.py`):**
     - `--<stem>-foreground` / `--<stem>-text` / `--on-<stem>` çiftleri **`combined_store`** (`:root` + parent tema + aktif blok) üzerinden çözülür; böylece `.dark` yalnız `--primary` değerini değiştirdiğinde `:root`'tan miras alınan `--primary-foreground` ile gerçek kontrast ihlali kaçırılmaz (pair tekilleştirmesiyle tekrar raporlanmaz).
     - Partner aramada `--<stem>`, `--<stem>-background`, `--<stem>-bg` desteklenir (shadcn v3 `--sidebar-background` + `--sidebar-foreground` uyumu).
     - `"accent"` kör hariç tutmadan çıkarılır; `--chart-*`, `--ring`, `--border`, `--input`, `--radius`, `--shadow*` denetim dışı tutulur.
     - Bare `--muted` ve `--secondary` yalnız kendi `-foreground` / `-text` partneri yoksa `muted_text` sayılır (böylece `bookmarkManagerProject` `--muted: #6e6e7c` ve `themes.css` `--text-secondary` korunur).
  3. **Hakem 2 sentez takviyesi (`commitx/SKILL.md` + `mandatory-git-release-workflow.md`):**
     - `commitx` protokolüne **Anti-Rationalization (Bahane Yasağı)** eklenir: `[FAIL]` *"önceden var"*, *"dokunulan dosyada değil"* veya *"false-positive"* sayılsa dahi ajan tek taraflı devam edemez; önce hatayı/scripti onarır.
     - Kullanıcı tüm `[FAIL]` detayını gördükten sonra açıkça istisna onayı verirse bile makbuz başlığı `✅ OTONOM SÜRÜM YAYINI TAMAMLANDI` / `[0 başarısız]` olamaz; **`⚠️ COMMITX: İSTİSNALI SÜRÜM YAYINI (Onaylı Mevcut Bulgu)`** formatı zorunlu tutulur.

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)
> [!IMPORTANT]
> Onay sonrası `skillSetWorks/.agent/` altındaki script ve kurallar güncellenip test edilecek; ardından kullanıcı isterse `delivery.py` ile `FEProjectv1` dahil hedef repolara dağıtılacaktır.
>
> **2-Modlu Onay Seçenekleri (Planı Nasıl İlerletelim?):**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan` / `"planı mühürle, kodlama yapma"`):** Planı `docs/plans/` altına arşivler, `HANDOFF.md` §3 ve `KANBAN.md` içine ekler; **kod yazmadan durur**.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onayla ve başla"`):** Faz 0 mühürlemesini yapıp Faz 1 (TDD Kırmızı Test) ile hemen uygulamaya geçer.

## 4. Open Questions (Açık Sorular)
Açık soru bulunmamaktadır. (Not: Kardeş proje dağıtımı `delivery.py` adımının bu oturumda otomatik koşulup koşulmayacağı kullanıcı onayına tabidir.)

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-BUG-005` | `Bekliyor` | `Yapılıyor` → `Yapıldı` (`HANDOFF.md` §3 + `KANBAN.md`) | `S2-25 / check_theme_contrast.py + commitx` |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- **Etkilenen Kardeş Uygulama, Yol & Topoloji:** `FEProjectv1`, `ocai`, `bookmarkManagerProject`, `kalansure` (`delivery.md` hedefleri — farklı dizinlerde; dağıtım kaynağı `skillSetWorks/.agent/`).
- **Kardeş Süreç Etkisi:** Doğrudan kardeş repo kaynak koduna dokunulmaz. `skillSetWorks` üzerinde düzeltme tamamlandıktan sonra `python delivery.py --only FEProjectv1` (veya tüm `enabled: true` projeler) ile `.agent/` güncellenir.
- **Yürütme Sahipliği Sorusu (Dağıtım Onayı):** *"Düzeltme `skillSetWorks/.agent/` içinde tamamlandıktan sonra `python delivery.py` ile `FEProjectv1` (ve diğer aktif projeler) `.agent/` klasörlerini güncelleyeyim mi, yoksa sadece `skillSetWorks` içinde bırakayım mı?"*

### 5.2 🛡️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Matrisi (Pre-Seal Conflict Check)
| Hedef / Yüzey | Sınıflandırma | İlgili Canlı Dosya / Bekleyen Plan | Alınacak Önlem |
|---|---|---|---|
| `.agent/skills/musgoku/scripts/check_theme_contrast.py` | `MODIFY_EXISTING` | Canlı script (L359-713) | Çakışan bekleyen plan yok; cerrahi güncelleme |
| `.agent/skills/ui-ux-pro-max/scripts/tests/test_check_theme_contrast.py` | `MODIFY_EXISTING` | Canlı test paketi (L1-170) | Yeni shadcn/ui + `.dark` + `--muted` regresyon testleri ekle |
| `.agent/skills/commitx/SKILL.md` & `.agent/rules/mandatory-git-release-workflow.md` | `MODIFY_EXISTING` | Canlı kural ve skill | Çift taraflı anti-rationalization + istisna makbuzu |

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (CLI / Kapı Altyapısı Uyarlaması)
| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | Kapsam dışı (Salt CLI / Kalite Kapısı deposu) | `Yok` |
| **2. Backend / Kapı Motoru** | `categorize_variables()` ve `audit_theme_block()` token-çift çözümlemesi + `combined_store` `.dark` miras çifti | `.agent/skills/musgoku/scripts/check_theme_contrast.py` |
| **3. Kural & Orkestrasyon Sözleşmesi** | `commitx` anti-bypass blokajı + `⚠️ İSTİSNALI YAYIN` makbuzu | `.agent/skills/commitx/SKILL.md`, `.agent/rules/mandatory-git-release-workflow.md` |
| **4. Arayüz / UX** | Kapsam dışı (Salt CLI / Kalite Kapısı) | `Yok` |
| **5. Döngü Kapanışı (Regresyon & Dağıtım)** | `test_check_theme_contrast.py` + `tests/run_all.py` + `scripts/sync_agy_global.py` + `delivery.py` | `tests/`, `.agent/skills/ui-ux-pro-max/scripts/tests/` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi
`Tier 0: Salt CLI / Kalite Kapısı & Kural Altyapısı — UI Değişikliği Yok`

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Onay Sonrası Mühürleme
1. **[Adım 1 - Planı Arşivle & Panoyu Güncelle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug theme-contrast-commitx-guard` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_theme-contrast-commitx-guard_<TS>.md` oluşur.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - shadcn/ui, Kısmi `.dark` ve Non-Shadcn Regresyon Testlerini Ekle]:** `.agent/skills/ui-ux-pro-max/scripts/tests/test_check_theme_contrast.py` içine şu 5 testi ekle ve `python -m unittest discover -s .agent/skills/ui-ux-pro-max/scripts/tests` çalıştır -> **Beklenen Çıktı:** Testler **KIRMIZI (FAIL)** verir:
   - `test_shadcn_tokens_no_false_positives` (`FEProjectv1` `:root`/`.dark` token seti -> 0 hata)
   - `test_shadcn_paired_foreground_low_contrast_fails_e1` (`--primary` vs `--primary-foreground` < 4.5:1 -> `[E1]`)
   - `test_shadcn_accent_and_destructive_pairs_checked` (`--accent`/`--accent-foreground` ve `--destructive`/`--destructive-foreground` düşük kontrast -> `[E1]`)
   - `test_partial_dark_override_inherits_pair_from_root` (`.dark` yalnız `--primary` değiştirince `:root` `--primary-foreground` ile `[E1]` yakalar)
   - `test_unpaired_muted_still_checked_as_muted_text` (`bookmarkManagerProject` stili tekil `--muted` düşük kontrast -> `[E2]`)

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
1. **[Adım 1 - `check_theme_contrast.py` Çift Eşleştirme Motorunu Güncelle]:** `.agent/skills/musgoku/scripts/check_theme_contrast.py` içinde:
   - Hariç tutma listesinden `"accent"` çıkarılır; `--chart-*`, `--ring`, `--border`, `--input`, `--radius`, `--shadow*` eklenir.
   - `categorize_variables()` + `audit_theme_block()` içinde `combined_store` üzerinden çift tespiti yapılır (`--<stem>-foreground` / `--<stem>-text` / `--on-<stem>` ↔ `--<stem>` / `--<stem>-background` / `--<stem>-bg`).
   - Eşleşmiş çiftler **yalnız kendi zeminleriyle** test edilir; `--background`/`--card`/`--popover` üzerine yalnız genel metin (`--foreground`, `--text*`, `--ink*`) ve kendi partneri olmayan bare `--muted`/`--secondary` düşer (`--muted-foreground` hem `--muted` hem temel yüzeylerde ≥ 3.0:1 test edilir).
   - `python -m unittest discover -s .agent/skills/ui-ux-pro-max/scripts/tests` çalıştır -> **Beklenen Çıktı:** Tüm testler **YEŞİL (PASS)** döner.

### 🧩 Faz 3: `commitx` Sıfır-Bypass Protokolü & Global Senkron
1. **[Adım 1 - `commitx/SKILL.md` ve `mandatory-git-release-workflow.md` Güncelle]:**
   - `commitx/SKILL.md` §1 Blokaj Kuralına *"önceden var olan (pre-existing), dokunulan diff dışında kalan veya false-positive sanılan `[FAIL]` dahil hiçbir `[FAIL]` tek taraflı atlanamaz"* maddesini ve kullanıcı onaylı istisnada zorunlu `⚠️ COMMITX: İSTİSNALI SÜRÜM YAYINI` şablonunu ekle.
   - `mandatory-git-release-workflow.md` §6'ya *"Kapsam-duyarlı derleme atlama kuralı, `run_all_gates.py` içindeki mevcut `[FAIL]` bulgularını sessizce geçme yetkisi vermez"* şerhini ekle.
   - -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/rules_gates.py --strict` ve `python tests/test_rule_gates.py` **PASS** döner.

### 🧹 Faz 4: Doğrulama, Global Plugin & Dağıtım
1. **[Adım 1 - Gerçek `FEProjectv1` Doğrulaması]:** `python .agent/skills/musgoku/scripts/check_theme_contrast.py --root C:\devtools\vscodeWS\peopleside-culture\FEProjectv1` çalıştır -> **Beklenen Çıktı:** **0 hata** (`[OK]`, önceki 21 false-positive sıfırlanır).
2. **[Adım 2 - Tam Test & Kapı Paketi]:** `python tests/run_all.py` ve `python .agent/skills/musgoku/scripts/run_all_gates.py` çalıştır -> **Beklenen Çıktı:** Tüm paketler ve kapılar `[OK]`.
3. **[Adım 3 - Global Plugin & Hedef Proje Dağıtımı (Onaylı)]:** `python scripts/sync_agy_global.py` ardından ⚠️ CRITICAL: hedef repoların çalışma ağacını güncelleyeceği için kullanıcı onayıyla `python delivery.py --only FEProjectv1` (veya tüm projeler) çalıştır -> **Beklenen Çıktı:** `delivery.py --verify` `TEMIZ` döner.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

#### [MODIFY] `.agent/skills/musgoku/scripts/check_theme_contrast.py`
- `categorize_variables()` (L359-411) ve `audit_theme_block()` (L414-615): Generic stem-pair çözümlemesi (`--<stem>-foreground` / `--<stem>-text` / `--on-<stem>` ↔ `--<stem>` / `--<stem>-background`), `combined_store` üzerinden kısmi `.dark` miras çifti denetimi, `--chart-*`/`--ring`/`--border`/`--input` dışlaması, `"accent"` kör dışlamasının kaldırılması.

#### [MODIFY] `.agent/skills/ui-ux-pro-max/scripts/tests/test_check_theme_contrast.py`
- shadcn/ui `:root`/`.dark`, düşük kontrastlı paired token `[E1]`, kısmi `.dark` mirası ve tekil `--muted` regresyon testleri.

#### [MODIFY] `.agent/skills/commitx/SKILL.md`
- Sıfır-bypass netleştirmesi (pre-existing / false-positive dahil tek taraflı atlama yasağı) ve `⚠️ COMMITX: İSTİSNALI SÜRÜM YAYINI` rapor şablonu.

#### [MODIFY] `.agent/rules/mandatory-git-release-workflow.md`
- §6 altına `run_all_gates.py` `[FAIL]` blokajının `commitx` sırasında docs-only diff bahanesiyle aşılamayacağı kuralı.

#### [MODIFY] `knowledge-base.md` & `HANDOFF.md` & `docs/KULLANICI_TEST_REHBERI.md`
- Kalıcı Council kararının ve yeni senaryonun işlenmesi (uygulama aşamasında).

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests
```bash
python -m unittest discover -s .agent/skills/ui-ux-pro-max/scripts/tests
python .agent/skills/musgoku/scripts/check_theme_contrast.py --root C:\devtools\vscodeWS\peopleside-culture\FEProjectv1
python tests/run_all.py
python .agent/skills/musgoku/scripts/run_all_gates.py
```

### Manual Verification (FAA AC 121-24C)
1. **[Adım 1 - `FEProjectv1` Kontrast Kapısı]:** `python .agent/skills/musgoku/scripts/check_theme_contrast.py --root C:\devtools\vscodeWS\peopleside-culture\FEProjectv1` çalıştır -> **Beklenen Çıktı:** `21 hata` yerine `[OK]` (0 kritik hata).
2. **[Adım 2 - `skillSetWorks` Tam Regresyon]:** `python tests/run_all.py` çalıştır -> **Beklenen Çıktı:** Tüm test paketleri `BAŞARIYLA GEÇTİ`.

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `themes.css` veya `bookmarkManagerProject` üzerinde beklenmedik yeni `[E1]/[E2]` | Tekil (`--muted`, `--text-secondary`) tokenların yanlışlıkla `paired` sanılması | `check_theme_contrast.py` içinde partner arama yalnız gerçek zemin partneri (`combined_store` içinde `--<stem>` varlığı) şartına bağlanır |
| `.dark` bloğunda aynı hata `:root` ile iki kez basılıyor | Miras çiftlerin deduplikasyonu eksik | `audit_theme_block()` yalnız aktif blokta override edilen değişkenlerden biri dahilse çifti test eder |
| `delivery.py` sonrası hedef projede yerel `.agent/` farkı | Önceki sürümün `yedekler/` altına yedeklenmesi gerekebilir | `python delivery.py --dry-run` ile diff gör, gerekirse `yedekler/` altından geri al |
