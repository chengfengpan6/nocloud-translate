@echo off
title NoCloud Translate
color 0A

echo ========================================================
echo        Starting NoCloud Translate...
echo        Keep this window open while using the WebUI.
echo        URL: http://127.0.0.1:7860
echo ========================================================

cd /d "%~dp0"

if not exist ".\venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -3.10 -m venv venv 2>nul
    if not exist ".\venv\Scripts\python.exe" python -m venv venv
)

".\venv\Scripts\python.exe" -m pip install --upgrade pip
".\venv\Scripts\python.exe" -m pip install -r requirements.txt
".\venv\Scripts\python.exe" web_ui.py

pause
