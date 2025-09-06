from abc import ABC, abstractmethod
from schemas.job import JobPosting
from schemas.user import UserProfile

class ResumeEngine(ABC):
    """Abstract interface for resume generation."""

    @abstractmethod
    def generate_resume(self, job: JobPosting, user: UserProfile, output_path: str, pros_and_cons: str) -> str:
        """
        Generate a tailored resume for the given job & user.
        Return the file path (PDF/DOCX).
        """
        pass
