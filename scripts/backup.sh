#!/bin/bash

# Stop on any error
set -e

# Get current timestamp
timestamp=$(date +"%Y%m%d_%H%M%S")

# Create backups directory if it doesn't exist
mkdir -p data/backups

# Backup database
echo "Creating database backup..."
cp data/jobs.db "data/backups/jobs_${timestamp}.db"

# Backup logs
echo "Creating logs backup..."
mkdir -p "data/backups/logs_${timestamp}"
cp logs/* "data/backups/logs_${timestamp}/"

# Compress backup
echo "Compressing backup..."
tar -czf "data/backups/backup_${timestamp}.tar.gz" \
    "data/backups/jobs_${timestamp}.db" \
    "data/backups/logs_${timestamp}"

# Remove temporary files
rm "data/backups/jobs_${timestamp}.db"
rm -r "data/backups/logs_${timestamp}"

# Keep only last 5 backups
cd data/backups
ls -t backup_*.tar.gz | tail -n +6 | xargs -r rm

echo "Backup completed successfully!"
echo "Backup file: data/backups/backup_${timestamp}.tar.gz"