---
name: MCP Usage Enforcement
description: second-brain-vault, context7 ve sequential-thinking MCP sunucularının ne zaman zorunlu devreye gireceğini tanımlayan tetikleyici tablosu.
sinif: TUTUM
---

# ⭐ Zorunlu: Best Practice ve Hafıza Desteği (second-brain-vault + context7 + sequential-thinking)

> Bu kural, "kural hatırlatıldı ama uygulanmadı" yaşanan oturumlar için yazıldı.
> Bu yüzden "kullan" değil, **"ne zaman tetiklenir"** şeklinde tanımlıdır.

---

## `second-brain-vault` — oturum başlangıcı, geliştirici tercihleri ve mimari kararlar

**İki adım:** `bootstrap` (`depth="brief"`, `project="<slug>"`) → `get_project_state` (`slug="<slug>"`).

### Zorunlu tetikleyiciler

| Tetikleyici | Somut örnek |
|---|---|
| ⭐ Yeni oturum açılışı / Göreve başlangıç | Ajan doğrudan yerel `HANDOFF.md` veya `knowledge-base.md` dosyasını açmaz. Önce `bootstrap` ile kiminle çalıştığı, yasaklar, tercihler ve kanıtlı dersleri (`DEV_BRIEF §3`) alır; ardından `get_project_state` ile projenin nerede kaldığını, bağlı kararlarını ve son hareketlerini çeker. |
| ⭐ "Nerede kaldık?", "Durum nedir?", "Sırada ne var?" | `get_project_state(slug="<slug>")` çağrısı zorunludur. |
| ⭐ Mimari karar / Kalıcı kural sorgusu | `get_decision(slug="...")` veya `ask(question="...")` / `search(query="...")` ile soru yöneltilir. |

### ⛔ Kullanma & Yasaklar

- ⛔ `knowledge-base.md` veya `HANDOFF.md` dosyasını baştan sona dosya olarak okumak yasaktır (token tasarrufu: ~15.000 → ~1.500).
- ⛔ Dosyalar yalnızca oturum sonunda kalıcı kararları yazmak (`knowledge-base.md` append) veya durumu kaydetmek (`HANDOFF.md`) içindir; okunmaz, MCP üzerinden sorgulanır.

### 🛡️ Yedek (Fallback — Yalnızca MCP Erişilemezse)

Yalnızca `second-brain-vault` MCP sunucusu erişilemez olduğunda veya hata verdiğinde yerel `HANDOFF.md` okunur. Ajan sessiz düşüş yapamaz, çıktısında *"second-brain-vault MCP erişilemediği için yerel HANDOFF.md okundu"* beyanını vermek zorundadır.

---

## `context7` — kütüphane / framework / SDK dokümantasyonu

**İki adım:** `resolve-library-id` → `query-docs` (**tek konu**, geniş soru yok).

### Zorunlu tetikleyiciler

| Tetikleyici | Somut örnek |
|---|---|
| ⭐ Yeni paket ekliyorsan | `@radix-ui/react-dropdown-menu` kuruldu → API sorulmadan bileşen yazılırsa bileşen adları ve imzalar tahmin olur |
| ⭐ Sürüm farkı kararı | "v5'te bu seçenek boolean mı fonksiyon mu?" → sorgula, "hatırlıyorum" deme |
| ⭐ API ismi / parametre yazıyorsan | Yanlış isim derlemede değil, çalışma zamanında patlar |
| ⭐ Erişilebilirlik davranışı | Odak yönetimi, typeahead, `Tab` engeli, focus trap |
| ⭐ Hata mesajı docs ile ilgiliyse | HTTP/DB/framework hata kodları ve açıklamaları |

### ⛔ Kullanma

Refactoring · sıfırdan script · iş mantığı hata ayıklama · code review · git ·
build ayarları · saf algoritma. Token harcar, karşılığı yok.

---

## `sequential-thinking` — karar verme

### Zorunlu tetikleyiciler

| Tetikleyici | Somut örnek |
|---|---|
| ⭐ 3+ adımlı bağlı plan kuruyorsan | Migration tasarımı, faz bölümü, refactor sırası |
| ⭐ İki yaklaşım arasında seçim | Cache mi kalıp mı · tek state mi iki mi · RLS mi uygulama katmanı mı |
| ⭐ Güvenlik / yetki sınırı | Token ≠ istek, satır bazlı yetki, XSS yüzeyi |
| ⭐ Belirsiz mimari karar | "Bu state'i kim sahiplensin?" · "Bu alan gerekli mi?" |
| ⭐ Tasarım / UX kararı | Bilgi hiyerarşisi, kontrol sahipliği, nerede ne gösterilir |

### ⛔ Kullanma

Tek satır düzeltme · dosya okuma · araç çıktısı yorumlama. Gürültüdür.

---

## Uygulama kontrol listesi

Kod yazmadan önce kendine sor:

0. Yeni oturum mu / Göreve başlangıç / Durum sorgusu mu → `second-brain-vault` (`bootstrap` + `get_project_state`) **şart**
1. Yeni paket mi ekliyorum → `context7` **şart**
2. API ismi / parametresi mi yazıyorum → şüpheliyim, `context7`'e sor
3. İki yaklaşım arasında mı seçim yapıyorum → `sequential-thinking` **şart**
4. Yetki / kimlik / veri sınırı mı → `sequential-thinking` **şart**
5. Evet ise → **önce MCP çağrısı, sonra kod**

## Şeffaflık

- Yanıtta kullanılan MCP'leri **adıyla** belirt.
- ⛔ Kullanmadıysan **"kullanmadım" de.** Gizleme.
  Kuralın kendisi denetlenebilir olmalı; aksi hâlde yazılı ama ölü kalır.

## Kaydedilecek ders

Bu kuralın ihlali bir kez olursa `knowledge-base.md`'ye
*Root Cause: kural tetikleyici olarak yazılmamıştı, sadece "kullan" deniyordu*
biçiminde yaz. Aynı hataya ikinci kez düşme.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü ek bir MCP sunucusu veya tetikleyici gerekirse (ör. özel DB/Search MCP), önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_