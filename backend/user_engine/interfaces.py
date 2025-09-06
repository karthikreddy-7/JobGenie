from abc import ABC, abstractmethod
from schemas.user import UserProfile

class UserEngine(ABC):
    """Abstract interface for user data operations."""

    @abstractmethod
    def insert_user_data(self, user_profile: UserProfile):
        """Inserts user profile data into the database."""
        pass
