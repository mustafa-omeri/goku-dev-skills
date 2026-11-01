# [Özellik / Görev Başlığı] Uygulama Planı
<!-- 
  Bu dosya Antigravity IDE Plan Modu (/plan) ve standart geliştirme planları için zorunlu şablondur.
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2
  UYARI: Serbest metinli, TDD'siz veya 5 katmansız plan üretmek AĞIR İHLALDİR (Anti-Adhoc-Planning Slop).
-->

> **Hedef Dal / Sürüm:** `<doldur: örn. main / v1.19.0>` · **Tarih:** `<doldur: YYYY-MM-DD>`  
> **Görevlendirilen Skill'ler:** `<doldur: örn. musgoku, tdd, frontend-design, ui-ux-pro-max, security-audit>`  
> **Kullanılan MCP'ler:** `<doldur: context7, sequential-thinking veya kullanılmadı>`  
> **İlgili KANBAN Kartı:** `<doldur: örn. [SPRINT-XX]-[KART-ID] veya Yeni Kart>`  

---

## 1. [Goal Description] (Amaç & Kapsam)
<doldur: Problemin kısa tanımı, arka plan bağlamı ve bu değişikliğin neyi başardığı.>

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
Feature: <doldur: Özellik Adı>
  Scenario: <doldur: Başarılı Senaryo Tanımı>
    Given <doldur: Başlangıç durumu>
    When <doldur: Kullanıcının veya sistemin yaptığı eylem>
    Then <doldur: Beklenen somut ve gözlenebilir sonuç>
```

---

## 2. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)
> [!IMPORTANT]
> <doldur: Kullanıcının onaylaması gereken mimari kararlar, breaking change'ler veya UX tercihleri.>

## 3. Open Questions (Açık Sorular)
<doldur: Varsa kullanıcıya sorulacak netleştirme soruları; yoksa 'Açık soru bulunmamaktadır.'>

---

## 4. 📋 Sprint & KANBAN Durumu
| Kart ID | Mevcut Sütun | Hedef Sütun (Proceed Sonrası) | WIP Limiti Kontrolü |
|---|---|---|---|
| `<doldur: ID>` | `Bekliyor` | `Yapılıyor` | Maksimum 3 aktif kart kuralı geçerli |

---

## 5. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Full-Stack Vertical Slice)
> ⛔ Bir katman dahi eksikse Sahte Bitti (Phantom Done) sayılır.

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | <doldur: Yeni tablo, kolon, RLS veya 'Kapsam dışı / Salt UI'> | `<doldur>` |
| **2. Backend / View / RPC** | <doldur: Endpoint, DTO, servis, controller veya 'Kapsam dışı'> | `<doldur>` |
| **3. İstemci API Entegrasyonu** | <doldur: Fetch/Axios istemcisi, tip tanımları, API fonksiyonu> | `<doldur>` |
| **4. Arayüz / UX & Eylemler** | <doldur: Bileşen, form, 4 UX Durumu + Zorunlu Skeleton Screens UI> | `<doldur>` |
| **5. Döngü Kapanışı (Admin)** | <doldur: Verinin tüketim/onay ekranı, moderasyon veya 'Kullanıcı döngüsü'> | `<doldur>` |

---

## 6. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları
> ⛔ **PROCEED İCRA KURALI (MANDATORY):** Kullanıcı "Proceed" butonuna bastığında ajan doğrudan üretim koduna GEÇEMEZ. Sırasıyla aşağıdaki fazları icra etmek zorundadır:

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
- **Test Dosyası:** `<doldur: örn. tests/.../feature.test.ts veya *Test.java>`
- **Test Edilen Dikiş Noktası (Public Seam):** `<doldur: Dahili detaylar değil, genel arayüz davranışı>`
- **Çalıştırılacak Test Komutu:** `<doldur: örn. pnpm test -- feature.test.ts>`
- **Beklenen Başarısızlık Kanıtı:** Testin çalıştırılarak **KIRMIZI (FAIL)** olduğunun terminalde gösterilmesi zorunludur.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
- **Üretim Kod Dosyası:** `<doldur: örn. src/.../FeatureService.ts>`
- **Kapsam:** Yalnızca Faz 1'deki testi yeşile döndürecek minimal kod yazılır (spekülatif kod eklenmez).
- **Çalıştırılacak Test Komutu:** `<doldur: örn. pnpm test -- feature.test.ts>`
- **Beklenen Başarı Kanıtı:** Testin **YEŞİL (PASS)** olduğunun kanıtlanması.

### 🧩 Faz 3: 5 Katman Tamamlama & UX Durumları
- Varsa API, DB ve UI katmanları bağlanır.
- Sayfa ve veri yükleme durumlarında **Skeleton Screens UI** uygulanır (spinner yasaktır).
- 3 Cihaz ergonomisi (Mobil, Tablet, Masaüstü) kontrol edilir.

### 🧹 Faz 4: Refactor, Kapılar & Kapanış
- Kod temizliği (`code-review` & `codebase-design` standartları).
- Zorunlu kapıların çalıştırılması: `python .agent/skills/musgoku/scripts/run_all_gates.py`.
- Kullanıcı test senaryosunun `docs/KULLANICI_TEST_REHBERI.md` dosyasına eklenmesi.
- `KANBAN.md` kartının `Yapıldı`'ya taşınması.

---

## 7. Proposed Changes (Önerilen Dosya Değişiklikleri)

### [Bileşen / Modül Adı]
#### [NEW] `yol/yeni_dosya.ext`
- <doldur: Dosyanın amacı ve içereceği temel fonksiyonlar/tipler>

#### [MODIFY] `yol/mevcut_dosya.ext`
- <doldur: Yapılacak somut değişiklikler ve patlama yarıçapı analizi>

#### [DELETE] `yol/silinecek_dosya.ext`
- <doldur: Varsa silinecek dosya gerekçesi>

---

## 8. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
# 1. Kırmızı test doğrulama (Faz 1)
<doldur: test komutu>

# 2. Yeşil test doğrulama (Faz 2)
<doldur: test komutu>

# 3. Birleşik doğrulama kapıları
python .agent/skills/musgoku/scripts/run_all_gates.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları)
1. `<doldur: Adım 1 — Tarayıcıda veya konsolda ne yapılacak>`
2. `<doldur: Adım 2 — Network/DB düzeyinde ne kontrol edilecek>`
3. `<doldur: Adım 3 — Hangi Skeleton ekranı ve son durum gözlemlenecek>`
