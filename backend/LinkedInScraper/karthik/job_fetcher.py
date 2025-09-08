from typing import List, Optional, Dict, Any
import pandas as pd
from jobspy import scrape_jobs

from helper.util import safe_str
from schemas.job import JobPosting
from helper.constants import ID, SITE, JOB_URL, JOB_URL_DIRECT, TITLE, COMPANY, LOCATION, DATE_POSTED, JOB_LEVEL, DESCRIPTION, COMPANY_INDUSTRY, COMPANY_URL, SITE_NAME
import uuid

class JobFetcher:
    """
    Abstracted helper class for fetching jobs using JobSpy.
    Provides a clean, modular interface for backend usage.
    """
    def __init__(self, default_site: Optional[List[str]] = None):
        self.default_site = default_site or ["linkedin"]

    def fetch_jobs(
        self,
        search_term: str,
        location: str,
        results_wanted: int = 20,
        hours_old: Optional[int] = None,
        google_search_term: Optional[str] = None,
        job_type: Optional[str] = None,
        is_remote: Optional[bool] = None,
        linkedin_fetch_description: bool = False,
        proxies: Optional[List[str]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Fetch jobs from job boards using JobSpy.
        All heavy lifting and parameter handling is done here.
        """
        params = {
            "site_name": self.default_site,
            "search_term": search_term,
            "location": location,
            "results_wanted": results_wanted,
            "linkedin_fetch_description": linkedin_fetch_description,
        }
        if google_search_term:
            params["google_search_term"] = google_search_term
        if hours_old:
            params["hours_old"] = hours_old
        if job_type:
            params["job_type"] = job_type
        if is_remote is not None:
            params["is_remote"] = is_remote
        if proxies:
            params["proxies"] = proxies
        if extra_params:
            params.update(extra_params)
        try:
            jobs = scrape_jobs(**params)
            return jobs
        except Exception as e:
            # Log error, raise custom exception, or return empty DataFrame
            print(f"Error fetching jobs: {e}")
            return pd.DataFrame()

    @staticmethod
    def _map_to_job_posting(job: Dict[str, Any]) -> JobPosting:
        """
        Map a job dict from JobSpy to a JobPosting instance, handling missing fields and using constants for keys.
        Uses safe_str and generates a UUID if id is missing.
        """
        # Compose location from CITY and STATE if available
        location = safe_str(job.get("CITY"))
        if job.get("STATE"):
            location += ", " + safe_str(job.get("STATE"))
        return JobPosting(
            id=safe_str(job.get(ID) or job.get(JOB_URL) or str(uuid.uuid4())),
            site=safe_str(job.get(SITE) or job.get("SITE") or SITE_NAME),
            job_url=safe_str(job.get(JOB_URL)),
            job_url_direct=safe_str(job.get(JOB_URL_DIRECT) or job.get(JOB_URL)),
            title=safe_str(job.get(TITLE) or job.get("TITLE")),
            company=safe_str(job.get(COMPANY) or job.get("COMPANY")),
            location=location,
            date_posted=safe_str(job.get(DATE_POSTED) or job.get("date_posted")),
            job_level=safe_str(job.get(JOB_LEVEL) or job.get("job_level")),
            description=safe_str(job.get(DESCRIPTION) or job.get("DESCRIPTION")),
            company_industry=safe_str(job.get(COMPANY_INDUSTRY) or job.get("company_industry")),
            company_url=safe_str(job.get(COMPANY_URL) or job.get("company_url")),
        )

    @staticmethod
    def format_jobs(jobs: pd.DataFrame) -> List[JobPosting]:
        """
        Convert jobs DataFrame to list of JobPosting objects for API responses or further processing.
        """
        job_dicts = jobs.to_dict(orient="records")
        return [JobFetcher._map_to_job_posting(job) for job in job_dicts]

    @staticmethod
    def get_columns(jobs: pd.DataFrame) -> List[str]:
        """
        Get available columns from the jobs DataFrame.
        """
        return list(jobs.columns)

# Example usage for backend:

fetcher = JobFetcher(default_site=["indeed"])
jobs_df = fetcher.fetch_jobs(search_term="software engineer", location="San Francisco, CA", results_wanted=1)
jobs_list = fetcher.format_jobs(jobs_df)
columns = fetcher.get_columns(jobs_df)

print(jobs_list)
print(columns)

