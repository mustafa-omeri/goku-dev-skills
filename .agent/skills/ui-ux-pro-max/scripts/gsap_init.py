#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gsap_init.py - GSAP & ScrollSmoother Integration & Lifecycle Management Engine

Automates GSAP detection, package management, plugin registration,
React 18 strict mode safe initialization, and ScrollSmoother / autoscroll scaffolding.
Part of the goku-dev-skills / ui-ux-pro-max motion system.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Ensure UTF-8 output on Windows
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def check_suitability(project_dir: Path) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Inspects target project to determine if it is suitable for GSAP integration.
    Must be a web/DOM project with a package.json. Rejects pure backend or non-web projects.
    """
    pkg_json_path = project_dir / "package.json"
    if not pkg_json_path.exists():
        # Check if it's a backend or empty project
        if (project_dir / "pom.xml").exists():
            return False, "Java/Maven backend projesi tespit edildi; package.json yok. GSAP entegrasyonu atlandı.", {}
        if (project_dir / "requirements.txt").exists() or (project_dir / "pyproject.toml").exists():
            return False, "Python backend projesi tespit edildi; package.json yok. GSAP entegrasyonu atlandı.", {}
        return False, "package.json bulunamadı. GSAP yalnızca web frontend projelerine entegre edilebilir.", {}

    try:
        data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"package.json okunamadı veya JSON geçersiz: {e}", {}

    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}

    # Framework detection
    framework = "vanilla"
    if "react" in all_deps or "react-dom" in all_deps:
        framework = "react"
    elif "vue" in all_deps:
        framework = "vue"
    elif "svelte" in all_deps:
        framework = "svelte"
    elif "@angular/core" in all_deps:
        framework = "angular"
    elif "astro" in all_deps:
        framework = "astro"

    # Bundler / Tooling detection
    is_vite = "vite" in all_deps or any((project_dir / f).exists() for f in [
        "vite.config.ts", "vite.config.js", "vite.config.mjs", "vite.config.cjs"
    ])
    is_next = "next" in all_deps or (project_dir / "next.config.js").exists() or (project_dir / "next.config.mjs").exists()
    is_typescript = "typescript" in all_deps or (project_dir / "tsconfig.json").exists()

    has_gsap = "gsap" in all_deps
    has_gsap_react = "@gsap/react" in all_deps

    meta = {
        "framework": framework,
        "is_vite": is_vite,
        "is_next": is_next,
        "is_typescript": is_typescript,
        "has_gsap": has_gsap,
        "has_gsap_react": has_gsap_react,
        "project_name": data.get("name", project_dir.name),
    }

    return True, f"Uygun web projesi tespit edildi ({framework}, {'TypeScript' if is_typescript else 'JavaScript'})", meta


def detect_package_manager(project_dir: Path) -> str:
    """
    Detects package manager from lockfiles, defaulting to 'npm'.
    """
    if (project_dir / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (project_dir / "yarn.lock").exists():
        return "yarn"
    if (project_dir / "bun.lockb").exists() or (project_dir / "bun.lock").exists():
        return "bun"
    if (project_dir / "package-lock.json").exists():
        return "npm"
    return "npm"


def build_install_command(package_manager: str, framework: str = "react") -> str:
    """
    Builds the command string to install gsap and @gsap/react (for React projects).
    """
    packages = ["gsap"]
    if framework == "react":
        packages.append("@gsap/react")

    pkg_str = " ".join(packages)
    if package_manager == "pnpm":
        return f"pnpm add {pkg_str}"
    elif package_manager == "yarn":
        return f"yarn add {pkg_str}"
    elif package_manager == "bun":
        return f"bun add {pkg_str}"
    return f"npm install {pkg_str}"


def get_vite_cache_notice(project_dir: Path) -> str:
    """
    Returns advice and commands for clearing Vite's pre-bundled dependency cache.
    """
    pm = detect_package_manager(project_dir)
    run_cmd = f"{pm} run dev -- --force" if pm != "npm" else "npm run dev -- --force"
    return (
        "💡 Vite Önbellek Yenileme Uyarısı:\n"
        "Vite, node_modules/.vite dizininde bağımlılık önbelleği tutar. "
        "GSAP paketi yüklendikten sonra 'Failed to resolve import \"gsap\"' "
        "hatası almamak için geliştirme sunucusunu önbelleği temizleyerek başlatın:\n"
        f"  👉 {run_cmd}\n"
        "  (Alternatif olarak 'node_modules/.vite' klasörünü silebilirsiniz)."
    )


def scaffold_gsap(
    project_dir: Path,
    framework: str = "react",
    is_typescript: bool = True,
    dry_run: bool = False,
) -> List[str]:
    """
    Scaffolds centralized GSAP registry and smooth scroll components.
    """
    created_files: List[str] = []
    src_dir = project_dir / "src"
    if not src_dir.exists():
        src_dir = project_dir

    lib_dir = src_dir / "lib"
    comp_dir = src_dir / "components"

    ext = "ts" if is_typescript else "js"
    jsx_ext = "tsx" if is_typescript else "jsx"

    # 1. Centralized GSAP Registry: src/lib/gsap.ts
    lib_file = lib_dir / f"gsap.{ext}"
    lib_content = f"""// src/lib/gsap.{ext}
// Centralized GSAP & Plugins Singleton Architecture
// Designed for React 18+ strict-mode and SSR resilience.

import gsap from "gsap";
import {{ ScrollTrigger }} from "gsap/ScrollTrigger";

// Safely register free standard plugins
if (typeof window !== "undefined") {{
  gsap.registerPlugin(ScrollTrigger);

  // Dynamic ScrollSmoother registration (Club GSAP fallback check)
  // If ScrollSmoother is imported in a project with Club token, register it.
  try {{
    // @ts-ignore - ScrollSmoother might be Club-only
    const maybeSmoother = (gsap as any).ScrollSmoother;
    if (maybeSmoother) {{
      gsap.registerPlugin(maybeSmoother);
    }}
  }} catch (e) {{
    // Graceful fallback: ScrollSmoother not loaded
  }}
}}

/**
 * Checks if user has requested reduced motion.
 */
export const prefersReducedMotion = (): boolean => {{
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}};

/**
 * Programmatic Smooth Autoscroll Helper
 */
export const autoScrollTo = (
  target: string | HTMLElement | number,
  options?: {{
    duration?: number;
    offset?: number;
    ease?: string;
  }}
) => {{
  if (typeof window === "undefined") return;
  const {{ duration = 1, offset = 0, ease = "power2.inOut" }} = options || {{}};

  if (prefersReducedMotion()) {{
    if (typeof target === "number") {{
      window.scrollTo(0, target);
    }} else {{
      const el = typeof target === "string" ? document.querySelector(target) : target;
      el?.scrollIntoView();
    }}
    return;
  }}

  let targetY = 0;
  if (typeof target === "number") {{
    targetY = target;
  }} else {{
    const el = typeof target === "string" ? document.querySelector(target) : target;
    if (el) {{
      const rect = el.getBoundingClientRect();
      targetY = window.pageYOffset + rect.top + offset;
    }}
  }}

  gsap.to(window, {{
    duration,
    scrollTo: {{ y: targetY, autoKill: true }},
    ease,
  }});
}};

export {{ gsap, ScrollTrigger }};
export default gsap;
"""

    if not dry_run:
        lib_dir.mkdir(parents=True, exist_ok=True)
        lib_file.write_text(lib_content.strip() + "\n", encoding="utf-8")
    created_files.append(str(lib_file.relative_to(project_dir)))

    # 2. React SmoothScrollProvider Component: src/components/SmoothScroll.tsx
    if framework == "react":
        comp_file = comp_dir / f"SmoothScroll.{jsx_ext}"
        comp_content = f"""// src/components/SmoothScroll.{jsx_ext}
import React, {{ useRef, useEffect }} from "react";
import {{ useGSAP }} from "@gsap/react";
import {{ gsap, ScrollTrigger, prefersReducedMotion }} from "../lib/gsap";

interface SmoothScrollProps {{
  children: React.ReactNode;
  smooth?: number;
  effects?: boolean;
  smoothTouch?: number;
}}

/**
 * SmoothScrollProvider
 * 
 * Provides ScrollSmoother DOM structure (#smooth-wrapper > #smooth-content)
 * with graceful fallback to standard smooth scrolling if Club GSAP is absent.
 * React 18 strict-mode safe using @gsap/react.
 */
export const SmoothScroll: React.FC<SmoothScrollProps> = ({{
  children,
  smooth = 1.2,
  effects = true,
  smoothTouch = 0.1,
}}) => {{
  const wrapperRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {{
      if (typeof window === "undefined" || prefersReducedMotion()) return;

      // Check if ScrollSmoother is registered on GSAP
      // @ts-ignore
      const ScrollSmoother = (gsap as any).ScrollSmoother;
      let smootherInstance: any = null;

      if (ScrollSmoother && wrapperRef.current && contentRef.current) {{
        smootherInstance = ScrollSmoother.create({{
          wrapper: wrapperRef.current,
          content: contentRef.current,
          smooth,
          effects,
          smoothTouch,
          normalizeScroll: true,
        }});
      }} else {{
        // Graceful fallback: Ensure standard smooth scroll behavior
        document.documentElement.style.scrollBehavior = "smooth";
      }}

      return () => {{
        if (smootherInstance) {{
          smootherInstance.kill();
        }}
        document.documentElement.style.scrollBehavior = "";
      }};
    }},
    {{ scope: wrapperRef }}
  );

  return (
    <div
      id="smooth-wrapper"
      ref={{wrapperRef}}
      style={{{{
        overflow: "hidden",
        position: "fixed",
        height: "100%",
        width: "100%",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
      }}}}
    >
      <div
        id="smooth-content"
        ref={{contentRef}}
        style={{{{
          overflow: "visible",
          width: "100%",
          minHeight: "100vh",
        }}}}
      >
        {{children}}
      </div>
    </div>
  );
}};

export default SmoothScroll;
"""
        if not dry_run:
            comp_dir.mkdir(parents=True, exist_ok=True)
            comp_file.write_text(comp_content.strip() + "\n", encoding="utf-8")
        created_files.append(str(comp_file.relative_to(project_dir)))

    return created_files


def run_integration(
    project_dir: Path,
    install: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Orchestrates full GSAP integration for the specified project.
    """
    is_suitable, reason, meta = check_suitability(project_dir)
    if not is_suitable:
        return {
            "success": False,
            "reason": reason,
            "meta": meta,
            "actions": [],
        }

    pm = detect_package_manager(project_dir)
    framework = meta.get("framework", "vanilla")
    is_ts = meta.get("is_typescript", True)
    is_vite = meta.get("is_vite", False)

    install_cmd = build_install_command(pm, framework)
    actions: List[str] = []

    actions.append(f"Paket yöneticisi tespit edildi: {pm}")
    actions.append(f"Kurulum komutu: {install_cmd}")

    if install and not dry_run:
        try:
            subprocess.run(install_cmd, shell=True, cwd=str(project_dir), check=True)
            actions.append("Paketler başarıyla kuruldu.")
        except subprocess.CalledProcessError as e:
            actions.append(f"Paket kurulumu başarısız oldu: {e}")

    scaffolded = scaffold_gsap(
        project_dir=project_dir,
        framework=framework,
        is_typescript=is_ts,
        dry_run=dry_run,
    )
    for f in scaffolded:
        actions.append(f"Dosya üretildi: {f}")

    vite_notice = get_vite_cache_notice(project_dir) if is_vite else ""

    return {
        "success": True,
        "reason": reason,
        "package_manager": pm,
        "framework": framework,
        "install_command": install_cmd,
        "scaffolded_files": scaffolded,
        "vite_notice": vite_notice,
        "actions": actions,
    }


def main():
    parser = argparse.ArgumentParser(description="GSAP & ScrollSmoother Integration Engine")
    parser.add_argument("--project", "-p", type=str, default=".", help="Target project root directory")
    parser.add_argument("--install", "-i", action="store_true", help="Execute package manager install command")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing files or installing")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()
    target_dir = Path(args.project).resolve()

    result = run_integration(target_dir, install=args.install, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["success"] else 1

    print("============================================================")
    print("🚀 GSAP & SCROLLSMOOTHER INTEGRATION ENGINE")
    print("============================================================")
    print(f"Hedef Dizin : {target_dir}")
    print(f"Durum       : {'UYGUN' if result['success'] else 'UYGUN DEĞİL'}")
    print(f"Gerekçe     : {result['reason']}")

    if not result["success"]:
        return 1

    print(f"Framework   : {result['framework']}")
    print(f"Paket Yön.  : {result['package_manager']}")
    print(f"Komut       : {result['install_command']}")
    print("\nÜretilen Dosyalar:")
    for f in result["scaffolded_files"]:
        print(f"  + {f}")

    if result.get("vite_notice"):
        print("\n" + result["vite_notice"])

    print("\n============================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
