import os
import sys
import json
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from sqlalchemy.orm import Session

from backend.database import models
from backend.database.setup_db import SessionLocal
from backend.helper.constants import *
from html_generator import generate_jobs_html, wrap_html_body

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

import os
import logging


# Read from environment variables
SMTP_SERVER = os.getenv(SMTP_HOST_KEY, DEFAULT_SMTP_HOST)
SMTP_PORT = int(os.getenv(SMTP_PORT_KEY, DEFAULT_SMTP_PORT))
SMTP_USERNAME = os.getenv(SMTP_USER_KEY)
SMTP_PASSWORD = os.getenv(SMTP_PASS_KEY)
SENDER_EMAIL = SMTP_USERNAME
RECIPIENT_EMAIL = os.getenv(RECIPIENT_EMAIL_KEY)

def get_jobs_for_email(db_session: Session, user_id: str):
    """Fetch jobs for a user with 'READY_FOR_EMAIL' status and fit='Yes', sorted by score descending."""
    logger.info(f"Fetching jobs ready for email for user: {user_id}")
    matches = (
        db_session.query(models.UserJobMatch)
        .filter(models.UserJobMatch.user_id == user_id)
        .filter(models.UserJobMatch.status == "READY_FOR_EMAIL")
        .filter(models.UserJobMatch.fit == "Yes")  # Only recommended jobs
        .all()
    )

    jobs_to_send = []
    for match in matches:
        job = db_session.query(models.Job).filter(models.Job.job_id == match.job_id).first()
        if job:
            jobs_to_send.append({
                "job_id": job.job_id,
                "title": job.title,
                "company": job.company,
                "job_url": job.job_url,
                "job_url_direct": job.job_url_direct or job.job_url,
                "score": match.score,
                "fit": match.fit,
                "date_posted": job.date_posted if job.date_posted else "N/A",
                "min_exp_required": job.min_exp_required if job.min_exp_required is not None else "N/A",
                "match_reasons": match.reasons if match.reasons else "High Match",
                "location":job.location if job.location else "Not Available"
            })
        else:
            logger.warning(f"Job {match.job_id} not found for user {user_id}")

    # Sort by score descending
    jobs_to_send.sort(key=lambda x: x["score"], reverse=True)
    return jobs_to_send



def send_email(recipient_email: str, subject: str, html_content: str):
    """Send an HTML email."""
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL]):
        logger.error("SMTP configuration incomplete. Cannot send email.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return False


def update_job_match_status(db_session: Session, user_id: str, job_ids: list, new_status: str):
    """Update UserJobMatch statuses."""
    logger.info(f"Updating {len(job_ids)} job matches for user {user_id} to {new_status}")
    db_session.query(models.UserJobMatch) \
        .filter(models.UserJobMatch.user_id == user_id) \
        .filter(models.UserJobMatch.job_id.in_(job_ids)) \
        .update({"status": new_status}, synchronize_session=False)
    db_session.commit()
    logger.debug("Updated job match statuses successfully.")


def main(user_id: str, recipient_email: str):
    logger.info(f"Starting EmailSender for user: {user_id}")
    db_session = SessionLocal()
    try:
        jobs_to_send = get_jobs_for_email(db_session, user_id)
        if not jobs_to_send:
            logger.info("No jobs to send. Exiting.")
            return

        html_table = generate_jobs_html(jobs_to_send)
        full_html_content = wrap_html_body(html_table)
        subject = f"Job Recommendations for You - {datetime.now():%Y-%m-%d}"

        if send_email(recipient_email, subject, full_html_content):
            job_ids = [job["job_id"] for job in jobs_to_send]
            update_job_match_status(db_session, user_id, job_ids, "EMAIL_SENT")

    except Exception as e:
        logger.error(f"Error in EmailSender: {e}", exc_info=True)
    finally:
        db_session.close()
        logger.info(f"EmailSender finished for user: {user_id}")


if __name__ == "__main__":
    example_user_id = "harshithavalli6@gmail.com"  # Replace with actual user ID
    example_recipient_email = "harshithavalli6@gmail.com"
    main(example_user_id, example_recipient_email)
