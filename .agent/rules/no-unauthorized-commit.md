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
   - **Kullanıcı Test Adımları:** Kullanıcının teslimatı bizzat gözüyle test edebilmesi için
     `docs/KULLANICI_TEST_REHBERI.md` dosyasındaki ilgili adımlar ve test komutları
     (minor rötüş veya dahili refactoring ise güncelleme gerekmediği ve geçerli mevcut senaryo açıkça belirtilir).
     ⛔ Yeni özellik veya akış değişikliğinde test adımları sunulmadan ve rehber güncellenmeden commit onayı istenemez.
3. Aşağıdakiler açık onay sayılır: "commit yap", "onaylıyorum", "evet",
   "commitleyebilirsin", "gönder", "commitx", "commitle".
   "devam et", "bak", "bir de şunu düzelt" onay **sayılmaz**.
4. Onay yoksa yalnızca değişiklikleri hazırla ve onay bekle.

## 1.0 Zorunlu Commit Teklifi (Mandatory Commit Prompting)

⛔ **Commit/Push Teklifini Atlama veya Sessiz Kalma Yasağı (Anti-Omission Rule):**
"Onaysız commit yapma" kuralı, ajanın commit aşamasını tamamen unutması, yok sayması veya kullanıcıya sormaktan kaçınması anlamına **GELMEZ**.

1. **Her Tamamlanan Görev / Defect / Refactoring Sonrası:**
   Çalışma ağacında doğrulanmış değişiklikler varsa (`git status --short` temiz değilse), ajan görevi veya defect onarımını bitirip sessizliğe gömülemez.
2. **Zorunlu Teklif Sunumu:**
   Ajan kullanıcıya her defasında açıkça:
   - Değişen dosyaları,
   - Önerilen konvansiyonel commit mesajını (`feat(...)`, `fix(...)` vb.),
   - Yeni semantik tag önerisini (`vX.Y.Z`),
   - Manuel doğrulama test adımlarını
   sunarak:
   > *"Yapılan değişiklikler test edildi ve doğrulandı. Yukarıdaki commit mesajı ve sürüm etiketiyle commit/push işlemini başlatmamı onaylıyor musunuz?"*
   sorusunu sormakla **YÜKÜMLÜDÜR**. Kullanıcıdan açık onay gelmeden komut çalıştırılamaz; ancak bu soru sorulmadan iş tamamlandı sayılamaz.

## 1.1 Doğrudan Kesintisiz Yayınlama İstisnası (`commitx`, `commitle`)

Kullanıcı mesajında açık bir eylem olarak **`commitx`** veya **`commitle`** yazdığında; bu talep **peşin ve açık tam yetki (Express Pre-Approval)** kabul edilir:

- Ajan ara onay sormak ("Onaylıyor musunuz?", "Commit yapayım mı?", "Push yapayım mı?") için **duraksamaz**.
- Kapsam-duyarlı doğrulama ilkesine göre gerekiyorsa test/build doğrulamalarını yapar, semantik tag artışını hesaplar, `git add` → `git commit` → `git tag` → `git push` adımlarını arka arkaya otonom ve kesintisiz tamamlar.
- Kullanıcıya doğrudan nihai sürüm ve push raporunu sunar.
- ⛔ Şartlı veya soru cümleleri (ör. *"commitlemeden önce şuna bak"*, *"commitlemeli miyiz?"*) peşin onay **sayılmaz**; yalnız doğrudan eylem kipi (*"commitle"*, *"bunu commitle"*, *"commitx"*) peşin onaydır.

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