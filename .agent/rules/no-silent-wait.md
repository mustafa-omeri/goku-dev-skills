---
name: No Silent Wait
description: Uzun süren komutlarda sessizce beklemeyi, sonsuz döngü kurmayı ve hata çıktısını tekrar tekrar denemeyi yasaklar; ilerleme bildirimi ve sağlık kontrolü düzenini tanımlar.
sinif: TUTUM
---

# ⛔ KESİN KURAL: Sessizce Bekleme, Ön Bildirim Yap

**Bu kural her komut için geçerlidir.** Nedeni: araç çıktıyı komut bitince
döndürür. Bekleme sırasında ne olduğu görünmez, ajan "çalışıyor" sanır,
kullanıcı ilerleme göremez ve süreç kilitlenir.

---

## 1. Ne yasak

| ⛔ Yasak | Neden |
|---|---|
| Bir komutun içinde bekleme döngüsü kurmak | Araç çıktıyı sonda döndürür; döngü dışarıdan izlenemez |
| Aynı komutu "çıktı yok" diye tekrar tekrar çalıştırmak | Genellikle ilk denemenin nedeni çözülmediğinde kilitlenmedir |
| Süre bildirmeden uzun komut başlatmak | Kullanıcı süreçte olduğunu bilmez |
| Sonsuz ya da çok uzun bekleme döngüsü | Hiçbir noktada ne olduğu belli olmaz |
| Çıktısı olmayan döngüde kendi kendine karar vermek | Geri dönüşü olmayan bir duruma girer |

---

## 2. Ne zaman bildirim zorunlu

| Süre | Davranış |
|---|---|
| **~30 saniyeyi aşacak her iş** | Başlamadan **önce tek satır** yaz: ne yapıyorum, en fazla kaç dakika sürecek, hangi adımda. |
| Arka planda bırakılan iş | Başlatıldığını ve nasıl izleneceğini yaz. |
| Kısa komut (~10 saniye) | Bildirim gerekmez. |

Örnek:
> Maven test derlemesi çalıştırıyorum, yaklaşık 3 dakika sürecek. Bitince tek
> komutla doğrulayıp net sonucu yazacağım.

---

## 3. Doğru çalışma düzeni

### 3.1 Sunucu / uzun ömürlü süreç

Sunucu, izleyici, kuyruk ve benzeri süreçler **asenkron** başlatılır ve
komut **hemen döner**. Bkz. ilgili platformun "arka planda başlat" yolu
(ör. süreci ayrı pencerede / ayrı iş olarak başlatma).

⛔ Bir komutun içinde bekleme saniyeleri **yok.**

### 3.2 Bekleme yerine kısa sağlık kontrolü

Beklemek yerine **kısa ve bitmiş** komutlarla durum sorulur:

| Amaç | Kontrol |
|---|---|
| Derleme bitti mi? | Çıktı/derleme dizini var mı, log dosyası büyüdü mü |
| Sunucu ayakta mı? | Tek istek — sağlık uç noktası veya ana sayfa |
| Test koştu mu? | Test rapor dosyası veya sayaç |

Kurallar:

1. Her kontrol **kısa ve bağımsızdır**; hiçbiri diğerinin çıktısına bağlı değildir.
2. Her kontrol **tek satır net sonuç** döndürür: `200` · `yok` · `3/12 dosya` · `zaman aşımı`.
3. Kontrolü tekrar etmek **döngü değildir** — her çağrı bitmiş ve bağımsız bir
   işlemdir. Asıl döngü, komutun **içinde** beklenmesidir.
4. Sağlık kontrolü çalışmıyorsa önce **nedenini yaz**, sonra tekrar dene.

### 3.3 Zaman aşımı

- Bekleme noktaları zaman aşımı tanımlar; süresi geçen adım **hızlı FAIL** verir.
- Hızlı FAIL = net hata mesajı + ne denendi + önerilen sonraki adım.
- Uzun süren iş = önceden **bildirilmiş** bekleme.
- Aradaki fark: sessizce donup kalmak **asla** olmaz.

---

## 4. Sonsuz döngü kurmama

Her döngüde üç şey aynı anda bulunmalıdır:

| Öğe | Örnek |
|---|---|
| Sayaç | "3/10 denendi" |
| Üst sınır | "en fazla 3 deneme" |
| Net hata mesajı | "sağlık uç noktası 3 denemede de zaman aşımı verdi" |

Üst sınır dolduğunda döngü **kendiliğinden durur** ve ne olmadığı yazılır.
"Belki biraz daha bekleyeyim" gerekçesiyle sınır aşılmaz.

---

## 5. Kurulum benzeri adımlar

Adım adım kurulum ve benzeri uzun akışlarda:

1. **Yol haritası** — sıralı adımları, her birinin süresini ve başarı ölçütünü yaz.
2. Her adımda **tek çıktı satırı**: adım tamam / başarısız + neden.
3. Toplam ilerleme **sayısal** olarak bildirilir (`4/7 adım`).
4. Bir adım takılırsa **o adımda** dur, ilerleme durumunu yaz, kararı sor.
   Sonraki adımlara sessizce geçme.

---

## 6. Kuralın kendi istisnası

Bu kuralın kendisi bir uygulama hatasıdır ve düzeltilebilir. O durumda:
kullanıcıya **açıkça** "süreç bildirimi atlandı" diye bildir. Gizleme.
Aynı ihlal ikinci kez yaşanırsa `knowledge-base.md`'ye yaz.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir zaman aşımı veya bekleme kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_