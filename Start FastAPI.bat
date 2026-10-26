@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Run Install Optional Streamlit and API.bat first.& pause& exit /b 1)
.venv\Scripts\python.exe -m uvicorn api:app --reload --port 8000
pause
