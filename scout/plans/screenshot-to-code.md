# 🔭 Scout Değerlendirme Raporu: abi/screenshot-to-code

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/abi/screenshot-to-code
- **Sahibi:** abi
- **Analiz Tarihi:** 2026-10-25 19:13
- **Tespit Edilen Katman:** Fullstack (Frontend + Backend + Agentic Tooling)
- **Dosya Sayısı & Boyut:** 311 dosya (~2658 KB)
- **Teknoloji Yığını:** FastAPI (Python), Poetry, React, Vite, Tailwind CSS, Playwright (Chromium test & visual runner), Multi-LLM SDKs (OpenAI, Anthropic, Gemini, Replicate)

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
- **Deponun Amacı:** Ekran görüntüleri, mockup'lar, Figma tasarımları ve video kayıtlarını (ekran hareketleri) alarak HTML+Tailwind, React, Vue, Bootstrap veya Ionic kodlarına dönüştüren uçtan uca bir AI aracıdır.
- **Mimari Yapı:**
  - `backend/agent`: Agent motoru (`engine.py`, `state.py`, `runner.py`), model sağlayıcıları (`providers/`) ve araçlar (`tools/`).
  - `backend/codegen`: Kod üretim şablonları, stack adaptörleri ve prompt mühendisliği modülleri.
  - `backend/costs`: Token tüketimi, maliyet hesaplama ve model fiyatlandırma tabloları.
  - `backend/debug`: Görsel çıktıları ve ara prompt durumlarını kaydeden `DebugFileWriter`.
  - `frontend`: Kullanıcının görsel yüklediği, kod türevlerini canlı iframe/tarayıcıda yan yana izlediği ve AI ile chat üzerinden kodu revize ettiği React SPA arayüzü.
- **Güçlü Yönleri:**
  - Çoklu model yarışması (side-by-side comparison): Aynı ekran görüntüsünden Claude, GPT ve Gemini türevlerini eşzamanlı çalıştırıp en iyi sonucu seçtirme.
  - Playwright entegrasyonu ile otomatik headless render alıp görsel farkı (screenshot diff) yakalayabilme.
  - Varlık ayrıştırma (asset extraction): Görseldeki gerçek logo ve resimleri izole edip koda yerleştirme mantığı.
- **Zayıf Yönleri:**
  - Üretilen kodlar sıklıkla monolithic, tek dosyalık ve bileşen mimarisinden (compound components, atomic design) uzak şablonik HTML/React blokları üretir.
  - Bir yazılım geliştirme metodolojisi veya agent kuralları bütünü değil; bağımsız bir SaaS son kullanıcı uygulamasıdır.

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:**
  - Bizim ekosistemimiz (`skillSetWorks`) bir son kullanıcı web arayüzü değil; otonom, deterministik ve zanaat odaklı bir **Ajan Sözleşmesi ve Skill Kütüphanesi**dir.
  - Görsel zanaat, tipografi, renk teorisi ve anti-slop ilkeleri `frontend-design`, `ui-styling` ve `ui-ux-pro-max` skill'lerimizde çok daha derin kurallarla (WCAG, contrast scripts, token hiyerarşisi) korunmaktadır.
  - Mock ve yer tutucu görsel/veri ihtiyacı `mock-asset-provider` tarafından deterministik olarak çözülmektedir.
- **Dış Repodaki Değer:**
  - Ekran görüntüsü veya Figma tasarımından kod üretirken LLM'e verilen "görsel ayrıştırma promptları" (OCR metin hiyerarşisi, flex/grid tahminleme kılavuzları).
  - Canlı iframe çıktısını Playwright ile otomatik fotoğraflayıp hedef görselle kıyaslayan görsel regresyon/karşılaştırma yaklaşımı.
- **Kesişim & Ayrışma:**
  - Reponun React/FastAPI uygulama kodunu veya UI arayüzünü repomuza çekmek mimarimize aykırıdır (kod tabanı şişkinliği ve gereksiz bağımlılık yaratır).
  - Yalnızca "Vision-to-Code" prompt kalıpları ve görsel regresyon doğrulama ipuçları değer taşır.

## 4. Karar ve Gerekçe
**Karar:** `KISMEN_ALINABILIR: Screenshot/video girdisinden kod üretiminde kullanılan çoklu model prompting stratejileri, Playwright ile görsel regresyon/karşılaştırma döngüsü ve görüntü tabanlı varlık ayrıştırma (asset extraction) referansları mock-asset-provider ve frontend-design zanaatımıza cerrahi olarak eklenebilir.`

**Gerekçe:**
Reponun tamamı bağımsız bir SaaS web uygulamasıdır ve sistemimize doğrudan klonlanması uygun değildir. Ancak `backend/codegen` ve `backend/agent/tools` altındaki görseli koda döken özel yönlendirmeler ve asset kurtarma pratikleri, `frontend-design` ve `mock-asset-provider` skill'lerimizin "mevcut bir görselden/UI'dan esinlenerek bileşen üretme" kabiliyetine değerli bir referans dokümanı olarak katkı sağlayabilir.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **Referans Dokümantasyonu:**
   - `.agent/skills/frontend-design/references/vision-to-component-patterns.md` dosyası planlanarak; ekran görüntüsü, mockup veya video kaydından Tailwind/React bileşeni türetirken dikkat edilecek bounding-box, renk tespiti ve semantik tag eşleme yönergeleri özetlenebilir.
2. **Mock Asset Entegrasyonu:**
   - `mock-asset-provider` içine görseldeki logo/ikonları tespit edip Lucide-react veya yerel mock asset eşleşmelerine bağlayan prompt rehberi eklenebilir.
3. **Kapsam Dışı Bırakılacaklar:**
   - FastAPI backend sunucusu, Replicate ödeme/maliyet motoru ve React frontend paneli kesinlikle sisteme dahil edilmeyecektir.