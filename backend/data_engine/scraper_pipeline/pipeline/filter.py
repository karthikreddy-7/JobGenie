from typing import Optional

def should_save_job(experience: Optional[int]) -> bool:
    if experience is None:
        return False  # Don't save jobs where experience is not found

    # Save jobs that require between 1 and 10 years of experience
    if 1 <= experience <= 10:
        return True

    return False
