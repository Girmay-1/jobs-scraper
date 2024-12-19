from app.scraper.glassdoor_scraper import GlassdoorScraper
from app.database.models import Job
from app.database.repository import JobRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    db_url = os.getenv('DATABASE_URL', 'sqlite:///jobs.db')
    engine = create_engine(db_url)
    session = Session(engine)
    job_repository = JobRepository(session)
    
    try:
        # Initialize scraper with reasonable delays
        scraper = GlassdoorScraper(min_delay=2.0, max_delay=5.0)
        
        # Search for jobs
        print("Scraping jobs from Glassdoor...")
        jobs = scraper.search_jobs(
            query="software engineer",
            location="United States",
            job_type="fulltime"  # Options: fulltime, parttime, contract, internship
        )
        
        # Save jobs to database
        print(f"\nFound {len(jobs)} jobs, saving to database...")
        for job in jobs:
            try:
                job_repository.create(job)
                print(f"Saved: {job['title']} at {job['company']}")
            except Exception as e:
                print(f"Error saving job: {str(e)}")
        
        print("\nScraping completed!")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    main()