---
name: commitx
description: Peşin kullanıcı yetkisiyle kesintisiz otonom sürüm yayını orkestratörü; doğrulama kapılarını çalıştırıp semantik sürüm artışı, commit ve push adımlarını tamamlar. Tetikleyiciler: "/commitx", "commitx", "[COMMITX]", "commitle", "commit yap", "push to remote". Tetiklenmez: salt diff ve log inceleme istekleri. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# CommitX Autonomous Release Orchestrator

Bu yetenek, kullanıcının `commitx` veya `commitle` yazarak peşin açık onay verdiği durumlarda kalite kapılarından uzak depoya gönderime kadar tüm adımları ara onaysız, kesintisiz ve otonom olarak icra eder.

## Orkestrasyon Akışı

1. **Kapsam-Duyarlı Doğrulama:**
   - Değişen dosyalara göre ilgili derleme, tip kontrolü ve test kapılarını çalıştır.
2. **Değişiklik Raporu Hazırlığı:**
   - Değiştirilen dosyaları ve anlamsal commit mesajını (Conventional Commits) belirle.
3. **Kesintisiz İcra:**
   - Git add, commit, semantik sürüm etiketi (tag) ve remote push adımlarını sırayla tek seferde yürüt.
4. **Devir ve Handoff:**
   - `HANDOFF.md` dosyasını son sürüm ve kanıt metrikleriyle güncelle, kullanıcıya nihai başarı raporunu sun.
