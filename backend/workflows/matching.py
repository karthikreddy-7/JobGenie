
import logging
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.database import models
from backend.matching_engine.semanticMatcher import LLMMatcher
from backend.schemas.user import UserProfile, Resume

logger = logging.getLogger(__name__)


def run_job_matching(db: Session, user: models.User):
    """Fetches jobs and a user profile, runs the matching engine, and saves the results."""
    logger.info(f"--- Starting Job Matching for user: {user.user_id} ---")

    try:
        user_profile = UserProfile(
            user_id=user.user_id,
            resume=Resume(**user.resume),
            preferences=user.preferences,
            linkedin=user.linkedin,
            user_automation_settings=user.user_automation_settings,
        )
    except Exception as e:
        logger.error(f"Failed to parse user profile for {user.user_id}: {e}")
        return

    max_exp = user.preferences.get("max_experience")
    if max_exp is None:
        logger.warning(f"User {user.user_id} does not have 'max_experience' set. Cannot run matching.")
        return

    preferred_locations = user.preferences.get("preferred_locations")
    if not preferred_locations:
        logger.warning(f"User {user.user_id} does not have 'preferred_locations' set. Cannot run matching.")
        return

    query = db.query(models.Job).filter(models.Job.min_exp_required <= max_exp)

    # Add location filter using ILIKE for partial matching
    location_filters = [models.Job.location.ilike(f"%{loc}%") for loc in preferred_locations]
    query = query.filter(or_(*location_filters))

    jobs_to_match = query.all()

    if not jobs_to_match:
        logger.info(f"No jobs found matching experience <= {max_exp} and locations: {preferred_locations}.")
        return

    logger.info(f"Found {len(jobs_to_match)} jobs to match against for user {user.user_id}.")

    matcher = LLMMatcher()
    match_count = 0

    for job_record in jobs_to_match:
        try:
            match_result = matcher.match(job=job_record, user=user_profile)
            existing_match = (
                db.query(models.UserJobMatch)
                .filter(
                    models.UserJobMatch.user_id == user.user_id,
                    models.UserJobMatch.job_id == job_record.job_id,
                )
                .first()
            )
            if existing_match:
                existing_match.fit = match_result["fit"]
                existing_match.reasons = " ".join(match_result["reasons"])
                existing_match.score = match_result["score"]
                existing_match.created_at = datetime.utcnow()
            else:
                new_match = models.UserJobMatch(
                    user_id=user.user_id,
                    job_id=job_record.job_id,
                    fit=match_result["fit"],
                    reasons=" ".join(match_result["reasons"]),
                    score=match_result["score"],
                    status="READY_FOR_EMAIL",
                )
                db.add(new_match)
            match_count += 1
        except Exception as e:
            logger.error(f"Failed to match job {job_record.job_id} for user {user.user_id}: {e}")
            continue

    if match_count > 0:
        db.commit()
        logger.info(f"Processed {match_count} matches for user {user.user_id}.")
    else:
        logger.info(f"No new matches processed for user {user.user_id}.")

    logger.info(f"--- Job Matching Finished for user: {user.user_id} ---")
