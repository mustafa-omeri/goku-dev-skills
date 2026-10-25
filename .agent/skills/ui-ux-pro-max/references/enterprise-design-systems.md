# Enterprise Design Systems Benchmark Index

> Kaynak: [alexpate/awesome-design-systems](https://github.com/alexpate/awesome-design-systems) · Scout Değerlendirme Raporu ID: 7
> Amaç: Kurumsal web ve mobil arayüz geliştirirken dünya devi teknoloji şirketlerinin tasarım sistemlerini, bileşen mimarilerini, ses/ton kılavuzlarını ve açık kaynak depolarını benchmark almak için referans kataloğu.

---

## 1. Tasarım Sistemi Boyutları

Kurumsal bir tasarım sistemi yalnızca bir UI kit veya CSS kütüphanesi değildir. 4 temel sütundan oluşur:

1. **Components:** Üretim kalitesinde kodlanmış bileşen kütüphanesi (React, Vue, Web Components vb.).
2. **Voice & Tone:** Ürünün yazım dili, mikrometinleri (microcopy), hata mesajı kılavuzu ve marka tonu.
3. **Designers Kit:** Figma / Sketch tasarım şablonları, auto-layout kuralları ve token kütüphaneleri.
4. **Source Code:** Açık kaynak erişilebilir mimari, monorepo yapısı ve test stratejileri.

---

## 2. Küratörlü Kurumsal Tasarım Sistemleri Kataloğu

| Şirket / Ürün | Sistem Adı | Dokümantasyon URL | Bileşenler | Voice & Tone | Figma / Kit | Açık Kaynak Repo |
|---|---|---|:---:|:---:|:---:|---|
| **Shopify** | Polaris | [polaris.shopify.com](https://polaris.shopify.com/) | ✅ React | ✅ Mükemmel | ✅ Figma | [github.com/Shopify/polaris](https://github.com/Shopify/polaris) |
| **IBM** | Carbon Design System | [carbondesignsystem.com](https://carbondesignsystem.com/) | ✅ React/Vue/Web | ✅ Kapsamlı | ✅ Figma | [github.com/carbon-design-system/carbon](https://github.com/carbon-design-system/carbon) |
| **GitHub** | Primer | [primer.style](https://primer.style/) | ✅ React/ViewComponent | ✅ Geliştirici Odaklı | ✅ Figma | [github.com/primer/react](https://github.com/primer/react) |
| **Atlassian** | Atlassian Design System | [atlassian.design](https://atlassian.design/) | ✅ React | ✅ Detaylı | ✅ Figma | [bitbucket.org/atlassian/atlassian-frontend-mirror](https://atlassian.design/resources) |
| **Salesforce** | Lightning (SLDS) | [lightningdesignsystem.com](https://www.lightningdesignsystem.com/) | ✅ LWC / CSS | ✅ Kurumsal | ✅ Sketch/Figma | [github.com/salesforce-ux/design-system](https://github.com/salesforce-ux/design-system) |
| **Adobe** | Spectrum | [spectrum.adobe.com](https://spectrum.adobe.com/) | ✅ React / Spectrum Web | ✅ Net | ✅ XD/Figma | [github.com/adobe/react-spectrum](https://github.com/adobe/react-spectrum) |
| **Microsoft** | Fluent 2 | [fluent2.microsoft.design](https://fluent2.microsoft.design/) | ✅ React / iOS / Android | ✅ Erişilebilir | ✅ Figma | [github.com/microsoft/fluentui](https://github.com/microsoft/fluentui) |
| **Google** | Material Design 3 | [m3.material.io](https://m3.material.io/) | ✅ Web / Flutter / Android | ✅ Kapsamlı | ✅ Figma | [github.com/material-components](https://github.com/material-components) |
| **Apple** | Human Interface Guidelines | [developer.apple.com/design](https://developer.apple.com/design/) | ✅ SwiftUI / UIKit | ✅ Apple Standardı | ✅ Figma | [developer.apple.com/design/resources](https://developer.apple.com/design/resources/) |
| **Ant Group** | Ant Design | [ant.design](https://ant.design/) | ✅ React / Vue / Angular | ✅ İş Odaklı (B2B) | ✅ Figma | [github.com/ant-design/ant-design](https://github.com/ant-design/ant-design) |
| **Uber** | Base Web | [baseweb.design](https://baseweb.design/) | ✅ React | ✅ Minimal | ✅ Figma | [github.com/uber/baseweb](https://github.com/uber/baseweb) |
| **GitLab** | Pajamas | [design.gitlab.com](https://design.gitlab.com/) | ✅ Vue / CSS | ✅ Şeffaf & Açık | ✅ Figma | [gitlab.com/gitlab-org/gitlab-ui](https://gitlab.com/gitlab-org/gitlab-ui) |
| **Pinterest** | Gestalt | [gestalt.pinterest.systems](https://gestalt.pinterest.systems/) | ✅ React | ✅ Görsel Odaklı | ✅ Figma | [github.com/pinterest/gestalt](https://github.com/pinterest/gestalt) |
| **Zendesk** | Garden | [garden.zendesk.com](https://garden.zendesk.com/) | ✅ React / CSS | ✅ Müşteri Hizmetleri | ✅ Figma | [github.com/zendeskgarden/react-components](https://github.com/zendeskgarden/react-components) |
| **Audi** | Audi UI | [ui.audi.com](https://ui.audi.com/) | ✅ Web Components | ✅ Lüks / Otomotiv | ✅ Figma | [github.com/audi/audi-ui](https://github.com/audi/audi-ui) |
| **Nordhealth** | Nord Design System | [nordhealth.design](https://nordhealth.design/) | ✅ Web Components | ✅ Sağlık / Medikal | ✅ Figma | [github.com/nordhealth/nord](https://github.com/nordhealth/nord) |
| **Decathlon** | Vitamin | [decathlon.design](https://decathlon.design/) | ✅ React / Android / iOS | ✅ Spor / Dinamik | ✅ Figma | [github.com/Decathlon/vitamin-web](https://github.com/Decathlon/vitamin-web) |
| **Deliveroo** | Prism | [prism.deliveroo.com](https://prism.deliveroo.com/) | ✅ React / React Native | ✅ Samimi | ✅ Figma | [github.com/deliveroo](https://github.com/deliveroo) |

---

## 3. Benchmark Nasıl Yapılır?

`ui-ux-pro-max` veya `brand` skill'leriyle yeni bir kurumsal ürün veya dashboard tasarlarken:

1. **B2B / Yoğun Veri / E-Ticaret:** Shopify Polaris ve Ant Design modellerini inceleyin (Kompakt formlar, bulk action barları, data table filtreleme).
2. **Karanlık Mod & Geliştirici Araçları:** GitHub Primer ve Vercel Geist yaklaşımlarını benchmark alın (Monospace fontlar, kopyalama butonları, diff bileşenleri).
3. **Karmaşık Sağlık / Kurumsal SaaS:** IBM Carbon ve Nord Design System'i inceleyin (WCAG AAA renk kontrastı, net hata göstergeleri, breadcrumbs).
4. **Token Mimarisi Referansı:** Tüm sistemlerin `design-tokens` sözlüklerini referans alarak `design-system` skill'imizdeki semantic token katmanıyla uyumlu hale getirin.
