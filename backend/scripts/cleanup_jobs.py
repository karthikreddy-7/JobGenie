
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.database.models import Job, UserJobMatch
from backend.database.setup_db import SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def cleanup_old_jobs(db: Session, days_old: int):
    """
    Deletes jobs and their associated matches that are older than a specified number of days.

    WARNING: This is a destructive operation. It removes data that may still be valuable to users
    and can cause users to miss job opportunities if they do not run the matching pipeline daily.
    """
    logger.warning("Starting destructive cleanup process based on user request.")
    logger.info(f"--- Cleanup for jobs older than {days_old} days initiated. ---")

    # 1. Calculate the cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    logger.info(f"Cutoff date: Deleting all jobs created before {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} UTC.")

    # 2. Find old job IDs to be deleted
    old_jobs_query = db.query(Job.job_id).filter(Job.created_at < cutoff_date)
    old_job_ids = [item[0] for item in old_jobs_query.all()]

    if not old_job_ids:
        logger.info("No old jobs found to delete. Cleanup finished.")
        return

    logger.info(f"Found {len(old_job_ids)} jobs to delete.")

    # 3. Delete corresponding records from the user_job_match table first
    delete_matches_stmt = UserJobMatch.__table__.delete().where(UserJobMatch.job_id.in_(old_job_ids))
    deleted_matches_count = db.execute(delete_matches_stmt).rowcount
    logger.info(f"Deleted {deleted_matches_count} records from user_job_match table.")

    # 4. Delete the old jobs from the jobs table
    delete_jobs_stmt = Job.__table__.delete().where(Job.job_id.in_(old_job_ids))
    deleted_jobs_count = db.execute(delete_jobs_stmt).rowcount
    logger.info(f"Deleted {deleted_jobs_count} records from jobs table.")

    # 5. Commit the transaction
    db.commit()
    logger.info("--- Destructive cleanup process finished successfully. ---")


if __name__ == "__main__":
    db_session = None
    try:
        db_session = SessionLocal()
        # Per user request, this script will delete all jobs and associated matches older than 2 days.
        cleanup_old_jobs(db=db_session, days_old=2)
    except Exception as e:
        logger.error(f"An error occurred during the cleanup process: {e}", exc_info=True)
        if db_session:
            db_session.rollback()
    finally:
        if db_session:
            db_session.close()
