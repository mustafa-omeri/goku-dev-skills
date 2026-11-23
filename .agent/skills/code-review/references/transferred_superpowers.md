# Cerrahi Entegrasyon Referansı: obra/superpowers

> **Kaynak Repo:** `https://github.com/obra/superpowers`  
> **Hedef Yetenekler:** `.agent/skills/code-review/`, `.agent/skills/verify-last/`, `.agent/skills/tdd/`, `.agent/skills/karpathy-guidelines/`  
> **Motto:** Dış depo bütünü değil; yaranmacılık-karşıtı review kabulü, taze kanıt demir yasası ve model kademelendirme disiplini cerrahi olarak aktarıldı.

---

## 1. Geri Bildirim Alma Protokolü (`receiving-code-review`)

Kod inceleme yorumu veya dış ajan önerisi alındığında körlemesine uygulamak yerine 6 adımlı teknik süzgeç işletilir:

1. **READ:** Tüm geri bildirimi tepki vermeden sonuna kadar oku.
2. **UNDERSTAND:** Gereksinimi kendi sözcüklerinle netleştir; belirsiz madde varsa dur ve tüm belirsizleri tek seferde sor.
3. **VERIFY:** Kod tabanı gerçekliğiyle (`grep`, çağrıcılar, testler) doğrula.
4. **EVALUATE:** Bu yığın, hedef sürüm ve YAGNI açısından teknik olarak doğru mu? (Kullanılmayan endpoint/abstraction önerilirse `grep` ile kanıtlayıp reddet).
5. **RESPOND:** Performanslı övgü yasaktır (*"Harika tespit!", "Kesinlikle haklısınız!", "Teşekkürler!"* yazılmaz). Yalnızca: `"Düzeltildi: [dosya:satır]"` veya teknik gerekçeli geri itme (`pushback`).
6. **IMPLEMENT:** Maddeleri tek tek uygula; her birini bağımsız testle doğrula.

---

## 2. Tamamlanma Öncesi Doğrulama Demir Yasası (`verification-before-completion`)

```
TAZE DOĞRULAMA KANITI OLMADAN TAMAMLANMA BEYANI YASAKTIR
```

- **"Muhtemelen çalışır", "önceki koşuda geçti", "linter temiz"** ifadeleri geçersizdir; komut **mevcut oturum ve son düzenleme sonrasında** tam çalıştırılıp `exit 0` çıktısı okunmalıdır.
- **Regresyon Testi Red-Green İspatı:** Yeni veya düzeltilen bir regresyon testi yazıldığında:
  `Testi Yaz -> Çalıştır (PASS) -> Fix'i Geçici Geri Al -> Çalıştır (KIRMIZI / FAIL GÖR) -> Fix'i Geri Koy -> Çalıştır (PASS)`.
- **Alt Ajan (Subagent) Çıktısı:** Alt ajan *"başarılı"* dese bile kabul edilmez; ana ajan `git diff --stat` / dosya ve test komutunu bağımsız doğrular.

### Rasyonalizasyon Önleme Tablosu

| Ajan Bahanesi | Gerçek Durum |
|---|---|
| `"Linter geçti, sorun yok"` | Linter derleyici/tip denetleyicisi (`tsc`, `mvn`) değildir |
| `"Sadece küçük bir değişiklik"` | Küçük diff büyük dosyayı veya çağrıcıyı kırabilir — tam kapı koş |
| `"Alt ajan bitti dedi"` | `git status` ve test çıktısı olmadan kanıt sayılmaz |

---

## 3. Alt Ajan Model Kademelendirmesi (`subagent-driven-development`)

- **Mekanik Görevler** (1-2 dosya, net spec): En hızlı/ekonomik model (`flash` / `flash_lite`).
- **Entegrasyon & Çoklu Dosya:** Standart model (`inherit`).
- **Final Bütün-Dal İncelemesi, Mimari & 3+ Tur Takılan Fix Döngüsü:** En güçlü mevcut model (`pro` / `inherit` üst katman).
- Uzun çoklu görev yürütmelerinde sohbet belleğine değil, diskteki ilerleme kaydına (`HANDOFF.md` / `git log`) güvenilir.
