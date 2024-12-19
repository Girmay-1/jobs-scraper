import os
import sys
import logging
from dotenv import load_dotenv
from app.scraper.linkedin_scraper import LinkedInScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_linkedin_scraper():
    print("\nTesting LinkedIn Scraper...")
    scraper = LinkedInScraper()
    
    # Software engineering positions in US
    test_queries = [
        ("software engineer", "United States"),
        ("software developer", "United States"),
        ("full stack developer", "United States"),
        ("backend engineer", "United States"),
        ("java developer", "United States")
    ]
    
    all_jobs = []
    for query, location in test_queries:
        print(f"\nSearching for {query} in {location}")
        try:
            jobs = scraper.search_jobs(query, location)  # No limit set to get maximum jobs
            all_jobs.extend(jobs)
            print(f"Found {len(jobs)} jobs")
            
            for i, job in enumerate(jobs[:5], 1):  # Show first 5 jobs as sample
                print(f"\nJob {i}:")
                for key, value in job.items():
                    print(f"{key}: {value}")
        except Exception as e:
            logging.error(f"Error during LinkedIn search: {str(e)}")
    
    print(f"\nTotal unique jobs found: {len(all_jobs)}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Test LinkedIn
    print("Starting LinkedIn Scraper test...")
    test_linkedin_scraper()