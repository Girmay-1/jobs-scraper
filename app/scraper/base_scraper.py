import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime
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

    # ... [rest of the methods remain the same] ...