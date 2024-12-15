from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class RecruiterInfo(BaseModel):
    """Model for recruiter/job poster information"""
    name: Optional[str] = None
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None

class JobPosting(BaseModel):
    """Model for job posting data"""
    job_id: str = Field(..., description="Unique identifier for the job posting")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    url: str = Field(..., description="URL of the job posting")
    posted_date: datetime = Field(..., description="Date when the job was posted")
    description: str = Field(..., description="Full job description")
    salary_range: Optional[str] = Field(None, description="Salary range if provided")
    required_skills: List[str] = Field(default_factory=list, description="List of required skills")
    recruiter: Optional[RecruiterInfo] = Field(None, description="Recruiter information")
    job_board: str = Field(..., description="Source job board")
    application_status: str = Field(default="New", description="Status of job application")
    
    class Config:
        """Pydantic model configuration"""
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
