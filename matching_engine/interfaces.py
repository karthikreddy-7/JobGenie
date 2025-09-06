from abc import ABC, abstractmethod
from typing import List
from schemas.job import JobPosting
from schemas.user import UserProfile

class MatchingEngine(ABC):
    """Abstract interface for job-user matching."""

    @abstractmethod
    def find_pros_and_cons(self, job: JobPosting, user: UserProfile) -> float: #returns an object containing pros and cons
        """Return returns an object containing pros and cons"""
        pass

    @abstractmethod
    def is_recommended(self, job: JobPosting, user: UserProfile) -> bool: 
        """Return a bool which indicates if user is recommended to apply at given job or not"""
        pass
