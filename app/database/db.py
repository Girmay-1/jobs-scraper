from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
from datetime import datetime
import shutil
from pathlib import Path
from typing import Optional

from .models import Base

class Database:
    def __init__(self, db_uri: str, db_path: str):
        """Initialize database connection
        
        Args:
            db_uri: SQLAlchemy database URI from app config
            db_path: Database file path from app config
        """
        self.db_path = db_path
        self._ensure_data_directory()
        
        # Use the configured SQLAlchemy URI
        self.engine = create_engine(db_uri, echo=False)
        
        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

    def _ensure_data_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def create_tables(self):
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(self.engine)
            logging.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logging.error(f"Error creating database tables: {e}")
            raise

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def backup_database(self) -> str:
        """Create a backup of the database"""
        try:
            # Close any open sessions
            self.Session.remove()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, f"jobs_db_backup_{timestamp}.db")
            shutil.copy2(self.db_path, backup_path)
            
            logging.info(f"Database backed up successfully to {backup_path}")
            return backup_path
            
        except Exception as e:
            logging.error(f"Backup error: {e}")
            raise