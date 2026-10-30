# STOP Koşulları, Reality Mismatch Abort & Rejection Log Sözleşmesi

> **Kaynak:** `shadcn/improve` Cerrahi Entegrasyonu (`plans/improve.md`)  
> **Kapsam:** `.agent/skills/code-review/`, `diagnosing-bugs`, alt-ajan iş delegasyonu ve refactoring iş akışları.

---

## 1. Çekirdek Felsefe: "The Plan is the Product"

Yapay zeka orkestrasyonunda zekanın en yoğun biriktiği aşama **keşif, kök neden tespiti ve uygulama şartnamesi çıkarma (Planning / Recon)** aşamasıdır.

- Plan bir kez dondurulduğunda, uygulama aşamasındaki alt ajanlar veya modeller serbest metinli varsayımlarla plana müdahale edemez.
- Plan içinde hedeflenen dosya yolları, dikiş noktaları (`seams`), beklenen mevcut durum ve çalıştırılacak doğrulama komutları açıkça yer alır.

---

## 2. STOP Koşulları (Reality Mismatch Abort Protocol)

Alt ajanlara veya alt iş parçacıklarına görev delege edildiğinde en büyük hata; alt ajanın kod tabanındaki gerçekliği plandaki varsayımdan farklı bulduğunda **"tahmin yürüterek"** veya **"kendi kafasından uydurarak"** kod üretmeye devam etmesidir.

### ⛔ Kesin Kural:
Bir alt ajan bir dosyayı düzenlemeye, bir metodu taşımaya veya bir refactoring uygulamaya başladığında; eğer kod tabanındaki durum planda tarif edilen durumla örtüşmüyorsa (Reality Mismatch) **DERHAL DURMALIDIR (STOP).**

### STOP Tetiklenme Koşulları:
1. **Eksik Dosya / Yol Sapması:** Planda belirtilen dosya yolu mevcut değilse veya farklı bir dizine taşınmışsa.
2. **Beklenmeyen Fonksiyon İmzası:** Değiştirilecek fonksiyonun parametreleri, dönüş tipi veya mantığı planda varsayılandan farklıysa.
3. **Kırık Önkoşul (Pre-condition Failure):** Planda "X testi geçiyor olmalı" veya "Y paketi kurulu olmalı" denildiği halde önkoşul sağlanmıyorsa.
4. **Çelişkili Mevcut Durum:** Planda "burada bir switch bloğu var" denildiği halde dosyada polimorfik bir yapı kurulmuşsa.

### STOP Bildirim Formatı:
```markdown
🛑 STOP: REALITY MISMATCH DETECTED
- **Hedef Dosya / Bileşen:** [Dosya yolu ve satır]
- **Plandaki Beklenti:** [Planda tarif edilen kod veya durum]
- **Karşılaşılan Gerçeklik:** [Kod tabanındaki gerçek durum]
- **Durdurma Gerekçesi:** Varsayımla kod üretilirse regresyon veya veri kaybı riski mevcuttur.
- **Kullanıcı / Üst Ajan Kararı Bekleniyor:** [Seçenek A vs Seçenek B]
```

---

## 3. Rejection Log (Bilinçli Mimari Tercih & Sahte Bulgu Kütüğü)

Kod inceleme (`code-review`) ve güvenlik denetimi (`check-security`) yapan alt ajanların en yaygın zafiyeti, projenin geçmişte **bilinçli olarak verdiği ödünleri (conscious tradeoffs)** veya geçici kararları "yeni bir hata / smell" sanarak raporlamasıdır (False Positive).

### Recon Katmanı (Zorunlu Ön Okuma):
İnceleme ajanı bulgu listesini kesinleştirmeden önce projenin karar hafızasını tarar:
- `HANDOFF.md` §0 (Tuzaklar) ve §4 (Alınan Kararlar)
- `knowledge-base.md` (Kalıcı Kararlar ve Bilinen Hatalar)
- `PROJECT_BRIEF.md` (Mimari Omurga)
- `docs/adr/` (Mimari Karar Kayıtları)

### Rejection Log İşletimi:
Eğer bulunan bir "kod kokusu" veya "şartname sapması", yukarıdaki karar belgelerinde açıkça gerekçelendirilmiş bir kararın sonucuysa:
1. Bu bulgu genel "Hata" listesine yazılmaz.
2. Raporun sonundaki `## Bilinçli Tercihler (Rejection Log)` tablosuna taşınır.
3. Böylece geliştiriciler her oturumda aynı yanlış pozitiflerle yorulmaz.

#### Örnek Rejection Log Tablosu:
| Dosya / Bölüm | Algılanan Smell | Elenme Nedeni | İlgili Karar Referansı |
|---|---|---|---|
| `scout/server.py` | `Primitive Obsession` / raw HTTP handler | Sıfır 3. parti bağımlılık tercihi | `knowledge-base.md` §2026-10-30 |
| `scout/` | `.gitignore` içinde yer alması | Yerel keşif motorunun bağımsız kalması | `HANDOFF.md` §5 |
