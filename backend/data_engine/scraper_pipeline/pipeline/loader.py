# pipeline/loader.py
from typing import List

from backend.data_engine.scraper_pipeline.pipeline.experience_extractor import extract_experience
from backend.data_engine.scraper_pipeline.pipeline.filter import should_save_job
from backend.database.models import Job
from backend.database.setup_db import get_db
from backend.schemas.job import JobPosting


def load_jobs_to_db(job_postings: List[JobPosting]):
    """
    Processes a list of job postings, filters them based on experience,
    and loads them into the database.
    """
    if not job_postings:
        print("No job postings to load.")
        return

    db = next(get_db())
    saved_count = 0
    for posting in job_postings:
        experience = extract_experience(posting.description)

        if should_save_job(experience):
            existing_job = db.query(Job).filter(Job.job_url == posting.job_url).first()
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
                company_url=posting.company_url,
                # TODO: Add a new column 'experience_extracted' to the Job model
                # and uncomment the following line:
                # experience_extracted=experience
            )
            db.add(job)
            saved_count += 1

    db.commit()
    print(f"Successfully saved {saved_count} job postings to the database.")
