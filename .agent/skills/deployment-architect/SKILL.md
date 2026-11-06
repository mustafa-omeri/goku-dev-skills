---
name: deployment-architect
description: >-
  Üretim ortamı dağıtım ve altyapı orkestratörü; VPS, PaaS, Cloud Container ve hibrit mimariler (React + Spring Boot vb.) için Nginx, SSL, .env.production, DB migration pre-deploy hook ve acil durum rollback playbook içeren 5 katmanlı DEPLOYMENT_PLAN.md üretir. Tetikleyiciler: "/deploy-plan", "deployment planı", "vps kurulumu", "prod config hazırla", "rollback planı", "hibrit dağıtım", "deploy plan". Tetiklenmez: salt imaj küçültme `production-docker-architect`'e, kod release `git-release-workflow`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Dağıtım ve Altyapı Mimarı (Deployment Architect)

Bu yetenek, bir yazılım projesinin canlıya (production) çıkış aşamasında; hedef altyapı arketipini (VPS, PaaS, Cloud Container veya Hibrit/Çok Katmanlı) belirleyerek eksiksiz ve güvenli bir **5 Katmanlı Üretime Geçiş Planı (`docs/deployment/DEPLOYMENT_PLAN.md`)** hazırlar.

Projeister tek bir monolit (Node.js, Python, Java) olsun, ister ayrık bir hibrit mimari (örneğin React.js Frontend + Spring Boot Backend + Supabase/PostgreSQL) olsun; ters proxy, SSL, ortam değişkenleri güvenliği, veritabanı migration'ı ve acil durum geri alma (Rollback) adımlarını deterministik bir reçeteye dönüştürür.

---

## Ne Zaman Kullanılır?

- Kullanıcı `"/deploy-plan"`, *"deployment planı çıkar"*, *"vps kurulumu"*, *"prod config hazırla"*, *"rollback planı"* veya *"hibrit dağıtım"* dediğinde.
- [`prelaunch`](../prelaunch/SKILL.md) / [`prelaunch-audit`](../prelaunch-audit/SKILL.md) denetimi tamamlanıp **`GO`** kararı verildiğinde, canlıya alma köprüsü olarak.
- Projenin `.env.production.template`, Nginx ters proxy veya Docker Compose canlı ortam yapılandırmaları oluşturulurken.

---

## Çift Giriş Modu (Dual Input Mode)

Kullanıcının tercihine göre iki farklı yöntemle çalışabilir:

### Mod 1: İnteraktif Adım Adım Seçim (Interactive Mode)
Ajan proje kod tabanını (`package.json`, `pom.xml`, `requirements.txt` vb.) tarayarak mimariyi sezer ve kullanıcıya yöneltilen adımlarla hedefi netleştirir:
1. **Frontend Katmanı:** Nerede çalışacak? (Vercel / Cloudflare Pages / VPS Nginx / Docker)
2. **Backend Katmanı:** Nerede çalışacak? (VPS Docker-Compose / Ubuntu Systemd / Cloud Run / Railway)
3. **Veritabanı Katmanı:** Nerede barınacak? (Yönetilen Supabase/RDS / VPS Local PostgreSQL)
4. **Alan Adı & SSL:** Canlı domain nedir? (örn. `app.example.com` ve `api.example.com`)

### Mod 2: Deklaratif Şablon Modu (`DEPLOYMENT_TARGET.yaml`)
Kullanıcı dilerse projesinin kök dizininde veya `docs/deployment/` altında [.agent/templates/DEPLOYMENT_TARGET.template.yaml](../../templates/DEPLOYMENT_TARGET.template.yaml) şablonunu doldurur ve ajan doğrudan tek komutla çalışır:
```powershell
python .agent/skills/deployment-architect/scripts/deployment_generator.py --target-file docs/deployment/target.yaml
```

---

## 5 Katmanlı Standart Dağıtım Mimarisi (`DEPLOYMENT_PLAN.md`)

Üretilen her planda şu 5 zorunlu katman bulunur:

1. **🏗️ 1. Altyapı ve Çalışma Zamanı Mimarisi (Infrastructure & Runtime):**
   - Sunucu / PaaS gereksinimleri (CPU, RAM, OS).
   - Port tahsisleri ve ağ izolasyonu (`internal network`).
   - Ters proxy (Nginx/Caddy) ve Let's Encrypt SSL konfigürasyonu.
   - Hibrit projelerde CORS izinleri ve URL rotalama (`/api/*` -> Backend, `/*` -> Frontend SPA).
2. **🔐 2. Üretim Konfigürasyon ve Secret Matrisi (Production Config & Secrets):**
   - `.env.production` şablonu (`.env.production.template`).
   - Hassas anahtarların (JWT, DB URL, API Key) güvenli saklanması ve sızıntı kalkanı.
3. **🗄️ 3. Veritabanı Migration ve Sıfır Kesinti (Zero-Downtime) Stratejisi:**
   - Pre-deploy migration çalıştırma sırası (önce şema, sonra kod).
   - Geriye dönük uyumluluk: **Expand-Contract (Genişlet-Küçült)** şema kuralı.
   - Otomatik anlık snapshot veya `pg_dump` yedekleme komutu.
4. **🔄 4. Geri Alma ve Acil Durum Protokolü (Rollback Playbook):**
   - **Kod Rollback:** Önceki stabil Docker imajına veya git tag'ine dönüş (`docker compose rollback` / `git checkout vX.Y.Z`).
   - **Veritabanı Rollback:** Down-migration veya anlık snapshot'tan veri kaybı olmaksızın geri dönüş.
   - **Bakım Modu (503):** Nginx üzerinden anında bakım sayfası bayrağı (`maintenance.flag`).
5. **🧪 5. Dağıtım Sonrası Doğrulama & Smoke Test (Health Check):**
   - HTTP 200 canlılık pingleme (`curl -Iv https://domain/health`).
   - SSL sertifika ve güvenlik başlıkları (HSTS, CSP, X-Frame-Options) kontrolü.
   - Canlı log izleme komutu (`docker compose logs -f --tail=100` / `journalctl`).

---

## Detaylı Referanslar

- [Hibrit Dağıtım Kalıpları (React + Spring Boot vb.)](references/hybrid-deployment-patterns.md)
- [Geri Alma ve Acil Durum Kurtarma Protokolü (Rollback)](references/rollback-and-disaster-recovery.md)
- [VPS Üretim Sertleştirme ve Güvenlik Rehberi](references/vps-hardening-playbook.md)
