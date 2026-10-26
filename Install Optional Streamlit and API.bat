@echo off
setlocal
cd /d "%~dp0"
set "PYCMD="
where py >nul 2>&1 && set "PYCMD=py -3"
if not defined PYCMD (where python >nul 2>&1 && set "PYCMD=python")
if not defined PYCMD (echo Python 3 not found.& pause& exit /b 1)
%PYCMD% -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
echo Optional environment installed.
pause
