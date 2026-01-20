@echo off
REM Activate virtual environment
call C:\Users\USER\Desktop\Important\Application\bofuri\Scripts\activate.bat

REM Navigate to project folder
cd C:\Users\USER\Desktop\Important\Application\BuynSell

REM Start Celery worker in a separate window
start celery -A BuynSell worker -l info

REM Start Celery beat in a separate window
start celery -A BuynSell beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
