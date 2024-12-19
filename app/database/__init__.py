from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Create SQLite database engine
DATABASE_URL = "sqlite:///jobs.db"
engine = create_engine(DATABASE_URL)

# Create session factory
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

# Initialize the database
def init_db():
    from .models import Base
    Base.metadata.create_all(bind=engine)

def get_session():
    return Session()