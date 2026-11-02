# 🔭 Scout Değerlendirme Raporu: shadcn/improve

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/shadcn/improve
- **Sahibi:** shadcn
- **Analiz Tarihi:** 2026-10-30 13:40
- **Tespit Edilen Katman:** Tooling / Agentic
- **Dosya Sayısı & Boyut:** 9 dosya (~61 KB)
- **Teknoloji Yığını:** Agent Skills Standardı (AgentSkills.io), Markdown Tabanlı Planlama Spesifikasyonları, CLI Orkestrasyonu

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
- **Felsefe (The Plan is the Product):** Reponun temel tezi, zekanın biriktiği kritik aşamayı (kod tabanını anlama, teknik borç/zafiyet tespiti, tasarım kararları ve uygulama şartnamesi çıkarma) en yetenekli/pahalı modele (örn. Pro/Sonnet) yaptırmak; ardından bu planı (`plans/*.md`) hiçbir şey uygulamadan dondurup, uygulama ve derleme aşamasını daha ucuz/hızlı alt modellere (Flash/Haiku) veya izole iş parçacıklarına devretmektir.
- **Güçlü Yönleri:**
  - **Negatif Eşleşme Kaydı (Rejection Log):** Denetim sırasında yanlış pozitifleri (örn. kurumsal proxy ortam değişkenlerini SSRF sanma) nedenleriyle birlikte kaydeder ve sonraki denetimlerde aynı hataya düşülmesini engeller.
  - **Mevcut Repo Dokümanlarını Okuma (Recon Katmanı):** ADR'ler (`docs/adr/`), PRD'ler, `DESIGN.md`, `PRODUCT.md` gibi dosyaları okuyarak bilinçli alınmış ödünleri (tradeoff) tekrar bulgu olarak listelemez.
  - **STOP Koşulları & Doğrulama Kapıları:** Plan içine kodun mevcut halini, geçilmesi zorunlu test komutlarını ve "gerçeklik beklentiyle uyuşmazsa dur" (STOP conditions) kurallarını gömer.
- **Zayıf Yönleri:**
  - Kod üretmez veya uygulamaz; tek başına bir "analiz ve spec yazma" becerisidir.
  - Bizim halihazırda sahip olduğumuz çok katmanlı kalite kapıları (5-katmanlı dikey dilim, E1-E5 gate kontrolleri, TDD kırmızı-yeşil döngüsü) yerine planın sadece markdown seviyesinde kalmasına dayanır.

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:**
  - `code-review`: Martin Fowler kod kokusu ve şartname uygunluğu ekseninde çift yönlü denetim yapar.
  - `diagnosing-bugs` & `tdd`: Kök neden analizi, kırmızı test geri bildirim döngüsü ve dikey dilim doğrulamasını halihazırda titizlikle yürütür.
  - `council`: Mimari ikilemlerde LLM konseyi ve Borda skoru ile karar verir.
  - `HANDOFF.md` & `knowledge-base.md`: Bilinen tuzakları ve kararları oturumlar arasında yaşatır.
- **Dış Repodaki Değer:**
  - `improve`'un **"STOP Koşulları" (Reality Mismatch Abort)** ve **"Reddedilen Bulgular Kütüğü" (False Positive Rejection Log)** pratikleri, alt ajanlara iş delege ederken veya kod incelemelerinde tekrarlayan uyarıları engellemek için son derece yalın ve etkilidir.
  - Görevleri doğrudan uygulamak yerine bağımsız, kendi kendine yeten bir `plans/00X-*.md` şartnamesine dönüştürme ve "ucuz yürütücü model - pahalı mimar model" ayrımını standardize etme yaklaşımı değerlidir.
- **Kesişim & Ayrışma:**
  - Mevcut yapımız zaten derin analiz, PRD entegrasyonu ve kalite kapılarına sahiptir. Bütün bir `improve` skill'ini olduğu gibi klonlamak mükerrerlik ve bağlam şişkinliği yaratır.
  - Ancak plan şablonundaki STOP koşulları ve sahte bulgu eliminasyon mekanizması cerrahi olarak çekilebilir.

## 4. Karar ve Gerekçe
**Karar: KISMEN_ALINABILIR**
- **Gerekçe:** Deponun tüm orkestrasyonunu içeri almak gereksizdir; çünkü Antigravity sistemimiz çok daha gelişmiş doğrulama kapılarına (`rules_gates.py`, katman bütünlüğü, `HANDOFF.md`) sahiptir. Ancak `shadcn/improve`'un geliştirdiği:
  1. *STOP Koşulları (Eğer kod tabanında X dosyası Y durumunda değilse dur ve kullanıcıya dön)* mantığı,
  2. *Rejection Log (Bilinçli yapılmış mimari tercihlerin tekrar hata olarak raporlanmaması)* deseni,
  mevcut `code-review`, `doc-coauthoring` ve alt-ajan delegasyon iş akışlarımızı güçlendirmek üzere kısmen devşirilmeye uygundur.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **`code-review` ve `diagnosing-bugs` Zenginleştirmesi:**
   - Kod inceleme ve hata teşhis çıktılarında "STOP Koşulları" formatı (`### STOP Koşulları: Beklenen durum sağlanmıyorsa ilerleme`) rehbere öneri olarak işlenebilir.
2. **Sahte Bulgu Eliminasyonu:**
   - `knowledge-base.md` ve `PROJECT_BRIEF.md` içerisindeki kararların, denetim ajanları tarafından "bilinçli tradeoff" olarak okunup false-positive üretmemesi ilkesi `code-review` yönergelerine belirgin bir kural olarak yansıtılabilir.
3. **Mevcut Bütünlüğün Korunması:**
   - Harici bir `npx skills add shadcn/improve` bağımlılığı yüklenmeyecek; deponun şablon ve STOP pattern'i yerel kurallarımıza zenginleştirme olarak aktarılacaktır.