@echo off
set "JAVA_HOME=C:\Program Files\Android\Android Studio1\jbr"
set "PATH=%JAVA_HOME%\bin;%PATH%"

cd /d "c:\Users\Lenovo\Desktop\Mayank\Codes\SIH Manrakshak\mobile_app"

echo =======================================================
echo  Launching Live App on Your Phone with HOT-RELOAD
echo =======================================================
echo.
echo TIP: Once running, press 'r' in this window to hot-reload 
echo      code changes instantly on your phone!
echo.

call flutter run
pause
