# schemas/user.py
from pydantic import BaseModel
from typing import List, Optional

class UserPreferences(BaseModel):
    """Schema for user’s personalized job preferences."""
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_companies: Optional[List[str]] = None
    avoid_companies: Optional[List[str]] = None
    remote_only: bool = False
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    keywords: Optional[List[str]] = None   # must-have words in job description
    blacklist_keywords: Optional[List[str]] = None  # reject jobs containing these

class UserAutomationSettings(BaseModel):
    auto_apply: bool = False
    referral_enabled: bool = True
    referral_threshold: float = 0.8  # min match score to request referral
    connection_threshold: int = 50  # min connections at company to request referral
    max_applications_per_day: int = 5

class LinkedInCredentials(BaseModel):
    """Schema for storing LinkedIn authentication details."""
    username: str
    password: str
    auth_token: Optional[str] = None   # session cookie / CSRF token if needed

class Header(BaseModel):
  full_name: str
  location: str
  phone: str
  email: str
  linkedin: str
  github: str
  portfolio: str

class EducationEntry(BaseModel):
  id: str
  institution: str
  degree: str
  city: str
  start_date: str
  end_date: str
  gpa: str
  coursework: str

class ExperienceEntry(BaseModel):
  id: str
  company: str
  role: str
  city: str
  start_date: str
  end_date: str
  bullets: List[str]

class ProjectEntry(BaseModel):
  id: str
  title: str
  date: str
  technologies: str
  link: str
  description_bullets: List[str]

class Skills(BaseModel):
  programming_languages: List[str]
  frameworks_tools: List[str]
  other: List[str]

class CertificationEntry(BaseModel):
  id: str
  title: str
  issuer: str
  date: str

class Resume(BaseModel):
  header: Header
  summary: Optional[str] = None
  education: List[EducationEntry]
  experience: List[ExperienceEntry]
  projects: List[ProjectEntry]
  skills: Skills
  certifications: List[CertificationEntry]

class UserProfile(BaseModel):
    user_id: str
    resume: Resume
    preferences: Optional[UserPreferences] = None
    linkedin: Optional[LinkedInCredentials] = None
    user_automation_settings: Optional[UserAutomationSettings] = None
