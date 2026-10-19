# Product

<!-- product-truth-schema: 1 -->

## Platform

[Web / Desktop / Mobile / CLI / Extension / API]

## Users

[Hedef kullanıcı profili: Kimler kullanıyor, teknik/tasarım seviyeleri nedir, bu ürüne nereden geliyorlar ve çözmek istedikleri temel problem/acı noktası nedir? Ziyaretçilerin aradığı şey nedir?]

## Product Purpose

[Ürünün varoluş amacı: Ne işe yarar, hangi problemi çözer? Başarı nasıl ölçülür?
1. Birinci somut başarı metriği veya kullanıcı kazanımı.
2. İkinci somut başarı metriği veya kalite standardı.]

## Positioning

[Pazardaki konumu: Rakiplerinden, klasik çözümlerden veya jenerik alternatiflerden farkı nedir? Neyi kasıtlı olarak yapmaz, neyi ödünsüz savunur?]

## Operating Context

[Çalışma bağlamı: Kullanıcı ürünü nasıl devreye alır, günlük iş akışında bu arayüzle nasıl etkileşime girer? Geliştiriciler ve tasarımcılar projeyi nasıl günceller?]

## Capabilities and Constraints

- [Yetenek 1: Temel özellik veya modül.]
- [Yetenek 2: Belirgin işlevsel güç.]
- [Kısıt 1: Teknik sınır, desteklenen platformlar veya kasıtlı olarak kapsam dışı bırakılan alan.]
- [Kısıt 2: Kesin Kısıt: Kanıtlanmamış iddialar, uydurma müşteri referansları, sahte kıyaslamalar veya şişirilmiş istatistikler ASLA ürün metnine yazılamaz.]

## Brand Commitments

[Ton ve Karakter: Ürünün konuşma tarzı, ses tonu ve kişiliği.]

- Üç kelimelik kişilik: **[örn: uzman, kararlı, editoryal / sade, hızlı, güvenilir]**
- **Kaçınılacak Klişeler (Anti-Patterns):**
  - **Jenerik Pazarlama:** [Örn: Mor gradyanlar, cam efekti (glassmorphism), sahte parçacıklar, neon ışıklar.]
  - **SaaS Klişeleri:** [Örn: Dev hero metrik kartları, kopyala-yapıştır 3'lü özellik kutuları, "verimliliğinizi 10x artırın" gibi klişe metinler.]
  - **Kaçamak / Tereddütlü Dil:** [Örn: "olabilir", "belki düşünün", "deneyebilirsiniz". Ürün ne yaptığını bilir, net ve kararlıdır.]
  - **Aşırı Süsleme:** [Örn: İşlevi olmayan süs çizgileri, sahte SVG ikonlar ve gereksiz bezemeler yasaktır.]

## Evidence on Hand

[Diskte, depoda veya gerçek kullanıcı verilerinde doğrulanabilir mevcut kanıtlar:]
- [Doğrulanabilir kanıt 1: Örn: README dokümantasyonu, CLI araçları, API testleri.]
- [Doğrulanabilir kanıt 2: Örn: Kaynak kodda çalışan test paketleri, canlı demo ekranları.]
- [Doğrulanabilir kısıt: Henüz resmi müşteri referansı veya bağımsız kıyaslama çalışması yoksa, gelecekteki arayüz ve metinlerde ASLA hayali referans üretilemez.]

## Product Principles

1. **Önce Kanıt (Proof Over Claims):** Tasarım ve ürün kalitesini süslü iddialarla değil, çalışan arayüz ve somut sonuçlarla göster.
2. **Amaca Uygun Kısıtlama (Purposeful Restraint):** Her görsel ve işlevsel öğe yerini hak etmelidir. İşlevi olmayan süs yer alamaz.
3. **Uzman Kararlılığı (Expert Confidence):** Net, doğrudan, kaçamak yapmayan ve ustalığa dayanan bir yaklaşım sergile.
4. **İşlev Odaklılık (Function First):** Gösteriş aracı görevin arkasında bırakmalı, kullanıcının işini en az sürtünmeyle bitirmesini sağla.

## Accessibility & Inclusion

Temel Seviye: WCAG 2.1 AA (Tüm sayfalarda ve durumlarda).
- Renk kontrastı varsayımlarla değil, ölçüm araçlarıyla (min 4.5:1 normal metin, 3:1 büyük metin/kontroller) doğrulanmalıdır.
- Tüm etkileşimli kontroller klavye ile erişilebilir olmalı ve görünür `focus-visible` taşımalıdır.
- `prefers-reduced-motion` her animasyon ve geçişte eksiksiz uygulanmalıdır.
- Semantik HTML (`button`, `a`, `main`, `nav`, `h1-h6`) esastır; ARIA eksik semantiğin yaması olarak değil, yalnızca ek zenginleştirme için kullanılır.
