@echo off
setlocal
cd /d "%~dp0"
echo DormFix Windows diagnostics
echo ----------------------------------------
ver
echo Architecture: %PROCESSOR_ARCHITECTURE%
where py 2>nul
py -3 --version 2>nul
where python 2>nul
python --version 2>nul
echo.
set "PYCMD="
where py >nul 2>&1 && set "PYCMD=py -3"
if not defined PYCMD (where python >nul 2>&1 && set "PYCMD=python")
if defined PYCMD %PYCMD% -m unittest discover -s tests -v
powershell -NoProfile -Command "foreach($p in 8502,8501,8000){try{$r=Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 -Uri ('http://127.0.0.1:'+ $p); Write-Host ('Port '+$p+': responding')}catch{Write-Host ('Port '+$p+': no HTTP response')}}"
pause
