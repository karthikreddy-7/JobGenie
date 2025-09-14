# pipeline/loader.py
import logging
from typing import List, Set

import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from backend.data_engine.pipeline.experience_extractor import extract_experience
from backend.data_engine.pipeline.filter import should_save_job
from backend.database.models import Job, SeenJob
from backend.database.setup_db import get_db
from backend.schemas.job import JobPosting


def get_seen_job_ids(db) -> Set[str]:
    """Fetches all existing job IDs from the seen_jobs table."""
    logging.info("Fetching seen job IDs from the database...")
    seen_job_ids = db.query(SeenJob.job_id).all()
    ids = {id[0] for id in seen_job_ids}
    logging.info(f"Found {len(ids)} seen job IDs.")
    return ids


def add_seen_jobs(db, new_jobs_df: pd.DataFrame):
    """Adds new job IDs to the seen_jobs table."""
    if new_jobs_df.empty:
        return

    # The scraped dataframe is expected to have 'id' and 'site' columns.
    # 'id' from the scraper is the external job_id.
    jobs_to_insert = new_jobs_df[['id', 'site']].rename(
        columns={'id': 'job_id', 'site': 'source'}
    ).to_dict(orient='records')

    if not jobs_to_insert:
        return

    logging.info(f"Adding {len(jobs_to_insert)} new job IDs to the seen_jobs table.")

    stmt = insert(SeenJob).values(jobs_to_insert)
    stmt = stmt.on_conflict_do_nothing(index_elements=['job_id'])
    db.execute(stmt)
    db.commit()


def load_jobs_to_db(job_postings: List[JobPosting], db):
    """
    Processes a list of job postings, filters them based on experience,
    and loads them into the database.
    """
    if not job_postings:
        logging.info("No job postings to load.")
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
                min_exp_required=experience
            )
            db.add(job)
            saved_count += 1

    db.commit()
    logging.info(f"Successfully saved {saved_count} job postings to the database.")
