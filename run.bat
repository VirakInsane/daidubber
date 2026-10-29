@echo off
chcp 65001 > nul
title JAI AUTO DUBBING - AI Chinese to Khmer Pro
echo ========================================================
echo   JAI AUTO DUBBING - AI Chinese to Khmer Dubbing Suite
echo ========================================================
echo.
echo Starting application...
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] An error occurred while running the application.
    pause
)
