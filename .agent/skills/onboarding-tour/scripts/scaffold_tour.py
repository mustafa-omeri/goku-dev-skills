#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Onboarding ve ürün turu şablon üreteci (scaffold_tour.py).

Driver.js, React Joyride veya hafif Coachmark (ipucu balonu) desenleri için
üretim kalitesinde TypeScript/React hook'ları ve bileşenleri üretir.
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


DRIVER_JS_TEMPLATE = """import { useEffect, useRef, useCallback } from 'react'
import { driver, DriveStep, Config } from 'driver.js'
import 'driver.js/dist/driver.css'

export interface TourStepConfig {
  element: string
  title: string
  description: string
  side?: 'top' | 'right' | 'bottom' | 'left'
  align?: 'start' | 'center' | 'end'
}

export const DEFAULT___TOUR_CONST___STEPS: TourStepConfig[] = [
  {
    element: '[data-tour="__TOUR_SLUG__-welcome"]',
    title: 'Hoş Geldiniz 👋',
    description: 'Uygulamanın ana özelliklerini hızlıca keşfetmek için bu kısa turu takip edebilirsiniz.',
    side: 'bottom',
    align: 'center',
  },
  {
    element: '[data-tour="__TOUR_SLUG__-action"]',
    title: 'Birincil Aksiyon 🚀',
    description: 'Yeni bir kayıt, sayaç veya proje başlatmak için burayı kullanabilirsiniz.',
    side: 'left',
    align: 'start',
  },
  {
    element: '[data-tour="__TOUR_SLUG__-settings"]',
    title: 'Ayarlar ve Özelleştirme ⚙️',
    description: 'Tema, dil ve kişisel tercihlerinizi dilediğiniz an buradan yönetebilirsiniz.',
    side: 'top',
    align: 'end',
  },
]

interface Use__TOUR_PASCAL__TourOptions {
  autoStart?: boolean
  storageKey?: string
  customSteps?: TourStepConfig[]
  onComplete?: () => void
  onDismiss?: () => void
}

/**
 * __TOUR_NAME__ için Driver.js tabanlı, ultra hafif (~5KB gzip) ve kalıcı onboarding hook'u.
 */
export function use__TOUR_PASCAL__Tour(options: Use__TOUR_PASCAL__TourOptions = {}) {
  const {
    autoStart = false,
    storageKey = '__STORAGE_KEY__',
    customSteps = DEFAULT___TOUR_CONST___STEPS,
    onComplete,
    onDismiss,
  } = options

  const driverRef = useRef<ReturnType<typeof driver> | null>(null)

  const markCompleted = useCallback(() => {
    try {
      localStorage.setItem(storageKey, 'true')
    } catch {
      // localStorage erişim hatası güvenle yutulur
    }
  }, [storageKey])

  const isCompleted = useCallback((): boolean => {
    try {
      return localStorage.getItem(storageKey) === 'true'
    } catch {
      return false
    }
  }, [storageKey])

  const resetTour = useCallback(() => {
    try {
      localStorage.removeItem(storageKey)
    } catch {}
  }, [storageKey])

  const startTour = useCallback(() => {
    const driveSteps: DriveStep[] = customSteps.map((step) => ({
      element: step.element,
      popover: {
        title: step.title,
        description: step.description,
        side: step.side || 'bottom',
        align: step.align || 'start',
        nextBtnText: 'Sonraki →',
        prevBtnText: '← Önceki',
        doneBtnText: 'Tamamla ✓',
      },
    }))

    const config: Config = {
      showProgress: true,
      allowClose: true,
      overlayColor: 'rgba(0, 0, 0, 0.75)',
      stagePadding: 6,
      stageRadius: 8,
      steps: driveSteps,
      onDestroyStarted: () => {
        if (!driverRef.current?.hasNextStep()) {
          markCompleted()
          onComplete?.()
        } else {
          onDismiss?.()
        }
        driverRef.current?.destroy()
      },
    }

    const driverObj = driver(config)
    driverRef.current = driverObj
    driverObj.drive()
  }, [customSteps, markCompleted, onComplete, onDismiss])

  useEffect(() => {
    if (autoStart && !isCompleted()) {
      // DOM elemanlarının yerleşmesi için kısa gecikme
      const timer = setTimeout(() => {
        startTour()
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [autoStart, isCompleted, startTour])

  return {
    startTour,
    resetTour,
    isCompleted,
  }
}
"""

JOYRIDE_TEMPLATE = """import React, { useState, useEffect, useCallback } from 'react'
import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride'

export interface TourStepItem {
  target: string
  title?: string
  content: string
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'center'
  disableBeacon?: boolean
}

export const DEFAULT___TOUR_CONST___STEPS: TourStepItem[] = [
  {
    target: '[data-tour="__TOUR_SLUG__-welcome"]',
    title: 'Hoş Geldiniz 👋',
    content: 'Uygulamanın ana özelliklerini keşfetmek için bu kısa turu takip edin.',
    placement: 'center',
    disableBeacon: true,
  },
  {
    target: '[data-tour="__TOUR_SLUG__-action"]',
    title: 'Birincil Aksiyon 🚀',
    content: 'Yeni bir kayıt, sayaç veya proje başlatmak için buraya tıklayabilirsiniz.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="__TOUR_SLUG__-settings"]',
    title: 'Ayarlar ve Tercihler ⚙️',
    content: 'Tema, dil ve kişisel ayarlarınızı buradan yapılandırabilirsiniz.',
    placement: 'top',
  },
]

interface __TOUR_PASCAL__TourProps {
  autoStart?: boolean
  storageKey?: string
  steps?: TourStepItem[]
  onComplete?: () => void
  onDismiss?: () => void
}

/**
 * __TOUR_NAME__ için React Joyride tabanlı onboarding bileşeni.
 * Not: Paket boyutu ~35KB gzip olduğundan `React.lazy()` ile dinamik yüklenmesi önerilir.
 */
export function __TOUR_PASCAL__Tour({
  autoStart = true,
  storageKey = '__STORAGE_KEY__',
  steps = DEFAULT___TOUR_CONST___STEPS,
  onComplete,
  onDismiss,
}: __TOUR_PASCAL__TourProps) {
  const [run, setRun] = useState(false)

  useEffect(() => {
    if (autoStart) {
      try {
        const completed = localStorage.getItem(storageKey) === 'true'
        if (!completed) {
          setRun(true)
        }
      } catch {
        setRun(true)
      }
    }
  }, [autoStart, storageKey])

  const handleJoyrideCallback = useCallback(
    (data: CallBackProps) => {
      const { status } = data
      const finishedStatuses: string[] = [STATUS.FINISHED, STATUS.SKIPPED]

      if (finishedStatuses.includes(status)) {
        setRun(false)
        try {
          localStorage.setItem(storageKey, 'true')
        } catch {}

        if (status === STATUS.FINISHED) {
          onComplete?.()
        } else {
          onDismiss?.()
        }
      }
    },
    [storageKey, onComplete, onDismiss]
  )

  const joyrideSteps: Step[] = steps.map((s) => ({
    target: s.target,
    title: s.title,
    content: s.content,
    placement: s.placement || 'bottom',
    disableBeacon: s.disableBeacon,
  }))

  return (
    <Joyride
      steps={joyrideSteps}
      run={run}
      continuous
      showSkipButton
      showProgress
      callback={handleJoyrideCallback}
      locale={{
        back: '← Geri',
        close: 'Kapat',
        last: 'Tamamla ✓',
        next: 'Sonraki →',
        skip: 'Turu Atla',
      }}
      styles={{
        options: {
          zIndex: 10000,
          primaryColor: '#3b82f6',
          textColor: '#1f2937',
          backgroundColor: '#ffffff',
          arrowColor: '#ffffff',
        },
      }}
    />
  )
}
"""

COACHMARK_TEMPLATE = """import React, { useState, useEffect } from 'react'

export interface CoachmarkProps {
  id: string
  title: string
  description: string
  children: React.ReactNode
  placement?: 'top' | 'bottom' | 'left' | 'right'
  storageKeyPrefix?: string
}

/**
 * Sıfır bağımlılıklı, pulsing beacon (yanıp sönen ipucu noktası) bileşeni.
 * Kullanıcı dokunduğunda ipucu balonunu açar; tıklandığında kalıcı olarak kapanır.
 */
export function CoachmarkBeacon({
  id,
  title,
  description,
  children,
  placement = 'top',
  storageKeyPrefix = 'coachmark_seen_',
}: CoachmarkProps) {
  const storageKey = `${storageKeyPrefix}${id}`
  const [seen, setSeen] = useState(true)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    try {
      const hasSeen = localStorage.getItem(storageKey) === 'true'
      setSeen(hasSeen)
    } catch {
      setSeen(false)
    }
  }, [storageKey])

  const dismiss = () => {
    setOpen(false)
    setSeen(true)
    try {
      localStorage.setItem(storageKey, 'true')
    } catch {}
  }

  const placementStyles: Record<string, string> = {
    top: 'bottom-full mb-3 left-1/2 -translate-x-1/2',
    bottom: 'top-full mt-3 left-1/2 -translate-x-1/2',
    left: 'right-full mr-3 top-1/2 -translate-y-1/2',
    right: 'left-full ml-3 top-1/2 -translate-y-1/2',
  }

  return (
    <div className="relative inline-flex items-center">
      {children}

      {!seen && (
        <span className="absolute -top-1 -right-1 flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary/80 opacity-75" />
          <button
            type="button"
            onClick={() => setOpen(!open)}
            aria-label={`İpucu: ${title}`}
            className="relative inline-flex rounded-full h-3 w-3 bg-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
        </span>
      )}

      {open && (
        <div
          role="dialog"
          aria-label={title}
          className={`absolute z-50 w-64 rounded-xl border border-border bg-card p-4 shadow-xl text-card-foreground text-left ${placementStyles[placement] || placementStyles.top}`}
        >
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-sm font-semibold text-primary-dark">{title}</h4>
            <button
              type="button"
              onClick={dismiss}
              className="text-muted-foreground hover:text-foreground text-xs p-1"
              aria-label="Kapat"
            >
              ✕
            </button>
          </div>
          <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">{description}</p>
          <div className="mt-3 flex justify-end">
            <button
              type="button"
              onClick={dismiss}
              className="px-2.5 py-1 text-xs font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition"
            >
              Anladım
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
"""


def to_pascal(name: str) -> str:
    parts = re_split(name)
    return "".join(p.capitalize() for p in parts)


def to_slug(name: str) -> str:
    parts = re_split(name)
    return "-".join(p.lower() for p in parts)


def to_const(name: str) -> str:
    parts = re_split(name)
    return "_".join(p.upper() for p in parts)


def re_split(name: str) -> list[str]:
    return [p for p in re.split(r"[-_.\s]+", name) if p]


def apply_placeholders(tmpl: str, name: str, storage_key: str | None = None) -> str:
    pascal = to_pascal(name)
    slug = to_slug(name)
    const_name = to_const(name)
    key = storage_key or f"onboarding_completed_{slug}"

    return (
        tmpl.replace("__TOUR_NAME__", name)
        .replace("__TOUR_PASCAL__", pascal)
        .replace("__TOUR_SLUG__", slug)
        .replace("__TOUR_CONST__", const_name)
        .replace("__STORAGE_KEY__", key)
    )


def generate_scaffold(engine: str, name: str, storage_key: str | None = None) -> str:
    if engine == "joyride":
        return apply_placeholders(JOYRIDE_TEMPLATE, name, storage_key)
    if engine == "coachmark":
        return COACHMARK_TEMPLATE
    # varsayılan: driverjs
    return apply_placeholders(DRIVER_JS_TEMPLATE, name, storage_key)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Onboarding Tour ve Rehberli Tur Şablon Üreteci"
    )
    parser.add_argument(
        "--engine",
        choices=["driverjs", "joyride", "coachmark"],
        default="driverjs",
        help="Kullanılacak tur motoru (varsayılan: driverjs - ultra hafif ~5KB)",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="product",
        help="Tur adı (ör. dashboard, submit-form, verification)",
    )
    parser.add_argument(
        "--storage-key",
        type=str,
        default=None,
        help="Özel localStorage tamamlama anahtarı",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Çıktının yazılacağı dosya yolu (verilmezse stdout'a basar)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Yapılandırma özetini JSON olarak döner",
    )

    args = parser.parse_args(argv)

    code = generate_scaffold(args.engine, args.name, args.storage_key)

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(code, encoding="utf-8")
        if not args.json:
            print(f"[OK] Şablon başarıyla üretildi: {out_path}")

    if args.json:
        result = {
            "status": "OK",
            "engine": args.engine,
            "tour_name": args.name,
            "storage_key": args.storage_key or f"onboarding_completed_{to_slug(args.name)}",
            "output_file": str(args.output) if args.output else None,
            "char_count": len(code),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif not args.output:
        print(code)

    return 0


if __name__ == "__main__":
    sys.exit(main())
