@echo off
echo Starting MedAi Application...
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting Django development server...
python manage.py runserver

pause
