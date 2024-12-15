import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    
    # Database Settings
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'jobs.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Scraping Settings
    SCRAPING_INTERVAL = int(os.getenv('SCRAPING_INTERVAL', '12'))  # hours
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 30  # seconds
    
    # Job Board URLs
    INDEED_URL = "https://www.indeed.com"
    LINKEDIN_URL = "https://www.linkedin.com/jobs"
    GLASSDOOR_URL = "https://www.glassdoor.com/Job"
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    
    # User Interface Settings
    ITEMS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 100