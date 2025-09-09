from sentence_transformers import SentenceTransformer, util
from matching_engine.interfaces import MatchingEngine
from schemas.job import JobPosting
from schemas.user import UserProfile
import re

class LLMMatcher(MatchingEngine):
    def __init__(self):
        self.model = SentenceTransformer("/home/karthik/dev/models/JobBERT-v2")

    def find_pros_and_cons(self, job: JobPosting, user: UserProfile) -> float:
        # Placeholder implementation
        pass

    def is_recommended(self, job: JobPosting, user: UserProfile) -> bool:
        # Placeholder implementation
        pass

    def _embed(self, text: str):
        return self.model.encode(str(text), convert_to_tensor=True)

    def _cosine(self, a, b) -> float:
        return util.cos_sim(a, b).item()

    def _extract_years(self, text: str) -> int:
        """
        Simple regex-based years of experience extractor.
        Example: '5+ years of experience' → 5
        """
        matches = re.findall(r"(\d+)\+?\s+years?", text.lower())
        if matches:
            return max(int(m) for m in matches)
        return 0

    def _skills_overlap(self, user_skills, job_text: str) -> float:
        """
        Compute % overlap of skills in job description.
        """
        job_text_lower = job_text.lower()
        user_skillset = set(s.lower() for s in (
                user_skills.programming_languages +
                user_skills.frameworks_tools +
                user_skills.other
        ))
        matches = [s for s in user_skillset if s in job_text_lower]
        return len(matches) / max(len(user_skillset), 1)

    def match(self, job: JobPosting, user: UserProfile) -> dict:
        """Return sub-scores and final match score for a user-job pair."""

        # -------- Experience similarity --------
        job_embedding = self._embed(job.description)
        exp_bullets = " ".join(
            bullet for exp in user.resume.experience for bullet in exp.bullets
        )
        exp_embedding = self._embed(exp_bullets) if exp_bullets else None
        exp_score = self._cosine(job_embedding, exp_embedding) if exp_embedding is not None else 0.0

        # -------- Skills overlap --------
        skills_score = self._skills_overlap(user.resume.skills, job.description)

        # -------- Project relevance --------
        project_text = " ".join(
            " ".join(p.description_bullets) for p in user.resume.projects
        )
        proj_embedding = self._embed(project_text) if project_text else None
        proj_score = self._cosine(job_embedding, proj_embedding) if proj_embedding is not None else 0.0

        # -------- Education relevance (rule-based placeholder) --------
        edu_match = any(
            deg.lower() in job.description.lower()
            for edu in user.resume.education
            for deg in [edu.degree]
        )

        # -------- Years of experience check --------
        job_years = self._extract_years(job.description)
        user_years = sum(
            self._extract_years(exp.role + " " + " ".join(exp.bullets))
            for exp in user.resume.experience
        )
        exp_requirement_ok = (user_years >= job_years)

        # -------- Weighted Final Score --------
        final_score = (
                0.4 * exp_score +
                0.3 * skills_score +
                0.15 * proj_score +
                0.1 * (1.0 if exp_requirement_ok else 0.0) +
                0.05 * (1.0 if edu_match else 0.0)
        )

        return {
            "experience_score": exp_score,
            "skills_score": skills_score,
            "project_score": proj_score,
            "education_match": edu_match,
            "experience_requirement_met": exp_requirement_ok,
            "final_score": round(final_score, 4)
        }
