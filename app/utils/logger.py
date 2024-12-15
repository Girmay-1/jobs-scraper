import logging
import os
from logging.handlers import RotatingFileHandler
from config.config import Config

def setup_logger(name, log_file):
    """Configure and return a logger instance with both file and console handlers.
    
    Args:
        name (str): The name of the logger
        log_file (str): The path to the log file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Create formatters
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # Create and configure file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    file_handler.setFormatter(formatter)
    
    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create separate loggers for different components
def get_scraper_logger():
    log_file = os.path.join(Config.LOG_DIRECTORY, 'scraper.log')
    return setup_logger('scraper', log_file)

def get_database_logger():
    log_file = os.path.join(Config.LOG_DIRECTORY, 'database.log')
    return setup_logger('database', log_file)

def get_web_logger():
    log_file = os.path.join(Config.LOG_DIRECTORY, 'web.log')
    return setup_logger('web', log_file)

def get_scheduler_logger():
    log_file = os.path.join(Config.LOG_DIRECTORY, 'scheduler.log')
    return setup_logger('scheduler', log_file)