# Feature Architect v2 — 6 Fiilli Karar Modeli (`decision-model.md`)

`/feature-architect` v2 konseyindeki her bulgu ve aksiyon, belirsiz "iyileştirilmeli" ifadeleri yerine aşağıdaki **6 deterministik karar fiilinden (`decision`)** birini taşır:

| Karar Fiili | Anlamı | Ne Zaman Kullanılır? |
| :--- | :--- | :--- |
| **`CONNECT`** | Mevcut Kabiliyeti Bağla | Backend API ucu, servis veya veri modeli zaten mevcut ve çalışır durumda; yalnızca istemci adaptörü veya UI ekran bağlantısı eksik (`UNWIRED_BACKEND_CAPABILITY`). |
| **`FIX`** | Kusuru / Kırığı Onar | 404'e giden rota, tıklanamayan link (`dead click`), RBAC/IDOR yetki açığı, DTO tip uyuşmazlığı veya CLS/spinner hatası. |
| **`REFACTOR`** | Mimarisi / Tasarımını Yenile | Çalışan ancak katman ihlali, God Component, N+1 sorgu, bundle şişkinliği veya tasarım dilinden kopuk ilkel UI barındıran yapı. |
| **`COMPLETE`** | Eksik Dikey Dilimi Tamamla | Aktif rotada bulunan ancak 5 katmanlı dikey diliminden (`DB -> Backend -> Client API -> UI 4-State -> Loop Closure`) biri veya birkaçı hiç yazılmamış gerçek yarım özellik. |
| **`REMOVE`** | Ölü / Gereksiz Kodu Kaldır | Aktif hiçbir rotadan erişilmeyen legacy bileşen, iş değeri olmayan sahte/dummy "Hızlı İşlemler" kartı veya terk edilmiş yetim uç. |
| **`DEFER`** | Ertele / Araştır | Kanıtı kısmi (`candidate`) olan, mevcut fazda önceliği düşük veya önce ürün/iş kararı netleştirilmesi gereken madde. |
