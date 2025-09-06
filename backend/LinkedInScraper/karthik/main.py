from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["linkedin"],
    search_term="software engineer",
    google_search_term="software engineer jobs near San Francisco, CA since yesterday",
    location="Mumbai, India",
    results_wanted=1,
    hours_old=10,
    linkedin_fetch_description=True
)
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print(jobs.to_string()) # keeps headers + rows

for col in jobs.columns:
    print(col)



"""
Printing columns

id
site
job_url
job_url_direct
title
company
location
date_posted
job_type
salary_source
interval
min_amount
max_amount
currency
is_remote
job_level
job_function
listing_type
emails
description
company_industry
company_url
company_logo
company_url_direct
company_addresses
company_num_employees
company_revenue
company_description
skills
experience_range
company_rating
company_reviews_count
vacancy_count
work_from_home_type
"""