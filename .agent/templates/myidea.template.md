# 💡 PROJE FİKİR HAVUZU (myidea.md)

> Bu dosya, mevcut sprint veya PRD kapsamı dışındaki yaratıcı, vizyoner ve deneysel fikirlerin serbestçe toplandığı havuzdur.
> Geliştirici veya kullanıcı aklına gelen her fikri buraya serbest formatta ekleyebilir.
> AI Kod Ajanı; büyük işler bittiğinde (otonom olarak) veya "fikirlerime bak" dendiğinde bu dosyayı inceler,
> projenin güncel durumuna göre re-rating yapar, bayatları eler ve en iyi 3 fikri sunar.

---

## 📌 Status Badges
- 💡 `[NEW]` : Newly added raw idea awaiting assessment.
- 🎯 `[RECOMMENDED]` : High-scoring idea recommended for the next sprint.
- ⏳ `[DEFERRED]` : Valuable, but deferred due to prerequisites or timing.
- ⛔ `[DROPPED - Reason]` : Obsolete, duplicated, or superseded (never deleted, archived with reason).
- ✅ `[SHIPPED - Card/Date]` : Shipped and verified in the codebase.

---

## 🎯 Puanlama (Rating) Kriterleri (1 - 10)
- **Etki (Impact - 1-10):** Kullanıcı deneyimine, performansa veya ürün değerine katkısı.
- **Efor (Effort - 1-10):** Ters orantılı kolaylık (10 = çok kolay/hızlı, 1 = çok zor/karmaşık).
- **Proje Uyumu (Fit - 1-10):** Mevcut sprint, mimari ve ürün vizyonuyla uyumu.
- **Genel Rating:** `(Etki * 0.4) + (Efor * 0.3) + (Proje Uyumu * 0.3)`

---

## 🚀 Fikirler Listesi

### IDEA-001: Komut Paletine (Ctrl+K) Sık Kullanılan Kısayolların Eklenmesi
- **Durum:** 💡 `[NEW]`
- **Rating:** `8.2/10` (Etki: 8 | Efor: 9 | Uyum: 8)
- **Açıklama:** Kullanıcıların klavyeden elini kaldırmadan en sık yaptığı 5 işlemi (yeni kayıt, arama, tema değişimi) hızlıca tetikleyebilmesi.
- **Değer / Gerekçe:** Power-user deneyimini ve platform içi gezinme hızını en az 2 kat artırır.
- **Ajan Değerlendirmesi:** Mevcut web-ide-ux-architect ve modal altyapımız ile 1-2 dikey dilimde hızlıca uygulanabilir.

### IDEA-002: Otomatik Offline Taslak Kaydı (Auto-Save to LocalStorage)
- **Durum:** ⏳ `[DEFERRED]`
- **Rating:** `6.8/10` (Etki: 7 | Efor: 8 | Uyum: 5)
- **Açıklama:** Form doldururken bağlantı kopsa dahi girdilerin kaybolmaması için yerel taslak tutulması.
- **Değer / Gerekçe:** Veri kaybını önler.
- **Ajan Değerlendirmesi:** Backend form validasyonları ve entity şeması henüz tamamlanmadığı için şimdilik ertelendi; form refactoring sonrası tekrar değerlendirilmeli.

### IDEA-003: Eski Flash Animasyonlu Karşılama Ekranı
- **Durum:** ⛔ `[DROPPED - Modern UX Standartlarına Uymuyor]`
- **Rating:** `1.5/10` (Etki: 2 | Efor: 2 | Uyum: 1)
- **Açıklama:** Giriş ekranında nostaljik flash benzeri intro animasyonu oynatılması.
- **Değer / Gerekçe:** Eğlenceli bir karşılama sunmak.
- **Ajan Değerlendirmesi:** Modern web standartları, bundle bütçesi ve onboarding-tour ilkelerine aykırı olduğu için elendi.

---
