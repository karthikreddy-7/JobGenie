from abc import ABC, abstractmethod
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Abstract base class for all job scrapers."""

    def __init__(self, site_name: str):
        self.site_name = site_name

    @abstractmethod
    def scrape(self, search_term: str, location: str, jobs: int, hours_old: int) -> pd.DataFrame:
        """Scrapes job data from the specific site."""
        logger.info(f"Scraping {self.site_name} for {jobs} jobs with search term '{search_term}' in '{location}'.")
        pass