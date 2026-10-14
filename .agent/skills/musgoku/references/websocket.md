# WebSocket / Gerçek Zamanlı İletişim Standardı

---

## 1. Olay DTO'su

Her modül için yapılandırılmış olay DTO'su oluşturulur.
Adlandırma: `[Module]WebSocketEvent`.

Zorunlu alanlar:

| Alan | Açıklama |
|---|---|
| `eventType` | Olay tipi (oluşturuldu, güncellendi, silindi, atandı, durum değişti, gönderildi, başarısız) |
| `timestamp` | Olay anı |
| `message` | Okunabilir açıklama |
| modüle özel alanlar | kimlik, ad vb. |

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class [Module]WebSocketEvent {
    private String eventType;
    private Long [moduleId];
    private String [moduleName];
    private String message;
    private Instant timestamp;

    // Olay tipi başına statik fabrika
    public static [Module]WebSocketEvent created(Long id, String name) {
        return new [Module]WebSocketEvent("CREATED", id, name, "...", Instant.now());
    }
}
```

## 2. Yayınlama

- Yayınlama tek bir yardımcı bileşen üzerinden yapılır
- Yayın, iş mantığının **sonunda** ve hata durumunda değil; iş kaydı
  tamamlandıktan sonra çağrılır
- Yayın hatası iş mantığını **iptal etmez**; yakalanır, loglanır

```java
try {
    messagingTemplate.convertAndSend("/topic/[module]", event);
    log.info("type=TOPIC_PUBLISH, topic={}, eventType={}, id={}, userId={}, requestId={}, ts={}",
             topic, event.getEventType(), event.getId(),
             MDC.get("userId"), MDC.get("requestId"), Instant.now());
} catch (Exception e) {
    log.error("type=TOPIC_PUBLISH_ERROR, topic={}, error={}, userId={}, requestId={}, ts={}",
              topic, e.getMessage(), MDC.get("userId"), MDC.get("requestId"), Instant.now());
}
```

## 3. Konu adlandırma

| Desen | Kullanım |
|---|---|
| `/topic/[module]` | Modüle özel olaylar |
| `/topic/user` | Kullanıcıya özel olaylar |
| `/topic/global` | Sistem geneli olaylar |

Konu adı **kullanıcı kimliği içermez.** Kullanıcıya özel kanallar
sunucu tarafında yetkilendirilerek açılır; istemci istediği konuya keyfi
abone olamaz.

## 4. Güvenlik

- Bağlantı kurulurken kimlik doğrulama zorunlu
- Abonelik yetkisi sunucu tarafında doğrulanır
- Olay yükünde hassas veri gönderilmez
- Yetkisiz abonelik reddedilir ve loglanır

## 5. Performans

- Olay işleyicilerinde engelleyici işlem yapılmaz
- Ağır iş asenkron kuyruğa alınır
- Bağlantı ve istemci havuzu yönetimi açıkça yapılır
- Olay sıklığı ölçülür; gereksiz yayın (fetch zorlaması) yapılmaz

## 6. Frontend entegrasyonu

- Olay yapısı ve örnek yükler dokümante edilir
- Olay tipi sabitleri paylaşılır
- Abonelik deseni örnek kodla gösterilir
- İstemci **elle refetch yerine** gelen olayla durumu günceller
- Yeniden bağlanma ve kopma durumu ele alınır; olay kaçırılmazsa liste tutarsız
  olabileceğinden bağlantı kurulunca ilk yükleme yapılır

## 7. Dokümantasyon

- Her değişiklikte WebSocket API dokümantasyonu güncellenir
- Hata yönetimi ve yeniden bağlanma davranışı yazılır

## 8. Test

- [ ] Olay yayınlama test edildi
- [ ] Yayın hatası senaryosu test edildi (iş mantığı yine de tamamlanıyor)
- [ ] Yetkisiz abonelik reddediliyor
- [ ] Olay yükü yapısı doğrulandı
- [ ] Frontend entegrasyonu test edildi

## 9. Uygulama kontrol listesi

- [ ] Olay DTO'su ve statik fabrika yazıldı
- [ ] Yayın yardımcısı üzerinden yapılıyor
- [ ] Hata yakalama ve yapılandırılmış log var
- [ ] Konu adlandırması standarda uygun
- [ ] Kimlik doğrulama ve abonelik yetkisi var
- [ ] Dokümantasyon güncellendi