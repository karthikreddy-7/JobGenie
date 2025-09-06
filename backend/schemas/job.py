# schemas/job.py
from pydantic import BaseModel
from typing import Optional

class JobPosting(BaseModel):
    job_id: str # this should be actual job_id from data source, if not available, use random + random uuid (not recommended)
    title: str  # if job title ? job title else company name + posted date
    description: str # if job description ? job description else "No description available"
    company: str # if company name ? company name else "Unknown Company"
    location: str # if location ? location else "Not specified"
    link: str # if job link ? job link else "No link available"
    source: str = "LinkedIn" # if source ? source else "Unknown Source"
