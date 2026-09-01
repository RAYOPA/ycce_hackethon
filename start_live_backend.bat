@echo off
echo =======================================================
echo  Starting ManRakshak LIVE Server (Public HTTPS)
echo =======================================================
echo.

taskkill /F /IM cloudflared.exe 2>NUL

echo [1/2] Starting Cloudflare Tunnel in background...
start /b "" "%~dp0cloudflared.exe" tunnel --url http://127.0.0.1:8000

echo.
echo [2/2] Starting FastAPI Backend Server on port 8000...
cd /d "%~dp0backend"

call "..\venv\Scripts\activate.bat"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
