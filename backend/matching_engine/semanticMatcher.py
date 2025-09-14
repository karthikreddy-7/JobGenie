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
            logger.debug("Added resume summary to relevant text.")

        if hasattr(resume, "experience"):
            for exp in resume.experience:
                parts.append(exp.role)
                parts.append(exp.company)
                parts.extend(exp.bullets or [])
            logger.debug(f"Added {len(resume.experience)} experience entries to relevant text.")

        if hasattr(resume, "projects"):
            for proj in resume.projects:
                parts.append(proj.title)
                parts.extend(proj.description_bullets or [])
            logger.debug(f"Added {len(resume.projects)} project entries to relevant text.")

        if hasattr(resume, "skills") and resume.skills:
            # Add skills as a block of text for embedding
            all_skills = (
                resume.skills.programming_languages
                + resume.skills.frameworks_tools
                + resume.skills.other
            )
            parts.append("Skills: " + ", ".join(all_skills))
            logger.debug(f"Added {len(all_skills)} skills to relevant text.")

        # Filter out empty strings
        relevant_text = "\n".join([str(p) for p in parts if p])
        logger.debug(f"Constructed relevant resume text (length: {len(relevant_text)}).")
        return relevant_text

    def match(self, job: JobPosting, user: UserProfile) -> Dict:
        """
        Match a job against a user profile using semantic similarity only.
        Removes brittle regex/skill matching logic.
        """
        job_desc = job.description or ""
        resume_text = self._get_relevant_resume_text(user.resume)

        logger.debug(f"Job description length: {len(job_desc)}, Resume text length: {len(resume_text)}.")

        if not job_desc.strip() or not resume_text.strip():
            logger.warning("Empty job description or resume text. Cannot perform semantic matching.")
            return {
                "fit": "No",
                "reasons": ["Insufficient data for matching."],
                "score": 0.0
            }

        # --- Semantic Similarity ---
        logger.debug("Encoding job description and resume text.")
        job_emb = self.model.encode(job_desc, convert_to_tensor=True)
        resume_emb = self.model.encode(resume_text, convert_to_tensor=True)
        semantic_score = float(util.pytorch_cos_sim(job_emb, resume_emb).item())
        logger.debug(f"Calculated raw semantic score: {semantic_score:.4f}.")

        # Normalize score to [0, 1]
        final_score = max(0.0, min(semantic_score, 1.0))
        logger.info(f"Normalized semantic score: {final_score:.4f}.")

        # Decision threshold
        threshold = 0.6
        fit = "Yes" if final_score >= threshold else "No"
        logger.info(f"Match decision: {fit} (Score: {final_score:.4f} vs Threshold: {threshold}).")

        # --- Reasons ---
        reasons = [f"Semantic similarity score: {semantic_score:.2f}."]
        if fit == "No":
            reasons.append(f"Score is below the threshold ({threshold}).")
            logger.debug(f"Added reason: Score below threshold.")

        logger.debug(f"Returning match result: Fit={fit}, Score={final_score:.2f}, Reasons={reasons}.")
        return {
            "fit": fit,
            "reasons": reasons,
            "score": round(semantic_score, 2)
        }

    def is_recommended(self, job: JobPosting, user: UserProfile) -> bool:
        result = self.match(job, user)
        return result["fit"] == "Yes" and result["score"] >= 0.6
