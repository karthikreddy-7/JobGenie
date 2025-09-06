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

class UserProfile(BaseModel):
    user_id: str
    resume: Resume
    preferences: Optional[UserPreferences] = None

export interface Header {
  fullName: string;
  location: string;
  phone: string;
  email: string;
  linkedin: string;
  github: string;
  portfolio: string;
}

export interface EducationEntry {
  id: string;
  institution: string;
  degree: string;
  city: string;
  startDate: string;
  endDate: string;
  gpa: string;
  coursework: string;
}

export interface ExperienceEntry {
  id: string;
  company: string;
  role: string;
  city: string;
  startDate: string;
  endDate: string;
  bullets: string[];
}

export interface ProjectEntry {
  id: string;
  title: string;
  date: string;
  technologies: string;
  link: string;
  descriptionBullets: string[];
}

export interface Skills {
  programmingLanguages: string[];
  frameworksTools: string[];
  other: string[];
}

export interface CertificationEntry {
  id: string;
  title: string;
  issuer: string;
  date: string;
}

export interface Resume {
  header: Header;
  summary: string | null;
  education: EducationEntry[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
  skills: Skills;
  certifications: CertificationEntry[];
}