# ==============================================================================
# Goku Dev Skills — Modular Profile Installer (Windows PowerShell)
#
# Usage:
#   irm https://raw.githubusercontent.com/mustafa-omeri/goku-dev-skills/main/scripts/install.ps1 | iex
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Profile backend
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Profile frontend -Minimal
# ==============================================================================

[CmdletBinding()]
param(
    [ValidateSet("fullstack", "backend", "frontend", "creative", "all")]
    [string]$Profile = "fullstack",

    [switch]$Minimal,
    [switch]$Detect,
    [string]$Dest = "."
)

$ErrorActionPreference = "Stop"

Write-Host "`n🚀 Goku Dev Skills — Installing Profile: $Profile..." -ForegroundColor Cyan

# 1. Prefer npx if available
$hasNpx = Get-Command "npx" -ErrorAction SilentlyContinue
if ($hasNpx) {
    $cliArgs = @("goku-dev-skills", "init", "-p", $Profile, "--dest", $Dest)
    if ($Minimal) { $cliArgs += "-m" }
    if ($Detect) { $cliArgs += "-d" }

    & npx --yes @cliArgs
    exit $LASTEXITCODE
}

# 2. Standalone fallback: download zip from GitHub
Write-Host "📦 Node.js not detected. Fetching directly from GitHub..." -ForegroundColor Yellow
$tempZip = Join-Path $env:TEMP "goku-dev-skills-$([Guid]::NewGuid().ToString('N')).zip"
$tempExtract = Join-Path $env:TEMP "goku-dev-skills-$([Guid]::NewGuid().ToString('N'))"

try {
    $zipUrl = "https://github.com/mustafa-omeri/goku-dev-skills/archive/refs/heads/main.zip"
    Invoke-WebRequest -Uri $zipUrl -OutFile $tempZip -UseBasicParsing
    Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force

    $srcAgent = Join-Path $tempExtract "goku-dev-skills-main\.agent"
    $targetAgent = Join-Path (Resolve-Path $Dest).Path ".agent"

    if (-not (Test-Path $targetAgent)) {
        New-Item -ItemType Directory -Path $targetAgent -Force | Out-Null
    }

    Copy-Item -Path "$srcAgent\*" -Destination $targetAgent -Recurse -Force
    Write-Host "✓ Successfully installed .agent/ into $Dest" -ForegroundColor Green
}
finally {
    if (Test-Path $tempZip) { Remove-Item -Force $tempZip -ErrorAction SilentlyContinue }
    if (Test-Path $tempExtract) { Remove-Item -Recurse -Force $tempExtract -ErrorAction SilentlyContinue }
}
