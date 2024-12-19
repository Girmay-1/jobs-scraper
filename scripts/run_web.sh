#!/bin/bash

# Get the project root directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Export Flask environment variables
export FLASK_APP=app.web
export FLASK_ENV=development
export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH

# Activate virtual environment
source venv/bin/activate

# Run Flask application
flask run