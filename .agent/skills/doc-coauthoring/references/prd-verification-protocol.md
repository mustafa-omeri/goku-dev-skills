# PRD ve Şartname Doğrulama Protokolü (/verify-prd)

Yapay zeka asistanlarının bir geliştirme veya sprint için *"Tüm işler tamamlandı, kod hazır!"* beyanında bulunmasının ardından, geliştiriciye ve ürün sahibine **"Bitti ama gerçekten şartnameye, mimariye ve katmanlara uygun mu bitti?"** güvenini kanıtıyla sunan bağımsız müfettiş protokolüdür.

---

## 1. Neden Bu Protokole İhtiyaç Var? (Anti-Phantom Finalizer)

Yapay zeka kodlama asistanlarının en yaygın zaaflarından biri **Erken Tamamlanma (Premature Completion / Phantom Done)** yanılgısıdır:
- Yalnızca izole bir React bileşeni ve mock test yazıp veritabanı migration'ını açmadan özelliği bitti ilan etmek,
- Şartnamedeki kritik köşe durumları (edge cases), boş (empty) ve hata (error) ekranlarını atlamak,
- Şartnamede hiç istenmeyen gereksiz soyutlamalar ve kapsam sapmaları (scope creep) üretmek.

`/verify-prd` komutu, ajanın kendi sözüne değil, **ölçülebilir ve denetlenebilir kanıtlara** dayalı bir doğrulama karnesi çıkarmasını sağlar.

---

## 2. 4 Aşamalı Doğrulama Döngüsü

### Aşama 1: Şartname ve Kabul Kriteri Eşleştirmesi (Spec & AC Audit)
- `docs/prd/`, `specs/`, `KANBAN.md` veya kullanıcının ilk prompt'undaki iş kuralları taranır.
- Her kabul kriteri için şu soru sorulur: *"Bu kural kaynak kodda nerede uygulanıyor ve hangi otomatik testle kanıtlanıyor?"*
- Karşılanmayan veya eksik bırakılan maddeler açıkça listelenir.

### Aşama 2: 5 Katmanlı Dikey Dilim (Full-Stack Vertical Slice) Denetimi
Bir özelliğin gerçek dünyada çalışabilmesi için 5 katmanın tamamı doğrulanmalıdır:

| # | Katman | Denetim Sorusu | Başarısızlık Durumu |
|---|---|---|---|
| **1** | **Veritabanı / Kalıcılık** | Fiziksel migration dosyası, tablo, kolon ve constraint'ler tanımlandı mı? | Eksikse: `YARIM (Katman 1 Eksik)` |
| **2** | **Backend / View / RPC** | Sunucu endpoint'i veya SQL view'ı yeni kolonları gerçekte dönüyor mu? | Eksikse: `YARIM (Katman 2 Eksik)` |
| **3** | **İstemci Entegrasyonu** | Arayüz mock veri yerine gerçek view ve API kontratına bağlandı mı? | Eksikse: `YARIM (Katman 3 Eksik)` |
| **4** | **Son Kullanıcı Arayüzü** | Render, loading, empty, error durumları ve mobil görünüm tam mı? | Eksikse: `YARIM (Katman 4 Eksik)` |
| **5** | **Yönetim & Form Döngüsü**| Veri sisteme nereden giriyor? Giriş formu veya admin paneli var mı? | Eksikse: `YARIM (Katman 5 Eksik)` |

### Aşama 3: İki Eksenli Kod Kalitesi & Kapsam Sapması (Scope Creep)
- **Standartlar Ekseni:** Martin Fowler kod kokusu (code smell) kataloğuna aykırı, şişkin veya karmaşık sınıflar var mı?
- **Şartname Ekseni:** Şartnamede talep edilmeyen fazladan kütüphaneler, gereksiz yardımcı sınıflar veya spekülatif soyutlamalar yapılmış mı?

### Aşama 4: Deterministik Kalite Kapıları
- Derleme ve tip kontrolü (`npx tsc --noEmit` veya `mvn clean compile`) exit 0 mı?
- Birim testleri gerçek assertion'lar içeriyor mu (totolojik mock testi yasağı)?
- Çevre temizliği: kullanılmayan importlar ve artık loglar temizlendi mi?

---

## 3. Doğrulama Karnesi Çıktı Formatı

`/verify-prd` komutu tamamlandığında kullanıcıya aşağıdaki şeffaf karne sunulur:

```markdown
### 🛡️ PRD & Şartname Doğrulama Karnesi (/verify-prd)

**Nihai Karar:** ✅ DOĞRULANDI (PASS) | ⚠️ YARIM (INCOMPLETE) | ❌ ŞARTNAME SAPMASI (DRIFT)

#### 1. Şartname & Kabul Kriterleri Uyumu
| Kriter No | Beklenen İster | Kod Konumu | Kanıt / Test | Durum |
|---|---|---|---|---|
| AC-1 | Kullanıcı bakiye görüntüleme | `src/components/Balance.tsx` | `Balance.test.tsx` | PASS |
| AC-2 | Yetersiz bakiye uyarı modalı | `src/components/AlertModal.tsx` | UI Testi | PASS |

#### 2. 5 Katmanlı Dikey Dilim Matrisi
- [x] Katman 1 (DB / Migration): `supabase/migrations/20261026_balance.sql`
- [x] Katman 2 (Backend / RPC): `rpc_get_user_balance()`
- [x] Katman 3 (İstemci API): `useUserBalance()` hook
- [x] Katman 4 (Arayüz & UX): Yükleme, hata ve bakiye rozeti
- [x] Katman 5 (Admin / Döngü Kapanışı): Bakiye yükleme formu

#### 3. Tespit Edilen Eksikler / Sapmalar
- *Tespit edilen eksik yok; özellik üretime hazır.*
```
