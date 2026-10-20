# 💡 PROJE FİKİR HAVUZU (myidea.md)

> Bu dosya, mevcut sprint veya PRD kapsamı dışındaki yaratıcı, vizyoner ve deneysel fikirlerin serbestçe toplandığı havuzdur.
> Geliştirici veya kullanıcı aklına gelen her fikri buraya serbest formatta ekleyebilir.
> AI Kod Ajanı; büyük işler bittiğinde (otonom olarak) veya "fikirlerime bak" dendiğinde bu dosyayı inceler,
> projenin güncel durumuna göre re-rating yapar, bayatları eler ve en iyi 3 fikri sunar.

---

## 📌 Status Badges
- 💡 `[NEW]` : Newly added raw idea awaiting assessment.
- 🎯 `[RECOMMENDED]` : High-scoring idea recommended for the next sprint.
- ⏳ `[DEFERRED]` : Valuable, but deferred due to prerequisites or timing.
- ⛔ `[DROPPED - Reason]` : Obsolete, duplicated, or superseded (never deleted, archived with reason).
- ✅ `[SHIPPED - Card/Date]` : Shipped and verified in the codebase.

---

## 🎯 Puanlama (Rating) Kriterleri (1 - 10)
- **Etki (Impact - 1-10):** Kullanıcı deneyimine, performansa veya ürün değerine katkısı.
- **Efor (Effort - 1-10):** Ters orantılı kolaylık (10 = çok kolay/hızlı, 1 = çok zor/karmaşık).
- **Proje Uyumu (Fit - 1-10):** Mevcut sprint, mimari ve ürün vizyonuyla uyumu.
- **Genel Rating:** `(Etki * 0.4) + (Efor * 0.3) + (Proje Uyumu * 0.3)`

---

## 🚀 Fikirler Listesi

### IDEA-001: CLI ile Tek Komutta Fikir Havuzunu İnceleme ve Sıralama
- **Durum:** 💡 `[NEW]`
- **Rating:** `9.1/10` (Etki: 9 | Efor: 9 | Uyum: 10)
- **Açıklama:** Terminalden `python .agent/skills/my-idea/scripts/idea_manager.py --top 3` çağrıldığında en yüksek puanlı fikirleri listelemesi.
- **Değer / Gerekçe:** Geliştiricinin ve ajanın fikir havuzunu anında analiz etmesini ve otomasyona bağlamasını sağlar.
- **Ajan Değerlendirmesi:** `my-idea` skill'i bünyesinde kolayca test edilebilir script ile uygulanabilir.

### IDEA-002: Fikirlerin GitHub Issue veya Kanban Kartına Otomatik Dönüştürülmesi
- **Durum:** ✅ `[SHIPPED - my-idea SKILL §5 & CLI --to-card]`
- **Rating:** `8.4/10` (Etki: 8 | Efor: 8 | Uyum: 9)
- **Açıklama:** Seçilen bir fikrin onay sonrası doğrudan `SPRINT_PLAN.md` veya `KANBAN.md` içine kart olarak yazılması.
- **Değer / Gerekçe:** Manuel kopyala-yapıştır zahmetini kaldırır, süreci hızlandırır.
- **Ajan Değerlendirmesi:** `my-idea` skill'i §5 el sıkışma kuralı ile bağlandı; `idea_manager.py --to-card <ID> [--append]` ile otomatik kart üretimi ve ekleme özelliği devreye alındı.

### IDEA-003: Ağır Harici Fikir Yönetim Servislerine Entegrasyon
- **Durum:** ⛔ `[DROPPED - Yerel Markdown İlkesine Aykırı]`
- **Rating:** `2.0/10` (Etki: 3 | Efor: 2 | Uyum: 1)
- **Açıklama:** Jira veya harici bir SaaS platformu ile karmaşık çift yönlü senkronizasyon kurmak.
- **Değer / Gerekçe:** Harici araç entegrasyonu sağlamak.
- **Ajan Değerlendirmesi:** Repo içi salt yerel markdown felsefesiyle ve sıfır harici API bağımlılığı kuralıyla çelişir; yerel `docs/idea/myidea.md` çok daha hızlı ve taşınabilirdir.

---
