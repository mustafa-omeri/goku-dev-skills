# Cerrahi Entegrasyon Referansı: addyosmani/agent-skills

> **Kaynak Repo:** `https://github.com/addyosmani/agent-skills`  
> **Hedef Yetenekler:** `.agent/skills/code-review/`, `.agent/skills/tdd/`, `.agent/skills/karpathy-guidelines/`, `.agent/skills/verify-last/`  
> **Motto:** Mutasyon deneyiyle test kanıtı, yapısal çözüm önerisi, kör adversarial şüphe döngüsü ve diff zemin koruması cerrahi olarak aktarıldı.

---

## 1. Değişiklik ve Dosya Boyutu Sınırları + Presumptive Blockers

- **Diff Boyut Hedefleri:** `~100 satır` (ideal) · `~300 satır` (tek mantıksal iş için üst sınır) · `~1000 satır` (bölünmeli).
- **Toplam Dosya Büyüklüğü:** Küçük bir diff dahi dosyayı sağlıksız sınıra (`~1000` satır) itiyorsa, üzerine eklemeden önce yardımcı/alt bileşene böl (*Decompose, then add*).
- **Presumptive Blockers (Varsayılan Engelleyiciler):**
  1. Karmaşıklığı azaltmak yerine yalnız başka yere taşıyan refactoring (okuyucunun tuttuğu kavram sayısı azalmıyorsa reddet).
  2. Mevcut kanonik yardımcının kopyasını üreten yeni helper veya paylaşılan modüle sızan özellik-özel mantık.
  3. Belirsiz bir değişmezi (invariant) örten sessiz fallback / yutulmuş hata.
  4. Mevcut akışa yamalanmış ilgisiz `if` dalı (policy/dispatcher yerine yama).
- **Yapısal Çare Önerisi:** İncelemede yalnız *"karmaşık"* demek yasaktır; somut taşıma hamlesi önerilir (ör. koşullu zinciri typed dispatcher ile değiştir, pass-through wrapper'ı sil).

---

## 2. Mutasyon Deneyiyle Test Doğrulaması (`code-review-and-quality` Step 2)

Testlerin gerçekten davranışı koruduğunu okumayla değil deneyle doğrula:
1. Değişikliğin eklediği kritik bir koşulu ters çevir (bir `!` kaldır veya `&&` yerine `||` koy).
2. Test paketini çalıştır.
3. **Kural:** Mutasyon sonrası testler **hala yeşil kalıyorsa**, bu gerçek bir bulgudur — eksik test senaryosunu adıyla raporla. Ardından dosyayı derhal eski haline döndür.

---

## 3. Bağımlılık Güncelleme Hijyeni (Dependency Hygiene)

- Toplu `"bump dependencies"` yerine **değişiklik başına tek paket** (veya sıkı bağlı küçük grup).
- Sürüm numarasına değil `CHANGELOG` / breaking notes'a bak.
- Yalnız `package.json` / `pom.xml` değil, **lockfile diff'ini** de incele; transitive bağımlılık şişmesini denetle.

---

## 4. Kör Adversarial Şüphe Döngüsü (`doubt-driven-development`)

Yüksek riskli kararlarda (auth, migration, concurrency, geri döndürülemez işlem) alt ajana **kendi sonucunu (`CLAIM`) ASLA verme**:
- Yalnız `ARTIFACT` (diff/öneri) + `CONTRACT` (kural/spec) + düşmanca (`adversarial`) istem ver: *"Hata bul, doğrulama yapma, varsayılanı çürüt."*
- Kritik güvenlik/eşzamanlılık kararlarında kullanıcıya **farklı modelden ikinci görüş** (cross-model escalation) seçeneğini sun.

---

## 5. Diff Zemin Koruması (`constraint-driven-development`)

`diff_triage.py` ile eklenen (`+`) satırlarda şu sessiz kalite düşürmeleri otomatik yakalanır:
- Yeni baskılama yorumları: `@ts-ignore`, `@ts-expect-error`, `eslint-disable`, `# noqa`, `# type: ignore`, `@SuppressWarnings`.
- Yeni atlanan testler: `it.skip(`, `test.skip(`, `@pytest.mark.skip`, `@Disabled`, `unittest.skip`.
- Boş/yarım bırakılmış stub'lar: `throw new Error("Not implemented")`, `raise NotImplementedError`.
