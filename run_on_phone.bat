@echo off
set ANDROID_PREFS_ROOT=
set JAVA_HOME=C:\Program Files\Android\Android Studio1\jbr
set PATH=%JAVA_HOME%\bin;%PATH%

echo [1/3] Ensuring phone is still connected...
"C:\Users\Lenovo\AppData\Local\Android\Sdk\platform-tools\adb.exe" devices

echo [2/3] Cleaning build to avoid lock issues...
cd mobile_app
call flutter clean
call flutter pub get

echo [3/3] Launching app on your phone...
:: Use the specific device ID we found
call flutter run -d cex4kvw89565on4h

pause
