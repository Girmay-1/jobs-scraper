import logging
import os
from pathlib import Path
from .db import Database

# Configure database path
BASE_DIR = Path(__file__).parent.parent.parent
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'jobs.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

def init_database():
    """Initialize the database"""
    # Initialize database with config
    db = Database(
        db_uri=SQLALCHEMY_DATABASE_URI,
        db_path=DATABASE_PATH
    )
    
    try:
        # Create all tables
        db.create_tables()
        
        # Set secure file permissions (readable/writable only by owner)
        os.chmod(DATABASE_PATH, 0o600)
        
        # Set secure directory permissions
        db_dir = os.path.dirname(DATABASE_PATH)
        os.chmod(db_dir, 0o700)
        
        logging.info("Database initialization completed successfully")
        logging.info(f"Database created at: {DATABASE_PATH}")
        logging.info("Secure file permissions set")
        
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise

if __name__ == '__main__':
    init_database()