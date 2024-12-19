#!/bin/bash

# Stop on any error
set -e

echo "Starting deployment process..."

# Function to check command existence
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "Error: $1 is required but not found"
        exit 1
    fi
}

# Check required commands
check_command python3
check_command pip
check_command git

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

# Create necessary directories
echo "Setting up required directories..."
directories=("data" "logs" "proxies" "instance")
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "Creating $dir directory..."
        mkdir -p "$dir"
        chmod 700 "$dir"
    fi
done

# Create default .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    cat > .env << EOL
# Scraper Configuration
MAX_RETRIES=3
MIN_DELAY=2
MAX_DELAY=5

# Selenium Configuration
HEADLESS=false
PROXY_LIST_PATH=proxies.txt

# Logging
LOG_LEVEL=INFO
EOL
fi

# Check Chrome/Chromium installation
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "Warning: Chrome/Chromium not found. Please install it manually."
fi

# Initialize database
echo "Initializing database..."
python -m app.database.init_db

# Run migrations if they exist
if [ -d "migrations" ]; then
    echo "Running database migrations..."
    python -m alembic upgrade head
fi

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest --cov=app tests/ -v

# Final checks
echo "Running final checks..."

# Check proxy list
if [ ! -f "proxies.txt" ]; then
    echo "Warning: proxies.txt not found. Scrapers will run without proxies."
    touch proxies.txt
fi

# Verify ChromeDriver
echo "Verifying ChromeDriver setup..."
python -c "from selenium import webdriver; from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

echo "Deployment completed successfully!"

# Print next steps
echo "
Next steps:
1. Add proxies to proxies.txt if needed
2. Configure .env file with your settings
3. Run 'python test_scrapers.py' to verify scraper functionality
4. Start the web interface with 'scripts/run_web.sh'
"