# AGENTS.md — Global Ajan Sözleşmesi

> Bu dosya **projeler arası ortaktır**. Proje adı, proje yolu, port, DB adı,
> teknoloji sürümü veya şirket/müşteri bilgisi **buraya yazılmaz.**
> Projeye özel olan tek istisna en sondaki "Proje Bazlı Ek Kurallar" bölümüdür.

---

## 0. Okuma Sırası (atlanmaz)

| # | Ne | Nerede |
|---|-----|--------|
| 1 | Oturum devri — nerede kaldık, sıradaki iş, düşülen tuzaklar | `<repo-kök>\HANDOFF.md` |
| 2 | Geliştirici profili ve kanıtlı ders kütüphanesi | `DEV_BRIEF.md` (varsa), yoksa vault `profile\` + `projects\_STANDARTLAR\decisions\` |
| 3 | Vault kararları (salt okunur) | `<vault>\CLAUDE.md`, `<vault>\profile\`, `<vault>\projects\_STANDARTLAR\decisions\` |
| 4 | Proje kararları | `<vault>\projects\<proje-slug>\` |
| 5 | Bu dizindeki kurallar | `.agent\rules\` (bkz. `trigger-rule-action.md`) |

**Okuma kanıtı:** koda geçmeden önce geçerli kararları başlıklarıyla özetle ya da
*"bu iş için geçerli bir karar bulamadım"* de. Hatırladığını yazma, uydurma.

**Öncelik:** proje kökündeki `AGENTS.md` → bu dosya → `DEV_BRIEF.md`.
Çelişmede proje kökü kazanır. Hiçbirinde olmayan bilgiyi uydurma — sor.

---

## 1. Yazma — tek hedef

| Ne zaman | Nereye |
|---|---|
| Çözdüğün kalıcı hata | `<repo-kök>\knowledge-base.md` |
| Verdiğin kalıcı karar | `<repo-kök>\knowledge-base.md` |
| Durum, sıradaki iş, tuzaklar | `<repo-kök>\HANDOFF.md` |

- ⛔ Başka hiçbir yere yazma. Bu iki dosyanın **tek ve zorunlu yeri repo köküdür.**
- ⛔ `knowledge-base.md`'yi baştan sona okuma; yalnız yaz (append). Boyutu büyüyebilir.
- ⛔ Vault'a hiçbir şey yazma. Vault salt okunur; kalıcı kararları Kütüphaneci taşır.
- ⛔ "Dosyada zaten var" dediğin kuralı ikinci kez yazma — terfi öner.

Formatlar ve "ne yazılır / ne yazılmaz" listesi:
[`.agent\rules\knowledge-base-management.md`](rules/knowledge-base-management.md)
ve [`.agent\rules\handoff-session-continuity.md`](rules/handoff-session-continuity.md).

Şablonlar (ilk kez oluşturulurken kopyalanır, sonra dosyanın kendisi güncellenir):
[`templates\HANDOFF.template.md`](templates/HANDOFF.template.md) ·
[`templates\knowledge-base.template.md`](templates/knowledge-base.template.md)

---

## 2. Her oturumun sonunda zorunlu adımlar

1. Doğrulama kapılarını çalıştır (aşağıdaki kapılar).
2. `knowledge-base.md`'ye bu adımda çözülen hataları ve verilen kararları **yaz**.
3. `HANDOFF.md`'yi güncelle: kanıt metrikleri, nerede kaldık, **sıradaki iş**,
   varsa yeni düşülen hata.
4. Kullanıcıya şeffaf rapor ver — aşağıdaki blok **zorunludur**.
5. Commit istenmedikçe `git commit` / `push` / `tag` **yapma**.

```markdown
### 📝 OTURUM DEVİR & BİLGİ TABANI GÜNCELLEMESİ (HANDOFF & KB RAPORU)
- **knowledge-base.md:** [Eklenen hata/karar başlıkları ve kısa özeti (yoksa "yeni yok")]
- **HANDOFF.md:**
  * Güncellik Kanıtı: [Ölçülen gerçek sayılar — test, assert, derleme, chunk boyutları]
  * Nerede Kaldık: [Tamamlanan adım ve durum]
  * Sıradaki İş: [Yeni oturumun başlayacağı ilk somut hedef]
  * Bu Projede Düşülen Hatalar: [Yeni ders/tuzak veya "yeni yok"]
  * Bu Projede Alınan Kararlar: [Yeni karar veya "yeni yok"]
- **Sonraki işler:** [Varsa numaralı liste — açık iş kalmadıysa "Açık iş yok — proje tamamlandı"]
- **Kullanılan MCP:** [context7 / sequential-thinking — ne için kullanıldı veya "kullanılmadı"]
- **Aktif skill'ler:** [Okunan skill adları]
```

> 💡 **Rapor Çıktı Tetikleme Politikası:** Bu blok varsayılan olarak yalnızca **görev bitiminde (commit öncesi)**
> ve **oturum kapanışında** üretilir (`[disabled, disabled, disabled, enabled, enabled]`).
> Ara kodlama ve test adımlarında token tasarrufu için basılmaz. Ayarlar ve detaylar için: `readme-help.md`.

---

## 3. Doğrulama kapıları — "bitti" demeden önce

Bu bölümdeki her kural **üç sınıftan birindedir** ve sınıfı kural dosyasının
front matter'ında `sinif:` alanıyla **yazılıdır.** Ajan hangi kuralı
doğrulayabileceğini bu alandan görür:

| Sınıf | Anlamı | Doğrulama |
|---|---|---|
| `OLCULEBILIR` | Ölçülebilir | Aşağıdaki komut çalıştırılır, exit kodu okunur |
| `TUTUM` | Ölçülemez | Ajan beyanı; `knowledge-base.md`'ye yazılır |
| `SUREC` | Akış | Skill adımları izlenir; kapı yoktur |

⛔ **"zorunlu" yazan bir kural `OLCULEBILIR` değilse, onu uyguladığını
kanıtlayamazsın — sadece beyan edersin.** Bu ayrım gizli değildir.

### 3.1 Ölçülebilir kapılar

> ⛔ Bu tablo **elle yazılmaz.** Kaynak kural dosyalarının front matter'ıdır.
> `python .agent/skills/musgoku/scripts/rules_gates.py --emit-table` ile üretilir;
> bayatlık `rules_gates.py` tarafından **hata** olarak raporlanır.

<!-- GATE-TABLE:BEGIN -->
| Yığın | Zorunlu komut | Ayrıntı |
|---|---|---|
| Backend / API dokümantasyonu | `python .agent/skills/musgoku/scripts/check_api_docs.py` | [`api-documentation-enforcement.md`](rules/api-documentation-enforcement.md) |
| Tasarım / skill sahipliği | `python .agent/skills/musgoku/scripts/check_design_skills.py` | [`design-skills-enforcement.md`](rules/design-skills-enforcement.md) |
| Frontend / bundle bütçesi | `npm run build` | [`frontend-bundle-limits.md`](rules/frontend-bundle-limits.md) |
| Frontend / i18n | `python .agent/skills/i18n-localization/scripts/i18n_checker.py` | [`i18n-enforcement.md`](rules/i18n-enforcement.md) |
| TypeScript / React | `npx tsc --noEmit` | [`no-unused-code.md`](rules/no-unused-code.md) |
| Java / Spring derleme | `mvn clean compile -DskipTests` | [`no-unused-code.md`](rules/no-unused-code.md) |
| Java / kullanılmayan kod | `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` | [`no-unused-code.md`](rules/no-unused-code.md) |
| Skill sözleşmesi / tetikleyici sözlüğü | `cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts` | [`skill-trigger-routing.md`](rules/skill-trigger-routing.md) |
| Frontend / Vite SPA | `python .agent/skills/musgoku/scripts/check_vite_spa.py` | [`vite-spa-enforcement.md`](rules/vite-spa-enforcement.md) |
<!-- GATE-TABLE:END -->

Ek kapı (tek kural dosyasına bağlı değildir):

| Kapsam | Komut |
|---|---|
| Kural setinin kendisi | `python .agent/skills/musgoku/scripts/rules_gates.py --strict` → `[OK]` |

### 3.2 Ölçülemeyen kurallar

> ⛔ Bu tablo **elle yazılmaz.** `rules_gates.py --emit-attitude` ile üretilir.

| Kural | Sınıf |
|---|---|
| `development-workflow.md` | SUREC |
| `mandatory-git-release-workflow.md` | SUREC |
| `no-unauthorized-commit.md` | SUREC |
| `trigger-rule-action.md` | SUREC |
| `always-read-skills.md` | TUTUM |
| `handoff-session-continuity.md` | TUTUM |
| `knowledge-base-management.md` | TUTUM |
| `mcp-usage-enforcement.md` | TUTUM |
| `no-silent-wait.md` | TUTUM |

⛔ **Bir şeyi doğrulamadıysan "yaptım" deme.** Test/build çalıştırılmadıysa
"çalıştırılmadı" de. Uydurma kanıt, kanıtsız başarıdan kötüdür.

⛔ **Sessizce bekleme.** ~30 saniyeyi aşan her iş için önce tek satır yaz:
ne yapıyorum, en fazla kaç dakika sürecek. Bekleme döngüsü kurma; sunucu
başlatma asenkron olsun, bekleyerek değil **kısa sağlık kontrolü** yaparak ilerle.
Ayrıntı: [`rules/no-silent-wait.md`](rules/no-silent-wait.md).

---

## 4. Skill ve kural kullanımı

- Kod yazmadan önce `.agent/skills/` altındaki ilgili skill'i oku.
- Yönlendirme: [`.agent\skills\musgoku\SKILL.md`](skills/musgoku/SKILL.md)
- Kurallar dizini tek kaynaktır: [`.agent\rules/`](rules/) — `trigger-rule-action.md` hepsini bağlar.
- Tasarım/UI taleplerinde `canvas-design` + `frontend-design` + `ui-ux-pro-max`
  birlikte okunur; hangi konunun sahibi olduğunu `design-skills-enforcement.md`
  §3 sahiplik haritasından doğrula.

---

## 5. Git kuralları

- ⛔ Kullanıcı açık onay vermeden `git commit` / `tag` / `push` **çalıştırma.**
- Onay sonrası tüm commit/release adımları `git-release-workflow` skill'iyle,
  **kesintisiz** yürütülür; her komut için ayrı onay istenmez.
- Ayrıntı: [`no-unauthorized-commit.md`](rules/no-unauthorized-commit.md),
  [`mandatory-git-release-workflow.md`](rules/mandatory-git-release-workflow.md).

---

## 6. Best practice doğrulaması (MCP)

| MCP | Ne zaman zorunlu |
|---|---|
| `context7` | Yeni paket ekliyorsan · sürüm farkı kararı · API ismi/parametresi yazıyorsan · hata mesajı docs ile ilgiliyse |
| `sequential-thinking` | 3+ adımlı plan · iki yaklaşım arasında seçim · güvenlik/yetki sınırı · belirsiz mimari karar |

Kullanmadıysan **"kullanmadım" de.** Ayrıntı ve sınır listesi:
[`mcp-usage-enforcement.md`](rules/mcp-usage-enforcement.md).

---

## 7. Tasarım kuralları

- Tasarım/UI/UX taleplerinde üç tasarım skill'i (`canvas-design`,
  `frontend-design`, `ui-ux-pro-max`) birlikte okunur ve yanıtta devrede
  oldukları belirtilir.
- Tasarım alanındaki 12 skill'in **sahiplik sınırı**
  [`rules\design-skills-enforcement.md`](rules/design-skills-enforcement.md) §3'te
  tanımlıdır. Bir konuyu iki skill sahiplenmez — çakışmada o tabloya bak.
- Generic/AI-slop çıktı kabul edilmez.
- Ayrıntı: [`design-skills-enforcement.md`](rules/design-skills-enforcement.md).

---

## 8. Frontend kuralları (yalnız frontend projesinde geçerli)

- Vite SPA / React projelerinde Next.js konseptleri kullanılmaz.
  Ayrıntı: [`vite-spa-enforcement.md`](rules/vite-spa-enforcement.md).
- Bundle ve chunk bütçesi ihlal edilmez.
  Ayrıntı: [`frontend-bundle-limits.md`](rules/frontend-bundle-limits.md).
- UI metni hardcode yazılmaz.
  Ayrıntı: [`i18n-enforcement.md`](rules/i18n-enforcement.md).

---

## 9. Güvenlik sınırı

- Tıbbi/hukuki/finansal risk doğuracak konularda veya güvenlik açığını
  kapatacak kod değişikliklerinde gerekçeyi kullanıcıya açıkça bildir.
- Şifre, token, kişisel veri asla loglanmaz, asla kaynak koda gömülmez.

---

## 10. Bu dosyaya ve kural dosyalarına kural ekleme kuralı (agent için)

⛔ **Global kurallar (bu dosyanın 0–9. bölümleri ve `.agent/rules/*.md` dosyalarının ana içeriği) en üsttedir, projeler arası ortaktır ve değiştirilmez.**

Proje için yeni veya istisnai bir kural gerekiyorsa:

1. **Önce mükerrerlik kontrolü yap:** Bu dosyada veya `.agent\rules/` altında
   aynı amaca hizmet eden bir kural varsa **kesinlikle yenisini ekleme**;
   *"zaten var, şurada"* de ve mevcut kuralı uygula.
2. **Kural dosyasının en altına ekle:** Yalnızca ilgili kural dosyasının (veya bu dosyanın)
   **en altında** yer alan `## Proje Bazlı Ek Kurallar` başlığı altına `### <Kural Başlığı>` olarak ekle.
3. **Global hiyerarşiyi bozma:** Global bölümlerin yapısını, sırasını, numaralandırmasını
   veya üslubunu asla değiştirme.

---

## Proje Bazlı Ek Kurallar

> Bu bölüm **projeye özeldir** ve `.agent/` klasörüyle birlikte projeye dağıtılır.
> Altında yalnızca bu projenin kendi gereksinimi yazılır — genel kural değil.
> Bu bölüme yazarken §10'daki mükerrerlik kontrolü zorunludur.

### Bu proje için ek kurallar

_(Aşağıdakiler yalnız **skillSetWorks** deposuna aittir. Genel kural değildir;
eklenen kural zaten kapsamı karşılıyorsa §10 gereği yazılmaz.)_

### Depo ne yapar, ne yapmaz

Bu depo **uygulama kodu içermez.** Yalnız projeler arası ortak ajan çalışma
kurallarını ve skill'leri üretir ve dağıtır. Buraya build çıktısı, uygulama
kodu, port, veritabanı adı veya proje mimarisi yazılmaz. Yazılacak tek şey ajan
kuralı, skill veya dağıtım tanımıdır.

### Tek gerçek kaynak ve dağıtım yönü

`skillSetWorks/.agent/` **tek gerçek kaynaktır.** Hedef projelerdeki `.agent/`
kopyaları türetilmiş çıktıdır. Bir kural ya da skill değişikliği:

1. **Burada** yapılır (`skillSetWorks/.agent/…`)
2. `python delivery.py --verify` ile hedeflerin eşit olduğu kanıtlanır
3. `python delivery.py` ile dağıtılır

⛔ Hedef projede `.agent/` altında yapılan değişiklik bir sonraki dağıtımda
**kaybolur** — çünkü dağıtım hedef ağacı önce siler. Bu yüzden hedef projede
`.agent/` içine elle yazma yapma; kural gerekiyorsa burada tanımla.
Hedefte korunması gereken tek şey `AGENTS.md → ## Proje Bazlı Ek Kurallar`
bölümüdür ve dağıtım onu otomatik korur.

### Değişiklik sonrası zorunlu doğrulama kapıları

```bash
# 1. Sözleşme + çekirdek test paketi (173 test)
cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest discover -p "test_*.py"

# 2. pytest paketleri (ui-styling 64 · design-system 2 · brand 21)
cd ../../ui-styling/scripts && python -m pytest tests -q
cd ../../design-system/scripts && python -m pytest tests -q
cd ../../brand/scripts && python -m pytest tests -q
```

`pytest` gerekir (`pip install pytest pytest-cov pytest-mock`). Bu kapı
koşturulmadan "bitti" deme.

⛔ Test koşumu `__pycache__`, `.pytest_cache` ve `.coverage` klasörleri
bırakır. Bunlar dağıtıma **girmez** (`delivery.py` filtreler), ama kaynak
ağacında birikirse `tree_index` sayımlarını bozar. Yeni skill eklerken
`delivery.py` → `copy_tree` → `ignore_patterns` listesini gözden geçir.

### Git

Bu depo bir git deposu **değildir** (`git status` çalışmaz). Hedef projelerde
`.agent/` izleme durumu **projeden projeye değişir ve bilinçlidir**:

- `ocai`, `FEProjectv1` → `.agent/` izleniyor
- `bookmarkManagerProject` → `.gitignore` yalnız `AGENTS.md` + `rules/` +
  `templates/` izliyor (`.agent/skills/` hariç, gerekçe `.gitignore` yorumunda)
- `kalansure` → `.agent/` **tamamen** ignore'da

⛔ **Bu depodan git komutu çalıştırılmaz ve hedef projelerde commit yapılmaz.**
Commit kararı kullanıcının, proje başına ayrı ayrı verilir. `delivery.py`
zaten hiçbir git komutu çağırmaz.

### Yeni skill ekleme sırası

1. `skillSetWorks/.agent/skills/<yeni-skill>/` altına ekle
2. `rules/skill-trigger-routing.md` §A tablosuna satır ekle (yoksa
   `test_dictionary_exists_and_lists_every_skill` kırmızıya döner)
3. `SKILL.md` `description` alanını sözleşmeye göre yaz:
   25-70 kelime · `Tetikleyiciler:` · `Tetiklenmez:` · TR + EN örnek ·
   araç/proje adı yok · sözlük atfı zorunlu
4. Yukarıdaki iki doğrulama kapısını koştur
5. `python delivery.py --dry-run` → hedefleri kontrol et
6. `python delivery.py` → dağıt
7. `delivery.md` §6 çalışma kaydını güncelle

### Ajan bulma tuzağı

Çalışma alanında bu repo dışında da `.agent/` klasörü olan
projeler bulunabilir. Bu depo yalnız `delivery.md` config'inde
listelenen yollara dağıtım yapar — diskte başka `.agent/` olması onları
kapsam dışı bırakmaz.