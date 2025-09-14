import enum

SITE_NAME = "linkedin"

# Job Posting Keys
ID = "id"
SITE = "site"
JOB_URL = "job_url"
JOB_URL_DIRECT = "job_url_direct"
TITLE = "title"
COMPANY = "company"
LOCATION = "location"
DATE_POSTED = "date_posted"
JOB_LEVEL = "job_level"
DESCRIPTION = "description"
COMPANY_INDUSTRY = "company_industry"
COMPANY_URL = "company_url"

# Email config keys
SMTP_HOST_KEY = "SMTP_HOST"
SMTP_PORT_KEY = "SMTP_PORT"
SMTP_USER_KEY = "SMTP_USER"
SMTP_PASS_KEY = "SMTP_PASS"
RECIPIENT_EMAIL_KEY = "RECIPIENT_EMAIL"

# Default values
DEFAULT_SMTP_HOST = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587

class MatchStatus(enum.Enum):
    READY_FOR_EMAIL = "READY_FOR_EMAIL"
    EMAIL_SENT = "EMAIL_SENT"

