# Job Scraper

A comprehensive job scraping and tracking system that collects job postings from Indeed, LinkedIn, and Glassdoor.

## Features

- Multi-source job scraping (Indeed, LinkedIn, Glassdoor)
- Automated scraping twice daily
- Web interface for job browsing and tracking
- Advanced search and filtering
- Application status tracking
- US jobs focus with remote work options

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/job-scraper.git
cd job_scraper
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python -m app.database.init_db
```

5. Start the web interface:
```bash
flask run
```

## Documentation

- [User Guide](docs/user/guide.md) - How to use the system
- [Technical Documentation](docs/technical/overview.md) - System architecture and components
- [API Documentation](docs/technical/api.md) - API endpoints and usage
- [Setup Guide](docs/technical/setup.md) - Detailed setup instructions
- [Maintenance Guide](docs/technical/maintenance.md) - System maintenance and troubleshooting

## Configuration

Key configuration options in `config/settings.py`:
- Database settings
- Scraping intervals
- Search parameters
- Logging configuration

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details