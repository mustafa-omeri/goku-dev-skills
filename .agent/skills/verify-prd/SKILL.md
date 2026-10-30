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

## 5 Aşamalı Tüm Proje Denetim ve Bulgu İşleme Protokolü

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
- Mount edilmemiş, import edilip kullanılmayan veya yalnızca testlerde render edilen yetim bileşenler (orphan components).

### 4. Kullanıcı Gözle Doğrulama & Test Rehberi Uyumu
- `docs/KULLANICI_TEST_REHBERI.md` (veya kökteki) dosyasını tara: Geçmiş sprintlerde bitti denmiş tüm kritik akışların kullanıcı tarafından tarayıcıda adım adım nasıl test edileceği yazılmış mı?

### 5. Deterministik Durum Kalıcılığı ve PRD Senkronizasyonu (Zorunlu İcra Adımı — VFRLP)
⛔ **Bulguları Yalnızca Ekrana Basıp Bırakma veya Doğrudan Koda Dalıp Bulguları Unutma Yasağı:** Denetim sonucunda eksik katman, mock kalıntısı, kırık kapı veya sapma tespit edildiğinde ajan yalnızca Markdown raporu üretmekle yetinemez; ayrıca kullanıcı onarımı onayladığında doğrudan koda dalıp 4-6. maddeleri sohbet geçmişinde unutmaya terk edemez. Şu **2 Fazlı Sıfır-Kayıplı Protokolü (`Faz 0: Dağıtım ➔ Faz 1..N: Dilimli Onarım`)** tavizsiz yürütür:

1. **FAZ 0.1 — PRD / Şartnameye 4 Bölümlü Tam İşleme (`## BULGULAR`):**
   - Projenin `PRODUCT.md`, `docs/*-prd.md` veya `docs/FEATURES.md` dosyasında tarih ve saat damgalı `## BULGULAR (DENETİM RAPORU — [YYYY-MM-DD HH:mm])` ana başlığı açılarak veya güncellenerek **yalnızca tablo değil, raporun 4 ana bölümünün tamamı** hiçbir bulgu kırpılmadan kalıcı olarak dokümana işlenir:
     * `### 1. Katman Bütünlüğü Matrisi (Full-Stack Slice Audit)`:
       `| Özellik / Modül (PRD / RFC) | 1. DB / Şema | 2. Backend / RPC | 3. İstemci API | 4. UI & Skeleton | 5. Döngü Kapanışı | Nihai Hüküm |`
     * `### 2. Tespit Edilen Sahte Bitti (Phantom Done), Yetim Bileşenler ve Kırık/Eksik Bağlantılar`
     * `### 3. Doküman-Kod Sapması (Spec Drift) & Test Rehberi Denetimi`
     * `### 4. Düzeltme & Tamamlama Eylem Planı (Action Items)` (`🔴 Kritik` ve `🟡 İyileştirme` alt başlıklarının tamamı)
2. **FAZ 0.2 — Sıfır-Kayıplı `HANDOFF.md` (§0 & §3) Dağıtımı:**
   - Tespit edilen tüm `🔴 Kritik` ve `🟡 İyileştirme` maddelerine deterministik `[DOM]-[TIP]-[NO]` (`[DOM]-BUG-XXX` veya `[DOM]-US-XXX`) kimliği verilir.
   - WIP limitini (maksimum 3) koruyarak ilk 3 kritik iş `🎯 Aktif Sprint / Anlık Görev Panosu` tablosuna (`1. ⏭️`, `2. ⬜`, `3. ⬜`), kalan **tüm** Kritik ve İyileştirme maddeleri ise hemen altındaki `📌 Gelecek Fazlar & Parking Lot / Sıradaki Dilimler (RTM)` tablosuna eksiksiz kaydedilir (`AGENTS.md` §2.4 ve `handoff-session-continuity.md` §2). Tek bir bulgu dahi dışarıda bırakılmaz.
   - Kodda saptanan sistemik yanılgılar ve mimari tuzaklar (örn: unmounted components, mock kalıntıları, bypass edilen tipler) `HANDOFF.md` §0 (Tuzaklar) ve `knowledge-base.md` dosyalarına işlenir.
3. **FAZ 0.3 — `KANBAN.md` Senkronu:**
   - Katmanı eksik olduğu halde `Yapıldı` işaretlenmiş kartlar derhal `Yapılıyor` veya `Bekliyor` sütununa geri çekilir; durum `🔴 Kapatılamaz (YARIM)` olarak güncellenir.
4. **FAZ 1..N — Dilimli Cerrahi Onarım (Sliced Remediation):**
   - Faz 0 dosya mühürlemesi tamamlandıktan sonra `.agent/rules/skill-trigger-routing.md` §D.1 (Post-Verification Remediation Matrix) kurallarına göre 3'erli WIP dilimleri halinde (`🔴 Kritik` 1..N ➔ `🟡 İyileştirme` 1..M sırasıyla) ilgili yetenekler (`fix-bug`, `tdd`, `db-migration-enforcement`, `ui-polish`, `doc-coauthoring`) devreye alınarak onarım yürütülür. Her dilim bittiğinde `HANDOFF.md` §3 panosu kaydırılır.

---

## Standart Çıktı Raporu

```markdown
### 🛡️ VERIFY-PRD: TÜM PROJE & RETROSPEKTİF DENETİM RAPORU

#### Özet Metrikler & Otomasyon Durumu
- **TypeScript Derleme (`tsc`):** [EXIT 0 / Hata Sayısı / Tip Baypasları]
- **SQL ↔ İstemci API/RPC Tutarlılığı:** [RPC eşleşme sayısı, doğrudan tablo yazımı ihlalleri]
- **Birim & Entegrasyon Testleri:** [X passed / Y failed]

#### 1. Katman Bütünlüğü Matrisi (Full-Stack Slice Audit)
| Özellik / Modül (PRD / RFC) | 1. DB / Şema | 2. Backend / RPC | 3. İstemci API | 4. UI & Skeleton | 5. Döngü Kapanışı | Nihai Hüküm |
|---|---|---|---|---|---|---|
| [Modül Adı] | ✅ Var | ❌ Yok | ✅ Var | ⚠️ Skeleton Yok | ❌ Form Yok | ⚠️ YARIM (View ve Form Eksik) |
| [Modül Adı] | ✅ Var | ✅ Var | ✅ Var | ✅ Var | ✅ Var | ✅ BİTTİ (Tam Dilim) |

#### 2. Tespit Edilen Sahte Bitti (Phantom Done), Yetim Bileşenler ve Kırık/Eksik Bağlantılar
- [Dosya Yolu:Satır]: [Mock veri, bağlanmamış fonksiyon veya yetim bileşen açıklaması]

#### 3. Doküman-Kod Sapması (Spec Drift) & Test Rehberi Denetimi
- Dokümanda olup kodda eksik kalanlar: ...
- Kodda olup dokümante edilmeyenler: ...
- `docs/KULLANICI_TEST_REHBERI.md` eksik adımları: ...

#### 4. Düzeltme & Tamamlama Eylem Planı (Action Items)
- **🔴 Kritik (Katman Eksikleri, Kırık Test Ortamı & Sahte Bitti Düzeltmeleri):**
  1. [Kritik Eksik 1]: ...
  2. [Kritik Eksik 2]: ...
- **🟡 İyileştirme (Ayarlar, Mobil Bileşenler ve Doküman Senkronu):**
  1. [İyileştirme 1]: ...
  2. [İyileştirme 2]: ...

#### 5. Yapılan Sistem Durumu Güncellemeleri (Faz 0 Sıfır-Kayıplı Kalıcılık Kanıtı)
- **PRD / PRODUCT.md (`## BULGULAR - [Tarih/Saat]`):** Raporun 4 ana bölümü (Katman Matrisi, Sahte Bitti/Yetim Bileşenler, Spec Drift ve 🔴 Kritik + 🟡 İyileştirme Eylem Planı) eksiksiz işlendi.
- **HANDOFF.md (§0 & §3):** İlk 3 kritik iş Aktif Görev Panosuna, kalan tüm Kritik ve İyileştirme maddeleri RTM tablosuna `[DOM]-[TIP]-[NO]` formatıyla kaydedildi; yeni tuzaklar §0'a eklendi.
- **KANBAN.md:** [Geri çekilen veya YARIM işaretlenen kartlar veya "Değişiklik yok"].
- **knowledge-base.md:** [Eklenen yeni mimari tuzaklar veya "Yeni yok"].

#### 6. Önerilen Cerrahi Müdahale ve Aksiyon Menüsü
1. ⚡ **Anında Dilimli Cerrahi Onarım (Fix Now — Faz 1..N):** Faz 0 ile mühürlenen `🔴 Kritik` maddeleri (3'erli WIP dilimleriyle) ve ardından `🟡 İyileştirme` maddelerini ilgili yeteneklerle (`fix-bug`, `tdd`, `db-migration-enforcement`, `ui-polish`, `doc-coauthoring`) sırayla çöz.
2. 📋 **Görev Panosunda Bırak (Plan Next):** Tüm bulguları PRD `## BULGULAR`, `HANDOFF.md` ve `KANBAN.md` üzerinde kayıtlı tutarak mevcut oturumu güvenle devret.
```
