from sentence_transformers import SentenceTransformer, util

from llm.client import OllamaChatClient
from matching_engine.interfaces import MatchingEngine
from schemas.job import JobPosting
from schemas.user import UserProfile
import json
import logging

logger = logging.getLogger(__name__)

class LLMMatcher(MatchingEngine):
    def __init__(self):
        self.client = OllamaChatClient(model="llama3.2")

    def find_pros_and_cons(self, job: JobPosting, user: UserProfile) -> float:
        # Placeholder implementation
        pass

    def is_recommended(self, job: JobPosting, user: UserProfile) -> bool:
        # Placeholder implementation
        pass


    def match(self, job: JobPosting, user: UserProfile) -> dict:
        """Return sub-scores and final match score for a user-job pair."""
        prompt = f"""
        You are a precise job matching assistant.
        Compare the following job description and candidate resume.
        
        Rules:
        - Always output valid JSON only.
        - Keys: "fit" (Yes/No), "reasons" (list of short bullets), "score" (0-1 float).
        - Place the highest weight on required years of experience and role relevance:
          - If the job explicitly requires experience (e.g., "3+ years in Java", "5 years of backend development")
            and the resume does not meet it → "fit" must be "No" regardless of other matches.
          - Skills and projects are secondary to experience.
        - The "score" should reflect this weighting (experience > skills > projects > education).
        
        Job Description:
        {job.description}
        
        Candidate Resume (structured JSON):
        {user.resume.json()}
        
        Return format (strict JSON):
        {{
          "fit": "Yes" or "No",
          "reasons": ["bullet1", "bullet2", "bullet3"],
          "score": 0.0 to 1.0
        }}
        """
        response = self.client.send_message(
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.strip("`")
                # also handle optional "json" language tag
                clean_response = clean_response.replace("json\n", "").replace("json", "", 1).strip()
            result = json.loads(clean_response)
            return result
        except Exception as e:
            logger.error(f"Failed to parse LLM output: {response} | Error: {e}")
            return {
                "fit": "No",
                "reasons": ["Parsing error – invalid LLM response"],
                "score": 0.0
            }


