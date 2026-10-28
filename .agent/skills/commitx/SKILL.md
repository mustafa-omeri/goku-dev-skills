---
name: commitx
description: Peşin kullanıcı yetkisiyle kesintisiz otonom sürüm yayını orkestratörü; doğrulama kapılarını çalıştırıp semantik sürüm artışı, commit ve push adımlarını tamamlar. Tetikleyiciler: "/commitx", "commitx", "[COMMITX]", "commitle", "commit yap", "push to remote". Tetiklenmez: salt diff ve log inceleme istekleri. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# CommitX Autonomous Release Orchestrator

Bu yetenek, kullanıcının `commitx`, `/commitx` veya `commitle` yazarak peşin açık onay verdiği durumlarda, birleşik kalite kapılarından uzak depoya (`origin`) gönderime kadar tüm adımları **ara onaysız, kesintisiz ve otonom** olarak icra eder (`.agent/skills/git-release-workflow/SKILL.md` ile tam entegre çalışır).

## Bağlı Kurallar ve Alt Yetenekler

- **Alt Yetenek:** `git-release-workflow` (`.agent/skills/git-release-workflow/SKILL.md`)
- **Kurallar:** `.agent/rules/mandatory-git-release-workflow.md`, `.agent/rules/no-unauthorized-commit.md`, `.agent/rules/handoff-session-continuity.md`

---

## 5 Aşamalı Kesintisiz Otonom İcra Protokolü

### 1. Birleşik Doğrulama Kapıları (Pre-Release Gate Check)
Commit ve sürüm etiketlemesine geçmeden önce çalışma ağacındaki tüm kapsam içi kapıları tek komutla doğrula:
```bash
python .agent/skills/musgoku/scripts/run_all_gates.py
```
- Uygulama kodu (`src/**`, `app/**`, `api/**`) değiştiyse ilgili derleme (`npm run build` / `mvn clean compile -DskipTests`), tip kontrolü (`npx tsc --noEmit`) ve birim testlerini çalıştır.
- ⛔ **Blokaj Kuralı:** Herhangi bir kapı `[FAIL]` dönerse (`E3`/`E4`/`E5`/`E6` `PROJECT_BRIEF.md` sapması, `check_handoff.py` `E3` sapması veya test hatası) commit işlemi **durdurulur**, önce eksik doküman/kod onarılır ve kapı yeşile döndürülür.

### 2. Oturum Devri ve Hafıza Senkronizasyonu
Commit öncesi çalışma ağacında şu dosyaların güncel olduğundan emin ol:
- `HANDOFF.md` (§1 yapılanlar, §2 gerçek test/kapı kanıt metrikleri, §3 canlı görev panosu)
- `PROJECT_BRIEF.md` (paket, DB, Edge Function veya altyapı değiştiyse)
- `DB_MIGRATIONS.md` (veritabanı/şema değiştiyse)
- `knowledge-base.md` (kalıcı karar veya kök neden çözümü varsa)

### 3. Semantik Sürüm (SemVer) Hesaplama
Mevcut son etiketi (`git describe --tags --abbrev=0`) kontrol et ve değişiklik tipine göre yeni etiketi belirle:
- `feat:` → `MINOR` artış (`vX.(Y+1).0`)
- `fix:`, `perf:`, `refactor:`, `docs:`, `chore:` → `PATCH` artış (`vX.Y.(Z+1)`)
- `BREAKING CHANGE` → `MAJOR` artış (`v(X+1).0.0`)
- `package.json` veya `bin/cli.js` içinde sürüm alanı varsa yeni etiketle senkronize et.

### 4. Kesintisiz Git İcrası (Ara Onay Sorma Yasağı)
Kullanıcı `commitx` / `commitle` dediğinde peşin yetki vermiştir; tekrar onay istemeden sırasıyla çalıştır:
```bash
git add -A
git commit -m "<type>(<scope>): <description>"
git tag -a vX.Y.Z -m "Release vX.Y.Z: <summary>"
git push origin HEAD --tags
```

### 5. Standart Çıktı Raporu
İşlem tamamlandığında `### 📝 OTURUM DEVİR & BİLGİ TABANI GÜNCELLEMESİ` bloğu ile birlikte aşağıdaki yayın özetini sun:

```markdown
### 🚀 COMMITX: OTONOM SÜRÜM YAYINI TAMAMLANDI
- **Birleşik Kapılar (`run_all_gates.py`):** ✅ [X geçti · Y kapsam dışı · 0 başarısız]
- **Commit:** `<hash>` — `<commit mesajı>`
- **Sürüm Etiketi (Tag):** `vX.Y.Z`
- **Uzak Depo (Remote):** `origin/<branch>` + `--tags` başarıyla gönderildi.
```
