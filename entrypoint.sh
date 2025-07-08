#!/bin/sh
set -e

# Run database initializations
echo "Running database initializations..."
python init_db.py

# Start the application
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 "server:create_app()"
