@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\streamlit.exe" (echo Run Install Optional Streamlit and API.bat first.& pause& exit /b 1)
.venv\Scripts\streamlit.exe run app.py
pause
