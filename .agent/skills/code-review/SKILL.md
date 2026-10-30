---
name: code-review
description: İki eksenli kod inceleme disiplini: Standartlar (Martin Fowler smell kataloğu) ve Şartname (gereksinim ve kapsam uygunluğu) eksenlerinde paralel alt ajan denetimi yürütür. Tetikleyiciler: "kod inceleme", "code review", "smell tara", "review code", "standards review", "spec review". Tetiklenmez: otonom commit ve release adımları `git-release-workflow` kapsamındadır. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Code Review (İki Eksenli Kod İnceleme)

Sabit bir referans noktası (`HEAD` ile `main`, tag veya commit arası) arasındaki değişikliklerin iki bağımsız eksende incelenmesi:

1. **Standartlar (Standards):** Kod, bu deponun belgelenmiş kodlama kurallarına ve temel kod kokusu (code smell) standartlarına uyuyor mu?
2. **Şartname (Spec):** Kod, kaynak issue / spec / PRD dokümanının talep ettiği gereksinimleri eksiksiz ve sapmasız karşılıyor mu?

Her iki eksen, birbirlerinin bağlamını kirletmemek adına **paralel alt ajanlar (sub-agents)** olarak çalıştırılır ve sonuçları yan yana raporlanır.

## Neden İki Ayrı Eksen?

Bir değişiklik bir ekseni başarıyla geçip diğerinden kalabilir:
- Tüm repo kurallarına ve smell kontrollerine uyan ama yanlış özelliği yapan kod → **Standartlar GEÇTİ, Şartname KALDI.**
- Kullanıcının istediği özelliği birebir yapan ama projeyi spagettiye çeviren kod → **Şartname GEÇTİ, Standartlar KALDI.**

Bu iki ekseni ayrı incelemek, bir eksenin diğerini maskelemesini kesin olarak önler.

## İnceleme Süreci

### 1. Referans Noktasını Sabitleyin
Kullanıcının belirttiği referans noktasını (`commit SHA`, dal adı, tag, `main`, `HEAD~3` vb.) alın. Belirtilmediyse sorun.
Diff komutunu hazırlayın: `git diff <ref>...HEAD` (merge-base karşılaştırması). Değişiklik listesini alın: `git log <ref>..HEAD --oneline`. Diff boşsa işlemi burada durdurun.

### 2. Şartname Kaynağını Belirleyin
1. Commit mesajlarındaki issue referansları (`#123`, `Closes #45`).
2. Kullanıcının doğrudan parametre olarak verdiği yol.
3. `docs/`, `specs/`, `.scratch/` veya PRD dosyaları.
4. Hiçbiri yoksa kullanıcıya spec kaynağını sorun. Spec yoksa Şartname alt ajanı "Şartname bulunamadı" raporlar.

### 3. Standartlar ve Fowler Kod Kokusu Tabanı (Smell Baseline)
Projedeki kurallara (`AGENTS.md`, `.agent/rules/`, `CONTRIBUTING.md`) ek olarak, Martin Fowler'ın *Refactoring* kitabındaki temel kod kokuları taranır:
- **Mysterious Name (Gizemli İsim):** Amacını ve içeriğini ele vermeyen isimlendirmeler.
- **Duplicated Code (Mükerrer Kod):** Aynı mantık şeklinin birden çok yerde tekrarlanması.
- **Feature Envy (Özellik Kıskançlığı):** Bir metodun kendi verisi yerine başka bir nesnenin verisine daha çok erişmesi.
- **Data Clumps (Veri Yığınları):** Sürekli birlikte gezen parametreler (ayrı bir tip olmayı bekleyen yapılar).
- **Primitive Obsession (İlkel Tip Saplantısı):** Kendi domain tipini hak eden kavramlar için string veya int kullanılması.
- **Repeated Switches (Tekrarlayan Switch/If Cascades):** Değişiklik boyunca tekrarlanan aynı tür switch veya if-else blokları.
- **Shotgun Surgery (Saçma Cerrahisi):** Tek bir mantıksal değişikliğin çok sayıda dosyada dağınık düzenlemelere yol açması.
- **Divergent Change (Iraksak Değişim):** Tek bir dosyanın birbirinden alakasız birden fazla gerekçeyle düzenlenmesi.
- **Speculative Generality (Spekülatif Genellik):** Şartnamede istenmeyen gelecek senaryoları için eklenen gereksiz kancalar ve soyutlamalar.
- **Message Chains (Mesaj Zincirleri):** `a.b().c().d()` şeklinde çağıranın bilmemesi gereken derin nesne gezinmeleri.
- **Middle Man (Aracı Nesne):** Yalnızca işi başka sınıfa devreden gereksiz aracı sınıflar/metotlar.
- **Refused Bequest (Reddedilen Miras):** Miras aldığı metotların çoğunu ezen veya boş bırakan alt sınıflar (kompozisyon tercih edilmelidir).

*Not: Deponun kendi açık dokümantasyonu her zaman smell tabanını ezer (override).*

### 4. İki Paralel Alt Ajanı Başlatın

**Standartlar Alt Ajanı:**
- Diff ve commit listesi verilir.
- Proje kural dosyaları ve yukarıdaki smell tabanı verilir.
- Görev: Her ihlali satır/dosya bazında listelemek, araçların zaten denetlediği (linter) konuları atlamak, 400 kelime altında özetlemek.

**Şartname Alt Ajanı:**
- Diff, commit listesi ve spec/PRD içeriği verilir.
- Görev: (a) Eksik veya yarım kalmış gereksinimler, (b) İstenmediği halde eklenen kapsam kaymaları (scope creep), (c) Yanlış uygulanmış kurallar. Her bulgu için şartnamedeki maddeyi alıntılamak.

### 5. Sonuçları Birleştirin (Aggregate) & Rejection Log
Bulguları `## Standartlar` ve `## Şartname` başlıkları altında yan yana sunun. İki eksenin bulgularını asla birbirine karıştırmayın veya tek bir puanlama yapmayın.

- **Rejection Log (Bilinçli Tercih Kontrolü):** `HANDOFF.md`, `knowledge-base.md` ve `PROJECT_BRIEF.md` içinde belgelenmiş bilinçli mimari ödünler (tradeoffs) "hata" olarak sunulmaz; `## Bilinçli Tercihler (Rejection Log)` tablosuna taşınır (Ayrıntı: `references/stop-conditions-and-rejections.md`).
- **STOP Koşulları:** Kod incelemesi sonrası refactoring veya onarım adımlarında gerçeklik beklentiyle uyuşmuyorsa (`Reality Mismatch`), alt ajan durur ve onay ister.

Raporu şu özetle bitirin: Her iki eksendeki toplam bulgu sayısı ve her eksenin kendi içindeki en kritik sorunu.
