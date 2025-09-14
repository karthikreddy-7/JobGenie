from sentence_transformers import SentenceTransformer, util
import logging
from typing import Dict

from backend.matching_engine.interfaces import MatchingEngine
from backend.schemas.job import JobPosting
from backend.schemas.user import UserProfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class LLMMatcher():
    def __init__(self):
        self.model = SentenceTransformer("/home/karthik/dev/models/JobBERT-v2")

    def _get_relevant_resume_text(self, resume) -> str:
        """
        Concatenate the most relevant parts of the resume for semantic matching.
        This avoids noise and ensures embeddings are focused.
        """
        parts = []

        if resume.summary:
            parts.append(resume.summary)

        if hasattr(resume, "experience"):
            for exp in resume.experience:
                parts.append(exp.role)
                parts.append(exp.company)
                parts.extend(exp.bullets or [])

        if hasattr(resume, "projects"):
            for proj in resume.projects:
                parts.append(proj.title)
                parts.extend(proj.description_bullets or [])

        if hasattr(resume, "skills") and resume.skills:
            # Add skills as a block of text for embedding
            all_skills = (
                resume.skills.programming_languages
                + resume.skills.frameworks_tools
                + resume.skills.other
            )
            parts.append("Skills: " + ", ".join(all_skills))

        # Filter out empty strings
        return "\n".join([str(p) for p in parts if p])

    def match(self, job: JobPosting, user: UserProfile) -> Dict:
        """
        Match a job against a user profile using semantic similarity only.
        Removes brittle regex/skill matching logic.
        """
        job_desc = job.description or ""
        resume_text = self._get_relevant_resume_text(user.resume)

        if not job_desc.strip() or not resume_text.strip():
            logger.warning("Empty job description or resume text.")
            return {
                "fit": "No",
                "reasons": ["Insufficient data for matching."],
                "score": 0.0
            }

        # --- Semantic Similarity ---
        job_emb = self.model.encode(job_desc, convert_to_tensor=True)
        resume_emb = self.model.encode(resume_text, convert_to_tensor=True)
        semantic_score = float(util.pytorch_cos_sim(job_emb, resume_emb).item())

        # Normalize score to [0, 1]
        final_score = max(0.0, min(semantic_score, 1.0))

        # Decision threshold
        threshold = 0.6
        fit = "Yes" if final_score >= threshold else "No"

        # --- Reasons ---
        reasons = [f"Semantic similarity score: {semantic_score:.2f}."]
        if fit == "No":
            reasons.append(f"Score is below the threshold ({threshold}).")

        return {
            "fit": fit,
            "reasons": reasons,
            "score": round(final_score, 2)
        }

    def is_recommended(self, job: JobPosting, user: UserProfile) -> bool:
        result = self.match(job, user)
        return result["fit"] == "Yes" and result["score"] >= 0.6
