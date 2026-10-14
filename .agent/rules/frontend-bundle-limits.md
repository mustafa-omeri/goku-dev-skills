---
name: Frontend Bundle Limits
description: Frontend projelerinde chunk boyutu, ağır kütüphane ve toplam bundle bütçesinin aşılmamasını zorunlu kılar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Frontend / bundle bütçesi"
    komut: "npm run build"
---

# ⛔ Bundle ve Chunk Bütçesi Kuralı (Frontend projelerinde zorunlu)

> Bu kural **yalnız frontend projesinde** geçerlidir. Backend projelerinde uygulanmaz.

## Neden

Tarayıcı indirilen her kilobit için bekler. Büyük tek chunk ilk yüklemeyi
yavaşlatır, mobil bağlantıda kullanıcıyı kaybettirir ve sonradan çözülmesi pahalıdır.

## Bütçe

| Ölçüt | Sınır | Nasıl ölçülür |
|---|---|---|
| Tek chunk (lazy olmayan başlangıç paketi) | gzip sonrası **≤ 200 KB** | Build çıktısı boyut listesi |
| Tek chunk (lazy yüklenen sayfa/kütüphane) | gzip sonrası **≤ 500 KB** | Aynı |
| Toplam ilk yükleme JS | gzip sonrası **≤ 600 KB** | Aynı |
| Tek bir dosya (component/hook) | **≤ 200 satır** | Satır sayımı |
| Toplam build süresi | Mevcut değerin **2 katını geçmemeli** | Süre karşılaştırması |

Proje kendi bütçesini tanımlıyorsa (ör. `vite.config.js` içinde `chunkSizeWarningLimit`,
CI'da bundle kontrolü) **projenin değeri geçerlidir**; bu tablodaki varsayılan
yalnız tanım yoksa uygulanır.

## Zorunlu kurallar

1. **Kod bölme varsayılandır.** Route veya ağır bileşen bazında `React.lazy()`
   + `Suspense` kullan; ana girişte (`main.tsx` / `index`) yalnız kabuk yükle.
2. **Ağır kütüphaneleri ayrı chunk'a al.** Grafik, tablo, editör, tarih
   seçici, harita, PDF görüntüleyici gibi modüller route bazında lazy import edilir.
3. **Tek satırlık `import` zinciri kurma.** `index.ts` üzerinden dışa aktarma
   zinciri kurmak, ağacın tamamını başlangıç paketine sokar.
4. **Vendor ayrımı anlamlıysa kullan.** Tek bir dev vendor chunk, "her şey
   büyük" demektir; gerçekten ayrılan kütüphaneleri ayır.
5. **Ölç.** "Bundle büyüdü mü" tahminle değil, build çıktısıyla cevaplanır.
   Build çıktısını yanıtta gerçek boyutlarla göster.

## Doğrulama ve Atlanamaz Kapı (Non-Bypassable Gate)

⛔ **Bu kapı atlanamaz:** Frontend projelerinde `npm run build` (veya `pnpm build`)
çalıştırılmadan ve terminal çıktısındaki chunk boyutları bizzat okunmadan iş "bitti"
ilan edilemez.

| Ne | Zorunlu İşlem |
|---|---|
| Boyut listesi | Build çıktısındaki chunk kB değerleri terminalden bizzat okunur |
| Chunk uyarısı | Vite'ın `chunkSizeWarningLimit` (>500 kB) sarı uyarısı **test hatası (FAIL)** sayılır, düzeltilmeden geçilemez |
| Rapor zorunluluğu | En büyük 3 chunk boyutu (Entry, Vendor, Dynamic) `HANDOFF.md` ve oturum raporunda kB olarak listelenir |
| Ayrıntılı analiz | `vite build --mode analyze` ya da bundle analyzer eklenmişse rapor açılır |
| Bütçe kontrolü | CI/CD bundle kontrol adımı varsa çalıştırılır |

> ⛔ **Soyut beyan yasaktır:** "Build başarılı, boyutlar uygun" ifadesi geçersizdir.
> Gerçekte ölçülen kB değerleri (ör. `index-xyz.js: 142 kB (gzip: 44 kB)`) yazılmalıdır.

## Sınır

- Analiz aracı projede yoksa **yeni paket eklemek zorunlu değildir.** Mevcut
  Vite derleme çıktısındaki satırları okumak yeterlidir.
- Kütüphane kaldırmak breaking change ise kullanıcıya sor; kararı
  `knowledge-base.md`'ye yaz.

## Aşım Durumunda Çözüm Hiyerarşisi

Aşım veya Vite chunk uyarısı tespit edildiğinde öncelik sırası:

1. **Kullanılmayan import ve bağımlılık taraması:** `npx tsc --noEmit` ve tree-shaking denetimi.
2. **Route bazlı kod bölme:** Tüm sayfa bileşenlerinde `React.lazy()` + `<Suspense>`.
3. **Ağır kütüphane dinamik import'u:** Grafik, editör, PDF, tarih seçici gibi araçları yalnızca kullanıldıkları yerde `import()` et.
4. **Rollup `manualChunks` optimizasyonu:** `vite.config.ts` içinde dev vendor paketini anlamlı parçalara (`vendor-react`, `vendor-ui`, `vendor-utils` vb.) ayır.
5. **Daha hafif alternatif:** Kullanıcı onayıyla ağır kütüphaneyi hafif alternatifiyle değiştir.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir istisna veya ek bundle bütçesi kuralı gerekirse (ör. özel chunkSizeWarningLimit), önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_