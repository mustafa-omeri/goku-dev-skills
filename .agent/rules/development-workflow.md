---
name: MuSGoKu Development Workflow
description: Her geliştirme talebinde doğru sırada skill okuma, MCP kullanımı, kalite kontrolü, devir güncellemesi ve kullanıcı onayı adımlarını tanımlar.
sinif: SUREC
---

# 🔀 MuSGoKu Geliştirme İş Akışı

---

## Adım 0 — Oturum Köprüsü

- Kod yazmadan, düzeltme yapmadan veya test koşmadan önce repo kökündeki
  `HANDOFF.md` dosyasını oku.
- Dosya yoksa veya boşsa kendin yaz.
- Ayrıntı: [handoff-session-continuity.md](./handoff-session-continuity.md)

---

## Adım 1 — Talebi analiz et ve skill seç

Genel matris ve yönlendirme:
[`.agent\skills\musgoku\SKILL.md`](../skills/musgoku/SKILL.md)

Backend için ayrıntılı matris `references\` altındaki dosyaların içindedir.

---

## Adım 2 — Best practice doğrulaması (MCP)

| Durum | MCP |
|---|---|
| Kütüphane API'si değişmiş olabilir | `context7` → `resolve-library-id` → `query-docs` |
| Karmaşık mimari karar, güvenlik sınırı | `sequential-thinking` |
| UI testi / ekran incelemesi | tarayıcı/ekran aracı (proje yapısına göre) |
| Dosya arama / proje keşfi | dosya sistemi aracı |

Tetikleyici tablosu ve sınırlar: [mcp-usage-enforcement.md](./mcp-usage-enforcement.md)

---

## Adım 3 — Geliştir

1. İlgili skill'leri oku ve kurallarına uy.
2. Kodu yaz — DRY, guard clauses, erken return, tip güvenliği.
3. Frontend projesi ise i18n anahtarlarını **her iki dil dosyasına** ekle.
4. Backend projesi ise API dokümantasyon dosyasını aynı değişiklikte güncelle.
5. Mevcut kodun akışını ve iş mantığını bozma; refactor'ı ayrı adımda yap.

---

## Adım 4 — Kalite kapıları

Kapılar `.agent\AGENTS.md` §3'ün kaynağıdır; buradaki tablo **üretilir** ve
bayatlığı `rules_gates.py` hata olarak raporlar. Kaynak: kural dosyalarının
front matter `sinif:` / `kapi:` alanları.

<!-- GATE-TABLE:BEGIN -->
| Yığın | Zorunlu komut | Ayrıntı |
|---|---|---|
| Backend / API dokümantasyonu | `python .agent/skills/musgoku/scripts/check_api_docs.py` | [`api-documentation-enforcement.md`](./api-documentation-enforcement.md) |
| Tasarım / skill sahipliği | `python .agent/skills/musgoku/scripts/check_design_skills.py` | [`design-skills-enforcement.md`](./design-skills-enforcement.md) |
| Frontend / bundle bütçesi | `npm run build` | [`frontend-bundle-limits.md`](./frontend-bundle-limits.md) |
| Frontend / i18n | `python .agent/skills/i18n-localization/scripts/i18n_checker.py` | [`i18n-enforcement.md`](./i18n-enforcement.md) |
| TypeScript / React | `npx tsc --noEmit` | [`no-unused-code.md`](./no-unused-code.md) |
| Java / Spring derleme | `mvn clean compile -DskipTests` | [`no-unused-code.md`](./no-unused-code.md) |
| Java / kullanılmayan kod | `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` | [`no-unused-code.md`](./no-unused-code.md) |
| Skill sözleşmesi / tetikleyici sözlüğü | `cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts` | [`skill-trigger-routing.md`](./skill-trigger-routing.md) |
| Frontend / Vite SPA | `python .agent/skills/musgoku/scripts/check_vite_spa.py` | [`vite-spa-enforcement.md`](./vite-spa-enforcement.md) |
<!-- GATE-TABLE:END -->

**Kapısız iki ölçüm** (ölçülebilir değil, gözle bakılır):

| Ölçüm | Sınır |
|---|---|
| Dosya boyutu | Java 300 LOC · React/TSX 200 satır |
| Kural setinin kendisi | `python .agent/skills/musgoku/scripts/rules_gates.py --strict` → `[OK]` |

Ayrıntı: [no-unused-code.md](./no-unused-code.md) ·
[AGENTS.md §3](../AGENTS.md)

---

## Adım 5 — Devir ve bilgi tabanı güncellemesi

1. `knowledge-base.md`'ye bu adımda alınan kararlar
   (`Karar / Gerekçe / Alternatifler`) ve çözülen hatalar
   (`Problem / Root Cause / Solution`) yaz.
2. `HANDOFF.md`'yi güncelle:
   §1 güncellik kanıtı · §2 nerede kaldık · §3 sıradaki iş ·
   §4 yeni ders · §5 yeni karar · §6 ortam bilgisi
3. Yanıtta `### 📝 OTURUM DEVİR & BİLGİ TABANI GÜNCELLEMESİ` bloğunu göster.
4. Açık iş kalmadıysa bunu açıkça yaz.

Ayrıntı: [knowledge-base-management.md](./knowledge-base-management.md)

---

## Adım 6 — Kullanıcı onayı

- Değişiklikleri listele.
- Commit mesajı ve tag öner.
- ⛔ Onay olmadan commit yapma.
- ✅ Onay verilirse `git-release-workflow` skill'iyle **kesintisiz** yürüt.

### Onay ne demektir, ne demek değil

**Onay sayılanlar** (uygulamaya devam et):

| Yönlendirme | Etki |
|---|---|
| "devam" · "devam edelim" · "ekliyorum" · "yapıyorum" · "güncelliyorum" · "güncellemeye bağlıyorum" | İstenen işi **tümüyle** bitir, arada sorma |
| "commit yap" · "onaylıyorum" · "evet" · "commitleyebilirsin" | Commit + tag + push aşamasına geç |

**Onay sayılmayanlar:**

| İfade | Neden |
|---|---|
| "devam et" gibi genel ifadeler, **commit** için | Uygulamaya devam ≠ commit izni. Commit ayrıca sorulur. |
| "bir de şunu düzelt" | Yeni iş tanımı; önceki işin commit iznini içermez |

### Uygulama sırasında sorma

- Uygulama adımlarında her değişiklik için ayrı onay **sorulmaz**.
- Ancak **kapsam dışına çıkılacaksa**, bir karar geri alınacaksa veya
  projede kararlaşmış bir kural çiğnenecekse **önce sor**.
- `git commit` / `tag` / `push` bu istisnadır: **her zaman ayrıca onay gerekir.**

Ayrıntı: [no-unauthorized-commit.md](./no-unauthorized-commit.md) ·
[mandatory-git-release-workflow.md](./mandatory-git-release-workflow.md)

---

## Her zaman geçerli kurallar

1. Oturum köprüsü — `HANDOFF.md` okunmadan kod yazılmaz.
2. Tasarım/UI talebi → üç tasarım skill'i birlikte okunur.
3. Frontend projesi → i18n ve bundle bütçesi kuralları atlanmaz.
4. Backend projesi → `mvn test-compile` ve API dokümantasyonu atlanmaz.
5. Mevcut kodun akışı ve iş mantığı bozulmadan revize edilir.
6. Entegrasyon testi kapatmak kural değildir; "test devre dışı bırakıldı" notunu
   `knowledge-base.md`'ye yaz ve geçici çözüm olarak işaretle.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir geliştirme akışı kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_