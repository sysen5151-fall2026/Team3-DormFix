@echo off
setlocal
set "TARGET=%LOCALAPPDATA%\DormFix"
echo DormFix Uninstaller
echo This removes the installed demo and local SQLite data.
set /p ANSWER=Type UNINSTALL to continue: 
if /I not "%ANSWER%"=="UNINSTALL" (echo Cancelled.& pause& exit /b 0)
if exist "%TARGET%\Stop DormFix.bat" call "%TARGET%\Stop DormFix.bat" /quiet
if exist "%USERPROFILE%\Desktop\DormFix.lnk" del /Q "%USERPROFILE%\Desktop\DormFix.lnk"
if exist "%TARGET%" rmdir /S /Q "%TARGET%"
echo DormFix removed.
pause
