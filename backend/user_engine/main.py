from sqlalchemy.orm import Session

from backend.database.models import User
from backend.database.setup_db import SessionLocal
from backend.schemas.user import *
from backend.user_engine.interfaces import UserEngine


class UserEngineImpl(UserEngine):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def insert_user_data(self, user_profile: UserProfile):
        # Convert UserProfile schema to User model
        user_data = User(
            user_id=user_profile.user_id,
            resume=user_profile.resume.model_dump_json(),
            preferences=user_profile.preferences.model_dump_json() if user_profile.preferences else None,
            linkedin=user_profile.linkedin.model_dump_json() if user_profile.linkedin else None,
            user_automation_settings=user_profile.user_automation_settings.model_dump_json() if user_profile.user_automation_settings else None,
        )
        self.db_session.add(user_data)
        self.db_session.commit()
        self.db_session.refresh(user_data)
        return user_data

if __name__ == "__main__":
    db = SessionLocal()
    user_engine = UserEngineImpl(db)

    # Example data based on the user's request
    example_resume = Resume(
        header=Header(
            full_name="Karthik Reddy B",
            location="Mumbai", # Assuming Mumbai based on experience
            phone="9063007185",
            email="basupallykarthikreddy@gmail.com",
            linkedin="LinkedIn", # Placeholder, ideally a URL
            github="GitHub",     # Placeholder, ideally a URL
            portfolio="Portfolio" # Placeholder, ideally a URL
        ),
        summary=None,
        education=[
            EducationEntry(
                id="edu1",
                institution="VIT University",
                degree="Bachelor of Technology (B.Tech) in Electronics & Communication Engineering",
                city="Vellore, Tamil Nadu, India",
                start_date="Sep 2020",
                end_date="May 2024",
                gpa="8.7/10.0",
                coursework="" # Not provided in the example
            )
        ],
        experience=[
            ExperienceEntry(
                id="exp1",
                company="Nomura",
                role="Software Engineer",
                city="Mumbai",
                start_date="Jul 2024",
                end_date="Present",
                bullets=[
                    "Served as Subject Matter Expert (SME) for 3+ critical downstream adapters, leveraging Java and Apache Camel microservices to manage high-volume client reporting, End-of-Day (EOD) trades, and regulatory flows within prime brokerage operations.",
                    "Pioneered a high-throughput Java Spring Boot microservice for regulatory trade persistence, optimizing an MS SQL-based storage solution. Accelerated processing of 60M+ transactions over 3 years by cutting insertion times from 6-7 seconds to 40 milliseconds through advanced query optimization and caching strategies.",
                    "Led the ”Sonar Auto Fix” initiative, deploying Dockerized GitLab runners for automated resolution of 500+ monthly code vulnerabilities. This CI/CD-integrated solution, utilizing LLM agentic workflows, reduced manual remediation by 40% for automated refactoring and documentation.",
                    "Developed Python AI scripts to automate bulk code editing across 20+ microservices, integrating Jira and GitLab APIs to streamline and enhance DevOps workflows."
                ]
            ),
            ExperienceEntry(
                id="exp2",
                company="Techwondoe",
                role="Full-Stack Developer intern",
                city="Remote",
                start_date="Apr 2024",
                end_date="Jul 2024",
                bullets=[
                    "Architected and implemented scalable RESTful APIs for a multi-tenant Task Management System using NestJS, TypeORM, and PostgreSQL, achieving 99.9% API uptime during production load testing.",
                    "Engineered a multi-layer data validation pipeline utilizing class-validator decorators, custom validation schemas, and pre-save hooks, which reduced invalid field submissions by 35% and streamlined data integrity.",
                    "Designed and integrated JWT-based authentication and role-based access control, improving security posture and reducing unauthorized access incidents by 45%.",
                    "Introduced Swagger/OpenAPI 3.0 documentation, decreasing onboarding time for frontend teams by 60% for API consumption."
                ]
            )
        ],
        projects=[
            ProjectEntry(
                id="proj1",
                title="InfyTrade",
                date="", # Not provided
                technologies="ReactJS, ChartJS, Flask, Django, PostgreSQL, Docker, AWS, ML models (Python), Figma, REST APIs.",
                link="GitHub", # Placeholder, ideally a URL
                description_bullets=[
                    "Developed a scalable, cloud-native backend on AWS with Dockerized Flask/Django microservices and PostgreSQL, integrating Machine Learning models (Python) for real-time portfolio management and predictive analytics across 20+ RESTful APIs.",
                    "Enabled users to analyze stocks, forex, crypto, and F&O via a live code editor for custom ML model development and algorithmic trading strategies."
                ]
            ),
            ProjectEntry(
                id="proj2",
                title="AGRI.AI",
                date="", # Not provided
                technologies="ReactJS, Django, Python, Machine Learning, Deep Learning, CNN, Random Forest, Decision Trees, Vercel.",
                link="GitHub", # Placeholder, ideally a URL
                description_bullets=[
                    "Crafted a predictive analytics platform using Machine Learning (ML) and Deep Learning (DL) to optimize agriculture, delivering crop recommendations and disease detection.",
                    "Integrated Random Forest, Decision Trees, and CNN models within a Django backend to analyze soil data and plant images for accurate, real-time insights."
                ]
            )
        ],
        skills=Skills(
            programming_languages=["Java", "Python", "JavaScript", "SQL", "HTML/CSS", "YAML"],
            frameworks_tools=["Spring Boot", "Apache Camel", "NestJs", "FastApi", "Flask", "React.js", "Spring Data JPA", "TypeORM", "REST APIs", "Docker", "Git", "GitHub", "GitLab", "Jira", "VS Code", "Apache Kafka", "Swagger/OpenAPI", "CI/CD", "LLM Agentic Workflows"],
            other=["Data Structures & Algorithms", "RESTful APIs", "Microservices", "Object-Oriented Programming (OOP)", "Test-Driven Development (TDD)", "System Design", "Full-Stack Development", "Agile Methodologies"]
        ),
        certifications=[
            CertificationEntry(
                id="cert1",
                title="5+ skill badges/certifications",
                issuer="IBM, Cisco, Google, AWS",
                date="" # Not provided
            ),
            CertificationEntry(
                id="cert2",
                title="Led and organized weekly coding sessions for the Tech Enthusiasts Club",
                issuer="", # Not provided
                date="" # Not provided
            )
        ]
    )

    # Mock data for UserPreferences
    mock_preferences = UserPreferences(
        preferred_roles=["Software Engineer", "Full-Stack Developer"],
        preferred_locations=["Mumbai", "Remote"],
        preferred_companies=["Nomura", "Google", "Amazon"],
        avoid_companies=["CompanyX"],
        remote_only=True,
        min_experience=0,
        max_experience=3,
        keywords=["Python", "Java", "Microservices"],
        blacklist_keywords=["Support", "Testing"]
    )

    # Mock data for LinkedInCredentials
    mock_linkedin = LinkedInCredentials(
        username="karthik.linkedin",
        password="mockpassword123",
        auth_token="mock_auth_token_abc"
    )

    # Mock data for UserAutomationSettings
    mock_automation_settings = UserAutomationSettings(
        auto_apply=True,
        referral_enabled=True,
        referral_threshold=0.85,
        connection_threshold=30,
        max_applications_per_day=10
    )

    user_profile_data = UserProfile(
        user_id="karthik_reddy_b", # Example user ID
        resume=example_resume,
        preferences=mock_preferences,
        linkedin=mock_linkedin,
        user_automation_settings=mock_automation_settings
    )

    print(f"Inserting user data for: {user_profile_data.user_id}")
    inserted_user = user_engine.insert_user_data(user_profile_data)
    print(f"User inserted with ID: {inserted_user.user_id}")

    # Clean up (optional, for testing purposes)
    # db.delete(inserted_user)
    # db.commit()
    db.close()
