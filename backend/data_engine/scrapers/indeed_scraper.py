# scrapers/indeed_scraper.py
import logging
from .base_scraper import BaseScraper
from jobspy import scrape_jobs
import pandas as pd

logger = logging.getLogger(__name__)

class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__("Indeed")

    def scrape(self, search_term: str, location: str, jobs: int = 1,hours_old:int=6) -> pd.DataFrame:
        logger.info(f"Scraping Indeed for '{search_term}' in '{location}'.")
        try:
            df = scrape_jobs(
                site_name=["indeed"],
                search_term=search_term,
                location=location,
                results_wanted=jobs,
                hours_old = hours_old
            )
            if df is not None and not df.empty:
                logger.info(f"Successfully scraped {len(df)} jobs from Indeed.")
            else:
                logger.info("No jobs found from Indeed.")
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}", exc_info=True)
            return pd.DataFrame()