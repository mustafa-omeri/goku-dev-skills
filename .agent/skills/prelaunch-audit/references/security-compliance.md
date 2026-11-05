# 20 Maddelik Uygulama Güvenliği ve OWASP Uyum Kılavuzu

Bu referans dokümanı, dijital ürünlerin canlıya alınmadan önce (`/prelaunch`) ve güvenlik denetimlerinde (`/check-security`) 20 maddelik güvenlik kontrol listesini OWASP Cheat Sheet standartlarına uygun olarak doğrulamak için kullanılır.

---

## 1. Secrets & Environment (Gizli Anahtarlar ve Ortam Değişkenleri)

### Madde 1: API Anahtarlarını Saklama (Hide my API keys)
- **Kural:** Kaynak kodda hiçbir canlı özel anahtar (`sk_live_*`, `AKIA*`, `ghp_*`, veritabanı şifresi) sabit string olarak yer alamaz.
- **Doğru Yol:** Anahtarlar sunucu tarafında ortam değişkeni (`process.env.STRIPE_SECRET`, `os.environ["AWS_SECRET_ACCESS_KEY"]`) olarak tutulur ve gizli anahtar yönetim servisleri (GCP Secret Manager, AWS Secrets Manager, Vault) ile enjekte edilir.

### Madde 2: Ortam Değişkenlerini Denetleme (Check my env variables)
- **Kural:** İstemci tarafı paketleyicilerine (`VITE_*`, `NEXT_PUBLIC_*`, `REACT_APP_*`) kesinlikle sunucu gizli anahtarları (`SERVICE_ROLE`, `SECRET_KEY`, veritabanı bağlantı URI'si) geçilemez.
- **Doğru Yol:** İstemciye yalnızca herkese açık genel anahtarlar (`anon_key`, `publishable_key`, `api_base_url`) geçirilir.

### Madde 15: Açıkta Kalan Dosyaları Temizleme (Check for exposed files)
- **Kural:** Web sunucusunun kök dizininde veya dağıtım klasöründe `.env`, `.env.local`, `.git/`, `*.pem`, `*.key`, `*.bak`, `*.sql` dosyaları bırakılamaz.
- **Doğru Yol:** `.gitignore` ve Docker `.dockerignore` dosyalarında bu uzantılar engellenir; sunucu yapılandırmasında gizli dosyalara erişim (`location ~ /\.` -> `deny all`) kapatılır.

### Madde 18: Git Geçmişinde Gizli Anahtar Taraması (Check git for leaked secrets)
- **Kural:** Git commit geçmişine veya staged dosyalara gizli anahtar commit edilemez.
- **Doğru Yol:** `gitleaks dir` veya `security_checker.py` pre-commit kancalarında çalıştırılır. Bir anahtar geçmişe girdiyse derhal invalidate/rotate edilir (yalnızca commit'i silmek yetmez).

---

## 2. Network, CORS & Headers (Ağ, CORS ve Güvenlik Başlıkları)

### Madde 10: CORS Ayarlarını Denetleme (Check my CORS settings)
- **Kural:** Kimlik doğrulama çerezleri (`credentials: true` / `Access-Control-Allow-Credentials: true`) kullanılırken kaynak asla joker karakter (`Access-Control-Allow-Origin: *`) veya rastgele yansıtılan (reflected) origin olamaz.
- **Doğru Yol:** İzin verilen güvenilir alan adları açıkça listelenir (`allow_origins = ["https://app.example.com", "https://admin.example.com"]`).

### Madde 11: Güvenlik Başlıklarını Ekleme (Add security headers)
OWASP HTTP Headers Cheat Sheet standartlarına uygun olarak sunucu yanıtlarına şu başlıklar eklenmelidir:
```http
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none';
```
*(Node.js uygulamalarında `helmet` middleware'i, Spring Boot'ta `HttpSecurity.headers()`, Next.js'te `next.config.js` headers dizisi kullanılır).*

### Madde 12: Debug Modunu Kapatma (Turn off debug mode)
- **Kural:** Canlı ortamda `DEBUG = True` (Django/Flask), `NODE_ENV=development` bırakılamaz; ayrıntılı hata yığın izleri (stack trace) kullanıcılara gösterilemez; `.map` sourcemap dosyaları public web-root'ta yayınlanamaz.
- **Doğru Yol:** `NODE_ENV=production` atanır; prod build'de sourcemap gizlenir (`sourcemap: false` veya `hidden`).

---

## 3. Sanitization & XSS (Girdi Temizleme ve XSS Koruması)

### Madde 6: Formları Temizleme ve Doğrulama (Sanitize my forms)
- **Kural:** Kullanıcı girdileri sunucu tarafında doğrulanmadan ve temizlenmeden iş mantığına alınamaz.
- **Doğru Yol:** Şema doğrulayıcılar (Zod, Joi, Bean Validation) ile sıkı tip, uzunluk ve karakter kümesi sınırları konur; HTML içerik kabul ediliyorsa `DOMPurify` veya `sanitize-html` ile temizlenir.

### Madde 7: XSS'e Karşı Koruma (Protect against XSS)
- **Kural:** React'te `dangerouslySetInnerHTML`, ham DOM manipülasyonunda `innerHTML = ...`, `eval()` veya `javascript:...` URL şemaları denetimsiz kullanılamaz.
- **Doğru Yol:** Güvenli textContent/innerText veya React'in yerleşik JSX kaçış mekanizmaları kullanılır.

---

## 4. Authentication, Access, Passwords & DB (Kimlik, Yetki, Parolalar ve DB)

### Madde 3 & Madde 4 & Madde 5: Admin Rotaları ve Yetkilendirme (Protect admin routes & proper auth)
- **Kural:** `/admin` veya yetki gerektiren API/sayfa rotaları yalnızca istemci tarafında gizlenemez; sunucu/Edge tarafında middleware (`AuthGuard`, `ProtectedRoute`, `@PreAuthorize`) ile token ve rol (RBAC) kontrolü zorunludur.
- **Doğru Yol:** Her istekte `auth.uid()` ve rol şeması sunucuda sorgulanır; parametrik nesne erişimlerinde (IDOR / BOLA) kaynak sahipliği doğrulanır.

### Madde 8: Hız Sınırlaması (Add rate limiting)
- **Kural:** Kimlik doğrulama (`/api/login`, `/api/register`, `/api/forgot-password`) ve genel form uç noktaları sınırsız isteğe açık bırakılamaz.
- **Doğru Yol:** IP ve hesap bazlı hız sınırlaması (`express-rate-limit`, Upstash Redis ratelimit, Cloudflare WAF kuralları) uygulanır.

### Madde 16: Veritabanını Güvene Alma (Secure my database)
- **Kural:** Ham SQL string birleştirmeleri (`SELECT * FROM users WHERE name = '` + name + `'`) kesinlikle yasaktır (SQL Injection). Supabase / PostgreSQL kullanılıyorsa RLS (Row Level Security) açık olmalıdır.
- **Doğru Yol:** Parametrik sorgular (Prepared Statements), ORM (Prisma, Hibernate, Drizzle) ve sıkı RLS politikaları kullanılır.

### Madde 17: Parolaları Doğru Hash'leme (Hash passwords properly)
- **Kural:** Parolalar ASLA düz metin (plaintext) veya zayıf algoritmalarla (MD5, SHA1, düz SHA256) saklanamaz.
- **Doğru Yol (OWASP Password Storage Cheat Sheet):**
  1. **Argon2id (Öncelikli):** Minimum 19 MiB bellek, 2 iterasyon, 1 derece paralellik (`argon2`).
  2. **bcrypt (Alternatif):** Work factor ≥ 10 (önerilen 12).
  3. **scrypt / PBKDF2 (Mevzuatsal zorunluluk varsa):** PBKDF2 HMAC-SHA256 ile en az 600.000 iterasyon.

---

## 5. Dependencies & Quality (Bağımlılıklar ve Denetim)

### Madde 13 & Madde 14: Bağımlılık Güncelliği ve Gereksiz Paketler (Dependencies & Unused packages)
- **Kural:** Bilinen kritik CVE güvenlik açığı (Critical/High Severity) bulunan paketler canlıya alınamaz.
- **Doğru Yol:** `pnpm audit` / `npm audit` / `pip audit` çalıştırılarak güvenlik açıkları onarılır; `knip` veya `depcheck` ile kullanılmayan ölü paketler temizlenir.

### Madde 19: Tam Güvenlik Denetimi (Run a full security audit)
- **Kural:** Canlıya alma öncesinde şüpheli durumlarda derin sızma testi ve zafiyet avcılığı disiplini işletilir.
- **Doğru Yol:** `.agent/skills/security-audit` yeteneği tam denetim modunda devreye sokulur.

### Madde 20: Sıfır Hata ve Kanıt Disiplini (Make no mistakes)
- **Kural:** Blocker seviyesinde tek bir bulgu dahi varsa prelaunch kararı **NO-GO** olmak zorundadır.
- **Doğru Yol:** Tüm bulgular `dosya:satır` kanıtıyla sunulur ve mekanik doğrulama kapıları (`security_checker.py`, `run_all_gates.py`) yeşile dönmeden canlıya onay verilmez.
