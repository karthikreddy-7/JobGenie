import logging
from typing import Optional

logger = logging.getLogger(__name__)

def should_save_job(experience: Optional[int]) -> bool:
    """
    Determines whether a job should be saved based on the required experience.

    Args:
        experience: The required years of experience for the job.

    Returns:
        True if the job should be saved, False otherwise.
    """
    if experience is None:
        logger.info("Job filtered out because experience is not found.")
        return False  # Don't save jobs where experience is not found

    # Save jobs that require between 1 and 10 years of experience
    if 1 <= experience <= 3:
        logger.info(f"Job with {experience} years of experience will be saved.")
        return True
    
    logger.info(f"Job with {experience} years of experience filtered out.")
    return False