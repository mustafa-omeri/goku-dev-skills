# UI/UX Ön-Tasarım Önizleme, Tel Kafes (Wireframe) ve `--ui-preview` (`--ui-ux`) 1:1 Gerçek Ekran Garantisi Uygulama Planı (`FAA AC 121-24C`)

> **Durum:** Nihai Plan — `S1..S5` Kararları Kilitlendi (`/seal-plan` veya `Proceed` Onayı Bekliyor) · **Borda Seçimi:** `Option B` (`1.00`, `4/4` oy)

---

## 1. Goal Description (Amaç ve Kapsam)

Frontend tarafını etkileyen her planda (doğrudan `/plan` ile açılan, `/seal-plan` ile mühürlenen veya kardeş bir repodan `sync_sibling_handoff.py` ile gelen işlerde), kod yazılmadan önce projenin mevcut `<repo-kök>/DESIGN.md` sözleşmesine bakılarak:
1. **Varsayılan (`Tier 1`):** Plan dosyası içinde renksiz, sade **ASCII/Kutu `Before -> After` Tel Kafes (Wireframe)** ile ekranın mevcut hali ve geliştirme sonrası alacağı halin kullanıcı onayına sunulması.
2. **`--ui-preview` (Kısa Alias: `--ui-ux`) Gerçek Ekran Modu (`Tier 3`):** Kullanıcı `--ui-preview` veya `--ui-ux` bayrağı verdiğinde, soyut kutu yerine **projenin mevcut gerçek ekran kodları ve `DESIGN.md` tokenları** kullanılarak tarayıcıda açılan canlı `Mevcut Gerçek Ekran [Before] <-> Planlanan Gerçek Ekran [After]` HTML önizlemesi üretilmesi ve onaylandığında **`UI-PREVIEW-LOCK` (1:1 Birebir Ekran Sadakat Kilidi)** ile kodlanan ekranın onaylanan önizlemeyle birebir aynı olmasının garanti edilmesi.
   *(Not: Kabuk/terminal ortamlarında `&` karakteri komut ayırıcı operatör olduğu için `--UI&UX` yerine kabuk-güvenli **`--ui-preview`** birincil bayrak, **`--ui-ux`** ise eşanlamlı kısa bayrak olarak seçilmiştir; doğal dilde kullanıcının `--UI&UX` yazması da aynı tetikleyiciye bağlanır).*

---

## 2. 🏛️ Council Deliberation & Kilitlenen Kullanıcı Kararları (`S1–S5`)

| Karar ID | Konu | Kilitlenen Karar (`S1–S5`) |
|---|---|---|
| **S1** | Varsayılan Format & Gerçek Ekran Bayrağı | Varsayılan: Plan `.md` içinde renksiz **ASCII/Kutu `Before -> After` Wireframe**. Kullanıcı **`--ui-preview`** (`--ui-ux` / `"--UI&UX"`) derse mevcut gerçek ekran DOM + `DESIGN.md` kullanılarak gerçek ekran üzerinde değişiklik gösterilir ve onayda **`UI-PREVIEW-LOCK` ile 1:1 aynı ekran garantisi** uygulanır. |
| **S2** | 4 Seviyeli Ön-Tasarım Matrisi | **Tier 0** (Bypass: Backend/tek satır CSS) · **Tier 1** (Varsayılan: `DESIGN.md` + ASCII `Before -> After` Wireframe) · **Tier 2** (+ `User Flow / Site Haritası`) · **Tier 3** (`--ui-preview` / `--ui-ux` Gerçek Ekran `Prototype` / `Mockup` + `1:1 Lock`). |
| **S3** | `/seal-plan` & `archive_plan.py` Kapısı | UI dosyası etkilenip planda Wireframe yoksa **`[WARN] [UI-WIREFRAME-MISSING]`** uyarısı basar; uyarı istenmiyorsa **`--allow-no-wireframe`** ile sessizce geçilir. |
| **S4** | Kardeş Repo (`sync_sibling_handoff.py`) | Kaynak plan *UI Etki Beklentisi* yazar; `sync_sibling_handoff.py --ui-wireframe-expected` kardeş frontend reposunun `HANDOFF.md` / `KANBAN.md` / `SPRINT_PLAN.md` görevine **`[UI-ÖN-TASARIM ZORUNLU]`** notu işler; asıl `DESIGN.md` + Wireframe kardeş frontend ajanında çizilip onaylanır. |
| **S5** | Tek Paket Teslimat | `PLAN.template.md`, kurallar, `archive_plan.py`, `sync_sibling_handoff.py`, `skills-catalog.html` ve birim testleri tek pakette güncellenir. |

---

## 3. User Review Required

> [!IMPORTANT]
> - **Açık Soru Kalmadı (`0 Open Questions`):** `S1–S5` yanıtlarınız plana eksiksiz işlendi.
> - **`UI-PREVIEW-LOCK` 1:1 Birebir Garantisi:** `--ui-preview` (`--ui-ux`) ile onaylanan gerçek ekran önizlemesinde hedef ekran yolu, DOM/layout imzası (`grid`/`flex` yerleşimi, bileşen sırası) ve `DESIGN.md` semantik tokenları plana mühürlenir; Faz 3/4 kodlamasında onaylanan önizlemeden sapılması (`Preview Drift`) kural ihlali sayılır.

---

## 4. Open Questions

Açık soru bulunmamaktadır (`S1–S5` kullanıcı kararlarıyla kapatıldı).

---

## 5. 📋 Görev & Sprint/KANBAN Etkisi (`[DOM]-[TIP]-[NO]`)

| Görev ID | Başlangıç | Hedef | Faz / Sprint |
|---|---|---|---|
| `GSW-FEAT-021` | `Bekliyor` | `Yapıldı` (`HANDOFF.md` §3 + `KANBAN.md`) | `S2-21` — UI/UX Ön-Tasarım Wireframe & `--ui-preview` 1:1 Kilit Kapısı |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- **Etkilenen Kardeş Uygulama, Yol & Topoloji:** `Tek Repo / Kardeş Uygulama Etkisi Yok` (ancak `sync_sibling_handoff.py` içine kardeş frontend projelerine UI Wireframe beklentisi aktaran `--ui-wireframe-expected` desteği eklenmektedir).

### 5.2 🛡️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Matrisi (Pre-Seal Conflict Check)

| Hedef / Yüzey | Sınıflandırma | İlgili Canlı Dosya / Bekleyen Plan | Alınacak Önlem |
|---|---|---|---|
| `.agent/templates/PLAN.template.md` | `ENRICHED_SUPERSET` | Canlı şablon (§7 mevcut) | `[MODIFY]` ile §7.1 UI/UX Ön-Tasarım & `UI-PREVIEW-LOCK` alt bölümü ekle |
| `.agent/skills/musgoku/scripts/archive_plan.py` | `ENRICHED_SUPERSET` | Canlı script (`plan_conflict_guard` mevcut) | `[MODIFY]` ile `check_ui_predesign_plan()` + `--allow-no-wireframe` ekle |
| `.agent/skills/musgoku/scripts/sync_sibling_handoff.py` | `ENRICHED_SUPERSET` | Canlı script | `[MODIFY]` ile `--ui-wireframe-expected` bayrağı ekle |
| `tests/test_ui_predesign_gate.py` | `NEW_CLEAN` | Yeni test dosyası | `[NEW]` birim test süiti oluştur |

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Full-Stack Vertical Slice)

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | Kapsam dışı (Dosya tabanlı plan ve süreç yönetişimi) | `PLAN.template.md`, `HANDOFF.md` |
| **2. Backend / View / RPC** | Plan arşivleme (`archive_plan.py`) UI wireframe kontrolü ve kardeş repo (`sync_sibling_handoff.py`) UI kontrat aktarımı | `archive_plan.py`, `sync_sibling_handoff.py` |
| **3. İstemci API Entegrasyonu** | CLI bayrakları (`--allow-no-wireframe`, `--ui-wireframe-expected`) ve kural tetikleyicileri (`--ui-preview`, `--ui-ux`, `"--UI&UX"`) | `development-workflow.md`, `design-skills-enforcement.md` |
| **4. Arayüz / UX & Eylemler** | `skills-catalog.html` içinde yeni bayrakların, 4 ön-tasarım kavramının (Wireframe, User Flow, Prototype, Mockup) ve arama anahtar kelimelerinin güncellenmesi | `.agent/skills-catalog.html` |
| **5. Döngü Kapanışı (Admin)** | Birim testleri (`test_ui_predesign_gate.py`) ve `run_all_gates.py` kalite kapısı doğrulaması | `tests/test_ui_predesign_gate.py` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi (Theme & Component Skeleton Contract)

- `skills-catalog.html` güncellemesinde mevcut **Living Surface** (`dark`/`light` CSS değişkenleri) ve kart yapısı %100 korunur; `test_py_design_audit.py` (`E8`, `E9`, `E14`, `E16`) kurallarına tam uyulur.

### 7.1 🖼️ UI/UX Ön-Tasarım Önizlemesi (`DESIGN.md` + `Before -> After` Wireframe)
- **Seçilen Seviye:** `Tier 1 (Plan-İçi Before -> After Wireframe)` — `skills-catalog.html` kart zenginleştirmesi:

```text
[BEFORE: .agent/skills-catalog.html - Plan & Tasarim Karti]
+-------------------------------------------------------------------+
| /seal-plan & archive_plan.py                                      |
| - --allow-conflicts / --skip-conflict-check                       |
+-------------------------------------------------------------------+

[AFTER: .agent/skills-catalog.html - UI Wireframe & --ui-preview]
+-------------------------------------------------------------------+
| /seal-plan & archive_plan.py + UI On-Tasarim Kapisi               |
| - Varsayilan: DESIGN.md + Plan-ici Before -> After ASCII Wireframe|
| - --ui-preview (--ui-ux): Mevcut gercek ekran DOM ile Before/After|
|   canli onizleme + UI-PREVIEW-LOCK (1:1 Birebir Ekran Garantisi)  |
| - --allow-no-wireframe & sync_sibling_handoff --ui-wireframe-expected |
+-------------------------------------------------------------------+
```

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 & Sprint Açılışı)
1. **[Adım 1 - Planı Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan "C:\Users\Mustafa\.gemini\antigravity-cli\brain\cf4c9670-8f87-47f1-80ab-8ca9794cec55\council_plan_ui_wireframe_pre_design_gate.md" --slug ui_wireframe_pre_design_gate --prefix council_plan` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/council_plan_ui_wireframe_pre_design_gate_<TIMESTAMP>.md` basılır.
2. **[Adım 2 - `HANDOFF.md` & `KANBAN.md` Senkronu]:** `GSW-FEAT-021` görevini `HANDOFF.md` §3 ve `KANBAN.md` içine işle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0 hata` döner.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - Kırmızı Testleri Yaz & Koştur]:** `tests/test_ui_predesign_gate.py` içinde `archive_plan.check_ui_predesign_plan` (`WARN` üretimi, `--allow-no-wireframe` susturma, `Before -> After` wireframe geçer durumu, `UI-PREVIEW-LOCK` kontrolü) ve `sync_sibling_handoff` (`ui_wireframe_expected=True`) testlerini yazıp `python -m unittest tests/test_ui_predesign_gate.py` çalıştır -> **Beklenen Çıktı:** Fonksiyonlar/parametreler henüz olmadığı için testler **KIRMIZI (FAIL/ERROR)** döner.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
1. **[Adım 1 - `archive_plan.py` & `sync_sibling_handoff.py` Güncelle]:** `check_ui_predesign_plan()`, `--allow-no-wireframe` ve `--ui-wireframe-expected` özelliklerini ekleyip `python -m unittest tests/test_ui_predesign_gate.py` çalıştır -> **Beklenen Çıktı:** Tüm yeni birim testleri **YEŞİL (OK)** döner.

### 🧩 Faz 3: Şablon, Kurallar ve `skills-catalog.html` Entegrasyonu
1. **[Adım 1 - Şablon ve Kural Dosyalarını Güncelle]:** `.agent/templates/PLAN.template.md` (§5.1 & §7.1), `.agent/rules/development-workflow.md`, `.agent/rules/design-skills-enforcement.md` ve `.agent/skills-catalog.html` dosyalarını güncelle -> **Beklenen Çıktı:** `check_aviation_docs.py` ve `check_design_skills.py` `[OK]` verir.

### 🧹 Faz 4: Kalite Kapıları & Kapanış
1. **[Adım 1 - Tüm Testleri ve Kapıları Çalıştır]:** `python -m unittest discover -s tests` ve `python .agent/skills/musgoku/scripts/check_design_skills.py && python .agent/skills/musgoku/scripts/check_aviation_docs.py && python .agent/skills/musgoku/scripts/check_handoff.py && python .agent/skills/musgoku/scripts/check_sprint_board.py` çalıştır -> **Beklenen Çıktı:** Tüm testler ve kapılar `exit 0` döner.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### 1. Plan Şablonu & Kurallar (`.agent/templates/` & `.agent/rules/`)

#### [MODIFY] [PLAN.template.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/templates/PLAN.template.md)
- **§5.1 Kardeş Uygulama:** Kardeş uygulama frontend içeriyorsa `--ui-wireframe-expected` ile `UI Wireframe & DESIGN.md Ön-Tasarım Beklentisi` satırı eklenecek.
- **§7.1 UI/UX Ön-Tasarım Önizlemesi (`DESIGN.md` + `Before -> After` Wireframe & `--ui-preview` 1:1 Kilit):**
  - 4 Ön-Tasarım Seviyesi (`Tier 0 Bypass` | `Tier 1 Plan-İçi ASCII Before -> After Wireframe [Varsayılan]` | `Tier 2 + User Flow / Site Haritası` | `Tier 3 --ui-preview / --ui-ux Gerçek Ekran Önizlemesi & UI-PREVIEW-LOCK`).
  - Varsayılan ````text` içinde `[BEFORE: ...]` -> `[AFTER: ...]` Tel Kafes şablonu.
  - `--ui-preview` (`--ui-ux` / `"--UI&UX"`) kullanıldığında doldurulan **`UI-PREVIEW-LOCK` (1:1 Birebir Ekran Sadakat Sözleşmesi)** tablosu (`Gerçek Kaynak Ekran Dosyası`, `Üretilen Önizleme HTML Yolu`, `Kilitlenen DOM/Layout İmzası`, `Kilitlenen DESIGN.md Tokenları`).

#### [MODIFY] [development-workflow.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/development-workflow.md)
- **Adım 2.1 Madde 6.1:** Kod yazmadan önce `DESIGN.md` okuma + 4 ön-tasarım kavramı (`Wireframe`, `User Flow`, `Prototype`, `Mockup`) + varsayılan Plan-içi `Before -> After` ASCII Wireframe + `--ui-preview` (`--ui-ux` / `"--UI&UX"`) gerçek ekran önizlemesi ve onay sonrası 1:1 ekran sadakat garantisi (`UI-PREVIEW-LOCK`).
- **Adım 2.2 Faz 0:** `archive_plan.py` mühürlemesinde UI planlarında wireframe kontrolü (`[WARN]`, istenirse `--allow-no-wireframe` ile susturma) ve kardeş repoya `sync_sibling_handoff.py --ui-wireframe-expected` aktarımı.

#### [MODIFY] [design-skills-enforcement.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/design-skills-enforcement.md)
- **§2.8.1 Kod Öncesi Ön-Tasarım (Wireframe / User Flow / Prototype / Mockup) ve `--ui-preview` 1:1 Sadakat Garantisi:**
  - Mevcut §3 Sahiplik Haritasına (`check_design_skills.py`) dokunmadan; `DESIGN.md` bazlı 4 ön-tasarım kademesi ve `--ui-preview` (`--ui-ux`) onaylandığında canlı ekranın onaylanan önizlemeyle birebir aynı DOM/token yapısında çıkmasını zorunlu kılan kural eklenecek.

---

### 2. Otomasyon Scriptleri & Katalog (`.agent/skills/musgoku/scripts/` & `.agent/skills-catalog.html`)

#### [MODIFY] [archive_plan.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/scripts/archive_plan.py)
- `check_ui_predesign_plan(plan_text: str) -> dict`:
  - Plan metninde frontend/UI dosya hedefleri (`src/pages/`, `src/components/`, `src/views/`, `.tsx`, `.jsx`, `.vue`, `.svelte` vb.) olup olmadığını ve planda `Tier 0` / `Salt Backend` beyanı veya `Before` -> `After` wireframe bloğu (`[BEFORE` / `[AFTER` / `Wireframe` / `UI-PREVIEW-LOCK`) bulunup bulunmadığını denetler.
  - Eksikse ve `allow_no_wireframe=False` ise `[WARN] [UI-WIREFRAME-MISSING]` uyarısı üretir (işlemi bloklamaz; kullanıcıya `--allow-no-wireframe` ipucunu gösterir).
  - `--ui-preview` / `UI-PREVIEW-LOCK` aktifse ve kilit alanları (`<doldur`) boş bırakılmışsa uyarı üretir.
- `archive_plan(..., allow_no_wireframe: bool = False)` parametresi ve CLI `--allow-no-wireframe` bayrağı eklenecek.

#### [MODIFY] [sync_sibling_handoff.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/scripts/sync_sibling_handoff.py)
- `sync_sibling_handoff(..., ui_wireframe_expected: bool = False)` parametresi ve CLI `--ui-wireframe-expected` bayrağı eklenecek.
- `ui_wireframe_expected=True` olduğunda kardeş `HANDOFF.md` (§2/§3), `KANBAN.md` ve `SPRINT_PLAN.md` satırlarına `[UI-ÖN-TASARIM ZORUNLU: Koddan önce DESIGN.md + Before/After Wireframe (--ui-preview / --ui-ux) onayı alınmalı]` ibaresi eklenecek.

#### [MODIFY] [skills-catalog.html](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills-catalog.html)
- `/seal-plan`, `frontend-design` ve arama indeksine `wireframe`, `tel kafes`, `user flow`, `prototype`, `mockup`, `--ui-preview`, `--ui-ux`, `--allow-no-wireframe`, `--ui-wireframe-expected`, `UI-PREVIEW-LOCK` anahtar kelimeleri ve kullanım örnekleri eklenecek.

---

### 3. Birim Testleri (`tests/`)

#### [NEW] [test_ui_predesign_gate.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/tests/test_ui_predesign_gate.py)
- `test_backend_only_plan_triggers_no_ui_warning`
- `test_ui_plan_without_wireframe_emits_warning`
- `test_ui_plan_with_allow_no_wireframe_suppresses_warning`
- `test_ui_plan_with_ascii_before_after_wireframe_passes_clean`
- `test_ui_preview_lock_contract_detection`
- `test_sync_sibling_handoff_ui_wireframe_expected_flag`

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
python -m unittest tests/test_ui_predesign_gate.py
python -m unittest discover -s tests
python .agent/skills/musgoku/scripts/check_design_skills.py
python .agent/skills/musgoku/scripts/check_aviation_docs.py
python .agent/skills/musgoku/scripts/check_handoff.py
```

### Manual Verification (Kullanıcı Gözüyle Doğrulama)
1. `[Adım 1].` `python .agent/skills/musgoku/scripts/archive_plan.py --help` çalıştırın -> `--allow-no-wireframe` bayrağının listede göründüğünü doğrulayın.
2. `[Adım 2].` `python .agent/skills/musgoku/scripts/sync_sibling_handoff.py --help` çalıştırın -> `--ui-wireframe-expected` bayrağının listede göründüğünü doğrulayın.
3. `[Adım 3].` `.agent/skills-catalog.html` dosyasını tarayıcıda açıp arama kutusuna `wireframe` veya `ui-preview` yazın -> İlgili kartların ve komut örneklerinin filtrelendiğini doğrulayın.

---

## 11. 🚨 Ditching & Emergency Exit (Acil Kurtarma Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| UI planı mühürlenirken `[WARN] [UI-WIREFRAME-MISSING]` çıkıyor | Planda `§7.1 Before -> After Wireframe` bloğu eksik veya bilinçli atlandı | Plana ASCII `Before -> After` ekleyin veya `archive_plan.py --allow-no-wireframe` bayrağını kullanın |
| Terminalde `--UI&UX` yazıldığında komut bölünüyor | Kabukta `&` operatörü komut ayırıcı olarak yorumlanıyor | Kabuk-güvenli `--ui-preview` veya `--ui-ux` bayrağını kullanın |
| `--ui-preview` onaylandıktan sonra kodlanan ekran önizlemeden farklı görünüyor | `UI-PREVIEW-LOCK` tablosundaki DOM imzası ve `DESIGN.md` tokenları izlenmemiş | `docs/plans/wireframes/ui_preview_<slug>.html` içindeki container sınıflarını ve tokenları hedef ekrana 1:1 kopyalayın |
