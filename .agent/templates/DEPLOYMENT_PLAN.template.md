# DEPLOYMENT_PLAN.md — Üretim Dağıtım ve Altyapı Planı

> Şablon. Kopyala, projenin `docs/deployment/DEPLOYMENT_PLAN.md` konumuna taşı ve doldur.
> Kural: `.agent/skills/deployment-architect/SKILL.md`
> Motor: `python .agent/skills/deployment-architect/scripts/deployment_generator.py`

**Proje:** <proje adı> · **Ortam:** Production · **Dağıtım Tipi:** <VPS / PaaS / Cloud Container / Hibrit>
**Alan Adı:** https://<alan-adi>
**Tarih:** <YYYY-MM-DD> · **Sorumlu:** <ad/ajan>

---

## 🏗️ Bölüm 1: Altyapı ve Çalışma Zamanı Mimarisi (Infrastructure & Runtime)

- **Sunucu / Platform:** <Ubuntu 22.04 LTS / Vercel / Railway / Cloud Run>
- **Port Haritası:**
  - Frontend: <Port / CDN Domain>
  - Backend API: <Port 8080 / 3000>
  - Veritabanı: <Port 5432 / Harici Managed>
- **Ters Proxy & SSL:** <Nginx Reverse Proxy + Let's Encrypt Certbot SSL>
- **Ağ İzolasyonu & Güvenlik Duvarı:** <UFW: 22, 80, 443 açık; iç portlar izole>

---

## 🔐 Bölüm 2: Üretim Konfigürasyon ve Secret Matrisi (Production Config & Secrets)

- `.env.production` dosyası asla versiyon kontrolüne (Git) eklenmez (`.gitignore` korumalı).
- Ortam değişkenleri `.env.production.template` üzerinden hazırlanır.

| Değişken Adı | Açıklama | Örnek / Format | Nereden Alınır |
|---|---|---|---|
| `NODE_ENV` | Çalışma modu | `production` | Sistem |
| `DATABASE_URL` | Veritabanı bağlantı dizesi | `postgresql://...` | DB Sağlayıcısı |
| `JWT_SECRET` | Token imzalama anahtarı | `64-karakterlik hex` | `openssl rand -hex 32` |
| `CORS_ORIGINS` | İzinli istemci domainleri | `https://app.example.com` | DNS / Frontend |

---

## 🗄️ Bölüm 3: Veritabanı Migration ve Sıfır Kesinti (Zero-Downtime) Stratejisi

1. **Pre-Deploy Hook (Önce Şema, Sonra Kod):**
   - Kod trafiğe çıkmadan önce migration komutu çalıştırılır: `<npm run db:migrate / prisma migrate deploy / liquibase update>`
2. **Geriye Dönük Uyumluluk (Expand-Contract):**
   - Yeni eklenen tüm kolonlar `NULLABLE` veya `DEFAULT` değerli olmalıdır.
3. **Dağıtım Öncesi Yedekleme:**
   - `<pg_dump -h host -U user -d dbname -Fc > /var/backups/pre-deploy.dump>`

---

## 🔄 Bölüm 4: Geri Alma ve Acil Durum Protokolü (Rollback Playbook)

Canlı ortamda beklenmeyen bir çökme yaşanırsa aşağıdaki adımlar tavizsiz işletilir:

### 1. Trafiği Kesme / Bakım Modu (Gerektiğinde)
- `touch /var/www/maintenance.flag` (503 Service Unavailable döner).

### 2. Uygulama Kodu Rollback
- **Konteyner / Docker:**
  ```bash
  docker compose -f docker-compose.prod.yml down
  export APP_TAG=v<onceki-stabil-surum>
  docker compose -f docker-compose.prod.yml up -d
  ```
- **Git / Systemd:**
  ```bash
  git checkout tags/v<onceki-stabil-surum>
  sudo systemctl restart app.service
  ```

### 3. Veritabanı Rollback
- Down-migration komutu çalıştırılır veya dağıtım öncesi alınan anlık yedek geri yüklenir.

---

## 🧪 Bölüm 5: Dağıtım Sonrası Doğrulama & Smoke Test (Health Check Playbook)

1. **Canlılık Kontrolü:**
   ```bash
   curl -Iv https://<alan-adi>/health
   ```
2. **SSL ve Güvenlik Başlıkları:**
   ```bash
   curl -s -D - https://<alan-adi> | grep -E 'X-Frame-Options|Strict-Transport-Security'
   ```
3. **Log İzleme:**
   ```bash
   docker compose logs -f --tail=100 | grep -i error
   ```
