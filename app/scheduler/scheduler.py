import schedule
import time
import logging
from datetime import datetime
import threading
from typing import Dict, Any

from app.scraper import IndeedScraper, LinkedInScraper, GlassdoorScraper
from app.database.db import Database
from app.database.repository import JobRepository

class JobScraperScheduler:
    """Scheduler for running job scraping tasks"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize scheduler with configuration"""
        self.config = config
        self.is_running = False
        self.thread = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('JobScraperScheduler')

    def scrape_jobs(self):
        """Run job scraping for all sources"""
        self.logger.info("Starting job scraping task")
        start_time = datetime.now()
        
        try:
            # Initialize database
            db = Database(
                db_uri=self.config['SQLALCHEMY_DATABASE_URI'],
                db_path=self.config['DATABASE_PATH']
            )
            session = db.get_session()
            job_repo = JobRepository(session)

            # Initialize scrapers
            scrapers = [
                IndeedScraper(),
                LinkedInScraper(),
                GlassdoorScraper()
            ]

            total_jobs = 0
            errors = []

            # Run each scraper
            for scraper in scrapers:
                try:
                    self.logger.info(f"Starting scraper: {scraper.site_name}")
                    jobs = scraper.search_jobs(
                        query=self.config.get('SEARCH_QUERY', 'software engineer'),
                        location=self.config.get('SEARCH_LOCATION', 'United States')
                    )
                    
                    # Store jobs in database
                    for job in jobs:
                        try:
                            job_repo.create(job)
                            total_jobs += 1
                        except Exception as e:
                            self.logger.error(f"Error storing job: {str(e)}")
                            errors.append(f"Storage error: {str(e)}")
                            
                except Exception as e:
                    error_msg = f"Error in {scraper.site_name} scraper: {str(e)}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)

            # Log summary
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Scraping completed. Duration: {duration:.2f}s, Jobs found: {total_jobs}")
            
            # Handle errors if any
            if errors:
                self.handle_errors(errors)

        except Exception as e:
            self.logger.error(f"Fatal error in scraping task: {str(e)}")
            self.handle_errors([f"Fatal error: {str(e)}"])
        
        finally:
            if 'session' in locals():
                session.close()

    def handle_errors(self, errors: list):
        """Handle and notify about errors"""
        error_message = "\n".join(errors)
        self.logger.error(f"Scraping errors occurred:\n{error_message}")
        
        # TODO: Implement notification system (email, Slack, etc.)
        # For now, just log errors
        
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return

        self.is_running = True
        self.logger.info("Starting scheduler")

        # Schedule jobs to run twice daily
        schedule.every().day.at("00:00").do(self.scrape_jobs)
        schedule.every().day.at("12:00").do(self.scrape_jobs)

        # Run in a separate thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        self.thread = threading.Thread(target=run_scheduler)
        self.thread.start()

        # Run initial scraping
        self.scrape_jobs()

    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            self.logger.warning("Scheduler is not running")
            return

        self.logger.info("Stopping scheduler")
        self.is_running = False
        
        if self.thread:
            self.thread.join()
            self.thread = None

    def status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'next_run': schedule.next_run().strftime('%Y-%m-%d %H:%M:%S') if self.is_running else None,
            'job_count': len(schedule.jobs),
            'last_run': getattr(self, 'last_run', None)
        }