#!/bin/bash
set -o errexit

echo "Starting deployment..."
echo "Current directory: $(pwd)"
echo "Working directory contents:"
ls -la

# Navigate to the project root (render puts code in /opt/render/project, not /opt/render/project/src)
cd /opt/render/project

echo "Changed to: $(pwd)"
echo "Directory contents:"
ls -la

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn BuynSell.wsgi:application --bind 0.0.0.0:10000 --workers 2 --timeout 60

