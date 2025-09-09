from database.setup_db import SessionLocal
from database.models import Job, User
from schemas.job import JobPosting
from schemas.user import UserProfile, Resume
from matching_engine.semanticMatcher import LLMMatcher
import json

# Create a session
session = SessionLocal()

# Query all jobs and users
jobs = session.query(Job).all()
users = session.query(User).all()

matcher = LLMMatcher()

for user in users:
    print(f"\n👤 User: {user.user_id}")
    results = []

    # Parse resume JSON from DB into Resume object
    try:
        resume_obj = Resume(**json.loads(user.resume))
    except Exception as e:
        print(f"❌ Failed to parse resume for user {user.user_id}: {e}")
        continue

    # Build UserProfile with parsed resume
    user_profile = UserProfile(
        user_id=user.user_id,
        resume=resume_obj,
        preferences=None,
        linkedin=None,
        user_automation_settings=None
    )

    for job in jobs[:50]:
        print(f"⚙️  Checking Job: {job.title}")
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

        match_result = matcher.match(job_posting, user_profile)
        score = match_result.get("score", 0.0)
        results.append((job.title, score, match_result))

    # Sort by LLM score
    results.sort(key=lambda x: x[1], reverse=True)

    # Print results
    for job_title, score, details in results:
        print(f"\n💼 Job: {job_title}")
        print(f"   ✅ Fit: {details.get('fit', 'No')}")
        print(f"   📊 Score: {score:.4f}")
        print("   📌 Reasons:")
        for r in details.get("reasons", []):
            print(f"      - {r}")

session.close()
