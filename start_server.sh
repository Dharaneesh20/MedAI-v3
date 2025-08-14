#!/bin/bash
echo "Starting MedAi Application..."
echo

echo "Activating virtual environment..."
source .venv_linux/bin/activate

echo
echo "Starting Django development server..."
python manage.py runserver
