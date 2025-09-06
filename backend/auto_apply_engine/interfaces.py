from abc import ABC, abstractmethod
from backend.schemas.job import JobPosting
from backend.schemas.user import UserProfile

class AutoApplyEngine(ABC):
    """Abstract interface for auto-applying to job postings."""

    @abstractmethod
    def apply_to_job(self, job: JobPosting, user: UserProfile, resume_path: str) -> bool:
        """Auto-fill job application forms and submit. Return success/failure."""
        pass
