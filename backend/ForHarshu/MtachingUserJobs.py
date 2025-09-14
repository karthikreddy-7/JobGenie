import logging
from datetime import datetime

from sqlalchemy.orm import Session

from backend.database.setup_db import get_db
from backend.database.models import User, Job, UserJobMatch
from backend.matching_engine.semanticMatcher import LLMMatcher
from backend.schemas.user import UserProfile
from backend.schemas.job import JobPosting

def setup_logging():
    """Configures the logging format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def match_jobs_for_user(user_id: str, max_years_exp: int = 3):
    """Fetches jobs and a user profile, runs the matching engine, and saves the results."""
    setup_logging()
    logging.info(f"Starting job matching process for user: {user_id}, exp filter: <= {max_years_exp} years")
    db: Session = next(get_db())
    # 1. Get user
    user_record = db.query(User).filter(User.user_id == user_id).first()
    if not user_record:
        logging.error(f"User with id {user_id} not found.")
        return
    try:
        user_profile = UserProfile(**user_record.resume)
    except Exception as e:
        logging.error(f"Failed to parse user profile: {e}")
        return
    # 2. Get jobs with filter
    jobs_to_match = db.query(Job).filter(Job.min_exp_required <= max_years_exp).all()
    if not jobs_to_match:
        logging.info(f"No jobs found with min_exp_required <= {max_years_exp}.")
        return

    logging.info(f"Found {len(jobs_to_match)} jobs to match against.")

    matcher = LLMMatcher()
    match_count = 0

    for job_record in jobs_to_match:
        try:
            job_posting = JobPosting.from_orm(job_record)
            match_result = matcher.match(job=job_posting, user=user_profile)
            existing_match = (
                db.query(UserJobMatch)
                .filter_by(user_id=user_id, job_id=job_record.job_id)
                .first()
            )
            if existing_match:
                existing_match.fit = match_result["fit"]
                existing_match.reasons = " ".join(match_result["reasons"])
                existing_match.score = match_result["score"]
                existing_match.created_at = datetime.utcnow()
            else:
                new_match = UserJobMatch(
                    user_id=user_id,
                    job_id=job_record.job_id,
                    fit=match_result["fit"],
                    reasons=" ".join(match_result["reasons"]),
                    score=match_result["score"],
                    status="READY_FOR_EMAIL",
                )
                db.add(new_match)
            match_count += 1
        except Exception as e:
            logging.error(f"Failed to match job {job_record.job_id} for user {user_id}: {e}")
            continue
    if match_count > 0:
        db.commit()
        logging.info(f"Processed {match_count} matches for user {user_id}.")
    else:
        logging.info("No matches processed.")

    logging.info("Job matching process finished.")


if __name__ == "__main__":
    match_jobs_for_user("user_123", max_years_exp=5)