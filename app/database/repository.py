from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
import logging

from .models import Job, JobApplication

class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, job_data: Dict[str, Any]) -> Job:
        """Create a new job listing"""
        try:
            job = Job(**job_data)
            self.session.add(job)
            self.session.commit()
            return job
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error creating job: {e}")
            raise

    def get(self, job_id: int) -> Optional[Job]:
        """Get a job by ID"""
        return self.session.query(Job).filter(Job.id == job_id).first()

    def update(self, job_id: int, job_data: Dict[str, Any]) -> Optional[Job]:
        """Update a job"""
        try:
            job = self.get(job_id)
            if job:
                for key, value in job_data.items():
                    setattr(job, key, value)
                self.session.commit()
            return job
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error updating job: {e}")
            raise

    def delete(self, job_id: int) -> bool:
        """Delete a job"""
        try:
            job = self.get(job_id)
            if job:
                self.session.delete(job)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error deleting job: {e}")
            raise

    def search(self, 
              keywords: Optional[str] = None,
              location: Optional[str] = None,
              company: Optional[str] = None,
              job_type: Optional[str] = None,
              days_posted: Optional[int] = None) -> List[Job]:
        """Search jobs with filters"""
        query = self.session.query(Job).filter(Job.is_active == True)

        if keywords:
            query = query.filter(
                or_(
                    Job.title.ilike(f"%{keywords}%"),
                    Job.description.ilike(f"%{keywords}%")
                )
            )

        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))

        if company:
            query = query.filter(Job.company.ilike(f"%{company}%"))

        if job_type:
            query = query.filter(Job.job_type == job_type)

        if days_posted:
            date_threshold = datetime.now() - timedelta(days=days_posted)
            query = query.filter(Job.posted_date >= date_threshold)

        return query.order_by(Job.posted_date.desc()).all()

class JobApplicationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, application_data: Dict[str, Any]) -> JobApplication:
        """Create a new job application"""
        try:
            application = JobApplication(**application_data)
            self.session.add(application)
            self.session.commit()
            return application
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error creating application: {e}")
            raise

    def get(self, application_id: int) -> Optional[JobApplication]:
        """Get an application by ID"""
        return self.session.query(JobApplication)\
            .filter(JobApplication.id == application_id)\
            .first()

    def update_status(self, application_id: int, status: str) -> Optional[JobApplication]:
        """Update application status"""
        try:
            application = self.get(application_id)
            if application:
                application.status = status
                self.session.commit()
            return application
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error updating application: {e}")
            raise