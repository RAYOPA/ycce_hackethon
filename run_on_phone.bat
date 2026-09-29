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
echo  Launching Live App on Your Phone with HOT-RELOAD
echo =======================================================
echo.
echo TIP: Once running, press 'r' in this window to hot-reload 
echo      code changes instantly on your phone!
echo.

call flutter run
pause

