---
name: No Unauthorized Git Commit
description: Kullanıcıdan açık onay alınmadan asla git commit, tag veya push çalıştırılmamasını zorunlu kılar.
sinif: SUREC
---

# ⛔ KESİN KURAL: Kullanıcı Onayı Olmadan Asla Commit Yapma

1. Açık ve net onay almadan **ASLA** `git commit`, `git tag`, `git push` çalıştırma.
   Otomatik commit içeren bir akış (`git-release-workflow` dahil) da aynı hükme tabidir.
2. Onay isterken **şunları göster:**
   - `git status --short` çıktısı veya değişen dosya listesi
   - Önerilen commit mesajı
   - Önerilen yeni semantik tag
3. Aşağıdakiler açık onay sayılır: "commit yap", "onaylıyorum", "evet",
   "commitleyebilirsin", "gönder".
   "devam et", "bak", "bir de şunu düzelt" onay **sayılmaz**.
4. Onay yoksa yalnızca değişiklikleri hazırla ve onay bekle.

## Onay sonrası davranış

Onay verildikten sonra `git add` · `git commit` · `git tag` · `git push`
adımlarının **tamamı** `git-release-workflow` skill'iyle, baştan sona
kesintisiz ve otonom çalıştırılır. Her komut için tekrar onay istenmez.

Push hatası alırsan otomatik `pull`/`merge`/rebase yapma. Hata çıktısını
kullanıcıya göster ve çözümü ona bırak. Force push asla yapılmaz.

Bu kural refactoring, hata düzeltme, dokümantasyon ve sürüm yayını dahil
**tüm** işlerde istisnasız geçerlidir.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir commit onay kuralı gerekirse (ör. branch koruma kuralları), önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_