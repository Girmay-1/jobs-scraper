#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set Python path
PYTHONPATH=$PYTHONPATH:. python3 scripts/manual_scrape.py