@echo off
title Agent Society
cd /d "%~dp0"

echo Starting Agent Society...
echo.

start "" "http://localhost:8000"
timeout /t 2 /nobreak >nul

uvicorn api.main:app --host 127.0.0.1 --port 8000
