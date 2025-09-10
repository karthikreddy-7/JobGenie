import json
import logging
import time
from database.setup_db import SessionLocal
from database.models import Job, User
from schemas.job import JobPosting
from schemas.user import UserProfile, Resume
from matching_engine.semanticMatcher import LLMMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def main():
    start_time = time.time()

    # Create a session
    session = SessionLocal()

    try:
        jobs = session.query(Job).all()
        users = session.query(User).all()
    except Exception as e:
        logger.error(f"Failed to query jobs or users from DB: {e}")
        return

    matcher = LLMMatcher()

    for user in users:
        user_start_time = time.time()
        logger.info(f"👤 Processing User: {user.user_id}")

        # Parse resume JSON from DB into Resume object
        try:
            resume_obj = Resume(**json.loads(user.resume))
        except Exception as e:
            logger.error(f"❌ Failed to parse resume for user {user.user_id}: {e}")
            continue

        user_profile = UserProfile(
            user_id=user.user_id,
            resume=resume_obj,
            preferences=None,
            linkedin=None,
            user_automation_settings=None
        )

        for job in jobs[:50]:
            job_start_time = time.time()
            logger.info(f"⚙️  Checking Job: {job.title}")
            job_posting = JobPosting(
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
            )

            try:
                match_result = matcher.match(job_posting, user_profile)
                score = match_result.get("score", 0.0)
                logger.info(f"💼 Job: {job.title}")
                logger.info(f"   ✅ Fit: {match_result.get('fit', 'No')}")
                logger.info(f"   📊 Score: {score:.4f}")
                logger.info("   📌 Reasons:")
                for r in match_result.get("reasons", []):
                    logger.info(f"      - {r}")
            except Exception as e:
                logger.error(f"Error matching job '{job.title}' for user '{user.user_id}': {e}")
                match_result = {"fit": "No", "score": 0.0, "reasons": ["Matching error"]}

            job_end_time = time.time()
            logger.info(f"⏱️ Time for this job: {job_end_time - job_start_time:.2f}s")

        user_end_time = time.time()
        logger.info(f"⏱️ Time for user {user.user_id}: {user_end_time - user_start_time:.2f}s")

    session.close()
    total_time = time.time() - start_time
    logger.info(f"✅ Job matching process completed in {total_time:.2f}s.")


if __name__ == "__main__":
    main()
