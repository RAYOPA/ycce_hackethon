@echo off
set "JAVA_HOME=C:\Program Files\Android\Android Studio1\jbr"
set "PATH=%JAVA_HOME%\bin;%PATH%"

cd /d "c:\Users\Lenovo\Desktop\Mayank\Codes\SIH Manrakshak\mobile_app"

echo [1/3] Running flutter clean...
call flutter clean

echo [2/3] Getting packages...
call flutter pub get

echo [3/3] Building APK...
call flutter build apk --target-platform android-arm64

echo.
if exist "build\app\outputs\flutter-apk\app-release.apk" (
    echo =======================================================
    echo  SUCCESS! APK is ready at:
    echo  %CD%\build\app\outputs\flutter-apk\app-release.apk
    echo =======================================================
) else (
    echo  BUILD FAILED!
)
