#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dağıtım aracı — skillSetWorks/.agent/ ağacını config'te listelenen projelere kopyalar.

Config kaynağı: delivery.md içindeki ```json delivery.config``` bloğu.
Bu dosya delivery.md'yi *okur*, *yazmaz* — config'in tek sahibi delivery.md'dir.

Kullanım:
    python delivery.py                  # enabled:true olan tüm projeler
    python delivery.py --dry-run        # hiçbir şey değiştirmeden ne olacağını göster
    python delivery.py --only ocai      # tek proje
    python delivery.py --list           # projeleri ve enable/disable durumunu listele

Yaptığı:
    1. yol doğrulama        5. kopyalama      (.agent/ temizlenerek)
    2. yedek                6. proje kurallarını geri yazma
    3. proje kuralı çıkarma  7. doğrulama
    4. eski .agent silme

Yapmadığı:
    git commit / push / branch — hiçbir git komutu çalıştırmaz.
    Proje kökündeki HANDOFF.md, knowledge-base.md, docs/, src/ — dokunmaz.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Windows konsol kodu sayfa 1254'tur ve Unicode karakter basmayi engeller.
# Ciktinin her zaman UTF-8 yazilmasi icin akis yeniden yapilandirilir.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
DELIVERY_MD = HERE / "delivery.md"
SCOUT_TARGETS_MD = HERE / "scout" / "targets.md"
CONFIG_RE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
PROJECT_BLOCK_HEADING = "## Proje Bazlı Ek Kurallar"
# Baslik yalnizca SATIR BASINDA olabilir. §10 gibi bolumler metin icinde
# `## Proje Bazlı Ek Kurallar` diye *satır ici referans* verir; ilk eslesmeyi
# almak projeyi o referanstan keser. Ayrica bolum "en sondaki" bolumdur:
# birden fazla satir basi eslesmesi varsa sonuncusu alinir.
PROJECT_BLOCK_RE = re.compile(
    r"^## Proje Bazlı Ek Kurallar[ \t]*\r?$", re.MULTILINE
)
# Bazı projelerde bolum basligi kaybolmus ya da yarım kesilmis olabilir
# (bkz. ocai / FEProjectv1: §10'un son satiri backtick ile kapandi mi diye
# bakmadan kesilmis ve baslik satirı hiç yazilmamis). Baslik bulunamazsa
# proje blogunun basladigi garanti nokta olan bu isaret satirina düşülür.
PROJECT_BLOCK_MARKER_RE = re.compile(
    r"^> Bu bölüm \*\*projeye özeldir", re.MULTILINE
)

GREEN, RED, YELLOW, DIM, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"
)


def colour(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if sys.stdout.isatty() else text


# --- config ------------------------------------------------------------------

def load_config(path: Path) -> dict:
    if not path.is_file():
        sys.exit(f"HATA: {path} bulunamadi.")

    # 1. scout/targets.md dosyası ise scout.targets motoru ile çöz
    if path.name == "targets.md" or (SCOUT_TARGETS_MD.is_file() and path.resolve() == SCOUT_TARGETS_MD.resolve()):
        try:
            from scout.targets import build_delivery_config_from_targets
            base_config = {}
            if DELIVERY_MD.is_file():
                try:
                    match = CONFIG_RE.search(DELIVERY_MD.read_text(encoding="utf-8"))
                    if match:
                        base_config = json.loads(match.group(1))
                except Exception:
                    pass
            return build_delivery_config_from_targets(path, base_config=base_config)
        except Exception as e:
            sys.exit(f"HATA: {path} hedefleri çözümlenemedi -> {e}")

    # 2. Standart ```json ... ``` bloğu içeren dosya (delivery.md vb.)
    match = CONFIG_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        try:
            from scout.targets import build_delivery_config_from_targets
            return build_delivery_config_from_targets(path)
        except Exception:
            sys.exit(f"HATA: {path.name} icinde ```json ... ``` config blogu yok.")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        sys.exit(f"HATA: config JSON ayristirilamadi -> {exc}")


def resolve_source(config: dict) -> Path:
    raw = Path(config["source"])
    return raw if raw.is_absolute() else HERE / raw


# --- yardimcilar -------------------------------------------------------------

def dir_stats(path: Path) -> tuple[int, int]:
    if not path.is_dir():
        return 0, 0
    files = [f for f in path.rglob("*") if f.is_file()]
    return len(files), sum(f.stat().st_size for f in files)


def looks_like_project(path: Path) -> bool:
    markers = (".git", "package.json", "pom.xml", "build.gradle", "build.gradle.kts")
    return any((path / m).exists() for m in markers)


def find_project_block(text: str) -> int:
    """Proje kurali bolumunun gercek baslangic offset'ini dondurur.

    Oncelik sirasi:
      1. Satir basi `## Proje Bazlı Ek Kurallar` basligi — en sondaki eslesme.
         Satir ici referanslar (`\\`## ...\\`) ve once gelen baska basliklar disarida kalir.
      2. Baslik yoksa/yArikmis ise `> Bu bölüm **projeye özeldir` isareti.
         Bu isaret blogun ilk satiri oldugu icin her zaman guvenilirdir.
    Donmezse -1.
    """
    matches = list(PROJECT_BLOCK_RE.finditer(text))
    if matches:
        return matches[-1].start()
    markers = list(PROJECT_BLOCK_MARKER_RE.finditer(text))
    return markers[-1].start() if markers else -1


def extract_project_block(agents_md: Path) -> str | None:
    """Proje kurali blogunu dondurur. Icerik yoksa None.

    Baslik her zaman yeniden yazilir: cikti her zaman gecerli bir
    `## Proje Bazlı Ek Kurallar` basligiyla baslar, boylece yarim kesik
    basliktan gelen bir proje dosyasi kendini onarir.
    """
    if not agents_md.is_file():
        return None
    text = agents_md.read_text(encoding="utf-8")
    index = find_project_block(text)
    if index == -1:
        return None
    body = text[index:]
    # baslik zaten basliyorsa tekrar etme
    if PROJECT_BLOCK_RE.match(body):
        body = body[len(PROJECT_BLOCK_HEADING):].lstrip("\r\n")
    meaningful = [
        ln.strip() for ln in body.splitlines()
        if ln.strip() and not ln.strip().startswith(">")
        and not ln.strip().startswith("#") and "_(" not in ln
    ]
    if not meaningful:
        return None
    return PROJECT_BLOCK_HEADING + "\n\n" + body.rstrip() + "\n"


PLACEHOLDER_BLOCK = """## Proje Bazlı Ek Kurallar

> Bu bölüm **projeye özeldir** ve `.agent/` klasörüyle birlikte projeye dağıtılır.
> Altında yalnızca bu projenin kendi gereksinimi yazılır — genel kural değil.
> Bu bölüme yazarken §10'daki mükerrerlik kontrolü zorunludur.

### Bu proje için ek kurallar

_(Henüz bu projeye özel ek bir kural tanımlanmamıştır. Bir kural gerektiğinde:
önce §10 mükerrerlik kontrolü, sonra aşağıya `### <Kural Adı>` başlığı altında
tek paragraf olarak ekle.)_
"""


def inject_project_block(agents_md: Path, block: str | None) -> str:
    """Yeni AGENTS.md icindeki bolumu hedef projenin bloguyla degistirir.

    Dondurulen: "yazildi" | "temizlendi" | "yok"

    ONEMLI: `block` None ise bolum **kaynagin placeholder'ina sifirlanir.**
    Aksi halde kaynagin (skillSetWorks) proje kurallari, kendi kural blogu
    olmayan yeni bir projeye sizar. Bu sessiz bir kirlilik olurdu.
    """
    if not agents_md.is_file():
        return "yok"
    text = agents_md.read_text(encoding="utf-8")
    index = find_project_block(text)
    replacement = block if block else PLACEHOLDER_BLOCK
    if index == -1:
        agents_md.write_text(text.rstrip() + "\n\n" + replacement, encoding="utf-8")
        return "yazildi" if block else "temizlendi"
    agents_md.write_text(text[:index] + replacement, encoding="utf-8")
    return "yazildi" if block else "temizlendi"


def backup_root(config: dict) -> Path:
    raw = Path(config.get("backupRoot", "yedekler"))
    return raw if raw.is_absolute() else HERE / raw


# Yedek klasörü adı: `<proje-id>-agent-YYYYMMDD-HHMMSS`. Kesirli adlar
# (eski kaynak yedekleri, `*-cursor-rules-*`) ASLA silinmez.
BACKUP_STAMP_RE = re.compile(r"^.+-agent-\d{8}-\d{6}$")


def create_backup(agent: Path, project: dict, config: dict, stamp: str) -> Path | None:
    """Hedefteki `.agent/` agacini yedekler. Yoksa None doner."""
    if not agent.is_dir():
        return None
    target = backup_root(config) / f"{project['id']}-agent-{stamp}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(agent, target, ignore=shutil.ignore_patterns("__pycache__"))
    return target


def prune_backups(config: dict, keep: int) -> tuple[int, int]:
    """Her proje icin en yeni `keep` yedegi birakir, eskisini siler.

    Geri donus: (silinen klasor sayisi, kazanilan MB).
    Yalniz `<id>-agent-<tarih>` bicimli klasorler silinir; eski kaynak
    yedekleri (`*-cursor-rules-*`, `ui-ux-pro-max-eski-*`) korunur.
    """
    root = backup_root(config)
    if not root.is_dir():
        return 0, 0

    removed = 0
    freed = 0
    for project in config["projects"]:
        prefix = f"{project['id']}-agent-"
        backups = sorted(
            d for d in root.iterdir()
            if d.is_dir() and d.name.startswith(prefix) and BACKUP_STAMP_RE.match(d.name)
        )
        stale = backups[:max(0, len(backups) - keep)]
        for old in stale:
            size = sum(f.stat().st_size for f in old.rglob("*") if f.is_file())
            shutil.rmtree(old)
            removed += 1
            freed += size
            print(colour(f"   eski yedek silindi: {old.name}"
                         f" ({size // 1024 // 1024} MB)", DIM))
    return removed, freed // 1024 // 1024


def copy_tree(source: Path, target: Path) -> tuple[int, int]:
    """Hedefi tamamen siler, sonra kaynagi kopyalar. Gecici dosyalar gelmez."""
    if target.is_dir():
        shutil.rmtree(target)
    shutil.copytree(
        source, target,
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".pytest_cache", ".coverage", "htmlcov"
        ),
    )
    return dir_stats(target)


def tree_index(root: Path) -> dict[str, str]:
    """Klasördeki her dosyanin göreli yolu -> sha256. Gecici dosyalar haric."""
    ignore = {"__pycache__", ".pytest_cache", ".coverage", "htmlcov"}
    out: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix == ".pyc":
            continue
        if any(part in ignore for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def root_files(config: dict, source: Path) -> list[Path]:
    """`.agent/` disinda, proje kokune dagitilan yonetilen dosyalar."""
    return [source.parent / name for name in config.get("rootFiles", [])]


def distribute_root_files(config: dict, source: Path, project: Path) -> tuple[int, int]:
    """Kok dosyalari proje kokune kopyalar. Doner: (yazilan, atlanan)."""
    written = skipped = 0
    for src in root_files(config, source):
        if not src.is_file():
            print(colour(f"   kok dosya: {src.name} kaynakta yok — ATLANDI", YELLOW))
            skipped += 1
            continue
        target = project / src.name
        shutil.copy2(src, target)
        written += 1
    return written, skipped


def verify_root_files(config: dict, source: Path, project: Path) -> list[str]:
    """Kok dosyalarin hedefte kaynakla ayni oldugunu dogrular."""
    problems = []
    for src in root_files(config, source):
        target = project / src.name
        if not target.is_file():
            problems.append(f"kok dosya eksik: {src.name}")
        elif hashlib.sha256(src.read_bytes()).hexdigest() != \
                hashlib.sha256(target.read_bytes()).hexdigest():
            problems.append(f"kok dosya farkli: {src.name}")
    return problems


def verify(project: dict, source: Path, config: dict) -> bool:
    """Dagitim butunlugunu kanitla: hedef agac kaynakla dosya dosya ayni mi?

    `AGENTS.md` haric tutulur — her projede proje-ozel `Proje Bazlı Ek Kurallar`
    blogu farklidir ve o farklilik beklenir.
    """
    name = project["name"]
    target = Path(project["path"]) / ".agent"
    if not target.is_dir():
        print(colour(f"── {name}", BOLD))
        print(colour("   ✗ .agent/ yok — dağıtım yapılmamış", RED))
        return False

    src, dst = tree_index(source), tree_index(target)
    # AGENTS.md her projede farklıdır
    src.pop("AGENTS.md", None)
    dst.pop("AGENTS.md", None)

    missing = sorted(set(src) - set(dst))
    extra = sorted(set(dst) - set(src))
    differing = sorted(k for k in set(src) & set(dst) if src[k] != dst[k])
    root_problems = verify_root_files(config, source, Path(project["path"]))

    print(colour(f"── {name}", BOLD))
    print(f"   kaynak {len(src)} dosya · hedef {len(dst)} dosya")
    if missing:
        print(colour(f"   ✗ EKSİK {len(missing)}:", RED))
        for item in missing[:10]:
            print(colour(f"       - {item}", RED))
    if extra:
        print(colour(f"   ~ fazla {len(extra)} (hedefe özgü olabilir):", YELLOW))
        for item in extra[:5]:
            print(colour(f"       + {item}", YELLOW))
    if differing:
        print(colour(f"   ✗ İÇERİK FARKLI {len(differing)}:", RED))
        for item in differing[:10]:
            print(colour(f"       ~ {item}", RED))
    for problem in root_problems:
        print(colour(f"   ✗ {problem}", RED))
    if not (missing or differing or root_problems):
        print(colour("   ✓ TAM — kaynakla byte-byte aynı "
                     "(.agent/ + yönetilen kök dosyalar)", GREEN))
        return True
    return False


# --- dogrulama ---------------------------------------------------------------

def validate(target: Path) -> list[str]:
    problems: list[str] = []
    skills_dir = target / "skills"
    if not skills_dir.is_dir():
        return ["skills/ dizini yok"]

    skills = sorted(d for d in skills_dir.iterdir() if d.is_dir())
    for skill in skills:
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            problems.append(f"{skill.name}: SKILL.md yok")
            continue
        raw = skill_md.read_bytes()
        if raw[:3] == b"\xef\xbb\xbf":
            problems.append(f"{skill.name}: UTF-8 BOM var (frontmatter okunamaz)")
        text = raw.decode("utf-8", errors="replace")
        if not text.startswith("---"):
            problems.append(f"{skill.name}: frontmatter acilisi yok")
            continue
        name = re.search(r"^name:\s*(\S+)", text, re.MULTILINE)
        if not name:
            problems.append(f"{skill.name}: 'name:' alani yok")
        elif name.group(1) != skill.name:
            problems.append(f"{skill.name}: name='{name.group(1)}' klasör adiyla uyusmuyor")

    for md in target.rglob("*.md"):
        text = md.read_text(encoding="utf-8", errors="replace")
        for link in re.findall(r"\]\((\.{1,2}/[^)#]+)\)", text):
            resolved = (md.parent / link).resolve()
            if not resolved.exists():
                problems.append(f"{md.relative_to(target)}: kırık baglanti {link}")

    rules = target / "rules"
    if not (rules / "skill-trigger-routing.md").is_file():
        problems.append("rules/skill-trigger-routing.md yok (tetikleme sözlüğü eksik)")

    # Proje kurali bolumu yerinde mi? Merge sirasinda kaybolmus olabilir.
    agents = target / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8", errors="replace")
        count = len(PROJECT_BLOCK_RE.findall(text))
        if count != 1:
            problems.append(
                f"AGENTS.md: '{PROJECT_BLOCK_HEADING}' basligi {count} kez bulundu "
                f"(1 olmali) — proje kurali blogu kaybolmus ya da tekrar etmis"
            )
    return problems


# --- ana akis ----------------------------------------------------------------

def distribute(project: dict, source: Path, config: dict, dry: bool,
               skip_backup: bool = False) -> bool:
    name = project["name"]
    path = Path(project["path"])

    print()
    print(colour(f"── {name}", BOLD))
    print(colour(f"   {path}", DIM))

    if not path.is_dir():
        print(colour(f"   ✗ yol bulunamadi — ATLANDI", RED))
        return False
    if not looks_like_project(path):
        print(colour("   ✗ proje isareti yok (.git/package.json/pom.xml) — ATLANDI", RED))
        return False

    agent = path / ".agent"
    old_files, old_bytes = dir_stats(agent)
    old_skills = len([d for d in (agent / "skills").iterdir() if d.is_dir()]) \
        if (agent / "skills").is_dir() else 0

    print(f"   mevcut : {old_files} dosya / {old_bytes // 1024} KB · {old_skills} skill")

    block = extract_project_block(agent / "AGENTS.md")
    print(colour("   proje kuralları: " + ("VAR — korunacak" if block else "yok"), DIM))

    src_files, src_bytes = dir_stats(source)
    src_skills = len([d for d in (source / "skills").iterdir() if d.is_dir()])
    print(f"   kaynak : {src_files} dosya / {src_bytes // 1024} KB · {src_skills} skill")

    if dry:
        print(colour("   [DRY-RUN] yedek + temizle + kopyala + yaz + dogrula YAPILMAZ", YELLOW))
        return True

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if skip_backup:
        print(colour("   yedek  : atlandi (--no-backup)", YELLOW))
    else:
        target_backup = create_backup(agent, project, config, stamp)
        if target_backup:
            print(f"   yedek  : {target_backup.relative_to(HERE)}")
        else:
            print(colour("   yedek  : yok (hedefte .agent/ bulunmadi)", YELLOW))

    new_files, new_bytes = copy_tree(source, agent)
    print(colour(f"   kopyala: {new_files} dosya / {new_bytes // 1024} KB", GREEN))

    written, skipped = distribute_root_files(config, source, path)
    if written:
        names = ", ".join(f.name for f in root_files(config, source))
        print(colour(f"   kok dosya: {written} yazıldı ({names})", GREEN))
    if skipped:
        print(colour("   kok dosya: bazıları atlandı", YELLOW))

    injected = inject_project_block(agent / "AGENTS.md", block)
    if injected == "yazildi":
        print(colour("   kurallar: proje blogu geri yazildi", GREEN))
    elif injected == "temizlendi":
        print(colour("   kurallar: hedefte proje blogu yok — kaynak placeholder'ina "
                     "sifirlandi (kirlilik onlendi)", YELLOW))
    else:
        print(colour("   kurallar: yazilacak proje-ozel icerik yok", DIM))

    problems = validate(agent)
    if problems:
        print(colour(f"   ✗ {len(problems)} dogrulama sorunu:", RED))
        for problem in problems[:12]:
            print(colour(f"       - {problem}", RED))
        return False
    print(colour("   dogrula: TEMIZ", GREEN))
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="skillSetWorks dagitim araci")
    parser.add_argument("--dry-run", action="store_true", help="degisiklik yapma")
    parser.add_argument("--only", metavar="ID", help="tek proje (id veya ad)")
    parser.add_argument("--list", action="store_true", help="projeleri listele ve cik")
    parser.add_argument(
        "--verify", action="store_true",
        help="dagitilan agacin kaynakla dosya dosya ayni oldugunu SHA256 ile dogrula",
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="bu kosuda yedek alma (yalniz kaynakla ayni degisse anlamli)",
    )
    parser.add_argument(
        "--keep", type=int, metavar="N", default=None,
        help="her proje icin en yeni N yedegi birak, eskisini sil (varsayilan: silme)",
    )
    parser.add_argument(
        "--prune-only", action="store_true",
        help="dagitim yapmadan yalnizca eski yedekleri temizle (--keep ile birlikte)",
    )
    parser.add_argument(
        "--config", metavar="PATH",
        help="ozel konfigurasyon dosyasi (scout/targets.md veya delivery.md)",
    )
    args = parser.parse_args()

    target_config = Path(args.config) if args.config else (SCOUT_TARGETS_MD if SCOUT_TARGETS_MD.is_file() else DELIVERY_MD)
    config = load_config(target_config)
    source = resolve_source(config)

    if args.list:
        print(colour(f"Konfigürasyon: {target_config}", BOLD))
        print(f"{'id':<26} {'enabled':<9} {'type':<10} {'stack':<18} path")
        for project in config["projects"]:
            flag = colour("EVET", GREEN) if project.get("enabled") else colour("hayir", DIM)
            stype = project.get("source_type", "single")
            print(f"{project['id']:<26} {flag:<9} {stype:<10} {project.get('stack',''):<18} {project['path']}")
        return 0

    if not source.is_dir():
        sys.exit(f"HATA: kaynak bulunamadi -> {source}")

    selected = config["projects"]
    if args.only:
        selected = [
            p for p in config["projects"]
            if args.only.lower() in (p["id"].lower(), p["name"].lower())
        ]
        if not selected:
            sys.exit(f"HATA: proje bulunamadi -> {args.only}")

    print(colour(f"KAYNAK: {source}", BOLD))
    print(colour(f"KIP: {source} -> {len(selected)} proje"
                 + ("  [DRY-RUN]" if args.dry_run else ""), DIM))

    if args.verify:
        ok, bad = 0, 0
        for project in config["projects"]:
            if not project.get("enabled"):
                continue
            if verify(project, source, config):
                ok += 1
            else:
                bad += 1
            print()
        print(colour(f"DOGRULAMA: {ok} tam · {bad} sorunlu", BOLD))
        return 0 if bad == 0 else 1

    if args.prune_only:
        keep = 1 if args.keep is None else args.keep
        print(colour(f"YEDEK TEMIZLIGI: her proje icin en yeni {keep} yedek kalacak", BOLD))
        removed, freed = prune_backups(config, keep)
        if not removed:
            print(colour("   silinecek yedek yok", DIM))
        else:
            print(colour(f"TEMIZLIK: {removed} yedek silindi · {freed} MB kazanildi", BOLD))
        return 0

    ok, skipped = 0, 0
    for project in config["projects"]:
        if not project.get("enabled"):
            print(colour(f"\n── {project['name']}", BOLD))
            print(colour(f"   {project['path']}", DIM))
            print(colour("   SKIP — enabled:false", YELLOW))
            skipped += 1
            continue
        if project not in selected:
            continue
        if distribute(project, source, config, args.dry_run, args.no_backup):
            ok += 1
        else:
            skipped += 1

    print()
    print(colour(f"TAMAM: {ok}  ·  ATLANDI/SKIP: {skipped}", BOLD))

    if args.keep is not None and not args.dry_run:
        removed, freed = prune_backups(config, max(0, args.keep))
        if removed:
            print(colour(f"TEMIZLIK: {removed} yedek silindi · {freed} MB kazanildi "
                         f"(her proje icin en yeni {max(0, args.keep)} yedek kaldi)", BOLD))
        else:
            print(colour(f"TEMIZLIK: silinecek yedek yok "
                         f"(her proje icin en yeni {max(0, args.keep)} yedek kaldi)", DIM))

    return 0 if skipped == 0 or ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
