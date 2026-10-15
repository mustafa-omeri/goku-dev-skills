---
name: Trigger Rule Action
description: Tüm geliştirme kurallarını ve referans dokümanlarını bağlayan giriş noktasıdır. Bu dosya tetiklendiğinde aşağıdaki kuralların tamamı geçerlidir.
sinif: SUREC
---

# Trigger Rule Action

Bu kural, `.agent\rules\` altındaki diğer kuralları ve `skills\musgoku\`
referanslarını **devreye sokar**. Aşağıdakilerin tamamına uyulur.

## A. Oturum ve kayıt kuralları (her zaman)

| Konu | Kural |
|---|---|
| Oturum sürekliliği | [handoff-session-continuity.md](./handoff-session-continuity.md) |
| Bilgi tabanı ve devir dosyası | [knowledge-base-management.md](./knowledge-base-management.md) |
| Skill'leri okuma zorunluluğu | [always-read-skills.md](./always-read-skills.md) |
| **Hangi kelime hangi skill'i açar** | **[skill-trigger-routing.md](./skill-trigger-routing.md)** |

## B. Geliştirme ve kalite kuralları

| Konu | Kural |
|---|---|
| Geliştirme iş akışı | [development-workflow.md](./development-workflow.md) |
| **Sprint / MVP / kanban / release planı** | **[sprint-delivery-workflow.md](./sprint-delivery-workflow.md)** |
| Kullanılmayan kod yasağı | [no-unused-code.md](./no-unused-code.md) |
| **Sessiz bekleme ve kilitlenme yasağı** | **[no-silent-wait.md](./no-silent-wait.md)** |

## C. Git kuralları (MUST)

| Konu | Kural |
|---|---|
| Onaysız commit yasağı | [no-unauthorized-commit.md](./no-unauthorized-commit.md) |
| Release workflow zorunluluğu | [mandatory-git-release-workflow.md](./mandatory-git-release-workflow.md) |

## D. Best practice doğrulaması (MUST)

| Konu | Kural |
|---|---|
| context7 + sequential-thinking tetikleyicileri | [mcp-usage-enforcement.md](./mcp-usage-enforcement.md) |

## E. Frontend kuralları (yalnız frontend projesinde)

| Konu | Kural |
|---|---|
| Vite SPA kısıtları | [vite-spa-enforcement.md](./vite-spa-enforcement.md) |
| Bundle / chunk bütçesi | [frontend-bundle-limits.md](./frontend-bundle-limits.md) |
| i18n zorunluluğu | [i18n-enforcement.md](./i18n-enforcement.md) |
| Tasarım skilleri (zorunlu üçlü + sahiplik haritası) | [design-skills-enforcement.md](./design-skills-enforcement.md) |

## F. Backend kuralları (yalnız backend projesinde)

Yönlendirme tek yerden yapılır:
[`.agent\skills\musgoku\SKILL.md`](../skills/musgoku/SKILL.md) →
`references\project-architecture.md` · `references\spring-boot-api.md` ·
`references\data-layer.md` · `references\security-logging.md` ·
`references\websocket.md` · `references\pagination-search.md` ·
`references\clean-code-conventions.md` · `references\search-strategies.md` ·
`references\pagination-checklists.md`

## G. Dokümantasyon kuralları

| Konu | Kural |
|---|---|
| API dokümantasyonu zorunluluğu | [api-documentation-enforcement.md](./api-documentation-enforcement.md) |

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir kural tetikleyici gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_