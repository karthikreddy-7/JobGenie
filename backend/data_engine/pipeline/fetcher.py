# pipeline/fetcher.py
import logging
import pandas as pd
from typing import List, Set

from backend.data_engine.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

def fetch_jobs(scrapers: List[BaseScraper], search_term: str, location_map: dict, jobs: int = 1, hours_old: int = 6, seen_job_ids: Set[str] = None) -> pd.DataFrame:
    """Fetches jobs from a list of scrapers and merges the results."""
    all_jobs = []
    logger.info(f"Fetching jobs for search term: '{search_term}'")
    for scraper in scrapers:
        site_location = location_map.get(scraper.site_name.lower())
        if not site_location:
            logger.warning(f"No location mapping found for {scraper.site_name}. Skipping.")
            continue
        
        logger.info(f"Fetching jobs from {scraper.site_name} for '{search_term}' in '{site_location}'...")
        try:
            df = scraper.scrape(search_term, site_location, jobs, hours_old)
            if not df.empty:
                logger.info(f"Successfully fetched {len(df)} jobs from {scraper.site_name}.")
                all_jobs.append(df)
            else:
                logger.info(f"No jobs found from {scraper.site_name}.")
        except Exception as e:
            logger.error(f"Error fetching from {scraper.site_name}: {e}", exc_info=True)

    if not all_jobs:
        logger.info("No jobs found from any scraper.")
        return pd.DataFrame()

    merged_df = pd.concat(all_jobs, ignore_index=True)
    logger.info(f"Successfully fetched a total of {len(merged_df)} jobs from all scrapers.")

    if seen_job_ids:
        original_count = len(merged_df)
        merged_df = merged_df[~merged_df['id'].isin(seen_job_ids)]
        new_count = len(merged_df)
        if original_count > new_count:
            logger.info(f"Filtered out {original_count - new_count} already seen jobs.")

    return merged_df
