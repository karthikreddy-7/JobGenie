JobGenie Technical Documentation

1. Overview

JobGenie is an automated job application system designed to streamline the job search process. It scrapes job postings from various sources, filters them based on
user preferences, tailors resumes for specific jobs, and automates the application process. Additionally, it includes a referral engine to facilitate networking on
LinkedIn.

2. System Architecture

The backend of JobGenie is built on a modular, engine-based architecture. Each engine is responsible for a specific set of tasks and is defined by an abstract
interface. This design allows for multiple implementations of each engine, promoting flexibility and extensibility.

The core components of the system are:

* Engines: The functional heart of the application, handling everything from data scraping to application submission.
* LLM Integration: A Large Language Model is leveraged for intelligent decision-making in job matching and resume tailoring.
* Database: A PostgreSQL database persists all user data, job postings, and application history.
* Frontend: A user interface for interacting with the system.

3. Engines

3.1. Data Engine

* Purpose: Fetches job postings from external sources.
* Interface: backend.data_engine.interfaces.DataEngine
* Methods:
    * fetch_jobs(query: str, location: str, limit: int = 50) -> List[JobPosting]: Retrieves a list of job postings based on a search query and location.
* Implementations:
    * backend.data_engine.linkedin_scraper.py: This file is intended to contain the implementation for scraping job postings specifically from LinkedIn. The
      implementation details are not yet present.

3.2. Filtration Engine

* Purpose: Filters the scraped job postings to match a user's profile and preferences.
* Interface: backend.filtration_engine.interfaces.FiltrationEngine
* Methods:
    * filter_jobs(jobs: List[JobPosting], user: UserProfile) -> List[JobPosting]: Takes a list of jobs and a user profile, and returns a filtered list of jobs that
      are relevant to the user.
* Implementations:
    * backend.filtration_engine.generic_filter.py: Intended for a basic, rule-based filtering approach.
    * backend.filtration_engine.personalised_filter.py: Intended for a more advanced, personalized filtering approach, potentially using an LLM to better understand
      the nuances of job descriptions and user preferences.

3.3. Matching Engine

* Purpose: Analyzes the fit between a user and a specific job posting.
* Interface: backend.matching_engine.interfaces.MatchingEngine
* Methods:
    * find_pros_and_cons(job: JobPosting, user: UserProfile) -> object: Returns an object detailing the pros and cons of a job for a given user.
    * is_recommended(job: JobPosting, user: UserProfile) -> bool: Returns a boolean indicating whether the job is a good match for the user.
* Implementations:
    * backend.matching_engine.llm_matcher.py: This will use an LLM to perform a detailed analysis of the user's resume against the job description to determine the
      quality of the match.

3.4. Resume Engine

* Purpose: Generates resumes tailored to specific job applications.
* Interface: backend.resume_engine.interfaces.ResumeEngine
* Methods:
    * generate_resume(job: JobPosting, user: UserProfile, output_path: str, pros_and_cons: str) -> str: Creates a customized resume and returns the path to the
      generated file.
* Implementations:
    * backend.resume_engine.pdf_resume_generator.py: This will contain the logic for programmatically creating a PDF resume.

3.5. Referral Engine

* Purpose: Manages networking and referral requests on LinkedIn.
* Interface: backend.referral_engine.interfaces.ReferralEngine
* Methods:
    * send_connection_requests(job: JobPosting, user: UserProfile) -> int: Sends LinkedIn connection requests to employees at the target company.
    * send_referral_messages(job: JobPosting, user: UserProfile) -> int: Sends messages requesting referrals to established connections.
* Implementations:
    * backend.referral_engine.linkedin_connector.py: This will handle all interactions with the LinkedIn platform.

3.6. Auto Apply Engine

* Purpose: Automates the final step of submitting the job application.
* Interface: backend.auto_apply_engine.interfaces.AutoApplyEngine
* Methods:
    * apply_to_job(job: JobPosting, user: UserProfile, resume_path: str) -> bool: Fills out and submits online job application forms.
* Implementations:
    * backend.auto_apply_engine.autofill_form.py: This will contain the logic for web automation to fill out application forms.

4. LLM Integration

JobGenie uses a Large Language Model to bring intelligence to several of its engines. The primary LLM client is configured in backend/llm/client.py, which uses the
ollama library to interface with the gemma3:1b model.

The LLM is intended to be used in:

* Matching Engine: To provide a deep, semantic understanding of the user's resume and the job description, enabling a more accurate match score and the
  identification of nuanced pros and cons.
* Resume Engine: To dynamically tailor the language of the resume, such as the summary and experience bullet points, to align with the keywords and requirements of
  the job description.
* Filtration Engine: To power the personalised_filter, allowing for a more sophisticated filtering of jobs that goes beyond simple keyword matching.

5. Database

The system uses a PostgreSQL database to store and manage all its data.

* Connection: The database connection is managed by the get_db_connection function in backend/database/connection.py. It securely loads database credentials from a
  .env file.
* Schema: The database schema is defined using Pydantic models located in the backend/schemas directory. This ensures data consistency and provides clear, validated
  data structures throughout the application.
    * `user.py`: This is the most comprehensive schema, defining the UserProfile, UserPreferences, UserAutomationSettings, LinkedInCredentials, and Resume models.
      It serves as the central repository for all user-related information.
    * `job.py`: Defines the JobPosting model, which standardizes the structure of job data scraped from various sources.
    * `application.py`: Defines the ApplicationRecord model, used to track the status and history of each job application initiated by the system.

6. Main Application and Frontend

* `backend/main.py`: This file is the main entry point for the backend application. It is responsible for orchestrating the various engines to execute the full job
  application pipeline, from scraping to submission. The implementation details are not yet present.
* `frontend/`: This directory is intended to house the user interface of the application. The specific technologies and structure of the frontend are not yet
  defined.

7. Future Implementation

To achieve full functionality, the following files require implementation:

* backend/data_engine/linkedin_scraper.py
* backend/filtration_engine/generic_filter.py
* backend/filtration_engine/personalised_filter.py
* backend/matching_engine/llm_matcher.py
* backend/resume_engine/pdf_resume_generator.py
* backend/referral_engine/linkedin_connector.py
* backend/auto_apply_engine/autofill_form.py
* backend/main.py

