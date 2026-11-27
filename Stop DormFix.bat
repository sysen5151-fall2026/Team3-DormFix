@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop_web.ps1"
if /I not "%~1"=="/quiet" pause
