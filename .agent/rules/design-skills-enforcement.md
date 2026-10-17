---
name: Mandatory Design Skills
description: Tasarım, UI/UX ve görsel yerleşim taleplerinde canvas-design, frontend-design ve ui-ux-pro-max skillerinin birlikte okunmasını zorunlu kılar; ayrıca 13 skill'in sahiplik (tek sahip) haritasını tanımlar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Tasarım / skill sahipliği"
    komut: "python .agent/skills/musgoku/scripts/check_design_skills.py"
---

# ⛔ Zorunlu Tasarım Skilleri

## 1. Zorunlu üçlü

Tasarım, UI/UX, görsel yerleşim, spacing, CSS stillendirme, bileşen veya sayfa
tasarımı (dashboard, kart, tablo, grafik, form, modal) ile ilgili **herhangi
bir talepte** aşağıdaki üç skill **birlikte** okunur ve uygulanır:

1. `canvas-design` — kompozisyon, negatif alan, derinlik, zanaat standardı
2. `frontend-design` — karakterli tipografi, renk paleti, generic "AI slop"
   kalıplarından kaçınma
3. `ui-ux-pro-max` — stil/palet/font/UX/grafik referans kütüphanesi

## 2. Zorunlu akış

1. Tasarım talebi geldiğinde **kodlamaya başlamadan** bu üç skill'i oku.
2. Generic hazır şablonlar ve sıradan renkler yerine ferah, profesyonel ve
   hiyerarşik görsel dil uygula.
3. Yanıtın başlangıcında bu üç skill'in ve kullanılan MCP araçlarının
   **aktif devrede olduğunu** açıkça belirt.

## 2.1 Prompt Makroları ve Hızlı Kısayollar (`[DESIGN-REFRESH]`, `[UI-POLISH]`, `[UX-POLISH]`, `[RESPONSIVE-POLISH]`)

Kullanıcının her seferinde uzun ve detaylı tasarım/UX prompt'ları yazmasını önlemek için standart kısayol etiketleri ve kısa tetikleyiciler tanımlıdır:

- **Etiketler:** `[DESIGN-REFRESH]`, `[UI-POLISH]`, `[DASHBOARD-POLISH]`, `[UX-POLISH]`, `[RESPONSIVE-POLISH]`
- **Kısa Tetikleyiciler:** `"UI polish"`, `"tasarımı düzelt"`, `"ekranları toparla"`, `"tasarımı profesyonelleştir"`, `"sayfaları güzelleştir"`, `"responsive yap"`, `"kullanıcı dostu yap"`, `"mobilde düzelt"`, `"modalı düzelt"`

Ajan bu etiket veya ifadelerden birini gördüğünde kullanıcıdan ek açıklama veya çözünürlük talimatı beklemeden doğrudan:
1. `frontend-design`, `ui-ux-pro-max` ve (Tailwind ise) `ui-styling` skill'lerini açar.
2. Belirtilen ekranlarda "AI-slop" şablonlarını temizler; derinlikli görsel hiyerarşi, nefes alan boşluk ritmi (spacing scale), rollerin hızlı taramasını (rapid scanning) destekleyen durum rozetleri ve diff alanları uygular.
3. Arka plandaki iş mantığını (logic), state yönetimini ve API veri akışını bozmadan cerrahi refactoring yapar.
4. Aşağıdaki §2.2 (4 UX Durumu), §2.3 (3 Cihaz Ergonomisi) ve §2.4 (Adaptif Modal) standartlarını eksiksiz sağlar.
5. Gözle doğrulama adımlarını (Masaüstü, Tablet ve Mobil için ayrı ayrı) `KULLANICI_TEST_REHBERI.md` dosyasına ekler.

## 2.2 Zorunlu 4 UX Durumu Sözleşmesi (The 4 UI/UX States Matrix)

Hiçbir sayfa, form, tablo veya arayüz bileşeni yalnızca "başarılı veri var" haliyle teslim edilemez. Her bileşen şu 4 UX durumunu eksiksiz karşılamak zorundadır:

1. **Loading State (Yüklenme Durumu):**
   - Veri çekilirken içeriğin düzenini koruyan skeleton screens veya belirgin spinner.
   - Form gönderimi veya buton tıklamasında çift tıklamayı önleyen `disabled` ve buton içi loading durumu (`isSubmitting`).
2. **Empty State (Boş Durum):**
   - Henüz veri/kayıt yokken veya filtre sonucu boş döndüğünde donuk/beyaz ekran bırakılamaz.
   - Amaca uygun açıklayıcı ikon + net başlık + yönlendirici açıklama + birincil aksiyon CTA butonu (*"İlk Projeni Ekle"*, *"Filtreleri Temizle"*).
3. **Error State (Hata Durumu):**
   - Genel/kriptik hata kodları yerine; kullanıcı diliyle yazılmış inline hata mesajı, problemin net sebebi ve doğrudan çözüm sunan *"Yeniden Dene"* (Retry) aksiyonu.
4. **Action Feedback & Success (Teyit ve Başarı):**
   - Kullanıcının gerçekleştirdiği her kritik aksiyon (ekleme, silme, güncelleme) anında geri bildirim üretmelidir: net Toast bildirimi, animasyonlu onay veya listenin anında güncellenmesi (optimistic UI).

## 2.3 Üç Katmanlı Çözünürlük & Cihaz Ergonomisi Sözleşmesi (Responsive Viewport Contract)

⛔ **Tek Boyutlu Büzüştürme Yasağı:** Responsive tasarım yalnızca masaüstü grid'ini dar ekranda `grid-cols-1` ile alt alta dizmek değildir. Kullanıcı her çözünürlüğü ayrı ayrı belirtmek zorunda kalmamalıdır. Ajan, her arayüzü şu 3 farklı ergonomik modda **varsayılan refleks** olarak tasarlamak zorundadır:

| Viewport | Genişlik | Ergonomik Rol & Davranış Standardı |
|---|---|---|
| **Mobil** | `< 768px` | **Başparmak Ergonomisi (Thumb Zone):** Tek sütun akış; kritik aksiyonlar ve navigasyon ekranın alt kısmında (`Bottom Navigation` / `Bottom Action Bar`); minimum 44×44px dokunma hedefleri (`min-h-[44px] min-w-[44px]`); yatay kaydırılabilir hap etiketler (`horizontal scroll chips`); geniş veri tabloları yerine kart listesi (card-based view). |
| **Tablet** | `768px – 1024px` | **Dengeli İki Sütun & Split-View:** Ne mobildeki gibi dar tek sütuna sıkışmalı ne de masaüstü gibi aşırı yayılmalıdır. İki sütunlu dengeli grid; sol tarafta liste sağ tarafta detay gösteren `Split-View`; katlanabilir/daraltılmış ikon çubuğu (rail sidebar); dokunmatik ekran önceliği (fare hover'ına bağımlı menü ve aksiyonlar KESİNLİKLE yasak). |
| **Masaüstü** | `> 1024px` | **Zengin Bilgi Yoğunluğu (Dense Layout):** Tam açık sol kenar çubuğu (sidebar); çok sütunlu zengin ızgara (3-4 kolon); detaylı veri tabloları ve filtre barları; klavye kısayolları ve hover mikro etkileşimleri. |

## 2.4 Adaptif Modal, Dialog & Popup Standartları (Adaptive Modal / Bottom-Sheet Pattern)

Popup ve modallar sayfanın en kritik etkileşim noktalarıdır. Bir modal teslim edilirken şu 3 ilke zorunludur:

1. **Tasarım Bütünlüğü ve Token Uyumu:**
   - Açılan her modal, popup veya popover; uygulamanın genel renk paletini, border-radius ritmini (`rounded-2xl` vb.), tipografi hiyerarşisini ve backdrop-blur (`backdrop-blur-sm bg-black/50`) stilini birebir miras almalıdır. Yabancı/harici kütüphanelerin varsayılan generic stilleri kabul edilemez.
2. **Adaptif Form Faktörü (Masaüstü Dialog ↔ Mobil Bottom Sheet):**
   - **Masaüstünde (`≥ 768px`):** Ortalanmış, odaklanmış Modal Dialog (`max-w-lg mx-auto rounded-2xl shadow-2xl`).
   - **Mobilde (`< 768px`):** Ortalanmış minik modal YASAKTIR. Otomatik olarak ekranın altından yükselen **Bottom Sheet (Drawer)** veya **Full-screen Sheet**'e dönüşmelidir (`fixed inset-x-0 bottom-0 rounded-t-2xl max-h-[90dvh]`). Kullanıcının başparmağıyla aşağı çekip kapatabileceği görsel tutamaç (`drag handle`) ve belirgin kapatma butonu zorunludur.
3. **Kaydırma, Klavye ve Taşma Güvenliği:**
   - **Scroll Koruması:** `max-h-[85dvh] overflow-y-auto` ve `overscroll-contain` zorunludur; modal açıldığında arka plan kaydırması (`body scroll lock`) kilitlenmelidir.
   - **Mobil Klavye Koruması:** Mobilde form inputuna tıklandığında sanal klavye açıldığında input alanının klavyenin altında kalmaması için safe-area padding (`pb-safe`, `pb-6`) ve dinamik viewport yüksekliği (`dvh`) kullanılmalıdır.

## 2.5 Gerçekçi Mock Veri ve Görsel Varlık Sözleşmesi (Realistic Mock Visuals Contract)

Arayüz bileşenlerinde (kartlar, kullanıcı profilleri, listeler, ürün ızgaraları, etkinlik/event takvimleri vb.) kullanıcı deneyimini ve görsel hiyerarşiyi bozacak donuk, gri boş kutular veya kırık harici placeholder servisleri (`via.placeholder.com` vb.) kullanılması **YASAKTIR**.

Ajan, görsel içeren her UI bileşeninde şu öncelik sırasını (fallback cascade) izlemek zorundadır:

1. **Öncelik 1 — Proje Varlıkları / Config (`.agent/config/assets.json`):**
   - Projede `.agent/config/assets.json` tanımlıysa ve yerel klasör veya GitHub deposu belirtilmişse varlıklar oradan çekilir.
2. **Öncelik 2 — Sıfır-Ayar Tematik Public Endpoint'ler (Deterministik & CORS-Free):**
   - Config yoksa veya ek varlık gerekiyorsa `mock-asset-provider` kataloğundaki kırılmayan servisler kullanılır:
     * **İnsan / Profil / Avatar:** RandomUser API (`https://randomuser.me/api/portraits/{women|men}/{id}.jpg`) veya DiceBear (`https://api.dicebear.com/7.x/...`).
     * **Etkinlik / Organizasyon / Zaman:** Deterministik seed ile Picsum (`https://picsum.photos/seed/{event-slug}/800/600`).
     * **E-Ticaret / Ürün:** DummyJSON veya Picsum ürün görselleri.
3. **Öncelik 3 — Yerel İndirme ve Kalıcı Ön Bellekleme (Local Caching):**
   - Çevrimdışı çalışabilirlik ve kırılma riskine karşı ajan, görselleri `python .agent/skills/mock-asset-provider/scripts/fetch_assets.py` ile projenin `public/mock-assets/` dizinine yerel olarak indirebilir veya Antigravity `image-generator` subagent'ı ile özgün üretebilir.

## 3. Sahiplik haritası — her konunun tek sahibi vardır

Tasarım alanına giren 13 skill'in sorumluluk sınırı şudur. **Bir konuyu iki
skill sahiplenmez.** Çakışma şüphesinde bu tabloya bak ve doğru olanı aç.

| Konu | Sahip skill |
|------|-------------|
| Ölçüsüz görsel sanat (poster, manifesto, `.png`/`.pdf`), font seti | `canvas-design` |
| Estetik yönelim, AI-slop kaçınma, UI kodu disiplini | `frontend-design` |
| Stil / palet / UX / stack önerisi (aranabilir veri) | `ui-ux-pro-max` |
| Hazır renk-font paleti (artifact teması) | `theme-factory` |
| Token üretimi (primitive → semantic → component) | `design-system` |
| Token'ı Tailwind/shadcn tarafına bağlama, stil uygulaması | `ui-styling` |
| Marka içeriği (ton, görsel kimlik, mesaj, varlık) | `brand` |
| Doküman yazma süreci (PRD, spec, karar) | `doc-coauthoring` |
| Sunum **stratejisi, metni, düzeni** | `slides` |
| Sunum/slayt **üretimi** (HTML render + token denetimi) | `design-system` |
| Sabit px ölçülü banner / kapak / reklam görseli | `banner-design` |
| Logo & CIP **brief'i**, sosyal medya görseli akışı, yönlendirme | `design` |
| UI kart, profil, etkinlik mock görselleri (placeholder alternatifi) | `mock-asset-provider` |
| IDE benzeri uygulama arayüzü | `web-ide-ux-architect` (kapsam dışı ilan eder) |

**Kapsam dışı ilan edilen:** `web-ide-ux-architect`

**Tipik hatalar ve doğrusu:**

- Sunum isteği → içerik için `slides`, render için `design-system`. İkisini birden
  "sahip" gösterme.
- "Poster yap" → `canvas-design`; "web hero banner yap" → `banner-design`
  (ölçüsüz sanat ≠ sabit px reklam).
- Palet sorusu → hazır tema `theme-factory`, ürüne özel palet `ui-ux-pro-max`,
  token `design-system`. Üçü farklı iş yapar.
- Marka dokümanı → içerik `brand`, yazma süreci `doc-coauthoring`.

## 4. Kapsam

Bu kural yalnız **görsel ve yapısal** tasarım işlerinde geçerlidir.
Yalnız renk değişikliği, tek bir metin düzeltmesi veya logik hatası için
üç skill'in tamamını okumak gerekmez — bu durumda hangisinin devrede olduğunu
belirtip geç.

`brand`, `slides`, `banner-design`, `design`, `doc-coauthoring`, `mock-asset-provider` üçlüye **dahil
değildir**; bunlar UI kodu üretmez, çıktı/strateji/varlık üretir. Onlar kendi
kapsam sınırı bölümünde tanımlıdır.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir tasarım/UI kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_