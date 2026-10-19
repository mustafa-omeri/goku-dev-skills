---
name: tdd
description: Test güdümlü geliştirme (TDD) disiplini: dikey dilimler, dikiş noktalarında (seam) önce kırmızı test yazma, minimal geçiş kodu ve sahte mock testlerinden kaçınma ilkeleri. Tetikleyiciler: "tdd", "test güdümlü", "önce test yaz", "test driven development", "red green refactor", "vertical slice". Tetiklenmez: salt arayüz görsel denetimi `ui-ux-pro-max` kapsamındadır. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Test-Driven Development (TDD)

TDD, kırmızı → yeşil döngüsüdür. Bu disiplin, döngünün saklamaya değer kalıcı testler üretmesini sağlar: iyi bir testin tanımı, testlerin nereye konacağı (dikiş noktaları), kaçınılması gereken anti-desenler ve döngü kuralları.

Kod tabanını keşfederken terimlerin projeyle uyumlu olması için `GLOSSARY.md` dosyasını ve ilgili alandaki ADR kayıtlarını inceleyin.

## İyi Bir Test Nedir?

Testler, uygulamanın dahili yapısını değil, **genel arayüzler (public interfaces) üzerinden davranışı** doğrular. Kodun içi tamamen değişebilir; testler ise davranış değişmedikçe bozulmamalıdır. İyi bir test şartname (spec) gibi okunur: "geçerli sepet ile ödeme yapılabilir" ifadesi doğrudan bir yeteneği anlatır.

Ayrıntılı örnekler için [references/tests.md](references/tests.md) ve sahte nesne kılavuzu için [references/mocking.md](references/mocking.md) dosyalarına bakın.

## Dikiş Noktaları (Seams): Testler Nereye Konur?

**Dikiş noktası (seam)**, test ettiğiniz genel sınır noktasıdır: kodun içine müdahale etmeden davranışı gözlemleyebildiğiniz arayüzdür. Testler dikiş noktalarında yaşar; dahili (private) metotlara asla bağlanmaz.

⛔ **Yalnızca önceden belirlenmiş dikiş noktalarında test yazın.**
Herhangi bir test yazmadan önce, test edilecek dikiş noktalarını belirleyin ve kullanıcıyla teyit edin. Teyit edilmemiş dikiş noktalarında test yazılmaz. Her şeyi test edemezsiniz; kritik yollara ve karmaşık mantığa odaklanmak için dikiş noktalarını baştan netleştirmek şarttır.

Soru: "Genel arayüz nedir ve hangi dikiş noktalarını test etmeliyiz?" Her önerilen dikiş noktası için neyi yakalayıp neyi kaçırdığını tek satırda belirtin. Modül tasarımı, derinliği ve dikiş noktası yerleşimi için `codebase-design` skill'ine başvurun.

## Kaçınılması Gereken Anti-Desenler (Anti-patterns)

- **Uygulama Bağımlı Testler (Implementation-coupled):** Dahili işbirlikçileri mock'lar, özel (private) metotları test eder veya arayüz yerine yan yollardan (örneğin arayüz yerine doğrudan veritabanını sorgulayarak) doğrular. Belirti: Davranış değişmediği halde ufak bir refactoring sırasında test kırılıyorsa test yapıya aşırı bağımlıdır.
- **Totolojik Testler (Tautological):** Beklenen değer, kodun yaptığı hesaplamayı birebir tekrarlar (`expect(topla(a, b)).toBe(a + b)` gibi). Bu testler yapısı gereği her zaman geçer ve kodla asla çelişemez. Beklenen değer bağımsız bir doğrudan gelmelidir: sabit bir veri, bilinen bir örnek veya şartname çıktısı.
- **Yatay Dilimleme (Horizontal Slicing):** Önce tüm testleri yazıp sonra tüm kodu yazmak. Bu yaklaşım hayali varsayımları test eder, gerçek gereksinimlere duyarsız kalır. Bunun yerine **Dikey Dilimler (Vertical Slices)** ile çalışın: her döngüde bir test → bir minimal kod → doğrulama. Her test, bir öncekinden öğrenilenlerle ilerleyen bir **iz mermisi (tracer bullet)** olmalıdır.

## Döngü Kuralları

1. **Yeşilden Önce Kırmızı:** Önce başarısız olan testi yazın, ardından yalnızca o testi geçirecek kadar minimal kod yazın. Gelecekteki testleri tahmin edip spekülatif kod eklemeyin.
2. **Döngü Başına Tek Dilim:** Bir dikiş noktası, bir test ve bir minimal kod.
3. **Refactoring Döngünün Parçası Değildir:** Refactoring ve kod temizliği kırmızı-yeşil döngüsü içinde değil, inceleme aşamasında (`code-review` skill'i ile) yapılır.
