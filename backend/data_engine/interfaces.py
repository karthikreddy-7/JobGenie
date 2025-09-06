from abc import ABC, abstractmethod
from typing import List
from backend.schemas.job import JobPosting

class DataEngine(ABC):
    """Abstract interface for job data sources (LinkedIn, Indeed, etc.)."""

    @abstractmethod
    def fetch_jobs(self, query: str, location: str, limit: int = 50) -> List[JobPosting]:
        """Fetch job postings from the data source."""
        pass
