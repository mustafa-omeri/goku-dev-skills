# STANDART KULLANICI REHBERİ TASARIM SPESİFİKASYONU (`rehber_design.md`)

> Bu doküman, tüm projelerde üretilen `docs/kullanici_rehberi.html` (veya İngilizce projelerde `docs/user-guide.html`) dosyasının **değişmez sistem tasarım standardıdır**.
> Her projede özelliklerin adım adım yapılışını ve kullanımını anlatan interaktif HTML rehberi bu tasarım spesifikasyonuna harfiyen uyarak üretilir.
> Proje geliştiricisi isterse kendi projesinde bu dosyayı manuel olarak özelleştirebilir.

---

## 1. TASARIM FELSEFESİ VE ESTETİK PRENSİPLER (Visual Standards)

Kullanıcı rehberi, salt kuru bir metin sayfası değil; `skills-catalog.html` seviyesinde modern, yüksek bilgi yoğunluğuna sahip, interaktif ve yaşayan bir ürün kılavuzudur.

1. **Tipografi Hiyerarşisi:**
   - **Display / Başlıklar:** `Space Grotesk`, `sans-serif` (500, 600, 700 ağırlıklar; modern teknik karakter).
   - **Gövde / Metinler:** `Plus Jakarta Sans`, `system-ui`, `sans-serif` (400, 500, 600 ağırlıklar; kusursuz okunabilirlik).
   - **Kod, Uç Noktalar ve Parametreler:** `JetBrains Mono`, `monospace` (0.8125rem; kod blokları ve URL yolları).
2. **3 Katmanlı Token ve Renk Mimarisi (`themes.css` Uyumu):**
   - Sayfa hiçbir zaman hardcoded renkler içermez; doğrudan sistem semantik CSS değişkenlerine (`--bg-base`, `--bg-surface`, `--bg-elevated`, `--border-subtle`, `--text-primary`, `--text-secondary`, `--text-muted`, `--accent-primary`) bağlanır.
   - Koyu mod (`[data-theme="..."]`) varsayılandır; tek tıkla açık moda (`[data-mode="light"]`) geçişi destekler.
3. **Sıfır Dış Bağımlılık (Zero External Runtime Dependency):**
   - Rehber tamamen çevrimdışı (`file://`) çalışabilir olmalıdır. Dış JavaScript kütüphanesi (React, Vue, CDN bundle) yüklenemez; saf modern vanilla ES6+ ve CSS3 kullanılmalıdır. (Yalnızca Google Fonts `@import` linki eklenebilir; font yüklenemezse sistem fontlarına geri düşer).

---

## 2. SAYFA ANATOMİSİ VE BİLEŞEN YERLEŞİMİ

Bir `kullanici_rehberi.html` sayfası şu 4 ana bölümden oluşur:

### 2.1 Üst Bar & Kokpit Başlığı (Sticky Header)
- **Marka & Başlık:** Proje adı, projenin canlı sürüm rozeti (`v1.x.x`), son güncelleme tarihi.
- **Canlı Arama (Instant Search):** Başlık, açıklama, katman ve etiketlerde anında süzme yapan arama kutusu (`Ctrl+K` veya `/` odaklanması).
- **Kategori Filtre Hapları (Filter Pills):** `Tümü`, `Mimari & Altyapı`, `Kullanıcı Arayüzü (UI)`, `Veri & API`, `Güvenlik & Yetki` gibi alanlara göre tek tıkla filtreleme.
- **Hızlı Sayaçlar (Metrics Strip):** Toplam özellik sayısı, tamamlanan dilimler, aktif skeleton durumu.
- **Tema & Mod Kontrolü:** Koyu / Açık mod toggle butonu (`🌙 / ☀️`).

### 2.2 Özellik Kartı Mimarisi (Feature Card Anatomy)
Her bir geliştirilen veya dokümante edilen özellik, aşağıdaki **4 zorunlu bölümü** içeren bağımsız bir kart olarak sunulur:

1. 🎯 **Amaç & Katma Değer:**
   - Ne işe yarar? Hangi kullanıcı problemini çözer? (2-3 cümlelik net iş değeri).
2. 🏗️ **Nasıl Yapıldı? (5 Katmanlı Dikey Dilim - Full-Stack Vertical Slice):**
   - Sekmeli veya kademeli panel yapısıyla 5 katmanın somut dökümü:
     * **1. DB / Şema / Migration:** Tablo, kolon, entity veya migration adı.
     * **2. Backend API / View / RPC:** Controller, servis, endpoint, RPC veya Edge Function yolu.
     * **3. İstemci Entegrasyonu:** API client metodu, SDK fonksiyonu veya veri çekme kancası (`useQuery`, `fetch`).
     * **4. UI Bileşenleri & State:** Ekran bileşeni (`src/components/...`), state yönetimi ve kullanıcı etkileşimi.
     * **5. Admin / Döngü Kapanışı:** Verinin sisteme nasıl girdiği (admin formu, submission ekranı).
3. 🚀 **Nasıl Kullanılır? (Adım Adım Playbook — FAA AC 121-24C):**
   - Sıfır lakırdı (Zero Fluff), kesin kronolojik sıralı eylemler.
   - Her adım deterministik formatta: `[Adım N]. [Eylem / Tıklama / Giriş] -> [Beklenen Görsel Çıktı / Ekran Değişimi]`.
   - Sayfa rotası, tıklanacak buton etiketleri ve form alanları atomik olarak belirtilir.
   - Riskli/yıkıcı eylemlerde komuttan/eylemden önce `⚠️ CRITICAL:` bloğu yer alır.
   - Playbook çekmecesi sonunda `| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |` hızlı sorun giderme tablosu zorunludur.
4. 📱 **Dört Arayüz Durumu (Interactive States Preview):**
   - Kart üzerinde interaktif olarak simüle edilebilen 4 UX durumu:
     * **İskelet Ekran (Skeleton Screens UI):** Veri yüklenirken sayfa kaset yapısını birebir taklit eden gri shimmer animasyonu.
     * **Dolu Durum (Hydrated State):** Verinin başarıyla ekranda listelendiği normal görünüm.
     * **Boş Durum (Empty State):** Henüz veri yokken gösterilen açıklayıcı ikon, metin ve "İlk Kaydı Ekle" CTA butonu.
     * **Hata Durumu (Error / Retry State):** Hata durumunda beliren bilgilendirme ve "Yeniden Dene" aksiyonu.

### 2.3 Doğrulama ve Test Adımları Çekmecesi (User Verification Playbook)
- Kullanıcının tarayıcı konsolunda veya arayüzde özelliği bizzat gözüyle test edebilmesi için adım adım manuel test talimatları.

### 2.4 Sayfa Altlığı (Footer)
- Projenin `PROJECT_BRIEF.md` ve `HANDOFF.md` durumuna referans, mimari sağlık damgası ve telif/versiyon bilgisi.

---

## 3. ZORUNLU CSS VE SKELETON ENTEGRASYONU

`kullanici_rehberi.html`, `themes.css` içindeki `.skeleton` shimmer motorunu ve semantik token'ları birebir kullanmalıdır:

```css
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-box {
  background: linear-gradient(90deg, var(--bg-surface) 25%, var(--bg-elevated) 50%, var(--bg-surface) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.6s infinite cubic-bezier(0.4, 0, 0.6, 1);
  border-radius: 6px;
  border: 1px solid var(--border-subtle);
}
```

---

## 4. PROJELERDE YAŞATMA PROTOKOLÜ

1. Ajan her anlamlı geliştirme veya sprint bitiminde `docs/kullanici_rehberi.html` dosyasını bu spesifikasyona sadık kalarak günceller.
2. Var olan özellik kartları korunur; yeni özellikler en üste veya ilgili kategori altına yeni kart olarak eklenir.
3. Minor rötüş veya dahili refactoring durumlarında (kullanıcı akışı değişmediğinde) raporda *"Güncelleme gerekmedi (Minor rötüş / mevcut senaryolar geçerli)"* beyan edilir.
