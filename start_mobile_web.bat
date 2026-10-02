@echo off
title ManRakshak Mobile Web App
echo =======================================================
echo  Starting ManRakshak Personnel Mobile Web App
echo =======================================================
echo.
echo  [+] Local Web App:    http://localhost:5174
echo  [+] API Backend URL:  http://localhost:8000/api/v1
echo =======================================================
echo.

cd /d "%~dp0mobile_web_app"

call npm run dev -- --port 5174
pause
