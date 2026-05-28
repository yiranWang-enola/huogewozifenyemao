#!/bin/bash
# Quick start script for Django development server on Linux/Mac

# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
