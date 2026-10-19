---
name: codebase-design
description: Yazılım mimarisi ve modül tasarımı standartları: derin modüller, dikiş noktaları (seams), silme testi (deletion test) ve karmaşıklığı soyutlama ilkeleri sağlar. Tetikleyiciler: "kod mimarisi", "modül tasarımı", "derin modül", "codebase design", "deep modules", "module design", "architectural seam". Tetiklenmez: salt CSS ve görsel stillendirme `ui-styling` ve `frontend-design` kapsamındadır. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Codebase Design

**Derin modüller (deep modules)** tasarlayın: temiz bir dikiş noktasının (seam) arkasında, küçük bir arayüzle zengin ve karmaşık bir davranışı gizleyin. Bu yaklaşım çağıranlar için yüksek kaldıraç (leverage), geliştirenler için yüksek yerellik (locality) ve herkes için test edilebilirlik sağlar.

## Terimler Sözlüğü (Glossary)

Bu terimleri tam anlamıyla kullanın:
- **Modül (Module):** Arayüzü ve uygulaması (gövdesi) olan her şey. Ölçekten bağımsızdır: bir fonksiyon, sınıf, paket veya dilim olabilir.
- **Arayüz (Interface):** Bir çağıranın modülü doğru kullanmak için bilmesi gereken her şey: tip imzası, değişmezler (invariants), sıralama kısıtları, hata modları ve performans özellikleri.
- **Uygulama (Implementation):** Modülün içindeki kod gövdesi.
- **Derinlik (Depth):** Arayüzdeki kaldıraç. Küçük bir arayüzün arkasında büyük bir davranış gizleniyorsa modül **derindir (deep)**. Arayüzün kendisi içerideki mantık kadar karmaşıksa modül **sığdır (shallow - kaçının)**.
- **Dikiş Noktası (Seam):** Davranışı o noktadaki kodu değiştirmeden değiştirebildiğiniz yer; modül arayüzünün yaşadığı konum.
- **Bağdaştırıcı (Adapter):** Bir dikiş noktasında arayüzü karşılayan somut yapı (ör. PostgreSQL adapter, In-memory fake).
- **Kaldıraç (Leverage):** Çağıranların derinlikten kazandığı güç. Az arayüz öğrenerek çok iş yapabilme yeteneği.
- **Yerellik (Locality):** Geliştiricilerin kazandığı avantaj. Değişiklik, hata ve bilginin çağıranlara dağılmak yerine tek bir modülde toplanması.

## Derin ve Sığ Modüller (Deep vs Shallow)

**Derin Modül (Hedef):** Küçük arayüz + zengin ve derin uygulama.
**Sığ Modül (Kaçının):** Büyük ve karmaşık arayüz + sığ, yalnızca passthrough (aktarıcı) uygulama.

Bir arayüz tasarlarken kendinize şu soruları sorun:
1. Metot sayısını azaltabilir miyim?
2. Parametreleri basitleştirebilir miyim?
3. Daha fazla karmaşıklığı modülün içine gizleyebilir miyim?

## Tasarım İlkeleri

- **Derinlik arayüzün bir özelliğidir:** Derin bir modül dahili olarak küçük parçalardan oluşabilir; bu parçalar genel arayüzün parçası olmamalıdır.
- **Silme Testi (The Deletion Test):** Modülü sildiğinizi hayal edin. Karmaşıklık tamamen yok oluyorsa, o modül sadece bir aracıdır (pass-through). Karmaşıklık N adet çağıran noktaya geri sıçrıyorsa, modül yerini hak ediyor demektir.
- **Arayüz test yüzeyidir:** Çağıranlar ve testler aynı dikiş noktasından geçer. Arayüzün ötesindeki iç detayları test etmek istiyorsanız, modülün şekli muhtemelen yanlıştır.
- **Tek bağdaştırıcı hipotetik dikiş demektir; iki bağdaştırıcı gerçek dikiş demektir:** Üzerinde gerçekten değişen bir şey yoksa gereksiz dikiş noktası (seam) üretmeyin.

## Test Edilebilirlik İçin Tasarım (Designing for Testability)

1. **Bağımlılıkları Kabul Edin, İçeride Üretmeyin (Accept dependencies, don't create them).**
2. **Sonuç Döndürün, Yan Etki Üretmeyin (Return results, don't produce side effects).**
3. **Yüzey Alanını Küçük Tutun (Small surface area):** Daha az metot ve daha az parametre, daha basit test kurgusu demektir.

Ayrıntılı kılavuzlar için [references/DEEPENING.md](references/DEEPENING.md) ve [references/DESIGN-IT-TWICE.md](references/DESIGN-IT-TWICE.md) dosyalarına bakın.
