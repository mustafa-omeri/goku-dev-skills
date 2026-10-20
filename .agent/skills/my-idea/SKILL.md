---
name: my-idea
description: Proje fikir havuzunu (docs/idea/myidea.md) otonom veya kullanıcı isteğiyle değerlendirir; güncel proje durumuna göre fikirleri puanlar, bayatları eler, ilk 3 öneriyi sunar ve seçileni TDD/PRD/Sprint iş akışına bağlar. Tetikleyiciler: "fikirlerime bak", "fikirlerimi incele", "fikir havuzu", "yeni fikir seç", "myidea", "my idea", "review ideas", "idea backlog". Tetiklenmez: kesinleşmiş sprint görevleri `sprint-delivery-workflow`'a, doğrudan PRD yazımı `doc-coauthoring`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# 💡 my-idea — Proje Fikir Havuzu & Otonom Değerlendirme

Bu yetenek, proje planı (sprint, PRD, MVP) dışındaki yaratıcı, vizyoner veya deneysel fikirleri
disiplinli bir havuzda (`docs/idea/myidea.md`) yönetir. Ajan elindeki büyük işleri tamamladığında
(otonom olarak) veya kullanıcının doğrudan çağrısıyla fikirleri güncel proje durumuna göre
yeniden değerlendirir, bayatları eler, en iyi 3 fikri sunar ve seçilen konuyu mevcut geliştirme
sürecine (PRD -> Sprint -> TDD -> Kodlama) sokar.

---

## 1. Dosya Konumu ve Basit Format

Fikir havuzu tek bir dosyada tutulur:
- **Konum:** `<repo-kök>/docs/idea/myidea.md` (yoksa `.agent/templates/myidea.template.md` şablonundan oluşturulur).

### Fikir Girdi Formatı
Kullanıcı veya geliştirici aklına gelen fikri karmaşık formlara girmeden, sadece başlık ve kısa açıklamayla ekleyebilir:

```markdown
### IDEA-004: [Fikir Başlığı]
- **Durum:** 💡 `[YENI]`
- **Rating:** `8.5/10` (Etki: 9 | Efor: 8 | Uyum: 8)
- **Açıklama:** Kullanıcıya veya projeye ne sağlayacak?
- **Değer / Gerekçe:** Neden yapılmalı?
- **Ajan Değerlendirmesi:** [Ajanın son analiz notu]
```

### Durum İmleri (Status Badges)
- 💡 `[YENI]` : Yeni eklenmiş, değerlendirme bekleyen ham fikir.
- 🎯 `[ONERILEN]` : Yüksek puanlı, sıradaki geliştirme için tavsiye edilen aday.
- ⏳ `[ERTELENDI]` : Değerli ancak önkoşullar veya mevcut mimari aşama için henüz erken olan.
- ⛔ `[ELENDI - Gerekçe]` : Bayatlamış, gereksizleşmiş veya mevcut yapıyla çakışan fikir (silinmez, gerekçesiyle arşivlenir).
- ✅ `[UYGULANDI - Kart/Tarih]` : Sürece alınıp kod tabanına entegre edilmiş tamamlanan fikir.

---

## 2. Tetiklenme Anları

1. **Kullanıcı İsteği ile:**
   - `"fikirlerime bak"`, `"fikirlerimi incele"`, `"fikir havuzunda ne var"`, `"yeni fikir seç"`, `"myidea"`.
2. **Otonom Ajan Kararı ile:**
   - Mevcut sprint tamamlandığında (`SPRINT_PLAN.md` içindeki tüm işler Done olduğunda).
   - Oturum kapanışında veya devirde (`HANDOFF.md`) açık iş kalmadığında ajan kendiliğinden:
     *"Mevcut sprint hedefleri tamamlandı. Fikir havuzunu (`docs/idea/myidea.md`) inceleyerek sıradaki adımlar için 3 öneri derledim..."* diyerek devreye girer.

---

## 3. Değerlendirme & Re-rating Döngüsü

Ajan dosyaya her baktığında şu adımları izler:

1. **Projenin Son Durumunu Tara:**
   - `PRODUCT.md` ve `docs/adr/` (ürün vizyonu ve mimari kararlar)
   - `SPRINT_PLAN.md` ve `HANDOFF.md` (son tamamlanan özellikler)
   - Mevcut kod tabanı (`src/`, `components/`, `api/`)
2. **Bayat / Gereksiz Fikirleri Ele:**
   - Zaten yapılmış veya mimari kararla gereksizleşmişse başına `⛔ [ELENDI - Neden]` imi koy ve gerekçesini `Ajan Değerlendirmesi` satırına yaz.
3. **Puanlama (Re-rating):**
   - **Etki (Impact - 1-10):** Kullanıcıya veya performansa sağladığı fayda.
   - **Efor (Effort - 1-10):** Ters kolaylık (10 = hızlı/kolay, 1 = çok zor).
   - **Uyum (Fit - 1-10):** Mevcut mimari ve son sprint durumuna uygunluk.
   - **Genel Rating:** `(Etki * 0.4) + (Efor * 0.3) + (Uyum * 0.3)`
4. **Dosyayı Güncelle:**
   - Güncellenen puanları ve ajan notlarını `docs/idea/myidea.md` içine yaz.

---

## 4. Kullanıcıya Sunum Standardı

Ajan değerlendirme sonrası **en yüksek ratingli 3 konuyu** seçer ve kullanıcıya net, özet bir formatta sunar:

```markdown
💡 Fikir havuzunuzu (`docs/idea/myidea.md`) projenin son durumuna göre değerlendirdim:

1. 🎯 **[IDEA-001] Başlık** (Rating: 9.1/10)
   - *Özet:* [1 cümlelik net fayda açıklaması]
   - *Neden Şimdi:* [Mevcut kod tabanına uyumu ve hızlı kazanım gerekçesi]

2. **[IDEA-002] Başlık** (Rating: 8.4/10)
   - *Özet:* [1 cümlelik açıklama]

3. **[IDEA-004] Başlık** (Rating: 7.9/10)
   - *Özet:* [1 cümlelik açıklama]

👉 **Hangisiyle ilerlemek istersin?**
```

---

## 5. Seçilen Fikri Sürece Sokma (Pipeline Handoff)

Kullanıcı bir fikir seçtiğinde (ör. *"1 ile ilerleyelim"*), sıfırdan hayali bir süreç **uydurulmaz**. Mevcut kurallar ve skill zinciri kesintisiz çalıştırılır:

```
[Seçilen Fikir]
       ↓
1. PRD / Kapsam Senkronizasyonu (`doc-coauthoring` / PRODUCT.md güncellemesi)
       ↓
2. Sprint / Kanban Planlama (`sprint-delivery-workflow` — SPRINT_PLAN.md'ye kart ekleme)
       ↓
3. Test Güdümlü Geliştirme (`tdd` — dikey dilim & önce kırmızı test)
       ↓
4. Mimari & Temiz Kodlama (`musgoku`, `codebase-design`, `karpathy-guidelines`)
       ↓
5. Havuz Güncellemesi (`docs/idea/myidea.md` -> `✅ [UYGULANDI - Kart ID]`)
```

---

## 6. Yardımcı Komutlar (Script)

Terminal üzerinden hızlı analiz ve listeleme:

```bash
# Tüm fikirleri listele
python .agent/skills/my-idea/scripts/idea_manager.py --list

# En yüksek puanlı 3 fikri getir
python .agent/skills/my-idea/scripts/idea_manager.py --top 3

# Yoksa dosyayı şablondan başlat
python .agent/skills/my-idea/scripts/idea_manager.py --init
```
