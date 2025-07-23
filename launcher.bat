@echo off
chcp 65001 >nul
title Spotify Ad Blocker - Launcher

echo.
echo ================================================================
echo                   SPOTIFY AD BLOCKER
echo                 Ad Blocker for Spotify
echo                      Version 1.0.0 - Python Edition
echo ================================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check for virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo [INFO] Create virtual environment: python -m venv .venv
    echo [INFO] Then install dependencies: .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate

REM Check for main script
if not exist "spotify_ad_blocker.py" (
    echo [ERROR] Main script spotify_ad_blocker.py not found!
    echo [INFO] Make sure the file is in the project folder
    echo.
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo [START] Starting Spotify Ad Blocker...
echo.
echo [INFO] Press Ctrl+C to stop
echo ================================================================
echo.

REM Run main script
python spotify_ad_blocker.py

echo.
echo [FINISH] Ad Blocker finished
echo [INFO] Thank you for using!
echo.
pause