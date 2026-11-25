@echo off
cd /d "%~dp0"
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
start "" http://127.0.0.1:8765
.venv\Scripts\python -m uvicorn app:app --host 127.0.0.1 --port 8765
pause
