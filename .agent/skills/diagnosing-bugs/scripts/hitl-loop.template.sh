#!/usr/bin/env bash
# Human-in-the-loop (HITL) manual test loop template
set -euo pipefail

echo "=== Human-in-the-loop Verification Loop ==="
echo "Adım 1: Tarayıcıda veya uygulamada ilgili sayfayı açın."
echo "Adım 2: Belirtilen adımları sırayla takip edin."
read -p "Hata yeniden üretildi mi? (e/h): " answer

if [ "$answer" = "e" ] || [ "$answer" = "E" ]; then
    echo "Hata gözlemlendi (RED)."
    exit 1
else
    echo "Hata gözlemlenmedi / Düzeltildi (GREEN)."
    exit 0
fi
