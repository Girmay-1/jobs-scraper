from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, contains_eager
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
import logging
from sqlalchemy.sql import text

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
        """Get a job by ID with optimized loading"""
        return self.session.query(Job)\
            .options(contains_eager(Job.applications))\
            .filter(Job.id == job_id)\
            .first()

    def bulk_create(self, jobs_data: List[Dict[str, Any]]) -> List[Job]:
        """Bulk create jobs for better performance"""
        try:
            jobs = [Job(**data) for data in jobs_data]
            self.session.bulk_save_objects(jobs)
            self.session.commit()
            return jobs
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error bulk creating jobs: {e}")
            raise

    def search(self, 
              keywords: Optional[str] = None,
              location: Optional[str] = None,
              company: Optional[str] = None,
              job_type: Optional[str] = None,
              days_posted: Optional[int] = None,
              source: Optional[str] = None) -> List[Job]:
        """Optimized search with query building"""
        try:
            # Start with base query
            query = self.session.query(Job).filter(Job.is_active == True)

            # Build filter conditions
            conditions = []
            
            if keywords:
                keyword_filter = or_(
                    Job.title.ilike(f"%{keywords}%"),
                    Job.description.ilike(f"%{keywords}%")
                )
                conditions.append(keyword_filter)

            if location:
                conditions.append(Job.location.ilike(f"%{location}%"))

            if company:
                conditions.append(Job.company.ilike(f"%{company}%"))

            if job_type:
                conditions.append(Job.job_type == job_type)

            if source:
                conditions.append(Job.source == source)

            if days_posted:
                date_threshold = datetime.now() - timedelta(days=days_posted)
                conditions.append(Job.posted_date >= date_threshold)

            # Apply all conditions at once
            if conditions:
                query = query.filter(and_(*conditions))

            # Optimize loading with limit
            return query.order_by(Job.posted_date.desc())\
                       .limit(1000)\
                       .all()

        except Exception as e:
            logging.error(f"Error searching jobs: {e}")
            raise

    def get_job_statistics(self) -> Dict[str, Any]:
        """Get job statistics using optimized queries"""
        try:
            # Use raw SQL for complex aggregations
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(DISTINCT company) as unique_companies,
                    COUNT(DISTINCT location) as unique_locations,
                    AVG(CASE 
                        WHEN salary_range REGEXP '^[0-9]+' 
                        THEN CAST(REGEXP_SUBSTR(salary_range, '^[0-9]+') AS INTEGER)
                        ELSE NULL 
                    END) as avg_salary_min
                FROM jobs 
                WHERE is_active = 1
            """)
            
            result = self.session.execute(stats_query).first()
            
            return {
                'total_jobs': result.total_jobs,
                'unique_companies': result.unique_companies,
                'unique_locations': result.unique_locations,
                'avg_salary_min': round(result.avg_salary_min) if result.avg_salary_min else None
            }
            
        except Exception as e:
            logging.error(f"Error getting job statistics: {e}")
            raise

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

    def get_with_job(self, application_id: int) -> Optional[JobApplication]:
        """Get application with job details optimized"""
        return self.session.query(JobApplication)\
            .options(contains_eager(JobApplication.job))\
            .filter(JobApplication.id == application_id)\
            .first()

    def get_application_stats(self) -> Dict[str, int]:
        """Get application statistics using optimized query"""
        try:
            stats_query = text("""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM job_applications
                GROUP BY status
            """)
            
            result = self.session.execute(stats_query)
            
            return {row.status: row.count for row in result}
            
        except Exception as e:
            logging.error(f"Error getting application statistics: {e}")
            raise