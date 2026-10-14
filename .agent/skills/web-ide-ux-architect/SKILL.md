---
name: web-ide-ux-architect
description: >-
  IDE benzeri geliştirici arayüzleri tasarlar: kod editörü, terminal, ajan/asistan paneli,
  dosya ağacı, komut paleti, split pane. React ve Next.js tabanlı, düşük gecikmeli ve
  yüksek bilgi yoğunluğuna sahip arayüzler için mimari ve tasarım rehberi.
  Tetikleyiciler: "IDE arayüzü", "editör arayüzü", "kod editörü tasarımı", "split pane",
  "komut paleti", "monospace tema", "ide-like ui", "code editor ui", "command palette".
  Tetiklenmez: dashboard ve marketing sayfaları `frontend-design` ile
  `ui-ux-pro-max` kapsamındadır. Tam sözlük:
  .agent/rules/skill-trigger-routing.md
---

# Web IDE Arayüz Mimarisi

> Bu skill **IDE benzeri üretim araçları** tasarlar. Normal uygulama ekranları,
> dashboard'lar veya landing sayfaları için `frontend-design` +
> `ui-ux-pro-max` kullanılır.
>
> Bu skill hiçbir IDEye, editöre veya kodlama aracına bağlı değildir.
> Tek kural: çıktı **tarayıcı tabanlı bir uygulama** olarak çalışır.

## Tasarım düşüncesi

Koda dökmeden önce bağlamı anla ve net bir mühendislik vizyonu belirle:

- **Amaç:** Geliştiricinin kodla arasına girmeyen, zihinsel yükü azaltan bir
  çalışma alanı. Asistan ve agentic özellikler sonradan eklenmiş bir widget gibi
  durmamalı, akışın doğal parçası olmalı.
- **Ton:** İşlevsel fütürizm veya zarif endüstriyel. Görsel gürültüden arınmış,
  pürüzsüz karanlık tema, yüksek kontrastlı tipografi, odaklanmayı artıran his.
- **Kısıt:** Tarayıcı tabanlı bir uygulamada performans her şeydir. Karmaşık DOM
  ağaçlarında yeniden render'ı minimize et. Bekleyen yanıtlar için iyimser arayüz
  güncellemesi kullan.
- **Farkındalık:** Bu bir web sitesi değil, bir üretim aracı. Yerel sunucuda da
  konteyner içinde de çalışacak kadar izole, bulutla senkron olacak kadar esnek
  olmalı.

## Frontend ve Next.js yönergeleri

- **Yığın:** Next.js (App Router). React Server Component ve Client Component
  ayrımını bilinçli yap — etkileşimli paneller için Client, statik kabuk ve
  başlangıç verisi için Server. Amaç ilk yükleme süresini düşürmektir.
- **Tipografi:** Kod blokları ve terminal için karakteristik, okunabilir
  monospace font (JetBrains Mono, Fira Code, Cascadia Code vb.). Menü ve arayüz
  için temiz, modern, mümkünse daha özgün geometrik bir sans-serif.
- **Renk ve tema:** CSS değişkenleriyle katı tasarım sistemi. Derin siyahlar ve
  koyu griler; vurgu yalnız eylem gerektiren yerlerde. Göz yormaması esastır.
- **Hareket:** Animasyon gösteri için değil sistem durumunu bildirmek için.
  Uzun süren işlerde (derleme, kod tamamlama) kaynak tüketmeyen geri bildirim.
  Hareket kütüphaneleri yalnız panel boyutlandırma ve sürükle-bırak akıcılığı için.
- **Mekansal kompozisyon:** Modüler ve özelleştirilebilir düzenler (split-pane),
  esnek ızgara, daraltılabilir yan menüler, bol ama kontrollü negatif alan.
- **Yapay zekâ arayüzü:** Inline kod tamamlama hayalet metinleri, bağlama duyarlı
  sağ tık menüleri, kodun içinde beliren temiz istem alanı.

## ASLA yapılmaması gerekenler

- Ağır, yavaş yüklenen, gereksiz render döngülerine giren React bileşenleri
- Kurumsal SaaS paneli kalıbını kopyalayan, hazır admin şablonları
- Kontrastı düşük, göz yoran renk paletleri
- Her şeyi yeniden render eden durum yönetimi; ağır listelerde sanallaştırma
  (devasa log ya da kayıt listeleri bu kapsamdadır)

## Performans notu

Kod bir konteyner içinde, bir vekil sunucunun arkasında çalışabilir. İstemci
tarafı performans optimizasyonuna (sanal liste, bellek sınırı, ağır listelerde
sayfalama) en üst düzeyde önem ver.

## Kontrol listesi

- [ ] Component/Client ayrımı bilinçli mi?
- [ ] İlk yükleme yolu sunucu tarafında mı?
- [ ] Monospace ve arayüz fontu ayrımı yapılmış mı?
- [ ] Renkler CSS değişkeniyle tanımlanmış mı?
- [ ] Animasyon kaynak tüketmiyor mu?
- [ ] Ağır listeler sanallaştırılmış mı?
- [ ] Klavye odağı ve erişilebilirlik korunmuş mu?
