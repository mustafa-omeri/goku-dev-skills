---
name: Mandatory Git Release Workflow
description: Tüm commit, etiketleme ve dağıtım işlemlerinde git-release-workflow skillinin kullanılmasını zorunlu kılar.
sinif: SUREC
---

# ⛔ KESİN KURAL: Tüm Commit İşlemlerinde git-release-workflow Kullanılır

1. **İstisnasız skill kullanımı.** Projedeki her commit ve sürümleme işlemi
   `.agent\skills\git-release-workflow\SKILL.md` adımlarına uygun yürütülür.
   Ad hoc, tek başına `git commit` çalıştırılmaz.
2. **Semantik etiketleme.** En son tag okunur ve bir sonraki semantik sürüme
   artırılır (`vX.Y.Z` → `vX.Y.Z+1`). Analiz kök nedeni belgeliyorsa `+1` yerine
   gerçek artış (minor/major) yapılır.
3. **Önce onay.** Değişiklikler ve önerilen mesaj kullanıcıya sunulur; açık onay
   alınmadan commit ve tag adımlarına geçilmez
   (bkz. `no-unauthorized-commit.md`).
4. **Uzak depo senkronu.** Commit sonrası hem aktif dal (`git push origin HEAD`)
   hem yeni tag'ler (`git push --tags`) gönderilir.
5. **Kesintisizlik.** Onay sonrası tüm pipeline tek seferde yürütülür; ara
   komut onayı istenmez.

## Adım özeti

1. `git status` — değişiklik yoksa dur ve bildir.
2. `git tag -l` — en son semantik tag'ı bul, sonraki sürümü hesapla.
3. `git add .`
4. Dosya listesi + önerilen mesaj + önerilen tag + kullanıcının bizzat gözüyle test edeceği adımları (`KULLANICI_TEST_REHBERI.md`) kullanıcıya göster, onay al.
5. `git commit -m "<mesaj>"`
6. `git tag <yeni_tag>`
7. `git push origin HEAD` ve `git push --tags`

## Dikkat

- PowerShell'de `&&` zincirlemesi çalışmayabilir; komutları sırayla çalıştır.
- Push hatasında otomatik pull/merge yapma; hata çıktısını kullanıcıya göster.
- Force push (`--force`, `--force-with-lease`) asla kullanılmaz.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir git sürüm kuralı gerekirse (ör. özel tag formatı, özel remote adı), önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_