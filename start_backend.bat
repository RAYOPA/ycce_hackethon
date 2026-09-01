@echo off
echo ===================================================
echo  Starting ManRakshak Backend Server on 0.0.0.0:8000
echo ===================================================
echo.

cd /d "c:\Users\Lenovo\Desktop\Mayank\Codes\SIH Manrakshak\backend"

if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
