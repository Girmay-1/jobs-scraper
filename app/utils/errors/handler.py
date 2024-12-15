from functools import wraps
from app.utils.logger import get_scraper_logger, get_database_logger
from app.utils.errors.exceptions import (
    JobScraperException,
    ScrapingException,
    DatabaseException,
    ValidationException,
    ConfigurationException,
    SchedulerException
)

def handle_exceptions(logger=None):
    """
    A decorator for handling exceptions in a consistent manner across the application.
    
    Args:
        logger: The logger instance to use. If None, a default logger will be used.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_scraper_logger()
            
            try:
                return func(*args, **kwargs)
            except ScrapingException as e:
                logger.error(f"Scraping error: {e.message}", extra={
                    'source': e.source,
                    'url': e.url,
                    'error_code': e.error_code
                })
                raise
            except DatabaseException as e:
                logger.error(f"Database error: {e.message}", extra={
                    'operation': e.operation,
                    'error_code': e.error_code
                })
                raise
            except ValidationException as e:
                logger.error(f"Validation error: {e.message}", extra={
                    'field': e.field,
                    'error_code': e.error_code
                })
                raise
            except ConfigurationException as e:
                logger.error(f"Configuration error: {e.message}", extra={
                    'parameter': e.parameter,
                    'error_code': e.error_code
                })
                raise
            except SchedulerException as e:
                logger.error(f"Scheduler error: {e.message}", extra={
                    'task': e.task,
                    'error_code': e.error_code
                })
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                raise JobScraperException(f"An unexpected error occurred: {str(e)}")
        return wrapper
    return decorator

def retry_on_failure(max_retries=3, delay=1):
    """
    A decorator that implements retry logic for functions that might fail temporarily.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                    continue
                    
            raise last_exception
        return wrapper
    return decorator