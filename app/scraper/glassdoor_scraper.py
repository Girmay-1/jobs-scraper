import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlencode
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

class GlassdoorScraper(BaseScraper):
    """Scraper for Glassdoor job listings"""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Initialize Glassdoor scraper"""
        super().__init__(
            base_url="https://www.glassdoor.com",
            site_name="Glassdoor",
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
        """Build Glassdoor search URL with parameters"""
        params = {
            'sc.keyword': query,
            'locT': 'N',  # Nationwide
            'locId': '1',  # United States
            'page': page + 1,  # Glassdoor uses 1-based page numbers
            'countryRedirect': 'true'
        }
        return f"{self.base_url}/Job/jobs.htm?{urlencode(params)}"

    def _extract_job_cards(self, soup: BeautifulSoup) -> List[Any]:
        """Extract job cards from search results page"""
        return soup.find_all('li', {'class': 'react-job-listing'})

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
            title_elem = card.find('a', {'class': 'jobLink'})
            company_elem = card.find('div', {'class': 'jobEmployerName'})
            location_elem = card.find('span', {'class': 'jobLocation'})
            
            if not (title_elem and company_elem and location_elem):
                return None
                
            location = location_elem.text.strip()
            # Skip non-US jobs
            if not self._is_us_location(location):
                return None
                
            # Get job URL
            job_url = self._build_full_url(title_elem.get('href'))
            if not job_url:
                return None
            
            # Extract additional information
            salary_elem = card.find('span', {'class': 'salary-estimate'})
            job_type_elem = card.find('span', {'class': 'jobType'})
            date_elem = card.find('div', {'class': 'listing-age'})
            
            # Build normalized job data
            job_data = {
                'title': title_elem.text.strip(),
                'company': company_elem.text.strip(),
                'location': self._normalize_location(location),
                'salary_range': self._normalize_salary(salary_elem.text.strip() if salary_elem else None),
                'job_type': self._normalize_job_type(job_type_elem.text.strip() if job_type_elem else None),
                'url': job_url,
                'source': 'Glassdoor',
                'posted_date': self._normalize_date(date_elem.text.strip() if date_elem else None),
                'description': None  # Will be filled in by get_job_details
            }
            
            return job_data
            
        except Exception as e:
            logging.error(f"Error parsing Glassdoor job data: {e}")
            return None

    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed job information from job page"""
        try:
            soup = self._get_soup(job_url)
            
            # Find job description
            description_elem = soup.find('div', {'class': 'jobDescriptionContent'})
            if not description_elem:
                return None
            
            # Try to find additional details
            benefits_elem = soup.find('div', {'class': 'benefits'})
            additional_info = soup.find('div', {'class': 'jobDetails'})
            
            details = {
                'description': description_elem.get_text(strip=True),
                'url': job_url,
                'source': 'Glassdoor'
            }
            
            # Add benefits if found
            if benefits_elem:
                details['benefits'] = benefits_elem.get_text(strip=True)
                
            return details
            
        except Exception as e:
            logging.error(f"Error fetching Glassdoor job details from {job_url}: {e}")
            return None

    def _handle_login_prompt(self, soup: BeautifulSoup) -> bool:
        """Check if we've hit a login wall and handle it"""
        login_wall = soup.find('div', {'class': 'SignInModal'})
        if login_wall:
            logging.warning("Hit Glassdoor login wall - some data may be incomplete")
            return True
        return False