# Deployment Guide

## System Requirements

- macOS (10.15 or later)
- Python 3.8 or later
- SQLite 3.x
- 1GB free disk space
- Internet connection

## Pre-deployment Checklist

1. Ensure Python 3.8+ is installed:
```bash
python3 --version
```

2. Ensure SQLite is installed:
```bash
sqlite3 --version
```

3. Check disk space:
```bash
df -h
```

## Deployment Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/job_scraper.git
cd job_scraper
```

2. Make deployment script executable:
```bash
chmod +x scripts/deploy.sh
```

3. Run deployment script:
```bash
./scripts/deploy.sh
```

The deployment script will:
- Create virtual environment
- Install dependencies
- Set up data directories
- Initialize database
- Run tests

## Post-deployment Steps

1. Configure the application:
   - Review config/settings.py
   - Adjust scraping intervals if needed
   - Set logging preferences

2. Start the application:
```bash
flask run
```

3. Verify deployment:
   - Access web interface (http://localhost:5000)
   - Check logs in logs directory
   - Verify database creation in data directory

## Backup Procedures

1. Make backup script executable:
```bash
chmod +x scripts/backup.sh
```

2. Run backup:
```bash
./scripts/backup.sh
```

The backup script will:
- Create timestamped database backup
- Backup log files
- Compress backups
- Maintain last 5 backups

## Maintenance

### Daily Tasks
- Check application logs
- Verify scraper runs
- Monitor disk space

### Weekly Tasks
- Run backup script
- Review error logs
- Check for updates

### Monthly Tasks
- Clean old backups
- Analyze database size
- Update dependencies

## Troubleshooting

### Common Issues

1. Database Errors
   - Check file permissions
   - Verify SQLite installation
   - Check disk space

2. Scraper Issues
   - Check internet connection
   - Verify rate limits
   - Review error logs

3. Web Interface Problems
   - Check Flask server logs
   - Verify port availability
   - Check browser console

### Recovery Procedures

1. Database Recovery:
```bash
cp data/backups/latest_backup.db data/jobs.db
```

2. Clean Start:
```bash
rm -rf venv
rm data/jobs.db
./scripts/deploy.sh
```

## Security Considerations

1. File Permissions
   - Database: 600
   - Log files: 600
   - Data directory: 700

2. Access Control
   - Restrict server access
   - Monitor access logs
   - Regular security updates