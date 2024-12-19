import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
from urllib.parse import urljoin
from abc import ABC, abstractmethod

from .rate_limiter import GlobalRateLimiter

class BaseScraper(ABC):
    """Base class for job scrapers with common functionality"""
    
    def __init__(self, 
                 base_url: str,
                 site_name: str,
                 min_delay: float = 1.0, 
                 max_delay: float = 3.0,
                 timeout: int = 30,
                 max_pages: int = 10):
        """
        Initialize base scraper
        
        Args:
            base_url: Base URL for the job site
            site_name: Name of the job site (e.g., 'Indeed', 'LinkedIn')
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
            timeout: Request timeout in seconds
            max_pages: Maximum number of pages to scrape per search
        """
        self.base_url = base_url
        self.site_name = site_name
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.max_pages = max_pages
        self.session = self._init_session()
        self.rate_limiter = GlobalRateLimiter()
        self.total_requests = 0

    def _init_session(self) -> requests.Session:
        """Initialize requests session with default headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        return session

    def _random_delay(self, min_delay: float = None, max_delay: float = None):
        """Add random delay between requests to avoid rate limiting"""
        min_d = min_delay if min_delay is not None else self.min_delay
        max_d = max_delay if max_delay is not None else self.max_delay
        delay = random.uniform(min_d, max_d)
        time.sleep(delay)

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Make HTTP request with rate limiting and error handling"""
        if not self.rate_limiter.can_make_request(self.site_name):
            stats = self.rate_limiter.get_stats()
            raise Exception(f"Rate limit reached for {self.site_name}. Stats: {stats}")
            
        try:
            self._random_delay()
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            
            # Log successful request
            self.rate_limiter.log_request(self.site_name)
            self.total_requests += 1
            
            logging.info(f"{self.site_name}: Made request {self.total_requests}")
            return response
            
        except requests.RequestException as e:
            logging.error(f"Request failed for {url}: {str(e)}")
            raise

    def normalize_salary(self, salary: str) -> Optional[Dict[str, float]]:
        """Normalize salary string into min/max values"""
        if not salary:
            return None

        # Remove common currency symbols and text
        salary = salary.replace('$', '')\
                      .replace(',', '')\
                      .replace('per year', '')\
                      .replace('a year', '')\
                      .replace('an hour', '')\
                      .strip()

        # Handle ranges like "50k - 70k"
        if ' - ' in salary:
            min_sal, max_sal = salary.split(' - ')
            return {
                'min': float(min_sal.replace('k', '000')),
                'max': float(max_sal.replace('k', '000'))
            }

        # If no range, clean the single value
        salary = salary.replace('k', '000')\
                      .replace('Estimated: ', '')\
                      .strip()

        amount = float(salary)
        return {
            'min': amount,
            'max': amount
        }

    def normalize_job_type(self, job_type: str) -> str:
        """Normalize job type string"""
        if not job_type:
            return "Unknown"

        job_type = job_type.lower()
        
        if 'full' in job_type:
            return 'Full-time'
        elif 'part' in job_type:
            return 'Part-time'
        elif 'contract' in job_type:
            return 'Contract'
        elif 'temp' in job_type:
            return 'Temporary'
        else:
            return 'Other'

    def normalize_location(self, location: str) -> Dict[str, str]:
        """Normalize location string into city/state"""
        if not location:
            return {'city': 'Unknown', 'state': 'Unknown'}
            
        parts = location.split(',')
        if len(parts) >= 2:
            return {
                'city': parts[0].strip(),
                'state': parts[1].strip()
            }
        return {
            'city': location.strip(),
            'state': 'Unknown'
        }

    def normalize_date(self, date_str: str) -> datetime:
        """Normalize date string into datetime object"""
        if not date_str:
            return datetime.now()

        try:
            # Handle relative dates
            date_str = date_str.lower()
            if any(x in date_str for x in ['just posted', 'today', 'posted today']):
                return datetime.now()

            if 'day ago' in date_str or 'days ago' in date_str:
                days = int(date_str.split()[0])
                return datetime.now() - timedelta(days=days)

            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

            logging.error(f"Error parsing date {date_str}: Unable to parse date: {date_str}")
            return datetime.now()

        except Exception as e:
            logging.error(f"Error parsing date {date_str}: {str(e)}")
            return datetime.now()

    @abstractmethod
    def search_jobs(self, query: str, location: str = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for jobs using the given criteria
        
        Args:
            query: Search query string
            location: Location string
            **kwargs: Additional search parameters
            
        Returns:
            List of job listings
        """
        pass