---
name: fix-bug
description: Sistematik altı aşamalı hata ayıklama ve kırmızı geri bildirim döngüsü orkestratörü; kök neden tespiti, regresyon testi ve cerrahi onarım sağlar. Tetikleyiciler: "/fix-bug", "fix bug", "[FIX-BUG]", "hata ayıkla", "bug çöz", "neden çalışmıyor". Tetiklenmez: yeni özellik ekleme `musgoku`'ya aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Fix Bug Ensemble Orchestrator

Bu yetenek, sisteme yeni hatalar ve regresyonlar sokmadan kök nedeni bilimsel yöntemle tespit edip çözen 6 aşamalı sistematik hata ayıklama protokolünü işletir.

## Orkestrasyon Akışı

1. **Kırmızı Geri Bildirim Döngüsü Kurma:**
   - Kodda tek bir satır dahi değiştirmeden önce, hatayı deterministik olarak tetikleyen ve başarısız olan (FAIL) bir test veya doğrulama senaryosu oluştur.
2. **Kök Neden Analizi:**
   - Belirtiyi (semptom) değil, temel mekanizmayı analiz et. Logları, stack trace'leri ve veri akışını incele.
3. **Cerrahi Onarım:**
   - `musgoku` ve `karpathy-guidelines` prensiplerine uygun olarak, yalnızca hatayı gideren minimal ve odaklı düzeltmeyi uygula.
4. **Yeşil Doğrulama:**
   - Adım 1'de oluşturulan kırmızı testin artık başarıyla geçtiğini (PASS) doğrula.
5. **Regresyon Denetimi:**
   - Mevcut tüm test paketini çalıştırarak yan etki oluşmadığını kanıtla.
6. **Ders Çıkarma:**
   - Hatanın kök nedenini ve çözümünü `knowledge-base.md` dosyasına kaydet.
