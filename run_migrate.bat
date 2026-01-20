@echo off
REM Apply Django migrations
cd /d "%~dp0"
python manage.py migrate
pause
