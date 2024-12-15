from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any
import time
import requests
from bs4 import BeautifulSoup

class BaseScraper(ABC):
    """
    Base class for all job scrapers.
    Implements common functionality and defines interface for specific job board scrapers.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.setup_logging()

    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def search_jobs(self, keywords: List[str], location: str = "United States") -> List[Dict[Any, Any]]:
        """
        Search for jobs using the provided keywords and location.
        Must be implemented by each specific scraper.
        """
        pass

    def make_request(self, url: str, method: str = "GET", data: Dict = None) -> requests.Response:
        """
        Make an HTTP request with built-in retry logic and rate limiting
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                # Basic rate limiting
                time.sleep(1)  # Minimum 1 second between requests
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    data=data
                )
                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    raise
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff

    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup
        """
        return BeautifulSoup(html_content, 'html.parser')

    @abstractmethod
    def extract_job_details(self, job_element: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract job details from a job posting element.
        Must be implemented by each specific scraper.
        """
        pass

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text data
        """
        if not text:
            return ""
        return " ".join(text.strip().split())
