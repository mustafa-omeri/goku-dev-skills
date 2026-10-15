---
name: musgoku-prd
description: Fikri adım adım sorularla ve 90 puan kalite kapısıyla uygulanabilir PRD'ye dönüştürür; kök dizinde zorunlu HANDOFF.md protokolünü kurar/günceller; kişisel veri işleyen her işte KVKK denetimi yapar. Tetikleyiciler: "şöyle bir uygulama istiyorum", "nereden başlasam", "bunu planlayalım", "spec çıkar", "kapsamı belirleyelim", "gereksinim dokümanı yaz", "handoff kur", "oturum devri", "KVKK", "gizlilik politikası", "çerez onayı", "write a prd", "define scope". Tetiklenmez: tek satırlık kod işi, PRD biçimlendirme, saf kod incelemesi. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
argument-hint: "[özellik veya proje adı — boş bırakılırsa görüşmeden aday önerilir]"
---

# musgoku-prd — Birleştirilmiş PRD ve Oturum Devir (HANDOFF) Skill'i

Bir fikri, bir geliştiricinin ya da AI ajanın **sıfır soru sorarak doğru uygulayabileceği** bir
belgeye dönüştürürsün. Belgenin kalitesi çıktının kalitesini belirler; ürünün kalitesini değil.
Bu yüzden belge kararları ve belrsizlikleri **gizlemeden** yazmakla işe yarar.

> **Felsefe:** Parlak görünen ama boş bir PRD, hiç PRD yazmamaktan kötüdür. Yazılmamış bir PRD eksik
> der; yazılmış ama uydurulmuş bir PRD ekibi yanlış yönlendirir.

---

## Temel ilke: yargı senin, genişletme benim

LLM'ler **genişletmede** güçlü, **yargılamada** güçsüzdür.

- **Genişletme** = user story yazmak, kabul kriteri türetmek, edge case listelemek, metni düzeltmek.
- **Yargı** = problemi doğru teşhis etmek, öncelik koymak, hedef sayı seçmek, kapsamdan neyi çıkarmak.

Bu yüzden:

- **Yargı bölümlerinin ilk paragrafını kullanıcı yazar** — problem, hedefler, kapsam dışı, öncelik.
- Sen o paragrafı **genişletirsin, değiştirmezsin.** Çelişki görürsen sor, kafana göre yeniden yazma.
- Modelin yazdığı hedef sayı bir **karar değil, öneridir.** Baseline'ı olmayan hedef
  (`engagement'ı %25 artır`) en sık görülen AI göstergesidir ve stakeholder ilk açılışta yakalar.

> Kullanıcının yazdığı bir başarı metriği bir **karardır**. Senin yazdığın bir başarı metriği
> **değerlendirilmesi unutulmuş bir öneridir.**

---

## 1. Soru Sorma Biçimi (Ortam Bağımsız)

Düz metinle "şunu da söyle" diye sormak yerine, ortamda **çoktan seçmeli soru
aracı** varsa onu kullan. Bu sette hangi aracın adı geçtiği yazmaz — ajan
kendi ortamının aracını belirler:

- **Arayüz varsa:** 2-4 şık sun. Önerdiğin şık ilk sırada, etiketinde
  `(Önerilen)` yazsın. Her şıkkın sonucunu/ödünleşimini açıklama alanında yaz.
  Bağımsız kararları tek çağrıda en fazla 4 soruda grupla. Açık uçlu anlatım
  ("problemi uzun anlat") için düz metin kullan.
- **Arayüz yoksa:** soruları net ve numaralı düz metin olarak sor.
- **Etkileşimsiz ortam (cron, CI, batch):** sadece burada sessiz varsayım serbest. Varsayımları
  PRD'nin §21 Varsayım Kaydı'nda tek tek listele ki sonradan teyit edilebilsin.

Genel kural: seçenek sayısı sınırlıysa seçimli sor, kullanıcının cümlesiyle anlatması gerekiyorsa
açık uçlu sor.

### Kaçış kapısı yoktur

Etkileşimli kullanıcı varken — kullanıcı **"sen varsay", "bana sorma", "sen karar ver",
"uygun gördüğünü yap"** dese bile — teknoloji seçimi, mimari yaklaşım, veri modeli, kapsam sınırı,
auth ve ödeme kararlarını tek başına verip belgeye ya da koda atlama.

"Sen varsay" talimatını **sessiz varsayma izni olarak değil**, "kararı benim önerimle yönlendir"
olarak yorumla:

- Kararı önerili seçimli soruya dönüştür.
- En güçlü seçeneği en üste koy, `(Önerilen)` ekle, gerekçesini bir cümlede yaz.
- En fazla 4 kritik kararı tek soru grubunda topla.

Hız, "hiç sormamakla" değil, "iyi bir varsayılanı en üste koyup tek tıkla onaylatmakla" sağlanır.

---

## 2. İş Akışı (7 Adım)

### Adım 0 — Sınıflandır ve ölçekle

İlk sorudan önce isteği sınıflandır ve **sınıflandırmayı kullanıcıya söyle** — çünkü kullanıcı
bunu duyup yönlendirebilir.

**Ön koşul / Oturum Köprüsü Kontrolü:** Projenin **kök dizininde** `HANDOFF.md` var mı kontrol et. Varsa, geçmiş oturumların bağlamı, tamamlanan işler ve düşülen tuzaklar doğrudan Adım 1 ve Adım 2'ye aktarılır. Kökte yoksa dosyayı kendin oluştur. Başka bir konumdaki kopyayı kaynak sayma.

| Sınıf | Belirti | Yaklaşım |
|---|---|---|
| **Sınırlı (bounded)** | Tek modül, net sınır, 1-3 gün | Kısa PRD (1-2 sayfa). Şablonun gereksiz bölümlerini atla |
| **Mimari (architectural)** | Yeni servis, şema değişikliği, birden çok modül | Tam şablon + derin modül analizi + slice önerisi |
| **Araştırma (spike)** | "Olur mu?" sorusu, belirsiz teknoloji | PRD yazma. Spike planı + karar soruları + başarı ölçütü ver |
| **Yayın (kamuya açık web)** | Landing page, kurumsal/pazarlama sitesi, portfolyo, dokümantasyon sitesi — **içeriği arayan ve kendi kararını kendi veren son kullanıcı vardır** | Kısa-orta PRD + **§20 Yayın Kontrol Listesi zorunlu, kısaltma yok** + §7 alt yüzey kuralları |

**Sınıflandırmadan sonra ikinci bir soru sor: veri ekseni.** Sınıf *ne kadar kapsamlı*
olacağını belirler; veri ekseni *hangi kapıların açılacağını* belirler. İkisi bağımsızdır —
kapsamlı bir iç araç hiçbir kişisel veri toplamıyor olabilir, küçük bir landing page beş
kişisel veri toplayabilir.

> **Veri ekseni sorusu:** "Bu iş kişisel veri **topluyor**, **saklıyor** veya **işliyor**
> mu, ya da toplayan bir sisteme dokunuyor mu?" — form, üyelik, sipariş, bülten, randevu,
> iletişim, WhatsApp, canlı destek, analitik, piksel, ödeme, dosya yükleme sayılır.

| Cevap | Sonuç |
|---|---|
| **EVET** | `references/kvkk-uyum-denetimi.md` okunur, uygulama tipi belirlenir (6 tip), **§20 Tier A-2 (KV-01..KV-06)** kapıları açılır ve **§20.1 denetim raporu** PRD'ye yazılır |
| **HAYIR** | Bu kapı kapanır; gerekçe §21'e yazılır |

**Veri ekseni `HAYIR` cevabı güvenli bir varsayımdır, teyit isteyen bir sorudur.** Projeyi
tarayıp "hiçbir yerde kişisel veri yok" dediğinde bu bir gözlemdir; kullanıcıya
sormalısın: "**Kimse adını ve e-postasını bize bırakmıyor mu — iletişim, bülten ya da
üyelik varsa bu eksen `EVET`'tir.**" Yanlış `HAYIR` cevabı, en pahalı hatadır: hiçbir yasal
sayfa yazılmaz ve site yayına girer.

> **Yayın sınıfı KVKK'yı hiçbir zaman muaf tutmaz.** Yayın sınıfında "veri ekseni `HAYIR`"
> ancak **yazılı gerekçeyle** verilebilir (ör. "salt-okunur dokümantasyon, tek yönlü veri
> girişi yok, `references/kvkk-uyum-denetimi.md` §1 tip tespitiyle doğrulandı").

**Uygulama tipi denetimi nasıl yapılır** (hangi tip hangi denetimleri zorunlu kılar) ve
KV-01..KV-06'nın her birinin yöntemi, kanıt ölçütü ve tarayıcı doğrulama adımları için:
`references/kvkk-uyum-denetimi.md`. Bu dosya **okunmadan** KVKK kapısı geçilmiş sayılmaz.

**Yayın sınıfı neden ayrı:** Diğer sınıflarda bir PRD eksikliği hatala **gecikmeli** bir maliyet
üretir. Yayın sınıfında eksik kalan madde çoğunlukla **geri dönüşü olmayan** bir maliyettir —
KVKK aydınlatma metni yoksa site yasal risk altındadır, HTTPS yoksa tarayıcı uyarı verir,
`Disallow: /` yanlış yazıldıysa site indeks dışıdır ve fark edilmez. Bu yüzden bu sınıfta
**"kısa PRD yeter" yaklaşımı geçerli değildir:** gövde 1-2 sayfada kalabilir ama §20 listesi
kısaltılamaz — kısaltmanın tek yolu `Opsiyonel` işaretlemektir, satır silmek değil.

**Uzunluk risk seviyesine göre ölçeklenir:** kişisel araç 1-2 sayfa · internal tool 5-8 sayfa ·
müşteriye açık / uyumluluk gerektiren ürün gereksinimleri kadar uzun olmalı.

Bölüm uzunluğu hak etmiyorsa **taşırma (parking lot)**: §19'a "v2 için aday" diye yaz, gövdeyi
şişirme. Kapsamı şişirip "kapsamlı görünen" belge üretmek ayıp değil — hatta hata.

### Adım 1 — Problemi dinle

Kullanıcıdan problemi uzun ve detaylı anlatmasını iste. Çözüm fikri varsa onu da sor. Bu adım açık
uçludur, düz metin sor.

Şunları geçmeden "anladım" deme: **iş değeri** (problem, kim, sıklık, kanıt, çözülmezse maliyet) ·
**kapsam** (must/should/could ve kapsam dışı + her birinin neden dışarıda olduğu) · **başarı**
(sonuç, ölçüm aracı, zaman penceresi, mevcut baseline) · **teknik** (platform, yığın, auth,
uyumluluk, performans, veri yerleşimi) · **deneyim** (ana akış, boş/hata/yükleme durumu, WCAG).

Eksikleri tek tek listeleyip geç: "Şunları netleştirmem gerekiyor: 1) ... 2) ... 3) ..." — kullanıcı
tek seferde yanıtlayabilsin.

### Adım 2 — Kod tabanını keşfet

**İlk iş:** Proje kökündeki `HANDOFF.md` varsa **önce bu dosya okunur**. Bu dosyadaki kanıtlanmış tuzaklar (ör. kabuk glob hataları, port yanılgıları, yetki/rol eşleşmeleri, sahte geçen testler) bilinmeden kod keşfine başlanamaz. Bu adım atlanırsa eski oturumun düştüğü tuzaklar tekrarlanır. Dosya yoksa süreci kendin devir al.

Varsa repoyu gez: `README`, paket dosyası (`package.json`, `pyproject.toml`, `pom.xml`,
`build.gradle`) gibi manifestleri **paralel** oku; mevcut mimari, auth yapısı, konvansiyonlar.
Kullanıcının söylediklerini **kodla doğrula** — her modül/servis/endpoint için gerçekten var
olduğunu bul. Boş proje ise bu adımı atla. Mevcut testleri de bul: bunlar "bu projede test şöyle
yazılır" ön bilgisidir.

Bulguyu 3-5 cümleyle özetle ve "Anlayışım doğru mu?" diye onayla.

**Veri ekseni `EVET` ise bu adım bir ek görev alır: kişisel veri toplayan her noktayı
envanterle.** Mimari keşfiyle aynı taramada yapılır, ayrı bir turda değil:

| Ne aranır | Neden |
|---|---|
| Form bileşenleri ve gönderim uç noktaları | Hangi alanlar toplanıyor, nereye gidiyor |
| Üyelik / giriş / profil ekranları | Hesap verisi, şifre geri dönüşü |
| Bülten, kampanya, "abone ol" | Açık rıza gerektiren tipik nokta |
| Sipariş / ödeme / adres | En yüksek hacimli kişisel veri |
| Randevu, rezervasyon, destek talebi | Zaman ve yer verisi |
| E-posta servisi, WhatsApp, canlı destek widget'ı | Kişisel verinin üçüncü tarafa çıkışı |
| Analytics / piksel / oturum kaydı / harita / video gömme | Yurt dışı aktarımı yapan sessiz noktalar |
| Hosting, CDN, ödeme, e-posta sağlayıcısı yapılandırması | Verinin **fiziksel** nerede durduğu |

Bu envanter, §20.1'in veri envanteri tablosunun **ham kaynağıdır.** Kodda bulamadığın
toplama noktalarını `Doğrulanmalı` olarak bırakma — bu adımın kendi çıktısı
`[VERIFY]` etiketleriyle işaretlenir. Tam yöntem ve alan listesi:
`references/kvkk-uyum-denetimi.md` §2 (KV-01).

**Doğrulama kuralı:** Her iddia için kaynak göster.

- Kodla doğruladıysan → `src/modules/saved-search/search.service.ts:112-140`
- Doğrulayamadıysan → `[VERIFY: "mevcut arama state'i URL param'larında tutuluyor" — doğrulanamadı]`
- Tahmininse → `[ASSUMPTION: ...]`

### Adım 2b — Belirsizliği etiketle

Kod okumadan yazılan PRD, en iyi ihtimalle güzel görünen bir kâğıttır. Kod okuyarak yazılan PRD,
ajanın ilk turda sıçramasını engeller.

| Etiket | Anlamı |
|---|---|
| `[ASSUMPTION: ...]` | Onaylanmadan çıkarım yaptın |
| `[VERIFY: ... — kaynak/sahiplik]` | İddia gerçek ama kanıtı yok; doğrulanmalı |
| `[NEEDS CLARIFICATION: ...]` | Cevaplanmadan ilerleyemezsen dur; cevaplanabiliyorsa devam et ve işaretle |
| `[CONFLICT: ...]` | İki kaynak/kullanıcı ifadesi çelişiyor — çözülene kadar işareti kalır |

**Bu dört etiket, halüsinasyonu azaltmanın mekanik yoludur.** "Uydurma" demek yetmez;
belirsizliği görünür kıl.

### Adım 3 — Kritik kararları kilitle (sessiz varsayım YOK)

Bölüm 1'deki kaçış kapısı kuralı burada uygulanır: teknoloji seçimi, mimari, veri modeli, kapsam
sınırı, auth ve ödeme kararlarını tek başına verme.

Kararlar arasındaki bağımlılıkları sırayla çöz. "Tasarım ağacının her dalını tek tek gez" — bir dalı
atladığında altındaki üç dal da belirsiz kalır.

### Adım 4 — Kalite puanı (100 puan, 90 eşik)

Sarah sistemiyle puanı hesapla, kullanıcıya tabloyla göster:

| Boyut | Puan |
|---|---|
| Business Value & Goals (problem, metrik, ROI) | /30 |
| Functional Requirements (hikaye + kriter, akış, edge case) | /25 |
| User Experience (persona, yolculuk, UI kısıtı) | /20 |
| Technical Constraints (performans, güvenlik, entegrasyon) | /15 |
| Scope & Priorities (MVP, faz planı, öncelik) | /10 |
| **Toplam** | **/100** |

**Yayın sınıfında ek kapı — puan yetmez.** Adım 0'da "Yayın" denilen PRD'de 90 puan geçse bile
§20'nin **Tier A (yasal)** ve **Tier B (yayın altyapısı)** satırları yeşil değilse PRD
"yayına hazır" ilan edilemez. Bu iki şey ölçülebilir değildir ve puan tablosu ölçülebilir olanı
puanlar: **90 puan = kalite, §20 yeşil = izin.** Biri diğerini ikame etmez.

**Veri ekseni `EVET` olan her PRD'de üçüncü kapı:** §20.1 denetim raporunda
**`Doğrulanmalı` durumunda satır kalmaz** ve Tier A-2'nin `Zorunlu` satırları yeşildir.
`Doğrulanmalı` kalmış bir KVKK raporu, hiç rapor yazılmamış gibi değerlendirilir:
"kontrol edilmedi" sonucu, kontrol edildiği anlamına gelmez. Bu kapı **puandan da
bağımsızdır** — 100 puan alan bir PRD KVKK raporu eksikse yayına hazır değildir.

- Puan < 90 ise **en düşük boyuttan başla**, 2-3 soru sor, her turda puanı güncelle.
- Puan ≥ 90 ise "Hazır, PRD üretiyorum" de ve Adım 5'e geç.

Soru örnekleri: "Başarıyı hangi sayıyla ölçeceğiz?", "Ana akışı adım adım anlatır mısın?", "[şu edge
case] olunca ne olsun?", "MVP'ye ne girer, ne girmez?", "Performans ve güvenlik beklentisi ne?"

### Adım 5 — Modülleri taslakla

İnşa edilecek veya değiştirilecek ana modülleri çıkar. İzole test edilebilen **derin modülleri**
tercih et (sade arayüz arkasında çok işlev, arayüzü nadiren değişen).

> **Derin modül**, çok sayıda işlevi sade, test edilebilen ve nadiren değişen bir arayüzün arkasına
> toplayan modüldür. Sığ modülün tersi. Derin modülün arayüzü stabil kalır, testleri izole yazılır.

Modül adı verirken arayüzü de tarif et: ne değişecek, sözleşmesi ne, neden bu sınırda.
Listeyi kullanıcıya onaylat ve **hangi modüllere test yazılacağını çoklu seçimle sor.**

İyi testin tanımı: sadece **dışa dönük davranışı** test eder, iç ayrıntıyı değil.

### Adım 6 — PRD'yi yaz ve kaydet

Aşağıdaki şablonla PRD'yi üret.

- **Kaydetme yolu:** `docs/{feature-name}-prd.md`. `docs/` yoksa `prd.md` kullan.
- **Yayın sınıfında:** §20'yi boş bırakma. Kullanıcı bir maddeyi "hallederiz" diyorsa
  `Şartlı` + gerekçe yaz; sessizce silme.
- **Önce dosyanın tam gövdesini yaz, sonra dur.** Sadece "yazıyorum" deyip durma — gerçekten
  içeriği üret.
- İstenirse GitHub issue olarak da aç (Matt zinciri: PRD → issue → implementasyon).
- **Zorunlu Devir Protokolü (HANDOFF.md):** PRD üretildikten sonra, geliştiriciye veya yeni bir kod ajanına aktarımı sağlamak için projenin kök dizininde `HANDOFF.md` oluşturulması veya mevcut `HANDOFF.md` dosyasının güncellenmesi **zorunludur**. PRD "ne yapılacağını" tanımlar; `HANDOFF.md` ise "nerede kaldık, hangi tuzaklara düşme, ilk hangi komutla başla" operasyonel oturum köprüsüdür (bkz. §5.1).
- Üretimden sonra "hangi bölüme derinleşelim, kapsam değişsin mi?" diye sor.

### Adım 6.1 — Sprint ve Dilimlenmiş Görev Planlama Protokolü (Nasıl Yapılacak? & Açık Kaynak Önceliği)

⛔ **KESİN KURAL:** PRD sonrası ister resmi bir sprint planlansın, ister işler bağımsız task veya dilimlere (slice'lara) bölünmüş olsun:
**"Ne yapılacağı" (what) listesi tek başına koda başlama izni vermez; "nasıl yapılacağı" (how) planlanmadan koda girilemez.**

Ajan geliştirmeye başlamadan önce mutlaka şu 4 aşamalı protokolü tamamlamalıdır:
1. **Detaylı Uygulama Planı ("Nasıl Yapılacak?"):** Mimari yaklaşım, etkilenecek dosyalar/bileşenler ve teknik uygulama adımları belirlenir.
2. **Kabul Kriterleri (Acceptance Criteria):** Doğrulanabilir Given/When/Then (Gherkin) senaryoları çıkarılır.
3. **3. Parti Araç ve Kütüphane Araştırması (Açık Kaynak Önceliği):**
   - Kullanılacak harici araç, kütüphane veya servisler plana detaylıca araştırılarak eklenir.
   - ⛔ **Öncelik kesinlikle açık kaynak (open-source) olmalıdır.** Tescilli/kapalı çözümler yerine geniş topluluk destekli, güvenli lisanslı (MIT, Apache 2.0 vb.) kütüphaneler tercih edilir.
4. **Kullanıcıya Sunum, Değişiklik/Review Şansı ve Açık Onay:**
   - Plan kullanıcıya sunulur. Kullanıcıya inceleme ve planda değişiklik yapma imkanı tanınır.
   - **Kullanıcıdan açık onay alınmadan koda BAŞLANAMAZ.**

---

## 3. Eskime Karşıtı Kurallar

- Satır numarası, commit hash ve yapışık kod bloğu yazma (veri modeli interface'i hariç). Hızlı eskir.
- Dosya yolları yerine **modül ve arayüz adı** yaz. `Suggested File Structure` sadece iskelet
  hedefidir, sözleşme değildir; değişmeyen dosyaları listeleme.
- Belirsiz ifade yasak: "güzel olsun", "doğru çalışsın", "hızlı tepki versin", "sezgisel olsun"
  yazma. Yerine **sayı ve akış** yaz: "tıklandıktan sonra 2 saniye içinde uygulanır".
- Tarih, sürüm ve pazar iddiası yazacaksan **kaynağını** yaz. Kaynağı olmayan sayı uydurma —
  `[VERIFY]` koy.
- **Bakılmayan PRD, PRD olmayandan kötüdür** — sahte güven verir. Onaydan sonra veri değişir,
  tasarım evrilir, kapsam kayar. Sürüm numarası ver ve canlı tut.
- **Operasyonel veri PRD'ye girmez:** sertifika son kullanma tarihi, DNS kaydı, hosting limiti,
  ücretli plan adı, geçerli fiyat listesi. Bunlar §20'nin konusudur ve aylarca eskir; §20'ye
  "kim, ne zaman kontrol edecek" biçiminde yaz, tarihi değil.

### Vague ↔ somut örnek çiftleri

| ❌ Belirsiz | ✅ Ölçülebilir |
|---|---|
| "Arama hızlı ve ilgili sonuçlar döndürsün" | "10k kayıtlık veri setinde arama 200 ms içinde döner; referans testlerinde Precision@10 ≥ %85" |
| "Arayüz modern ve kullanımı kolay olsun" | "WCAG 2.1 AA; kritik akışlarda Lighthouse erişilebilirlik skoru 100" |
| "Performans kabul edilebilir seviyede olsun" | "Liste sayfası p95 gecikmesi 400 ms'yi geçmez" |
| "Giriş güvenli olmalı" | "Kimlik doğrulama mevcut auth servisine bağlanır; yetkisiz istek 403 döner; oturum 30 dk hareketsizlikte düşer" |

> Arama "verimli" geçen her ifade **bir kategori tarifi**, gereksinim değildir. Her B2B SaaS
> ürünü için doğru olur — demektir ki ölçülemez.

---

## 4. Gherkin Kuralları (Kabul Kriterleri İçin)

Her User Story'nin kabul kriteri **iki katmanlı** yazılır: önce Gherkin senaryosu, sonra ikili
checklist. Checklist QA için kopyalanabilir; Gherkin davranışı tanımlar.

### Sözleşme

| Keyword | Ne yapar | Ne yazmaz |
|---|---|---|
| **`Given`** | Sistemi bilinen bir duruma getirir | Kullanıcı etkileşiminden bahsetmez |
| **`When`** | Tek bir olay veya eylem | Arka arkaya birden fazla eylem |
| **`Then`** | **Gözlemlenebilir** çıktı | Sistemin içine gömülü davranış (veritabanı kaydı gibi) |
| **`And` / `But`** | Aynı türden adımı tekrarlar, okunabilirlik içindir | — |

**Perde metaforu:** Perde arkasında sahne ekipmenleri hazırlar — bu `Given`. Perde açılır, oyun
başlar — bu `When`. Sahnede bir şey başka bir şeye yol açar, gözlemlenebilir değişim olur — bu
`Then`.

**`Then` kayıt kontrol edemez.** Veritabanına bakıp "kayıt oluştu" demek cazip ama yanlıştır —
bulgular kırılganlaşır. Gözlemlenebilir çıktıyı yaz.

### Kurallar (Cucumber docs güncel standardı)

1. **Yapı:** `Feature` > `Background` (ortak Given) > `Scenario` > `Given / When / Then` (+ `And` / `But`).
2. **Tek davranış:** bir senaryo **bir** davranışı test eder. Mutlu yol, edge case ve hata ayrı
   senaryodur. Bir senaryoda iki bağımsız kalite konusu sıkıştırma (ana davranış + performans +
   erişilebilirlik + güvenlik aynı senaryoda olmaz).
3. **Declarative yaz:** **ne yapıldığını yaz, nasıl yapıldığını değil.** Kötü: `When SQL'e INSERT
   atarım`. İyi: `When yeni arama kaydederim`. Selector, tablo adı, endpoint, CSS sınıfı yazma —
   UI tendansları iş kuralından çok daha çabuk değişir, bu satırlar testi bozar.
4. **Sıra sabit:** Given (başlangıç durumu) → When (eylem) → Then (gözlenen sonuç).
5. **Tekrarlı veri:** aynı akış farklı veriyle test ediliyorsa `Scenario Outline` + `Examples` tablosu
   kullan. Gerçekten birden çok değer varsa — tek değer için `Outline` kullanma.
6. **Ortak önkoşul:** tüm senaryolarda tekrar eden Given varsa `Background` altına al. Ama
   **`Background` 4 satırı geçmemeli** — aşıyorsa gereksiz `Given`'ları taşı. Karmaşık durum
   kurulumu için `Background` kullanma; kural gerçekten tüm senaryolarda ortak değilse.
7. **Tag:** filtrelenecek kümelere `@smoke`, `@mvp`, `@edge`, `@regression` gibi tag koy.
8. **Kısa ol:** senaryo ideal olarak **10 adımdan kısa**. Bir feature'da **5-20 senaryo** makul
   aralık.
9. **Durum, gezinmeden yeğdir:** *"Given kullanıcı 'Editör' rolüyle giriş yapmış"* > *"Given ana
   sayfaya gittim, giriş yaptım, dashboard'a tıkladım, ayarları açtım"*.
10. **Senaryo adı spesifik olsun:** "Ürün açıklaması eksik" iyi · "Ürün Ekle, Giriş Yap, Bakiye
    Görüntüle" kötü.
11. **Vague sonuç yazma:** "çalışır" / "başarılı olur" → nasıl çalıştığı bilindiği belirtilmeli.
12. **Negatif kriter ekle.** En çok atlanan ve en pahalı bölüm: sistem bunu **YAPMAMALI**.

**Litmus testi:** Senaryoyu al, alanında uzman olmayan birine göster ve "bu ne yapıyor, anlatabilir
misin?" diye sor. Anlatamıyorsa senaryo bozuk demektir.

**Bağımsızlık:** Her senaryo tek başına anlamlı ve çalıştırılabilir olmalı.

```gherkin
Feature: Kayıtlı aramalar
  Kullanıcı karmaşık aramaları kaydedip tek tıkla uygular.

  Background:
    Given kullanıcı giriş yapmış
    And en az bir kayıtlı arama var

  @mvp
  Scenario: Kayıtlı aramayı uygulama
    Given "Enterprise Q1" adlı kayıtlı arama var
    When kullanıcı aramaya tıklar
    Then URL parametreleri aramanın sorgu değeriyle güncellenir
    And dashboard verisi yeni parametreyle yeniden yüklenir

  @edge
  Scenario: Boş isimle kaydetme
    Given kullanıcı arama çubuğundaki "Kaydet"e basar
    When isim alanını boş bırakıp onaylar
    Then satır içi hata görünür
    And popover kapanmaz

  @edge
  Scenario: Yetkisiz kullanıcı başkasının kaydına erişir
    Given başka bir kullanıcının kayıtlı araması var
    When kullanıcı bu kaydın adresine doğrudan gider
    Then erişim reddedilir ve 403 gösterilir

  Scenario Outline: Farklı veri kümelerinde uygulama
    Given "<name>" adlı kayıtlı arama var
    When kullanıcı aramaya tıklar
    Then sonuç listesi <count> kayıt gösterir

    Examples:
      | name          | count |
      | Enterprise Q1 | 42    |
      | Churn riski   | 7     |
```

Her senaryo `US-N` kimliğine bağlanır, checklist buna atıf verir.

---

## 5. PRD Şablonu

Her PRD bu bölümleri kullanır. **Uymayan bölümü şişirme, çıkar** — ama çıkardığını §19'a yaz.

---

<prd-sablonu>

# PRD: [Özellik Adı]

| | |
|---|---|
| **Sürüm** | 1.0 |
| **Tarih** | [YYYY-MM-DD] |
| **Durum** | Taslak / Onay bekliyor / Onaylandı |
| **Sahip** | [isim] |
| **Kalite puanı** | [Adım 4 sonucu] /100 |

---

### 1. Yönetici Özeti

**Özellik / Proje Adı:** [ad]

**Problem Statement:** 2-4 cümle. Kullanıcı ve iş gözünden neden önemli.

**Proposed Solution:** 1-2 cümle, implementasyon detaysız.

**AI Build Summary:** Emir kipiyle tek paragraf. Ne inşa edilecek, stack ne, en sert kısıt ne,
MVP'de olmayanlar. Örnek: "Build a Next.js 14 + Supabase web app that lets users save and
re-apply searches. No sharing in MVP. Must support markdown export."

> Bu bloğu atlayan ajan hiçbir şey sormadan başlar. Şablonun en yüksek getirili bölümüdür.

---

### 2. Problem ve Kanıt

**Problem:** [Kullanıcının yaşadığı problem, kullanıcının gözünden.]

**Etkilenen segment:** [Kim, ne sıklıkta.]

**Kanıt:**
- [Ölçüm / log / destek kaydı / görüşme — kaynağıyla. "Kullanıcılar zorlanıyor" bir görüş,
  "Trial kullananların %38'i kurulum sihirbazını tamamlamıyor (Amplitude, Q2 2026)" bir veridir.]

**Çözülmezse:** [Fırsat maliyeti.]

---

### 3. Hedefler ve Başarı Metrikleri

**Primary Goal:** tek cümlelik en önemli **sonuç**. Çıktı değil — "onboarding sihirbazını yapmak"
değil, "ilk değere ulaşma süresini %50 düşürmek".

| Metrik | Tanım | Mevcut (baseline) | Hedef | Pencere | Ölçüm yöntemi |
|---|---|---|---|---|---|
| | | | | | [hangi araç, hangi sorgu] |

> Baseline'ı olmayan hedef yazma — `[VERIFY: baseline gerekli]` koy ve kullanıcıdan iste.
> Hedefin zaman ufku ve baseline'ı olmadan ölçülebilir değildir.

**Lagging (sonuç) metrikler:** [-retention, gelir, destek kaydı azalması]
**Leading (öncü) metrikler:** [benimseme, aktivasyon, görev tamamlama, hata oranı, süre]

**Eşik ve hedef:** [Asgari kabul eşiği + beklenti hedefi. "Yüksek benimsenme" değil, "30 gün içinde
güçlü kullanıcıların %30'u en az bir arama kaydeder."]

**Anti-goals:** başarının explicitly içermedikleri. Kapsam kaymasını önler.

> **Bu ölçümü yapmayan metrik varsa buraya yazma.** Vanity metrik koymak, hiç koymamaktan kötüdür.

---

### 4. Kapsam, Öncelik ve Kısıtlar

#### In scope (MoSCoW)

| Öncelik | Gereksinim | Gerekçe |
|---|---|---|
| **Must** | | "Bu olmasa projeyi iptal ederiz" cevabı Must'tur |
| **Should** | | Acı verir ama çözüm ayakta kalır (geçici workaround yeter) |
| **Could** | | İstenir, çıkarılırsa etki düşük — **contingency havuzu** |
| **Won't (bu sefer)** | | Kasıtlı olarak dışarıda |

> **Must %60'ı geçiyorsa kapsamı daralt.** DSDM kuralı: Must effort %60'ın üzerindeyse projenin
> başarısı ve öngörülebilirliği risk altındadır. **Hepsi Must ise hiçbiri Must değildir.**

#### Out of scope

Her satır somut bir ifade + gerekçe. "CRM yapmayacağız" değil, "Bu sürümde özel şablon oluşturma
yok; kullanıcılar hazır şablonlar arasından seçer."

**Yeni kapsam ekleme kuralı:** Her ekleme bir **kapsam çıkarma** veya **takvim uzatma** ile
gelmelidir. İncelenmeyen fikirler için §19'daki parking lot'u kullan.

#### Teknik kısıtlar

- **Platform:** web / iOS / Android
- **Auth:** mevcut sistem mi, yeni bağımlılık mi
- **Erişilebilirlik:** WCAG AA / AAA
- **Offline:** evet / hayır
- **Performans:** p95 gecikme, sayfa yükleme, eşzamanlı kullanıcı
- **Ölçek:** mevcut yükün kaç katı
- **Compliance:** veri yerleşimi, GDPR / KVKK / SOC2

**Yayın sınıfında ayrıca zorunlu kısıt blokları** *(Adım 0'da sınıf "Yayın" değilse atlanır; §20'e yaz)*:

**Hukuki sayfalar — hangi metin, hangi kanun, kimi koruyor:**

| Yükümlülük | Kapsam | Kanun dayanağı | Kim onaylar |
|---|---|---|---|
| Aydınlatma metni (gizlilik) | Hangi veri, hangi amaçla, ne kadar süre, yurt dışı aktarım var mı, açık rıza | KVKK 6698 m.10 | Hukuk |
| Çerez onayı | Analytics/piksel/oturum çerezi varsa kabul-redd ayrımı + tercih yönetimi | KVKK 6698 m.5 (aydınlatma) + onay | Hukuk |
| Kullanım şartları | Hizmet sözleşmesi; ücretli üründe cayma hakkı | TKHK / mesafeli sözleşmeler | Hukuk |

> **Politika sayfası tek başına aydınlatma metni değildir.** Genel bir "gizlilik politikamız"
> sayfası, hangi veriyi hangi amaçla işlediğini söylemiyorsa yükümlülüğü karşılamaz. PRD'de
> sayfa adını değil, **o sayfada hangi bilginin yer alacağını** yaz.

**Teknik indeks ve tarama (SEO):**
- `Canonical` politikası — birden fazla URL aynı içeriği gösteriyorsa tek adres
- `sitemap.xml` — hangi URL'ler dahil/hariç, Search Console'da doğrulandı mı
- `robots.txt` — ne engellendi; **`Disallow: /` yanlışlıkla yazılırsa site indeks dışı kalır**
- Yönlendirme kuralları — `http→https`, `www↟non-www`, slug değişiklikleri (301)
- **Var olmayan URL gerçek `404` döner** — `200` dönen "yok" sayfaları soft-404 olarak
  indekslenir ve SEO sinyali zehirlenir
- Yapılandırılmış veri (JSON-LD): `Organization` / `LocalBusiness` / `Service` / `FAQPage`
- AI tarayıcı kuralları — `GPTBot` (eğitim) ile `OAI-SearchBot` (arama), `ClaudeBot` /
  `Claude-SearchBot`, `Google-Extended` **ayrı user-agent'lardır**; hepsini tek blok halinde
  engellemek siteyi cevap motorlarından da çıkarır

**Ölçümleme (analytics):**
- Hangi araç (GA4, başka) · hangi olaylar (`page_view`, form gönderimi, CTA tıklaması)
- **Çerez onayıyla ilişkisi** — analytics, onay öncesinde yükleniyorsa YL-02 ile çelişir
- Karar veri noktası: hangi karar hangi rapora bağlanacak (rapor yoksa ölçüm de yoktur)

**Altyapı ve işletim:**
- Domain sahipliği · SSL/HTTPS · yedekleme kapsamı (kod + içerik + veri) · hata ve uptime
  izleme · yenileme sorumluluğu

**Performans (yayın sınıfında sayı zorunlu):**
- Core Web Vitals — LCP ≤ 2.5 sn, INP ≤ 200 ms, CLS ≤ 0.1, **75. persentilde** ve **mobilde**
  ölçülür (masaüstü lab sonucu geçmez)
- Görsel boyutu/formatı (WebP/AVIF, lazy loading) · üçüncü taraf betik yükü · font yükleme

**Uyumluluk (brownfield projeler için ayrı ve en kritik):**
- Mevcut API sözleşmesi bozulmadan kalır mı?
- Mevcut veri şemasıyla geriye uyumlu mu, yoksa migration mı gerekiyor?
- Mevcut UI/UX tutarlılığı korunuyor mu?
- Mevcut performans karakteristiği korunuyor mu (örn. "bellek kullanımı %20'yi geçmemeli")?

---

### 5. Jobs to Be Done (JTBD)

Format: **"When [durum], I want to [motivasyon], so I can [beklenen sonuç]."** En fazla 2-5 iş,
sıklık ve öneme göre sıralı.

| # | Job statement | Öncelik |
|---|---|---|
| J1 | | 1 |

> Job ifadeleri ekran tasarımından önce gelir — "bu özellik neden var?" sorusunu API'ye dokunmadan
> cevaplar. User story'ler bu referansa bağlanır.

---

### 6. Kullanıcı Hikâyeleri

JTBD'ye bağlı tablo. Uzun ve kapsamlı liste.

| ID | Rol | İstiyorum | Böylece | JTBD | Öncelik | Bağımsız test |
|---|---|---|---|---|---|---|
| US1 | | | | J1 | P0 | [tek başına test edilebilir mi?] |
| US2 | | | | J2 | P1 | |

> **Bağımsız test:** US1'i tek başına yapsan bile değer üreten bir yürürlükte olur mu? Olmazsa
> story'leri birbirine bağımlı hâle getirmişsindir — böl veya birleştir.

#### US-N — [Başlık]

**Oyuncu:** [spesifik rol — "kurumsal yönetici", "user" değil]
**İstiyorum:** [ihtiyaç, arayüz aracı değil]
**Böylece:** [kullanıcıya kazandırdığı]

**INVEST kontrolü:**
- [ ] **I**ndependent — diğerlerine bağımlı değil
- [ ] **N**egotiable — gereksinimin özü var, çözüm yolu esnek
- [ ] **V**alued — müşteri için değerli (sadece ekip için değil)
- [ ] **E**stimable — kaba tahmin için yeterince anlaşılır
- [ ] **S**mall — birkaç kişi-haftası
- [ ] **T**estable — kabul kriteri yazılabilir

**Bu hikâyede olması gerekenler:**
- Ana akış (mutlu yol) · Boş durum (veri yokken) · Hata durumu (işlem başarısız)
- Kenar durumları (sınır değerler, eşzamanlılık, sıfır kayıt)
- **Olması gerekenler:** [sistemin YAPMAMASI gerekenler]

**Yaygın hikâye hataları:**
- *Çok belirsiz:* "Ürün daha hızlı olsun."
- *Çözüm dayatıyor:* "Bir açılır listeye ihtiyacım var" — ihtiyacı yaz, aracı §7'ye.
- *Faydası yok:* "Yönetici olarak rapor görmek istiyorum." — hangi kararı bu raporla vereceksin?
- *Çok büyük:* "Tüm ürünü yönetebilmek istiyorum." — bu story değil, bir program.
- *Ekip içi:* "Mühendis olarak veritabanını yeniden yapılandırmak istiyorum." — bu görev, story değil.

---

### 7. Deneyim ve Durumlar

*UI ağırlıklı işlerde zorunlu; API/veri ağırlıklı işlerde atlanabilir.*

**Design Direction:** [Kullanım nasıl hissettiriyor? Hangi mental model?]

**Key Screens / States:**
- **[Ekran]:** [ne yapar]
- **Empty state:** [veri yokken kullanıcı ne görür]
- **Loading state:** [skeleton / spinner / aşamalı açılış]
- **Error state (yükleme):** [ne görünür, ne yapılabilir]
- **Error state (kayıt/işlem):** [ne görünür, form kapanır mı kalır mı]
- **Validation error:** [nerede, hangi mesajla]

**Interaction Model:**
1. [adımlar]
- [Geri al / geri al-yinele davranışı] · [Klavye kısayolları]

**Accessibility Notes:**
- [Klavye gezinmesi, odak tuzakları (focus trap), iptalde odak geri dönüşü]
- [Ekran okuyucu: aria-label, aria-expanded, canlı bölge]
- [Renk kontrastı oranı]

**Figma / Design Link:** [placeholder — tasarım bitince link. Bitmediyse `[VERIFY]`]

**Yayın alt yüzeyi** *(Adım 0'da sınıf "Yayın" ise zorunlu, §20 ile eşleşir)*:

| Yüzey | PRD'de yazılması gereken |
|---|---|
| **Mobil görünüm** | 360-414 px genişlikte hangi ekranlar kırılıyor, hangi akış mobilde var/yok, yatay kaydırma var mı |
| **Birincil CTA** | Sayfa başına **tek bir** birincil eylem; nerede görünür (ilk ekran mı, kaydırma sonrası mı), metni ne, nereye götürür |
| **Form davranışı** | Alan sayısı ve hepsi gerekli mi · gönderim sonrası ne görünür · hata mesajı hangi alanda · çift gönderim kilidi · spam/KVKK onayı · doğrulama kodu |
| **Görseller** | Hangi görsel alt metinli, hangisi dekoratif (`alt=""`); sonuç sayfası dışında anlamsız `alt` yazma |
| **Hata yüzeyleri** | 404 sayfası ne gösterir, ana sayfaya bağlantısı var mı · 500 · bağlantı kesildiğinde form verisi kayboluyor mu |
| **Paylaşım kartı** | Open Graph + Twitter Card meta'ları; görsel 1200×630, başlık ve açıklama sayfayla aynı |
| **Site kimliği** | Favicon, `apple-touch-icon`, PWA manifest, `<html lang>` |

> **Birincil CTA kuralı:** Sayfa başına iki eşit ağırlıklı buton varsa hiçbiri seçilmez.
> Birincil eylem tek olmalı; ikincil eylem görsel olarak ikincil olmalı. Aynı sayfada
> "Bize Ulaşın" ve "Ürünü İncele" aynı ağırlıktaysa bu bir belirsizliktir — §2 Adım 3'e
> `[NEEDS CLARIFICATION]` olarak yaz.]

---

### 8. Component Inventory

`Component | Type | Description | Linked Stories` — v0, Lovable gibi AI component araçları
doğrudan kullanabilsin.

| Component | Type (Form/Layout/Action/Display/Navigation/Modal) | Description | Linked Stories |
|---|---|---|---|
| | | | US1, US2 |

Her anlamlı parçayı listele: form, kart, modal, boş durum, buton, navigasyon, veri tablosu.

---

### 9. Data Models

TypeScript interface ile şekil. Açık olmayan alana yorum satırı. TS yoksa JSON Schema veya düz
alan listesi.

```typescript
interface SavedSearch {
  id: string;            // UUID
  userId: string;        // FK, RLS ile korunur
  name: string;          // max 100 karakter, kullanıcı başına unique
  queryParams: string;   // serialize URL params
  createdAt: string;     // ISO8601
  lastUsedAt: string;    // ISO8601
}
```

Her alan için tek satır kural tablosu:

| Alan | Tip | Zorunlu | Kural | Örnek |
|---|---|---|---|---|

`[VERIFY: benzersizlik kısıtı — aynı kullanıcı için ad tekrar edebilir mi?]`

**Şema değişiklikleri:** [hangi tablolar, hangi kolonlar, hangi index'ler, migration gerekli mi]

---

### 10. API / Integration Surface

| Method | Path | Description | Auth Required | Error | Response Shape |
|---|---|---|---|---|---|
| | | | | | |

BaaS varsa (Supabase, Firebase) REST endpoint yerine tablo operasyonu yaz.

**External integrations:** [hangi servis, hangi SDK, hangi sınır — rate limit, timeout, retry]

**Hata sözleşmesi:** [hangi hata kodları, kullanıcıya hangi mesaj, hangi kısımda retry]

**Kırılma (breaking change) riski:** [var mı, kimi etkiler, geçiş planı]

---

### 11. State Management Map

`State | Location | Persistence | Notes` — AI araçlarının hangi state'in nerede yaşadığını ve
**neden** orada yaşadığını bilmesi için.

| State | Location (Server/Local/URL/Auth/Cache) | Persistence | Notes |
|---|---|---|---|

---

### 12. Tech Stack Recommendation

Önce kullanıcıya sor, yoksa öner. `Layer | Choice | Rationale`.

| Layer | Choice | Rationale |
|---|---|---|

> **Anti-hallüsinasyon:** Yeni bir teknoloji öneriyorsan güncel bir kaynak bağlantısı ekle. Doğrulanamıyorsa
> "doğrulanmalı" işaretle. Ürünün kendi verisine bağlı olmayan genel bir AI çıktısı, elle yazılmış
> bir PRD'den kötüdür — üründen gelmeyen veriye sahte güven yaratır.

**Suggested File Structure:** ASCII ağaç, sadece değişen dosyalar. İskelet hedefidir, sözleşme değildir.

---

### 13. Fonksiyonel Gereksinimler (EARS + RFC 2119)

User story'leri burada **tekil, numaralı, test edilebilir** ifadelere indir. Bu, PRD'nin en
önemli bölümüdür.

**Normatif dil:** `MUST/SHALL`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY` kelimeleri
[RFC 2119 / BCP 14](https://www.rfc-editor.org/rfc/rfc2119) anlamında kullanılır — **yalnız büyük
harfle**. Küçük harfle yazarsan normal İngilizce anlamını taşır. Bu kelimeleri seyrek kullan:
gereksinimi sadece geriye dönük uyumluluk veya zarar önleme gerektiğinde gerektir.

#### EARS kalıpları

Her gereksinim **tek cümle**, **tek sistem adı**, **tek yanıt** içerir.

| Kalıp | Kalıp ifadesi | Ne zaman |
|---|---|---|
| **Ubiquitous** | `Sistem, <yanıt> yapmalıdır.` | Her zaman doğru olan |
| **Event-driven** | `<tetikleyici> olduğunda, Sistem <yanıt> yapmalıdır.` | Bir eylem sonucu |
| **State-driven** | `<durum> sürerken, Sistem <yanıt> yapmalıdır.` | Bir durum boyunca |
| **Optional feature** | `<özellik> mevcutsa, Sistem <yanıt> yapmalıdır.` | Feature flag / plan bazlı |
| **Unwanted behaviour** | `<istenmeyen durum> oluşursa, Sistem <yanıt> yapmalıdır.` | Hata, istisna, çakışma |

Karmaşık kalıpta ön koşullar ve tetikleyicilerin **tümü `shall`'den önce** gelir.

> ⚠️ **EARS'ın çözdüğü sorun:** Bir `When` ifadesinin yanında `If-Then` gereksinimi bulamıyorsan
> büyük ihtimalle boşluk var. Yazılım başarıldığından çok daha fazla şekilde başarısız olur.

**Katman disiplini:** "`Sistem Redis cache kullanmalıdır`" bir gereksinim değil, bir tasarım kararının
gereksinim kılığına girmiş halidir — ve ajanın daha iyisini önermesini engeller. Kullanıcının
gözlemlediğini yaz ("önbelleklenmiş sorgularda 300 ms altında sonuç dönmeli"), mekanizmayı tasarıma
bırak.

#### Gereksinim listesi

| ID | Gereksinim (EARS) | Story | Öncelik | Kabul kriteri |
|---|---|---|---|---|
| FR-001 | Sistem, oturum açmış kullanıcı sorgusunu kaydettiğinde, ad alanının kullanıcı bazında benzersiz olduğunu doğrulamalıdır. | US1 | P0 | AC-01, AC-04 |
| FR-002 | | | | |

**Yayın sınıfında indeks ve uyum gereksinimleri de EARS ile yazılır** — bunlar ayrı bir
"teknik ek" bölümüne gömülmez. Kapsam örnekleri:

| Gereksinim | EARS |
|---|---|
| Hız | `İstenen sayfa, mobil bağlantıda 75. persentilde LCP 2.5 saniyeyi, INP 200 milisaniyeyi ve CLS 0.1'i geçmemelidir.` (unwanted behaviour kalıbı) |
| Soft-404 | `İstenen kayıt bulunamadığında, Sistem 200 durum kodu döndürmemeli; 404 döndürmelidir.` |
| HTTPS | `Sayfa isteği düz HTTP üzerinden geldiğinde, Sistem isteği HTTPS adresine 301 ile yönlendirmelidir.` |
| Çerez onayı | `Analytics yüklenmeden önce kullanıcı çerez tercihini vermediyse, Sistem analiz betiğini yüklememelidir.` |
| Yanlışlıkla indeks | `Staging ortamına gelen istekte, Sistem tarama için `200` döndürmemeli; `noindex` döndürmelidir.` |

> Bu gereksinimlerin her biri §20'de karşılık gelen bir `YL-NN` satırına bağlanır:
> `FR-007 → YL-10`. Bağlanmayan gereksinim gereksizdir; bağlanmayan kontrol satırı eksik
> kapsamdır. **İki yönlü olmalıdır.**

---

### 14. Kabul Kriterleri (Gherkin + Checklist)

Her kabul kriteri **ikili (geç/kal)** olmalı. Her madde geç/kal olarak test edilebilmeli. **Her
hikaye için önce Gherkin senaryosu, sonra ikili checklist.** "Doğru çalışır" yasak — "auth yokken
401 döner" gibi net yaz. Mutlu yol + edge case + error state + **olmaması gerekenler** ayrı maddeler.

#### US1 — [Başlık] (JTBD: J1)

**Mutlu yol**
```gherkin
Scenario: [spesifik, davranışı anlatan ad]
  Given [anlamlı başlangıç durumu]
  When  [tek eylem]
  Then  [gözlemlenebilir sonuç]
```

**Hata / kenar durumu**
```gherkin
Scenario: [spesifik ad]
  Given [durum]
  When  [eylem]
  Then  [hata davranışı — ne görünür, veri değişir mi]
```

**Negatif kriter**
```gherkin
Scenario: [ne YAPILMAMASI gerektiği]
  Given [durum]
  When  [eylem]
  Then  [sistem bunu YAPMAZ — açıkça belirt]
```

- [ ] [ölçülebilir kriter 1]
- [ ] [ölçülebilir kriter 2]
- [ ] [edge case: ...]
- [ ] [error state: ...]
- [ ] [olması gerekenler: sistem ... YAPMAZ]

> **Negatif kriterleri atlama.** "Olmaması gerekenler" en pahalı atlanan bölümdür: yetkisiz
> erişim engellendi mi, silinen kayıt geri geliyor mu, iki kullanıcı aynı anda kaydedince ne oluyor?

---

### 15. Test Kararları

**İyi testin tanımı:** sadece **dışa dönük davranışı** test eder, iç ayrıntıyı değil.

- **Hangi modüller** test edilecek (Adım 5'te kullanıcıyla seçildi)
- **Bu projede benzer testler** nerede, hangi düzende — dosya yolu ver
- **Sınır ve kenar değerleri:** [boş, tek, çok, maksimum, negatif]
- **Eşzamanlılık:** [aynı anda iki istek gelirse]
- **Test verisi:** [fixture/seed stratejisi, kimlik verisi]

**Kapsam dışı bırakılanlar:** [hangi davranış test edilmeyecek ve neden]. Test edilmeyecek şeyi
yazmak, neden yazmaktan daha güçlüdür.

---

### 16. Davranışsal Kısıtlar

*Bu bölüm hiçbir standart şablonda yok, ama sistemi en çok koruyan bölümdür.*

**Sistemin asla YAPMAMASI gerekenler** — kullanıcı ne isterse istensin:

- [sınır, davranış ne olmalı]

> "Hallüsinasyon yapmamalı" işe yaramaz; mühendise verilen belirsiz talimat, modele verilen belirsiz
> prompt'tan aynı sonucu doğurur: **güvenli görünen gürültü.** Şöyle de yaz: *"Getirilen bağlamda
> bulunmayan bir kaynağı asla alıntılamamalı."*

**Yapay zekâ / olasılıksal davranış içeren bir özellikte ek olarak:**

- **Değerlendirme stratejisi:** [başarı nasıl ölçülür? LLM-as-judge? İnsan incelemesi? Kaç örnek?]
  - *"Kıdemli PM her sprint 15 rastgele çıktı inceler; 2'den fazlası kalite çizgisini geçmezse özellik
    prompt iterasyonuna geri döner."* — Bu cümle test edilebilir bir sözleşmedir. *"Doğru ve öz olmalı"* değildir.
- **Güvenlik sayıları:** [halüsinasyon oranı < %3, kapsam puanı > %85 gibi]
- **Başarısızlık modları:** [gerçek çıktılar incelenerek yazılır, tahminle değil]
- **Güvenli reddetme:** [hangi girdide ne söyler]
- **Belirsizlik işaretleme:** [hangi durumda emin olmadığını belirtir]
- **Geri düşme davranışı:** [model yanlışladığında: başarısız mı, uyarı mı, insana mı eskalasyon?]

> **Başarısız modları tahminle yazma.** En iyi başarısız modları, prototip çıktıları incelenerek
> bulunur. PM ~100 gerçek etkileşimi izleyip açık notlar tutar, sonra 20-50 çıktıyı inceleyip
> kategorilere ayırır. **Sıra şudur: önce sistemin başarısını gör, sonra sözleşmeyi yaz.**

---

### 17. Riskler, Açık Sorular

#### Riskler

| Risk | Olasılık | Etki | Mitigasyon |
|---|---|---|---|
| | High/Med/Low | High/Med/Low | |

#### Açık sorular

| Soru | Engelleyici mi? | Sahip (PM/Eng/Design) | Hedef tarih |
|---|---|---|---|
| | Evet / Hayır | | |

Engelleyici olanı tek tek çöz. Engelleyici olmayanı "sahibi + yeniden bakma koşulu" ile ertele.

#### Verilen ödünler (tradeoff)

- [Ne verildi, neden, karşılığında ne alındı]

---

### 18. Kavram Sözlüğü

Görüşmede "müşteri", "hesap", "üye", "abone" dendi mi? "İptal" sipariş iptali mi, abonelik
sonlandırma mı? Terimleri tek tabloda sabitle; aksi halde belge sessizce iki kavramı birleştirir.

| Terim | Tanım | Diğer adlar | ID |
|---|---|---|---|

---

### 19. Yayın Planı ve Sonraki Adımlar

**MVP kapsamı:** [En küçük, değer üreten çalışan sürüm. Includes / Excludes.]

**Phase 2+ (parking lot):** [Fikirleri buraya yaz — gövdeye değil. Gövdeye girerse kapsam genişler.]

**Sign-off:** [ ] PM · [ ] Mühendislik lideri · [ ] Tasarım · [ ] Uyumluluk/Hukuk

**Next steps:** [işlem] — *Sahibi: [isim], Tarih: [tarih]*

**Slice önerisi (vertical slice):** PRD'yi iş takip sistemine bölerken katman katman değil
**uçtan uca ince dilimler** olarak böl: her dilim şema → API → UI → test katmanlarının hepsinden
geçsin ve tek başına gösterilebilir olsun. Birincisi en basit uçtan uca yol ("hello world" tracer
bullet), sonrakiler genişlik eklesin. Dilimler `US-N` referansı taşısın — böylece PRD'den koda
izlenebilirlik kurulur.

**Handoff ve Oturum Devir Protokolü:** PRD tamamlandıktan ve onaylandıktan sonra, kod geliştirme aşamasına başlamadan önce kök dizindeki `HANDOFF.md` güncellenir. Yeni gelen ajan veya geliştirici, ilk iş bu dosyayı okur (özellikle §0 tuzaklar ve §3 ilk komutlar).

**Teknik ödeme:** ajandan ne zaman teklif isteyebilirsin: `[NEEDS CLARIFICATION]` işaretli hiçbir
madde kalmadığında ve her `AC` ikili test edilebilir olduğunda.

---

### 20. Yayın Kontrol Listesi (Public Launch Gate)

*§2 Adım 0 sınıflandırmasında **"Yayın (kamuya açık web)"** denilen her PRD'de **zorunludur.** İç araç,
kütüphane veya backend PRD'sinde atlanır — atlandığını §21'e yaz.*

Bu bölüm §4'teki teknik kısıtların, §7'deki yüzey kurallarının ve §13'teki ölçülebilir
gereksinimlerin **yayın öncesi hâli**dir. Tekrar değildir: görev listesidir, gereksinim
tanımı değil.

**Nasıl kullanılır:** Her satır ya `[x]` yeşil ya `[ ]` kırmızıdır — **belirsiz bırakılmaz.**
Dört sütun zorunludur:

- **Kanıt / hedef** — sayı veya gözlenebilir durum. "İyi görünecek" yazılmaz.
- **Sahibi** — tek bir kişi. Sorumsuz satır yoktur.
- **Uyg.** — `Zorunlu` · `Şartlı` · `Opsiyonel`. `Şartlı`nın şartı parantez içinde yazılır.
- **Tarih** — kapanış tarihi (gün değil, tarih).

> **Bu bölüm puanlamaya girmez** (bkz. §6). Puan kaliteyi ölçer, bu liste **yayına izin** verir.
> 90 puan almak bu listeyi **tetiklemez**; yalnız listeyi doldurmak da yayın için yeterli
> değildir — ikisi birlikte gerekir.
>
> **Satır silme.** Bir madde senin için önemsiz görünüyorsa `Opsiyonel` yaz ve gerekçesini
> tek cümlede ver. Silinen madde, sonradan hatırlanmayan ve sorulmayan risktir.

#### Tier A — Yasal zorunluluk *(yayın engelleyici)*

| ID | Kontrol | Kanıt / hedef | Uyg. |
|---|---|---|---|
| YL-01 | **Gizlilik politikası + aydınlatma metni** — politika sayfası tek başına yetmez: veri sorumlusu, işlenen veriler, amaçlar, saklama süresi, yurt dışı aktarım, açık rıza, haklar | Yayınlanmış sayfa + hukuk onayı (KVKK 6698 m.10) | Zorunlu |
| YL-02 | **Çerez onayı** — kabul/red ayrımı, tercih yönetimi, çerez politikası metni | Onaylanmış **ve** reddedilmiş iki akışın kaydı (KVKK m.5) | Şartlı *(pazarlama/analytics/piksel/oturum çerezi varsa)* |
| YL-03 | **Kullanım şartları** — hizmet sözleşmesi; ücretli üründe cayma hakkı | Yayınlanmış sayfa | Zorunlu |

#### Tier A-2 — KVKK derin denetim *(veri ekseni `EVET` ise zorunlu)*

*Tier A "sayfa var mı" diye sorar; bu tier "sayfa doğru mu, gerçekten ne oluyor mu"
diye sorar. YL-01/YL-02 yeşil olsa bile bu satırlar kırmızıysa yayın engeli vardır.*

| ID | Kontrol | Kanıt / hedef | Uyg. |
|---|---|---|---|
| KV-01 | **Veri envanteri** — kişisel veri toplayan her nokta, hangi alan, nereye gidiyor, hukuki sebep, saklama süresi, aktarım | §20.1 veri envanteri tablosu dolu; her satırda dosya:satır | Zorunlu |
| KV-02 | **Dış servisler** — analytics, tag manager, piksel, oturum kaydı, harita, video, harici font, destek, ödeme, e-posta, hosting: hangi veri gidiyor, **yurt dışı mı** | Her servis için veri + ülke + amaç; kullanılmayanlar "veri gönderilmiyor" diye yazılmış | Zorunlu |
| KV-03 | **Aydınlatma metni ↔ site karşılaştırması** — **iki yönlü**: metinde olup sitede olmayanlar, sitede olup metinde olmayanlar; md.10 başlıkları ve md.11 haklarının tamamı | Fark listesi boş; her hakkın uygulamada karşılığı (ör. silme endpoint'i) | Zorunlu |
| KV-04 | **Onay kutuları** — aydınlatma ile açık rıza ayrı; cevap vermek rızaya bağlı değil; pazarlama izni ayrı, isteğe bağlı ve **önceden işaretli değil**; rıza kanıtı saklanıyor | Kutuların görüntüsü + onayın nerede kaydedildiği (metin sürümü, tarih) | Zorunlu |
| KV-05 | **Çerez onayı gerçekten engelliyor mu** — reddedince analytics/pixel isteği **gitmiyor**; karar kalıcı; kabul ve red eşit görünürlükte | Red sonrası boş Network paneli + kayıtlı karar; iki akışın da kaydı | Zorunlu *(izleme/reklam varsa)* · Opsiyonel *(yalnız zorunlu çerez varsa, gerekçeyle)* |
| KV-06 | **Güvenlik** — loglarda düz metin kişisel veri yok; hız sınırı + captcha/honeypot; gömülü gizli anahtar yok; kişisel veri dönüren uç noktada yetki kontrolü var | Log örneği + uç nokta isteği (oturumsuz tekrar) + anahtar taraması | Zorunlu |

**Bu tablo tek başına geçilmez.** Her satırın yöntemi, kanıt ölçütü, tuzakları ve
tarayıcıda nasıl doğrulanacağı `references/kvkk-uyum-denetimi.md` dosyasındadır; KV-01'in
hangi uygulama tiplerinde `Zorunlu`, hangisinde `Şartlı` olduğu da oradaki **6 tip
matrisiyle** belirlenir. Matris okunmadan `Uyg.` sütunu doldurulmaz.

**Matristeki `Şartlı` ve `Opsiyonel` değerleri gerekçeyle yazılır.** "Analytics yok" demek
`Opsiyonel` demektir — ancak bu, o satırın **kapandığı** anlamına gelir; kontrol edilmemiş
anlamına gelmez.

#### Tier B — Yayın altyapısı *(yayın engelleyici)*

| ID | Kontrol | Kanıt / hedef | Uyg. |
|---|---|---|---|
| YL-04 | **HTTPS zorunlu** + `http → https` **301** | `curl -I` ile 301 doğrulaması, geçersiz sertifika yok | Zorunlu |
| YL-05 | **Tek host adı** — `www` ve non-www'dan biri 301 ile diğerine gider | Diğer adresin tek yönlü 301 vermesi (çift içerik yok) | Zorunlu |
| YL-06 | **Eski URL'ler için 301** — slug değişikliği, taşınmış sayfa, eski kampanya | Eski her URL'nin güncel hedefe 301 vermesi; 302/307 değil | Şartlı *(eski yayın/URL varsa)* |
| YL-07 | **Var olmayan URL gerçek `404`** döner | Rastgele bir URL `200` değil `404` veriyor (soft-404 yok) | Zorunlu |
| YL-08 | **Yanlışlıkla indeks dışı kalmış sayfa yok** — staging/preview erişilebilir değil, `Disallow: /` yazılmamış, `noindex` kalmamış | `site:` ve URL Inspection ile doğrulama | Zorunlu |

#### Tier C — Trafik ve dönüşüm

| ID | Kontrol | Kanıt / hedef | Uyg. |
|---|---|---|---|
| YL-09 | **Mobil görünüm** — 360/414 px'te yatay kaydırma yok, CTA görünür, form doldurulabiliyor | Cihaz emülasyonu + gerçek cihaz kaydı | Zorunlu |
| YL-10 | **Core Web Vitals** — LCP ≤ 2.5 sn · INP ≤ 200 ms · CLS ≤ 0.1, **75. persentil, mobil** | CrUX veya RUM; masaüstü Lighthouse tek başına yeterli **değil** | Zorunlu |
| YL-11 | **Görsel optimizasyonu** — WebP/AVIF, boyut sınırı, lazy loading, `width`/`height` (CLS kaynağı) | Ana görsellerde format + ölçü kaydı | Zorunlu |
| YL-12 | **Net bir CTA** — sayfa başına tek birincil eylem, ilk ekrandan görünür, nereye götürür net | Her sayfada tek bir birincil buton | Zorunlu |
| YL-13 | **Formlar çalışıyor** — gönderim ulaşıyor, hata/başarı mesajı görünür, çift gönderim kilitli, doğrulama gerçek, KVKK onayı kutusu bağlı | Uçtan uca kayıt: tarayıcı + sunucu + teslim (e-posta/CRM) | Zorunlu |
| YL-14 | **Analytics kurulu ve doğrulanmış** — hangi olaylar, hangi panoya girdiği, çerez onayıyla ilişkisi | Test olayının panelde görünmesi | Şartlı *(ölçüm isteniyorsa)* |

#### Tier D — Arama motoru temeli

| ID | Kontrol | Kanıt / hedef | Uyg. |
|---|---|---|---|
| YL-15 | **Meta başlık + açıklama** — sayfa bazlı, her sayfada tekil, sınır içinde | Sayfa listesi + benzersizlik kontrolü | Zorunlu |
| YL-16 | **Canonical URL'ler** — parametreli/çoklu URL'lerde tek adres | İncelenen sayfalarda `rel=canonical` | Zorunlu |
| YL-17 | **sitemap.xml** — yalnız indekslenebilir URL'ler, Search Console'a gönderildi | GSC sitemap durumu + kapsam | Zorunlu |
| YL-18 | **robots.txt** — engellenmesi gerekenler engellendi; **AI tarayıcı kuralları ayrı ayrı düşünüldü** (`GPTBot` eğitim · `OAI-SearchBot` arama · `ClaudeBot` / `Claude-SearchBot` · `Google-Extended`) | Robots.txt Test aracından doğrulama; CDN katmanında AI bot engeli yok | Zorunlu |
| YL-19 | **Özel 404 sayfası** — kullanıcıyı ana sayfaya veya ilgili bölüme yönlendirir | Adres çubuğunda kalan, link veren 404 | Şartlı *(site 3+ sayfaysa)* |

#### Tier E — Erişilebilirlik ve içerik

| ID | Kontrol | Kanıt / hedef | Uyg. |
|---|---|---|---|
| YL-20 | **Erişilebilirlik** — WCAG 2.1 AA: klavye ile tam kullanım, odak görünür, form etiketleri, başlık sırası, renk kontrastı | Otomatik tarama **+ klavye/ekran okuyucu elle deneme** (tarama tek başına yeterli değil) | Zorunlu |
| YL-21 | **Görsel alt metinleri** — anlamlı görsellerde açıklayıcı, dekoratifte `alt=""`, `width`/`height` zorunlu | Sayfa sayımı + elle kontrol | Zorunlu |
| YL-22 | **Sık sorulan sorular** — gerçek sorular, `FAQPage` JSON-LD ile işaretli | İçerik + şema doğrulaması | Opsiyonel |
| YL-23 | **Yapılandırılmış veri** — `Organization` / `LocalBusiness` / `Service` / `BreadcrumbList` | Rich Result Test | Opsiyonel *(yerel/kurumsal görünüm varsa Şartlı)* |
| YL-24 | **İç bağlantı** — breadcrumb, ilgili içerik, ölü iç link yok | Kırık link taraması + site haritası | Şartlı *(içerik sitesi varsa)* |

#### Tier F — Marka ve ikincil yüzeyler

| ID | Kontrol | Kanıt / hedef | Uyg. |
|---|---|---|---|
| YL-25 | **Sosyal paylaşım** — Open Graph + Twitter Card, 1200×630 görsel, başlık/açıklama | Paylaşım önizlemesinin doğru çıkması | Opsiyonel |
| YL-26 | **Favicon + `apple-touch-icon` + manifest + `<html lang>`** | Sekme, iOS ana ekran, dil işaretleme | Opsiyonel |
| YL-27 | **`llms.txt`** — kökte `200`, H1 + özet + bağlantılar | *Beklenen faydası kanıtlanmamıştır, aşağıya bak.* | Opsiyonel |

> **⚠️ `llms.txt` hakkında dürüst ol.** Bu dosya `robots.txt`'in AI karşılığı **değildir** ve
> `robots.txt`'e alternatif değildir — bu ikisi farklı işler yapar ve karıştırılması bir
> kategori hatasıdır. `robots.txt` (RFC 9309) kimin neyi okuyabileceğini **kısıtlar** ve büyük
> tarayıcılar bunu uyarır. `llms.txt` yalnızca bir okuma önerisi sunar.
>
> **Ölçülmüş durum (2026):** dört bağımsız çalışma fayda bulamadı — geniş alan tarayıcılarının
> çoğunluğunda dosyaya yapılan istek oranı %0.1'in altında, yayımlayan alan adlarının ~%97'sinde
> dosya hiç istek almıyor; alan adı ölçekli çalışma korelasyon bulamadı. Google kendi
> dokümantasyonunda Search'ın bu dosyayı **kullanmadığını** yazıyor.
>
> **Yine de `Opsiyonel` işaretlenir, çünkü:** maliyeti ~1 saat, gözlenen zararı yok ve
> **geliştirici dokümantasyonu / kod ajanları için gerçek bir kullanım var** (agent
> tabanlı kodlama araçlarına yönlendirme girdisi vermek; bu, tarayıcı tabanlı
> cevap motorlarının okuduğu senaryodan farklıdır). Doğrulanabilir tek senaryo:
> **kendi sunucu loglarında `/llms.txt` isteği saymak.**
> Logda istek yoksa dosya işlevini yapmıyor demektir — bu ölçüm PRD'de yazılmalıdır.

#### Tier G — Yayından sonra sessizce öldürenler

*Bu tier yayın gününde bitmez; sahibi ve kontrol periyodu yazılır. Tarih değil, sorumluluk yazılır.*

| ID | Kontrol | Kanıt / hedef | Uyg. |
|---|---|---|---|
| YL-28 | **Domain + SSL yenileme sorumluluğu** — kim, hangi periyotta, hatırlatma nerede | Süre dolmadan yenileme prosedürü | Zorunlu |
| YL-29 | **Yedekleme** — kod + içerik + veri; geri yükleme provası yapıldı mı | En az bir geri yükleme denemesi | Zorunlu |
| YL-30 | **Hata ve uptime izleme** — form bozulduğunda kimse öğrenmesin | Sentry/telemetri + uptime alarmı | Şartlı *(form varsa Zorunlu)* |

#### Tier H — Bağlama göre

| ID | Kontrol | Uyg. |
|---|---|---|
| YL-31 | **İçerik JS ile mi render ediliyor?** — öyleyse Googlebot'a görünür mü doğrulanır (URL Inspection) | Şartlı *(SSR/CSR ayrımı varsa Zorunlu)* |
| YL-32 | **Çok dilli ise `hreflang`** — karşılıklı dil etiketleri, `x-default` | Şartlı *(>1 dil varsa)* |
| YL-33 | **Fiyat/plan şeffaflığı** — neyin ücretsiz, neyin ücretli, neyin sınırlı olduğu sayfada yazılı | Şartlı *(ücretli model varsa)* |

#### Bu bölümü doldururken

1. **Kanıt sütununu tahmin etme.** Ürünün kendi verisine bağlı olmayan genel bir AI çıktısı,
   elle yazılmış bir PRD'den kötüdür (bkz. §12). Ölçmediysen `Şartlı` + "kim ölçecek" yaz.
2. **`Şartlı` satırın şartı karar değildir, cümledir.** "Şartlı *(e-ticaret varsa)*" yeter;
   şartın kendisi bir sahibe ve tarihe bağlanır.
3. **`Opsiyonel` ≠ `Yapma.`** Opsiyonel bir satır, kapsam dışı değildir; karar kaydıyla bekler.
   Asıl kapsam dışı (§4) hâlinde yazılır.
4. **Tutarlılık §6'nın işidir.** "Hedeflenmiyor" yazan bir §3 ile "Zorunlu" yazan bu liste
   çelişiyorsa belgenin hangisinin doğru olduğunu bul — bu listenin reddedilmesi değil,
   belgenin hangisinin güncelleneceğidir.

#### 20.1 KVKK / Gizlilik Denetim Raporu

*Veri ekseni `EVET`se **zorunludur** ve `HAYIR` ise §21'e gerekçesiyle yazılır. Bu
bölüm görev listesi değil, **üretilen kanıttır**; boş bırakılmaz.*

**Denetim tarihi:** [tarih] · **Kapsam:** [commit/branch veya yayın adresi] · **Uygulama tipi:** [6 tipten biri — `references/kvkk-uyum-denetimi.md` §1 matrisi]

##### 20.1.1 Denetim tablosu

**Durum sözlüğü dört değerdir:** `Uyumlu` · `Eksik` · `Uyuşmazlık` · `Doğrulanmalı`.
"Kötü", "riskli", "olmalı" bir durum **değildir** — yorum "Ne yapılmalı" sütununa yazılır.

> **Kanıt yoksa `Uyumlu` yazılmaz.** Emin olmadığın her yerde `Doğrulanmalı` yazılır.
> Bu bölüm yayın izni verdiği için, anahtar niteliğinde bir konuda yazılan "Uyumlu"
> hukuki risk doğurur.

| # | Madde | Dosya:satır | Durum | Ne yapılmalı | Sorumlu | Tarih |
|---|---|---|---|---|---|---|
| KV-01 | [veri toplama noktası] | [dosya:satır] | Uyumlu | — | | |
| KV-01 | [veri toplama noktası] | [dosya:satır] | Eksik | | | |
| KV-02 | [dış servis] | [dosya:satır] | Uyuşmazlık | | | |
| KV-03 | [metin ↔ site farkı] | [sayfa ↔ dosya:satır] | Uyuşmazlık | | | |
| KV-04 | [onay kutusu] | [dosya:satır] | Eksik | | | |
| KV-05 | [reddin engellediği istek] | [dosya:satır] | Doğrulanmalı | | | |
| KV-06 | [güvenlik bulgusu] | [dosya:satır] | Uyuşmazlık | | | |

> **`Dosya:satır` burada §3'ün istisnasıdır.** PRD gövdesi zamanla eskir, bu yüzden
> gövdede dosya yolu ve satır numarası yazılmaz. **Denetim raporu bir anlık görüntüdür**
> ve izlenebilir olmak zorundadır; bu yüzden satır numarası yazılır. Raporun başındaki
> tarih ve kapsam notu bu "eskiyebilir" riskini yönetir.

##### 20.1.2 Veri envanteri

| Veri | Toplayan nokta | Nereye gidiyor | Hukuki sebep | Saklama | Aktarım (yurt dışı mı?) |
|---|---|---|---|---|---|
| [ad, e-posta] | [form / ekran] | [tablo / e-posta servisi / API] | [sözleşme m.5/1 · açık rıza] | [süre] | [servis — ülke] |

Boş tablo bırakılmaz: **"kişisel veri toplanmıyor" ise bu cümle tek satır olarak yazılır**
ve gerekçesi verilir (hangi ekran ve uç noktaların tarandığı).

##### 20.1.3 Koddan doğrulanamayanlar

Bu alt bölüm **boş bırakılamaz.** Koddan doğrulanamayan her madde buraya, tarayıcı veya
panel adımıyla birlikte yazılır:

| Madde | Neden koddan doğrulanamadı | Nasıl kontrol edilir | Sorumlu | Tarih |
|---|---|---|---|---|
| | | [Network paneli · Application/Cookies · sağlayıcı paneli] | | |

##### 20.1.4 Kapanış

Rapor şu paragrafın **birebir kopyasıyla** kapanır:

> Bu inceleme hukuki danışmanlık yerine geçmez; yasal metinler işletme tarafından, gerekirse bir hukukçuyla onaylanmalıdır.

---

### 21. Varsayım Kaydı ve Ekler

**Kullanılmayan bölümler:** [Bu PRD'de hangi bölümler yazılmadı ve neden — atlanan her bölüm kayıt altındadır.]

**Varsayımlar:** [Belgede kullanılan `[ASSUMPTION]` etiketlerinin özeti. Tablo boşsa "varsayım yok" yaz.]

**Ekler:** [Figma, prototip, ilgili PRD'ler, karar kayıtları, benchmark sonuçları]

</prd-sablonu>

---

## 5.1 Zorunlu HANDOFF.md Sistemi ve Şablonu

PRD "ne inşa edileceğini", kabul kriterlerini ve sınırları belirler. Ancak yazılım tek bir oturumda bitmez; yeni bir yapay zekâ ajanı veya geliştirici projeye dahil olduğunda bağlam penceresi sıfırlanır.

**HANDOFF.md dosyasının amacı:**
1. **Oturumlar arası sıfır kafa karışıklığı:** Yeni gelen ajanın "nerede kaldık?" sorusuna tek dosyada yanıt vermek.
2. **Hata tekrarlarını önlemek:** Önceki oturumda yaşanan, saatler kaybettiren ve kanıtlanmış tuzakları listeleyerek yeni ajanın aynı çukura düşmesini engellemek.
3. **Doğrudan eyleme geçiş:** Yeni ajanın varsayımda bulunmadan önce çalıştıracağı ilk doğrulama komutlarını ve 1-2-3 şeklinde sıralı iş listesini sunmak.

### HANDOFF.md Kuralları
- **Konum:** Her zaman projenin **kök dizininde** (`HANDOFF.md`). Başka bir konuma
  kopya yazılmaz; alt klasördeki kopya bayat olabilir.
- **Zorunlu Güncelleme:** PRD teslim edildiğinde veya geliştirme oturumu
  tamamlandığında/devredildiğinde **mutlaka** güncellenir.
- **Uydurma Yasaktır:** "Önce Bunu Oku" bölümündeki tuzaklar tahminle değil,
  oturum sırasında bizzat karşılaşılan ve çözülen somut hatalardan yazılır.
- **Yarım bırakma yok:** §3 "Sıradaki İş" boş bırakılmaz. Açık iş kalmadıysa
  `Açık iş yok — proje tamamlandı.` yazılır.

### Şablon ve ayrıntılar

Şablon **tek kaynaktan** gelir; bu skill içinde ikinci bir kopya tutulmaz:

- Şablon: [`templates/HANDOFF.template.md`](../../templates/HANDOFF.template.md)
- İçerik kuralları ve "ne yazılır / ne yazılmaz":
  [`rules/knowledge-base-management.md`](../../rules/knowledge-base-management.md)

`HANDOFF.md` ile `knowledge-base.md` karışmaz: kararlar `knowledge-base.md`'ye,
durum ve sıralı işler `HANDOFF.md`'ye yazılır.

---

## 6. Kalite Kontrol (Üretmeden Önce)

**Bu bölüm bilinçli olarak puanlamaz.** Tek kalite kapısı Adım 4'teki 90 puanlı kontroldür: o,
yazmadan önce "hazır mıyım" sorusunu yanıtlar; buradaki liste ise yazılan metinde tutarlılık
aranır. Aynı işi yapan iki ayrı puanlama mekanizması yan yana koymak hangisinin esas olduğunu
belirsizleştirir ve ikisini de zayıflatır.

- [ ] Her US'nin Gherkin senaryosu var mı?
- [ ] Her kriter ikili (geç/kal) mi?
- [ ] JTBD → US → FR → kriter zinciri kopuk değil mi?
- [ ] Anti-goals ve Out of scope dolu mu?
- [ ] Kalite puanı ≥ 90 mı?
- [ ] Her sayının kaynağı var ya da `[VERIFY]` ile işaretli mi?
- [ ] Her metriğin baseline'ı var mı?
- [ ] Her `[VERIFY]` / `[ASSUMPTION]` / `[NEEDS CLARIFICATION]` etiketinin sahibi ve hedef tarihi var mı?
- [ ] Negatif kriter ("bu olmamalı") var mı?
- [ ] Hiçbir yerde `TBD`, "implement later", "uygulama sonra", "hata yönetimi ekle" kalmadı mı?
- [ ] Kapsam dışındaki hiçbir madde gövdede gereksinim olarak geri gelmedi mi?
- [ ] Eskime karşıtı kurallara uyuldu mu?
- [ ] Dosya `docs/{feature}-prd.md` yoluna **tam gövdeyle** yazıldı mı?
- [ ] **Geliştirme devri için kök dizinde `HANDOFF.md` üretildi veya güncellendi mi?**
- [ ] **`HANDOFF.md` içinde "Önce Bunu Oku" (düşülen hatalar ve kanıtlanmış tuzaklar) bölümü somut örneklerle dolu mu?**
- [ ] **Yeni bir kod ajanının sıfır soruyla devam edebileceği doğrulama komutları ve sıralı iş listesi mevcut mu?**

**Yayın sınıfında ayrıca** (bu kontrol puanlamaya dahil değildir):

- [ ] §20 yazıldı mı — ya da Adım 0'da sınıf "Yayın" değilse gerekçesi §21'de mi?
- [ ] §20'de **belirsiz satır yok** (her satır `[x]` ya `[ ]`, kanıt + sahip + tarih)?
- [ ] **Tier A (yasal) ve Tier B (altyapı) yeşil mi?**
- [ ] Core Web Vitals hedefi **mobil ve 75. persentil** için mi yazıldı?
- [ ] §4 teknik kısıtlarıyla §20 arasında **çelişki var mı**?
- [ ] Ölçülebilir faydası olmadığı bilinen kalemler (`llms.txt`) **`Opsiyonel` + gerekçeyle** mi yazıldı?

**Veri ekseni `EVET` olan PRD'de ayrıca** (bu kontrol puanlamaya dahil değildir):

- [ ] **Uygulama tipi** belirlendi ve `references/kvkk-uyum-denetimi.md` §1 matrisi uygulandı mı?
- [ ] §20 Tier A-2 (KV-01..KV-06) yazıldı mı — `Şartlı`/`Opsiyonel` satırları gerekçeli mi?
- [ ] §20.1 raporu **dört alt bölümüyle** dolu mu (denetim tablosu · veri envanteri · koddan doğrulanamayanlar · kapanış)?
- [ ] **Durum sözlüğü dört değerden mi?** "Kötü / riskli / olmalı" gibi bir durum yazılmadı mı?
- [ ] **Kanıtı olmayan hiçbir satır `Uyumlu` değil** ve **raporda `Doğrulanmalı` kalmadı** mı?
- [ ] Aydınlatma metni karşılaştırması **iki yönlü** mi (metinde olup sitede yok **ve** sitede olup metinde yok)?
- [ ] md.11 haklarının **her biri** hem metinde hem uygulamada karşılığı var mı?
- [ ] Pazarlama onayı **önceden işaretli değil** ve cevap vermek rızaya bağlı değil mi?
- [ ] "Reddet" akışı **gerçekten** hiçbir izleme isteği göndermiyor mu (kod kanıtı veya tarayıcı kanıtı)?
- [ ] Yasal uyarı paragrafı **birebir** yazıldı mı?

---

## 7. Adversarial İnceleme (Güçlü, Opsiyonel)

Kendi yazdığın belgeyi kendi gözden geçirmek yerine **ayrı bir geçişte düşman bakışıyla**
okut:

```
Şimdi bu PRD'yi şüpheci bir mühendislik lideri olarak oku. Niyetin onaylamak değil, çökertmek.
Şunları listele:

1. Bu PRD'deki hangi varsayımlar verilen kanıta dayanmıyor? Her biri için: hangi ifade yanlış
   çıkarsa proje çöker, ve bunun yanlış olduğunu anlamanın yolu ne?
2. Hangi başarı metriği oyunlanabilir? Nasıl?
3. En riskli üç açık soruyu öncelik sırasıyla ver.
4. Kabul kriterleri gerçekten ikili mi? Hangileri iki kişi farklı yorumlar?
5. Kapsam dışı listesinde gizlenmiş bir kapsam genişletme var mı?
6. Bu belgeyi okuyan bir geliştirici hangi soruyu sormak zorunda kalır?
```

**Neden ayrı geçiş:** Kodunu az önce üreten bir model, kendini doğrularken doğruluğu halüsine
eder. Bu yüzden gözden geçirme, bağlamı paylaşmayan ayrı bir okuma olarak yapılmalı.

**Bu çıktının tamamını belgeye koyma.** Her biri ya düzeltmeye dönüşür ya da açık soruya (sahibi +
tarih ile) dönüşür. Düzeltme yapmadan atlanan eleştiri, hiç sorulmamış bir eleştiriden daha kötüdür —
görüntü var, karşılığı yok.

---

## 8. Sık Yapılan Hatalar

| Hata | Belirti | Düzeltme |
|---|---|---|
| Uydurulmuş kesinlik | "Yanıt süresi 200 ms olmalı", kimse ölçmemiş | `[VERIFY]` koy veya kullanıcıya sor |
| Baseline'sız hedef | "Etkileşimi %25 artır" | Baseline sor, yoksa `[VERIFY]` |
| Kategori tarifi | "Sonuçlar verimli aranabilir" | Sayı ver veya `[VERIFY]` |
| Uydurulmuş iş kuralı | "Kurumsal müşteriler için 14 gün deneme" — kimse söylememiş | Kaynağını iste; yoksa `[NEEDS CLARIFICATION]` |
| Erken çözüm | Story'nin içine UI aracı girmiş | İhtiyacı yaz, aracı §7'ye |
| Aşırı kesinlik | "Tam olarak 7.5 inç, 14 ons" — gerekçesi yok | Gerekçe yoksa o kadar kesin olma |
| Kod sızdırma | Belgede dosya yolu, SQL, kod parçası | Modül + sözleşme + gerekçe yeter |
| **Tutarsızlık** | Bir bölüm "mobil desteklenir", diğerinde mobil kapsam dışı | §6 zincir kontrolü |
| **Uyumsuz standart** | "Sakinleştirici sesler" ürünü için endüstriyel alarm standardı | İlgili olmayan standardı koyma |
| **Aşırı korumasız** | "Bunlar temeldir, kaldırılırsa proje çöker" | Must %60 kuralı |
| **Duruma gömülü `Then`** | "veritabanında kayıt oluşmuştur" | Gözlemlenebilir çıktı yaz |
| **Bakım yok** | PRD onaylandı, 2 hafta sonra güncellenmedi | **Bakılmayan PRD, PRD olmayandan kötüdür** — sürüm ver, canlı tut |
| **Yayın kapısı atlandı** | Site canlıya alındı, HTTPS/meta/sitemap hiç yazılmamış | §20 zorunlu; "sonra bakarız" yayın engelidir |
| **Teknik SEO uyduruldu** | "SEO uyumlu olacak" | Her kalem tek satır: canonical, sitemap, robots, 301, 404 durum kodu |
| **Kanıtsız teknoloji vaadi** | "`llms.txt` AI görünürlüğünü artırır" | Ölçülmüş faydası yok — `Opsiyonel` + gerekçe + "logda say" ölçümü |
| **Dosya kategorisi karıştırıldı** | "`llms.txt`, `robots.txt` yerine geçer" | Hayır: `robots.txt` (RFC 9309) izin verir, `llms.txt` yalnızca önerir |
| **Yasal sayfa "sonra"** | "KVKK metni yayından sonra yazılır" | Geri dönüşü yok; Tier A yayın engelleyicidir |
| **KVKK tuzağı: şablon** | Metinde var, sitede yok (ya da tam tersi) | Karşılaştırma **iki yönlü**; `Uyuşmazlık` yaz |
| **KVKK tuzağı: tek onay kutusu** | Aydınlatma ve rıza tek `✓`'da birleşik | Ayrı kutular; rıza geri alınabilir olmalı |
| **KVKK tuzağı: rızaya bağlı hizmet** | "Mesaj gönderebilmek için işaretleyin" | Cevap vermek serbest; pazarlama izni ayrı ve isteğe bağlı |
| **KVKK tuzağı: banner yeterli sanmak** | Çerez onay bandırı var, kod onay öncesi yükleniyor | Red sonrası **hiç istek gitmiyor** mu diye kanıtlanmalı |
| **KVKK tuzağı: "veri gönderilmiyor"** | Piksel/analytics "sadece ziyaretçi sayar" | IP, yönlendirme, oturum kaydı gider; yurt dışı aktarımı da yazılır |
| **Kanıtsız "Uyumlu"** | Tarama yapılmadan rapor tümü yeşil | Kanıt yoksa `Doğrulanmalı` — bu, kontrol edilmemiş demektir |
| **Kişisel veri logda** | `console.log(formData)`, `logger.info(user)` | Kişisel veri hiç yazılmaz; korelasyon id yeter |
| **Sadece masaüstü test edildi** | Lighthouse masaüstü skoru 98 | Core Web Vitals 75. persentil **mobil** ölçülür |
| **HANDOFF.md yazılmadı / güncellenmedi** | Yeni oturumdaki ajan sıfırdan başlar, aynı tuzaklara düşer, saatler kaybedilir | Her PRD tesliminde ve oturum devrinde kök HANDOFF.md zorunlu |

---

## 9. Kaynaklar

Bu skill şu kaynakların iyi olan kısımlarını birleştirir:

- **Oturumlar arası bağlam kaybını ve hata tekrarlarını önleyen HANDOFF.md standardı** → projeler arası geliştirici belleği ve oturum devir protokolü (`.agent/AGENTS.md` + `rules/handoff-session-continuity.md`)

- **Keşif, derin modül, test kararı, "dosya yolu/kod yazma" yasağı** → `prd-yaz` (eyaprak)
- **15+ bölümlü AI-uyumlu şablon, JTBD, AI Build Summary, Component/Data/API/State, iki katmanlı AC**
  → johnnychauvet
- **100 puan kalite kapısı, 90 eşik, risk matrisi, fazlama, glossary, bağımlılıklar** → McpMarket (Sarah)
- **PRD bir konuşma ürünüdür, PRD → issue zincirine girer** → Matt Pococ / mattpocock `write-a-prd` + `prd-to-issues`
- **Gherkin sözleşmesi, `Background`, `Scenario Outline`, tag, tek davranış, deklaratif yazım, anti-pattern**
  → Cucumber / Gherkin docs
- **EARS kalıpları, RFC 2119/BCP 14, katman disiplini, "teknoloji önerisine kaynak zorunluluğu"**
  → EARS (Mavin vd., IEEE RE'09) + AWS Kiro
- **Non-goals, "hepsi Must ise hiçbiri Must değildir", Must %60, parking lot, leading/lagging, INVEST,
  "amaç değil sonuç"** → Anthropic `feature-spec` + DSDM MoSCoW
- **`[NEEDS CLARIFICATION]`, `[ASSUMPTION]`, `FR-00N` izlenebilirlik şeması** → GitHub spec-kit
- **Vague ↔ somut örnek çiftleri, TBD yasağı, ayrılmış eleştiri bağlamı** → GitHub awesome-copilot `prd` + superpowers
- **Değerlendirme stratejisi, davranışsal kısıtlar, başarısız modlarının gerçek çıktılardan çıkarılması,
  ikili ölçüm** → Adaline AI
- **Yargı/genişletme ayrımı, 4 geçişli düzenleme akışı** → Pickuma
- **Baseline + pencere + ölçüm yöntemi tablosu, bitirme kontrol listesi, "bakılmayan PRD kötüdür"**
  → Vantage / aioproductos
- **Uzunluğun riske göre ölçeklenmesi, "bölüm uydur" kuralı** → BMAD-METHOD
- **Soru aracı seçimi, kritik kararlarda sessiz varsayım yasağı** → `prd-yaz` (eyaprak)
- **§20 Yayın Kontrol Listesi: Core Web Vitals eşikleri (LCP 2.5 sn / INP 200 ms / CLS 0.1,
  75. persentil), sitemap + Search Console, canonical, robots.txt, soft-404, JSON-LD**
  → [Google Search Central](https://developers.google.com/search/docs)
- **`robots.txt` bir standarttır (RFC 9309) ve AI tarayıcıları da uyar; `llms.txt` bir öneridir
  ve faydası ölçülmemiştir; AI tarayıcı user-agent ayrımları (GPTBot vs OAI-SearchBot,
  ClaudeBot vs Claude-SearchBot, Google-Extended)**
  → [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309) ·
  [Google — AI features in Search](https://developers.google.com/search/docs/appearance/ai-features) ·
  alan adı ölçekli log ve alan adı ölçekli korelasyon çalışmaları (Ahrefs, SE Ranking, OtterlyAI, Adobe/Longato)
- **KVKK aydınlatma metni ve çerez onayı içeriği (hangi başlık zorunlu)**
  → [KVKK 6698](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.6698.pdf) · Çerez politikası için
  [İnternet haberleşmesi hizmeti sağlayıcıları**nın** benzer hizmet sağlayıcılara ilişkin
  yerine getirilmesi gereken bilgiler** yönetmeliği — `[VERIFY: güncel madde numarası, metni
  hukuk onaylasın]`
- **§20.1 KVKK denetimi ve Tier A-2 yöntemi (veri envanteri, dış servisler, aydınlatma
  karşılaştırması, onay kutuları, çerez onayı, güvenlik; 6 uygulama tipi matrisi)**
  → `references/kvkk-uyum-denetimi.md` (bu skill'in kendi kaynağı)
- **Çerez onayı gerçekten engelliyor mu: `setDefaultConsentState` varsayılanı `denied` olmalı
  ve `wait_for_update` (ms) CMP yanıtını bekletir; izin kararı etiketten **önce** verilir;
  GTM'de varsayılan izin `Consent Initialization` tetikleyicisiyle kurulur ve izleme etiketleri
  consent sinyaline bağlıdır; `addConsentListener` **`unset → granted` geçişinde tetiklenmez**
  (`unset` granted sayılır), bu yüzden "listener var ama çalışmıyor" görüntüsü çıkar; Analytics'in
  *gelişmiş* uygulamasında `analytics_storage: denied` olsa bile kimliksiz ölçüm gönderilir**
  → [Google Tag Manager — Consent Mode / consent APIs](https://developers.google.com/tag-platform/tag-manager/templates/consent-apis) ·
  [Server-side Consent Mode davranışı](https://developers.google.com/tag-platform/tag-manager/server-side/consent-mode)


Hiçbiri tek başına yeterli değil: süreç odaklı olanlar ölçümü kaçırır, şablon odaklı olanlar
görüşmeyi kaçırır, metodolojiyi iyi bilenler halüsinasyonu kaçırır. Bu skill'in değeri birleşimde.
