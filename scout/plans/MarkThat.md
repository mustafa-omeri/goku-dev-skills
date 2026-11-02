# 🔭 Scout Değerlendirme Raporu: Flopsky/MarkThat

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/Flopsky/MarkThat
- **Sahibi:** Flopsky
- **Analiz Tarihi:** 2026-10-30 13:22
- **Tespit Edilen Katman:** Backend / Multimodal Document Processing
- **Dosya Sayısı & Boyut:** 42 dosya (~180 KB)
- **Teknoloji Yığını:** Python 3.10+, PyMuPDF, Jinja2, LangChain (OpenAI/Anthropic/Google GenAI/Mistral), LiteLLM, Pillow, Matplotlib

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
- **Ne Yapıyor:** PDF ve görsel dosyalarını (PNG/JPG) gelişmiş çok modlu (multimodal) LLM'ler aracılığıyla yapılandırılmış Markdown formatına dönüştüren veya zengin görsel açıklamaları üreten bir Python kütüphanesidir.
- **Mimari Özellikler:**
  1. **Çift Modlu Çalışma (Dual Mode):** Hem standart OCR/Markdown dönüşümü hem de detaylı figür/görsel betimleme modu (`description_mode`).
  2. **İki Aşamalı Figür Çıkarma (Coordinate Detection & Parsing):** PDF içerisindeki grafikleri ve şekilleri tespit etmek için bir koordinat tespit modeli (`coordinate_model`, örn. Gemini 2.0 Flash) ile bunları parçalayıp metne/tabloya döken ayrıştırma modelini (`parsing_model`, örn. Gemini 2.5 Flash Lite) asenkron pipeline ile ayırması.
  3. **Şablon Odaklı Prompt Yönetimi:** `prompts/templates/*.j2` altında Jinja2 şablonları ile LLM komut istemlerini dinamik parametrelerle yönetmesi.
  4. **Sağlam Fallback ve Hata Toleransı:** Model çağrılarında sağlayıcılar (OpenAI, Anthropic, Gemini, Mistral, OpenRouter) arası fallback mekanizmaları.
- **Zayıf Yönleri:**
  - Bağımlılık şişkinliği: Aynı anda hem yerel SDK'lar (`google-generativeai`, `openai`, `anthropic`, `mistralai`), hem `litellm`, hem de tüm `langchain-*` paketlerini gerektirmesi yüksek bağımlılık yükü yaratmaktadır.
  - Ajan/Skill mantığı yerine monolitik bir SDK kütüphanesi olarak kurgulanmıştır.

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:**
  - Bizim `.agent/skills` havuzumuz ağırlıklı olarak yazılım mühendisliği, kod kalitesi, TDD, mimari tasarım, PRD/doküman yazımı (`doc-coauthoring`), güvenlik denetimleri ve uçtan uca UI/UX tasarım orkestrasyonu üzerine odaklanmıştır.
  - Sistemimizde PDF ve taranmış belgelerden teknik şartname/doküman çıkarma, mimari şema ayrıştırma veya zengin görsel betimlemeleri çıkarma konusunda doğrudan özelleşmiş bir PDF-to-Markdown dikey multimodal prompt/çıkarım deseni bulunmamaktadır.
- **Dış Repodaki Değer:**
  - Özellikle PDF'lerdeki görsel, grafik ve diyagramları tespit edip koordinat kırparak (`PyMuPDF` + `Pillow`) multimodal LLM'e besleme mimarisi (Figure Extraction Pipeline) ve `prompts/templates/*.j2` şablonları son derece temiz ve öğreticidir.
- **Kesişim & Ayrışma:**
  - Deponun Python SDK yapısını olduğu gibi skill setimize dahil etmek gereksiz bağımlılık (LangChain bloatı) ve bakım yükü getirir. Ancak `doc-coauthoring` veya veri hazırlama süreçlerinde kullanılabilecek 2 aşamalı (koordinat tespiti -> figür ayrıştırma) prompt deseni ve Jinja2 şablonlama stratejisi yüksek değere sahiptir.

## 4. Karar ve Gerekçe
**Karar:** `KISMEN_ALINABILIR: Doküman ve görselden Markdown'a dönüşüm için Jinja2 şablonlama yapısı, koordinat bazlı figür çıkarma (PyMuPDF + multimodal LLM) ve çoklu model fallback mantığı referans olarak faydalıdır; ancak projenin kendisi bağımsız bir Python kütüphanesidir ve skill setimize doğrudan bir tam kütüphane olarak değil, doküman işleme referans deseni olarak kazandırılabilir.`

**Gerekçe:**
Tüm repoyu doğrudan bir agent skill'ine çevirmek `langchain`, `litellm` ve ağır Python bağımlılıkları nedeniyle mimarimizi şişirir. Ancak reponun getirdiği **"İki Aşamalı Figür Çıkarma & Multimodal Markdown Ayrıştırma Deseni"** ve prompt şablonları, doküman işleme ve analiz ihtiyaçlarında referans mimari kalıp olarak alınmalıdır.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **Referans Dokümantasyonu / Pattern Kaydı:**
   - `doc-coauthoring` veya ilgili referans kılavuzuna "Multimodal PDF/Görsel Doküman Ayrıştırma Mimarisi" başlığı altında bir referans deseni notu eklenebilir.
2. **Çıkarılacak Çekirdek Desenler:**
   - **Adım 1 (Bounding Box Detection):** Görsel/PDF sayfasındaki şekil/tabloların normalize koordinatlarını (ymin, xmin, ymax, xmax) hızlı/hafif bir vision modeline tespit ettirme.
   - **Adım 2 (Cropping & Detailed Parsing):** Kırpılan görsel alanını derin analiz modeliyle Markdown/tablo formatına dönüştürme.
   - **Adım 3 (Markdown Assembly):** Jinja2 şablonuyla ana metin ve figür açıklamalarını hiyerarşik Markdown olarak birleştirme.
3. **Kapsam Dışı Bırakılanlar:**
   - `langchain-*` ve `gradio` bağımlılıkları tamamen elenecek; ihtiyaç halinde doğrudan standart API çağrıları veya hafif yardımcı scriptler tercih edilecektir.