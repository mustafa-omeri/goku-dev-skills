# Dashboard Theme — Visual Reference Library

Bu klasör `frontend-design` skill'i için dashboard referans kütüphanesidir.
18 adet seçilmiş dashboard ekran görüntüsü içerir (`dashboard-theme-01.webp` → `dashboard-theme-18.webp`).

## Ne zaman kullan

Kullanıcı `dashboard` istediğinde (oluştur, düzenle, iyileştir, fikir ver):
1. Önce bu klasöre bak.
2. İsteğe en yakın 1-2 görseli seç.
3. Layout'u birebir kopyalama, desenleri al.

## Ortak desenler (bu 18 görselde)

- **Layout:** Sol sidebar + üst topbar + kart ızgarası. Sidebar dar, ikon + label.
- **Kartlar:** Beyaz zemin, büyük radius (16-24px), yumuşak gölge, bol padding.
- **Renk:** Açık gri zemin (`#F5F7FA` benzeri), koyu sidebar (`#2D2A4A` / siyah) + tek canlı vurgu (turuncu, mor, cyan).
- **Tipografi:** Başlık koyu ve kalın, gövde gri. Sayılar büyük ve net.
- **Bileşenler:** Haftalık takvim şeridi, istatistik kartları, progress halkaları, tablo + sağ detay paneli, avatar grupları.
- **OCAI uyarlaması:** Bu desenleri Tailwind + Shadcn UI ile kur. `Card`, `Table`, `Badge`, `Avatar`, `Progress` kullan. Dark mode (`dark:`) ekle. Tüm string'ler i18n ile.

## Nasıl uygula

1. Referans görseldeki ızgarayı çıkar (ör. 4'lü KPI kartı + 2'li grafik altı).
2. Renkleri `./themes/` kartlarından değil, bu dashboard'un vurgu renginden al.
3. `musgoku-styling-ui` kurallarına uy: `cn()`, semantic renk (`bg-primary`), mobile-first.
4. Recharts gerekiyorsa `ui-ux-pro-max --domain chart` ile grafik tipini seç.

## Dosya listesi

- `dashboard-theme-01.webp` — Temizlik / sistem durumu dashboard'u (turuncu hero, mor sidebar, haftalık rapor kartları)
- `dashboard-theme-02.webp` — Takım performans dashboard'u (3 KPI kartı, sıralama, tartışma grupları)
- `dashboard-theme-03.webp` … `dashboard-theme-18.webp` — Proje raporlama, destek talepleri, test sonuçları ve benzeri admin panel varyasyonları. İsteğe en yakın olanı görsel olarak seç.

Yeni görsel eklersen `dashboard-theme-19.webp` diye devam et, bu dosyaya bir satır ekle.
