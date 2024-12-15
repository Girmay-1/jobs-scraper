class JobScraperException(Exception):
    """Base exception class for all job scraper exceptions."""
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ScrapingException(JobScraperException):
    """Exception raised for errors during web scraping."""
    def __init__(self, message, source=None, url=None):
        self.source = source
        self.url = url
        error_code = 'SCRAPING_ERROR'
        super().__init__(f"Scraping error from {source} at {url}: {message}", error_code)

class DatabaseException(JobScraperException):
    """Exception raised for database-related errors."""
    def __init__(self, message, operation=None):
        self.operation = operation
        error_code = 'DATABASE_ERROR'
        super().__init__(f"Database error during {operation}: {message}", error_code)

class ValidationException(JobScraperException):
    """Exception raised for data validation errors."""
    def __init__(self, message, field=None):
        self.field = field
        error_code = 'VALIDATION_ERROR'
        super().__init__(f"Validation error for {field}: {message}", error_code)

class ConfigurationException(JobScraperException):
    """Exception raised for configuration-related errors."""
    def __init__(self, message, parameter=None):
        self.parameter = parameter
        error_code = 'CONFIG_ERROR'
        super().__init__(f"Configuration error for {parameter}: {message}", error_code)

class SchedulerException(JobScraperException):
    """Exception raised for scheduler-related errors."""
    def __init__(self, message, task=None):
        self.task = task
        error_code = 'SCHEDULER_ERROR'
        super().__init__(f"Scheduler error in task {task}: {message}", error_code)