import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import User, Job, UserJobMatch
from LinkedInScraper.karthik.job_fetcher import JobFetcher
from matching_engine.semanticMatcher import LLMMatcher
from helper.constants import SMTP_USER_KEY, RECIPIENT_EMAIL_KEY
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import html
from dotenv import load_dotenv
from schemas.job import JobPosting
from schemas.user import UserProfile, Resume
import uuid
import logging
from helper.util import safe_str
from helper import constants as c

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database setup
DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Email config
SMTP_USER = os.getenv(SMTP_USER_KEY)
RECIPIENT_EMAIL = os.getenv(RECIPIENT_EMAIL_KEY)

# Location and roles arrays
locations = [
    {"city": "New York City", "country": "United States"}
]
"""
{"city": "San Francisco Bay Area", "country": "United States"},
{"city": "San Francisco", "country": "United States"},
{"city": "San Jose", "country": "United States"},
{"city": "Palo Alto", "country": "United States"},
{"city": "Seattle", "country": "United States"},
{"city": "Chicago", "country": "United States"},
{"city": "Houston", "country": "United States"},
{"city": "Los Angeles", "country": "United States"},
{"city": "Dallas–Fort Worth", "country": "United States"},
{"city": "Boston", "country": "United States"},
{"city": "Atlanta", "country": "United States"},
{"city": "Washington, D.C.", "country": "United States"},
{"city": "Arlington", "country": "United States"},
{"city": "Maryland suburbs", "country": "United States"},
{"city": "Austin", "country": "United States"},
{"city": "Raleigh–Durham", "country": "United States"},
{"city": "Nashville", "country": "United States"},
{"city": "Denver", "country": "United States"},
{"city": "Salt Lake City", "country": "United States"},
{"city": "Columbus", "country": "United States"},
{"city": "Pittsburgh", "country": "United States"},
{"city": "Orlando", "country": "United States"},
{"city": "Phoenix", "country": "United States"},
{"city": "Miami", "country": "United States"},
{"city": "Charlotte", "country": "United States"},
{"city": "San Diego", "country": "United States"},
{"city": "Minneapolis–St. Paul", "country": "United States"},
{"city": "Detroit", "country": "United States"},
{"city": "Philadelphia", "country": "United States"},
{"city": "Indianapolis", "country": "United States"},
{"city": "St. Louis", "country": "United States"},
{"city": "Kansas City", "country": "United States"},
{"city": "Cincinnati", "country": "United States"},
{"city": "Cleveland", "country": "United States"},
{"city": "Milwaukee", "country": "United States"},
{"city": "Tampa–St. Petersburg", "country": "United States"},
{"city": "Jacksonville", "country": "United States"},
{"city": "San Antonio", "country": "United States"},
{"city": "Portland", "country": "United States"},
{"city": "Baltimore", "country": "United States"},
{"city": "Las Vegas", "country": "United States"},
{"city": "Albany", "country": "United States"},
{"city": "Hartford", "country": "United States"},
{"city": "Providence", "country": "United States"},
{"city": "Richmond", "country": "United States"},
{"city": "Oklahoma City", "country": "United States"},
{"city": "Tulsa", "country": "United States"},
{"city": "New Orleans", "country": "United States"},
{"city": "Memphis", "country": "United States"},
{"city": "Louisville", "country": "United States"},
{"city": "Omaha", "country": "United States"},
{"city": "Des Moines", "country": "United States"},
{"city": "Boise", "country": "United States"},
{"city": "Birmingham", "country": "United States"},
{"city": "Albuquerque", "country": "United States"},
{"city": "Madison", "country": "United States"}
"""
roles = [
    "Data Analyst",
    "Data Scientist",
    "Data Engineer"
]

def fetch_and_match_jobs_for_users():
    matcher = LLMMatcher()
    users = session.query(User).all()
    logger.info(f"Fetched {len(users)} users from database.")
    for user in users:
        try:
            user_profile = UserProfile(
                user_id=user.user_id,
                resume=Resume(**user.resume),
                preferences=user.preferences,
                linkedin=user.linkedin,
                user_automation_settings=user.user_automation_settings
            )
        except Exception as e:
            logger.error(f"Error converting user '{user.user_id}' resume to Pydantic model: {e}")
            continue
        logger.info(f"Processing user: {user.user_id}")
        for loc in locations:
            for role in roles:
                logger.info(f"Fetching jobs for role '{role}' in location '{loc['city']}'")
                try:
                    fetcher = JobFetcher(default_site=["indeed"])
                    jobs_df = fetcher.fetch_jobs(
                        search_term=role,
                        location=loc["city"],
                        results_wanted=1,
                        hours_old=6
                    )
                except Exception as e:
                    logger.error(f"Error fetching jobs for role '{role}' in location '{loc['city']}': {e}")
                    continue
                job_postings = []
                new_jobs = []
                for _, row in jobs_df.iterrows():
                    job_id = str(row.get("id") or str(uuid.uuid4()))
                    job_posting = JobPosting(
                        id=safe_str(row.get(c.ID) or str(uuid.uuid4())),
                        site=safe_str(row.get(c.SITE)),
                        job_url=safe_str(row.get(c.JOB_URL)),
                        job_url_direct=safe_str(row.get(c.JOB_URL_DIRECT)),
                        title=safe_str(row.get(c.TITLE)),
                        company=safe_str(row.get(c.COMPANY)),
                        location=safe_str(row.get(c.LOCATION)),
                        date_posted=safe_str(row.get(c.DATE_POSTED)),
                        job_level=safe_str(row.get(c.JOB_LEVEL)),
                        description=safe_str(row.get(c.DESCRIPTION)),
                        company_industry=safe_str(row.get(c.COMPANY_INDUSTRY)),
                        company_url=safe_str(row.get(c.COMPANY_URL)),
                    )
                    job_postings.append(job_posting)
                    existing_job = session.query(Job).filter_by(job_id=job_id).first()
                    if not existing_job:
                        job = Job(
                            job_id=job_posting.id,
                            site=job_posting.site,
                            job_url=job_posting.job_url,
                            job_url_direct=job_posting.job_url_direct,
                            title=job_posting.title,
                            company=job_posting.company,
                            location=job_posting.location,
                            date_posted=job_posting.date_posted,
                            job_level=job_posting.job_level,
                            description=job_posting.description,
                            company_industry=job_posting.company_industry,
                            company_url=job_posting.company_url
                        )
                        session.add(job)
                        new_jobs.append(job_posting)
                        logger.info(f"Added new job to DB: {job_posting.title} at {job_posting.company} [{job_posting.id}]")
                    else:
                        logger.debug(f"Duplicate job skipped: {job_posting.title} at {job_posting.company} [{job_posting.id}]")
                try:
                    session.commit()
                    logger.info(f"Committed {len(new_jobs)} new jobs to DB for role '{role}' in location '{loc['city']}'")
                except Exception as e:
                    logger.error(f"Error committing jobs to DB: {e}")
                    session.rollback()
                # Only match new jobs
                for job in new_jobs:
                    try:
                        logger.info(f"Matching job '{job.title}' for user '{user.user_id}'")
                        match_result = matcher.match(job, user_profile)
                        fit = match_result.get("fit")
                        reasons = match_result.get("reasons")
                        score = match_result.get("score")
                        logger.info(f"Match result for job '{job.title}': fit={fit}, score={score}, reasons={reasons}")
                        if fit == "Yes":
                            user_job_match = UserJobMatch(
                                user_id=user.user_id,
                                job_id=job.id,
                                fit=fit,
                                reasons=", ".join(reasons) if reasons else None,
                                score=int(score * 100) if score is not None else None
                            )
                            session.add(user_job_match)
                            logger.info(f"Added user-job match for user '{user.user_id}' and job '{job.title}'")
                    except Exception as e:
                        logger.error(f"Error matching job '{job.title}' for user '{user.user_id}': {e}")
                try:
                    session.commit()
                    logger.info(f"Committed user-job matches for user '{user.user_id}'")
                except Exception as e:
                    logger.error(f"Error committing user-job matches: {e}")
                    session.rollback()

def format_matches_html(matches):
    logger.info(f"Formatting {len(matches)} matches into HTML table.")
    header = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse:collapse;'>"
    header += "<tr><th>Title</th><th>Company</th><th>Date Posted</th><th>Job URL</th><th>Score</th><th>Reasons</th></tr>"
    rows = []
    for match in matches:
        job = session.query(Job).filter_by(job_id=match.job_id).first()
        rows.append(
            f"<tr>"
            f"<td>{html.escape(job.title)}</td>"
            f"<td>{html.escape(job.company)}</td>"
            f"<td>{html.escape(job.date_posted or '')}</td>"
            f"<td><a href='{html.escape(job.job_url)}'>Link</a></td>"
            f"<td>{html.escape(str(match.score))}</td>"
            f"<td>{html.escape(match.reasons or '')}</td>"
            f"</tr>"
        )
    return header + "\n".join(rows) + "</table>"


def send_email(subject, body, to_email):
    logger.info(f"Sending email to {to_email} with subject '{subject}'")
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    try:
        with smtplib.SMTP("localhost") as server:
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")


def process_and_notify_users():
    users = session.query(User).all()
    logger.info(f"Processing notifications for {len(users)} users.")
    for user in users:
        matches = session.query(UserJobMatch).filter_by(user_id=user.user_id, fit="Yes").all()
        logger.info(f"User '{user.user_id}' has {len(matches)} matches.")
        if matches:
            html_table = format_matches_html(matches)
            send_email(
                subject="Your JobGenie Matches",
                body=html_table,
                to_email=RECIPIENT_EMAIL
            )
            logger.info(f"Notification sent to user '{user.user_id}'")
        else:
            logger.info(f"No matches to notify for user '{user.user_id}'")

if __name__ == "__main__":
    logger.info("Starting JobGenie cron job...")
    fetch_and_match_jobs_for_users()
    process_and_notify_users()
    logger.info("JobGenie cron job completed.")
