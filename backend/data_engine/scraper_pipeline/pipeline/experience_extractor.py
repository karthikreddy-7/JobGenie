import re
from typing import Optional


NUMBER_WORDS = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
}

def extract_experience(description: str) -> int:
    if not description:
        return 0

    # First, filter out lines containing "preferred" to avoid capturing optional experience levels.
    # This is a key step to ensure we only focus on required qualifications.
    lines = description.lower().split('\n')
    non_preferred_lines = [line for line in lines if 'preferred' not in line]
    text = '\n'.join(non_preferred_lines)

    all_found_years = []

    # Pattern 1: Most common - digits followed by "year" or "yr".
    # Captures "2 years", "3-5 yrs", "4+ years", "5 - 7 years".
    # It specifically looks for the first number in a potential range.
    pattern1 = r'(\d+)\s*(?:[-–to+]?\s*\d*)?\s*(?:year|yr)s?'
    matches1 = re.findall(pattern1, text)
    if matches1:
        all_found_years.extend([int(m) for m in matches1])

    # Pattern 2: Keywords like "minimum", "at least", "required" followed by a number.
    # e.g., "minimum of 3 years", "at least 5 yrs", "8 years required"
    pattern2 = r'(?:minimum|min|at least|required)\s*(?:of\s*)?(\d+)\s*(?:year|yr)s?'
    matches2 = re.findall(pattern2, text)
    if matches2:
        all_found_years.extend([int(m) for m in matches2])

    # Pattern 3: Handle number words (e.g., "one year", "five years").
    word_pattern = r'\b(' + '|'.join(NUMBER_WORDS.keys()) + r')\s+(?:year|yr)s?'
    matches3 = re.findall(word_pattern, text)
    if matches3:
        all_found_years.extend([NUMBER_WORDS[word] for word in matches3])

    # If any experience is mentioned, return the smallest number found,
    # as this now represents the minimum *required* experience.
    if all_found_years:
        return min(all_found_years)

    # Default to 0 if no specific experience is found.
    return 0




# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    jd = """
Data Warehouse Administrator -The State of Florida
Experience :- 4+ Years

Vacancy :- 1

Location :- The State of Florida USA

Salary :- Negotiable

Job Type :- Hybrid

Provides data warehouse support functions including database maintenance, development, and enhancement.
Performs database administration functions such as loading data into database from external sources, supports users in constructing queries and generating output files.
Responsible for on-going design and performance enhancement, which include reviewing queries for performance issues, estimating, monitoring, and tuning the warehouse as it operates.
Develops and administers processes to ensure interoperability and security of data warehouse system.
Must possess a strong understanding of source data, data modeling, and data repository requirements.

Dimensions Education:

Bachelor’s degree in computer science, Information Systems, or another related field. Or equivalent work experience.


Experience:

A minimum of 4 years of IT work experience in business intelligence tools and systems.


Complexity:

Intermediate professional level role. Provides daily administration, maintenance, and support of data warehouse applications in multi-platform environments. Works on multiple projects as a team member and may lead projects of moderate complexity. May coach more junior technical staff.

Email Us: jobs@goldenfive.net .Only qualified applicants will be contacted.
    """

    experience = extract_experience(jd)
    print("Minimum experience required:", experience)  # Output: 2
