# Deepening (Modülleri Derinleştirme)

Sığ modül öbeklerini (shallow clusters) bağımlılıklarına göre güvenli bir şekilde derinleştirme rehberi.

## Bağımlılık Kategorileri

Bir adayı derinleştirirken bağımlılıklarını 4 sınıfa ayırın:

### 1. Süreç İçi (In-process)
Saf hesaplama, bellek içi durum, sıfır I/O. Her zaman derinleştirilebilir: modülleri birleştirin ve yeni arayüz üzerinden doğrudan test edin. Ayrı bir adaptöre gerek yoktur.

### 2. Yerel İkame Edilebilir (Local-substitutable)
Yerel test karşılığı olan bağımlılıklar (Postgres yerine PGLite/testcontainer, bellek içi dosya sistemi). Derinleştirilmiş modül bu yerel bileşenle test edilir. Dikiş noktası dahilidir.

### 3. Uzak Ama Bize Ait (Ports & Adapters)
Ağ sınırının ötesindeki kendi servisleriniz (mikroservisler, dahili API'ler). Dikiş noktasında bir **port (arayüz)** tanımlayın. Derin modül mantığa sahip olur; taşıma katmanı bir **bağdaştırıcı (adapter)** olarak enjekte edilir. Testler bellek içi adaptör, prod ise HTTP/gRPC adaptörü kullanır.

### 4. Gerçek Dış Servis (True External / Mock)
Kontrolünüz dışındaki 3. parti servisler (Stripe, Twilio). Derin modül dış bağımlılığı bir port olarak alır; testler sahte (mock) adaptör sağlar.

## Dikiş Noktası Disiplini (Seam Discipline)

- **Bir adaptör hipotetik dikiş demektir; iki adaptör gerçek dikiş demektir:** En az iki adaptör (genelde prod + test) gerekmedikçe dikiş noktası açmayın. Tek adaptörlü dikiş gereksiz bir yönlendirmedir (indirection).
- **Dahili ve Harici Dikişler:** Derin bir modül kendi içinde dahili dikişlere sahip olabilir. Sırf testler kullanıyor diye dahili dikişleri dış arayüze sızdırmayın.

## Test Stratejisi: Katmanlama Değil Değiştirme (Replace, Don't Layer)

- Sığ modüller birleştirildiğinde eski birim testleri silin; derinleştirilmiş modülün yeni arayüzü üzerinden test yazın.
- Testler arayüz üzerinden gözlemlenebilir sonuçları assert etmelidir, dahili durumu değil.
- Davranışı anlatan testler iç refactoring'lerde kırılmaz.
