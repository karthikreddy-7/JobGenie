
import logging

from backend.database import models
from backend.database.setup_db import SessionLocal
from backend.data_engine import config as data_engine_config
from backend.workflows.scraping import run_job_scraping
from backend.workflows.matching import run_job_matching
from backend.workflows.emailing import run_email_sending

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def process_user_pipeline(user_id: str):
    """
    Runs the full pipeline for a single user:
    1. Scrapes new jobs based on user preferences.
    2. Matches the jobs against the user's profile.
    3. Emails the best matches to the user.
    """
    logger.info(f"===== Starting full pipeline for user: {user_id} =====")
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            logger.error(f"User with id {user_id} not found.")
            return

        if not user.preferences or not user.resume:
            logger.error(f"User {user_id} is missing preferences or resume. Skipping.")
            return

        # 1. Scrape jobs based on preferences
        preferred_roles = user.preferences.get("preferred_roles")
        preferred_locations = user.preferences.get("preferred_locations")

        if preferred_roles and preferred_locations:
            run_job_scraping(
                db=db,
                search_terms=preferred_roles,
                locations_to_search=preferred_locations,
                jobs_to_scrape=data_engine_config.DEFAULT_JOBS_TO_SCRAPE,
                hours_old=data_engine_config.DEFAULT_HOURS_OLD,
            )
        else:
            logger.warning(
                f"User {user_id} is missing preferred roles or locations. Skipping job scraping."
            )

        # 2. Match jobs to user
        run_job_matching(db=db, user=user)

        # 3. Send email with matched jobs
        run_email_sending(db=db, user=user)

    except Exception as e:
        logger.error(f"An unexpected error occurred during the pipeline for user {user_id}: {e}", exc_info=True)
    finally:
        db.close()
        logger.info(f"===== Finished full pipeline for user: {user_id} =====")


if __name__ == "__main__":
    # --- List of User IDs to process ---
    user_ids_to_process = [
        "harshithavalli6@gmail.com",
        # Add other user IDs here
    ]
    # -----------------------------------

    for user_id in user_ids_to_process:
        process_user_pipeline(user_id)
