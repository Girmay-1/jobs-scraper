from datetime import datetime
from collections import deque

class GlobalRateLimiter:
    """Global rate limiter shared across all scrapers"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize or reset the rate limiter"""
        self.max_requests_per_session = 300  # Increased to 300 total requests across all sites
        self.session_requests = deque(maxlen=self.max_requests_per_session)
        self.session_start = datetime.now()
        self.requests_per_site = {}  # Track requests per site
        
    def can_make_request(self, site_name: str) -> bool:
        """Check if a new request is allowed"""
        # Check total requests
        if len(self.session_requests) >= self.max_requests_per_session:
            return False
            
        # Check per-site requests (limit each site to 1/3 of total)
        site_limit = self.max_requests_per_session // 3  # 100 requests per site
        site_requests = self.requests_per_site.get(site_name, 0)
        return site_requests < site_limit
        
    def log_request(self, site_name: str):
        """Log a new request"""
        now = datetime.now()
        self.session_requests.append(now)
        self.requests_per_site[site_name] = self.requests_per_site.get(site_name, 0) + 1
        
    def get_stats(self) -> dict:
        """Get current rate limiting stats"""
        return {
            'total_requests': len(self.session_requests),
            'max_requests': self.max_requests_per_session,
            'requests_per_site': self.requests_per_site.copy(),
            'session_start': self.session_start
        }