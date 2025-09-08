from jobspy import scrape_jobs
from data_engine.interfaces import DataEngine
from schemas.job import JobPosting
import uuid

from helper.util import safe_str
from helper import constants as c
from database.models import Job
from database.setup_db import get_db


class LinkedInDataEngine(DataEngine):
    """Concrete DataEngine implementation using JobSpy for LinkedIn."""

    def fetch_jobs(self, query: str, location: str, limit: int = 50):
        jobs_df = scrape_jobs(
            site_name=[c.SITE_NAME],
            search_term=query,
            location=location,
            results_wanted=limit,
            hours_old=100,
            linkedin_fetch_description=True
        )
        if jobs_df is None or jobs_df.empty:
            return []

        job_postings = []
        for _, row in jobs_df.iterrows():
            job_postings.append(JobPosting(
                id=safe_str(row.get(c.ID) or str(uuid.uuid4())),
                site=safe_str(row.get(c.SITE)),
                job_url=safe_str(row.get(c.JOB_URL)),
                job_url_direct=safe_str(row.get(c.JOB_URL_DIRECT)),
                title=safe_str(row.get(c.TITLE)),
                company=safe_str(row.get(c.COMPANY)),
                location=safe_str(row.get(c.LOCATION)),
                date_posted=safe_str(row.get(c.DATE_POSTED)),
                job_level=safe_str(row.get(c.JOB_LEVEL)),
                description=safe_str(row.get(c.DESCRIPTION)),
                company_industry=safe_str(row.get(c.COMPANY_INDUSTRY)),
                company_url=safe_str(row.get(c.COMPANY_URL)),
            ))

        db = next(get_db())
        for posting in job_postings:
            existing_job = db.query(Job).filter(Job.job_id == posting.id).first()
            if existing_job:
                continue
            job = Job(
                job_id=posting.id,
                site=posting.site,
                job_url=posting.job_url,
                job_url_direct=posting.job_url_direct,
                title=posting.title,
                company=posting.company,
                location=posting.location,
                date_posted=posting.date_posted,
                job_level=posting.job_level,
                description=posting.description,
                company_industry=posting.company_industry,
                company_url=posting.company_url
            )
            db.add(job)
        db.commit()

        return job_postings


# Example Run
# To run this file directly, use:
#   python -m data_engine.linkedin_scraper
# from the project root (backend/)
if __name__=='__main__':
    engine = LinkedInDataEngine()
    jobs = engine.fetch_jobs(query="software engineer", location="Mumbai, India", limit=100)
