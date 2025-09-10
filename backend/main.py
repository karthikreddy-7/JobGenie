from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
import uvicorn
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler

from database.models import User, Job
from schemas.user import UserProfile
from schemas.job import JobPosting
from database.setup_db import get_db
from sqlalchemy.orm import Session
import logging

app = FastAPI()

logger = logging.getLogger(__name__)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the validation errors in detail
    logger.error(f"Validation error for request {request.url}: {exc.errors()}")
    logger.error(f"Request body: {await request.body()}")
    # Reuse FastAPI’s default response
    return await request_validation_exception_handler(request, exc)

@app.post("/users/", response_model=UserProfile)
def create_user(user: UserProfile, db: Session = Depends(get_db)):
    db_user = User(
        user_id=user.user_id,
        resume=user.resume.model_dump(),
        preferences=user.preferences.model_dump() if user.preferences else None,
        linkedin=user.linkedin.model_dump() if user.linkedin else None,
        user_automation_settings=user.user_automation_settings.model_dump() if user.user_automation_settings else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user

@app.get("/users/{user_id}", response_model=UserProfile)
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(
        user_id=db_user.user_id,
        resume=db_user.resume,
        preferences=db_user.preferences,
        linkedin=db_user.linkedin,
        user_automation_settings=db_user.user_automation_settings
    )

@app.get("/jobs/", response_model=List[JobPosting])
def read_jobs(q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Job)
    if q:
        query = query.filter(Job.title.ilike(f"%{q}%"))
    jobs = query.all()
    return [JobPosting(
        id=job.job_id,
        site=job.site,
        job_url=job.job_url,
        job_url_direct=job.job_url_direct,
        title=job.title,
        company=job.company,
        location=job.location,
        date_posted=job.date_posted,
        job_level=job.job_level,
        description=job.description,
        company_industry=job.company_industry,
        company_url=job.company_url
    ) for job in jobs]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
