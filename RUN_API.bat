@echo off
setlocal
cd /d "%~dp0"
title AGNAYA - FastAPI REST Service

echo ===================================================================
echo   AGNAYA - REST API Service (FastAPI)
echo   Raipur City Infrastructure Cascade API
echo ===================================================================
echo.
echo [*] Starting Uvicorn API server on http://localhost:8000
echo [*] Interactive API docs available at http://localhost:8000/docs
echo.

.venv\Scripts\python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

pause
