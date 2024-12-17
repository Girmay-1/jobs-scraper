import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlencode
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

class IndeedScraper(BaseScraper):
    """Scraper for Indeed job listings"""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Initialize Indeed scraper"""
        super().__init__(
            base_url="https://www.indeed.com",
            site_name="Indeed",
            min_delay=min_delay,
            max_delay=max_delay
        )
        self.us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }
    
    def _build_search_url(self, query: str, location: str, page: int) -> str:
        """Build Indeed search URL with parameters"""
        params = {
            'q': query,
            'l': location,
            'start': page * 15,
            'country': 'US',  # Ensure US jobs only
        }
        return f"{self.base_url}/jobs?{urlencode(params)}"

    def _is_us_location(self, location: str) -> bool:
        """Check if the job location is in the US"""
        if not location:
            return False
            
        location = location.upper()
        # Check for US state names or abbreviations
        for state in self.us_states:
            if f", {state}" in location or f", {state.title()}" in location:
                return True
                
        # Check for "United States" or "Remote"
        if "UNITED STATES" in location or "USA" in location or "REMOTE" in location:
            return True
            
        return False

    def _parse_job_card(self, card: Any) -> Optional[Dict[str, Any]]:
        """Parse individual job card data"""
        try:
            # Extract basic job information
            title_elem = card.find('h2', class_='jobTitle')
            company_elem = card.find('span', class_='companyName')
            location_elem = card.find('div', class_='companyLocation')
            
            if not (title_elem and company_elem and location_elem):
                return None
                
            location = location_elem.text.strip()
            # Skip non-US jobs
            if not self._is_us_location(location):
                return None
                
            # Get job URL
            title_link = title_elem.find('a')
            job_url = self._build_full_url(title_link.get('href')) if title_link else None
            
            if not job_url:
                return None
            
            # Extract additional information
            salary_elem = card.find('div', class_='salary-snippet-container')
            job_type_elem = card.find('div', class_='attribute_snippet')
            date_elem = card.find('span', class_='date')
            
            # Build normalized job data
            job_data = {
                'title': title_elem.text.strip(),
                'company': company_elem.text.strip(),
                'location': self._normalize_location(location),
                'salary_range': self._normalize_salary(salary_elem.text if salary_elem else None),
                'job_type': self._normalize_job_type(job_type_elem.text if job_type_elem else None),
                'url': job_url,
                'source': 'Indeed',
                'posted_date': self._normalize_date(date_elem.text if date_elem else None),
                'description': None  # Will be filled in by get_job_details
            }
            
            return job_data
            
        except Exception as e:
            logging.error(f"Error parsing Indeed job data: {e}")
            return None

    # ... rest of the methods remain the same ...