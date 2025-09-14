# scrapers/indeed_scraper.py
from .base_scraper import BaseScraper
from jobspy import scrape_jobs
import pandas as pd

class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__("Indeed")

    def scrape(self, search_term: str, location: str, jobs: int = 1,hours_old:int=6) -> pd.DataFrame:
        try:
            df = scrape_jobs(
                site_name=["indeed"],
                search_term=search_term,
                location=location,
                results_wanted=jobs,
                hours_old = hours_old
            )
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            print(f"Error scraping Indeed: {e}")
            return pd.DataFrame()
