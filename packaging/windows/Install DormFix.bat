@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "HERE=%~dp0"
set "SRC=%HERE%DormFix"
set "TARGET=%LOCALAPPDATA%\DormFix"
set "OLDDB=%TEMP%\dormfix_old_%RANDOM%.db"

echo ==========================================
echo  DormFix Windows Installer
echo  Cornell SYSEN 5151 / SYSEN 5930 Demo
echo ==========================================
echo.

if not exist "%SRC%\webapp.py" (
  echo ERROR: DormFix payload not found next to installer.
  pause
  exit /b 1
)

set "PYCMD="
where py >nul 2>&1 && set "PYCMD=py -3"
if not defined PYCMD (where python >nul 2>&1 && set "PYCMD=python")
if not defined PYCMD (
  echo Python 3 not found. Install Python 3.10+ and enable Add Python to PATH.
  start "" "https://www.python.org/downloads/windows/"
  pause
  exit /b 1
)

%PYCMD% -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
  echo Python 3.10 or newer is required.
  pause
  exit /b 1
)

if exist "%TARGET%\data\dormfix.db" copy /Y "%TARGET%\data\dormfix.db" "%OLDDB%" >nul
if exist "%TARGET%" rmdir /S /Q "%TARGET%"
mkdir "%TARGET%" >nul 2>&1
xcopy "%SRC%\*" "%TARGET%\" /E /I /Y /Q >nul
if exist "%OLDDB%" (
  if not exist "%TARGET%\data" mkdir "%TARGET%\data"
  copy /Y "%OLDDB%" "%TARGET%\data\dormfix.db" >nul
  del /Q "%OLDDB%" >nul 2>&1
  echo Preserved existing SQLite demo database.
)

echo Running DormFix verification tests...
pushd "%TARGET%"
%PYCMD% -m unittest discover -s tests -q
set "TESTRC=%ERRORLEVEL%"
popd
if "%TESTRC%"=="0" (echo Verification passed.) else echo WARNING: verification tests reported a failure.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut([IO.Path]::Combine($env:USERPROFILE,'Desktop','DormFix.lnk')); $s.TargetPath=[IO.Path]::Combine($env:LOCALAPPDATA,'DormFix','Start DormFix.bat'); $s.WorkingDirectory=[IO.Path]::Combine($env:LOCALAPPDATA,'DormFix'); $s.IconLocation='%SystemRoot%\System32\shell32.dll,21'; $s.Save()" >nul 2>&1

echo.
echo Installed successfully:
echo   %TARGET%
echo   Desktop shortcut: DormFix
echo.
echo Double-click the DormFix desktop shortcut to start the site.
pause
