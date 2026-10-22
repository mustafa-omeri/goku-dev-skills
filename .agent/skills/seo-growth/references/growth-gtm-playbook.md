# GTM (Go-to-Market) & Büyüme Lansman Playbook'u

Bu doküman, yeni bir ürün, özellik veya açık kaynaklı kütüphane yayına alınırken organik çekim gücü (organic traction) oluşturma ve dağıtım kanallarını yönetme adımlarını kapsar.

---

## 1. 3 Aşamalı Lansman Çerçevesi

| Aşama | Zamanlama | Temel Görevler & Çıktılar |
|---|---|---|
| **1. Hazırlık (Pre-Launch)** | -14 gün → -1 gün | Landing page & SEO doğrulaması (`seo_checker.py`), demo video/GIF hazırlığı, README cilası, sosyal medya hook taslakları, erken erişim listesi. |
| **2. Lansman Günü (Launch Day)** | Gün 0 (00:01 → 23:59) | Ana platform duyurusu (Hacker News Show HN, Product Hunt, GitHub release), kurucu yorumunun sabitlenmesi, gelen sorulara <15 dk içinde anlık yanıt verilmesi. |
| **3. Sürdürülebilirlik (Post-Launch)** | +1 gün → +14 gün | Geri bildirim analizi, kullanıcıların düştüğü tuzaklar için anında v1.1 yaması, "Öğrenilen Dersler" blog yazısı, topluluk paylaşımları. |

---

## 2. Geliştirici ve Teknoloji Dağıtım Kanalları

### A. Hacker News — "Show HN" Protokolü

- **Başlık Formatı:** `Show HN: [Proje Adı] – [Tek Cümlede Ne İşe Yaradığı / Hangi Problemi Çözdüğü]`
  - *Örnek İyi:* `Show HN: Goku-Skills – 28 production-ready agent skills for fullstack devs`
  - *Örnek Kötü:* `Show HN: Check out our revolutionary next-gen AI platform!` (Pazarlama jargonu HN'de anında elenir).
- **İlk Yorum (Founder Comment):** Lansmandan hemen sonra kurucu/geliştirici yorumu eklenmeli:
  1. Bu aracı neden geliştirdik? (Kişisel deneyim ve acı noktası).
  2. Mevcut alternatiflerden temel farkı nedir?
  3. Mimari ve teknik kararlar (açık ve dürüstçe).
  4. Topluluktan ne tür geri bildirim bekleniyor?
- **Altın Kural:** Asla arkadaşlarından ya da gruplardan toplu oy (upvote) isteme; HN algoritması yapay oy artışını tespit edip cezalandırır (shadowban).

### B. Product Hunt Lansmanı

- **Zamanlama:** San Francisco saatiyle 00:01 PST (Pazartesi veya Salı günleri yüksek rekabet, Perşembe/Cuma daha dengeli).
- **Tagline:** Maksimum 60 karakter; net, anlaşılır ve eylem odaklı.
- **Varlıklar:**
  - 1 adet 1200x630 kapak görseli veya kısa demo video.
  - 4-5 adet gerçek arayüz/terminal ekran görüntüsü (mockup değil, çalışan gerçek ekranlar).
  - Kurucu Maker Yorumu (Maker Comment).

### C. Reddit & Topluluk Paylaşımları

- **9:1 Kuralı:** Toplulukta paylaşılan her 10 gönderiden 9'u faydalı, yardımlaşma ve saf değer olmalı; yalnız 1 tanesi kendi projenle ilgili olmalıdır.
- **Doğru Subreddit Seçimi:** r/webdev, r/reactjs, r/java, r/selfhosted, r/SideProject, r/opensource.
- **Gönderi Formatı:** "Lansman yaptık, satın alın" yerine "Şu zorluğu yaşarken şöyle bir çözüm geliştirdik, kodları açık kaynakta paylaştık, mimari hakkında ne düşünüyorsunuz?" yaklaşımı.

### D. GitHub README Vitrini

GitHub reposu bir yazılımın ana landing page'idir:
1. **Hero & Rozetler:** Net başlık, mimari katman rozetleri (MIT License, Stars, Tests passing).
2. **Hızlı Özet (TL;DR):** 2 cümlede değer önerisi.
3. **Demo (GIF / SVG / Terminal):** Kullanıcının 3 saniyede ne olduğunu anlamasını sağlayan görsel.
4. **Quickstart (Kopyalanabilir Komut):** Tek satırda kurulum (`npx ...` veya `docker run ...`).
5. **Mimari / Karşılaştırma Tablosu:** Alternatiflerle dürüst ve objektif kıyaslama.

---

## 3. Soğuk Başlangıç (Cold Start) & İlk Çekim Taktikleri

1. **Birebir İletişim (High-touch Onboarding):** İlk 20 kullanıcıyla birebir konuşup kurulumlarındaki sürtünmeleri sıfıra indirmek.
2. **Kişiselleştirilmiş Geri Bildirim Entegrasyonu:** Kullanıcının bildirdiği bir hatayı 2 saat içinde çözüp teşekkür ederek release notlarına adını yazmak (kalıcı sadakat ve word-of-mouth yaratır).
3. **Açık Geliştirme (Build in Public):** Hataları, zorlukları ve teknik mimari kararları LinkedIn veya X üzerinden şeffafça paylaşmak.
