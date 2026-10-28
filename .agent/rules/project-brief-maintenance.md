---
name: Project Brief Maintenance & Architecture Synchronization
description: Projenin canlı mimari ve teknoloji özetini (PROJECT_BRIEF.md) taze tutar; bağımlılık, DB ve karar değişikliklerinde senkronizasyonu zorunlu kılar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Proje Mimarisi / Canlı Brief"
    komut: "python .agent/skills/musgoku/scripts/check_project_brief.py"
---

# 📐 Canlı Proje Özeti ve Mimari Senkronizasyon (PROJECT_BRIEF.md)

> Bu kural `skillSetWorks` çatısını kullanan **tüm projelerde** (frontend, backend, fullstack, CLI) istisnasız geçerlidir.
> AI kod ajanları çalıştıkları projenin mimari gerçekliğini tek bir yaşayan belgede konsolide tutmakla yükümlüdür.

---

## 0. Tek Doğruluk Kaynağı: `PROJECT_BRIEF.md`

`PROJECT_BRIEF.md`, projenin güncel teknolojisini, kütüphane sürümlerini, veritabanı şemasını, dizin haritasını ve bağlayıcı kararlarını tek sayfada toplayan konsolide zihin haritasıdır.

⛔ **Bu dosya asla bayat bırakılamaz ve tahminle doldurulamaz.**
Canlı kod tabanındaki değişiklikler aynı oturumda bu dosyaya yansıtılmalıdır.

---

## 1. Kod Ajanının Temel Sorumlulukları

Ajan aşağıdaki 4 temel durumda `PROJECT_BRIEF.md` dosyasını senkronize etmekle yükümlüdür:

1. **Bağımlılık ve Stack Değişikliği:**
   - Projeye yeni bir paket eklendiğinde (`pnpm add`, `npm i`, `mvn dependency`, `pip install`) veya sürüm yükseltildiğinde `PROJECT_BRIEF.md` içindeki "Teknoloji Yığını & Altyapı" bölümü ve frontmatter'daki `frameworks` listesi anında güncellenir.
2. **Veritabanı Şeması ve Migration:**
   - Yeni bir tablo, RLS kuralı, entity veya migration eklendiğinde `PROJECT_BRIEF.md` içindeki veritabanı bölümü ve frontmatter'daki `database` listesi güncellenir.
3. **Bağlayıcı Kararlar ve Dış Referanslar:**
   - Projede kalıcı bir mimari karar alındığında (`knowledge-base.md`'ye işlenen kararlar, ADR'ler) veya `projects/_STANDARTLAR/` kuralları benimsendiğinde, `PROJECT_BRIEF.md` altındaki `## 3. Bağlayıcı Kararlar & Dış Referanslar` tablosuna ve frontmatter'daki `depends_on:` listesine işlenir.
   - Projeye yeni dokümantasyon dosyaları eklendiğinde (örn: PRD, test rehberi), frontmatter `related_docs:` listesine eklenir.
4. **Oturum Başlangıcı ve Kapanışı:**
   - **Başlangıç:** Ajan oturum başında `PROJECT_BRIEF.md` dosyasını okuyarak projenin güncel dilini, kütüphanelerini ve anayasal standartlarını öğrenir (`AGENTS.md` §0 Okuma Sırası).
   - **Kapanış:** `HANDOFF.md` teslim edilmeden önce `PROJECT_BRIEF.md`'nin mevcut kod gerçekliğini yansıttığı doğrulanır ve devir raporunda durumu açıkça belirtilir.

⛔ **Sahte 'Stabil' Beyanı Yasağı (Anti-Lazy Stabil Declaration):**
Git çalışma ağacında bağımlılık manifesti (`package.json`, `pom.xml`, `requirements.txt` vb.), yeni bir servis/sunucusuz fonksiyon (örn. Edge Function, worker) veya veritabanı şeması/migration'ı değiştirilmişken devir raporunda `PROJECT_BRIEF.md: Değişiklik yok / stabil` beyanında bulunmak ağır kural ihlalidir. Bu dosya canlı mimariyi yansıtmak zorundadır.

---

## 2. Dosya Konumu ve Şablonu

- **Konum:** `<repo-kök>/PROJECT_BRIEF.md` (Repo kökünde, `HANDOFF.md` ile aynı seviyede yer alır).
- **İlk Kurulum / Şablon:** Projede dosya yoksa, `.agent/templates/PROJECT_BRIEF.template.md` şablonu kopyalanarak veya `ProjectInitializer` / `generate_project_brief.py` CLI'si ile oluşturulur.
- **Dağıtım Koruması:** `PROJECT_BRIEF.md` yaşayan, projeye özel bir belgedir. `delivery.py` bu dosyayı merkezi olarak ezmez; projede kendi durumunu korur.

---

## 3. Deterministik Doğrulama Kapısı (`check_project_brief.py`)

Kural `OLCULEBILIR` sınıfındadır. Oturum tesliminden veya commit onayından önce aşağıdaki komut çalıştırılır:

```bash
python .agent/skills/musgoku/scripts/check_project_brief.py
```

### Kapı Kontrolleri:
- **E1 (Dosya Eksik):** Proje kökünde `PROJECT_BRIEF.md` bulunamadı.
- **E2 (Bozuk Frontmatter):** YAML frontmatter eksik veya zorunlu alanlar (`title`, `type: project-brief`, `primary_language`) tanımlanmamış.
- **E3 (Bağımlılık Sapması - Git Diff Drift):** Git çalışma ağacında `package.json`, `pom.xml`, `requirements.txt` vb. değişmiş ama `PROJECT_BRIEF.md` güncellenmemiş!
- **E4 (DB / Şema Sapması - Git Diff Drift):** Git çalışma ağacında migration veya DB modelleri değişmiş ama `PROJECT_BRIEF.md` güncellenmemiş!
- **E5 (Kırık Dosya Bağlantısı):** Frontmatter'daki `related_docs` listesindeki dosya yolları diskte mevcut değil.
- **E6 (Edge Function / Altyapı Sapması - Git Diff Drift):** Git çalışma ağacında sunucusuz işlev (`supabase/functions/**`, `netlify/functions/**`) veya altyapı yapılandırması (`Dockerfile`, `docker-compose.yml`, `wrangler.toml`, `supabase/config.toml`) değişmiş ama `PROJECT_BRIEF.md` güncellenmemiş!
- **E7 (Şablon Yer Tutucusu):** `PROJECT_BRIEF.md` içinde doldurulmamış şablon yer tutucusu (`[PROJE_ADI]`, `[proje-slug]`, `[YYYY-MM-DD]`) bırakılmış.
- **W1 (Tarih Sapması):** Dosya içeriği değiştiği halde frontmatter'daki `updated` alanı bugünün tarihini taşımıyor.

E1-E7 kodları **hata (exit 1)** üretir ve commit/handoff sürecini bloke eder.

- 💡 **Çift Yönlü Güvenlik Ağı (Dual Mapping Guard):** `check_db_migrations.py` kapısı da simetrik olarak `E5` (Dual Mapping Drift Guard) denetimiyle donatılmıştır; dolayısıyla bir ajan yalnızca veritabanı kapısını çalıştırsa dahi `PROJECT_BRIEF.md` güncellenmeden `exit 0` alamaz. Mimari ve şema asla birbirinden kopamaz.

---

## Proje Bazlı Ek Kurallar

> Bu bölüm projeye özeldir. Altında yalnızca projenin özel mimari notları yazılır.
