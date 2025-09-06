import os
from sqlalchemy import create_engine
from models import Base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in .env file")

# Create engine and initialize tables
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

print("✅ Tables created successfully!")
