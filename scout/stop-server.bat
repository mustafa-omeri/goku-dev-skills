@echo off
chcp 65001 >nul
echo 5055 portunu kullanan Scout sunucusu aranıyor...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5055') do (
    echo Sunucu bulundu (PID: %%a), sonlandırılıyor...
    taskkill /f /pid %%a >nul 2>&1
)
echo [OK] Scout sunucusu durduruldu.
timeout /t 2 >nul
