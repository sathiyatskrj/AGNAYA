@echo off
setlocal
cd /d "%~dp0"
title AGNAYA - Raipur Heatwave Intelligence System

echo ===================================================================
echo   AGNAYA - Urban Climate & Power Grid Digital Twin
echo   Raipur Municipal Corporation & CSPDCL Resilience Platform
echo ===================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found. Initializing .venv...
    py -3.14 -m venv .venv 2>nul || python -m venv .venv
    echo [*] Installing required packages into virtual environment...
    .venv\Scripts\pip install -r requirements.txt -q
)

echo [*] Launching AGNAYA Dashboard...
echo [*] Local URL will open at: http://localhost:8501
echo.

.venv\Scripts\python -m streamlit run app.py --server.port 8501 --theme.base dark

pause
