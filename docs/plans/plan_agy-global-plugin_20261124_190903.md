# Tüm Skillset'i Antigravity CLI İçin Global Tanımlama Uygulama Planı
<!--
  Kaynak: .agent/templates/PLAN.template.md
  Standart: FAA AC 121-24C + /caveman
-->

> **Hedef Dal / Sürüm:** `main / v1.46.0` · **Tarih:** `2026-11-24`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `agy-customizations`, `antigravity-guide`, `council`, `karpathy-guidelines`, `doc-coauthoring`, `tdd`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`, `get_project_state`), `sequential-thinking`  
> **Desteklenen Ortamlar:** `Antigravity CLI (agy)`, `Antigravity App`, `Antigravity IDE`  

---

## 1. Goal Description (Amaç & Kapsam)

`skillSetWorks/.agent/` altındaki **50 skill**, **22 kural**, **20 şablon** ve yardımcı Python script'lerinin her yazılım projesine ayrı ayrı `.agent/` klasörü kopyalanmadan Antigravity CLI (`agy`) oturumlarının **tamamında** otomatik kullanılabilmesi için makine-geneli (`~/.gemini/config/`) global kurulum altyapısı kurmak.

### Ölçülen Mevcut Sınırlar (Doğrulanmış Gerçekler)
- `skillSetWorks/.agent/` envanteri: **50 skill**, **22 kural (`303.9 KB`)**, **20 şablon**.
- Antigravity kural motoru sınırları (`agy-customizations/docs/rules.md`):
  - Tek dosya üst sınırı: **`24.000` byte** (`24 KB`) — üstü satır sınırından kırpılır.
  - Toplam Always-On kural bütçesi: **`20.000` token** — üstü tam metin yerine dosya pointer'ına düşürülür.
- `24 KB` sınırını aşan mevcut 4 kural dosyası:
  1. `design-skills-enforcement.md` (`58.538` byte)
  2. `skill-trigger-routing.md` (`48.113` byte)
  3. `development-workflow.md` (`47.737` byte)
  4. `sprint-delivery-workflow.md` (`31.426` byte)
- `agy-customizations/docs/plugins.md` gereği `plugins/<ad>/rules/` içindeki tüm dosyalar aktif kural setine yüklenir; bu nedenle 22 kural doğrudan `rules/` içine konulamaz.

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin)
```gherkin
Feature: Global Antigravity CLI Goku Dev Skills Plugin
  Scenario: Yeni bir projede .agent klasörü olmadan skillset kullanımı
    Given kullanıcının ~/.gemini/config/plugins/goku-dev-skills/ plugini etkin ve validate geçmiş durumdadır
    When kullanıcı içinde .agent/ bulunmayan herhangi bir projede agy oturumu başlatır
    Then Antigravity CLI 50 skill'in tamamını ve global yönlendiriciyi keşfeder
    And agy plugin validate --strict komutu 0 hata döner

  Scenario: Kural bütçesi ve proje anayasası koruması
    Given global plugin aktifken kullanıcı özel AGENTS.md içeren bir projeyi (örn. MyBrainForDev) açar
    When agy oturumu kuralları yükler
    Then global plugin tek kural dosyası (rules/AGENTS.md) 24.000 byte altındadır
    And projenin kendi kök AGENTS.md veya .agent/ kuralları öncelik sırasıyla korunur
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Derecesi (Ort.) |
|---|---|---|---|:---:|
| **Option A (`skills.json` Pointer)** | `~/.gemini/config/skills.json` üzerinden doğrudan `skillSetWorks/.agent/skills` bağlamak | Sıfır dosya kopyası; canlı senkron | Yalnız skill'leri bağlar; `rules/` ve `templates/` getirmez; `agy plugin enable/disable` yok; mevcut `~/.gemini/config/skills/git-release-workflow` ile gölgeleme | `2.33` |
| **Option B (Global Plugin + Kompakt Router — Önerilen)** | `~/.gemini/config/plugins/goku-dev-skills/` + `plugin.json` + 50 skill + 20 şablon + `references/rules/` + `<24 KB` `rules/AGENTS.md` + `scripts/sync_agy_global.py` | 50 skill + 22 kural (on-demand) + 20 şablon tek pakette; `agy plugin enable/disable` ve `agy plugin validate` destekli; 24 KB / 20K token bütçesine %100 uyumlu; mevcut `.agent/` bulunan projelerle çakışmaz | `skillSetWorks` güncellendiğinde tek komutla (`sync_agy_global.py` / `npx goku-dev-skills update --agy-global`) senkron gerekir (~65 MB kopya) | **`1.00` (#1 Kazanan)** |
| **Option C (Düz `~/.gemini/config/skills/` + Tüm Kurallar)** | 50 skill'i doğrudan `~/.gemini/config/skills/` altına, 22 kuralı `~/.gemini/config/AGENTS.md` içine gömmek | Tek dizin | `303.9 KB` kural bütçeyi patlatır ve 4 dosya `24 KB`'dan kırpılır; web/Spring kuralları tüm non-code projelere sızar; kapatıp açma yok | `2.67` |

- **Borda Hesaplama Kanıtı (`council_ranker.py`):** 3 hakem (`ARCH`, `QA`, `UX/PO`) `B > A > C` ve `B > C > A` sıralamasıyla Option B ortalama derece **`1.00` (3/3 birincilik oyu)** ile seçildi.

---

## 3. User Review Required & Open Questions

> [!IMPORTANT]
> **Onay Gerektiren Mimari Kararlar:**
> 1. **Kapsam & Kurulum Modu:** Global plugine `frontend-design` içindeki 55 HTML tema (`~54.5 MB`) dahil **tamamı (~65 MB)** mı kurulsun, yoksa `--minimal` (temalar hariç `~11 MB`) mı? *(Varsayılan plan: tam paket `~65 MB`, `--minimal` opsiyonu script'te destekli).*
> 2. **Tekrarlı Skill (`git-release-workflow`):** `C:\Users\Mustafa\.gemini\config\skills\git-release-workflow` zaten mevcut. Global plugin kurulunca eski kopya kaldırılsın mı, kalsın mı? *(Önerilen: eski kopya yedeklenip temizlensin ki iki kez görünmesin).*
> 3. **`MyBrainForDev\.agent` Durumu:** Az önce `C:\MyBrainZarbulat\MyBrainForDev\.agent` içine kurduğumuz `1.31 MB` planlama alt kümesi **kalsın mı** (avantajı: vault içinde Java/React/UI skill'leri gizli kalır), yoksa global plugin sonrası **kaldırılsın mı**? *(Önerilen: kalsın veya vault'a özel `skills.json` exclude ile sadeleştirilsin — karar sizin).*
>
> **2-Modlu Onay Seçenekleri:**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan`):** Planı `docs/plans/` altına arşivler ve `HANDOFF.md` §3 panosuna yazar; değişiklik yapmadan durur.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onayla"`):** Faz 0 arşivlemesi + Faz 1 TDD Kırmızı Test → Faz 4 doğrulama adımlarını uygular.

---

## 4. 🏗️ Mimari Tasarım: Global Antigravity Plugin + Yol Köprüsü

```text
C:\Users\Mustafa\.gemini\config\plugins\goku-dev-skills\
├── plugin.json                 # Antigravity resmi plugin manifesti (agy plugin validate uyumlu)
├── rules\
│   └── AGENTS.md               # < 24 KB kompakt Global Router + Scope Guard + Path Bridge
├── references\
│   └── rules\                  # 22 tam kural dosyası (on-demand okunur, Always-On bütçesini şişirmez)
├── templates\                  # 20 şablon (PLAN.template.md, HANDOFF.template.md, ...)
└── skills\                     # 50 skill + scripts/ + references/ + themes
```

### Kritik Tasarım Çözümleri
1. **24 KB Kural Bütçesi Çözümü (`rules/AGENTS.md` + `references/rules/`):**
   - `rules/AGENTS.md` yalnızca tetikleyici yönlendirme matrisini, kapsam korumasını ve dosya haritasını tutar (`< 8 KB`).
   - 22 tam kural `references/rules/` altında yaşar; böylece Antigravity başlangıçta 303.9 KB kural yüklemez, sadece ilgili görevde (ör. `/plan`, UI, DB) tam kural dosyasını okur.
2. **Yol Çözümleyici (Path Bridge):**
   - Global modda çalışılan bir projede `./.agent/` yoksa ajan script ve şablonları (`council_ranker.py`, `archive_plan.py`, `PLAN.template.md`, `check_design_slop.py` vb.) otomatik olarak `C:/Users/Mustafa/.gemini/config/plugins/goku-dev-skills/` altından çağırır.
3. **Proje Anayasası & Mevcut `.agent/` Koruması (Scope Guard):**
   - Projede `.agent/` varsa **Workspace > Global** önceliği gereği yerel `.agent/` geçerlidir.
   - Projede özel `AGENTS.md` / `CLAUDE.md` varsa (ör. Obsidian Vault) global kural o projenin kurallarını ezmez; yazılım dışı depolara zorla `HANDOFF.md` / `SPRINT_PLAN.md` üretmez.

---

## 5. Proposed Changes (Önerilen Dosya Değişiklikleri)

### Bileşen 1: Global Antigravity Senkronizasyon Motoru (`skillSetWorks`)
#### [NEW] `scripts/sync_agy_global.py`
- `skillSetWorks/.agent/` içeriğini `C:\Users\Mustafa\.gemini\config\plugins\goku-dev-skills\` altına deterministik senkronize eder.
- `plugin.json` ve `< 24 KB` kompakt `rules/AGENTS.md` dosyasını üretir.
- `22` tam kuralı `references/rules/`, `20` şablonu `templates/`, `50` skill'i `skills/` altına kopyalar.
- Bayraklar: `--check` (dry-run), `--minimal` (55 HTML tema hariç), `--dest <yol>`, `--dedupe-global-skills` (opsiyonel), `--uninstall`.

#### [MODIFY] `bin/cli.js`
- `npx goku-dev-skills sync-agy` (ve `update --agy-global`) komutu ile `scripts/sync_agy_global.py` motorunu (veya doğrudan JS karşılığını) çağırır; `--help` çıktısına belgelenir.

#### [MODIFY] `delivery.py` / `tests/`
#### [NEW] `tests/test_agy_global_plugin.py`
- Geçici hedef dizinde senkronizasyon, `plugin.json` doğrulaması, `rules/AGENTS.md` `< 24.000` byte kuralı, `rules/` altında tek dosya şartı, 50 skill + 20 şablon + 22 referans kural tamlığı ve `--check` idempotency testleri.

---

## 6. 🧪 Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Plan Arşivi & Görev Kaydı
1. **[Adım 1 - Planı Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug agy-global-plugin` -> **Beklenen Çıktı:** `docs/plans/plan_agy-global-plugin_<TIMESTAMP>.md` oluşur ve çakışma guard'ı yeşil döner.
2. **[Adım 2 - `HANDOFF.md` §3 Güncelle]:** Görev kimliği (`[GSW]-FEAT-022`) `HANDOFF.md` §3 panosuna işlenir -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0` hata döner.

### 🔴 Faz 1: Kırmızı Test (Red Loop)
1. **[Adım 1 - Sözleşme & Senkronizasyon Testini Yaz]:** `tests/test_agy_global_plugin.py` dosyasını oluştur ve `python -m unittest tests/test_agy_global_plugin.py` çalıştır -> **Beklenen Çıktı:** `sync_agy_global.py` henüz olmadığı için test **KIRMIZI (FAIL)** döner.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
1. **[Adım 1 - `scripts/sync_agy_global.py` Oluştur]:** Plugin paketleyici, kompakt `rules/AGENTS.md` üretici, `--check` ve `--minimal` bayraklarını yaz -> **Beklenen Çıktı:** `python -m unittest tests/test_agy_global_plugin.py` **YEŞİL (PASS)** döner.
2. **[Adım 2 - `bin/cli.js` Entegrasyonu]:** `sync-agy` alt komutunu ekle ve `node bin/cli.js --help` ile doğrula -> **Beklenen Çıktı:** Yardım çıktısında `sync-agy` görünür.

### 🧩 Faz 3: Global Kurulum & `agy` Doğrulaması
1. **[Adım 1 - Global Plugini Kur]:** `python scripts/sync_agy_global.py` çalıştır -> **Beklenen Çıktı:** `C:\Users\Mustafa\.gemini\config\plugins\goku-dev-skills\` altına 50 skill, 20 şablon, 22 referans kural ve `<24 KB` `rules/AGENTS.md` kurulur.
2. **[Adım 2 - Resmi `agy` Doğrulayıcısı ile Test Et]:** `agy plugin validate C:\Users\Mustafa\.gemini\config\plugins\goku-dev-skills --strict --json` ve `agy plugin list --json` çalıştır -> **Beklenen Çıktı:** Plugin hatasız `valid` ve `enabled` raporlanır.

### 🧹 Faz 4: Regresyon & Kapanış
1. **[Adım 1 - Tüm Kapıları Çalıştır]:** `python tests/run_all.py` ve `python .agent/skills/musgoku/scripts/rules_gates.py --strict` çalıştır -> **Beklenen Çıktı:** Tüm testler ve kapılar `[OK]` döner; `.agent` içermeyen bir test klasöründe `agy` ile skill listesinin göründüğü doğrulanır.

---

## 7. Verification Plan (Doğrulama Planı)

### Automated Tests
```powershell
python -m unittest tests/test_agy_global_plugin.py
python scripts/sync_agy_global.py --check
agy plugin validate C:\Users\Mustafa\.gemini\config\plugins\goku-dev-skills --strict --json
agy plugin list --json
python tests/run_all.py
```

### Manual Verification (FAA AC 121-24C)
1. **[Adım 1 - Boş/Yeni Klasörde Test]:** `.agent` içermeyen geçici bir klasörde `agy` başlat -> **Beklenen Çıktı:** `musgoku`, `council`, `frontend-design`, `ui-polish` dahil 50 skill kullanılabilir görünür.
2. **[Adım 2 - Mevcut Projede Öncelik Testi]:** `MyBrainForDev` veya `ocai` içinde `agy` başlat -> **Beklenen Çıktı:** Projenin kendi `.agent/` ve `AGENTS.md` kuralları global pluginin önünde korunur.
3. **[Adım 3 - Kapatıp Açma Testi]:** `agy plugin disable goku-dev-skills` ardından `agy plugin enable goku-dev-skills` çalıştır -> **Beklenen Çıktı:** Tüm skillset tek komutla devre dışı bırakılıp geri açılabilir.

---

## 8. 🚨 Ditching & Emergency Exit (Geri Dönüş & Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `agy plugin validate` manifest veya kural hatası verirse | `plugin.json` alanı eksik veya `rules/` boyutu > `24 KB` | `rules/AGENTS.md` boyutunu `< 24 KB` altında tut, `agy plugin validate --strict` çıktısındaki alanı düzelt |
| Mevcut bir projede kural çakışması veya istenmeyen kapı uyarısı çıkarsa | Global plugin `rules/AGENTS.md` fazla agresif tetikleniyor | Geçici durdurma: `agy plugin disable goku-dev-skills`; ardından `rules/AGENTS.md` içindeki Scope Guard kuralını daralt |
| Skill iki kez listelenirse (`git-release-workflow`) | Hem `~/.gemini/config/skills/` hem global pluginde mevcut | `~/.gemini/config/skills/git-release-workflow` kopyasını yedekleyip kaldır (`--dedupe-global-skills`) |
| Tamamen geri almak gerekirse | Global plugin kaldırılmak isteniyor | `agy plugin uninstall goku-dev-skills` veya `python scripts/sync_agy_global.py --uninstall` çalıştır |
