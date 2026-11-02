# 🔭 Private Repo Scout & Intelligence Engine

Bu araç, dış GitHub repolarını token harcamadan hızlıca taramak, mimari katmanını (Backend / Frontend / Tooling) tespit etmek, mevcut `skillSetWorks` yetenek havuzumuzla kıyaslayarak **"Biz daha iyiyiz"** veya **"Entegre et / Zenginleştir"** kararı vermek için tasarlanmış **özel (private)** bir motordur.

---

## 🔒 Gizlilik ve Dağıtım Güvenliği

- **`.gitignore` Koruması:** `scout/` ve `temp/` klasörleri `.gitignore` altındadır. Bu dosyalar kesinlikle sürüm kontrolüne (git) girmez.
- **Dağıtım İzolasyonu:** `delivery.py` dağıtım aracı yalnızca `.agent/` ağacını hedef projelere (`ocai`, `FEProjectv1`, `kalansure` vb.) kopyalar. `scout/` kök dizinde yer aldığı için hedef projelere **asla sızmaz**.

---

## 🚀 Kullanım & Komutlar

Süreç iki taraflı çalışır:
1. **Kullanıcı:** İncelemek istediği repoyu `scout/repos.json` tablosuna ekler veya doğrudan komut verir.
2. **Antigravity Agent:** Komutu aldığında `scout/engine.py` üzerinden repoyu temp alanına çeker, parmak izini inceler, katman ayrımını yapar, karar verir, gerekirse entegrasyon planı hazırlar ve tabloyu günceller.

### Desteklenen Komutlar (Sohbette Ajan İçin):

| Komut | Davranış |
|---|---|
| `scout` | `scout/repos.json` dosyasındaki ilk bekleyen (`PENDING`) repoyu inceler, karara bağlar ve `scout-catalog.html` sayfasını günceller. |
| `scout all` | Tablodaki tüm `PENDING` repoları sırayla inceler. |
| `scout <github-url>` | Listede olmasa bile repoyu anında inceler, kararı verir ve tabloya ekler. |

---

## 📊 Scout Dashboard & Görsel Takip Kataloğu

İncelenen repoları, katmanları ve planları tarayıcı üzerinden modern bir arayüzle izlemek ve **doğrudan web üzerinden yeni repo eklemek** için:
- **Dosya Konumu:** [`scout/scout-catalog.html`](scout-catalog.html)
- **Özellikler:**
  - ➕ **Web Üzerinden Repo Ekleme:** Arayüzdeki "Yeni Repo Ekle" butonuna basarak URL ve katman belirleyip doğrudan `repos.json` dosyasına kaydedebilirsiniz.
  - 🚀 **Yerel Sunucu Modu (Opsiyonel):** `python scout/server.py` çalıştırarak `http://localhost:5055` adresinden tek tıkla canlı ekleme yapabilirsiniz.
  - 💡 **Sunucusuz (File) Modu:** Sunucu kapalıyken sayfayı doğrudan açsanız dahi form hazır komutu (`scout <url>`) panonuza kopyalar.
  - 🔒 **Tamamen İzole & Private:** Dağıtılan `.agent/skills-catalog.html`'den bağımsızdır, `.gitignore` altındadır.
  - 📈 **KPI Sayaçları:** Kabul/Zenginleştir, Elendi/Biz Daha İyiyiz, Bekleyen, Katman dağılımı.
  - 🔍 **Canlı Arama & Katman Filtreleri:** Frontend / Backend / Tooling anlık arama.
  - 🎛️ **Çift Görünüm:** Modern Kart Grid & Yoğun Veri Tablosu.
  - 📄 **Rapor Önizleme Modalı:** Rapor içeriğini doğrudan panelde okuma.
- **Yeniden Derleme:** `python scout/generate_scout_catalog.py` (veya `python scout/engine.py --html`). `scout` komutu her çalıştığında bu HTML otomatik güncellenir.



---


---

## ⚡ Yerel Sunucuyu Açma ve Kapatma Yöntemleri

Sunucuyu başlatmak ve durdurmak için 3 son derece pratik yol vardır:

### Yöntem 1: Çift Tıklama (En Kolay)
- **Başlatmak için:** `scout/start-server.bat` dosyasına çift tıklayın. (Otomatik olarak tarayıcınızda `http://localhost:5055` açılır).
- **Kapatmak için:** Açılan siyah konsol penceresini kapatın veya `scout/stop-server.bat` dosyasına çift tıklayın.

### Yöntem 2: Terminal / Konsol
- **Başlatmak için:**
  ```bash
  python scout/server.py
  ```
- **Kapatmak için:** Terminalde `Ctrl + C` tuşlayın.

### Yöntem 3: Sohbet Üzerinden (Ajan Aracılığıyla)
- Bana doğrudan *"Scout sunucusunu başlat"* veya *"Scout sunucusunu durdur"* demeniz yeterlidir; arka plandaki işlemi hemen yönetirim.

## ⚖️ Karar Rubriği (Değerlendirme Kriterleri)

Ajan her repo için şu 3 karardan birini verir:

1. **`BIZ_DAHA_IYIYIZ` (Eleme):**
   - Mevcut kural ve skill setimiz (`ui-ux-pro-max`, `frontend-design`, `ui-styling`, `musgoku`, `rules_gates.py` vb.) incelenen repodan daha derin, daha katı veya daha kapsamlıysa.
   - Örnek: Generic bir shadcn klonu veya basit bir todo app.
   - Çıktı: `repos.json` tablosuna gerekçeli not düşülür, gereksiz plan dosyası açılmaz (token tasarrufu).

2. **`ZENGINLESTIR` (Kabul & Entegrasyon):**
   - Repoda bizim yapımıza doğrudan değer katacak, eksik bir kural maddesi, yeni bir CLI scripti, özel bir tasarım deseni veya backend mimari kalıbı varsa.
   - Çıktı: `scout/plans/<repo-adi>.md` dosyasına cerrahi entegrasyon planı (Backend / Frontend etki alanı belirtilerek) yazılır.

3. **`KISMEN_ALINABILIR` (Cerrahi Ayıklama):**
   - Reponun tamamı değil, yalnız belirli bir algoritma, regex, CSS utility'si veya doğrulama fonksiyonu faydalıysa.
   - Çıktı: Hangi dosyanın nereye taşınacağını gösteren kısa bir plan hazırlanır.

---

## 🛡️ Token Tuzağı Önleme (Anti-Token Trap)

- Reponun tüm kaynak kodu LLM context'ine aktarılmaz.
- `scout/engine.py` reponun dosya ağacı, bağımlılıkları ve README özetinden oluşan ~10 KB'lık bir `fingerprint.json` üretir.
- Ajan sadece bu özeti okur.
- İnceleme bittiğinde klonlanan repo diskten derhal silinir (`safe_rmtree`).
