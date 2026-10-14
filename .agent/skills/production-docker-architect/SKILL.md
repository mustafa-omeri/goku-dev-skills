---
name: production-docker-architect
description: Üretim ortamı için optimize edilmiş, güvenli ve hafif Docker imajları ve Docker Compose mimarileri tasarlar: multi-stage build, katman önbellekleme, non-root kullanıcı, zero-trust güvenlik prensipleri. Tetikleyiciler: "dockerfile", "docker compose", "imaj boyutu", "prod imajı", "containerize", "production image", "multi-stage build". Tetiklenmez: CI/CD ve release adımları `git-release-workflow`'e aittir. Tam sözlük: `.agent/rules/skill-trigger-routing.md`
license: Complete terms in LICENSE.txt
---

Bu yetenek (skill), uygulamaların konteynerleştirme (Dockerize) süreçlerini sıradan "hazır şablon" mantığından çıkarıp; kaynak tüketimi minimum, imaj boyutu optimize ve güvenlik açıkları kapatılmış üretim standardına taşımak için rehberlik eder.

Kullanıcı bir Dockerfile, .dockerignore, docker-compose.yml veya bir uygulamanın (Next.js, Spring Boot, Node.js, Python vb.) container mimarisini kurgulamanızı istediğinde bu yeteneği kullanın.

## Konteyner Mimarisi ve Stratejik Düşünce (Container Thinking)

Dockerfile veya Compose dosyası yazmaya başlamadan önce sistem mimarisini şu üç temel sütun üzerinde kurgulayın:

- **Hafiflik ve Hız (Minimalism & Speed)**: Derleme (build) sürelerini kısaltmak için Docker katman önbelleklemesini (layer caching) maksimum verimle kullanın. Çalışma zamanı (runtime) imajlarında gereksiz paketleri (build-essential, curl, git vb.) temizleyin. Alpine veya Distroless tabanlı imajları tercih edin.
- **Güvenlik (Zero-Trust Containerization)**: Konteynerler asla `root` kullanıcısı ile çalıştırılmamalıdır. Her zaman özel bir sistem kullanıcısı (`USER node`, `USER appuser` vb.) tanımlayın. Hassas verileri (API anahtarları, DB şifreleri) imajın içine gömmeyin; çevre değişkenleri (environment variables) veya Docker Secrets ile yönetin.
- **Taşınabilirlik ve Ölçeklenebilirlik**: Konteynerler geçici (ephemeral) olmalıdır. Durum bilgisi (state) konteyner içinde tutulmamalı, kalıcı veriler hacimler (volumes) ile dışarıya taşınmalıdır. Port yapılandırmaları ve ağ (network) izolasyonları net olmalıdır.

## Dockerize ve Yapılandırma Yönergeleri

Odaklanmanız gereken teknik detaylar:

### 1. Dockerfile Standardı (Multi-Stage Build)

- **Aşamalı Derleme**: Derleme araçlarını (build tools) ve bağımlılık indirme süreçlerini ilk aşamada (`BUILD stage`) çözün. Son üretim imajına (`RUN stage`) sadece çalıştırılabilir dosyaları (örneğin Next.js standalone klasörü veya Spring Boot .jar dosyası) taşıyın.
- **Katman Önbellekleme**: Kaynak kod kopyalanmadan önce _sadece_ bağımlılık yönetim dosyalarını (`package.json`, `pom.xml`, `go.mod`) kopyalayın ve bağımlılıkları yükleyin. Böylece kod değişikliklerinde tüm paketler tekrar indirilmez.
- **Temel İmaj Seçimi**: Rastgele `latest` etiketleri kullanmayın. Her zaman spesifik versiyonlar belirleyin (ör. `node:<sürüm>-alpine`, `eclipse-temurin:<sürüm>-jre-alpine`). **Sürüm seçimi:** yalnız **desteklenen (LTS)** ana sürümleri kullanın; EOL olmuş sürümler güvenlik açığı bırakır. EOL sürüm imajıyla karşılaşırsanız güncel LTS sürümüne geçin ve gerekçeyi `knowledge-base.md`'ye yazın. (Örnek: Node 20 EOL — Mart 2026.) Hangisinin LTS olduğunu tahmin etmeyin, doğrulayın.

### 2. .dockerignore Yönetimi

- Proje kök dizinindeki `.git`, `node_modules`, `.next`, `target`, `build`, `.env` gibi yerel geliştirme kalıntılarını ve hassas dosyaları kesinlikle imaj bağlamının (build context) dışında bırakın. Bu, build performansını doğrudan artırır.

### 3. Docker Compose ve Canlı Ortam Mimari Mimarisi

- **Servis İzolasyonu**: Veritabanı, önbellek (Redis) ve uygulama katmanlarını aynı iç ağda (`internal network`) toplayın. Dış dünyaya sadece reverse proxy (Nginx, Caddy vb.) veya API Gateway portunu açın.
- **Restart Politikaları**: Canlı ortamda çökmelere karşı koruma sağlamak için servisler için `restart: unless-stopped` veya `always` politikalarını tanımlayın.
- **Kaynak Sınırlandırması (Resource Limits)**: Tek bir konteynerin tüm VPS kaynaklarını tüketmesini engellemek için CPU ve RAM limitleri (`mem_limit`, `cpus`) koyun.

## ASLA YAPILMAMASI GEREKENLER (Anti-Patterns)

- İmajın içinde `apt-get upgrade` çalıştırmak veya üretim imajında `npm install` (devDependencies dahil) bırakmak.
- Dockerfile içinde gizli anahtarları (`ENV DB_PASSWORD=12345`) açık metin olarak yazmak.
- Logları container içindeki dosyalara yazmak. Loglar her zaman standart çıktıya (`stdout` / `stderr`) basılmalı, log rotasyonu (log rotation) Docker daemon seviyesinde veya bir volume ile yönetilmelidir.
- Geliştirme (development) ve Üretim (production) bağımlılıklarını tek bir katmanda birleştirmek.

**ÖNEMLİ**: Yazdığınız her Docker yapılandırması CI/CD hatlarında (GitHub Actions, GitLab CI vb.) sorunsuz çalışacak, bulut sunucularında veya yerel Docker cluster'larında (Swarm/K8s hazır) en optimize kaynak tüketimiyle ayağa kalkacak nitelikte olmalıdır.
