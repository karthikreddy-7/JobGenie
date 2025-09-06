from abc import ABC, abstractmethod
from typing import List
from backend.schemas.job import JobPosting
from backend.schemas.user import UserProfile

class FiltrationEngine(ABC):
    """Abstract interface for filtering job postings."""

    @abstractmethod
    def filter_jobs(self, jobs: List[JobPosting], user: UserProfile) -> List[JobPosting]:
        """Filter job postings based on user profile and preferences."""
        pass
