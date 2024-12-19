from typing import Optional, List, Dict, Any
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from .base_scraper import BaseScraper

class EnhancedBaseScraper(BaseScraper):
    def __init__(self, base_url: str, site_name: str, min_delay: float = 2.0, 
                 max_delay: float = 5.0, use_selenium: bool = False, 
                 proxy_list_path: str = None):
        super().__init__(base_url, site_name, min_delay, max_delay)
        self.use_selenium = use_selenium
        self.proxy_list = self._load_proxies(proxy_list_path) if proxy_list_path else None
        self.user_agent = UserAgent()
        self.driver = self._init_selenium() if use_selenium else None

    def _init_selenium(self) -> Optional[webdriver.Chrome]:
        """Initialize Selenium WebDriver with anti-detection measures"""
        try:
            options = Options()
            # Don't use headless mode so we can see and interact with the browser
            options.add_argument('--start-maximized')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument(f'--user-agent={self.user_agent.random}')
            
            # Disable automation flags
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize service and driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Additional stealth settings
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": self.user_agent.random
            })
            
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                '''
            })
            
            return driver
            
        except Exception as e:
            logging.error(f"Failed to initialize Selenium: {str(e)}")
            return None

    def _load_proxies(self, proxy_list_path: str) -> List[str]:
        """Load proxies from file"""
        try:
            with open(proxy_list_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Failed to load proxies: {str(e)}")
            return []
            
    def normalize_location(self, location: str) -> str:
        """Normalize location string"""
        location = location.replace('•', '').strip()
        return ' '.join(location.split())
        
    def normalize_salary(self, salary: str) -> str:
        """Normalize salary string"""
        return salary.replace('Estimated', '').replace('$', '').strip()

    def __del__(self):
        """Clean up Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass