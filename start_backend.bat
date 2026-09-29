@echo off
setlocal enabledelayedexpansion
title ManRakshak Backend Server
echo =======================================================
echo  Starting ManRakshak Backend Server (FastAPI)
echo =======================================================
echo.
for /f "usebackq tokens=*" %%a in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' -and $_.IPAddress -notlike '169.254.*' } | Select-Object -First 1).IPAddress"`) do set "LOCAL_IP=%%a"
if "!LOCAL_IP!"=="" set "LOCAL_IP=127.0.0.1"

echo  [✓] Localhost:     http://127.0.0.1:8000
echo  [✓] Local Wi-Fi:   http://!LOCAL_IP!:8000
echo  [✓] Swagger Docs:  http://127.0.0.1:8000/docs
echo.
echo  * Tip for Mobile APK: Make sure phone is on the same Wi-Fi
echo    and has server set to: http://!LOCAL_IP!:8000/api/v1
echo =======================================================
echo.
echo.
echo Attempting to setup USB port forwarding (adb reverse) for offline mode...
adb reverse tcp:8000 tcp:8000 2>nul
if %errorlevel%==0 (
    echo  [✓] ADB Port Forwarding Active. You can use http://127.0.0.1:8000/api/v1 in the mobile app via USB!
) else (
    echo  [!] ADB not found or no device connected via USB. (Ignore if using Wi-Fi or Emulator)
)
echo.

cd /d "%~dp0backend"

if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause

