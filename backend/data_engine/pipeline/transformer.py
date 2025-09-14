# pipeline/transformer.py
import logging
import pandas as pd
from typing import List

from backend.data_engine.helper.constants import JobFields
from backend.data_engine.helper.util import generate_id, safe_str
from backend.schemas.job import JobPosting

logger = logging.getLogger(__name__)

def transform_jobs(df: pd.DataFrame) -> List[JobPosting]:
    """Transforms a DataFrame of raw job data into a list of JobPosting objects."""
    logger.info(f"Transforming {len(df)} raw job listings.")
    job_postings = []
    for _, row in df.iterrows():
        try:
            job_id = generate_id(safe_str(row.get(JobFields.JOB_URL)) + safe_str(row.get(JobFields.TITLE)))
            
            job_posting = JobPosting(
                id=safe_str(row.get(JobFields.ID)),
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
        except Exception as e:
            logger.error(f"Error transforming a job listing: {e}", exc_info=True)
    
    logger.info(f"Successfully transformed {len(job_postings)} job listings.")
    return job_postings