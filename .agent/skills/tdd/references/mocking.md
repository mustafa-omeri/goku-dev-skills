# Ne Zaman Mock Yapılmalı? (When to Mock)

Yalnızca **Sistem Sınırlarında (System Boundaries)** mock yapın:
- Dış 3. parti API'ler (Ödeme, e-posta, SMS)
- Veritabanları (Mümkünse test veritabanı veya container tercih edin)
- Zaman ve rastgelelik (Date, random UUID)
- Dosya sistemi (yalnızca zorunluysa)

**Asla Mock Yapmayın:**
- Kendi sınıflarınız ve modülleriniz
- Dahili işbirlikçileriniz
- Kendi kontrolünüzde olan herhangi bir bileşen

---

## Mock'lanabilirlik İçin Tasarım (Designing for Mockability)

Sistem sınırlarında kolay mock'lanan arayüzler tasarlayın:

### 1. Bağımlılık Enjeksiyonu (Dependency Injection)
Dış bağımlılıkları içeride üretmek yerine parametre olarak alın:

```typescript
// Kolay test edilir / mock'lanır:
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Zor test edilir:
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

### 2. Jenerik İstekler Yerine SDK Tarzı Arayüzler
Tek bir `fetch` fonksiyonu yerine her operasyon için ayrı metotlar tanımlayın:

```typescript
// İYİ: Her fonksiyon bağımsız test edilir
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// KÖTÜ: Mock içinde karmaşık koşullar gerektirir
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```
