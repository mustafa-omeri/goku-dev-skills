#!/usr/bin/env bash
# ==============================================================================
# Goku Dev Skills — Modular Profile Installer (Linux / macOS)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/mustafa-omeri/goku-dev-skills/main/scripts/install.sh | bash -s -- -p backend
#   curl -fsSL https://raw.githubusercontent.com/mustafa-omeri/goku-dev-skills/main/scripts/install.sh | bash -s -- -p frontend -m
#   ./scripts/install.sh --detect
# ==============================================================================

set -euo pipefail

PROFILE="fullstack"
MINIMAL=false
DETECT=false
DEST="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--profile)
      PROFILE="$2"
      shift 2
      ;;
    -m|--minimal)
      MINIMAL=true
      shift
      ;;
    -d|--detect)
      DETECT=true
      shift
      ;;
    --dest)
      DEST="$2"
      shift 2
      ;;
    -h|--help)
      echo "Goku Dev Skills Installer"
      echo "Usage: install.sh [-p <backend|frontend|creative|fullstack>] [-m] [-d] [--dest <path>]"
      exit 0
      ;;
    *)
      shift
      ;;
  esac
done

echo "🚀 Goku Dev Skills — Installing [Profile: $PROFILE]..."

# 1. Prefer npx / node if available
if command -v npx >/dev/null 2>&1; then
  ARGS=("-p" "$PROFILE" "--dest" "$DEST")
  if [ "$MINIMAL" = true ]; then ARGS+=("-m"); fi
  if [ "$DETECT" = true ]; then ARGS+=("-d"); fi
  npx --yes goku-dev-skills init "${ARGS[@]}"
  exit 0
fi

# 2. Standalone fallback: download archive from GitHub
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "📦 Node.js not detected. Fetching directly from GitHub..."
ARCHIVE_URL="https://github.com/mustafa-omeri/goku-dev-skills/archive/refs/heads/main.tar.gz"
curl -fsSL "$ARCHIVE_URL" | tar -xz -C "$TEMP_DIR"

EXTRACTED_DIR="$TEMP_DIR/goku-dev-skills-main"
TARGET_AGENT="$DEST/.agent"
mkdir -p "$TARGET_AGENT"

# Copy base agent files
cp -r "$EXTRACTED_DIR/.agent/"* "$TARGET_AGENT/"

echo "✓ Successfully installed .agent/ into $DEST"
