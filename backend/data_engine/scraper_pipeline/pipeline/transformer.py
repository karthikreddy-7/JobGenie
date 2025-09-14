# pipeline/transformer.py
import pandas as pd
from typing import List

from backend.schemas.job import JobPosting
from ..helper.util import safe_str, generate_id
from ..helper.constants import JobFields

def transform_jobs(df: pd.DataFrame) -> List[JobPosting]:
    """Transforms a DataFrame of raw job data into a list of JobPosting objects."""
    job_postings = []
    for _, row in df.iterrows():
        job_id = generate_id(safe_str(row.get(JobFields.JOB_URL)) + safe_str(row.get(JobFields.TITLE)))
        
        job_posting = JobPosting(
            id=job_id,
            site=safe_str(row.get(JobFields.SITE)),
            job_url=safe_str(row.get(JobFields.JOB_URL)),
            job_url_direct=safe_str(row.get(JobFields.JOB_URL_DIRECT)),
            title=safe_str(row.get(JobFields.TITLE)),
            company=safe_str(row.get(JobFields.COMPANY)),
            location=safe_str(row.get(JobFields.LOCATION)),
            date_posted=safe_str(row.get(JobFields.DATE_POSTED)),
            job_level=safe_str(row.get("job_level")),
            description=safe_str(row.get(JobFields.DESCRIPTION)),
            company_industry=safe_str(row.get(JobFields.COMPANY_INDUSTRY)),
            company_url=safe_str(row.get(JobFields.COMPANY_URL)),
            min_exp_required=None # To be filled later
        )
        job_postings.append(job_posting)
    
    return job_postings
