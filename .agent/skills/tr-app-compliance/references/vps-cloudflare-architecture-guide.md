# VPS + Cloudflare Mimari Rehberi

Hostinger VPS ve Cloudflare CDN kullanan yapılar için mevzuat uyumu:

## 1. Nginx Real-IP (5651 Uyumlu)
Cloudflare arkasında gerçek IP loglanmalıdır. `/etc/nginx/conf.d/cloudflare.conf` içine Cloudflare IP listesi ve `real_ip_header CF-Connecting-IP;` eklenmelidir.

## 2. Self-Hosted Font ve Varlıklar
Google Fonts CDN yerine fontlar `/public/fonts` altına alınmalı ve `@font-face` ile yerelden çağrılmalıdır.

## 3. Özel Görsel Güvenliği
Kullanıcıların yüklediği özel resimler (kimlik vb.) public CDN cache'ine bırakılmamalı; yetkilendirme arkasında servis edilmelidir.

