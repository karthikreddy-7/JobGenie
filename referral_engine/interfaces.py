from abc import ABC, abstractmethod
from typing import List
from schemas.job import JobPosting
from schemas.user import UserProfile

class ReferralEngine(ABC):
    """Abstract interface for handling referrals & networking."""

    @abstractmethod
    def send_connection_requests(self, job: JobPosting, user: UserProfile) -> int:
        """Send connection requests to company employees. Return count."""
        pass

    @abstractmethod
    def send_referral_messages(self, job: JobPosting, user: UserProfile) -> int:
        """Send referral messages to accepted connections. Return count."""
        pass
