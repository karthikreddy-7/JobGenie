import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from LinkedInScraper.karthik.job_fetcher import JobFetcher
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
SEARCH_TERMS = [
    "Entry Level Data Analyst",
    "Entry Level Data Scientist",
    "Entry Level Data Engineer"
]
LOCATIONS = [
    "Austin, TX",
    "Arizona",
    "Texas",
    "North Carolina",
    "Washington, DC",
    "Florida"
]
RESULTS_WANTED = 500

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
    email_sections = []
    for search_term in SEARCH_TERMS:
        for location in LOCATIONS:
            logger.info(f"Fetching jobs for '{search_term}' in '{location}'...")
            fetcher = JobFetcher(default_site=["indeed"])
            jobs_df = fetcher.fetch_jobs(
                search_term=search_term,
                location=location,
                results_wanted=RESULTS_WANTED,
                hours_old=100
            )
            jobs_list = fetcher.format_jobs(jobs_df)
            logger.info(f"Fetched {len(jobs_list)} jobs for '{search_term}' in '{location}'.")
            section_html = format_jobs_for_html(jobs_list, search_term, location)
            email_sections.append(section_html)
    total_jobs = sum([section.count('<tr>')-1 for section in email_sections])  # -1 for header row
    confirm = input(f"Found {total_jobs} jobs in total, Confirm to send email (Y/N): ")
    if confirm == 'Y':
        email_body = "<br><br>".join(email_sections)
        send_email(
            subject=f"JobGenie Results: Multiple Searches",
            body=email_body,
            to_email=RECIPIENT_EMAIL
        )
    else:
        logger.info("No Jobs were fetched")

if __name__ == "__main__":
    main()

locations = [
    {"city": "New York City", "country": "United States"},
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
]