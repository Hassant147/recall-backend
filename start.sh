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
import socket
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

# Set a socket timeout to prevent hanging connections
socket.setdefaulttimeout(10)  # 10 second timeout

# Try to connect with retries
max_retries = 3
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
            port=port,
            connect_timeout=10  # 10 second connection timeout
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
            print('Continuing anyway, but the app may not function correctly.')
            break  # Don't exit, try to continue
"

# Skip migrations for now, just try to start the server
echo 'Skipping migrations temporarily to test server startup'

echo 'Starting Gunicorn with a simplified configuration...'
exec gunicorn Search.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --log-level debug 