@echo off
setlocal enabledelayedexpansion

set "ADB=C:\Users\Lenovo\AppData\Local\Android\Sdk\platform-tools\adb.exe"
if not exist "!ADB!" (
    where adb >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        set "ADB=adb"
    )
)

set "APK=%~dp0ManRakshak.apk"

echo ===================================================
echo  Installing ManRakshak App to Connected Phone...
echo ===================================================
echo.

echo Checking connected devices...
"%ADB%" devices

echo.
echo Installing APK (%APK%)...
"%ADB%" install -r "%APK%"

echo.
if %ERRORLEVEL% EQU 0 (
    echo ===================================================
    echo  SUCCESS! App installed on your phone!
    echo ===================================================
) else (
    echo [!] If it failed: 
    echo     1. Make sure your phone is plugged in via USB
    echo     2. Ensure 'USB Debugging' is enabled in Developer Options
    echo     3. Check your phone screen and tap 'Allow USB Debugging'
)
echo.
pause
