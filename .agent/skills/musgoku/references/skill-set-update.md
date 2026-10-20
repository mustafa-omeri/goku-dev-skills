# Goku Dev Skills — Cerrahi Güncelleme Protokolü

> Bu referans dokümanı, kullanıcının AI ajanından yüklü skill setini güncellemesini
> istediğinde izlenecek deterministik adımları tanımlar.

---

## 1. Tetikleyiciler (Triggers)

Kullanıcı aşağıdaki veya benzeri ifadelerle talepte bulunduğunda bu protokol devreye girer:

- **Türkçe:**
  - `"Goku skill güncelle"`
  - `"skill update"`
  - `"GS update"`
  - `"GS güncelle"`
  - `"goku update"`
  - `"skillset güncelle"`
  - `"skill'leri güncelle"` / `"skillleri güncelle"`
  - `"goku skills update"`
  - `"goku güncelle"`
  - `"ajan yeteneklerini güncelle"`
  - `"skill seti güncelle"`
- **İngilizce:**
  - `"update skills"`
  - `"goku update"`
  - `"skill update"`
  - `"GS update"`
  - `"update skill set"`
  - `"upgrade skills"`
  - `"sync skills"`
  - `"sync goku skills"`

---

## 2. Ajanın İzleyeceği Eylem Akışı (Execution Workflow)

Kullanıcı bu komutlardan birini verdiğinde ajan şu sırayla hareket eder:

### Adım 1 — Ön Kontrol
Çalışma alanında `.agent/` dizininin var olduğunu doğrula.
- `.agent/` yoksa kullanıcıya önce kurulum yapması gerektiğini bildir:
  `npx goku-dev-skills init`

### Adım 2 — İsteğe Bağlı Kuru Çalıştırma (`--check`)
Eğer kullanıcı özellikle "güncelleme var mı", "neyi güncelleyecek", "check et" dediyse:
```bash
npx goku-dev-skills update --check
```
Terminal çıktısını inceleyerek bekleyen güncellemeleri kullanıcıya özetle.

### Adım 3 — Cerrahi Güncelleme İcrası
Kullanıcı doğrudan güncelleme istediyse komutu çalıştır:
```bash
# Standart güncelleme (yerel npm paketinden / cache'ten)
npx goku-dev-skills update

# Veya en son GitHub main dalından canlı çekmek gerekirse:
npx goku-dev-skills update --remote
```

### Adım 4 — Dörtlü Güvenlik ve Sıfır Kirlilik Garantisi
Ajan güncelleme sonrası şu 4 ilkeyi doğrular ve kullanıcıya teyit eder:
1. **Kurulu Olmayan Skill İndirilmeme İlkesi:** Projede kurulu olmayan hiçbir skill diske yazılmaz (zero-clutter).
2. **Minimal Mod Koruması:** Proje minimal modda kurulduysa (`-m`), çıkarılmış olan ağır bileşen temaları (`component-themes/`) asla tekrar indirilmez.
3. **Proje Kuralları Dokunulmazlığı:** `AGENTS.md` dosyasındaki `## Proje Bazlı Ek Kurallar` bloğu ve `rules/*.md` altındaki özel eklemeler harfiyen korunur.
4. **Metadata Bütünlüğü:** `.agent/goku.json` manifest dosyası yeni sürüm numarası ve güncelleme zaman damgasıyla yenilenir.

### Adım 5 — Kullanıcıya Raporlama
İşlem tamamlandığında aşağıdaki kısa şablonla kullanıcıya şeffaf rapor verilir:

```markdown
### ⚡ Goku Dev Skills Güncelleme Raporu
- **Yeni Sürüm:** vX.Y.Z
- **Güncellenen Skill'ler:** [Güncellenen skill listesi veya "Tümü güncel"]
- **Güncellenen Kurallar:** [Güncellenen kural listesi]
- **Proje Kuralları Durumu:** `AGENTS.md` içerisindeki proje-özel kurallar korundu.
- **Sıfır Kirlilik:** Kurulu olmayan skill'ler bypass edildi, gereksiz dosya indirilmedi.
```
