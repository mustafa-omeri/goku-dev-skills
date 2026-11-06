# Hibrit ve Çok Katmanlı (Polyglot) Dağıtım Kalıpları

Modern mimarilerde ön yüz (Frontend) ve arka yüz (Backend) genellikle farklı teknolojiler ve farklı altyapılar üzerinde barındırılır. Bu doküman, en sık karşılaşılan hibrit kombinasyonların dağıtım kurallarını tanımlar.

---

## 1. React / Vite (SPA) + Spring Boot (Java)

Bu modelde React statik varlıkları ve Spring Boot REST API'si yer alır. İki temel dağıtım yaklaşımı mevcuttur:

### Model A: Ayrık Alan Adı (Separate Subdomains — Önerilen)
- **Frontend:** Vercel veya Cloudflare Pages üzerinde `https://app.example.com`
- **Backend:** VPS / Docker üzerinde `https://api.example.com`

**Kritik Yapılandırmalar:**
1. **Spring Boot CORS Yapılandırması:**
   ```java
   @Configuration
   public class WebCorsConfig implements WebMvcConfigurer {
       @Override
       public void addCorsMappings(CorsRegistry registry) {
           registry.addMapping("/api/**")
                   .allowedOrigins("https://app.example.com")
                   .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                   .allowedHeaders("*")
                   .allowCredentials(true);
       }
   }
   ```
2. **Ortam Değişkeni (`.env.production`):**
   ```bash
   VITE_API_BASE_URL=https://api.example.com/api
   ```

### Model B: Tek Alan Adı ve Nginx Ters Proxy (Single Domain Unified)
- **Tek Alan Adı:** `https://example.com`
- **Nginx Rotalaması:**
  - `/*` -> React statik derleme klasörü (`/var/www/dist`)
  - `/api/*` -> Spring Boot backend portu (`http://127.0.0.1:8080`)

**Nginx Yapılandırması:**
```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # Frontend SPA
    root /var/www/html/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
*Bu modelde CORS yapılandırmasına gerek kalmaz çünkü tüm trafik aynı origin üzerinden akar.*

---

## 2. Next.js (SSR / Hybrid) + Python / FastAPI

- **Next.js:** Node.js runtime veya Vercel/Docker üzerinde (SSR için Node motoru gereklidir).
- **FastAPI:** Uvicorn / Gunicorn arkasında Docker container.
- **İletişim:** Next.js Server Components veya Route Handlers doğrudan iç ağdaki FastAPI portuna (`http://fastapi-service:8000`) erişebilir; böylece dış dünyaya API portunu açmadan güvenli iç ağ iletişimi (Private Network) kurulur.

---

## 3. Yönetilen Veritabanı (Supabase / RDS) Entegrasyonu

- Canlı ortamda veritabanı Docker içinde barındırılmıyorsa (harici managed DB ise):
  1. `DATABASE_URL` bağlantı dizesinde mutlaka `?sslmode=require` parametresi bulunmalıdır.
  2. Bağlantı havuzu (Connection Pooling - örn. PgBouncer veya Supabase port 6543) kullanılmalıdır.
  3. Güvenlik duvarında VPS'in sabit çıkış IP'si (Egress IP) veritabanı sağlayıcısının IP Allowlist'ine eklenmelidir.
