---
name: ui-polish
description: Arayüz parlatma, anti-slop temizliği ve zanaat tabanı orkestratörü; 55 hazır bileşen teması ve 10 ölçülmüş paletle başlayıp tipografi, boşluk ritmi ve WCAG 2.2 AA kontrastını doğrular. Tetikleyiciler: "/ui-polish", "ui polish", "[UI-POLISH]", "arayüz parlat", "polish ui". Tetiklenmez: sıfırdan backend API ve veritabanı `musgoku`'ya aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# UI Polish Ensemble Orchestrator

Bu yetenek, web ve mobil arayüzlerdeki "generic AI slop" görünümünü temizleyen ve prodüksiyon kalitesinde zanaat standardı kuran 4 aşamalı orkestrasyon zincirini işletir.

## Orkestrasyon Akışı

1. **Hazır Varlık Taraması:**
   - 55 bileşen temasını incele:
     `python .agent/skills/frontend-design/scripts/get_component.py --list`
   - 10 ölçülmüş WCAG AA/AAA kontrastlı paleti incele ve CSS değişkeni üret:
     `python .agent/skills/frontend-design/scripts/get_palette.py --list`
2. **Görsel Yön ve Tipografi:**
   - `ui-ux-pro-max` veritabanından amaca uygun stil (79 stil) ve ürün paletini seç:
     `python .agent/skills/ui-ux-pro-max/scripts/search.py "<konsept>"`
3. **Kod ve Zanaat Uygulaması:**
   - `frontend-design` ve `ui-styling` kurallarıyla kodu işle:
     * Sıfır emoji (`E8`): Tüm ikonlar tutarlı SVG olmalı.
     * Sıfır hardcoded renk (`E9`): Renkler token veya CSS değişkeninden gelmeli.
     * Sıfır gradyan metin, sıfır kalın kenar çizgisi (`border-l-4`).
4. **Mekanik Doğrulama:**
   - `python .agent/skills/musgoku/scripts/check_design_slop.py --include-agent`
   - `python .agent/skills/musgoku/scripts/check_theme_contrast.py`
