# Goku Dev Skills — Cerrahi Güncelleme Protokolü

> Bu referans dokümanı, kullanıcının AI ajanından yüklü skill setini güncellemesini
> istediğinde izlenecek deterministik adımları tanımlar.

---

## 1. Tetikleyiciler (Triggers)

Kullanıcı aşağıdaki veya benzeri ifadelerle talepte bulunduğunda bu protokol devreye girer:

- **Komutlar & Kısayollar:**
  - `"/goku-skills-update"`
  - `"/gs-update"`
  - `"[GOKU-SKILLS-UPDATE]"`
  - `"[GS-UPDATE]"`
  - `"goku-skills-update"`
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

### Adım 1 — Kapsam Belirleme (Workspace vs. Global)
Ajan doğrudan varsayımda bulunmaz; kullanıcıya hangi kapsamda güncelleme yapmak istediğini sorar:
1. **[1] Mevcut Çalışma Alanı (Workspace):** Yalnızca aktif projedeki `.agent/` dizini ve yüklü skill'ler güncellenir.
2. **[2] Global Dağıtım (Tüm Hedef Projeler / Targets):** `skillSetWorks` kaynak deposundan `delivery.md` listesindeki tüm projelere dağıtım yapılır (`npx goku-dev-skills update --global`).
3. **[3] Topyekûn Güncelleme (Workspace + Global):** Hem mevcut proje test edilir hem de tüm kayıtlı hedeflere dağıtılır.

### Adım 2 — Ön Kontrol
- **Workspace güncellemesinde:** Çalışma alanında `.agent/` dizininin var olduğunu doğrula. `.agent/` yoksa kullanıcıya önce kurulum yapması gerektiğini bildir: `npx goku-dev-skills init`.
- **Global güncellemede:** Dağıtım yapılandırmasının (`delivery.md`) varlığını teyit et.

### Adım 3 — İsteğe Bağlı Kuru Çalıştırma (`--check`)
Eğer kullanıcı özellikle "güncelleme var mı", "neyi güncelleyecek", "check et" dediyse:
```bash
npx goku-dev-skills update --check
```
Terminal çıktısını inceleyerek bekleyen güncellemeleri kullanıcıya özetle.

### Adım 4 — Cerrahi Güncelleme İcrası
Kullanıcının belirlediği kapsama göre işlemi yürüt:

```bash
# Kapsam 1: Mevcut Workspace
npx goku-dev-skills update
# veya uzaktan en son GitHub main dalından çekmek gerekirse:
npx goku-dev-skills update --remote

# Kapsam 2: Global Dağıtım (Tüm Hedef Projeler)
npx goku-dev-skills update --global

# Kapsam 3: Topyekûn Güncelleme
python .agent/skills/musgoku/scripts/run_all_gates.py
npx goku-dev-skills update --global
```

### Adım 5 — Dörtlü Güvenlik ve Sıfır Kirlilik Garantisi
Ajan güncelleme sonrası şu 4 ilkeyi doğrular ve kullanıcıya teyit eder:
1. **Kurulu Olmayan Skill İndirilmeme İlkesi:** Projede kurulu olmayan hiçbir skill diske yazılmaz (zero-clutter).
2. **Minimal Mod Koruması:** Proje minimal modda kurulduysa (`-m`), çıkarılmış olan ağır bileşen temaları (`component-themes/`) asla tekrar indirilmez.
3. **Proje Kuralları Dokunulmazlığı:** `AGENTS.md` dosyasındaki `## Proje Bazlı Ek Kurallar` bloğu ve `rules/*.md` altındaki özel eklemeler harfiyen korunur.
4. **Metadata Bütünlüğü:** `.agent/goku.json` manifest dosyası yeni sürüm numarası ve güncelleme zaman damgasıyla yenilenir.

### Adım 6 — Kullanıcıya Raporlama
İşlem tamamlandığında aşağıdaki şablonla kullanıcıya şeffaf rapor verilir:

```markdown
### ⚡ Goku Dev Skills Güncelleme Raporu
- **Kapsam:** [Mevcut Workspace / Global Dağıtım / Topyekûn]
- **Yeni Sürüm:** vX.Y.Z
- **Güncellenen Skill'ler:** [Güncellenen skill listesi veya "Tümü güncel"]
- **Güncellenen Kurallar:** [Güncellenen kural listesi]
- **Proje Kuralları Durumu:** `AGENTS.md` içerisindeki proje-özel kurallar korundu.
- **Sıfır Kirlilik:** Kurulu olmayan skill'ler bypass edildi, gereksiz dosya indirilmedi.
- **Doğrulama Kapıları:** `python .agent/skills/musgoku/scripts/run_all_gates.py` → ✅ `[OK]`
```
