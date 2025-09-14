# models.py
from sqlalchemy import (
    create_engine, Column, String, Integer, Text, DateTime, Enum, JSON, Boolean, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
import enum
from datetime import datetime

Base = declarative_base()


# --- Enum for Application Status ---
class ApplicationStatusEnum(enum.Enum):
    RESUME_PREPARED = "resume_prepared"
    REFERRAL_REQUESTED = "referral_requested"
    NO_REFERRAL_RESPONSE = "no_referral_response"
    AUTO_APPLIED = "auto_applied"
    REJECTED = "rejected"


# --- Jobs Table ---
class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, index=True)  # id
    site = Column(String, nullable=False)                  # site
    job_url = Column(Text, nullable=False)                 # job_url
    job_url_direct = Column(Text, nullable=True)           # job_url_direct
    title = Column(String, nullable=False)                 # title
    company = Column(String, nullable=False)               # company
    location = Column(String, nullable=True)               # location
    date_posted = Column(String, nullable=True)            # date_posted
    job_level = Column(String, nullable=True)              # job_level
    description = Column(Text, nullable=False)             # description
    company_industry = Column(String, nullable=True)       # company_industry
    company_url = Column(Text, nullable=True)              # company_url
    created_at = Column(DateTime, default=datetime.utcnow())
    min_exp_required = Column(Integer,nullable=True)


# --- Users Table ---
class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    resume = Column(JSON, nullable=False)   # Store Resume schema as JSONB
    preferences = Column(JSON, nullable=True)  # UserPreferences
    linkedin = Column(JSON, nullable=True)     # LinkedInCredentials
    user_automation_settings = Column(JSON, nullable=True)  # Automation Settings

# --- UserJobMatch Table ---
class UserJobMatch(Base):
    __tablename__ = "user_job_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.job_id"), nullable=False)
    fit = Column(String, nullable=False)  # 'yes' or 'no'
    reasons = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow())

    user = relationship("User")
    job = relationship("Job")
