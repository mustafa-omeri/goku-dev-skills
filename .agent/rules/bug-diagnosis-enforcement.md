---
name: Bug Diagnosis & Red-Loop Enforcement
description: Hata ayıklama ve regresyon düzeltmelerinde kod değiştirmeden veya varsayım üretmeden önce hatayı kanıtlayan kırmızı geri bildirim döngüsü kurulmasını zorunlu kılar.
sinif: SUREC
---

# 🐞 Hata Teşhisi ve Kırmızı Döngü Kuralı (Bug Diagnosis & Red-Loop Enforcement)

Bu kural, yazılım geliştirme sürecinde "tahmin yürüterek kod yamalama" (guess-and-patch / vibe coding) alışkanlığını kesin olarak yasaklar. Hata ayıklama, doğrulanabilir bir mühendislik disiplinidir.

İlgili yetenek kılavuzu: [`.agent/skills/diagnosing-bugs/SKILL.md`](../skills/diagnosing-bugs/SKILL.md)

---

## ⛔ 1. KESİN VE TAVİZSİZ KURAL: Kırmızı Döngü Olmadan Koda Dokunma Yasağı

Ajan, kullanıcı bir hata bildirdiğinde veya bir çökme/performans sorunu yaşandığında:

1. **Önce Kırmızı Döngü:** Hatanın varlığını ve kullanıcının tarif ettiği tam semptomu kanıtlayan **çalıştırılabilir tek bir komut** oluşturup en az bir kez çalıştırmadan ve çıktısında **kırmızı (fail) verdiğini kanıtlamadan**:
   - ⛔ **ASLA kaynak kodda değişiklik yapamaz.**
   - ⛔ **ASLA "bence sorun şurada" diyerek spekülatif teori üretemez.**
   - ⛔ **ASLA koda rastgele debug logları serpiştiremez.**

2. **İstisna Durumu (Döngü Kurulamıyorsa):**
   Eğer döngü nesnel olarak kurulamıyorsa (ortam erişimi yok, harici gizli veri eksik vb.), ajan durmalı, ne denediğini açıkça listelemeli ve kullanıcıdan (a) repro ortamı, (b) sanitize edilmiş log/har verisi veya (c) geçici enstrümantasyon izni istemelidir. Döngü olmadan hipotez aşamasına geçilemez.

---

## 2. Sistematik 6 Aşama Protokolü

### Aşama 1: Sıkı ve Kırmızı Geri Bildirim Döngüsü Kurma (Tight Red Loop)
Aşağıdaki mekanizmalardan biriyle en hızlı, deterministik ve otonom çalıştırılabilir döngüyü kurun:
- Doğru dikiş noktasında (seam) **Failing Test** (Birim, entegrasyon veya e2e).
- Dev sunucuya karşı **Curl / HTTP isteği**.
- CLI çağırma ve snapshot diff'i.
- Headless tarayıcı otomasyonu.
- Yakalanan bir payload/trace'in izole kod yolunda yeniden oynatılması.

### Aşama 2: Yeniden Üretim ve Yük Taşımayan Kodları Budama (Minimise)
Hata kırmızıya döndüğünde girdileri, adımları ve parametreleri tek tek budayın. Kalan her bileşen hatanın tetiklenmesi için zorunlu olmalıdır (biri çıkarıldığında yeşile dönmelidir).

### Aşama 3: Sıralanmış 3-5 Yanlışlanabilir Hipotez
Tek bir fikre kilitlenmeyin. Test etmeden önce 3 ila 5 adet sıralı hipotez listeleyin:
> "Eğer sebep X ise, Y'yi değiştirmek hatayı çözecektir / Z'yi değiştirmek hatayı büyütecektir."

### Aşama 4: Cerrahi Enstrümantasyon ve `[DEBUG-xxxx]` Etiketleri
- Her log, Aşama 3'teki somut bir tahmini sınamalıdır.
- Her seferinde **yalnızca tek bir değişken** değiştirilmelidir.
- Eklenen her debug loguna benzersiz etiket konulmalıdır: `[DEBUG-a4f2]`.

### Aşama 5: Dikiş Noktasında Regresyon Testi ve Düzeltme
- Düzeltme yapılmadan önce, hatanın gerçek kullanım desenini sınayan dikiş noktasında regresyon testi yazılır ve kırmızı verdiği görülür.
- Minimal cerrahi düzeltme uygulanır.
- Testin yeşile döndüğü kanıtlanır.
- Aşama 1'deki orijinal genel döngü çalıştırılarak tam çözüm doğrulanır.

### Aşama 6: Temizlik Protokolü (Zero-Artifact Cleanup)
İş tamamlandı denmeden önce:
- [ ] Orijinal hata döngüsü yeşil (hata çözüldü).
- [ ] Regresyon testi yeşil ve kalıcı.
- [ ] Tüm `[DEBUG-...]` logları koddan tamamen silindi (`grep` ile sıfır eşleşme).
- [ ] Geçici test harness/script'leri temizlendi.
- [ ] Doğru çıkan kök neden ve çözüm, devir raporunda açıklandı.
