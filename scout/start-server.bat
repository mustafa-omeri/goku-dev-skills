@echo off
chcp 65001 >nul
echo ===================================================
echo   🔭 Private Repo Scout Yerel Sunucusu Başlatılıyor
echo ===================================================
echo.
echo Tarayıcınız açılıyor: http://localhost:5055
start http://localhost:5055
echo.
echo Sunucuyu durdurmak için bu pencereyi kapatın veya Ctrl+C yapın.
echo.
python "%~dp0server.py"
pause
