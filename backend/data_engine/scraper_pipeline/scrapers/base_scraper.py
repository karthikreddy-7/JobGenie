# scrapers/base_scraper.py
from abc import ABC, abstractmethod
import pandas as pd

class BaseScraper(ABC):
    """Abstract base class for job scrapers."""

    def __init__(self, site_name: str):
        self.site_name = site_name

    @abstractmethod
    def scrape(self, search_term: str, location: str, jobs: int = 1,hours_old:int =6) -> pd.DataFrame:
        """Scrape job postings for a given search term and location."""
        pass
