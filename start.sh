#!/bin/bash
set -e

echo "Starting application initialization..."

echo "Running collectstatic..."
python manage.py collectstatic --noinput
echo "Collectstatic completed successfully."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL is not set. Database connections may fail."
else
    echo "Database URL is configured."
fi

echo "Testing database connection..."
python -c "
import psycopg2
import os
import time
from urllib.parse import urlparse

url = os.environ.get('DATABASE_URL')
if not url:
    print('No DATABASE_URL found')
    exit(1)

parsed = urlparse(url)
dbname = parsed.path[1:]
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port

# Try to connect with retries
max_retries = 5
retry_count = 0
connected = False

while retry_count < max_retries and not connected:
    try:
        print(f'Attempting to connect to PostgreSQL at {host}:{port} (attempt {retry_count+1})')
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.close()
        print('Database connection successful!')
        connected = True
    except Exception as e:
        print(f'Connection attempt failed: {str(e)}')
        retry_count += 1
        if retry_count < max_retries:
            print(f'Retrying in 5 seconds...')
            time.sleep(5)
        else:
            print(f'Max retries reached. Unable to connect to database.')
            exit(1)
"

echo "Running migrations with timeout..."
# Run migrations with a 2-minute timeout
timeout 120 python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo "Migrations completed successfully."
else
    echo "Error: Migrations timed out or failed. Proceeding anyway..."
fi

echo "Starting Gunicorn..."
exec gunicorn Search.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --log-level debug 