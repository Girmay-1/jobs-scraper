import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from datetime import datetime

from app.scraper.base_scraper import BaseScraper

class TestScraper(BaseScraper):
    """Test implementation of BaseScraper"""
    def __init__(self):
        super().__init__(
            base_url="https://test.com",
            site_name="TestSite"
        )

    def search_jobs(self, query, location):
        pass

def test_normalize_salary():
    scraper = TestScraper()
    
    test_cases = [
        ("$50,000 - $70,000 a year", "50000-70000/year"),
        ("$30 an hour", "30/hour"),
        ("$40k - $60k per year", "40000-60000/year"),
        ("Estimated: $90,000", "90000"),
        (None, None),
        ("", None)
    ]
    
    for input_text, expected in test_cases:
        assert scraper._normalize_salary(input_text) == expected

def test_normalize_job_type():
    scraper = TestScraper()
    
    test_cases = [
        ("Full-time", "Full Time"),
        ("PART-TIME", "Part Time"),
        ("Contract", "Contract"),
        ("Remote", "Remote"),
        ("full time", "Full Time"),
        (None, None),
        ("", None)
    ]
    
    for input_text, expected in test_cases:
        assert scraper._normalize_job_type(input_text) == expected

def test_normalize_location():
    scraper = TestScraper()
    
    test_cases = [
        ("New York, NY", "New York, NY"),
        ("located in San Francisco, CA", "San Francisco, CA"),
        ("location: Austin, TX", "Austin, TX"),
        ("Remote", "Remote"),
        (None, None),
        ("", None)
    ]
    
    for input_text, expected in test_cases:
        assert scraper._normalize_location(input_text) == expected

def test_normalize_date():
    scraper = TestScraper()
    now = datetime.now()
    
    test_cases = [
        ("Just posted", now),
        ("Today", now),
        ("Posted today", now),
        ("1 day ago", now.replace(day=now.day-1)),
        ("2 days ago", now.replace(day=now.day-2)),
        (None, None)
    ]
    
    for input_text, expected in test_cases:
        result = scraper._normalize_date(input_text)
        if expected:
            assert result.date() == expected.date()
        else:
            assert result == expected

@patch('requests.Session')
def test_make_request(mock_session):
    scraper = TestScraper()
    mock_response = Mock()
    mock_response.text = "<html></html>"
    mock_session.return_value.get.return_value = mock_response
    
    response = scraper._make_request("https://test.com")
    assert response == mock_response
    mock_session.return_value.get.assert_called_once()