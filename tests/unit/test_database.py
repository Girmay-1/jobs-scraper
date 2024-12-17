import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base, Job, JobApplication
from app.database.repository import JobRepository

@pytest.fixture
def test_db():
    """Create a test database"""
    db_path = "test_jobs.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def job_repository(test_db):
    return JobRepository(test_db)

def test_create_job(job_repository):
    job_data = {
        'title': 'Test Job',
        'company': 'Test Company',
        'location': 'Test Location',
        'url': 'https://test.com/job/1',
        'source': 'Test'
    }
    
    job = job_repository.create(job_data)
    
    assert job.id is not None
    assert job.title == job_data['title']
    assert job.company == job_data['company']
    assert job.url == job_data['url']

def test_get_job(job_repository):
    # Create a job first
    job_data = {
        'title': 'Test Job',
        'company': 'Test Company',
        'location': 'Test Location',
        'url': 'https://test.com/job/1',
        'source': 'Test'
    }
    created_job = job_repository.create(job_data)
    
    # Retrieve the job
    job = job_repository.get(created_job.id)
    
    assert job is not None
    assert job.id == created_job.id
    assert job.title == job_data['title']

def test_update_job(job_repository):
    # Create a job first
    job_data = {
        'title': 'Test Job',
        'company': 'Test Company',
        'location': 'Test Location',
        'url': 'https://test.com/job/1',
        'source': 'Test'
    }
    job = job_repository.create(job_data)
    
    # Update the job
    updated_data = {
        'title': 'Updated Job',
        'company': 'Updated Company'
    }
    updated_job = job_repository.update(job.id, updated_data)
    
    assert updated_job.title == updated_data['title']
    assert updated_job.company == updated_data['company']
    assert updated_job.location == job_data['location']  # Unchanged field

def test_delete_job(job_repository):
    # Create a job first
    job_data = {
        'title': 'Test Job',
        'company': 'Test Company',
        'location': 'Test Location',
        'url': 'https://test.com/job/1',
        'source': 'Test'
    }
    job = job_repository.create(job_data)
    
    # Delete the job
    result = job_repository.delete(job.id)
    assert result is True
    
    # Try to retrieve the deleted job
    deleted_job = job_repository.get(job.id)
    assert deleted_job is None

def test_search_jobs(job_repository):
    # Create multiple jobs
    jobs_data = [
        {
            'title': 'Python Developer',
            'company': 'Tech Co',
            'location': 'New York, NY',
            'url': 'https://test.com/job/1',
            'source': 'Test',
            'job_type': 'Full Time'
        },
        {
            'title': 'Senior Developer',
            'company': 'Software Inc',
            'location': 'Remote',
            'url': 'https://test.com/job/2',
            'source': 'Test',
            'job_type': 'Contract'
        }
    ]
    
    for job_data in jobs_data:
        job_repository.create(job_data)
    
    # Test different search criteria
    python_jobs = job_repository.search(keywords='Python')
    assert len(python_jobs) == 1
    
    remote_jobs = job_repository.search(location='Remote')
    assert len(remote_jobs) == 1
    
    full_time_jobs = job_repository.search(job_type='Full Time')
    assert len(full_time_jobs) == 1