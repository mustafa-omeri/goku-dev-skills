# Feature Architect v2 — Alan-Bağımsız Yetenek Çıkarımı (`capability-derivation.md`)

`intelligence.py` modülü ve `01-snr-product-owner.md` şapkası, sabit sektörel şablonlar (SaaS, E-ticaret, İK vb.) kullanmak yerine projenin yeteneklerini 4 dikey boyutta kod ve doküman kanıtlarından çıkarır:

1. **Topoloji (`topology`):** `full-stack-web` | `frontend-spa-or-ssr` | `backend-api-service` | `cli-or-library`
2. **Durumsallık (`statefulness`):** `persistent-data` (ORM/SQL/Migration var) | `stateless`
3. **Kimlik ve Yetki Modeli (`identity_model`):** `role-based-authenticated` | `stateless-or-public`
4. **Erişim Yüzeyi (`access_surface`):** `authenticated-app` | `public-or-local`

> **Strateji Girdisi Kuralı:** `PRODUCT.md` veya PRD dokümanı yoksa mevcut koddan çıkarılan ürün özeti `INFERRED` olarak işaretlenir; eksik stratejik eksenler uydurulmaz, kullanıcıya yapılandırılmış soru olarak yöneltilir.
