import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from app.scraper.base_scraper import BaseScraper

class TestScraper(BaseScraper):
    """Test implementation of BaseScraper"""
    def __init__(self):
        super().__init__(
            base_url="https://test.com",
            site_name="TestSite"
        )

    def search_jobs(self, query: str, location: str = None, **kwargs):
        """Mock implementation of search_jobs"""
        return []

def test_normalize_salary():
    scraper = TestScraper()
    
    test_cases = [
        ("$50,000 - $70,000 a year", {"min": 50000.0, "max": 70000.0}),
        ("$30 an hour", {"min": 30.0, "max": 30.0}),
        ("$40k - $60k per year", {"min": 40000.0, "max": 60000.0}),
        ("Estimated: $90,000", {"min": 90000.0, "max": 90000.0}),
        (None, None),
        ("", None)
    ]
    
    for input_text, expected in test_cases:
        assert scraper.normalize_salary(input_text) == expected

def test_normalize_job_type():
    scraper = TestScraper()
    
    test_cases = [
        ("Full-time", "Full-time"),
        ("PART-TIME", "Part-time"),
        ("Contract", "Contract"),
        ("full time", "Full-time"),
        ("part", "Part-time"),
        (None, "Unknown"),
        ("", "Unknown")
    ]
    
    for input_text, expected in test_cases:
        assert scraper.normalize_job_type(input_text) == expected

def test_normalize_location():
    scraper = TestScraper()
    
    test_cases = [
        ("New York, NY", {"city": "New York", "state": "NY"}),
        ("San Francisco, CA", {"city": "San Francisco", "state": "CA"}),
        ("Austin, TX", {"city": "Austin", "state": "TX"}),
        ("Remote", {"city": "Remote", "state": "Unknown"}),
        (None, {"city": "Unknown", "state": "Unknown"}),
        ("", {"city": "Unknown", "state": "Unknown"})
    ]
    
    for input_text, expected in test_cases:
        assert scraper.normalize_location(input_text) == expected

def test_normalize_date():
    scraper = TestScraper()
    now = datetime.now()
    
    test_cases = [
        ("Just posted", now),
        ("Today", now),
        ("Posted today", now),
        ("1 day ago", now - timedelta(days=1)),
        ("2 days ago", now - timedelta(days=2)),
        (None, now)
    ]
    
    for input_text, expected in test_cases:
        result = scraper.normalize_date(input_text)
        # Compare just the date portion since times will differ slightly
        assert result.date() == expected.date()

@patch('requests.Session')
def test_make_request(mock_session):
    scraper = TestScraper()
    mock_response = Mock()
    mock_response.text = "<html></html>"
    mock_session.return_value.request.return_value = mock_response
    
    response = scraper._make_request("https://test.com")
    assert response == mock_response
    mock_session.return_value.request.assert_called_once_with(
        method='GET',
        url="https://test.com",
        timeout=30
    )