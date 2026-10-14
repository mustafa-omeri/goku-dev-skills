#!/usr/bin/env python3
"""i18n denetleyicisi — hardcode metin, eksik anahtar ve çeviri boşluğu.

Neden var?
----------
Bir i18n projesinde en sık ve en sessiz ihlal şudur:

    t('stats.activity', 'Platform Aktivitesi')

i18next anahtarı bulamazsa `defaultValue`'ya düşer. Anahtar hiçbir sözlükte
tanımlı değilse bu **her dilde** Türkçe metin gösterir — kullanıcı İngilizce
seçse bile. Proje testleri bunu yakalamaz: anahtar kümesi tr ile en arasında
senkron olduğu için "eksik anahtar yok" denir, oysa ikisi de eksiktir.

Bu script o boşluğu kapatır ve `defaultValue` tuzağını gözle görünür kılar.

Kontroller
----------
E1 sözlük senkronu        tüm diller birebir aynı anahtar kümesinde mi
E2 boş değer              çeviri boş bırakılmış mı
E3 eksik anahtar          kodda çağrılan her t() anahtarı tanımlı mı   <-- asıl kapı
E4 defaultValue tuzağı    t(key, 'sabit metin') deseni kullanılmış mı
E5 hardcode metin         kaynakta `t()` olmadan Türkçe UI metni var mı
E6 çeviri kalıntısı       yabancı dil sözlüğünde Türkçe değer kalmış mı
E7 placeholder uyumu      {{degisken}} yer tutucuları tüm dillerde eşit mi

E3 ve E4 hata (exit 1) · E5-E6 uyarı · E1-E2-E7 hata · exit 2 = araç hatası

Kullanım
--------
    python .agent/skills/i18n-localization/scripts/i18n_checker.py
    python .agent/skills/i18n-localization/scripts/i18n_checker.py --json
    python .agent/skills/i18n-localization/scripts/i18n_checker.py --strict

Ortam
-----
I18N_PROJECT_ROOT   proje kökünü elle verir (yoksa çalışma dizininden aranır)
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

# --- Türkçe tespiti -------------------------------------------------------------
# Kural: bir metin Türkçedir en az biri doğruysa.
# 1) Türkçeye özgü harf: ç ğ ı İ ö ş ü. "i" tek başına asla işaret değildir.
# 2) Sözlükteki Türkçe kökler. Morfoloji eklentileri için kök başlangıcı yeter.
#    Liste KASITLI olarak dardır: İngilizce karşılığı olan kökler (total,
#    sonuç, liste, uygulama) ve İngilizce kelimeye benzeyenler (trend)
#    çıkarıldı. Geniş liste "Trending Categories"i Türkçe sayardı — uyarının
#    güvenilir olması, hassas olmasından önemlidir.
TR_UNIQUE_CHARS = set("çÇğĞıİöÖşŞüÜ")
TR_ROOTS = re.compile(
    r"(?:^|[^A-Za-zÇĞİÖŞÜçğıöşü])(?:"
    r"kaydet|vazgeç|görüntülenme|katılımcı|tümünü|tümü|başarıyla|"
    r"düzenle|giriş|çıkış|kullanıcı|şifre|parola|başlık|açıklama|"
    r"sağlık|eğlence|kültür|yayın|arşiv|hata|başarılı|başarısız|özet|"
    r"kategori|abone|etkinlik|yorum|beğeni|paylaş|kopyala|bulunamadı|"
    r"oluştur|üzgün|sorun|zorunlu|yeniden|istatistik|etkin|bildirim|"
    r"onayla|iptal|dosya|kapat|menü|profil|ayar|ödeme|devam|önceki|"
    r"sonraki|bilinmiyor|okundu|resim|ayarlar|yapamaz|edemez|görünen"
    r"|ana sayfa|sayım"
    r")(?:[^A-Za-zÇĞİÖŞÜçğıöşü]|$)",
    re.IGNORECASE,
)

# Kaynak taranacak uzantılar
SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte"}
# Taranmayacak klasörler. `supabase/functions` **edge backend**'dir — tarayıcıda
# görünmez, çeviri kapsamı dışıdır. `scripts` CLI araçlarıdır. `e2e` testlerdir.
SKIP_DIRS = {
    "node_modules", "dist", "build", "coverage", ".git", "__pycache__",
    ".next", ".nuxt", "out", "vendor", "__snapshots__", "supabase",
    "scripts", "e2e", "migrations", "functions", "public",
}
# Test dosyaları — içlerindeki Türkçe genelde fixture/veri, UI metni değil
TEST_SUFFIXES = (".test.", ".spec.", "_test.", ".stories.", ".cy.")
# E5'te UI metni sayılmayacak satırlar: konsol logu, hata nesnesi, uyarı.
# Bunlar kullanıcıya **görünmez** (ya konsola gider ya hata yolunda kalır).
#
# `includes`/`replace`/`startsWith` eklendi: bunlar **hata mesajı eşleme** ve
# **metin normalizasyonu** mantığıdır. `m.includes('gerekçe')` Türkçe bir UI
# metni değil, bir hata sınıfını ayırt etme kuralıdır. Aynı şekilde
# `.replace(/ı/g, 'i')` arama motoru normalizasyonudur.
NON_UI_MARKERS = re.compile(
    r"\bthrow\b|\bconsole\.(log|info|warn|error|debug)\b|new Error\(|alert\(|"
    r"\.includes\(|\.replace\(|\.replaceAll\(|\.startsWith\(|\.endsWith\(|"
    r"\.indexOf\(|\.lastIndexOf\(|process\.env"
)
# Rota / URL deseni. `/kategori/:slug` bir **adres**tir, çeviri değildir —
# slug'ı çevirirseniz URL her dilde değişir ve linkler kırılır.
URL_MARKER = re.compile(r"""(?:path|to|href|src|action)\s*=\s*\{?\s*[`'"][^`'"]*/""")
# Şema/validasyon katmanı (Zod, Yup, Joi, class-validator…). Bunlar **React
# bileşeni değildir**: `useTranslation()` hook'una erişemezler, dolayısıyla
# mesajın içine doğrudan `t()` yazılamaz. Doğru çözüm mesajı i18n **anahtarı**
# olarak taşımak ve form render katmanında çevirmektir — ayrı bir refactor.
# Script bu satırları "çeviri gerektiren yapı" olarak ayrı koda (E8) böler,
# kapıyı kırmaz ama unutulmaz.
SCHEMA_MARKER = re.compile(
    r"\bz\.(?:string|number|object|array|boolean)\b|\.(?:min|max|regex|email|url|uuid|length)\s*\(|"
    r"\byup\.|class-validator|@Is[A-Z]"
)

# Dil adı -> dil ailesi. Sözlük dosya adından çıkarılır.
SOURCE_LANG_HINTS = {"en", "en_us", "en-gb", "de", "fr", "es", "it", "nl", "pt", "ru", "ja", "zh"}
TARGET_LANG_HINTS = {"tr", "tr_tr", "tr-tr"}


def looks_turkish(text: str) -> bool:
    """Metinde Türkçe izi var mı? (Türkçe sözlüğü için de kullanılır)"""
    if not text:
        return False
    if any(ch in TR_UNIQUE_CHARS for ch in text):
        return True
    return bool(TR_ROOTS.search(text))


# --- proje kökü ve dosya keşfi --------------------------------------------------
def find_project_root() -> Path:
    override = os.environ.get("I18N_PROJECT_ROOT")
    if override:
        return Path(override).resolve()
    start = Path.cwd().resolve()
    for candidate in (start, *start.parents):
        if (candidate / "package.json").is_file() or (candidate / ".git").exists():
            return candidate
    return start


LOCALE_DIR_CANDIDATES = (
    "src/locales", "src/i18n/locales", "src/lang", "src/langs",
    "locales", "lang", "i18n/locales", "public/locales",
)


def find_locale_dir(root: Path, explicit: str | None) -> Path | None:
    if explicit:
        p = (root / explicit).resolve()
        return p if p.is_dir() else None
    for rel in LOCALE_DIR_CANDIDATES:
        p = root / rel
        if p.is_dir():
            return p
    # src altında herhangi bir yerde *locales* / *lang* klasörü
    for base in (root / "src", root):
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and child.name in {"locales", "lang", "langs", "i18n", "translations"}:
                return child
    return None


def load_dictionaries(locale_dir: Path) -> dict[str, dict]:
    """{dil: {duz.yol: deger}} — her .json/.ts/.js sözlük dosyası bir dildir."""
    out: dict[str, dict] = {}
    for path in sorted(locale_dir.iterdir()):
        if not path.is_file():
            continue
        name = path.name
        if name.startswith(("tr", "en", "es", "de", "fr", "it", "nl", "pt", "ru", "ja", "zh")):
            lang = name.split(".")[0]
        else:
            continue
        try:
            if path.suffix == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix in {".ts", ".js"}:
                # export default { ... } — sözlük nesnesi
                raw = path.read_text(encoding="utf-8")
                raw = re.sub(r"^\s*(export\s+default|export\s+const\s+\w+\s*=)\s*", "", raw, flags=re.M)
                data = json.loads(raw.rstrip().rstrip(";").strip())
            else:
                continue
        except (json.JSONDecodeError, OSError) as exc:
            raise SystemExit(f"HATA: {path} okunamadi -> {exc}")
        if not isinstance(data, dict):
            continue
        if lang in out:
            data = {**out[lang], **data}
        out[lang] = flatten(data)
    return out


def flatten(obj, prefix: str = "") -> dict:
    """İç içe sözlük -> düz anahtar yolu. Liste ve çalışma zamanı ifadesi atlanır."""
    out: dict = {}
    if not isinstance(obj, dict):
        return out
    for key, value in obj.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def strip_comments(text: str) -> str:
    """Yorumları boşlukla değiştirir — satır sayısı korunur, JSX metni kalır."""
    out = list(text)
    i, n = 0, len(text)
    quote: str | None = None
    while i < n:
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'`":
            quote = ch
            i += 1
            continue
        if text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j == -1 else j
            for k in range(i, j):
                out[k] = " "
            i = j
            continue
        if text.startswith("/*", i):
            j = text.find("*/", i)
            j = n if j == -1 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        i += 1
    return "".join(out)


def source_files(root: Path, locale_dir: Path | None) -> list[Path]:
    # `src/` varsa **yalnız** o taranır. Yoksa proje kökü taranır (src'siz
    # projeler: düz HTML/JS, CDN kütüphaneleri). Kök taraması `SKIP_DIRS`
    # ile daraltılır — aksi halde `supabase/`, `scripts/`, `public/` kapsama girer.
    bases = [root / "src"] if (root / "src").is_dir() else [root]
    seen: set[Path] = set()
    out: list[Path] = []
    for base in bases:
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.suffix not in SOURCE_SUFFIXES or not path.is_file():
                continue
            if SKIP_DIRS & set(path.parts):
                continue
            if locale_dir and locale_dir in path.parents:
                continue
            if any(mark in path.name for mark in TEST_SUFFIXES):
                continue
            if path not in seen:
                seen.add(path)
                out.append(path)
    return sorted(out)


# --- t() cagrisi cikarimi ------------------------------------------------------
# t('a.b') · t("a.b") · t(`a.b`) · t('a.b', 'varsayilan')
CALL = re.compile(
    r"""\bt\(\s*(['"`])([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)\1\s*(?:,\s*(['"`])(.*?)\3\s*)?\)""",
    re.DOTALL,
)
# Dinamik anahtar: t(`status.${x}`) — şablon, denetlenemez
DYNAMIC = re.compile(r"""\bt\(\s*`[^`]*\$\{[^`]*`""")


def extract_calls(text: str) -> list[tuple[str, str | None, int]]:
    """[(anahtar, defaultValue|None, satır)] — t() çağrılarını verir."""
    found: list[tuple[str, str | None, int]] = []
    for match in CALL.finditer(text):
        key, default = match.group(2), match.group(4)
        line = text[: match.start()].count("\n") + 1
        found.append((key, default, line))
    return found


def strip_t_arguments(line: str) -> str:
    """Bir satırdaki t() çağrılarının argümanlarını siler → kalan metni verir."""
    return CALL.sub("t()", line)


# --- kontroller -----------------------------------------------------------------
class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[str, str, str]] = []
        self.warnings: list[tuple[str, str, str]] = []

    def err(self, code: str, where: str, msg: str) -> None:
        self.errors.append((code, where, msg))

    def warn(self, code: str, where: str, msg: str) -> None:
        self.warnings.append((code, where, msg))


def check_dictionaries(dicts: dict[str, dict], report: Report) -> None:
    langs = sorted(dicts)
    if not langs:
        report.err("E1", "locales", "hiçbir sözlük dosyası bulunamadı")
        return
    if len(langs) < 2:
        report.err("E1", "locales", f"tek dil ({langs[0]}) — çok dilli zorunlu kural için yetersiz")
    base = dicts[langs[0]]
    for lang in langs[1:]:
        other = dicts[lang]
        only_a = sorted(set(base) - set(other))
        only_b = sorted(set(other) - set(base))
        if only_a:
            report.err("E1", f"{langs[0]}.json", f"{len(only_a)} anahtar {lang} sözlüğünde yok: {', '.join(only_a[:8])}")
        if only_b:
            report.err("E1", f"{lang}.json", f"{len(only_b)} anahtar {langs[0]} sözlüğünde yok: {', '.join(only_b[:8])}")
    for lang, flat in dicts.items():
        empty = [k for k, v in flat.items() if isinstance(v, str) and not v.strip()]
        if empty:
            report.err("E2", f"{lang}.json", f"{len(empty)} boş çeviri: {', '.join(empty[:8])}")
    _check_placeholders(dicts, report)


def _check_placeholders(dicts: dict[str, dict], report: Report) -> None:
    langs = sorted(dicts)
    if len(langs) < 2:
        return
    ref = langs[0]
    pat = re.compile(r"\{\{?\s*(\w+)\s*\}?\}")
    for lang in langs[1:]:
        mismatches = []
        for key, value in dicts[ref].items():
            a = sorted(pat.findall(value if isinstance(value, str) else ""))
            b = sorted(pat.findall(dicts[lang].get(key, "") if isinstance(dicts[lang].get(key, ""), str) else ""))
            if a != b:
                mismatches.append(f"{key}: {langs[0]}={a} {lang}={b}")
        if mismatches:
            report.err("E7", f"{lang}.json", f"{len(mismatches)} yer tutucu uyuşmazlığı: {mismatches[0]}")


def check_residue(dicts: dict[str, dict], report: Report) -> None:
    """Yabancı dil sözlüğünde kalmış Türkçe değer."""
    for lang, flat in dicts.items():
        if lang.lower().replace("-", "_") in TARGET_LANG_HINTS:
            continue
        bad = [(k, v) for k, v in flat.items() if isinstance(v, str) and looks_turkish(v)]
        if bad:
            preview = "; ".join(f"{k}={v!r}" for k, v in bad[:3])
            report.warn("E6", f"{lang}.json", f"{len(bad)} değerde Türkçe izi var: {preview}")


def check_calls(files: list[Path], dicts: dict[str, dict], root: Path, report: Report) -> None:
    all_keys = set().union(*dicts.values()) if dicts else set()
    for path in files:
        rel = path.relative_to(root).as_posix()
        text = strip_comments(path.read_text(encoding="utf-8"))
        for key, default, line in extract_calls(text):
            if key not in all_keys:
                shown = f" -> ekranda {default!r}" if default else " -> ekranda anahtar adı"
                report.err(
                    "E3", f"{rel}:{line}",
                    f"t('{key}') hiçbir sözlükte tanımlı değil{shown}",
                )
            elif default is not None and default.strip():
                report.warn(
                    "E4", f"{rel}:{line}",
                    f"t('{key}', {default!r}) — anahtar sözlükte var, defaultValue kullanılmamalı",
                )
            elif default is not None:
                report.warn("E4", f"{rel}:{line}", f"t('{key}', '') — boş defaultValue nedensiz")
        for match in DYNAMIC.finditer(text):
            line = text[: match.start()].count("\n") + 1
            report.warn(
                "E3", f"{rel}:{line}",
                "dinamik anahtar t(`...${...}`) — denetlenemez; anahtar kümesini üretimde doğrula",
            )


def check_hardcoded(files: list[Path], root: Path, report: Report) -> None:
    for path in files:
        rel = path.relative_to(root).as_posix()
        cleaned = strip_comments(path.read_text(encoding="utf-8"))
        hits = 0
        schema_hits = 0
        samples: list[str] = []
        for n, line in enumerate(cleaned.splitlines(), 1):
            body = strip_t_arguments(line)
            body = re.sub(r"^\s*(import|export|from)\b.*$", "", body)
            body = re.sub(r"\buseTranslation\b|\bi18n\b|\blanguage\b", "", body)
            if NON_UI_MARKERS.search(body) or URL_MARKER.search(body):
                continue
            if not looks_turkish(body):
                continue
            if SCHEMA_MARKER.search(line):
                schema_hits += 1
                if len(samples) < 3:
                    samples.append(f"L{n}: {line.strip()[:90]}")
                continue
            hits += 1
            if len(samples) < 3:
                samples.append(f"L{n}: {line.strip()[:90]}")
        if hits:
            report.warn(
                "E5", rel,
                f"{hits} satırda t() olmadan Türkçe metin · " + " · ".join(samples),
            )
        if schema_hits:
            report.warn(
                "E8", rel,
                f"{schema_hits} validasyon mesajı Türkçe — bu katman React değil, t() "
                f"çağrılamaz. Mesajı i18n anahtarı olarak taşı ve form render "
                f"katmanında çevir · " + " · ".join(samples),
            )


# --- giriş noktası --------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="i18n denetleyicisi")
    parser.add_argument("--locales", help="sözlük klasörü (varsayılan: src/locales)")
    parser.add_argument("--root", help="proje kökü (varsayılan: çalışma dizininden aranır)")
    parser.add_argument("--json", action="store_true", help="makine okunur çıktı")
    parser.add_argument("--strict", action="store_true", help="uyarıları da hata say")
    parser.add_argument("--no-hardcode", action="store_true", help="E5 taramasını atla (büyük projeler)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else find_project_root()
    if not root.is_dir():
        print(f"HATA: proje kökü yok -> {root}", file=sys.stderr)
        return 2
    locale_dir = find_locale_dir(root, args.locales)
    if locale_dir is None:
        print(f"HATA: sözlük klasörü bulunamadı -> {root}. --locales ile belirt", file=sys.stderr)
        return 2

    try:
        dicts = load_dictionaries(locale_dir)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2

    files = source_files(root, locale_dir)
    report = Report()
    check_dictionaries(dicts, report)
    check_residue(dicts, report)
    check_calls(files, dicts, root, report)
    if not args.no_hardcode:
        check_hardcoded(files, root, report)

    langs = sorted(dicts)
    keys = len(next(iter(dicts.values()))) if dicts else 0

    if args.json:
        print(json.dumps({
            "root": str(root),
            "localeDir": str(locale_dir),
            "languages": langs,
            "keyCount": keys,
            "sourceFiles": len(files),
            "errors": [{"code": c, "where": w, "message": m} for c, w, m in report.errors],
            "warnings": [{"code": c, "where": w, "message": m} for c, w, m in report.warnings],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"KOK   : {root}")
        print(f"SOZLUK: {locale_dir}  ({', '.join(langs)} · {keys} anahtar)")
        print(f"KAYNAK: {len(files)} dosya")
        for code, where, msg in report.errors:
            print(f"  [HATA]   {code} {where}\n          {msg}", file=sys.stderr)
        for code, where, msg in report.warnings:
            print(f"  [uyari]  {code} {where}\n          {msg}", file=sys.stderr)
        if report.errors:
            print(f"\n[FAIL] {len(report.errors)} hata · {len(report.warnings)} uyari", file=sys.stderr)
        else:
            print(f"\n[OK] Anahtar eksigi yok. ({len(report.warnings)} uyari)")
            for code, where, msg in report.warnings[:3]:
                print(f"  [uyari]  {code} {where}: {msg}")
            if len(report.warnings) > 3:
                print(f"  ... +{len(report.warnings) - 3} uyari")

    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())