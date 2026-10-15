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
| `KULLANICI_TEST_REHBERI.md` | proje kökü | **dağıtılmaz** — proje-özel durum (şablon: `templates/KULLANICI_TEST_REHBERI.template.md`) |

⛔ Bu adları değiştirme, çoğulize etme (`SPRINT_PLANS.md`) veya başka bir klasöre
koyma. Kapı bu adlara bakar; ad değişirse kapı susar ve kural ölü kalır.

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

## 2. Akış (her yeni işte bu sıra)

```
1. Sprint aç      -> SPRINT_PLAN.md: Hedef + MVP Kapsam + Kapsam Dışı
2. Kart yaz       -> KANBAN.md: id + Gherkin dosyası + kapi + kullanıcı test adımı
3. Taşı           -> Yapılıyor → Sınırdı → Yapıldı  (WIP limiti 3)
4. Kapat          -> kapı yeşil değilse Yapıldı olmaz
5. Devret         -> RELEASE_PLAN.md: kapanmayan her kart ID'si burada
```

⛔ **Sıra atlanmaz.** Gherkin yazılmadan kart `Yapılıyor`'a girmez;
kullanıcı test adımı yazılmadan kart `Yapıldı` olamaz.

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
- **Tek davranış = tek `Scenario`.** "Ve" ile bağlanmış iki davranış iki
  `Scenario`'dur.
- `Then` adımı gözlenebilir olmalı: *"ekran açılır"* değil, *"hata mesajı görünür"*.
- Kartta `gherkin:` alanı dosya yolunu **ve** senaryo adını taşır
  (`#senaryo-adi`). Senaryo adı dosyada yoksa kapı kızar (E7).

Bu karar PRD yazan `musgoku-prd` skill'iyle **tutarlıdır**; kapsam farkı yoktur
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
 
 ⛔ "Test edildi", "çalışıyor", "doğrulandı" bir test adımı **değildir**.
 Ölçülebilir sonuç içermeli: `178 test, 0 hata` · `4/4 proje doğrulandı` ·
 `[OK]` · `süre: 0:08`.

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