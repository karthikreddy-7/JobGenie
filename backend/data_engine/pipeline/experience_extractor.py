import re
from typing import Optional, List, Tuple

# --- Configuration ---
NUMBER_WORDS = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
}

# Keywords to identify high-priority sections
SECTION_KEYWORDS = {
    'requirements': 10,
    'qualifications': 10,
    'experience': 8,
    'skills': 5,
    'responsibilities': 1,
}

# Common technical skills to deprioritize skill-specific experience
SKILL_KEYWORDS = [
    'python', 'java', 'c#', 'c++', 'javascript', 'typescript', 'sql', 'nosql',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'react', 'angular', 'vue',
    'terraform', 'ansible', 'machine learning', 'data science'
]


def extract_experience(description: str) -> int:
    """
    Extracts minimum experience using a scored, contextual, and hierarchical approach.

    This enhanced architecture provides higher accuracy by:
    1.  **Sectional Weighting**: Prioritizing experience found in "Requirements" sections.
    2.  **Contextual Scoring**: Differentiating between general and skill-specific experience.
    3.  **Month Conversion**: Handling experience mentioned in months.
    """
    if not description:
        return 0

    # --- 1. Preprocessing ---
    lines = description.lower().split('\n')

    # --- 2. Candidate Extraction & Scoring ---
    candidates: List[Tuple[int, int]] = []  # (years, score)
    current_section_score = 1  # Default score

    for line in lines:
        # --- 2a. Sectional Analysis ---
        # Update current score if a section header is found
        for keyword, score in SECTION_KEYWORDS.items():
            if line.strip().startswith(keyword):
                current_section_score = score
                break

        # --- 2b. Line Filtering ---
        optional_keywords = ['preferred', 'nice to have', 'optional', 'a plus']
        if any(keyword in line for keyword in optional_keywords):
            continue

        # --- 2c. Regex Matching & Scoring ---
        clean_line = re.sub(r'[^a-z0-9\s+\-]', ' ', line)
        clean_line = re.sub(r'\s+', ' ', clean_line).strip()

        # Determine score based on context
        score = current_section_score
        if 'overall' in clean_line:
            score += 20  # Highest priority
        if any(skill in clean_line for skill in SKILL_KEYWORDS):
            score -= 5  # Deprioritize skill-specific lines

        # --- Regex for years ---
        year_patterns = [
            r'(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:-|to)\s*\d+\s*(?:years?|yrs?)'
        ]
        for pattern in year_patterns:
            matches = re.findall(pattern, clean_line)
            for match in matches:
                if match.isdigit():
                    candidates.append((int(match), score))

        # --- Regex for months (and convert to years) ---
        month_pattern = r'(\d+)\s*\+?\s*months?'
        matches = re.findall(month_pattern, clean_line)
        for match in matches:
            if match.isdigit():
                years = round(int(match) / 12, 1)
                candidates.append((years, score))

    # --- 3. Post-Processing & Selection ---
    if not candidates:
        return 0

    # Handle "0-X years" cases explicitly
    for years, _ in candidates:
        if years == 0:
            return 0

    # Sort candidates: first by the highest score, then by the lowest number of years
    candidates.sort(key=lambda x: (-x[1], x[0]))

    # The best candidate is the first one after sorting
    best_candidate_years = candidates[0][0]

    # Return as an integer (rounding up for fractions)
    return int(best_candidate_years + 0.5)


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    jd = """
    Qualifications:
    - Minimum of 2 years backend development
    - Experience with SQL, Python, and AWS
    - Nice to have: 1 year experience with Kubernetes
    - Overall, candidate should have at least 3 years experience in software projects
    """
    experience = extract_experience(jd)
    print("Minimum experience required:", experience)  # Output: 0
