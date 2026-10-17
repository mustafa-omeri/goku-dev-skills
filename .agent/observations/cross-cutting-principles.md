# Cross-Cutting Principles

## P1: Uçtan Uca Veri Yaşam Döngüsü ve Döngü Kapanışı (Producer-Consumer Loop Closure)
Bir özellik veri üretiyorsa, o verinin tüketileceği veya karşılanacağı operasyonel akış (admin paneli, moderasyon masası, webhook vb.) planlanmadan ve veri saklama katmanı (DB & RLS) doğrulanmadan özellik tamamlanmış sayılamaz.

## P2: Sessiz Mock Yasağı (No Silent Mocking)
Ajanlar backend/DB gerektiren özellikleri gizlice localStorage veya in-memory state arkasında simüle edip "tamamlandı" diyemez. Prototip ise açıkça `// TODO: MOCK`, ekranda demo uyarısı ve planda "Mock Prototip" olarak beyan edilmelidir.

## P3: 3 Katmanlı Doğrulama Standardı (Three-Layer Verification)
Veri toplayan sistemlerde kabul testi 3 katmanlı kanıt sunmalıdır:
1. Görsel UX (Toast/UI temizliği)
2. Ağ İletimi (F12 Network HTTP 201/200 ve payload)
3. Veritabanı Kalıcılığı (SQL sorgusu veya admin ekranında yeni kayıt)

## P4: Kapsam-Duyarlı Doğrulama (Scope-Aware Verification)
Bir commit veya görevde yalnızca ajan kuralları (`.agent/**`) veya dokümanlar (`*.md`, `docs/**`) değiştiyse, uygulama derleme (`build`) ve test (`test`, `typecheck`) komutları çalıştırılmaz (atlanır / skipped). Kaynak kod değişmemişken test koşturmak israftır. Kapılar yalnızca ilgili etki alanı değiştiğinde zorunludur.

## P5: Adaptif Viewport ve UX Ergonomisi İlkliği (Adaptive Viewport & UX Ergonomics First)
Tasarım sadece masaüstünde başlayıp dar ekranda tek sütuna büzüşen statik bir görüntü değildir. Mobil (< 768px: Thumb Zone, Bottom Sheet/Drawer, min 44×44px touch, kart listesi), Tablet (768px–1024px: 2 sütunlu grid, split-view, dokunmatik alanlar) ve Masaüstü (> 1024px: multi-column, dialog) ergonomisi kullanıcı talep etmeden varsayılan refleks olarak uygulanır. Masaüstündeki bir modal mobilde asla ortalanmış küçük pencere olarak kalamaz; alttan açılan Bottom Sheet (Drawer) veya tam ekrana dönüşür. Her arayüz 4 UX durumunu (Loading, Empty, Error, Feedback) eksiksiz sağlamak zorundadır.

