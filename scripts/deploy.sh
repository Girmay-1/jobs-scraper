#!/bin/bash

# Stop on any error
set -e

echo "Starting deployment process..."

# Check Python version
python_version=$(python3 --version)
if [[ $? -ne 0 ]]; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi
echo "Using $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory if it doesn't exist
echo "Setting up data directory..."
mkdir -p data
chmod 700 data

# Create logs directory if it doesn't exist
echo "Setting up logs directory..."
mkdir -p logs
chmod 700 logs

# Initialize database
echo "Initializing database..."
python -m app.database.init_db

# Run tests
echo "Running tests..."
python -m pytest

echo "Deployment completed successfully!"