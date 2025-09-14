import re
from typing import Optional

def extract_experience(description: str) -> Optional[int]:
    """
    Extracts the minimum years of experience from a job description.

    Args:
        description: The job description text.

    Returns:
        The extracted minimum years of experience as an integer, or None if not found.
    """
    if not description:
        return None

    # Regex to find patterns like "5+ years of experience", "3-5 years", "2 years experience"
    patterns = [
        r'(\d+)\s*\+\s*years of experience',
        r'(\d+)\s*-\s*\d+\s*years',
        r'(\d+)\s*years experience'
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return None
