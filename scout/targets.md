# Scout Dağıtım Hedefleri (Distribution Targets)

> Bu dosya `.agent/` ağacı ve ajan kurallarının dağıtılacağı hedef yolları tanımlar.
> - **Kullanım:** Yalnızca **DURUM** (`ON` / `OFF`) ve **PATH** girilir.
> - **Tekil Proje Path:** Belirtilen path doğrudan bir proje ise dağıtım doğrudan o projeye yapılır.
> - **Genel Dizin Path:** Belirtilen path bir çatı/çalışma alanı ise altındaki tüm projeler taranarak her birine dağıtım yapılır.
> - **Kaynak Depo:** Kaynak depo (`skillSetWorks`) dağıtım dışı tutulur.

| Durum | Hedef Path | Açıklama |
|---|---|---|
| ON | C:/devtools/vscodeWS/peopleside-culture/ocai | Tekil Proje (Java 21 / Spring Boot 3) |
| ON | C:/devtools/vscodeWS/peopleside-culture/FEProjectv1 | Tekil Proje (React / Vite SPA) |
| ON | C:/devtools/myProjectsAreaWS/bookmarkProjectWS/bookmarkManagerProject | Tekil Proje (React / Vite SPA) |
| ON | C:/devtools/myProjectsAreaWS/kalansureWS/kalansure | Tekil Proje (Java / Spring Boot) |
| OFF | C:/devtools/myProjectsAreaWS | Genel Dizin (ON yapıldığında altındaki tüm 12 projeye dağıtılır) |
