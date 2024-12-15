# Job Scraper

A Python-based job scraping tool that aggregates software engineering job postings from Indeed, LinkedIn, and Glassdoor. This tool provides a centralized platform for tracking and analyzing job opportunities through a local web interface.

## Features

- Automated job scraping from multiple sources
- Local web interface for easy job browsing
- Advanced filtering and search capabilities
- Automated scheduling for regular updates
- Data persistence using SQLite

## Requirements

- Python 3.x
- pip (Python package installer)
- Git

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd job_scraper
```

2. Create and activate a virtual environment:
```bash
# On macOS and Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

1. Start the local server:
```bash
python run.py
```

2. Access the web interface:
Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
job_scraper/
│
├── app/
│   ├── scraper/        # Job scraping modules
│   ├── database/       # Database operations
│   ├── web/           # Web interface
│   └── scheduler/     # Automated scheduling
│
├── config/            # Configuration files
├── tests/            # Test suite
├── requirements.txt  # Project dependencies
└── run.py           # Application entry point
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- BeautifulSoup4 for web scraping
- Flask for web interface
- SQLite for data storage