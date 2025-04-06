#!/bin/bash

# Script to set up local development environment with SQLite

echo "Setting up local development environment..."

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    cp .env.example .env.local
    echo "Remember to edit .env.local with your development settings!"
else
    echo ".env.local file already exists."
fi

# Backup current .env if it exists
if [ -f .env ]; then
    echo "Backing up current .env file to .env.backup..."
    cp .env .env.backup
fi

# Replace .env with .env.local
echo "Setting .env to use local development settings..."
cp .env.local .env

echo "Activating virtual environment..."
source venv/bin/activate || echo "Virtual environment not found. Please create one with 'python3 -m venv venv'"

echo "Local development environment is now set up!"
echo "Run 'python manage.py migrate' to set up the SQLite database."
echo "Run 'python manage.py runserver' to start the local server."
echo ""
echo "IMPORTANT: Do not commit the .env file to git!"
echo "To switch back to production settings, run: cp .env.backup .env" 