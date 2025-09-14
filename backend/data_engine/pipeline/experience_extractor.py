import re
from typing import List

# --- Number words mapping ---
NUMBER_WORDS = {
    'a': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20,
    'half': 0.5, 'quarter': 0.25, 'dozen': 12
}

# --- Fresher synonyms ---
FRESHER_TERMS = [
    "fresher", "entry level", "graduate trainee", "campus hire",
    "fresh graduate", "recent graduate", "walk in", "walk-in",
    "intern to full time", "trainee program"
]

# --- Filtering terms ---
OPTIONAL_KEYWORDS = ["preferred", "nice to have", "optional", "a plus"]
BLACKLIST_KEYWORDS = [
    "company", "organization", "established", "founded",
    "in business", "track record", "industry experience"
]


def extract_experience(description: str) -> int:
    """
    Extracts minimum years of experience required from job description.
    Returns:
        int: Minimum years (0 for fresher, -1 for error/uncertain).
    """
    try:
        if not description:
            return 0

        desc = description.lower()

        # --- 1. Check for fresher roles ---
        for term in FRESHER_TERMS:
            if term in desc:
                return 0

        lines = desc.split("\n")
        candidates: List[float] = []

        # --- 2. Parse each line ---
        for line in lines:
            if any(k in line for k in OPTIONAL_KEYWORDS):
                continue
            if any(k in line for k in BLACKLIST_KEYWORDS):
                continue

            clean_line = re.sub(r'[^a-z0-9\s.\-]', ' ', line)
            clean_line = re.sub(r'\s+', ' ', clean_line).strip()

            # --- 2a. Ranges like "2-4 years" / "2 to 4 years" ---
            range_pattern = r'(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?|y|exp)'
            for match in re.findall(range_pattern, clean_line):
                low, high = match
                try:
                    low, high = float(low), float(high)
                    candidates.append(low)  # take minimum
                except ValueError:
                    continue

            # --- 2b. Word ranges: "between three and five years" ---
            word_range_pattern = (
                r'between\s+(' + '|'.join(NUMBER_WORDS.keys()) + r')\s+(?:and|to)\s+('
                + '|'.join(NUMBER_WORDS.keys()) + r')\s+years?'
            )
            for match in re.findall(word_range_pattern, clean_line):
                low, high = match
                if low in NUMBER_WORDS:
                    candidates.append(float(NUMBER_WORDS[low]))

            # --- 2c. Numeric years: "5+ years", "3 years exp" ---
            numeric_year_pattern = r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?|y|exp)'
            for match in re.findall(numeric_year_pattern, clean_line):
                try:
                    candidates.append(float(match))
                except ValueError:
                    continue

            # --- 2d. Word-based years: "five years", "dozen years" ---
            word_year_pattern = r'\b(' + '|'.join(NUMBER_WORDS.keys()) + r')\b\s+(?:years?|yrs?|exp)'
            for match in re.findall(word_year_pattern, clean_line):
                if match in NUMBER_WORDS:
                    candidates.append(float(NUMBER_WORDS[match]))

            # --- 2e. Months: "18 months", "6+ months" ---
            month_pattern = r'(\d+(?:\.\d+)?)\s*\+?\s*months?'
            for match in re.findall(month_pattern, clean_line):
                try:
                    years = float(match) / 12
                    candidates.append(round(years, 1))
                except ValueError:
                    continue

        # --- 3. Post-processing ---
        if not candidates:
            return 0

        if 0 in candidates:
            return 0

        # Special handling: "max X years" or "up to X years" → treat as fresher
        if re.search(r'\b(up to|max)\s+\d+\s+years?', desc):
            return 0

        # Normally take the highest *minimum requirement*
        result = max(candidates)

        return int(result + 0.5)  # round to nearest int

    except Exception:
        return -1



# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    jd = """
**DESCRIPTION**
---------------


The Amazon Web Services Professional Services (ProServe) team is seeking a Senior Betting and Gaming Advisory Consultant to shape and transform how enterprises leverage cloud technology. As a Consulting Cloud Architect specializing in Betting and Gaming, you will design, implement, and optimize cloud\-based solutions tailored to the unique needs of online sports betting, iGaming, and casino gaming clients. You will work closely with industry leaders like FanDuel, DraftKings, and Scientific to architect cloud environments that support real\-time transactions, massive user concurrency, and stringent regulatory requirements. Your expertise will drive low\-latency, secure, and compliant platforms that enhance player engagement and operational success.  

  

Possessing a deep understanding of AWS products and services, as a Senior Betting and Gaming Delivery Consultant you will drive innovation and influence executive\-level stakeholders across multiple organizations. You’ll work closely with stakeholders as trusted advisors providing guidance on industry trends, enterprise cloud transformation, and innovative cloud solutions. You will be responsible sales support, ensuring alignment to customer business outcomes and value realization.  

  

The AWS Professional Services organization is a global team of experts that help customers realize their desired business outcomes when using the AWS Cloud. We work together with customer teams and the AWS Partner Network (APN) to execute enterprise cloud computing initiatives. Our team provides assistance through a collection of offerings which help customers achieve specific outcomes related to enterprise cloud adoption. We also deliver focused guidance through our global specialty practices, which cover a variety of solutions, technologies, and industries.  

  

Key job responsibilities  

As an experienced Betting and Gaming industry business and IT Advisory professional, you will be responsible for:  

  

* Solution Design: Architect AWS cloud solutions to support betting and gaming platforms. Design infrastructure for high\-availability, low\-latency applications.
* Client Collaboration: Partner with Betting and Gaming clients to understand their technical and regulatory needs, such as real\-time data processing, fraud detection, and compliance with gaming regulations (e.g., GLI, MGA, or state\-specific rules). Translate business requirements into robust cloud architectures.
* Optimization: Leverage cloud\-native tools to optimize performance, reduce latency, and manage costs. Implement solutions for real\-time analytics, such as player behavior tracking or churn prediction, using tools such as AWS Kinesis.
* Scalability and Performance: Design infrastructure to handle peak loads (e.g., millions of simultaneous bets during major sporting events like the Super Bowl). Ensure global scalability for multi\-jurisdictional operations, supporting platforms in regulated markets.
* Security and Compliance: Design secure cloud environments with encryption, identity management (e.g., AWS IAM), and audit trails to meet regulatory standards (e.g., PCI DSS, GDPR, or U.S. state gaming laws). Protect sensitive player data and ensure compliance with responsible gaming protocols.
* Consulting and Advisory: Provide technical guidance on cloud\-native technologies, microservices, and containerization. Advise on integrating AI/ML for various use cases inclusive of fraud detection.
* Cross\-Functional Collaboration: Work with internal teams and external partners to deliver end\-to\-end solutions. Collaborate with client engineering teams to integrate cloud services with betting platforms or casino management systems.
* Innovation and Trends: Stay updated on Betting and Gaming trends, such as mobile betting, live in\-play wagering, and blockchain for transparent transactions. Prototype emerging technologies and evaluate their applicability for client use cases.

  

A day in the life  

Advisory Team partners with our customers to increase their shareholder value and assist in disrupting their business models. We enable our customers to drive competitive advantage by enhancing their digital capabilities that will enable them to innovate on new products and services.  

  

Our key focus areas include: Cloud Strategy and Business Value Alignment (Enterprise Transformation), Cloud Operating Models \& Governance, Cloud Migration Readiness and Planning, Organizational Change \& Enablement, Data \& AI Transformation, Supply Chain, Telco, Media, Gaming and Entertainment.  

  

About the team  

About AWS:  

Diverse Experiences: AWS values diverse experiences. Even if you do not meet all of the preferred qualifications and skills listed in the job below, we encourage candidates to apply. If your career is just starting, hasn’t followed a traditional path, or includes alternative experiences, don’t let it stop you from applying.  

Why AWS? Amazon Web Services (AWS) is the world’s most comprehensive and broadly adopted cloud platform. We pioneered cloud computing and never stopped innovating — that’s why customers from the most successful startups to Global 500 companies trust our robust suite of products and services to power their businesses.  

Inclusive Team Culture \- Here at AWS, it’s in our nature to learn and be curious. Our employee\-led affinity groups foster a culture of inclusion that empower us to be proud of our differences. Ongoing events and learning experiences, including our Conversations on Race and Ethnicity (CORE) and AmazeCon (diversity) conferences, inspire us to never stop embracing our uniqueness.  

Mentorship \& Career Growth \- We’re continuously raising our performance bar as we strive to become Earth’s Best Employer. That’s why you’ll find endless knowledge\-sharing, mentorship and other career\-advancing resources here to help you develop into a better\-rounded professional.  

Work/Life Balance \- We value work\-life harmony. Achieving success at work should never come at the expense of sacrifices at home, which is why we strive for flexibility as part of our working culture. When we feel supported in the workplace and at home, there’s nothing we can’t achieve in the cloud.  

  

**BASIC QUALIFICATIONS**
------------------------

* 5\+ years in cloud architecture, IT consulting, or solutions engineering, with at least 2 years focused on Betting and Gaming.
* Bachelor's degree in Computer Science, Engineering, related field, or equivalent experience
* 2\+ yrs experience designing cloud solutions for real\-time, regulated applications (e.g., sports betting, online casinos). Including familiarity with betting/gaming platforms and compliance frameworks.
* 2\+ years experience with data lakes, real\-time analytics, and/or fraud detection.
* 3\+ years experience with sales targets, business development, and driving customer satisfaction

**PREFERRED QUALIFICATIONS**
----------------------------

* AWS experience preferred, with proficiency in a wide range of AWS services (e.g., EC2, Lambda, RDS, ElastiCache, and API Gateway.)
* AWS Professional level certifications (e.g., AWS Certified AI Practitioner, Machine Learning, Solutions Architect)
* Understanding of betting/gaming workflows.
* Proficiency in containerization (Docker, Kubernetes), infrastructure\-as\-code (Terraform, CloudFormation), and CI/CD pipelines.
* Knowledge of real\-time data processing (e.g., Kafka, Kinesis) and database technologies (e.g., DynamoDB, PostgreSQL).
* Knowledge of security and compliance standards (e.g., HIPAA, GDPR)
* Strong communication skills with the ability to explain technical concepts to both technical and non\-technical audiences

  

Amazon is an equal opportunity employer and does not discriminate on the basis of protected veteran status, disability, or other legally protected status.  

  

Los Angeles County applicants: Job duties for this position include: work safely and cooperatively with other employees, supervisors, and staff; adhere to standards of excellence despite stressful conditions; communicate effectively and respectfully with employees, supervisors, and staff to ensure exceptional customer service; and follow all federal, state, and local laws and Company policies. Criminal history may have a direct, adverse, and negative relationship with some of the material job duties of this position. These include the duties and responsibilities listed above, as well as the abilities to adhere to company policies, exercise sound judgment, effectively manage stress and work safely and respectfully with others, exhibit trustworthiness and professionalism, and safeguard business operations and the Company’s reputation. Pursuant to the Los Angeles County Fair Chance Ordinance, we will consider for employment qualified applicants with arrest and conviction records.  

  

Our inclusive culture empowers Amazonians to deliver the best results for our customers. If you have a disability and need a workplace accommodation or adjustment during the application and hiring process, including support for the interview or onboarding process, please visit https://amazon.jobs/content/en/how\-we\-hire/accommodations for more information. If the country/region you’re applying in isn’t listed, please contact your Recruiting Partner.  

  

Our compensation reflects the cost of labor across several US geographic markets. The base pay for this position ranges from $138,200/year in our lowest geographic market up to $239,000/year in our highest geographic market. Pay is based on a number of factors including market location and may vary depending on job\-related knowledge, skills, and experience. Amazon is a total compensation company. Dependent on the position offered, equity, sign\-on payments, and other forms of compensation may be provided as part of a total compensation package, in addition to a full range of medical, financial, and/or other benefits. For more information, please visit https://www.aboutamazon.com/workplace/employee\-benefits. This position will remain posted until filled. Applicants should apply via our internal or external career site.
    """
    experience = extract_experience(jd)
    print("Minimum experience required:", experience)  # Output: 5
