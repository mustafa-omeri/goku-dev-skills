---
name: verify-prd
description: Tüm proje ve PRD genelinde retrospektif kabul denetimi ve sahte bitti avcılığı orkestratörü; tamamlanan tüm özelliklerin beş katmanlı dikey dilimini, mock kalıntılarını ve şartname uyumunu doğrular. Tetikleyiciler: "/verify-prd", "/prd-verify", "verify prd", "[VERIFY-PRD]", "tüm projeyi denetle", "audit all features", "full project verification". Tetiklenmez: tek bir sprint denetimi `verify-sprint`'e, anlık kod değişiklikleri `verify-last`'a aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Verify PRD (Makro / Tüm Proje & Retrospektif Denetim Orkestratörü)

Bu yetenek, projenin geçmişten bugüne `SPRINT_PLAN.md`, `KANBAN.md` veya `HANDOFF.md` içinde "BİTTİ / TAMAMLANDI" olarak kaydedilmiş **tüm özelliklerini baştan sona** tarar. Amaç; otomasyon testlerinin yeşil olmasına aldanarak gözden kaçan **Sahte Bitti (Phantom Done)** durumlarını, unutulmuş mock veri kalıntılarını ve doküman-kod sapmalarını (Spec Drift) ortaya çıkarmaktır.

---

## Ne Zaman Kullanılır?

- Kullanıcı *"öncesinde tüm projeyi incele, bitti görünen işlerin gerçekten bittiğinden emin ol"*, *"/verify-prd"* veya *"/prd-verify"* dediğinde.
- Büyük bir sürüm (release / major milestone) öncesinde genel ürün kabul testi yapılırken.
- Birden fazla sprint tamamlandıktan sonra mimari borç ve eksik katman taraması gerektiğinde.

---

## 4 Aşamalı Tüm Proje Denetim Protokolü

### 1. Şartname & Kapsam Taraması (Spec vs Kod)
- `docs/*-prd.md`, `PRODUCT.md` ve `HANDOFF.md` içindeki tüm fonksiyonel gereksinimleri (`FR`), User Story'leri (`US`) ve yol haritası (`PL`) maddelerini listele.
- **Kapsam Sapması (Spec Drift):** Kod tabanında geliştirilmiş ama dokümanda olmayan veya dokümanda "bitti" denip kodda karşılığı bulunmayan maddeleri tespit et.

### 2. 5 Katmanlı Dikey Dilim Retrospektifi (Full-Stack Vertical Slice)
Tüm özelliklerin şu 5 katmandan eksiksiz geçtiğini doğrula:
1. **DB / Şema / Migration:** Tablo, kolon, indeks ve RLS politikaları veritabanında var mı?
2. **Backend / View / RPC / SQL:** Gerçek view veya endpoint'te arayüzün beklediği tüm kolonlar mevcut mu? (Kolon yoksa `undefined` döner ve bileşen sessizce hiç çizilmez).
3. **İstemci API & Tip:** Servis, React Query / hook ve TypeScript arayüzü backend ile tam uyumlu mu?
4. **Kullanıcı Arayüzü & Etkileşim:** Bileşen veriyi doğru render ediyor mu? Boş durum (empty state) ve hata yönetimi var mı?
5. **Yönetim / Giriş Formu (Döngü Kapanışı):** Bu veri sisteme nereden giriyor? (Admin formu veya kullanıcı gönderim ekranı olmadan özellik tamamlanmış sayılamaz).
*Katmanlardan biri eksikse asla 'BİTTİ' sayılamaz; durum açıkça **'YARIM (Eksik Katman: ...)'** olarak ilan edilir.*

### 3. Sahte Bitti (Phantom Done) & Mock Veri Avcılığı
- Kaynak kodda unutulmuş mock/dummy veri dizileri (`mockEvents`, `dummyItems`, hardcoded array'ler).
- Testlerin yeşil olmasına aldanıp gerçek API'ye bağlanmamış sahte fonksiyonlar.
- Arayüzde tıklanınca hiçbir işlem yapmayan ölü butonlar veya sahte linkler.

### 4. Kullanıcı Gözle Doğrulama & Test Rehberi Uyumu
- `KULLANICI_TEST_REHBERI.md` dosyasını tara: Geçmiş sprintlerde bitti denmiş tüm kritik akışların kullanıcı tarafından tarayıcıda adım adım nasıl test edileceği yazılmış mı?

---

## Standart Çıktı Raporu

```markdown
### 🛡️ VERIFY-PRD: TÜM PROJE & RETROSPEKTİF DENETİM RAPORU

#### 1. Katman Bütünlüğü Matrisi (Full-Stack Slice Audit)
| Özellik / Kart ID | 1. DB Şema | 2. View/RPC | 3. İstemci API | 4. UI / UX | 5. Admin Form | Sonuç |
|---|---|---|---|---|---|---|
| [ID / İsim] | ✅ Var | ❌ Yok | ✅ Var | ✅ Var | ❌ Yok | ⚠️ YARIM (View ve Form Eksik) |
| [ID / İsim] | ✅ Var | ✅ Var | ✅ Var | ✅ Var | ✅ Var | ✅ BİTTİ (Tam Dilim) |

#### 2. Tespit Edilen Sahte Bitti (Phantom Done) ve Mock Kalıntıları
- [Dosya Yolu:Satır]: [Mock veri veya bağlanmamış fonksiyon açıklaması]

#### 3. Doküman-Kod Sapması (Spec Drift)
- Dokümanda olup kodda eksik kalanlar: ...
- Kodda olup dokümante edilmeyenler: ...

#### 4. Düzeltme & Tamamlama Eylem Planı (Action Items)
1. 🔴 [Kritik Eksik]: ...
2. 🟡 [İyileştirme]: ...
```
