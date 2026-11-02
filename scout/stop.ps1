# Private Repo Scout Sunucusu Durdurucu
$ErrorActionPreference = "SilentlyContinue"

Write-Host "5055 portunu kullanan Scout sunucusu aranıyor..." -ForegroundColor Yellow
$conns = Get-NetTCPConnection -LocalPort 5055 -ErrorAction SilentlyContinue

if ($conns) {
    foreach ($c in $conns) {
        $pidNum = $c.OwningProcess
        Write-Host "Sunucu işlemi bulundu (PID: $pidNum), durduruluyor..." -ForegroundColor Cyan
        Stop-Process -Id $pidNum -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] Scout sunucusu durduruldu." -ForegroundColor Green
} else {
    Write-Host "[INFO] 5055 portunda çalışan aktif bir sunucu bulunamadı." -ForegroundColor Gray
}
