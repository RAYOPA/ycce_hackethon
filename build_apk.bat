@echo off
setlocal enabledelayedexpansion

if exist "C:\Program Files\Android\Android Studio1\jbr" (
    set "JAVA_HOME=C:\Program Files\Android\Android Studio1\jbr"
) else if exist "C:\Program Files\Android\Android Studio\jbr" (
    set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
)

set "PATH=C:\src\flutter\bin;%JAVA_HOME%\bin;%PATH%"

cd /d "%~dp0mobile_app"

echo =======================================================
echo  Building ManRakshak Release APK (ARM64)
echo =======================================================
echo.

echo [1/3] Running flutter clean...
call flutter clean

echo.
echo [2/3] Getting packages...
call flutter pub get

echo.
echo [3/3] Building APK...
call flutter build apk --target-platform android-arm64

echo.
if exist "build\app\outputs\flutter-apk\app-release.apk" (
    echo Copying APK to root directory as ManRakshak.apk...
    copy /y "build\app\outputs\flutter-apk\app-release.apk" "%~dp0ManRakshak.apk" >nul
    echo =======================================================
    echo  SUCCESS! APK is ready:
    echo  1. %~dp0ManRakshak.apk
    echo  2. %CD%\build\app\outputs\flutter-apk\app-release.apk
    echo =======================================================
) else (
    echo =======================================================
    echo  BUILD FAILED! Please check logs above.
    echo =======================================================
)

echo.
pause

