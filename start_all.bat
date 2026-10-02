@echo off
title ManRakshak - Start Full Stack
echo =======================================================
echo     Starting ManRakshak Full Stack Services
echo =======================================================
echo.
echo  [1/3] Launching FastAPI Backend Server...
start "ManRakshak Backend" cmd /k "%~dp0start_backend.bat"

timeout /t 3 /nobreak >nul

echo  [2/3] Launching Web Dashboard (Port 5173)...
start "ManRakshak Web Dashboard" cmd /k "%~dp0start_web_dashboard.bat"

timeout /t 2 /nobreak >nul

echo  [3/3] Launching Mobile Web App (Port 5174)...
start "ManRakshak Mobile Web App" cmd /k "%~dp0start_mobile_web.bat"

echo.
echo =======================================================
echo  All services have been launched!
echo.
echo   * Backend API:      http://127.0.0.1:8000
echo   * Swagger Docs:     http://127.0.0.1:8000/docs
echo   * Web Dashboard:    http://localhost:5173
echo   * Mobile Web App:   http://localhost:5174
echo =======================================================
pause
