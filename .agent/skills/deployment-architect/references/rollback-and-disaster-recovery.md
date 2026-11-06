# Geri Alma ve Acil Durum Kurtarma Protokolü (Rollback & Disaster Recovery)

Canlıya geçiş (deployment) sırasında veya hemen ardından beklenmeyen bir kaza (çökme, 500 hataları, veri bozulması, bellek tükenmesi) yaşandığında panik yapmadan sistemi stabil hale getiren deterministik eylem kılavuzudur.

---

## 1. Altın Kural: Expand-Contract Veritabanı Şeması

Yazılım sürümleri geri alınabilir; ancak canlıda veri yazılmaya başladıktan sonra veritabanını geri almak veri kaybına yol açabilir. Bu yüzden veritabanı değişiklikleri daima **Expand-Contract (Genişlet-Küçült)** prensibine uymalıdır:

1. **Aşama 1 (Expand - Genişletme):**
   - Yeni kolonlar daima `NULLABLE` veya `DEFAULT` değerli olarak eklenir.
   - Eski kod çalışırken yeni kolonları bilmese bile veritabanına yazmaya devam edebilir.
   - Kod yayınlanır ve doğrulanır.
2. **Aşama 2 (Geçiş):**
   - Kod artık yeni kolonu kullanmaya başlar.
3. **Aşama 3 (Contract - Küçültme):**
   - Bir sonraki sürümde eski/kullanılmayan kolon silinir veya `NOT NULL` kısıtı eklenir.

> **Sonuç:** Kod önceki sürüme geri alındığında (rollback) veritabanı şeması eski kodla %100 uyumlu kalır ve çökme yaşanmaz.

---

## 2. Acil Durum Bakım Modu (503 Service Unavailable)

Sistem kritik bir hata veriyorsa, kullanıcıların yarım işlem yapmasını veya bozuk veri kaydetmesini önlemek için derhal bakım moduna geçilir:

```bash
# Nginx bakım modunu aç:
touch /var/www/maintenance.flag

# Nginx bakım modunu kapat (işlem bitince):
rm /var/www/maintenance.flag
```

**Nginx Yapılandırması:**
```nginx
# Bakım modu kontrolü
if (-f /var/www/maintenance.flag) {
    return 503;
}
error_page 503 @maintenance;
location @maintenance {
    root /var/www/html;
    rewrite ^(.*)$ /maintenance.html break;
}
```

---

## 3. Kod ve Konteyner Geri Alma Adımları

### Docker & Docker Compose:
```bash
# 1. Önceki çalışan stabil imaj etiketini belirle (örn. v1.25.0)
docker compose -f docker-compose.prod.yml down

# 2. Önceki imajla servisi ayağa kaldır
export APP_TAG=v1.25.0
docker compose -f docker-compose.prod.yml up -d

# 3. Canlı logları doğrula
docker compose -f docker-compose.prod.yml logs -f --tail=50
```

### Git & Systemd:
```bash
# 1. Önceki etiketli stabil sürüme geç
cd /var/www/app
git fetch --tags
git checkout tags/v1.25.0

# 2. Servisi yeniden başlat
sudo systemctl restart app.service

# 3. Durumu ve logları denetle
sudo systemctl status app.service
journalctl -u app.service -n 50 --no-pager
```

---

## 4. Veritabanı Down-Migration ve Snapshot Geri Yükleme

Eğer migration veritabanını bozduysa ve geri almak şartsa:

1. **Down-Migration:**
   - Migration aracının rollback komutu çalıştırılır:
     - Prisma: `npx prisma migrate resolve --rolled-back <migration-name>`
     - Liquibase: `mvn liquibase:rollback -Dliquibase.rollbackCount=1`
     - Flyway: Flyway undo komutu veya manuel `down.sql`.
2. **Snapshot / Yedekten Geri Yükleme (Felaket Durumu):**
   - Dağıtım öncesinde alınan snapshot (`/var/backups/db-pre-deploy-<tarih>.sql`) geri yüklenir:
     ```bash
     psql -U appuser -d appdb -f /var/backups/db-pre-deploy-<tarih>.sql
     ```
