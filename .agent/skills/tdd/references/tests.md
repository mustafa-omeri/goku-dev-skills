# İyi ve Kötü Test Standartları

## İyi Testler (Good Tests)

**Entegrasyon Tarzı (Integration-style):** Dahili parçaların sahte kopyaları yerine gerçek arayüzler üzerinden test edin.

```typescript
// İYİ: Gözlemlenebilir davranışı test eder
test("kullanıcı geçerli sepet ile ödeme yapabilir", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

Özellikler:
- Kullanıcıların / çağıranların önemsediği davranışı test eder
- Yalnızca public API kullanır
- Dahili refactor'larda kırılmaz
- "Nasıl yapıldığını" değil "NE yapıldığını" açıklar
- Test başına tek bir mantıksal doğrulama taşır

---

## Kötü Testler (Bad Tests)

**Uygulama Detayı Testleri (Implementation-detail tests):** Dahili yapıya aşırı bağımlıdır.

```typescript
// KÖTÜ: İç detayları test eder
test("checkout fonksiyonu paymentService.process metodunu çağırır", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

Kırmızı Bayraklar:
- Dahili işbirlikçileri mock'lamak
- Private metotları test etmek
- Çağrı adetlerini / çağrı sıralarını assert etmek
- Davranış değişmediği halde kod temizliğinde testin kırılması
- Doğrulamayı arayüz yerine dış yan yollardan yapmak

```typescript
// KÖTÜ: Doğrulamak için arayüzü atlar
test("createUser veritabanına kaydeder", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// İYİ: Arayüz üzerinden doğrular
test("createUser ile oluşturulan kullanıcı sorgulanabilir", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

**Totolojik Testler (Tautological tests):** Beklenen değer kodun hesabını yineler:

```typescript
// KÖTÜ: Beklenen değer fonksiyonun aynısıyla hesaplanıyor
test("toplamHesapla satırları toplar", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// İYİ: Beklenen değer bağımsız, bilinen bir sabittir
test("toplamHesapla satırları doğru toplar", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```
