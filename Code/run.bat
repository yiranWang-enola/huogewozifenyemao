@echo off
REM Quick start script for Django development server on Windows

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run migrations
python manage.py migrate

REM Start development server
python manage.py runserver
