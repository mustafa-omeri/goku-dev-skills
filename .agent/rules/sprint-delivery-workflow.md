---
name: Sprint Delivery Workflow
description: Sprint plani, MVP kapsami, Gherkin kabul kriteri, kanban tasi ve release plani olusturma duzeni. Sureci tanimlayan sabit dosya adlari, kart alanlari ve kapisi zorunlu kilar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Sprint / kanban / MVP"
    komut: "python .agent/skills/musgoku/scripts/check_sprint_board.py"
---

# ⛔ KESİN KURAL: Sprint → Gherkin → Kanban → Release

> **Bu kural "zorunlu" yazıyor ve kapısı var.** Yani uyduğunu iddia ettiğin
> her şey `check_sprint_board.py` çıkış koduyla kanıtlanır. Kanıtın yoksa
> beyan etme.

---

## 0. Neden bu kural ayrı

Bu setin 2026-10-13 tespiti: 11 kural "zorunlu / asla / istisnasız" yazıyordu,
**kapısı yoktu**. Ajan "uyguladım" diyor, kimse ölçmüyor. Aynı hata
` t(key, 'Türkçe')`nın kural katmanındaki hali.

Bu kuralın ikinci amacı **determinizm**: aynı kuralı okuyan iki ajan aynı işi
**farklı biçimde yapmamalı**. Bunu açıklama satırı değil, aşağıdaki sabit sözleşme
ve kapı sağlar. Sözleşmeye uymayan ajan "yaptım" diyemez.

---

## 1. Dosya sözleşmesi (sabit adlar)

| Dosya | Nerede | Dağıtımda |
|---|---|---|
| `SPRINT_PLAN.md` | proje kökü | **dağıtılmaz** — proje-özel durum |
| `KANBAN.md` | proje kökü | **dağıtılmaz** |
| `RELEASE_PLAN.md` | proje kökü | **dağıtılmaz** |
| `specs/<kart-id>.feature` | proje kökü `specs/` | **dağıtılmaz** |
| `KULLANICI_TEST_REHBERI.md` | proje kökü (Birincil) veya `docs/KULLANICI_TEST_REHBERI.md` (Alternatif) | **dağıtılmaz** — proje-özel durum (şablon: `templates/KULLANICI_TEST_REHBERI.template.md`) |

⛔ Bu adları değiştirme veya çoğulize etme (`SPRINT_PLANS.md`). `KULLANICI_TEST_REHBERI.md` için proje kökü (birincil) veya `docs/KULLANICI_TEST_REHBERI.md` (kabul edilen alternatif) geçerlidir; kapı her iki konumu da tanır. Ad değişirse kapı susar ve kural ölü kalır.

### Şablon nasıl kullanılır

Şablonlar **nereye konulacağını ve hangi alanların bulunacağını** gösterir;
içeriği sen doldurursun:

[`.agent/templates/SPRINT_PLAN.template.md`](../templates/SPRINT_PLAN.template.md) ·
[`.agent/templates/KANBAN.template.md`](../templates/KANBAN.template.md) ·
[`.agent/templates/RELEASE_PLAN.template.md`](../templates/RELEASE_PLAN.template.md) ·
[`.agent/templates/KULLANICI_TEST_REHBERI.template.md`](../templates/KULLANICI_TEST_REHBERI.template.md)

⛔ **Şablonu olduğu gibi kopyalayıp boş bırakma.** Projeye göre uyarla:

| Karar | Neden senin |
|---|---|
| Sprint hedefi, tarih, kart id'leri | Projenin gerçek işi senin bilgin |
| `kapi:` komutları | Hangi kapı bu projede çalışıyor, projeden anlaşılır |
| Gherkin metni, `test:` adımları | Gerçek çıktıyı sen biliyorsun |
| Kart sayısı ve öncelik | Projenin o anki durumu |

Bir alanı dolduramıyorsan **"bilinmiyor" yaz veya kartı `Bekliyor`'da bırak.**
Boş bırakmak yerine kapının seni uyarmasını tercih et.

> Şablonlar `.agent/templates/` altında **dağıtılır**; her proje kendi
> kök dosyalarını kendisi açar. `npx goku-dev-skills init` plan dosyası
> **yaratmaz** — proje tercihine göre karar senindir.

---

---

## 2. Akış (her yeni sprint ve işte zorunlu sıra)

```
1. Planla & Araştır -> Nasıl yapılacak? (Detaylı plan) + Kabul Kriterleri (Gherkin) + 3. Parti Araştırması (AÇIK KAYNAK ÖNCELİKLİ)
2. Sun & Onay Al    -> Planı kullanıcıya sun, inceleme/değişiklik şansı ver; KULLANICI ONAYI OLMADAN KODA BAŞLAMA
3. Sprint Aç & Kart -> SPRINT_PLAN.md + KANBAN.md (id + Gherkin + kapi + kullanıcı test adımı)
4. Taşı             -> Yapılıyor → Sınırdı → Yapıldı (WIP limiti 3)
5. Kapat & Doğrula  -> Kapı yeşil değilse ve kullanıcı test adımı yoksa Yapıldı olamaz
6. Devret           -> RELEASE_PLAN.md: kapanmayan her kart ID'si burada
```

⛔ **Sıra atlanmaz.** Detaylı uygulama planı çıkarılmadan, acceptance criteria belirlenmeden, 3. parti araçlar araştırılmadan ve kullanıcıdan açık onay alınmadan kart `Yapılıyor`'a alınamaz ve koda başlanamaz!

### 2.1 Sprint Öncesi Detaylı Uygulama Planı ve 3. Parti Araç Araştırması (Açık Kaynak Önceliği)

1. **"Ne" Değil, "Nasıl Yapılacak?" Planı:**
   Sadece bir iş veya başlık listesi ("ne yapılacağı") bir plan değildir. Her yeni sprinte veya iş parçasına başlamadan önce:
   - Mimari yaklaşım,
   - Değişecek/oluşturulacak dosyalar ve modül sınırları,
   - Veri modelleri, arayüzler ve entegrasyon adımları detaylı olarak planlanmalıdır.
2. **Kabul Kriterleri (Acceptance Criteria):**
   Her bir teslimat için test edilebilir, somut ve gözlenebilir kabul kriterleri (`Given / When / Then` formatında Gherkin senaryoları) önceden çıkarılmalıdır.
3. **Üçüncü Parti Araç ve Kütüphane Araştırması:**
   Uygulama içinde veya altyapısında kullanılacak herhangi bir 3. parti araç, paket, kütüphane veya servis varsa, doğrudan plana eklenmeden önce detaylıca araştırılmalıdır:
   - ⛔ **Açık Kaynak (Open-Source) Önceliği Kesin Kuraldır:** Tescilli, kapalı veya ücretli araçlar yerine daima aktif bakımı yapılan, geniş topluluk desteği ve güvenilir lisansı (MIT, Apache 2.0, BSD) olan açık kaynaklı çözümler önceliklendirilmelidir.
   - Planda kütüphanenin adı, lisansı, dokümantasyon linki, neden seçildiği ve açık kaynak gerekçesi belirtilmelidir.

### 2.2 Kullanıcı İnceleme (Review), Değişiklik ve Açık Onay Kapısı

1. **Kullanıcıya Sunum:** Ajan hazırladığı detaylı uygulama planını, kabul kriterlerini ve 3. parti araç seçimlerini kullanıcıya şeffaf bir şekilde sunar.
2. **Review ve Değişiklik Şansı:** Kullanıcıya plan üzerinde inceleme (review) yapma, kapsamı daraltma/genişletme veya alternatif araç/yöntem talep etme fırsatı verilir.
3. ⛔ **Kullanıcı Onayı Olmadan Koda Başlanamaz:** Kullanıcıdan açık ve net onay ("onay", "başla", "plan uygun" vb.) alınmadan kartlar `Yapılıyor` sütununa taşınamaz ve tek bir satır dahi kod yazılamaz.

### 2.3 Sprint Dışı Dilimlenmiş (Sliced/Task) İşlerde de Aynı Sistemin İşletilmesi Zorunluluğu

⛔ **KURAL NET:** Geliştirme ister resmi bir sprint kapsamında olsun, ister sprint dışı küçük dilimlere (slice'lara) veya task listesine bölünmüş olsun:
- Eğer işin yalnızca "ne yapılacağı" (what) biliniyor ama "nasıl yapılacağı" (how) detaylandırılmamışsa, ajanın "nasılsa küçük iş, hemen kodlayayım" diyerek doğrudan koda dalması **KESİNLİKLE YASAKTIR.**
- Sprint dışındaki her task/slice için de:
  1. Detaylı nasıl yapılacak planı çıkarılır,
  2. Kabul kriterleri belirlenir,
  3. Gerekli 3. parti bağımlılıklar açık kaynak önceliğiyle araştırılır,
  4. Plan kullanıcıya sunulup review/değişiklik şansı verilir ve **kullanıcıdan açık onay alınır.** Onay geldikten sonra geliştirmeye geçilir.

### 2.4 Sprint Ortası Major Değişiklik ve PRD/Gherkin Revizyon Protokolü (Mid-Sprint Scope Disruption)

Sprint devam ederken kullanıcı tarafından talep edilen ve yapılması onaylanan, sprint hedefini veya sistem mimarisini değiştiren her **major talepte** şu 4 adımlı protokol tavizsiz işletilir:

1. **PRD Güncellemesi (Gherkin Kabul Kriteri ile):**
   Onaylanan talep, projenin `PRODUCT.md` (veya `docs/*-prd.md`) dokümanına ilgili özellik/modül altına doğrudan eklenir. Kabul kriterleri serbest metin olarak değil; `Feature` ve `Scenario` (`Given / When / Then`) formatında derin Gherkin senaryosu olarak kalıcı şekilde işlenir. Kod ile PRD dokümanının birbirinden kopması (spec drift) kesin olarak engellenir.
2. **Sprint Planı Revizyonu (`SPRINT_PLAN.md` & `RELEASE_PLAN.md`):**
   Sprint hedefi ve `**MVP Kapsam**` listesi revize edilir. Yeni işin plana dahil edilmesiyle birlikte, WIP limitini (maksimum 3 kart) ve sprint gerçekçiliğini korumak adına ötelenmesi gereken mevcut kartlar belirlenerek `RELEASE_PLAN.md`'ye aktarılır (**Kapsam Takası / Scope Trade-off**). Kullanıcıya hangi işin neden ötelendiği şeffafça bildirilir.
3. **Feature Dosyası ve Kanban Kartı Açılışı:**
   PRD'ye işlenen Gherkin senaryosu referans alınarak `specs/<kart-id>.feature` dosyası oluşturulur. `KANBAN.md` üzerinde yeni kart açılır (`gherkin:`, `kapi:`, `test:` alanlarıyla) ve `Bekliyor` sütununa kaydedilir.
4. **TDD Kırmızı → Yeşil Döngüsü:**
   Yeni talep koda dökülürken doğrudan üretim kodu yazılmaz; [`tdd`](../skills/tdd/SKILL.md) disiplini gereğince belirlenen dikiş noktasında (`seam`) önce kırmızı test yazılır, minimal kodla yeşile çevrilir ve doğrulanır.

---

## 3. Kanban sözleşmesi

### 3.1 Sütunlar — tam olarak dört, adı değişmez

`Bekliyor` → `Yapılıyor` → `Sınırdı` → `Yapıldı`

Başka sütun (`Todo`, `Blocked`, `Done`) **yazılamaz** (E3). Kart geriye
`Bekliyor`'a dönebilir — ileri hareket sırası bozulmaz.

**WIP limiti:** `Yapılıyor` en fazla **3** kart. Aşarsa yeni kart başlatma,
önce bitir. (Kapı `--wip` ile değiştirilebilir; değişiklik KB'ye yazılır.)

### 3.2 Kart biçimi — tek kip

```markdown
### S1-03 · Kullanıcı test rehberi yazılsın
| alan | değer |
|---|---|
| durum | Yapıldı |
| oncelik | P1 |
| sprint | S1 |
| gherkin | specs/S1-03.feature#rehber-nokta-basligi |
| kapi | python .agent/skills/musgoku/scripts/check_sprint_board.py |
| test | Kullanıcı KULLANICI_TEST_REHBERI.md açar, 3 numaralı adımı uygular, hangi çıktıyı neyle doğrulayacağını görür |
| risk | düşük |
```

| Alan | Kural |
|---|---|
| başlık | `### S<sprint>-<no> · <tek cümle>` — id ve başlık arası `·` |
| `durum` | bulunduğu sütunla **birebir aynı** olmalı |
| `oncelik` | `P1` · `P2` · `P3` |
| `sprint` | kartın ait olduğu sprint (`S2` = S2'ye taşındı) |
| `gherkin` | `specs/<id>.feature[#SenaryoAdi]` — **başlamış kartta dosya gerçekten olmalı** |
| `kapi` | çalıştırılabilir komut; boş bırakılmaz (E9) |
| `test` | kullanıcının **gerçekten yapacağı** adım; `Yapıldı`'da boş/sablon olamaz (E8) |
| `risk` | `yüksek` · `orta` · `düşük` |

⛔ Kart id'si **global benzersizdir.** Aynı id iki yerde kullanılmaz (E4).
Taşınan kart id'sini **korur**, sadece `sprint` alanı değişir.

### 3.3 Gherkin metodolojisi — kesin karar

Kabul kriteri düz cümle değil, `.feature` dosyasıdır:

```gherkin
# language: tr
Feature: Kullanıcı test rehberi

  Scenario: Rehber nokta başlığı
    Given KULLANICI_TEST_REHBERI.md dağıtılmış .agent/ kökünde değil, proje kökünde
    When kullanıcı rehberi açar
    Then her çıktı için "nasıl test edilir" adımı bulunur
```

- `Feature` + `Scenario` zorunlu; en az bir `Given` / `When` / **`Then`** adımı.

### 3.4 Kurumsal Gereksinim & RTM Eşleşmesi (Requirements Traceability)

Kurumsal projelerde sprint kartları bağımsız ad-hoc işler değildir; PRD ve RTM matrisindeki gereksinimlere dayanır:

1. **Sprint Kartı Başlığı & Referans:**
   - Bir sprint kartı PRD'deki bir fonksiyonel gereksinimi (`FR`) veya yol haritasındaki bir parking lot (`PL`) maddesini karşılıyorsa, başlıkta veya açıklamada gereksinim ID'si açıkça belirtilir:
     `### S25-01 · KS-PL-001: Otomatik dış kaynak çekici edge function servisi`
2. **BDD / Gherkin Senaryo Numaralandırma Standardı:**
   - Gherkin senaryoları ilgili gereksinim ID'siyle izlenebilir formatta etiketlenir:
     `@[Gereksinim ID] - SC[Sıra No] : [Senaryo Başlığı]`
     Örnek: `@KS-FR-038.1-SC01: Anonim kullanıcının sayaç favorilemesi`
3. **İzlenebilirlik Matrisi Güncellemesi:**
   - Kart `Yapıldı` sütununa geçtiğinde, `HANDOFF.md` içindeki RTM tablosunda ilgili `FR` veya `PL` maddesinin durumu `✅ Done` veya `vX.Y.Z` sürümüne bağlanır. Gereksinim asla tablodan silinmez.
- **Tek davranış = tek `Scenario`.** "Ve" ile bağlanmış iki davranış iki
  `Scenario`'dur.
- `Then` adımı gözlenebilir olmalı: *"ekran açılır"* değil, *"hata mesajı görünür"*.
- ⛔ **Yüzeysel Gherkin Yasağı (No Shallow Gherkin):** Veri toplayan/üreten (form, bildirim, geri bildirim vb.) özelliklerde kabul kriteri yalnızca arayüzdeki toast/modal mesajıyla bitemez. Ağ yanıtı ve veritabanı kalıcılığı senaryoda açıkça yer almalıdır:
  ```gherkin
  Scenario: Düzeltme bildiriminin uçtan uca kaydedilmesi
    Given kullanıcı geçerli bildirim alanlarını doldurur
    When gönder butonuna tıklar
    Then ağ isteği HTTP 201 Created döner
    And veritabanında "content_corrections" tablosuna yeni kayıt eklenir
    And RLS kuralı gereği anonim kullanıcı bu kaydı SELECT ile okuyamaz
  ```
- Kartta `gherkin:` alanı dosya yolunu **ve** senaryo adını taşır
  (`#senaryo-adi`). Senaryo adı dosyada yoksa kapı kızar (E7).

Bu karar PRD standartlarıyla **tutarlıdır**; kapsam farkı yoktur
(oran Gherkin üretir, burada kapı denetler).

---

## 4. MVP kapsamı — "ne girer / ne girmez" yazılmadan sprint açılmaz

`SPRINT_PLAN.md` içinde iki liste **zorunlu**:

- `**MVP Kapsam**` — bu sprintte teslim edilecekler (kart ID'leriyle)
- `**Kapsam Dışı**` — bilinçli olarak dışarıda bırakılanlar

Bir kart ne birinde ne diğerinde geçmiyorsa uyarı alır (W3). Bu, "kapsam
sürüklenmesi"nin en ucuz denetimidir: sprint hedefiyle kartlar arasındaki
sapma ilk gün görünür.

---

## 5. Release planı — açık iş sessizce düşmez

`RELEASE_PLAN.md`, **kapanmamış her kartın id'sini** içermek zorundadır (E10).
Bir kart taşındıysa id'si korunur; kart "unutulursa" kapı kızar.

Bu kuralın amacı: **mevcut açık işleri ezmeden aksatmayan** ilerleme. Yeni bir
sprint açarken önceki `RELEASE_PLAN.md`'deki her madde ya tamamlanmış ya da
bilinçli olarak `sprint: S<n+1>` ile taşınmış olmalıdır. Üçüncü yol
(yok saymak) yoktur.

---

## 6. Kullanıcı tarafından test edilebilirlik
 
 Her bir çıktı kullanıcı tarafından test edilebilir olmalı ve nasıl test edeceğine
 dair proje kökündeki `KULLANICI_TEST_REHBERI.md` dosyası yoksa şablondan oluşturulmalı,
 varsa güncellenmelidir.
 
 Her `Yapıldı` kartının `test:` alanı, kullanıcının **tarayıcıyı/terminali açıp
 yapacağı** adım olmalıdır. Proje genel rehberi: `KULLANICI_TEST_REHBERI.md` (proje kökünde,
 şablondan türetilir).
 
 ⛔ **Otomasyon Yeşilliği Yanılgısı (Kritik Tuzak):**
 Otomasyon testlerinin (`pnpm test`, `typecheck`, `test:e2e`, `mvn test`) yeşil olması,
 kodun syntax ve birim seviyesinde çalıştığını kanıtlar; ancak kullanıcının kendi gözüyle
 tarayıcıda bu özellikleri adım adım nasıl doğrulayacağını göstermez.
 `KULLANICI_TEST_REHBERI.md` güncellenmeden veya kullanıcıya adım adım test yöntemi
 sunulmadan kart `Yapıldı` sütununa taşınamaz ve commit onayı istenemez!
 
 💡 **İstisna (Minor Rötüş & Dahili İyileştirmeler):**
 Mevcut kullanıcı akışını, ekran bileşenlerini veya kabul senaryolarını değiştirmeyen minor
 rötüşlarda (küçük CSS/boşluk ayarı, dahili refactoring, tip düzeltmesi, typo) rehbere yapay
 satır eklenmez; mevcut senaryoların geçerli olduğu beyan edilir.
 
 ⛔ **Veri Toplayan/Üreten Çıktılarda 3 Katmanlı Doğrulama:**
 Bir form veya veri akışı içeren kartın `test:` alanı ve rehber adımı yalnızca ekrandaki başarı mesajıyla (toast/modal) yetinemez; 3 katmanlı olmalıdır:
 1. Görsel UX: Formu doldur, gönder, başarı toast'unu ve formun sıfırlandığını gör.
 2. Ağ (Network): F12 Ağ sekmesinde giden API isteğinin `201 Created` / `200 OK` olduğunu ve giden payload'u doğrula.
 3. Veritabanı (DB): Veritabanı sorgusu (`SELECT ...`) veya Admin panelinde yeni satırın oluştuğunu doğrula. DB kanıtı olmadan veri toplama işi "Yapıldı" yapılamaz.

### 6.1 UI/UX Kalite Kapısı ve Anti-Slop Zorunluluğu (Definition of Done)

Bir kart veya sprint görevi yeni bir kullanıcı arayüzü (sayfa, dashboard, form, tablo, görünüm veya bileşen) üretiyorsa ya da mevcut bir arayüzü güncelliyorsa:

1. **Zorunlu Tasarım Skilleri:** `frontend-design`, `ui-ux-pro-max` ve (Tailwind/CSS ise) `ui-styling` kurallarına uymak **ZORUNLUDUR**.
2. ⛔ **Anti-Slop Kuralı (Generic UI Yasağı):** Yalnızca fonksiyonel testlerin (`pnpm test`, `typecheck`, Gherkin senaryoları) yeşil olması işin bittiğini kanıtlamaz. Standart, tekdüze ve çiğ "AI-slop" (ör. tekdüze `p-4 bg-white border rounded` kutuları, zayıf tipografi kontrastı, hiyerarşisiz düğmeler, nefes almayan padding'ler, okunaksız veri tabloları) içeren tasarımlar **Yapıldı (Done)** kabul edilemez.
3. **Dashboard ve Yönetim Ekranı Standartları:** Yönetici (admin), onaylayıcı (approver) veya içerik sağlayıcı (provider) ekranlarında:
   - Net görsel hiyerarşi ve KPI/metrik kartları,
   - Hızlı tarama (rapid scanning): net durum rozetleri (status badges), diff/karşılaştırma alanları,
   - Boş durumlar (empty states) ve eylemlerde tehlike/onay renk dengesi zorunludur.
4. Bu görsel ve hiyerarşik standartlar sağlanmadan kart `Yapıldı` sütununa taşınamaz.

 ⛔ "Test edildi", "çalışıyor", "doğrulandı" bir test adımı **değildir**.
 Ölçülebilir sonuç içermeli: `178 test, 0 hata` · `4/4 proje doğrulandı` ·
 `[OK]` · `süre: 0:08`.

### 6.2 Uçtan Uca Dikey Dilim & Sahte Bitti Yasağı (Full-Stack Vertical Slice & Anti-Phantom Done Gate)

⛔ **TAVİZSİZ KESİN KURAL:** Bir kartın veya sprint hedefinin "Yapıldı (Done)" sütununa taşınabilmesi ve sprintin "BİTTİ / TAMAMLANDI" ilan edilebilmesi için şu 5 katmanlı **Dikey Dilim Bütünlüğü (Full-Stack Vertical Slice)** eksiksiz doğrulanmalıdır:

1. **Katman 1 (Kalıcılık & DB Şeması):**
   - Veri alanı (kolon, bayrak, sayaç, ilişki) veya yeni varlık gerektiren her özellikte fiziksel migration scripti yazılmış, uygulanmış ve `DB_MIGRATIONS.md`'ye işlenmiş olmalıdır.
   - Sadece TypeScript/Java arayüzünde (ör. `is_sponsored?: boolean`) opsiyonel tip alanı tanımlayıp veritabanı şemasını açmamak KESİNLİKLE YASAKTIR.

2. **Katman 2 (Sunucu / View / RPC / Sorgu Katmanı):**
   - Veritabanı görünümleri (SQL view'ları), API endpoint'leri veya RPC fonksiyonları bu alanı gerçekte dönmeli veya işlemelidir.
   - ⚠️ **Sessiz Render Olmamasının Önlenmesi:** SQL View'da seçilmeyen alan çalışma zamanında `undefined` geleceğinden, istemci arayüzünde bileşenin sessizce hiç çizilmemesi tuzağı (ör. `SponsoredBadge` bileşeninin canlıda asla görünmemesi) bu katmanda engellenir. View sorgularının ve RPC'lerin gerçek şemayla eşleştiği kanıtlanmalıdır.

3. **Katman 3 (İstemci Entegrasyonu & Gerçek Veri Akışı):**
   - Frontend API/servis katmanı veya React hook'u, gerçek endpoint/view ile konuşmalıdır.
   - ⛔ **Mock Yanılgısı:** Birim testinde `render(<Badge isSponsored={true} />)` testinin %100 yeşil olması, özelliğin canlıda çalıştığını KANITLAMAZ. Gerçek view/API kontratı doğrulanmalıdır.

4. **Katman 4 (Arayüz & Kullanıcı Eylemleri):**
   - Arayüz bileşeni (rozet, kart, modal, sayaç vb.); veri varlığı, yokluğu, boş ve yükleme durumları ile eksiksiz render edilmelidir.
   - Kabul kriterlerindeki (AC) tıklama sayacı, harici yönlendirme veya buton eylemleri doğrudan dummy link ile geçiştirilemez; RPC/izleme çağrısı bağlanmalı, `rel="sponsored noopener noreferrer"` gibi güvenlik/SEO etiketleri eksiksiz uygulanmalıdır.

5. **Katman 5 (Yönetim / Giriş / Döngü Kapanışı - Loop Closure):**
   - *"Bu veriyi sisteme kim, nereden ve nasıl girecek?"* sorusunun cevabı olmadan hiçbir veri tabanlı özellik bitmiş sayılamaz.
   - İçerik sağlayıcı formu, admin yönetim ekranı (`/yonetim/...`), moderasyon masası veya otomatik ingestion hattı bulunmalıdır.
   - "Kullanıcıya rozet gösterdik ama adminin veya sağlayıcının sponsorluk tanımlayacağı form sonraki sprintin TODO'su" deniyorsa, o iş BİTMEMİŞTİR; kart `Yapılıyor` veya `Bekliyor`'da tutulur ve durum açıkça **"YARIM (Yönetim Formu Eksik)"** ilan edilir.

#### Zorunlu Katman Denetimi Matrisi (Layer Audit Matrix)

Sprinti veya ilgili kartı kapatmadan önce ajan şu matrisi çıkarmak ve doğrulamakla yükümlüdür:

| Katman | Durum | Kanıt |
|---|---|---|
| 1. DB / Şema / Migration | ✅ Var / ❌ Yok / ➖ Kapsam Dışı | [migration dosya adı veya salt UI gerekçesi] |
| 2. Backend / View / RPC | ✅ Var / ❌ Yok / ➖ Kapsam Dışı | [view / RPC adı veya sorgu] |
| 3. API & İstemci Entegrasyonu | ✅ Var / ❌ Yok | [hook / servis / DTO] |
| 4. UI / UX & Eylemler | ✅ Var / ❌ Yok | [bileşen & event RPC / feedback] |
| 5. Yönetim / Giriş Formu (Döngü Kapanışı) | ✅ Var / ❌ Yok | [form / ekran veya veri kaynağı] |

⛔ **Matriste tek bir `❌ Yok` veya `⚠️ Mock/Yarım` katman dahi varsa:**
Kart `Yapıldı` sütununa TAŞINAMAZ. Sprint "BİTTİ" İLAN EDİLEMEZ.
Durum `YARIM` olarak bildirilir ve eksik katman `HANDOFF.md` §3 Sıradaki İşler ve `RELEASE_PLAN.md`'ye derhal işlenir.

---

## 7. Kapı çıktısı ve exit kodu

| Kod | Anlam |
|---|---|
| `0` | kapı geçti · **veya** plan dosyası yok → kapsam dışı |
| `1` | E1-E11: kapı kırmızı — kart `Yapıldı` olamaz |
| `2` | araç hatası (dosya okunamadı) |

```bash
python .agent/skills/musgoku/scripts/check_sprint_board.py
python .agent/skills/musgoku/scripts/check_sprint_board.py --json
python .agent/skills/musgoku/scripts/check_sprint_board.py --wip 2
```

⛔ **Kapsam dışı çıktısı yeşildir ama iş yapılmış demek değildir.**
`SPRINT_PLAN.md` yoksa kapı hiçbir şey ölçmez. Bu ayrım `delivery.py` → `SKIP`
çıktısıyla aynı mantıktadır: "denetlenmedi" ile "denetlendi ve temiz" aynı
görünmemelidir.

---

## 8. Bu kural neyi **değil** yapar

- Kod yazmaz, test koşmaz, commit atmaz — bunlar
  [development-workflow.md](./development-workflow.md) ve
  [mandatory-git-release-workflow.md](./mandatory-git-release-workflow.md)'nin işidir.
- Tasarım/i18n/bundle kapılarının yerine geçmez; o kapılar ayrıca koşar.
- Hedef projenin kendi ajanına iş atamaz; yalnızca **bu depodaki** süreci
  tanımlar.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir sprint kuralı gerekirse (ör. 2 haftalık sprint, farklı
>    sütun adları), önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.
> 4. Sütun adı, kart alanı veya dosya adı **proje blokunda değiştirilemez** —
>    kapı sabit adları okur. Değişiklik isteniyorsa kapı script'iyle birlikte
>    değişir ve `knowledge-base.md`'ye karar olarak yazılır.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_