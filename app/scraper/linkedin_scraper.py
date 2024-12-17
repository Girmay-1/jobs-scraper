import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlencode
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn job listings"""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Initialize LinkedIn scraper"""
        super().__init__(
            base_url="https://www.linkedin.com/jobs",
            site_name="LinkedIn",
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
        """Build LinkedIn search URL with parameters"""
        params = {
            'keywords': query,
            'location': location,
            'start': page * 25,  # LinkedIn shows 25 jobs per page
            'position': 1,
            'pageNum': page,
            'geoId': '103644278',  # United States geo ID
            'f_TPR': 'r86400',     # Last 24 hours
        }
        return f"{self.base_url}/search?{urlencode(params)}"

    def _extract_job_cards(self, soup: BeautifulSoup) -> List[Any]:
        """Extract job cards from search results page"""
        return soup.find_all('div', class_='base-card')

    def _is_us_location(self, location: str) -> bool:
        """Check if the job location is in the US"""
        if not location:
            return False
            
        location = location.upper()
        # Check for US state names or abbreviations
        for state in self.us_states:
            if f", {state}" in location or f", {state.title()}" in location:
                return True
                
        # Check for United States, USA, or Remote
        if "UNITED STATES" in location or "USA" in location or "REMOTE" in location:
            return True
            
        return False

    def _parse_job_card(self, card: Any) -> Optional[Dict[str, Any]]:
        """Parse individual job card data"""
        try:
            # Extract basic job information
            title_elem = card.find('h3', class_='base-search-card__title')
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            location_elem = card.find('span', class_='job-search-card__location')
            
            if not (title_elem and company_elem and location_elem):
                return None
                
            location = location_elem.text.strip()
            # Skip non-US jobs
            if not self._is_us_location(location):
                return None
                
            # Get job URL
            job_link = card.find('a', class_='base-card__full-link')
            job_url = job_link.get('href') if job_link else None
            
            if not job_url:
                return None
            
            # Extract additional information
            job_type_elem = card.find('span', class_='job-search-card__listdate')
            date_elem = card.find('time', class_='job-search-card__listdate')
            
            # Build normalized job data
            job_data = {
                'title': title_elem.text.strip(),
                'company': company_elem.text.strip(),
                'location': self._normalize_location(location),
                'salary_range': None,  # LinkedIn usually doesn't show salary on cards
                'job_type': self._normalize_job_type(job_type_elem.text.strip() if job_type_elem else None),
                'url': job_url,
                'source': 'LinkedIn',
                'posted_date': self._normalize_date(date_elem.get('datetime') if date_elem else None),
                'description': None  # Will be filled in by get_job_details
            }
            
            return job_data
            
        except Exception as e:
            logging.error(f"Error parsing LinkedIn job data: {e}")
            return None

    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed job information from job page"""
        try:
            soup = self._get_soup(job_url)
            
            # Find job description
            description_elem = soup.find('div', class_='show-more-less-html__markup')
            if not description_elem:
                return None
            
            # Try to find salary information in the details
            salary_elem = soup.find('span', class_='salary')
            
            # Try to find employment type
            job_type_elem = soup.find('span', class_='employment-type')
            
            details = {
                'description': description_elem.get_text(strip=True),
                'url': job_url,
                'source': 'LinkedIn'
            }
            
            # Add salary if found
            if salary_elem:
                details['salary_range'] = self._normalize_salary(salary_elem.text)
                
            # Add or update job type if found
            if job_type_elem:
                details['job_type'] = self._normalize_job_type(job_type_elem.text)
            
            return details
            
        except Exception as e:
            logging.error(f"Error fetching LinkedIn job details from {job_url}: {e}")
            return None