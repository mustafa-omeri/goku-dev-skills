# GEO / AEO Alıntı Optimizasyonu ve Kaynak Gösterim Rehberi

> **Kaynak:** `nowork-studio/notfair-plugin` Cerrahi Entegrasyonu (`plans/notfair-plugin.md`)  
> **Kapsam:** Yapay Zeka Arama Motorları (ChatGPT Search, Perplexity AI, Google Gemini, Claude) için alıntı yapılabilirlik (citation readiness) ve kaynak gösterilme protokolü.

---

## 1. AI Arama Motorları Nasıl Alıntı Yapar?

Perplexity, ChatGPT Search ve Gemini gibi yanıt motorları (AEO/GEO), geleneksel 10 mavi link yerine kullanıcı sorusunu sentezleyerek dipnot veya referans linki (`[1]`, `[cite]`) üretir.

Bir içeriğin alıntı havuzuna girebilmesi için metnin şu 4 yapısal özelliği taşıması gerekir:

1. **Doğrudan Yanıt Paragrafı (Direct Answer Capsule):** Başlığın hemen altındaki ilk 40-60 kelimede konunun tanımı ve doğrudan cevabı net bir dille verilmeli; lafazanlık (preamble) yapılmamalıdır.
2. **Doğrulanabilir İddia Yoğunluğu (Factual Claim Density):** Soyut sıfatlar yerine ölçülebilir sayılar, tarihler, sürümler ve spesifik vaka verileri içermelidir.
3. **Tablo ve Yapılandırılmış Karşılaştırma (Structured Comparison):** AI modelleri Markdown tablolarını (`| Seçenek | Hız | Maliyet |`) çok yüksek güvenilirlikle alıntılar.
4. **Alıntı Çapası (Quotation Anchor):** Net tanımlar tırnak içinde veya vurgulu kutularda özetlenmelidir.

---

## 2. Alıntı Hazırlığı Kontrol Listesi (Citation Readiness Checklist)

- [ ] **H1 & H2 Soru-Cevap Uyumu:** Başlık doğrudan kullanıcının sorduğu soruyu (`X Nasıl Yapılır?`, `Y Nedir?`) yansıtıyor mu?
- [ ] **İlk Cümle Netliği:** Sayfanın ilk cümlesi sorulan kavramın tam tanımını veriyor mu?
- [ ] **Tablo / Liste Biçimi:** Temel karşılaştırmalar madde işaretli veya Markdown tablosu olarak sunulmuş mu?
- [ ] **Otorite ve Kaynak Atfı:** İddialar resmi kaynaklara, standartlara (W3C, MDN, ISO) veya ölçüm verilerine bağlanmış mı?
- [ ] **JSON-LD Schema Bütünlüğü:** Sayfada `Article`, `TechArticle` veya `FAQPage` şeması mevcut ve eksiksiz mi?
- [ ] **Bot İzinleri:** `robots.txt` dosyasında `GPTBot`, `PerplexityBot`, `ClaudeBot` ve `Google-Extended` erişimine izin verilmiş mi?

---

## 3. Örnek Kapsül Şablonu

```markdown
## [Kavram] Nedir?

**[Kavram]**, [kısa ve net 1 cümlelik resmi tanım]. [Temel işlevi ve ne işe yaradığına dair 2. cümle]. [Ölçülebilir bir avantaj veya standart metriği belirten 3. cümle].

### Temel Özellikler
| Parametre | Standart | Etki |
|---|---|---|
| ... | ... | ... |
```
