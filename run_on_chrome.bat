@echo off
title ManRakshak Web App (Flutter on Chrome)
echo =======================================================
echo  Launching ManRakshak Flutter App in Google Chrome
echo =======================================================
echo.
echo TIP: Once the browser opens:
echo  - Press 'r' in this window to Hot-Reload instantly!
echo  - Press 'R' to Hot-Restart
echo  - Press 'q' to quit
echo.

cd /d "%~dp0mobile_app"

call flutter run -d chrome --web-renderer canvaskit
pause
