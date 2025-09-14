import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from LinkedInScraper.job_fetcher import JobFetcher
from helper.constants import SMTP_HOST_KEY, SMTP_PORT_KEY, SMTP_USER_KEY, SMTP_PASS_KEY, RECIPIENT_EMAIL_KEY, DEFAULT_SMTP_HOST, DEFAULT_SMTP_PORT
import logging
from dotenv import load_dotenv
import html


load_dotenv()

# Email config (replace with env vars or config in production)
SMTP_HOST = os.getenv(SMTP_HOST_KEY, DEFAULT_SMTP_HOST)
SMTP_PORT = int(os.getenv(SMTP_PORT_KEY, DEFAULT_SMTP_PORT))
SMTP_USER = os.getenv(SMTP_USER_KEY)   # required
SMTP_PASS = os.getenv(SMTP_PASS_KEY)   # required
RECIPIENT_EMAIL = os.getenv(RECIPIENT_EMAIL_KEY)

# Job search config
SEARCH_TERM = "Senior Sales Executive"
LOCATION = "Mumbai"
RESULTS_WANTED = 300

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def format_jobs_for_email(jobs):
    """
    Format a list of JobPosting objects for email body.
    """
    if not jobs:
        return "No jobs found."
    lines = [
        f"{job.title} at {job.company} ({job.location})\n{job.job_url}\n" for job in jobs
    ]
    return "\n".join(lines)


def format_jobs_for_html(jobs, search_term, location):
    """
    Format a list of JobPosting objects as an HTML table for email body.
    Includes search term and location in the header.
    """
    header = f"<h2>Job Results for '<b>{html.escape(search_term)}</b>' in '<b>{html.escape(location)}</b>'</h2>"
    if not jobs:
        return header + "<p>No jobs found.</p>"
    table = [
        "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse:collapse;'>",
        "<tr><th>Title</th><th>Company</th><th>Date Posted</th><th>Job URL</th></tr>"
    ]
    for job in jobs:
        table.append(
            f"<tr>"
            f"<td>{html.escape(job.title)}</td>"
            f"<td>{html.escape(job.company)}</td>"
            f"<td>{html.escape(job.date_posted)}</td>"
            f"<td><a href='{html.escape(job.job_url)}'>Link</a></td>"
            f"</tr>"
        )
    table.append("</table>")
    return header + "\n" + "\n".join(table)


def send_email(subject: str, body: str, to_email: str):
    """
    Send an email with the given subject and HTML body to to_email.
    """
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


def main():
    logger.info(f"Fetching jobs for '{SEARCH_TERM}' in '{LOCATION}'...")
    fetcher = JobFetcher(default_site=["indeed"])
    jobs_df = fetcher.fetch_jobs(
        search_term=SEARCH_TERM,
        location=LOCATION,
        results_wanted=RESULTS_WANTED,
        hours_old=300,
        country_indeed="India"
    )
    jobs_list = fetcher.format_jobs(jobs_df)
    logger.info(f"Fetched {len(jobs_list)} jobs.")
    confirm = input(f"Found {len(jobs_list)}, Confirm to send email (Y/N): ")
    if confirm=='Y':
        email_body = format_jobs_for_html(jobs_list, SEARCH_TERM, LOCATION)
        send_email(
            subject=f"JobGenie Results: {SEARCH_TERM} in {LOCATION}",
            body=email_body,
            to_email=RECIPIENT_EMAIL
        )
    else:
        logger.info("No Jobs were fetched")

if __name__ == "__main__":
    main()
