---
name: diagnosing-bugs
description: Sistematik 6 aşamalı hata ayıklama disiplini; kod değiştirmeden önce hatayı kanıtlayan kırmızı geri bildirim döngüsü kurar, hipotezleri sınar ve regresyon testi ekler. Tetikleyiciler: "hata ayıkla", "bug çöz", "neden çalışmıyor", "kök neden", "diagnose bug", "debug issue", "root cause". Tetiklenmez: genel refactoring ve yeni özellik ekleme `musgoku` kapsamındadır. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Diagnosing Bugs

Zorlu hatalar, çökmeler ve performans gerilemeleri için sistematik teşhis döngüsü. Bir aşama yalnızca açıkça gerekçelendirildiğinde atlanabilir.

Kod tabanını incelerken ilgili modüllerin zihinsel modelini anlamak için `GLOSSARY.md` dosyasını (varsa) ve dokunduğunuz alandaki ADR kayıtlarını okuyun.

## Gizleme (Redact)

Komut, çıktı veya yakalanan logları sunarken **tüm gizli bilgileri ve parolaları gizleyin**: yerine `<REDACTED>` yazın. Döngüleri ortam değişkenlerine (env vars) bağlayarak sırların raporda görünmesini engelleyin.

Gizlenmiş çıktı hatayı teşhis etmek için yetersizse, bunu açıkça belirtip kullanıcıdan bilgi isteyin.

## Aşama 1: Geri Bildirim Döngüsü Kur (Build a Feedback Loop)

**Bu disiplinin özü burasıdır.** Geri kalan her şey mekaniktir. Elde *bu spesifik hatada* kırmızıya dönen (fail eden) sıkı bir sinyal varsa, kök neden mutlaka bulunur. Böyle bir sinyal yoksa, saatlerce koda bakmak bir işe yaramaz.

⛔ **KESİN KURAL:** Kırmızıya düşen çalıştırılabilir tek bir komut üretip çalıştırmadan önce **koda dokunmak, kod değiştirmek veya teoriler üretmek YASAKTIR.**

### Döngü Oluşturma Yöntemleri (Öncelik Sırasıyla):

1. **Başarısız Test (Failing Test):** Hataya ulaşan dikiş noktasında (seam) bir unit, integration veya e2e testi yazmak.
2. **Curl / HTTP İsteği:** Çalışan dev sunucuya karşı uç nokta çağrısı yapmak.
3. **CLI Çağrısı:** Bilinen geçerli bir girdi verip çıktıyı beklenen ile karşılaştırmak.
4. **Headless Tarayıcı Scripti:** UI'ı tetikleyip konsol, ağ veya DOM'u denetlemek.
5. **Yakalanan İzi Yeniden Oynatma (Replay Trace):** Gerçek ağ isteğini veya payload'u kaydedip izole kod yolunda tekrar çalıştırmak.
6. **Geçici Test Düzeneği (Throwaway Harness):** Hatalı kod yolunu tek bir fonksiyon çağrısıyla tetikleyen minimal bir test betiği.
7. **Fuzzing / Özellik Döngüsü:** "Bazen yanlış çıktı veriyor" durumlarında 1000 rastgele girdi ile hatayı yakalamak.
8. **Git Bisect Düzeneği:** Hatanın hangi commit veya sürümde başladığını otomatik `git bisect run` ile bulmak.
9. **Diferansiyel Döngü:** Aynı girdiyi eski ve yeni versiyonda çalıştırıp diff almak.
10. **HITL (İnsan Döngüde) Scripti:** Kullanıcının tıklaması gerekiyorsa `scripts/hitl-loop.template.sh` ile yapılandırılmış adımlar sunmak.

### Döngüyü Sıkılaştır (Tighten):
- **Daha hızlı mı?** (Gereksiz başlatmaları atla, test kapsamını daralt, saniyeler içinde çalışsın).
- **Sinyal daha keskin mi?** ("Çökmedi" yerine spesifik semptomu assert et).
- **Deterministik mi?** (Zamanı ve rastgeleliği sabitle).

### Aşama 1 Bitiş Kriteri:
Aşama 1 ancak şu özelliklere sahip **tek bir çalıştırılabilir komut** belirlenip **en az bir kez çalıştırıldığında ve kırmızı (fail) verdiği kanıtlandığında** tamamlanmış sayılır:
- [ ] **Kırmızı Yetenekli (Red-capable):** Gerçek hata yolunu tetikler ve kullanıcının belirttiği tam semptomu doğrular.
- [ ] **Deterministik:** Her çalıştırmada aynı sonucu üretir.
- [ ] **Hızlı:** Dakikalar değil saniyeler sürer.
- [ ] **Ajan Tarafından Çalıştırılabilir:** Otonom çalıştırılabilir.

## Aşama 2: Yeniden Üret ve Sadeleştir (Reproduce + Minimise)

Döngüyü çalıştırın ve kırmızıya dönmesini gözlemleyin.
- Kullanıcının bildirdiği hatanın aynısı mı, yoksa yakındaki başka bir hata mı?
- Başarısızlık tekrarlanabilir mi?
- Tam hata mesajı ve semptom yakalandı mı?

### Sadeleştir (Minimise):
Hata kırmızıya döndüğünde, senaryoyu **hâlâ kırmızıya dönen en küçük duruma** kadar budayın.
Girdileri, çağıranları ve adımları tek tek çıkarın. Kalan her şey hatayı üretmek için zorunlu olmalıdır (biri çıkarıldığında döngü yeşile dönmelidir).

## Aşama 3: Hipotez Üret (Hypothesise)

Herhangi birini test etmeden önce **3 ila 5 adet sıralanmış hipotez** üretin. Tek bir fikre saplanıp kalmayın.

Her hipotez **yanlışlanabilir (falsifiable)** olmalıdır:
> Format: "Eğer sebep <X> ise, <Y'yi değiştirmek> hatayı yok edecek / <Z'yi değiştirmek> hatayı daha da kötüleştirecektir."

Tahmini açıkça ifade edemiyorsanız o hipotez bir histir; çöpe atın ya da netleştirin.

## Aşama 4: Enstrümantasyon (Instrument)

Her prob, Aşama 3'teki somut bir tahmine karşılık gelmelidir. **Her seferinde yalnızca tek bir değişkeni değiştirin.**

- Varsa debugger veya REPL incelemesi.
- Hipotezleri ayıran sınırlara hedeflenmiş loglar.
- **Her logu benzersiz bir etiketle işaretleyin:** `[DEBUG-a4f2]`. Sonunda tek bir grep ile temizlenir.
- Performans sorunlarında log eklemeyin; profil çıkarıcı (profiler) veya query plan ile süreleri ölçün.

## Aşama 5: Düzeltme ve Regresyon Testi (Fix + Regression Test)

Doğru bir dikiş noktası (seam) varsa regresyon testini **düzeltmeden önce** yazın.
- Gerçek kullanım desenini simüle eden doğru bir dikiş noktası seçin.
- Testin kırmızıya düştüğünü görün.
- Cerrahi düzeltmeyi uygulayın.
- Testin yeşile döndüğünü görün.
- Aşama 1'deki orijinal genel senaryoyu yeniden çalıştırarak yeşili doğrulayın.

## Aşama 6: Temizlik Protokolü (Cleanup)

Görevi bitirmeden önce zorunlu kontrol listesi:
- [ ] Orijinal senaryoda hata artık yeniden üretilemiyor (Aşama 1 döngüsü doğrulandı).
- [ ] Regresyon testi kalıcı olarak yeşil geçiyor.
- [ ] Tüm `[DEBUG-...]` enstrümantasyon logları ve geçici kodlar tamamen temizlendi (`grep` ile sıfır sonuç).
- [ ] Geçici prototipler silindi.
- [ ] Doğru çıkan kök neden ve çözüm, commit / devir raporunda net olarak açıklandı.
