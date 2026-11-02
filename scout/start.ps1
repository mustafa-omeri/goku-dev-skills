# Private Repo Scout Sunucusu Başlatıcı
$ErrorActionPreference = "SilentlyContinue"
$scoutDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  🔭 Private Repo Scout Yerel Sunucusu Başlatılıyor" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tarayıcınız açılıyor: http://localhost:5055" -ForegroundColor Green
Start-Process "http://localhost:5055"
Write-Host "Sunucuyu durdurmak için bu pencereyi kapatın veya Ctrl+C tuşlayın.`n" -ForegroundColor Yellow

python "$scoutDir\server.py"
