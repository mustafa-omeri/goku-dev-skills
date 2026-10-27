# Context Compression & Headroom Principles for AI Coding Agents

> Bu doküman, `headroomlabs-ai/headroom` mimari incelemesinden süzülen; prompt önbellek (prompt cache) verimliliğini koruyan, bağlam penceresi (context window) şişkinliğini önleyen ve kritik hata kanıtlarını kayıpsız tutan bağlam yönetimi ilkelerini tanımlar.

---

## 1. Altın Zihinsel Model: Canlı Bölge (Live Zone) vs. Sıcak Bölge (Hot Zone)

Yapay zeka asistanlarının en sık düştüğü bağlam yönetimi yanılgısı: *"Bağlam dolduğunda konuşma geçmişinden veya kurallardan parçalar silerek/özetleyerek yer açmaktır."*

Bu yaklaşım:
1. Modelin sistem promptunu ve anayasal kurallarını kaybetmesine yol açar.
2. Prompt önbellek (Prompt Cache) mekanizmasını her istekte sıfırlar (cache-busting); yanıt gecikmesini ve token maliyetini 5-10 kat artırır.

### Doğru İlke:
- **Dokunulmaz Sıcak Bölge (Cache Hot Zone):** System prompt, araç şemaları (`tool definitions`), mimari sözleşmeler ve oturum açılış bağlamı sabittir; istekler arasında dinamik olarak mutasyona uğratılmaz.
- **Canlı Sıkıştırma Bölgesi (Live Zone):** Sıkıştırma **yalnızca** en son kullanıcı mesajı içeriği ve en son araç çıktısına (`tool_result`, terminal stdout/stderr, dosya okuma çıktısı) uygulanır.

---

## 2. Dört Temel Sıkıştırma İlkesi

### A. Pre-Context Kabul Kontrolü (Admission Control)
Devasa bir terminal veya dosya çıktısını (örneğin binlerce satırlık `npm list`, ham log dökümü, 5 MB JSON verisi) doğrudan context'e basıp ardından LLM'e *"bunu özetle"* demek en pahalı ve riskli yoldur.
- **Kural:** Veri context'e girmeden önce araç düzeyinde filtrelenmelidir.
  * `cat big_file.txt` yerine `grep` veya hedef satır aralığı (`line ranges`).
  * `npm test` yerine yalnızca başarısız test odaklı filtreleme (`--testNamePattern`).
  * `git log` yerine odaklı `git log -n 5 --oneline`.

### B. Byte-Accurate Hata Koruma (Fatal Line Preservation)
Bir araç çıktısı (derleme hatası, test çıktısı, stack trace) sıkıştırılırken veya raporlanırken:
- **Asla Silinmez:** `FATAL`, `FAIL`, `Error:`, `Exception`, `at line X:Y`, dosya yolları ve exit code satırları **karakteri karakterine** korunur.
- **Elenir:** Tekrarlayan ilerleme çubukları (`[=====>] 85%`), spinner satırları, başarıyla geçen 200 adet birim testin ara onay tikleri, verbose bilgi logları.

### C. Dışsallaştırma (Externalize State)
Konuşma geçmişini hafızada tutarak context'i şişirmek yerine, kalıcı bilgi diskteki standart dosyalara yazılır ve context temizlenir:
- Kalıcı dersler ve kararlar: `knowledge-base.md`
- Oturum devri ve canlı iş durumu: `HANDOFF.md`
- Mimari kararlar: `docs/adr/`
- Ürün gereksinimleri: `PRODUCT.md` ve `GLOSSARY.md`

### D. Telegrafik & Yüksek Bilgi Yoğunluklu İletişim (Caveman + ADHD + Headroom)
- Gereksiz nezaket cümleleri, uzun tekrarlar, "Tabii ki yapıyorum" önsözleri ve son sözler kaldırılır.
- Teknik kod/diff %100 tam, açıklayıcı metin odaklı ve yoğun tutulur.
