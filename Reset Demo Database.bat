@echo off
setlocal
set /p A=Type RESET to delete the local demo database: 
if /I not "%A%"=="RESET" (echo Cancelled.& pause& exit /b 0)
call "%~dp0Stop DormFix.bat" /quiet
if exist "%~dp0data\dormfix.db" del /Q "%~dp0data\dormfix.db"
echo Database reset. It will be recreated on next start.
pause
