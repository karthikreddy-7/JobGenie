from jobspy import scrape_jobs
from data_engine.interfaces import DataEngine
from schemas.job import JobPosting
import uuid

from helper.util import safe_str
from helper import constants as c


class LinkedInDataEngine(DataEngine):
    """Concrete DataEngine implementation using JobSpy for LinkedIn."""

    def fetch_jobs(self, query: str, location: str, limit: int = 50):
        jobs_df = scrape_jobs(
            site_name=[c.SITE_NAME],
            search_term=query,
            location=location,
            results_wanted=limit,
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

        for posting in job_postings:
            print(posting)

        return job_postings


#Example Run
if __name__=='__main__':
    engine = LinkedInDataEngine()
    jobs = engine.fetch_jobs(query="software engineer", location="Mumbai, India", limit=1) # jobs is a list of JobPosting objects
