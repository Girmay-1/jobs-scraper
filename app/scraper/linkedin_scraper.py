from typing import List, Dict, Any, Optional
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .enhanced_base_scraper import EnhancedBaseScraper
import time

class LinkedInScraper(EnhancedBaseScraper):
    """Enhanced LinkedIn job scraper with anti-detection measures"""
    
    def __init__(self, proxy_list_path: str = None):
        super().__init__(
            base_url="https://www.linkedin.com/jobs/search",
            site_name="LinkedIn",
            min_delay=3.0,
            max_delay=7.0,
            use_selenium=True,
            proxy_list_path=proxy_list_path
        )
        
    def search_jobs(self, query: str, location: str = None, **kwargs) -> List[Dict[str, Any]]:
        jobs = []
        location = location or "United States"
        max_jobs = kwargs.get('limit', 100)  # Default to 100 jobs if no limit specified
        
        try:
            if not self.driver:
                logging.error("Selenium driver not initialized")
                return jobs

            page = 0
            while len(jobs) < max_jobs and page < 10:  # Limit to 10 pages maximum
                url = self._build_search_url(query, location, page)
                
                try:
                    # Load the page
                    self.driver.get(url)
                    
                    # Wait for job cards to load
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "base-search-card"))
                    )
                    
                    # Scroll to load all jobs
                    self._scroll_to_load_jobs()
                    
                    # Get page content
                    content = self.driver.page_source
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Find all job cards
                    job_cards = soup.find_all('div', class_=['base-card', 'base-search-card'])
                    
                    if not job_cards:
                        logging.warning(f"No job cards found on page {page + 1}")
                        break
                    
                    # Process each job card
                    for card in job_cards:
                        if len(jobs) >= max_jobs:
                            break
                            
                        try:
                            job_data = self._parse_job_card(card)
                            if job_data:
                                jobs.append(job_data)
                        except Exception as e:
                            logging.error(f"Error processing job card: {str(e)}")
                            continue
                    
                    # Check if we need to load more
                    if len(job_cards) < 25:  # LinkedIn typically shows 25 jobs per page
                        break
                    
                    page += 1
                    self._random_delay()
                    
                except Exception as e:
                    logging.error(f"Error processing page {page}: {str(e)}")
                    break
                
        except Exception as e:
            logging.error(f"LinkedIn scraping error: {str(e)}")
            
        return jobs
    
    def _build_search_url(self, query: str, location: str, page: int) -> str:
        params = {
            'keywords': query,
            'location': location,
            'start': page * 25,
            'sortBy': 'DD',      # Most recent
            'f_TPR': 'r86400'    # Last 24 hours
        }
        return f"{self.base_url}?{urlencode(params)}"
    
    def _scroll_to_load_jobs(self):
        """Scroll the page to load all job listings"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for content to load
                time.sleep(2)
                
                # Calculate new scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                # Break if no more content
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
        except Exception as e:
            logging.error(f"Error during scrolling: {str(e)}")
    
    def _parse_job_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        try:
            # Extract job details
            title_elem = card.find(['h3', 'h4'], class_=['base-search-card__title', 'job-card-list__title'])
            company_elem = card.find(['h4', 'a'], class_=['base-search-card__subtitle', 'job-card-container__company-name'])
            location_elem = card.find('span', class_=['job-search-card__location', 'job-card-container__metadata-item'])
            
            # Verify required elements exist
            if not all([title_elem, company_elem, location_elem]):
                return None
            
            # Get URL
            link_elem = card.find('a', class_=['base-card__full-link', 'job-card-container__link'])
            if not link_elem or not link_elem.get('href'):
                return None
            
            job_data = {
                'title': title_elem.text.strip(),
                'company': company_elem.text.strip(),
                'location': location_elem.text.strip(),
                'url': link_elem['href'],
                'source': 'LinkedIn',
                'posted_date': self._extract_date(card)
            }
            
            # Extract salary if available
            salary_elem = card.find('span', class_=['job-search-card__salary-info', 'job-card-container__salary-info'])
            if salary_elem:
                job_data['salary'] = salary_elem.text.strip()
            
            return job_data
            
        except Exception as e:
            logging.error(f"Error parsing LinkedIn job card: {str(e)}")
            return None
    
    def _extract_date(self, card: BeautifulSoup) -> str:
        """Extract job posting date"""
        time_elem = card.find(['time', 'span'], class_=['job-search-card__listdate', 'job-card-container__listed-status'])
        if time_elem:
            return time_elem.get('datetime', time_elem.text.strip())
        return ''