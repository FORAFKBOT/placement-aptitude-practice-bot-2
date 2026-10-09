@echo off
title Placement Aptitude Practice Bot
cls
echo =====================================================================
echo           PLACEMENT APTITUDE PRACTICE BOT - LAUNCHER
echo =====================================================================
echo.
echo Select interface:
echo   1. Interactive Terminal Bot (CLI)
echo   2. Web Browser Dashboard (HTTP Server on http://localhost:8080)
echo   3. Extract / Re-sync Questions from Google Drive Material
echo   4. Run Automated Test Suite
echo   5. Exit
echo.
set /p opt="Enter option (1-5): "

if "%opt%"=="1" (
    python cli_bot.py
) else if "%opt%"=="2" (
    echo Starting Web Server... Open http://localhost:8080 in your browser.
    python app.py
) else if "%opt%"=="3" (
    python extractor.py
    pause
) else if "%opt%"=="4" (
    python test_bot.py
    pause
) else (
    exit
)
