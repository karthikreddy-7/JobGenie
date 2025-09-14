# pipeline/fetcher.py
import pandas as pd
from typing import List
from ..scrapers.base_scraper import BaseScraper

def fetch_jobs(scrapers: List[BaseScraper], search_term: str, location_map: dict, jobs: int = 1,hours_old:int=6) -> pd.DataFrame:
    """Fetches jobs from a list of scrapers and merges the results."""
    all_jobs = []
    for scraper in scrapers:
        site_location = location_map.get(scraper.site_name.lower())
        if not site_location:
            print(f"Warning: No location mapping found for {scraper.site_name}. Skipping.")
            continue
        
        print(f"Fetching jobs from {scraper.site_name} for '{search_term}' in '{site_location}'...")
        try:
            df = scraper.scrape(search_term, site_location, jobs,hours_old)
            if not df.empty:
                all_jobs.append(df)
        except Exception as e:
            print(f"Error fetching from {scraper.site_name}: {e}")

    if not all_jobs:
        return pd.DataFrame()

    return pd.concat(all_jobs, ignore_index=True)
