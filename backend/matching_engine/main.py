from database.setup_db import SessionLocal
from database.models import Job, User
from schemas.job import JobPosting
from schemas.user import UserProfile
from matching_engine.semanticMatcher import LLMMatcher
import json

# Create a session
session = SessionLocal()

# Query all jobs and users
jobs = session.query(Job).all()
users = session.query(User).all()

matcher = LLMMatcher()

for user in users:
    print(f"\nUser: {user.user_id}")
    results = []

    for job in jobs:
        # Convert job DB model to JobPosting schema
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

        # Use the new matcher with breakdown
        match_result = matcher.match(job_posting, user)
        final_score = match_result["final_score"]

        results.append((job.title, final_score, match_result))

    # Sort by final score descending
    results.sort(key=lambda x: x[1], reverse=True)

    # Print sorted jobs with breakdown
    for job_title, score, details in results:
        print(f"  Job: {job_title} | Final Score: {score:.4f}")
        print(f"    Breakdown: exp={details['experience_score']:.4f}, "
              f"skills={details['skills_score']:.4f}, "
              f"projects={details['project_score']:.4f}, "
              f"edu={'✔' if details['education_match'] else '✘'}, "
              f"exp_req={'✔' if details['experience_requirement_met'] else '✘'}")

session.close()
