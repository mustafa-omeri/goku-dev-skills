# Token-Efficient Prose Compression Guidelines

> Kaynak: [juliusbrussee/caveman](https://github.com/juliusbrussee/caveman) · Scout Değerlendirme Raporu ID: 9
> Amaç: Kod blokları ve teknik kesinliği %100 korurken, açıklayıcı metinleri yüksek yoğunluklu (high-density) tutarak token tasarrufu sağlamak ve bağlam penceresini (context window) korumak.

---

## 1. Altın Kural (The Golden Rule)

> **"Kod, diff'ler, fonksiyon imzaları ve dosya yolları %100 eksiksiz ve tam; çevreleyen açıklayıcı nesir ise sıkıştırılmış ve yüksek yoğunluklu."**

Bir ajanın en büyük kaynağı bağlam penceresidir (context window). Gereksiz nezaket, giriş paragrafları ve aşırı lafazanlık (fluff) hem token tüketimini 2-3 kat artırır hem de modelin kritik kod ayrıntılarını unutmasına yol açar.

---

## 2. Nesir Sıkıştırma İlkeleri (Prose Compression Heuristics)

### 2.1 Pasif ve Dolaylı Anlatımı Doğrudan Eyleme İndirge
- ❌ *"Burada React bileşeninin her render edildiğinde yeni bir obje referansı oluşturması sebebiyle gereksiz re-render döngüsüne girdiği tespit edilmiştir. Bu durumu düzeltmek amacıyla useMemo kancası kullanılması tavsiye edilmektedir."* (36 kelime)
- ✅ *"Her render yeni referans üretip re-render tetikliyor. `useMemo` ile sarıldı."* (10 kelime)

### 2.2 Diyalog ve Törensel Dolguları Sıfırla
- "Harika bir fikir", "Kesinlikle haklısınız", "Memnuniyetle yapıyorum", "Umarım yardımcı olmuştur" gibi tüm yapay nezaket ifadelerini tamamen kes.

### 2.3 Teknik Doğruluğu Asla Kırpma
- Kod blokları, dosya adları, satır numaraları, SQL sorguları, tipler ve hata mesajları asla kısaltılmaz veya uydurulmaz.
- Sıkıştırma **yalnızca** doğal dil açıklamalarında (prose) yapılır.

---

## 3. Kompresyon Örnekleri

| Durum | Klasik Uzun Yanıt (Fluff) | Sıkıştırılmış Yüksek Yoğunluklu Yanıt (Token-Efficient) |
|---|---|---|
| **Hata Tespiti** | *"Projenizde yapmış olduğum detaylı inceleme sonucunda kullanıcı profil sayfasında bir null reference hatası oluştuğunu gördüm..."* | `UserProfile.tsx` L24: `user.profile` tanımsızken alt alana erişiliyor. |
| **Çözüm Açıklaması** | *"Bu sorunu çözmek için ilgili değişkene optional chaining operatörü ekledim ve ayrıca varsayılan bir fallback tanımladım..."* | Çözüm: `user?.profile?.avatar ?? DEFAULT_AVATAR` eklendi. |
| **Test Sonucu** | *"Yaptığım bu değişikliğin ardından sistemdeki test paketini çalıştırdım ve tüm testlerin başarılı olduğunu memnuniyetle bildirmek isterim..."* | Test: `npm test` → 12/12 PASS, hata giderildi. |

---

## 4. Uzun Oturum Faydaları

1. **Bağlam Bütünlüğü:** 30+ adımlı uzun oturumlarda bağlamın erken taşmasını ve özetleme (context compaction) ihtiyacını geciktirir.
2. **Göz Yorgunluğu Azalması:** Kullanıcı gereksiz metin bloklarını atlamak zorunda kalmaz; doğrudan teknik karara ve diff'e odaklanır.
3. **Maliyet ve Hız:** Yanıt üretim süresi (TTFT ve token generation) %40-60 kısalır.
