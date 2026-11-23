# Cerrahi Entegrasyon Referansı: alibaba/open-code-review

> **Kaynak Repo:** `https://github.com/alibaba/open-code-review`  
> **Hedef Yetenek:** `.agent/skills/code-review/`  
> **Motto:** Harici Go `ocr` binary bağımlılığı zorunlu kılınmadı; çekirdek hibrit mühendislik desenleri (dosya kapsam muhasebesi, akıllı demetleme ve davranışsal etki analizi) saf Python `diff_triage.py` + `code-review` protokolüne uyarlandı.

---

## 1. Deterministik Kapsam Muhasebesi (Coverage Accounting)

LLM'in büyük diff'lerde dosya atlamasını ("cutting corners") önlemek için:
1. İnceleme başında `diff_triage.py --json` ile `coverage_manifest.checklist` çıkarılır.
2. İnceleme tamamlandığında raporda **zorunlu kapsam özeti** verilir:
   - `total_files` · `reviewed_files` · `skipped_files` (atlanan her dosya için somut gerekçe) · `coverage_rate`.
3. `coverage_rate < 1.0` iken *"Sorun bulunamadı / LGTM"* beyanı **YASAKTIR**.

---

## 2. Akıllı Dosya Demetleme (Smart Bundling)

İlişkili dosyalar bağlam kopmasını önlemek için tek inceleme biriminde birlikte okunur:
- **i18n Çiftleri:** Aynı dizindeki dil dosyaları (`locales/tr.json` + `locales/en.json`) tek demette anahtar paritesiyle incelenir.
- **Kaynak + Test Çifti:** `FooService.ts` ve `FooService.test.ts` (veya `foo.py` + `test_foo.py`) tek demette davranış-test uyumuyla doğrulanır.

---

## 3. Davranışsal ve İş Akışı Etki Analizi (Material Behavior Impact)

Kodda tek bir bug olmasa dahi, **mevcut kullanıcı veya çağrıcı akışını değiştiren** her değişiklik (`flag kaldırma`, `varsayılan değer değişimi`, `silinen dosya/arayüz`) hata bulgularından ayrı bir başlıkta raporlanır:
- **Etkilenen Akış:** Hangi çağrıcı/CLI/kullanıcı yolu etkileniyor?
- **Öncesi -> Sonrası:** Önce ne oluyordu, şimdi ne oluyor?
- **Kanıt Konumu:** `dosya:satır`.

---

## 4. Opsiyonel Harici CLI Modu (`ocr delegate`)

*(Zorunlu değildir; yalnızca kullanıcının ortamında `@alibaba-group/open-code-review` zaten kuruluysa kullanılabilir).*
Harici `ocr` kurulu ortamlarda `ocr delegate preview --format json` ve `ocr delegate rule --format json <files...>` çıktıları, mevcut host ajan modelinin kapsam muhasebesi girdisi olarak değerlendirilebilir. Varsayılan akış daima sıfır-bağımlılıklı `diff_triage.py` üzerindendir.
