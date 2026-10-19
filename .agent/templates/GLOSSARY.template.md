# GLOSSARY — Proje Alan Dili ve Terminoloji Sözlüğü (Ubiquitous Language)

> Bu dosya projenin **3. Kalıcı Proje Belleğidir** (`PRODUCT.md` ürün gerçeği, `DESIGN.md` tasarım dili, `GLOSSARY.md` alan dili).
> Amacı: Ajanın ve geliştiricinin proje jargonu üzerinde tam mutabakat sağlaması; ajanın 20 kelimeyle gevezelik etmek yerine tek bir kanonik terimle düşünmesi ve kodlamasıdır.
>
> ⛔ **KURAL:** Bu dosyaya genel programlama kavramları (timeout, utility, cache vb.) veya implementasyon detayları (SQL sorgusu, CSS sınıfı) **YAZILMAZ**. Yalnızca bu projenin iş alanına (domain) özgü kavramlar ve tanımlar yer alır.

---

## 1. Temel İş Kavramları (Domain Vocabulary)

### [Örnek Alan / Varlık Grubu]

**Kanonik Terim (TR / EN)**:
- **Tanım**: Kavramın 1-2 cümlelik net, öz tanımı. Ne yaptığı değil, ne olduğu yazılır.
- **Kod Karşılığı**: `src/.../models/EntityName.ts` veya `com.project.entity.EntityName`
- **_Kaçın_ (Avoid)**: Eş anlamlı gibi duran ama kafa karıştıran yasaklı kelimeler (örn: _Müşteri_ yerine _Kullanıcı_, _Purchase_ yerine _Order_).

---

## 2. Kavram Haritası ve İlişkiler

| Kavram (Canonical) | Yanlış / Yasaklı Terim (_Avoid_) | Kod / Modül Sınırı | Açıklama / Nüans |
|---|---|---|---|
| **Sipariş (Order)** | Satın Alma, Sepet, Transaction | `OrderModule` / `orders` | Onaylanmış ve ödeme aşamasına geçmiş talep. |
| **Kullanıcı (User)** | Müşteri, Hesap, Client | `UserModule` / `users` | Sistemde oturum açan kimlik. |

---

## 3. Kurallar ve İlkeler

1. **Görüş Bildir (Be Opinionated):** Bir kavram için birden fazla kelime dolaşıyorsa en doğrusunu kanonik yap, diğerlerini `_Kaçın_` listesine al.
2. **Kısa ve Net Tanım:** Tanımlar en fazla 1-2 cümle olmalıdır.
3. **Anında Güncelleme:** Oturum sırasında yeni bir iş terimi netleştiğinde veya bulanık bir jargon netleştirildiğinde bu dosya bekletilmeden satır içi güncellenir.
