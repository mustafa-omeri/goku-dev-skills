---
name: Enforce Skill Usage
description: Kod yazmadan, dosya oluşturmadan veya terminal komutu çalıştırmadan önce ilgili skill dosyalarının okunmasını zorunlu kılar.
sinif: TUTUM
---

# ⛔ KESİN KURAL: Kod Yazmadan Önce Skill Oku

Kod yazmadan, dosya oluşturmadan veya terminal komutu çalıştırmadan önce
`.agent/skills/` altındaki ilgili skill dosyalarını bul ve oku.

## Zorunlu akış

0. Repo kökündeki `HANDOFF.md`'yi oku
   ([handoff-session-continuity.md](./handoff-session-continuity.md)).
1. Talebi analiz et.
2. İlgili olabilecek skill dosyalarını `.agent/skills/` altında tara.
3. Kodlamaya veya planlamaya geçmeden önce bu skill dosyalarını oku.
4. Skill'teki standartlara **birebir** uyarak geliştirmeyi tamamla.

## Yönlendirme

Ana yönlendirici: `.agent\skills\musgoku\SKILL.md`.
Frontend taleplerinde `musgoku-react-component`, `musgoku-api-data-layer`,
`musgoku-forms-validation`, `musgoku-routing-auth`, `musgoku-styling-ui`,
`musgoku-typescript-quality`; backend taleplerinde `references\` altındaki
referanslar devreye girer. Tablo için `musgoku/SKILL.md`'ye bak.

**Hangi kelime hangi skill'i açar?** →
[`skill-trigger-routing.md`](./skill-trigger-routing.md). Bu dosya tetikleyici
sözlüğünün tek sahibidir; istek geldiğinde önce oradan eşleştir, sonra
`SKILL.md`'yi oku.

**Tasarım alanında hangi konunun sahibi kim?**
→ [`design-skills-enforcement.md`](./design-skills-enforcement.md) §3.

## Bu kuralın istisnası

Tek satırlık düzeltme, açıklama değişikliği veya dosya adı düzeltmesi gibi
talep genişliği yoksa skill okumadan geçilebilir — bunu yanıtta **açıkça**
belirt. Gizleme.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir istisna veya ek skill okuma kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_