# GLOSSARY.md Format Standartları

## Yapı

```markdown
# {Bağlam Adı}

{Bu bağlamın ne olduğunu ve neden var olduğunu anlatan 1-2 cümlelik açıklama.}

## İş Kavramları (Language)

**Sipariş (Order)**:
Müşteri tarafından satın alınmak üzere onaylanan ürünler listesi ve ödeme taahhüdü.
_Kaçın_: Satın alma, işlem

**Fatura (Invoice)**:
Teslimat sonrasında müşteriye iletilen resmi ödeme talebi.
_Kaçın_: Hesap, ödeme fişi

**Müşteri (Customer)**:
Sipariş veren gerçek veya tüzel kişi.
_Kaçın_: Alıcı, hesap, kullanıcı
```

## Kurallar

- **Taraf Tutun (Be opinionated):** Aynı kavram için birden fazla kelime varsa en doğrusunu seçin, diğerlerini `_Kaçın_` altına yazın.
- **Tanımları Sıkı Tutun:** En fazla 1-2 cümle. Ne yaptığını değil, NE OLDUĞUNU tanımlayın.
- **Yalnızca Bu Projeye Özel Kavramlar:** Genel programlama kavramları (timeout, error handling, helper) sözlüğe girmez.
- **Saf İş Alanı:** Teknik detay veya kod kütüphaneleri sözlükte yer almaz.
