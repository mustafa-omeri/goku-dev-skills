---
name: Mandatory Design Skills
description: Tasarım, UI/UX ve görsel yerleşim taleplerinde canvas-design, frontend-design ve ui-ux-pro-max skillerinin birlikte okunmasını zorunlu kılar; ayrıca 13 skill'in sahiplik (tek sahip) haritasını tanımlar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Tasarım / sözleşme ve DESIGN.md uyumu"
    komut: "python .agent/skills/musgoku/scripts/check_design_contract.py"
  - yigin: "Tasarım / skill sahipliği"
    komut: "python .agent/skills/musgoku/scripts/check_design_skills.py"
  - yigin: "Tasarım / zanaat tabanı ve anti-slop"
    komut: "python .agent/skills/musgoku/scripts/check_design_slop.py"
  - yigin: "Tasarım / tema kontrastı ve WCAG uyumu"
    komut: "python .agent/skills/musgoku/scripts/check_theme_contrast.py"
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

## 2.1 Prompt Makroları ve Tasarım Fiilleri (`[DESIGN-REFRESH]`, `[UI-POLISH]`, `[BOLDER]`, `[QUIETER]`, `[DISTILL]`, `[HARDEN]`)

Kullanıcının her seferinde uzun ve detaylı tasarım/UX prompt'ları yazmasını önlemek için standart kısayol etiketleri ve 24 Tasarım Fiili (Design Verbs) makroları tanımlıdır:

- **Genel Yenileme Etiketleri:** `[DESIGN-REFRESH]`, `[UI-POLISH]`, `[DASHBOARD-POLISH]`, `[UX-POLISH]`, `[RESPONSIVE-POLISH]`
- **Tasarım Fiil Makroları (Design Verbs):** `[POLISH]`, `[BOLDER]`, `[QUIETER]`, `[DISTILL]`, `[HARDEN]`, `[CRITIQUE]`, `[AUDIT]`, `[SHAPE]`, `[TYPESET]`, `[COLORIZE]`, `[LAYOUT]`, `[DELIGHT]`, `[CLARIFY]`, `[ADAPT]`, `[ONBOARD]`, `[OPTIMIZE]`
- **Kısa Tetikleyiciler:** `"UI polish"`, `"tasarımı düzelt"`, `"daha cesur yap"`, `"sakinleştir"`, `"sadeleştir"`, `"sağlamlaştır"`, `"tasarımı eleştir"`, `"tipografiyi düzelt"`, `"renklendir"`, `"metinleri netleştir"`, `"responsive yap"`, `"tur ekle"`

### Fiil İcra Semantiği ve Davranış İlkeleri (Verb Execution Semantics)
Ajan, bu makro veya tetikleyicilerden birini aldığında şu davranış sınırlarına harfiyen uyar:
1. **`bolder` (Güçlendir):** Yalnızca hedef bileşeni güçlendirir; komşu elemanları veya sayfa sistemini bozmaz. Mevcut tasarım sisteminin tipografi ölçeğini ve motiflerini sonuna kadar kullanır; yeni renk veya font uydurmaz.
2. **`quieter` (Sakinleştir):** Fazla bağıran öğelerin doygunluğunu (%70–85) ve kontrastını düşürür; görsel gürültüyü arındırır. Ancak asla generic gri-beyaz şablona düşmez (dinginlik = zanaat inceliği).
3. **`distill` (Özüne İndir):** Süs kutularını, iç içe çerçeveleri ve anlamsız dekorasyonları ayıklar; tasarımı salt işlevsel özüne ve negatif alana kavuşturur.
4. **`harden` (Sağlamlaştır):** Bileşenin tüm 4 UX durumunu (Skeleton Loading, Empty State, Inline Error + Retry, Feedback Toast), klavye erişilebilirliğini ve taşma güvenliğini eksiksiz bağlar.
5. **`clarify` (Netleştir):** UX metinlerini ve buton etiketlerini eyleme dayalı ("Kaydet", "Projeyi Yayınla") ve doğrudan kullanıcı diline çevirir.
6. **`critique` (Eleştir):** Arayüzü Zanaat Tabanı (Craft Floor) ve Yüzey Modu (Surface Mode) açısından inceler, P0/P1/P2 öncelikli aksiyon listesi sunar.

Ajan, belirtilen ekranlarda iş mantığını (logic), state yönetimini ve API veri akışını bozmadan cerrahi refactoring yapar; gözle doğrulama adımlarını `KULLANICI_TEST_REHBERI.md` dosyasına ekler.

## 2.2 Zorunlu 4 UX Durumu Sözleşmesi (The 4 UI/UX States Matrix)

Hiçbir sayfa, form, tablo veya arayüz bileşeni yalnızca "başarılı veri var" haliyle teslim edilemez. Her bileşen şu 4 UX durumunu eksiksiz karşılamak zorundadır:

1. **Loading State (Yüklenme Durumu):**
   - **İskelet Ekranlar (Skeleton screens UI) KESİNTİSİZ ZORUNLUDUR:** Bir web sitesinde veya mobil uygulamada içerikler sunucudan yüklenirken gerçek verilerin yerine gösterilen, sayfanın genel yerleşimini (wireframe/kaset yapısını) taklit eden gri tonlu görsel taslakların (Skeleton screens) sunulması zorunludur. AI ajanları bu kuralı ASLA ATLAYAMAZ.
   - **Spinner Kullanım Sınırı:** Dönen yükleme göstergesi (Spinner), YALNIZCA buton içi form gönderimlerinde (`isSubmitting` durumunda `disabled` buton yanında) veya mikro aksiyon rozetlerinde kullanılabilir. Sayfa, kart listesi, tablo, panel, modal içeriği veya asenkron veri yüklenen hiçbir alanda spinner veya boş beyaz ekran KULLANILAMAZ.
2. **Empty State (Boş Durum):**
   - Henüz veri/kayıt yokken veya filtre sonucu boş döndüğünde donuk/beyaz ekran bırakılamaz.
   - Amaca uygun açıklayıcı ikon + net başlık + yönlendirici açıklama + birincil aksiyon CTA butonu (*"İlk Projeni Ekle"*, *"Filtreleri Temizle"*).
3. **Error State (Hata Durumu):**
   - Genel/kriptik hata kodları yerine; kullanıcı diliyle yazılmış inline hata mesajı, problemin net sebebi ve doğrudan çözüm sunan *"Yeniden Dene"* (Retry) aksiyonu.
4. **Action Feedback & Success (Teyit ve Başarı):**
   - Kullanıcının gerçekleştirdiği her kritik aksiyon (ekleme, silme, güncelleme) anında geri bildirim üretmelidir: net Toast bildirimi, animasyonlu onay veya listenin anında güncellenmesi (optimistic UI).

## 2.2.1 Zorunlu İskelet Ekran (Skeleton Screen UI) ve Kaset Yapısı Sözleşmesi (Mandatory Skeleton Screen Contract)

> 💡 **Temel İlke & Tanım:**  
> *"Skeleton screens UI (İskelet ekranlar), bir web sitesinde veya mobil uygulamada içerikler sunucudan yüklenirken gerçek verilerin yerine gösterilen, sayfanın genel yerleşimini (wireframe/kaset yapısını) taklit eden gri tonlu görsel taslaklardır."*  
> Bu kural kesinlikle uygulanan bir sistem anayasasıdır; **AI ajanları bu kuralı hiçbir koşulda atlayamaz.**

Bir bileşen veya sayfa için Skeleton screen tasarlanırken şu 5 mimari gereksinim eksiksiz sağlanmalıdır:

1. **Kaset / Wireframe Sadakati (Cassette Wireframe Fidelity):**
   - İskelet ekran, rastgele tek bir dev gri kutu veya generic dikdörtgen olamaz.
   - Nihai verinin yerleşeceği arayüzün kaset yapısını (avatar daireleri `rounded-full`, başlık çubukları, çok satırlı metinlerde değişken genişlikler örn. %100 - %85 - %60, kart çerçeveleri, buton şekilleri, tablo kolonları ve satırları) birebir taklit etmelidir.
2. **Sıfır Düzen Kayması (Zero Cumulative Layout Shift - Zero CLS):**
   - Gerçek veri API veya sunucudan gelip render edildiğinde sayfa elemanlarının sıçramaması veya aşağı/sağa kaymaması esastır.
   - İskelet elemanlarının yükseklikleri (`min-h-*`), genişlikleri, grid kolonları ve boşlukları (`gap-*`, `p-*`, `m-*`), yüklenecek nihai içerikle piksel ve oran seviyesinde tam eşleşmelidir.
3. **Zanaat Renk Standartları (Theme-Aware Semantic Tokens):**
   - İskelet renkleri sabit ham hex (`#cccccc`, `#e0e0e0`, `#333333`) OLAMAZ.
   - Daima projenin tasarım sistemi ve tema token'larını kullanmalıdır: `bg-muted` (Tailwind/shadcn), `bg-neutral-200 dark:bg-neutral-800` veya CSS değişkeni `hsl(var(--muted))`.
   - Açık modda yumuşak açık gri, koyu modda ise gözü yormayan derin mat yüzey tonlarında olmalıdır.
4. **Animasyon ve Hareket Zanaatı (Subtle Motion & a11y):**
   - İskelet yüzeylerine yumuşak bir nefes alma efekti (`animate-pulse`) veya hafif gradyan parıltısı (shimmer sweep) uygulanmalıdır.
   - Göz yoran, hızlı veya flaş patlaması yapan sert animasyonlar KESİNLİKLE YASAKTIR.
   - Erişilebilirlik kapsamında `motion-reduce:animate-none` kuralı desteklenmeli; kullanıcının hareket azaltma tercihinde nabız durdurulup statik kaset gösterilmelidir.
5. **Erişilebilirlik ve ARIA Sözleşmesi (Accessible Loading Attributes):**
   - İskelet kapsayıcısında ekran okuyucular için `aria-busy="true"` ve `aria-live="polite"` özellikleri tanımlanmalıdır.
   - Ekran okuyucu kullanıcıları için gizli metin (`<span className="sr-only">İçerik yükleniyor...</span>` veya `aria-label="Yükleniyor"`) bulunmalıdır.
   - İskeletin görsel sahte şekillerine (çizgiler, daireler) yardımcı teknolojilerin takılmaması için `aria-hidden="true"` verilmelidir.


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

## 2.6 Tasarım Zanaat Tabanı ve Kesin Yasaklar (Craft Floor & Strict Anti-Patterns)

Tüm web arayüzü, frontend bileşeni ve sayfa geliştirmelerinde "generic AI slop" çıktısını önlemek ve zanaat kalitesini garanti altına almak için aşağıdaki **Kesin Yasaklar** (Hard Refusals) ve **Zorunlu Çıktı Kontrolleri** (Craft Floor Verifications) tavizsiz uygulanır:

### A. Kesin Yasaklar ve Anti-Pattern Reddi (Hard Refusals)

1. **İç İçe Kart Yasağı (No Nested Cards):** Kart içine kart koymak şablon tembelliğidir ve KESİNLİKLE YASAKTIR. Hiyerarşi iç içe kutularla değil; düz zeminler, negatif alan veya ince ton adımlarıyla sağlanır. Birbirinin kopyası aynı boyutlu ikon+başlık+metin ızgaralarından kaçınılmalıdır.
2. **Başlık Üstü Süs Etiketi Yasağı (No Eyebrow/Kicker Labels):** Başlıkların üzerine konan minik, izli (tracked) büyük harfli etiketler veya `"FEATURE"`, `"WHY US"`, `"YENİ"` gibi süs hapları KESİNLİKLE YASAKTIR. Başlık kendi ağırlığını taşımalıdır; süs etiketleri silinmeli ve doğrudan başlık konuşturulmalıdır.
3. **Gradyan Metin Yasağı (No Gradient Text):** Metinlerde renk gradyanı (`bg-clip-text text-transparent`) yasaktır. Tipografik vurgu gradyandan değil; font ağırlığı (`font-weight`), boyutu (`font-size`) veya renk kontrastından gelir.
4. **Kalın Renkli Kenar Çizgisi Yasağı (No Side Stripe Borders > 1px):** Kartların, callout'ların veya alert kutularının soluna/sağına konulan 3-4px kalın renkli dikey şeritler (`border-l-4`) yasaktır.
5. **Sıfır-Blur Blok Gölgeler Yasağı (No Hard Offset Shadows):** Açıkça neobrutalist bir dünya tasarlanmıyorsa `box-shadow: 4px 4px 0` gibi sıfır-blur blok gölgeler yasaktır. Gölgeler her zaman yumuşak bir blur (`blur-md`, `blur-lg`) ve doğal bir offset taşımalıdır.
6. **Yükseltiyi (Elevation) Tek Şey Belirler:** Ya border ya gölge. Geniş yumuşak gölgenin altına 1px border koymak "hayalet kart" (ghost card) hatasıdır. Kart köşe yuvarlaklığı (`border-radius`) 12–16px (`rounded-xl` / `rounded-2xl`) aralığında kalır; tam yuvarlak haplar (pills) sadece minik rozet/kontroller içindir.
7. **Sistem Display Font Fallback Yasağı:** Karakterli bir display başlık yerine Impact, Arial Black gibi sistem fallback'lerini kullanmak yasaktır. Projeye özgü web fontları veya karakterli tipografi tercih edilmelidir.
8. **Emoji veya Ham Unicode ile İkon Yasağı (E8 - emoji-icon):** İkonlar rastgele emoji veya Unicode gliflerinden (`⚡`, `🚀`, `✔`, `🔲`, `🔍` vb.) ibaret olamaz. Arayüzde buton, menü, rozet veya kart içi ikon olarak inline emoji kullanılması KESİNLİKLE YASAKTIR. Tutarlı bir SVG ikon kütüphanesinden (Lucide, Heroicons vb.) tek bir çizgi kalınlığı ve stil ile gelmelidir. `check_design_slop.py` tarafından mekanik olarak engellenir.
9. **Klişe Hero-Metrik ve Dekoratif Göstergeler Yasağı:** Anlamsız hero-metrik şablonları (dev sayı + minik etiket + gradient), içerik yerine konan sahte sparkline'lar ve içi boş ilerleme halkaları yasaktır. İddia ve veriler gerçek ve dürüst olmalıdır.
10. **Refleks Modal Yasağı:** Kullanıcı akışını kesintiye uğratması gerekmeyen sıradan işlemler için ezbere modal/dialog açmak yerine yerinde (inline) açılma veya panel geçişi uygulanmalıdır.
11. **Uydurma Karalama SVG Yasağı (No Doodles/Sketchy SVGs):** `loose-sketch`, `doodle` veya `feTurbulence` gibi amatör karalama SVG'leri yasaktır. Vektör ya net geometridir (diyagram, ikon, shader, animasyonlu çizgi) ya da profesyonel illüstrasyondur.
12. **Hardcoded Renk ve Başıboş Stil Yasağı (E9 - hardcoded-palette):** HTML veya JSX içinde inline `style="color: #..."` gibi başıboş hex renkler kullanmak yasaktır. Renkler her zaman ölçülmüş token'lardan (`get_palette.py --id <num> --format css` veya CSS değişkenleri / Tailwind sınıfları) gelmelidir. `check_design_slop.py` tarafından mekanik olarak denetlenir.
13. **Yatay Scroll Slop'u Yasağı (W3 / A.13 - No Horizontal Scroll Slop):** Görev ve eylem alanlarında (navigasyon, komut şeridi, filtre çubuğu, etiketler veya sayfa gövdesinde) seçeneklere erişmek için yapay yatay kaydırma zorunluluğu (`overflow-x: auto; white-space: nowrap;`) oluşturulamaz. Bu durum tembelce tasarlanmış bir "AI slop" belirtisidir. Çözüm; gereksiz boşlukları azaltmak, responsive sarma (`flex-wrap: wrap`) uygulamak ve ikincil seçenekleri açılır bir komut paleti/popover veya gruplanmış bir kontrol altına almaktır. *İstisnalar:* Çok kolonlu geniş veri tabloları (`table`, `.table-card`, `.table-wrap`) ve kod/log blokları (`pre`, `code`, `.code-block`) doğası gereği geniş olduğu için yatay kaydırma gerekçesiyle korunur.
14. **Çerçevesiz Kategori Yığılması ve Mağara Modalları Yasağı (A.14 - No Unframed Floating Groups & No Cavernous Modals):** Çoklu kategori, grup veya etki alanı barındıran modal/popup panellerde kategorilerin çerçevesiz, arka plansız havada asılı bırakılması ve modalın içeriğin 2-3 katı genişliğe (ör. 1100px+) açılarak devasa asimetrik karanlık boşluklar yaratması kesinlikle yasaktır. Gruplar çerçevelenmeli ve modal boyutu içeriğin doğal ızgara genişliğiyle orantılı sınırlandırılmalıdır.
15. **Veri Yüklemede Jenerik Spinner ve Boş Ekran Kolaycılığı Yasağı (A.15 - No Data-Loading Spinners & Mandatory Skeleton Screens):** Bir web sitesinde veya mobil uygulamada içerikler (sayfa, görünüm, kart, liste, tablo, profil, istatistik) sunucudan/API'den yüklenirken gerçek verilerin yerine sayfanın genel yerleşimini (wireframe/kaset yapısını) taklit eden gri tonlu görsel taslakların (Skeleton screens UI) sunulması KESİNLİKLE ZORUNLUDUR. AI ajanları bu kuralı atlayamaz. Veri yükleme anında tüm sayfayı veya veri konteynerini bloklayan jenerik spinner veya donuk/boş ekran bırakılması KESİNLİKLE YASAKTIR. Spinner (dönen yükleme ikonu), YALNIZCA buton içi form gönderimlerinde (`isSubmitting`) veya küçük durum rozetlerinde kullanılabilir.

### B. Çıktı Üzerinde Zorunlu Zanaat Kontrolleri (Craft Floor Verifications)

1. **Kontrast ve Renkli Zeminlerde Tonlama (Contrast & Hue Tinting):** Gövde metni ve placeholder kontrastı ≥ 4.5:1, büyük metin ≥ 3:1 (WCAG AA). Renkli zeminlerdeki ikincil metinler asla saf gri yapılmaz; her zaman zeminin renginden türetilmiş tonlu renk (tinted hue) taşır. CSS tema değişkenleri arasındaki matematiksel kontrast oranı `python .agent/skills/musgoku/scripts/check_theme_contrast.py` kapısıyla deterministik olarak denetlenir. Koyu modda karanlık metin veya parlak modda aşırı soluk metin kalması kesin olarak engellenir.
2. **Boşluk ve Ritim Orantısı (Spacing Rhythm):** Sıkı gruplamalar, cömert ayırıcılar; bir başlığın üstündeki boşluk (`mt`) her zaman altındaki boşluktan (`mb`) daha fazladır.
3. **Tipografi Ölçüleri ve Denge (Typography Floor):** Gövde metni satır genişliği 65–75ch, display başlık max 6rem, harf aralığı (tracking) -0.04em'den daha sıkışık olamaz (ideal: -0.02em - -0.03em), başlıklar dengeli sarılmalıdır (`text-wrap: balance`). Taşma (`overflow`) kesinlikle çözülmelidir.
4. **Tarayıcı Yüzeylerinin Temalandırılması (Themed Browser Surfaces):** Sayfanın "hazır şablon mu yoksa özenle inşa edilmiş mi" olduğunu gösteren en güçlü sinyal tarayıcı varsayılanlarını tasarım paletiyle giydirmektir:
   - `::selection`: Seçim arka planı ve metin rengi token paletinden renk alır.
   - `caret-color`: Input imleç rengi vurgu rengiyle eşleşir.
   - `::-webkit-scrollbar` / `scrollbar-color`: Özel ince kaydırma çubuğu.
   - `focus-visible` & `outline-offset`: Özel odak halkaları (erişilebilir ve token uyumlu).
   - `font-variant-numeric: tabular-nums` (W1): Tablo, sayaç ve sayısal verilerde sabit genişlikli rakamlar.
   - `text-underline-offset`: Bağlantı alt çizgilerinde doğal mesafe (`underline-offset-4`).
5. **Dürüst ve Eyleme Dayalı Metinler (Material & Copy Honesty):** Butonlar ve kontroller yaptıkları eylemi net söyler ("Kaydet", "Projeyi Yayınla"); hatalar sorunun ne olduğunu ve çözümünü kullanıcı diliyle açıklar.
6. **İşlevsel Tamamlanma (Kural A — Complete Visible Interaction):** Kullanıcıya etkileşim vaat eden her kontrol (buton, sekme, filtre, görünüm seçici), açıkça tanımlı bir eylemi ve doğrulanabilir bir sonucu sağlamalıdır. Kontrolün görünümü, iç durumu (`aria-pressed`, `aria-selected`) ve ekranda ürettiği sonuç birbiriyle tutarlı olmalıdır. Boş handler, yalnızca console çıktısı, `href="#"`, sonucu etkilemeyen state değişikliği ve gerçek işlem yerine sahte başarı bildirimi teslim edilemez. Bir görünüm veya özellik desteklenmiyorsa o bağlamda yanıltıcı bir kontrol sunulamaz.
7. **Akıcı Responsive Kullanım (Kural C — Fluid Adaptive Layout):** Her tasarım mobil (320px–390px), tablet (768px–834px) ve masaüstü (1024px–1440px+) kullanımını desteklemelidir. Breakpoint'ler sabit piksel etiketlerine göre değil, sidebar/dock çıktıktan sonra ana içeriğe kalan net kullanılabilir alana göre akıcı hesaplanmalıdır (`minmax(min(100%, 320px), 1fr)`). Görünüm değişikliği kullanıcı girdisini, filtreyi veya seçili kaydı kaybettiremez; mobilde dar alanlarda off-canvas çekmece (`drawer`) ve en az 44 × 44 CSS px dokunma hedefleri sağlanmalıdır.
8. **Doğrulama Olmadan Tamamlandı Denilemez (Kural D — Real Interaction Proof):** Kritik kullanıcı akışları gerçek tarayıcı etkileşimleriyle (`chrome-devtools-mcp` ile tıklama, odak ve 0px yatay taşma ölçümü) kanıtlanmalıdır. Yalnızca statik tarama, hatasız derleme veya ekran görüntüsü tek başına işlevsellik kanıtı sayılmaz.
9. **Ölçeklenebilir Eylem Grupları ve Alttan Açılan Kart Paneli Standardı (Kural B.9 — Scalable Action Groups & Bottom-Sheet Card Hub):**
   Eylem, araç veya komut koleksiyonlarının tasarımında sistem şu soruyu sormak zorundadır: *"Burada 12 değil 100 öğe olsaydı ne olacaktı?"*. Tembelce onlarca butonu yan yana dizip ekranı boğmak veya yatay kaydırma çubuğuna (horizontal scroll slop) hapsetmek kesinlikle yasaktır.
   - **Drop-down Yasağı:** Çoklu eylem veya komut keşfinde native `<select>` veya sıkışık tek boyutlu dropdown listeler KESİNLİKLE KULLANILAMAZ ("drop&down mu kesinlikle hayır").
   - **İki Bağımsız Sunum Modu (Dual Modes):**
     * **Mod 1 (`panel-only`):** Tek bir anlamlı grup butonu (örn. `⚡ Oturum Komutları (12)`). Tıklandığında animasyonlu alttan açılan kart panelini doğrudan açar.
     * **Mod 2 (`preview-and-panel`):** Konteynerin kullanılabilir genişliğini dinamik hesaplar (`ResizeObserver` / layout hesabı). Ekrana sığan ilk N öğeyi önizleme çipi olarak gösterir; sığmayanları ise sağa eklenen `... (+K)` overflow butonu ile alttan açılan karta yönlendirir.
   - **Alttan Açılan Kart Paneli (Bottom-Sheet Card Hub):**
     * Ekranın altından animasyonla (`translateY(0)`, backdrop-filter blur) yükselir.
     * Ögeleri anlamsal alanlara (domain/kategori) göre gruplar; her alan tema uyumlu renkli rozet/kenarlık taşır.
     * **Eşit Boyutlu Kart Sözleşmesi (Equal Dimensions Card Contract):** Tüm kartlar eşit minimum yükseklik ve genişlik matrisinde (`grid-template-columns: repeat(auto-fill, minmax(260px, 1fr))`) yer alır; tek öğeli kategorilerde kart tüm satıra yayılmaz (`subgrid` veya tutarlı track).
     * **Erişilebilir Odak İadesi:** Panel `ESC` veya kapat butonuyla kapandığında klavye odağı paneli tetikleyen asıl butona (grup butonu veya `... (+K)` butonu) iade edilir.
10. **Modal ve Popup Panellerde Çerçeveli Kategori İzolasyonu, Orantılı Boyut ve Asimetri Koruması Sözleşmesi (Kural B.10 — Framed Section Containment, Proportional Sizing & Anti-Void Modal Contract):**
    Çoklu aksiyon, komut veya eylem koleksiyonu barındıran popup/sheet panellerinin tasarımında aşağıdaki üç ilke tavizsiz uygulanır:
    - **Orantılı Boyut Tavanı (Proportional Viewport Clamping):** Modal ve popup paneller içeriğin doğal ızgara genişliğine göre boyutlandırılmalı; masaüstünde `max-width: min(94vw, 780px)` (veya 800px) sınırında tutulmalıdır. Ekranda gereksiz devasa siyah boşluklar / mağara etkisi (cavernous empty void) yaratılması zanaat hatasıdır. Yükseklik içeriğe göre esnek olmalı, `max-height: min(80vh, 680px)` tavanında `overscroll-behavior: contain` taşımalıdır.
    - **Ayrı Gösterimlerin Çerçevelenmesi (Framed Category / Section Containment - Gestalt Common Region):** Farklı etki alanları (domain/kategori), filtre grupları veya alt koleksiyonlar havada başıboş bırakılamaz. Her alan açık bir çerçeve (`border: 1px solid var(--border-subtle)`, yüzey arka plan dolgusu `var(--bg-surface)`, `border-radius: var(--radius-md)`, iç padding `0.85rem–1rem`) içine alınarak görsel bir bütünlük sağlanmalıdır.
    - **Çerçeve İçi Konumlandırma ve Simetrik Izgara (Intra-Frame Alignment & Symmetrical Grid):** Çerçeve içinde üstte başlık şeridi (rozet, sayaç, başlık ve süptil ayırıcı çizgi), altta ise masaüstünde tam 2 simetrik kolondan (`grid-template-columns: repeat(2, 1fr)`) oluşan kart ızgarası yer almalıdır. Mobilde tek kolona (`1fr`) geçmelidir. Tek kartlı alanlar kontrolsüzce sağa doğru esneyemez; çerçevenin dengeli sol yarısında orantılı konumunu korur.

### C. Hazır Bileşen ve Ölçülmüş Palet Önceliği (Zero-Friction Ready-Made Lookup)

⛔ **Ezbere CSS/HTML Üretme Yasağı:** Modelin eğitim hafızasından uydurma ortalama 2023 grid'leri ve renkleri basmasını engellemek için, bir bileşen (sidebar, navbar, card, login, footer, accordion, menu) tasarlanırken veya renklendirilirken **önce** şu araçlar taranmak ZORUNDADIR:
1. **Hazır Bileşen Şablonları (55 Tema):** `python .agent/skills/frontend-design/scripts/get_component.py --list` veya `--theme <name> --html` ile doğrudan üretim kalitesindeki CSS/HTML referans alınır.
2. **Ölçülmüş Kontrastlı Paletler (10 Palet):** `python .agent/skills/frontend-design/scripts/get_palette.py --id <1-10> --format css` ile WCAG AA/AAA kontrastı garanti edilmiş CSS değişkenleri projeye aktarılır.
3. **Merkezi Tasarım Arama Motoru:** `python .agent/skills/ui-ux-pro-max/scripts/search.py "<query>"` araması, sorguya uyan yerel hazır bileşen ve paletleri otomatik olarak yüzeye çıkarır.

## 2.7 Dört Yüzey Modu Sözleşmesi (The 4 Surface Modes: Persuade, Operate, Read, Experience)

Tasarım başarısı tüm ekranlarda aynı görünmez. Bir landing page'in ihtiyacı olan cesur ve dramatik görsel dünya, bir admin paneline veya ayarlar ekranına zorla dayatılamaz. Ajan, üzerinde çalıştığı her arayüzün **Yüzey Modunu** (Surface Mode) belirlemek ve o modun disiplinine tavizsiz uymak zorundadır:

| Yüzey Modu | Hedef & Ziyaretçi Başarısı | Tipik Ekranlar | Tipografi & Renk Standardı | Hareket (Motion) & Yoğunluk |
|---|---|---|---|---|
| **`Persuade`** *(İkna Et)* | Ziyaretçi karar verir ve aksiyon alır; **tasarım ürünün kendisidir**. | Landing page, pazarlama, fiyatlandırma, ürün lansman sayfaları. | Karakterli display/body font eşleşmesi; zengin renk paleti ve yüksek kontrastlı vurgular. | Tek bir amaca yönelik etkileyici giriş animasyonu (authored moment); cömert negatif alan ve nefes alan bölümler. |
| **`Operate`** *(Çalıştır)* | Ziyaretçi bir iş/görev tamamlar. **Araç görevin arkasında kaybolmalıdır**. | Web app, dashboard, ayarlar (settings), veri tabloları, formlar, editörler. | **Tek bir Sans yazı tipi ailesi** (süs fontları ve devasa fluid başlıklar YASAKTIR); işlevsel durum renkleri (semantic tokens). | **Hızlı mikro geçişler (150–250ms)**; yavaş sayfa giriş koreografileri YASAKTIR; yüksek bilgi yoğunluğu (dense layout). |
| **`Read`** *(Anla / Oku)* | Ziyaretçi bilgiyi anlar ve öğrenir. **Okuma deneyimi odaklıdır**. | Dokümantasyon, teknik spec, kılavuzlar, yardım merkezi, changelog, blog. | Okuma konforu; 65–75ch satır genişliği; belirgin `h1-h6` hiyerarşisi; kod bloklarında net kontrast. | Statik, sakin ve dikkat dağıtmayan zemin; yapışkan içindekiler tablosu (sticky TOC). |
| **`Experience`** *(Deneyimle)* | Ziyaretçi eserin/içeriğin doğrudan içine girer; **arayüz geri çekilir**. | Portfolyolar, fotoğraf/sanat galerileri, multimedya vitrinleri. | Minimal ve geri planda tipografi; nötr ve eseri öne çıkaran zeminler. | Akıcı imersif geçişler; ilk ekrandan itibaren eseri öne çıkaran tam ekran kurgusu. |

### Operate Modunda "Product Slop" Yasakları
Admin panelleri, dashboard'lar veya uygulama arayüzlerinde (`Operate` modu):
1. **Süslü Başlık ve Display Font Yasağı:** Form etiketlerinde, tablo başlıklarında veya butonlarda dekoratif display fontları kullanılamaz; tek bir temiz kurumsal Sans-serif ailesi kullanılır.
2. **Yavaş Giriş Animasyonu Yasağı:** Kullanıcı her gün işini yapmak için girdiği ekranda bölümlerin tek tek süzülerek gelmesini (staggered fade-in) bekleyemez. Geçişler 150-250ms içinde anında gerçekleşir.
3. **Standart Kontrolleri Yeniden İcat Etme Yasağı:** Standart buton, input veya dropdown'ları "farklı görünmek adına" kullanışsız ve garip biçimlere sokmak yasaktır. Tutarlılık, gösterişten önce gelir.
4. **Ezbere Modal Açma Yasağı:** Görev kesinti gerektirmiyorsa modal açılmaz; inline genişleme veya yan çekmece (drawer) tercih edilir.

## 2.8 Çift Katmanlı Proje Belleği Standardı (PRODUCT.md vs DESIGN.md)

Frontend ve arayüz projelerinde tutarlılık, keyfi kararlarla değil çift katmanlı proje belleğiyle sağlanır. İki dosya proje kökünde yer alır ve rolleri kesin sınırlarla ayrılmıştır:

| Katman Dosyası | Rolü ve Niteliği | İçeriği | Kapsam Dışı / Yasak |
|---|---|---|---|
| **`PRODUCT.md`** | **Ürün Gerçeği (Product Truth):** Ürünün kimliği, kitlesi ve değişmez gerçekleri. | Platform, hedef kullanıcılar, ürünün varoluş amacı, pazardaki konumu, çalışma bağlamı, yetenekler, teknik ve operasyonel kısıtlar, marka taahhütleri ve ses tonu, eldeki doğrulanabilir kanıtlar (evidence on hand), ürün ilkeleri ve WCAG 2.1 AA erişilebilirlik standardı. | **CSS, renk kodları, tipografi boyutları, HTML/Tailwind sınıfları YASAKTIR.** Hayali müşteri referansları, şişirilmiş istatistikler ve kanıtlanmamış iddialar ASLA yazılamaz. |
| **`DESIGN.md`** | **Görsel Dünya & Tasarım Sözleşmesi (Visual World & Design Tokens):** Ürünün estetik kuzey yıldızı ve taşınabilir token kütüphanesi. | YAML Frontmatter'da taşınabilir token'lar (`colors`, `typography.scale`, `rounded`, `spacing`, `components`). Gövdede Kreatif Kuzey Yıldızı, Yüzey Modu (`Persuade`/`Operate`/`Read`/`Experience`), Bileşen Primitifleri Kiti, Renk/Zemin Kuralları, Tipografi Hiyerarşisi, Malzeme/Derinlik Kuralları, Tarayıcı Yüzeyleri (`::selection`, `caret-color`) ve Do/Do Not redline listesi. | Ürünün iş hedeflerini veya pazar stratejisini değiştirmeye kalkışmak yasaktır. |

### İyileştirme (Refinement) vs Yeniden Tasarım (Redesign) Semantiği
Ajan tasarım üzerinde çalışırken bu ayrımı kesinlikle gözetir:
### Baseline Çıkarma (Brownfield), İyileştirme (Refinement) ve Yeniden Tasarım (Redesign) Semantiği
Ajan tasarım üzerinde çalışırken bu üç modu kesinlikle gözetir:
0. **Mevcut Projelerde Baseline Çıkarma (`mode: baseline` — İlk Adım):**
   - Halihazırda çalışan bir arayüzü olan projede (`kalansure`, `ocai`, `FEProjectv1`, `bookmarkManagerProject` vb.) `<repo-kök>/DESIGN.md` henüz yoksa, ajan **mevcut tasarımı ve UI kodunu ASLA kendi başına değiştirmez**.
   - Önce projenin mevcut renkleri, fontları, yüzeyleri ve bileşenleri olduğu gibi analiz edilerek `DESIGN.md` (`mode: baseline`) olarak kayıt altına alınır.
   - Mevcut tasarımın değiştirilmesi yalnızca kullanıcı açıkça talep ettiğinde / zorladığında (`--redesign`, `[OVERDRIVE]`, `"tasarımı değiştir / yeniden tasarla"`) gerçekleşir.
1. **İyileştirme (Refinement - `[POLISH]`, `[AUDIT]`, `[HARDEN]`, `[DISTILL]`, `[CLARIFY]`):**
   - Hem `PRODUCT.md` hem de `DESIGN.md` korunur.
   - Mevcut tasarım diline, token'larına ve kreatif kuzey yıldızına sadık kalınarak cerrahi iyileştirmeler yapılır.
2. **Yeniden Tasarım (Redesign - `[OVERDRIVE]`, `[SHAPE]`, Yeni Konsept):**
   - **`PRODUCT.md` DOKUNULMAZDIR.** Ürünün varoluş amacı, hedef kitlesi ve kısıtları değişmez.
   - Mevcut `DESIGN.md` bir anti-referans kabul edilir; yeni bir görsel yön belirlenir ve `DESIGN.md` baştan yazılarak yeni token sözleşmesi ilan edilir.

Şablonlar proje başlatılırken kopyalanır:
- `.agent/templates/PRODUCT.template.md` → `<repo-kök>/PRODUCT.md`
- `.agent/templates/DESIGN.template.md` → `<repo-kök>/DESIGN.md`

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
| Kullanıcı onboarding ve ürün tanıtım turu (rehberli adımlar, coachmarks) | `onboarding-tour` |
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

`brand`, `slides`, `banner-design`, `design`, `doc-coauthoring`, `mock-asset-provider`, `onboarding-tour` üçlüye **dahil
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