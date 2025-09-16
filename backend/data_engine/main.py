import json
import logging
from datetime import datetime
from typing import Dict, List

import pandas as pd

from backend.database.setup_db import get_db
from backend.schemas.job import JobPosting
from scrapers.indeed_scraper import IndeedScraper
from pipeline.fetcher import fetch_jobs
from pipeline.transformer import transform_jobs
from pipeline.loader import load_jobs_to_db, get_seen_job_ids, add_seen_jobs
import config


def setup_logging():
    """Configures the logging format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_locations(config_path: str) -> Dict:
    """Loads the locations configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at: {config_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from: {config_path}")
        return {}


def main():
    """Main function to orchestrate the job scraping pipeline."""
    setup_logging()

    # --- Parameters to Configure ---
    SEARCH_TERMS = ["Software Engineer","Software Developer"]
    # Set to a list of location names (e.g., ["Hyderabad", "Bengaluru"]) or None to process all
    LOCATIONS = ["Hyderabad", "Bengaluru","Mumbai"]
    JOBS_TO_SCRAPE = config.DEFAULT_JOBS_TO_SCRAPE
    HOURS_OLD = config.DEFAULT_HOURS_OLD
    # -----------------------------

    locations = load_locations(config.LOCATIONS_CONFIG_PATH)
    if not locations:
        return

    # Determine which locations to process
    if LOCATIONS:
        locations_to_process = {}
        for loc in LOCATIONS:
            if loc in locations:
                locations_to_process[loc] = locations[loc]
            else:
                logging.warning(f"Location '{loc}' not found in locations.json and will be skipped.")

        if not locations_to_process:
            logging.error("None of the specified locations were valid. Exiting.")
            return
        logging.info(f"Processing for specified locations: {list(locations_to_process.keys())}")
    else:
        logging.info("No specific location provided. Running for all locations...")
        locations_to_process = locations

    # Initialize scrapers
    scrapers = [IndeedScraper()]

    # Get DB session and seen jobs
    db = next(get_db())
    seen_job_ids = get_seen_job_ids(db)

    # Loop over each search term
    for search_term in SEARCH_TERMS:
        logging.info(f"=== Processing search term: '{search_term}' ===")
        for common_name, location_map in locations_to_process.items():
            logging.info(f"--- Processing location: {common_name} ---")

            # 1. Fetch new jobs
            raw_jobs_df = fetch_jobs(
                scrapers=scrapers,
                search_term=search_term,
                location_map=location_map,
                jobs=JOBS_TO_SCRAPE,
                hours_old=HOURS_OLD,
                seen_job_ids=seen_job_ids
            )
            if raw_jobs_df.empty:
                logging.warning(f"No new jobs found for '{search_term}' in '{common_name}'.")
                continue

            # 2. Add new jobs to seen_jobs table
            add_seen_jobs(db, raw_jobs_df)

            # 3. Transform
            logging.info(f"Transforming {len(raw_jobs_df)} raw job listings for {common_name}...")
            job_postings = transform_jobs(raw_jobs_df)

            # 4. Load / Save
            if not job_postings:
                logging.info("No job postings were found after transformation.")
                continue

            logging.info(f"Loading {len(job_postings)} job postings to the database for {common_name}...")
            load_jobs_to_db(job_postings, db)

    logging.info("--- Pipeline finished successfully. ---")


if __name__ == "__main__":
    main()