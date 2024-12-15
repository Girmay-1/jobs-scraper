import pandas as pd
from typing import List
from datetime import datetime
from pathlib import Path
from .models import JobPosting

class ExcelExporter:
    """Class to handle exporting job data to Excel"""
    
    def __init__(self, output_dir: str = "../data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _job_to_dict(self, job: JobPosting) -> dict:
        """Convert a JobPosting object to a flat dictionary for Excel export"""
        job_dict = job.dict()
        
        # Flatten recruiter information
        if job.recruiter:
            recruiter_dict = job.recruiter.dict()
            job_dict.update({
                'recruiter_name': recruiter_dict['name'],
                'recruiter_title': recruiter_dict['title'],
                'recruiter_linkedin': recruiter_dict['linkedin_url'],
                'recruiter_email': recruiter_dict['email']
            })
        del job_dict['recruiter']
        
        # Convert skills list to comma-separated string
        job_dict['required_skills'] = ', '.join(job_dict['required_skills'])
        
        return job_dict

    def export_jobs(self, jobs: List[JobPosting], filename: str = None) -> str:
        """
        Export jobs to Excel file
        
        Args:
            jobs: List of JobPosting objects
            filename: Optional filename, if not provided will use current timestamp
            
        Returns:
            Path to the created Excel file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'job_postings_{timestamp}.xlsx'
        
        filepath = self.output_dir / filename
        
        # Convert jobs to list of dictionaries
        job_dicts = [self._job_to_dict(job) for job in jobs]
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(job_dicts)
        
        # Reorder columns for better readability
        column_order = [
            'job_id', 'title', 'company', 'location', 'url', 'posted_date',
            'salary_range', 'required_skills', 'recruiter_name', 'recruiter_title',
            'recruiter_linkedin', 'recruiter_email', 'job_board',
            'application_status', 'description'
        ]
        
        # Reorder columns (only include those that exist)
        df = df[[col for col in column_order if col in df.columns]]
        
        # Export to Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Job Postings')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Job Postings']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        return str(filepath)
