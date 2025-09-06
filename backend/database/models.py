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

    job_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    link = Column(Text, nullable=False)
    source = Column(String, default="LinkedIn")

    applications = relationship("Application", back_populates="job")


# --- Users Table ---
class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    resume = Column(JSON, nullable=False)   # Store Resume schema as JSONB
    preferences = Column(JSON, nullable=True)  # UserPreferences
    linkedin = Column(JSON, nullable=True)     # LinkedInCredentials
    user_automation_settings = Column(JSON, nullable=True)  # Automation Settings

    applications = relationship("Application", back_populates="user")


# --- Applications Table ---
class Application(Base):
    __tablename__ = "applications"

    application_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.job_id", ondelete="CASCADE"))
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"))

    status = Column(Enum(ApplicationStatusEnum), nullable=False)
    status_reason = Column(Text, nullable=True)
    applied_on = Column(DateTime, default=datetime.utcnow)
    referral_sent = Column(Integer, default=0)
    referral_accepted = Column(Integer, default=0)

    # Relationships
    job = relationship("Job", back_populates="applications")
    user = relationship("User", back_populates="applications")
