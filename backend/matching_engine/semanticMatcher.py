from sentence_transformers import SentenceTransformer, util
import re
from matching_engine.interfaces import MatchingEngine
from schemas.job import JobPosting
from schemas.user import UserProfile
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class LLMMatcher(MatchingEngine):
    def __init__(self):
        self.model = SentenceTransformer('/home/karthik/dev/models/JobBERT-v2')

    def _extract_experience(self, text):
        """Extract required years of experience from job description or resume text."""
        # Look for patterns like '3+ years', '5 years', 'at least 2 years', etc.
        match = re.search(r'(\d+)\s*\+?\s*(?:years?|yrs?)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _get_resume_experience(self, resume_json):
        """Try to extract total years of experience from resume JSON."""
        # Try to find a field like 'total_experience', else parse work history
        if 'total_experience' in resume_json:
            return resume_json['total_experience']
        # Fallback: sum durations in work history if available
        years = 0
        if 'work_experience' in resume_json:
            for job in resume_json['work_experience']:
                if 'duration_years' in job:
                    years += job['duration_years']
        return years

    def _get_relevant_resume_text(self, resume):
        """Extract and concatenate relevant resume sections for semantic similarity."""
        parts = []
        # Summary
        if resume.summary:
            parts.append(resume.summary)
        # Experience
        for exp in resume.experience:
            parts.append(exp.role)
            parts.append(exp.company)
            parts.extend(exp.bullets)
        # Skills
        skills = resume.skills
        parts.extend(skills.programming_languages)
        parts.extend(skills.frameworks_tools)
        parts.extend(skills.other)
        # Projects
        for proj in resume.projects:
            parts.append(proj.title)
            parts.extend(proj.description_bullets)
        return '\n'.join([str(p) for p in parts if p])

    def match(self, job: JobPosting, user: UserProfile) -> dict:
        """Return sub-scores and final match score for a user-job pair using JobBERT-v2."""
        job_desc = job.description
        resume_json = user.resume.json()
        # Use only relevant resume sections for semantic similarity
        resume_text = self._get_relevant_resume_text(user.resume)

        required_exp = self._extract_experience(job_desc)
        candidate_exp = self._get_resume_experience(resume_json)

        reasons = []
        if required_exp > 0 and candidate_exp < required_exp:
            reasons.append(f"Required experience: {required_exp} years. Candidate has: {candidate_exp} years.")
            return {
                "fit": "No",
                "reasons": reasons,
                "score": 0.0
            }

        # Semantic similarity
        job_emb = self.model.encode(job_desc, convert_to_tensor=True)
        resume_emb = self.model.encode(resume_text, convert_to_tensor=True)
        score = float(util.pytorch_cos_sim(job_emb, resume_emb).item())

        fit = "Yes" if score >= 0.6 else "No"
        if fit == "No":
            reasons.append(f"Semantic match score below threshold: {score:.2f}")
        else:
            reasons.append(f"Semantic match score: {score:.2f}")
        return {
            "fit": fit,
            "reasons": reasons,
            "score": round(score, 2)
        }

    def find_pros_and_cons(self, job: JobPosting, user: UserProfile) -> float:
        # Optional: implement if needed
        pass

    def is_recommended(self, job: JobPosting, user: UserProfile) -> bool:
        result = self.match(job, user)
        return result["fit"] == "Yes" and result["score"] >= 0.6
