#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sıfır-Sürtünmeli Hazır Bileşen Teması Köprüsü (get_component.py).

Neden var?
----------
`frontend-design` becerisi altında 55 adet prodüksiyon kalitesinde, çalışan
HTML/CSS bileşen teması (`component-themes/`) bulunmaktadır.

Bu CLI aracı, ajanın veya geliştiricinin diskteki yüzlerce alt klasörü tek tek
gezip vakit kaybetmesini önler; tek bir komutla arama yapmasını, kategorileri
listelemesini ve doğrudan kopyalanabilir HTML/CSS kodunu çekmesini sağlar.

Kullanım:
    python get_component.py --list
    python get_component.py --type sidebar
    python get_component.py --theme violet-minimal-sidebar
    python get_component.py --theme violet-minimal-sidebar --html
    python get_component.py --theme violet-minimal-sidebar --css
    python get_component.py --search "split screen login"
    python get_component.py --search "pricing" --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
FRONTEND_DESIGN_DIR = SCRIPT_DIR.parent
COMPONENT_THEMES_DIR = FRONTEND_DESIGN_DIR / "component-themes"

CATEGORIES = [
    "sidebars", "navbars", "menus", "parallax",
    "accordions", "cards", "logins", "footers"
]


def load_theme_metadata(theme_dir: Path) -> dict:
    """Belirli bir bileşen temasının dizinini tarar ve meta verilerini döner."""
    theme_name = theme_dir.name
    category = theme_dir.parent.name
    html_file = theme_dir / "index.html"
    css_file = theme_dir / "styles.css"
    
    # .design.md dosyasını bul
    design_files = list(theme_dir.glob("*.design.md"))
    design_file = design_files[0] if design_files else None
    
    title = theme_name.replace("-", " ").title()
    description = ""
    ideal_for = ""
    
    if design_file and design_file.is_file():
        try:
            doc_text = design_file.read_text(encoding="utf-8", errors="replace")
            # İlk başlığı bul
            for line in doc_text.splitlines():
                line_str = line.strip()
                if line_str.startswith("# ") and not title:
                    title = line_str[2:].strip()
                elif line_str.startswith("> ") and not description:
                    description = line_str[2:].strip()
                elif ("ideal for" in line_str.lower() or "best for" in line_str.lower() or "uygun:" in line_str.lower()) and not ideal_for:
                    ideal_for = line_str
        except Exception:
            pass

    if not description:
        description = f"{category.rstrip('s').title()} bileşeni için {theme_name} hazır teması."

    return {
        "name": theme_name,
        "title": title,
        "category": category,
        "description": description,
        "ideal_for": ideal_for,
        "path": str(theme_dir),
        "has_html": html_file.is_file(),
        "has_css": css_file.is_file(),
        "design_file": str(design_file) if design_file else None
    }


def get_all_themes() -> list[dict]:
    """component-themes/ altındaki tüm temaları tarar."""
    themes = []
    if not COMPONENT_THEMES_DIR.is_dir():
        return themes

    for cat_dir in sorted(COMPONENT_THEMES_DIR.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name not in CATEGORIES:
            continue
        for t_dir in sorted(cat_dir.iterdir()):
            if not t_dir.is_dir():
                continue
            if (t_dir / "index.html").is_file() or list(t_dir.glob("*.design.md")):
                themes.append(load_theme_metadata(t_dir))
    return themes


def find_theme_by_name(name: str) -> dict | None:
    all_themes = get_all_themes()
    name_clean = name.lower().strip()
    # Tam eşleşme
    for t in all_themes:
        if t["name"].lower() == name_clean:
            return t
    # Kısmi eşleşme
    for t in all_themes:
        if name_clean in t["name"].lower():
            return t
    return None


def get_dashboard_catalog_ids() -> dict[str, dict]:
    """dashboard-theme/catalog.json içindeki 18 resmi dashboard/sayfa arketipini döner."""
    catalog_path = FRONTEND_DESIGN_DIR / "dashboard-theme" / "catalog.json"
    if not catalog_path.is_file():
        return {}
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8", errors="replace"))
        items = data.get("archetypes", []) if isinstance(data, dict) else []
        return {str(item.get("id", "")).lower().strip(): item for item in items if item.get("id")}
    except Exception:
        return {}


def verify_theme_names(raw_names: str) -> tuple[bool, list[dict], list[str]]:
    """Virgülle ayrılmış tema adlarının gerçek katalogda (56 component + 18 dashboard) varlığını doğrular."""
    all_themes = get_all_themes()
    exact_map = {t["name"].lower(): t for t in all_themes}
    dash_map = get_dashboard_catalog_ids()

    requested = [n.strip() for n in raw_names.split(",") if n.strip()]
    if not requested:
        return False, [], ["<boş-tema-listesi>"]

    verified: list[dict] = []
    invalid: list[str] = []
    for name in requested:
        key = name.lower()
        if key in exact_map:
            verified.append(exact_map[key])
        elif key in dash_map:
            d_item = dash_map[key]
            verified.append({
                "name": d_item.get("id", name),
                "title": d_item.get("title", name),
                "category": f"dashboard-theme/{d_item.get('sector', 'general')}",
                "description": d_item.get("summary", ""),
                "path": str(FRONTEND_DESIGN_DIR / "dashboard-theme" / "catalog.json"),
            })
        else:
            invalid.append(name)

    return len(invalid) == 0, verified, invalid


def format_adapt_guide(target: dict) -> str:
    """Seçilen temanın Living Surface (DESIGN.md) ile nasıl yapısal olarak port edileceğini açıklar."""
    cat = target.get("category", "")
    name = target.get("name", "")
    lines = [
        "=" * 70,
        f"STRUCTURAL PORTING BLUEPRINT (LIVING SURFACE ADAPTATION): {name}",
        "=" * 70,
        "1. TEMEL İLKE (PALET SADAKATİ != İSKELET TEMBELLİĞİ):",
        "   - Projenin `DESIGN.md` / Living Surface renk tokenlarını (%100 Palet Sadakati) KORUYUN.",
        "   - Ancak mevcut ekrandaki sıkıcı/dar DOM iskeletini KORUMAYIN; bu temanın çok katmanlı",
        "     yapısal anatomisini (Grid, Split-Hero, Katmanlı Kart, Segmented Switcher) JSX/TSX'e port edin!",
        "   - Yalnızca `pl-10`, `shadow-sm` veya `aria-*` değiştirip çıkmak (Cosmetic Micro-Diff Slop) YASAKTIR.",
        "",
    ]
    if cat == "logins":
        if name in ("sliding-hero-auth-switcher-login", "sliding-dual-auth-toggle-login"):
            lines.extend([
                "2. LOGIN / AUTH KAYAR KAPAK MİMARİSİ (SLIDING HERO OVERLAY ARCHITECTURE — 50%/50% Çift Form):",
                "   - Tek sütunlu dar kutu (`max-w-[440px]` / `max-w-md`) tam sayfa Login ekranlarında YASAKTIR (E12).",
                "   - Dış Kapsayıcı (Masaüstü İki Yarı Card):",
                "     `relative w-full max-w-[960px] min-h-[620px] rounded-[24px] bg-white border-8 border-white shadow-[0_12px_80px_rgba(41,30,113,0.12)] overflow-hidden`",
                "   - FORM PANELİ MİMARİSİ VE BUTON YERLEŞİMLERİ (SOL %50 - phase === 'signin' / SAĞ %50 - phase === 'signup'):",
                "     * ⛔ MASAÜSTÜNDE ÇİFT KATMANLI TAB VE UYDURMA EK GEÇİŞLER YASAKTIR (E13):",
                "       Formun tepesinde 'Giriş Yap | Kayıt Ol' sekmesi veya 'Şifre ile Giriş / Ek Giriş' alt butonları ASLA kullanılmaz! Masaüstünde geçişi sağlayan TEK mekanizma kayar vitrin kapağındaki outline pill butondur.",
                "       ⛔ Şablonda olmayan uydurma ek kimlik doğrulama modal veya sekmeleri KESİNLİKLE YASAKTIR (E13 ile bloke edilir). Giriş ekranı daima doğrudan E-posta + Şifre ile açılır.",
                "     * Başlık: Temiz, ferah 'Login' (veya 'Giriş Yap') / 'Sign Up' (veya 'Hesap Oluştur') — manifesto paragrafları yazmayın.",
                "     * Form Alanları (Inputs): E-posta (`hello@example.com`) ve Şifre (`••••••••`) temiz input kontrolleri.",
                "     * Yardımcı Satır (Auxiliary Row — flex items-center justify-between text-xs my-2):",
                "       - Sol: [x] Remember me / Beni hatırla (checkbox + etiket)",
                "       - Sağ: Forgot password? / Şifremi unuttum? (link/button)",
                "     * Birincil Eylem Butonu (Primary Action Button):",
                "       - w-full h-[46px] rounded-[10px] bg-[#212625] text-white font-medium hover:bg-black transition-colors ('LOGIN' / 'GİRİŞ YAP' veya 'SIGN UP' / 'KAYIT OL').",
                "     * Bölücü (Divider):",
                "       - relative text-center my-4: '── Or ──' (veya '── Veya ──') ince yatay çizgi ve ortalanmış metin.",
                "     * Alternatif Login Tipleri / Sosyal Giriş Butonları (Social Buttons):",
                "       - grid grid-cols-2 gap-3 w-full: [Google] ve [GitHub] (veya [Facebook]) resmi marka SVG logoları ve butonları.",
                "       - ⛔ Şablonda olmayan uydurma ek kimlik doğrulama modal veya sekmeleri kullanılmaz.",
                "   - KAYAR VİTRİN KAPAĞI (.card-bg + .hero, hidden lg:flex lg:w-1/2 absolute inset-y-0 left-0 z-20 rounded-[18px] transition-transform duration-[650ms] ease-[cubic-bezier(0.65,0,0.35,1)]):",
                "     * ⛔ PITCH-BLACK SLOP VE DÜZ SİYAH KUTU KESİNLİKLE YASAKTIR: Zemin asla düz siyah/koyu (#252528, bg-black, bg-zinc-950) bırakılamaz!",
                "     * HERO PHOTOGRAPHY BACKDROP (Zorunlu 2-Kademeli Görsel Üretim Protokolü):",
                "       ⛔ Rastgele Picsum (picsum.photos/seed/...) KESİNLİKLE KULLANILAMAZ (alakasız rastgele fotoğraflar basar)!",
                "       Ajan, projenin arketipine uygun atmosferik 1200x800 görseli iki yöntemden biriyle temin eder ve `public/assets/auth/hero.jpg` konumuna kaydeder:",
                "       - Yöntem A (Antigravity IDE): `invoke_subagent` ile `image-generator` çağrılır (Prompt: 'Generate an atmospheric editorial photograph for <proje-adı> (<arketip>), high resolution 1200x800 landscape, save to public/assets/auth/hero.jpg').",
                "       - Yöntem B (Yerel CLI Aracı): `python .agent/skills/mock-asset-provider/scripts/generate_auth_hero.py --archetype <arketip> --project-name <ad> --output public/assets/auth/hero.jpg` çalıştırılır.",
                "       `background: url('/assets/auth/hero.jpg') center/cover no-repeat;` üzerine `bg-gradient-to-t from-black/75 via-black/35 to-black/20` karartma scrim'i eklenir.",
                "     * ⛔ ASLA 3 tane kocaman özellik kartı (Layers, Sparkles, Shield vb. feature card listesi) vitrine doldurulmaz! Vitrin bir landing page değil, formların üzerini örten zarif atmosferik bir maskedir.",
                "     * Vitrin İçeriği ve Kayan Hareket Mekaniği:",
                "       - phase === 'signin' (Giriş) durumunda: `translate-x-full` ile sağ yarıyı (%50) örter. Üzerinde ortalanmış 'Hello there' başlığı, 1-2 satırlık özlü alt metin ve `[SIGN UP]` / `[KAYIT OL]` outline pill butonu bulunur (tıklanınca phase = 'signup').",
                "       - phase === 'signup' (Kayıt) durumunda: `translate-x-0` ile sol yarıyı (%50) örter. Üzerinde ortalanmış 'Welcome back' başlığı, 1-2 satırlık özlü alt metin ve `[LOGIN]` / `[GİRİŞ YAP]` outline pill butonu bulunur (tıklanınca phase = 'signin').",
                "       - Outline Pill Buton Stili: rounded-full border border-white/80 bg-white/10 backdrop-blur-xs px-10 py-3 text-white text-xs font-semibold tracking-wider hover:bg-white hover:text-[#212625] transition-all cursor-pointer",
                "   - Mobil (375px / <1024px) Ergonomisi:",
                "     * Mobilde kayar kapak gizlenir (`hidden lg:flex`).",
                "     * Üstte 44px dokunma hedefli Segmented Switcher (`lg:hidden`) belirir; `phase` değiştikçe tek form tam ekran (`px-4 sm:p-6`) akıcı olarak gösterilir.",
            ])
        else:
            lines.extend([
                f"2. LOGIN / AUTH VİTRİN MİMARİSİ ({name} — Desktop Dual-Pane & E12/W6 Kapısı):",
                "   - Tek sütunlu dar kutu (`max-w-[440px]` / `max-w-md`) tam sayfa Login ekranlarında YASAKTIR (E12).",
                "   - Dış Kapsayıcı (Desktop Dual-Pane):",
                "     `w-full max-w-[1020px] grid grid-cols-1 lg:grid-cols-12 overflow-hidden rounded-3xl border shadow-sm`",
                "   - VİTRİN SÜTUNU (Sol/Sağ Showcase — lg:col-span-5 flex flex-col justify-between p-8 sm:p-10 relative overflow-hidden):",
                "     * ⛔ PITCH-BLACK SLOP VE DÜZ SİYAH KUTU KESİNLİKLE YASAKTIR: Vitrin zemini asla düz siyah/koyu (#252528, bg-black, bg-zinc-950) bırakılamaz! (W6)",
                "     * HERO PHOTOGRAPHY BACKDROP (Zorunlu 2-Kademeli Görsel Üretim Protokolü):",
                "       ⛔ Rastgele Picsum (picsum.photos/seed/...) KESİNLİKLE KULLANILAMAZ (alakasız rastgele fotoğraflar basar)!",
                "       Ajan, projenin arketipine uygun atmosferik 1200x800 görseli iki yöntemden biriyle temin eder ve `public/assets/auth/hero.jpg` konumuna kaydeder:",
                "       - Yöntem A (Antigravity IDE): `invoke_subagent` ile `image-generator` çağrılır.",
                "       - Yöntem B (Yerel CLI Aracı): `python .agent/skills/mock-asset-provider/scripts/generate_auth_hero.py --archetype <arketip> --project-name <ad> --output public/assets/auth/hero.jpg` çalıştırılır.",
                "       `background: url('/assets/auth/hero.jpg') center/cover no-repeat;` üzerine `bg-gradient-to-t from-black/75 via-black/35 to-black/20` karartma scrim'i ekler.",
                "     * ⛔ ASLA 3 tane devasa özellik kartı yığını doldurulmaz. Vitrinde marka rozeti, güçlü 1 satırlık değer önerisi, zarif bir güven rozeti veya odaklanmış tek bir canlı önizleme yer alır.",
                "   - FORM PANELİ MİMARİSİ VE BUTON YERLEŞİMLERİ (lg:col-span-7 p-6 sm:p-10 bg-white / var(--bg-surface)):",
                "     * ⛔ UYDURMA EK GEÇİŞLER VE ÇİFT KATMANLI BUTONLAR YASAKTIR (E13):",
                "       Zaten 'Giriş Yap' / 'Kayıt Ol' varken araya ikinci bir 'Şifre ile Giriş / Ek Giriş' alt seçicisi koymak yasaktır (E13 ile bloke edilir). Giriş ekranı doğrudan E-posta + Şifre ile açılır.",
                "     * Mod Geçişi: Üstte tekil, temiz Segmented Switcher (`Giriş Yap` / `Kayıt Ol` — lg:col-span-7 içinde). Asla çift katmanlı karmaşık tablar açılmaz.",
                "     * Başlık: Temiz, ferah 'Login' (veya 'Giriş Yap') / 'Sign Up' — manifesto paragrafları yazmayın.",
                "     * Form Alanları (Inputs): E-posta (`hello@example.com`) ve Şifre (`••••••••`) temiz input kontrolleri.",
                "     * Yardımcı Satır (Auxiliary Row — flex items-center justify-between text-xs my-2):",
                "       - Sol: [x] Remember me / Beni hatırla (checkbox + etiket)",
                "       - Sağ: Forgot password? / Şifremi unuttum? (link/button)",
                "     * Birincil Eylem Butonu (Primary Action Button):",
                "       - w-full h-[46px] rounded-[10px] bg-[#212625] text-white font-medium hover:bg-black transition-colors ('LOGIN' / 'GİRİŞ YAP' veya 'SIGN UP' / 'KAYIT OL').",
                "     * Bölücü (Divider):",
                "       - relative text-center my-4: '── Or ──' (veya '── Veya ──') ince yatay çizgi ve ortalanmış metin.",
                "     * Alternatif Login Tipleri / Sosyal Giriş Butonları (Social Buttons):",
                "       - grid grid-cols-2 gap-3 w-full: [Google] ve [GitHub] (veya [Facebook]) resmi marka SVG logoları ve butonları.",
                "   - Mobil (375px) Ergonomisi:",
                "     * Vitrin sütunu mobilde gizlenir (`hidden lg:flex`) veya kompakt başlık bandına dönüşür; form `px-4 sm:p-6` ile taşmadan tam oturur.",
            ])
    else:
        lines.extend([
            f"2. [{cat.upper()}] YAPISAL ANATOMİ PORT REHBERİ:",
            "   - Katman 1 (Üst Bar / Omnibar): Yapışkan (`sticky top-0 z-10`) başlık, durum rozeti ve segmented sekme/arama kontrolü.",
            "   - Katman 2 (Yükseltilmiş İçerik Kartları): Zemin kanvasından ayrışan (`bg-white` / `var(--bg-surface)`), `border` ve `shadow-sm` derinlikli etkileşim kartları.",
            "   - Katman 3 (Alt Eylem / Durum Çubuğu): Seçili öğeler veya birincil aksiyon için sabit/yüzen (`sticky bottom-0`) kontrol barı.",
        ])
    lines.extend([
        "",
        "3. DOĞRULAMA KAPISI:",
        "   - Kodlamadan sonra `python .agent/skills/musgoku/scripts/check_design_slop.py` çalıştırın (E1-E12 = 0 hata olmalı).",
        "=" * 70,
    ])
    return "\n".join(lines)


def search_themes(query: str) -> list[dict]:
    q = query.lower().strip()
    if not q:
        return []
    words = [w for w in re.split(r'\s+', q) if len(w) > 2]
    exact_matches = []
    word_matches = []

    for t in get_all_themes():
        search_blob = f"{t['name']} {t['title']} {t['category']} {t['description']} {t['ideal_for']}".lower()
        if q in search_blob:
            exact_matches.append(t)
        elif words:
            matched_words = [w for w in words if w in search_blob]
            if matched_words:
                word_matches.append((len(matched_words), t))

    word_matches.sort(key=lambda x: x[0], reverse=True)
    return exact_matches + [t for _, t in word_matches if t not in exact_matches]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Hazır Bileşen Teması Köprüsü (get_component.py)")
    parser.add_argument("--list", "-l", action="store_true", help="Tüm hazır bileşen temalarını listeler")
    parser.add_argument("--type", "-t", type=str, default=None, help="Kategoriye göre filtreler (sidebars, navbars, cards, logins, footers...)")
    parser.add_argument("--theme", type=str, default=None, help="Seçilen temanın kodunu ve detaylarını çeker")
    parser.add_argument("--search", "-s", type=str, default=None, help="Bileşen temaları arasında anahtar kelime araması yapar")
    parser.add_argument("--html", action="store_true", help="Yalnızca HTML kodunu basar")
    parser.add_argument("--css", action="store_true", help="Yalnızca CSS kodunu basar")
    parser.add_argument("--json", action="store_true", help="Makine okunur JSON çıktısı üretir")
    parser.add_argument("--verify", type=str, default=None, help="Virgülle ayrılmış tema adlarının gerçek katalogda varlığını doğrular (uydurma temaları reddeder)")
    parser.add_argument("--adapt-guide", action="store_true", help="--theme ile birlikte kullanıldığında Living Surface yapısal portlama şablonunu (STRUCTURAL PORTING BLUEPRINT) basar")
    args = parser.parse_args(argv)

    all_themes = get_all_themes()

    # 0. DOĞRULAMA (--verify)
    if args.verify is not None:
        ok, verified, invalid = verify_theme_names(args.verify)
        if args.json:
            print(json.dumps({"ok": ok, "verified": verified, "invalid": invalid}, indent=2, ensure_ascii=False))
            return 0 if ok else 1
        if not ok:
            print(f"[FAIL] Uydurma / Katalog Dışı Bileşen Teması Tespit Edildi: {', '.join(invalid)}", file=sys.stderr)
            print("Ajan Execution Receipt içinde uydurma (hallucinated) tema adı yazamaz!", file=sys.stderr)
            login_names = [t["name"] for t in all_themes if t["category"] == "logins"]
            card_names = [t["name"] for t in all_themes if t["category"] == "cards"]
            print(f"Geçerli 'logins' temaları ({len(login_names)}): {', '.join(login_names)}", file=sys.stderr)
            print(f"Geçerli 'cards' temaları ({len(card_names)}): {', '.join(card_names)}", file=sys.stderr)
            return 1
        print(f"[OK] Tüm seçilen temalar gerçek katalogda doğrulandı ({len(verified)} tema):")
        for v in verified:
            print(f"  • [{v['category']}] {v['name']} -> {v['path']}")
        return 0

    # 1. ARAMA
    if args.search:
        results = search_themes(args.search)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return 0
        print(f"\n🔍 '{args.search}' için {len(results)} hazır tema bulundu:")
        print("─" * 70)
        for r in results:
            print(f"• [{r['category']}] {r['name']} — {r['title']}")
            print(f"  {r['description']}")
            print(f"  Komut: python .agent/skills/frontend-design/scripts/get_component.py --theme {r['name']}")
            print()
        return 0

    # 2. TEK TEMA ÇEKME
    if args.theme:
        target = find_theme_by_name(args.theme)
        if not target:
            print(f"HATA: '{args.theme}' adında bir bileşen teması bulunamadı!", file=sys.stderr)
            print("Mevcut temaları görmek için: python get_component.py --list", file=sys.stderr)
            return 1

        t_dir = Path(target["path"])
        html_code = (t_dir / "index.html").read_text(encoding="utf-8", errors="replace") if (t_dir / "index.html").is_file() else ""
        css_code = (t_dir / "styles.css").read_text(encoding="utf-8", errors="replace") if (t_dir / "styles.css").is_file() else ""

        if args.json:
            output_obj = dict(target)
            output_obj["html"] = html_code
            output_obj["css"] = css_code
            print(json.dumps(output_obj, indent=2, ensure_ascii=False))
            return 0

        if args.html and not args.css:
            print(html_code)
            return 0

        if args.css and not args.html:
            print(css_code)
            return 0

        # Tam bundle çıktısı
        print("=" * 70)
        print(f"HAZIR BİLEŞEN TEMASI: {target['name']} ({target['category']})")
        print(f"Açıklama: {target['description']}")
        print(f"Konum   : {target['path']}")
        print("=" * 70)
        if args.adapt_guide:
            print("\n" + format_adapt_guide(target))
        print("\n<!-- ═══ HTML ISKELETI (index.html) ═══ -->")
        print(html_code)
        print("\n/* ═══ CSS STILLERI (styles.css) ═══ */")
        print(css_code)
        print("\n" + "=" * 70)
        return 0

    # 3. KATEGORİ VEYA TÜMÜNÜ LİSTELEME
    cat_filter = args.type.lower().strip() if args.type else None
    if cat_filter:
        # Tekil/çoğul normalizasyonu (sidebar -> sidebars)
        if not cat_filter.endswith("s") and cat_filter + "s" in CATEGORIES:
            cat_filter = cat_filter + "s"
        filtered = [t for t in all_themes if t["category"] == cat_filter]
    else:
        filtered = all_themes

    if args.json:
        print(json.dumps(filtered, indent=2, ensure_ascii=False))
        return 0

    print("=" * 70)
    print(f"FRONTEND-DESIGN HAZIR BİLEŞEN KÜTÜPHANESİ ({len(filtered)} / {len(all_themes)} Tema)")
    print("=" * 70)

    # Kategoriye göre grupla
    by_cat: dict[str, list[dict]] = {}
    for t in filtered:
        by_cat.setdefault(t["category"], []).append(t)

    for cat_name, themes in sorted(by_cat.items()):
        print(f"\n📁 [{cat_name.upper()}] ({len(themes)} tema):")
        for t in themes:
            print(f"  • {t['name']:<36} {t['description'][:60]}")

    print("\n" + "─" * 70)
    print("Kullanım İpucu:")
    print("  python get_component.py --theme <tema-adi>         (Tüm HTML + CSS kodunu çeker)")
    print("  python get_component.py --search <kelime>          (Anahtar kelimeyle tema arar)")
    print("  python get_component.py --type <kategori>          (Kategoriye göre listeler)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
