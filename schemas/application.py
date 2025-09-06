# schemas/application.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplicationStatus(str):
    RESUME_PREPARED = "resume_prepared"
    REFERRAL_REQUESTED = "referral_requested"
    NO_REFERRAL_RESPONSE = "no_referral_response"
    AUTO_APPLIED = "auto_applied"
    REJECTED = 'rejected'

class ApplicationRecord(BaseModel):
    job_id: str
    user_id: str
    status: ApplicationStatus
    status_reason: str
    applied_on: Optional[datetime] = None
    referral_sent: Optional[int] = 0
    referral_accepted: Optional[int] = 0
