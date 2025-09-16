
import json
import logging
from typing import Dict, List

from sqlalchemy.orm import Session

from backend.data_engine import config as data_engine_config
from backend.data_engine.pipeline.fetcher import fetch_jobs
from backend.data_engine.pipeline.loader import add_seen_jobs, get_seen_job_ids, load_jobs_to_db
from backend.data_engine.pipeline.transformer import transform_jobs
from backend.data_engine.scrapers.indeed_scraper import IndeedScraper

logger = logging.getLogger(__name__)


def load_locations(config_path: str) -> Dict:
    """Loads the locations configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {config_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from: {config_path}")
        return {}


def run_job_scraping(
    db: Session,
    search_terms: List[str],
    locations_to_search: List[str],
    jobs_to_scrape: int,
    hours_old: int,
):
    """Orchestrates the job scraping pipeline based on user preferences."""
    logger.info("--- Starting Job Scraping ---")

    all_locations = load_locations(data_engine_config.LOCATIONS_CONFIG_PATH)
    if not all_locations:
        return

    locations_to_process = {}
    for loc in locations_to_search:
        if loc in all_locations:
            locations_to_process[loc] = all_locations[loc]
        else:
            logger.warning(f"Location '{loc}' not found in locations.json and will be skipped.")

    if not locations_to_process:
        logger.error("None of the specified locations were valid. Exiting scraping.")
        return

    scrapers = [IndeedScraper()]
    seen_job_ids = get_seen_job_ids(db)

    for search_term in search_terms:
        logger.info(f"=== Processing search term: '{search_term}' ===")
        for common_name, location_map in locations_to_process.items():
            logger.info(f"--- Processing location: {common_name} ---")

            raw_jobs_df = fetch_jobs(
                scrapers=scrapers,
                search_term=search_term,
                location_map=location_map,
                jobs=jobs_to_scrape,
                hours_old=hours_old,
                seen_job_ids=seen_job_ids,
            )
            if raw_jobs_df.empty:
                logger.warning(f"No new jobs found for '{search_term}' in '{common_name}'.")
                continue

            add_seen_jobs(db, raw_jobs_df)
            job_postings = transform_jobs(raw_jobs_df, common_name)

            if not job_postings:
                logger.info("No job postings were found after transformation.")
                continue

            load_jobs_to_db(job_postings, db)
    logger.info("--- Job Scraping Finished ---")
