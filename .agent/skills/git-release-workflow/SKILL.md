---
name: git-release-workflow
description: >-
  Kullanıcı onayından sonra değişiklikleri hazırlama, semantik sürüm etiketi artırma,
  commit oluşturma ve dal ile etiketleri uzak depoya gönderme akışını kesintisiz
  otomatik yürütür. Tetikleyiciler: "commit yap", "sürüm yayınla", "release çıkar",
  "tag at", "gönder", "push", "yayına al", "commit this", "tag a release", "push to
  remote". Her commit/tag/push öncesi ayrı onay zorunludur; onaysız çalışmaz.
  Tetiklenmez: "git durumu nedir", "diff göster", "log" gibi salt okuma istekleri.
  Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Git Release Workflow

> Bu skill **onay sonrası** çalışır. Onay kuralı:
> [`.agent/rules/no-unauthorized-commit.md`](../../rules/no-unauthorized-commit.md).

## Kapsam

Bu skill tek işi yapar: **onaylanmış** değişiklikleri semantik sürüm etiketiyle
commit edip uzak depoya gönderir. Dal modeli kurma, korumalı dal ayarı, imzalı
commit, PR kontrolü gibi konular bu skill'in kapsamı **değildir.**

## Ön koşullar

1. Kullanıcı açık onay verdi mi? → Hayırsa **başlama.**
2. Çalışma ağacında değişiklik var mı? → Yoksa dur ve bildir.
3. `git-release-workflow` kuralları projedeki `AGENTS.md` ile çelişmiyor mu?
   → Çelişiyorsa proje kuralı kazanır, akışı durdur ve sor.

## Hızlı kullanım

Kullanıcı: *"Değişiklikleri commit et, mesaj: 'layout hatası düzeltildi'."*
Ajan: etiketleri okur → hazırlar → **onay ister** → onay gelince tek seferde
commit + tag + push yapar ve sonucu raporlar.

## İş Akışı

### 1. Check Status

- Run `git status` in the project root.
- If the output indicates "nothing to commit, working tree clean", notify the user and **stop execution**.

### 2. Determine Next Tag

- Run `git tag -l -n1` or `git tag -l` to list all tags. Find the latest tag numerically (e.g., `v1.7.1`).
- Parse the version number and increment the last digit to generate the new tag (e.g., `v1.7.2`).

### 3. Stage Changes

- Run `git add .` to stage all modifications.

### 4. Ask User for Commit Approval (CRITICAL MANDATORY STEP)

- **ASLA KULLANICIYA SORMAYIP ONAY ALMADAN COMMIT ATMA!**
- Değiştirilen dosyaları, önerilen commit mesajını ve **kullanıcının çıktıyı gözüyle nasıl doğrulayacağını (`KULLANICI_TEST_REHBERI.md` adımları)** kullanıcıya göster.
- Kullanıcıdan açık onay (onaylıyorum / evet / commit yap / commitleyebilirsin) almadan `git commit` adımına geçme. "devam et" gibi ifadeler onay **sayılmaz**.
- ⭐ **ONAY SONRASI KESİNTİSİZ OTONOM ÇALIŞTIRMA:** Kullanıcıdan onay alındıktan sonra, sıradaki adımlar (`git add`, `git commit`, `git tag`, `git push` vb.) için her komutta TEKRAR TEKRAR ONAY İSTENMEZ. Tüm akış uçtan uca tek seferde, kesintisiz ve otonom olarak çalıştırılır, doğrudan nihai sonuç raporlanır.

### 5. Commit Changes (Only After User Confirmation)

- Run `git commit -m "<message>"`.
- If the user provided a message, use it. If not, use the approved message from Step 4.

### 6. Create Tag

- Run `git tag <new_tag>` using the tag generated in Step 2.

### 7. Push Commits and Tags

- Run `git push origin HEAD` to push the commit to the current branch.
- Run `git push --tags` to push the newly created tag to the remote repository.
- **Error Handling**: If the push fails due to remote changes (e.g., `fetch first`), **do not** attempt an automatic pull or merge. Fail loudly, print the error to the user, and ask them to resolve the conflict manually.

## Common Mistakes

- Continuing the workflow when `git status` shows no changes.
- Attempting to force push (`--force`) when conflicts occur. The agent must fail loudly on push errors.
- Failing to use environment-appropriate syntax for chained commands (e.g., using `&&` in PowerShell might fail, so running commands sequentially or using `;` is safer).
