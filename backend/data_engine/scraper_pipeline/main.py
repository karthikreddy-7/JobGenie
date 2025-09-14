import json
import os
import logging
from datetime import datetime
from typing import Dict, List

import pandas as pd

from scrapers.indeed_scraper import IndeedScraper
from pipeline.fetcher import fetch_jobs
from pipeline.transformer import transform_jobs
from pipeline.loader import save_to_csv
from schemas.job import JobPosting
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
    SEARCH_TERM = "Software Engineer"
    # Set to a specific location name from locations.json (e.g., "New York")
    # or set to None to run for all locations.
    LOCATION = None
    JOBS_TO_SCRAPE = config.DEFAULT_JOBS_TO_SCRAPE
    HOURS_OLD = config.DEFAULT_HOURS_OLD
    # -----------------------------

    locations = load_locations(config.LOCATIONS_CONFIG_PATH)
    if not locations:
        return

    # Determine which locations to process
    if LOCATION:
        if LOCATION not in locations:
            logging.error(f"Error: Location '{LOCATION}' not found in locations.json")
            return
        locations_to_process = {LOCATION: locations[LOCATION]}
    else:
        logging.info("No specific location provided. Running for all locations...")
        locations_to_process = locations

    # Initialize scrapers
    scrapers = [IndeedScraper()]
    all_job_postings: List[JobPosting] = []

    # Main processing loop
    for common_name, location_map in locations_to_process.items():
        logging.info(f"--- Processing location: {common_name} ---")

        # 1. Fetch
        raw_jobs_df = fetch_jobs(
            scrapers=scrapers,
            search_term=SEARCH_TERM,
            location_map=location_map,
            jobs=JOBS_TO_SCRAPE,
            hours_old=HOURS_OLD
        )
        if raw_jobs_df.empty:
            logging.warning(f"No jobs found for '{SEARCH_TERM}' in '{common_name}'.")
            continue

        # 2. Transform
        logging.info(f"Transforming {len(raw_jobs_df)} raw job listings for {common_name}...")
        job_postings = transform_jobs(raw_jobs_df)
        all_job_postings.extend(job_postings)

    # 3. Load
    if not all_job_postings:
        logging.info("Pipeline finished, but no job postings were found across all locations.")
        return

    logging.info(f"Aggregated a total of {len(all_job_postings)} job postings.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"job_postings_{timestamp}.csv"

    save_to_csv(all_job_postings, output_filename)
    logging.info("--- Pipeline finished successfully. ---")


if __name__ == "__main__":
    main()

