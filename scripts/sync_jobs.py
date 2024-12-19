import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from app.scraper.linkedin_scraper import LinkedInScraper
from app.database.models import Job
from app.database import engine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

Session = sessionmaker(bind=engine)

def sync_jobs():
    """Sync jobs from LinkedIn to database"""
    scraper = LinkedInScraper()
    session = Session()
    
    # Software engineering positions to search for
    search_queries = [
        ("software engineer", "United States"),
        ("software developer", "United States"),
        ("full stack developer", "United States"),
        ("backend engineer", "United States"),
        ("java developer", "United States")
    ]
    
    total_jobs = 0
    for query, location in search_queries:
        logging.info(f"Searching for {query} in {location}")
        try:
            jobs = scraper.search_jobs(query, location)
            
            for job_data in jobs:
                # Check if job already exists
                existing_job = session.query(Job).filter_by(
                    url=job_data['url']
                ).first()
                
                if not existing_job:
                    job = Job(
                        title=job_data['title'],
                        company=job_data['company'],
                        location=job_data['location'],
                        url=job_data['url'],
                        source=job_data['source'],
                        posted_date=job_data.get('posted_date'),
                        salary=job_data.get('salary')
                    )
                    session.add(job)
                    total_jobs += 1
            
            session.commit()
            logging.info(f"Added {total_jobs} new jobs from {query} search")
            
        except Exception as e:
            logging.error(f"Error syncing jobs for {query}: {str(e)}")
            session.rollback()
    
    session.close()
    logging.info(f"Total new jobs added: {total_jobs}")

if __name__ == "__main__":
    load_dotenv()
    sync_jobs()