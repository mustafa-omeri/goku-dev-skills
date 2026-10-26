# /seo-apply — Uçtan Uca SEO & GEO Uygulama Protokolü

Bu protokol, bir yapay zeka ajanının projede tek bir yüzeysel meta etiketi ekleyip işi bitti saymasını (**Surface-Level SEO Tuzağı**) engellemek; projenin kod tabanına arama motorları (Googlebot, Bingbot) ve yapay zeka arama motorları (Perplexity, ChatGPT, Claude) için **üretim kalitesinde tam teşekküllü SEO & GEO altyapısını bizzat tatbik etmesini** sağlamak için tasarlanmıştır.

---

## 🎯 Komut Felsefesi ve Sınır Ayrımı

| Komut | Rol | Yaptığı Eylem & Çıktı |
|---|---|---|
| **`/seo-apply`** | **Yapıcı & İcraatçı (Builder)** | Kod tabanına bizzat girer; eksik meta etiketlerini, JSON-LD şemalarını, `robots.txt`, `sitemap.xml` ve `/llms.txt` dosyalarını üretir, enjekte eder ve test eder. |
| **`/prelaunch`** | **Denetçi & Hakem (Auditor)** | Canlıya çıkış öncesi tüm siteyi (KVKK, çerez onayı, WCAG 2.2 erişilebilirlik, formlar, SEO) salt-okunur tarar ve GO/NO-GO kalite karnesi verir. |

---

## 🔗 Bağlayıcı Yetenekler Zinciri (Ensemble Pipeline)

$$\text{seo-growth (Kural \& Şablon)} \longrightarrow \text{frontend-design (HTML Head \& SSR Enjeksiyonu)} \longrightarrow \text{seo\_checker.py (Deterministik Test)}$$

1. **`seo-growth`**: Başlık/açıklama karakter limitleri (50-60 / 120-155), Schema.org şablonları, robots.txt direktifleri ve `/llms.txt` özeti.
2. **`frontend-design`**: Head etiketlerinin, canonical URL'nin ve OpenGraph etiketlerinin React/HTML yapısına temiz ve hydration hatası üretmeyecek şekilde yerleştirilmesi.
3. **`seo_checker.py`**: Değişiklikler yapıldıktan sonra exit code 0 (`[OK]`) alınana kadar deterministik test kanıtı üretilmesi.

---

## ⚡ 4 Aşamalı Uygulama Döngüsü

### Aşama 1: Semantik Head & Sosyal Kartlar (HTML / JSX)
Sayfanın `<head>` veya React Helmet/Next.js Metadata bileşenine aşağıdaki etiketleri doğrudan yerleştirin:
- **Title:** 50–60 karakter arası, anahtar değer önerisini içeren vurucu başlık (`<title>Ürün Adı - Ana Değer Önerisi | Marka</title>`).
- **Meta Description:** 120–155 karakter arası, harekete geçirici eylem (CTA) içeren net açıklama.
- **Canonical URL:** Sayfanın asıl ve tekil URL'si (`<link rel="canonical" href="..." />`).
- **OpenGraph & Twitter Card:**
  - `og:title`, `og:description`, `og:url`, `og:type="website"`, `og:image`.
  - `twitter:card="summary_large_image"`, `twitter:title`, `twitter:description`, `twitter:image`.

### Aşama 2: Yapılandırılmış Veri (JSON-LD Schema.org)
Sayfa türünü tespit edin ve `<script type="application/ld+json">` bloğunu geçerli JSON sözdizimiyle sayfaya gömün:
- **SaaS / Web Uygulaması:** `SoftwareApplication` veya `WebApplication` (adı, açıklaması, applicationCategory, operatingSystem).
- **Kurumsal / Şirket Sayfası:** `Organization` (adı, url, logo, sameAs sosyal linkleri).
- **İçerik / Blog / Rehber:** `Article` veya `TechArticle` (headline, datePublished, author).
- **Sıkça Sorulan Sorular:** `FAQPage` (mainEntity soru ve cevapları - Google zengin sonuçları ve Perplexity/ChatGPT alıntıları için kritiktir).

### Aşama 3: GEO & AI Search Keşif Paketi (Public Dizin)
Projenin public varlık klasörüne (`public/` veya static web kökü) 3 temel dosyayı oluşturun ya da güncelleyin:
1. **`public/robots.txt`**:
   - Googlebot ve Bingbot'a izin verin.
   - Yapay zeka arama/atıf botlarına (`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`) sayfa tarama izni verin (GEO uyumu).
   - `Sitemap: https://<domain>/sitemap.xml` direktifini dosyanın en altına ekleyin.
2. **`public/sitemap.xml`**:
   - Tüm indekslenebilir sayfaları ISO 8601 tarih damgasıyla (`<lastmod>YYYY-MM-DD</lastmod>`) ve geçerli `<loc>` adresleriyle listeleyin.
3. **`public/llms.txt`**:
   - LLM'lerin (ChatGPT, Claude, Gemini, Cursor) projeyi tek bir istekte doğru anlaması için projenin ne işe yaradığını, temel özelliklerini ve API/dokümantasyon bağlantılarını içeren telegrafik bir markdown manifestosu oluşturun.

### Aşama 4: Deterministik Doğrulama & Çıkış Kodu Kanıtı
Yapılan değişiklikleri asla "yaptım ve çalışıyor" beyanıyla bırakmayın. Aşağıdaki test betiğini çalıştırın:
```bash
python .agent/skills/seo-growth/scripts/seo_checker.py --strict
```
- **Exit Code 0:** Doğrulama başarılıdır; oluşturulan/güncellenen dosyalar ve metrikler kullanıcıya raporlanır.
- **Exit Code 1 / Uyarı:** Hata mesajındaki satırları düzeltin ve exit code 0 elde edene kadar döngüyü tekrarlayın.

---

## 📊 Standart Çıktı Tablosu (SEO Karne Formatı)

Ajan, `/seo-apply` sonrasında kullanıcıya şu şeffaf formatı sunar:

```markdown
### 🌐 SEO & GEO UYGULAMA RAPORU (/seo-apply)
- **Sayfa Başlığı & Açıklama:** [Title karakter sayısı (örn: 54 kar) | Description (örn: 142 kar)]
- **Canonical & Sosyal Kartlar:** [Canonical URL + OpenGraph + Twitter Card enjekte edildi]
- **JSON-LD Schema.org:** [Eklenen şema tipi: SoftwareApplication / Organization / FAQPage]
- **GEO & Keşif Dosyaları:**
  * robots.txt: [Mevcut/Oluşturuldu — AI bot direktifleri eklendi]
  * sitemap.xml: [Mevcut/Oluşturuldu — ISO 8601 formatında URL sayısı]
  * llms.txt: [Oluşturuldu — AI arama motorları için markdown manifestosu]
- **Deterministik Doğrulama:** `seo_checker.py` -> [0 Hata, 0 Uyarı — EXIT 0 [OK]]
```
