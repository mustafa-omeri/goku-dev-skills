# Mimari Karar Kaydı (ADR) Format Standartları

ADR kayıtları `docs/adr/` altında sıralı numaralandırma ile yaşar: `0001-baslik.md`, `0002-baslik.md`.

## Şablon

```markdown
# {Kararın Kısa Başlığı}

{1-3 cümle: Bağlam neydi, neye karar verdik ve gerekçesi nedir.}
```

Bir ADR tek bir paragraf olabilir. Amaç bürokrasi değil, bir kararın verildiğini ve *nedenini* kaydetmektir.

## İsteğe Bağlı Bölümler (Yalnızca Gerekliyse)
- **Durum:** `önerildi | kabul edildi | kullanımdan kaldırıldı | ADR-NNNN ile değiştirildi`
- **Değerlendirilen Seçenekler:** Reddedilen alternatiflerin neden elendiği hatırlanmaya değer olduğunda.
- **Sonuçlar:** Aşağı akışta doğacak bariz olmayan etkiler.

## ADR Açma Eşiği (3 Zorunlu Kural)
1. **Geri Dönüşü Zor:** Değiştirme maliyeti yüksek.
2. **Bağlamsız Şaşırtıcı:** Gelecekte kodu okuyan "Neden böyle yapılmış?" diyecektir.
3. **Gerçek Ödünleşim:** Gerçek alternatifler arasından gerekçeli seçim yapıldı.
