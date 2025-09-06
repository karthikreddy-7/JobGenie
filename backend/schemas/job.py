# schemas/job.py
from pydantic import BaseModel
from typing import Optional

class JobPosting(BaseModel):
    id: str
    site: str
    job_url: str
    job_url_direct: str
    title: str
    company: str
    location: str
    date_posted: str
    job_level: str
    description: str
    company_industry: str
    company_url: str
