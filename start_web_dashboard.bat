@echo off
title ManRakshak Web Dashboard
echo =======================================================
echo  Starting ManRakshak Commander/Admin Web Dashboard
echo =======================================================
echo.
echo  [+] Local Dashboard:  http://localhost:5173
echo  [+] API Backend URL:  http://localhost:8000/api/v1
echo =======================================================
echo.

cd /d "%~dp0web_dashboard"

call npm run dev
pause
