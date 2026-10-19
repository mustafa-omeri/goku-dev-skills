# Design It Twice (İki Kez Tasarla)

Kullanıcı seçilen bir modül için alternatif arayüzleri keşfetmek istediğinde bu paralel alt ajan (sub-agent) desenini kullanın. John Ousterhout'un "Design It Twice" ilkesine dayanır: ilk aklınıza gelen fikir nadiren en iyisidir.

## Süreç

### 1. Problem Alanını Çerçeveleyin
Alt ajanları başlatmadan önce problem alanını kullanıcıya özetleyin:
- Yeni arayüzün karşılaması gereken kısıtlar
- Güvendiği bağımlılıklar ve kategorisi (`references/DEEPENING.md`)
- Kısıtları somutlaştıran taslak bir kod eskizi

### 2. Paralel Alt Ajanları Başlatın
3 veya daha fazla alt ajanı paralel olarak başlatın. Her biri derinleştirilmiş modül için **radikal derecede farklı** bir arayüz üretmelidir:
- **Ajan 1:** "Arayüzü minimize et: en fazla 1-3 giriş noktası hedefle. Giriş noktası başına kaldıracı maksimize et."
- **Ajan 2:** "Esnekliği maksimize et: birçok kullanım senaryosunu ve genişletilebilirliği destekle."
- **Ajan 3:** "En yaygın çağıran için optimize et: varsayılan senaryoyu zahmetsiz hale getir."
- **Ajan 4:** "Sınırlar arası bağımlılıklar için Ports & Adapters etrafında tasarla."

Her alt ajan şunları çıktı verir:
1. Arayüz (tipler, metotlar, parametreler, değişmezler, hata modları)
2. Kullanım örneği
3. Uygulamanın dikiş noktası arkasında ne gizlediği
4. Bağımlılık ve adaptör stratejisi
5. Ödünleşimler (trade-offs)

### 3. Sun ve Karşılaştır
Tasarımları sıralı olarak sunun, ardından **derinlik**, **yerellik** ve **dikiş noktası yerleşimi** açısından karşılaştırın. Güçlü bir gerekçeyle kendi önerinizi sunun veya hibrit bir çözüm teklif edin.
