@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
python setup.py
python spotify_ad_blocker.py
pause
