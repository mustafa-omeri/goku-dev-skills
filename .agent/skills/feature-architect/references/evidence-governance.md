# Feature Architect v2 — V1–V8 Deterministik Kanıt Yönetişimi (`evidence-governance.md`)

`council_merger.py` birleştiricisi, 6 uzmandan gelen JSON raporlarını nihai plana dönüştürmeden önce 8 deterministik yönetişim kapısından geçirir:

| Kapı | Kod | Kural ve Yaptırım |
| :---: | :--- | :--- |
| **V1** | `HALLUCINATED_EVIDENCE_PATH` | `--project-root` verildiğinde diskte var olmayan `dosya:satır` adresine sahip bulgular `rejected_finding_ids` listesine alınarak reddedilir. |
| **V2** | `UNREACHABLE_LEGACY_COMPONENT` (`_FOR_PO`) | `--kg` verildiğinde aktif hiçbir `Route` düğümünden erişilemeyen ölü/legacy bileşenler için 6 şapkanın herhangi biri tarafından açılan `STUB_PAGE` bulguları otomatik olarak **`REMOVE`** kararına çevrilir. |
| **V3** | `CONFIDENCE_CEILING` | L1 statik/heuristic sinyallerle çalışma zamanı davranışını kesin iddia eden bulgular `candidate` seviyesinde tutulur. |
| **V4** | `GENERIC_BOILERPLATE_CONSTRAINT` | Somut dosya/sözleşme referansı içermeyen klişe `non_negotiable_constraints` maddeleri uyarıyla işaretlenir. |
| **V5** | `CROSS_SECTION_DUPLICATE_*` | 6 şapkanın tamamında aynı raporda `audits[]` altında bildirilen bir sorunun `ui_ux_mismatches[]` veya `new_features[]` altında tekrarlanması engellenir. |
| **V6** | `PO_BOUNDARY_*`, `ARCH_BOUNDARY_VISUAL_STYLING`, `FABRICATED_METRIC_CLAIM`, `SEO_PROTECTED_ROUTE_INDEXING`, `QA_CLIENT_ONLY_SECURITY_FIX` | Her şapka kendi uzmanlık sınırına kilitlenir (`PO` teknik/görsel sızıntısı, `ARCH` salt renk stili, `UX`/`GRW`/`PO` kanıtsız `%XX artırır` metrik iddiası, `SEO` korumalı rotaya index önerisi, `QA` sunucusuz salt istemci güvenlik yaması engellenir). |
| **V7** | `SIX_VERB_DECISION` | Her bulgu deterministik olarak 6 fiilli karar modeline (`CONNECT | FIX | REFACTOR | COMPLETE | REMOVE | DEFER`) eşlenir. |
| **V8** | `ZERO_DROP_GATE` | Hiçbir doğrulanmış `CRITICAL` veya `HIGH` bulgu ID'si konsolide raporda düşürülemez (`--check-report` -> `exit 2`). |
