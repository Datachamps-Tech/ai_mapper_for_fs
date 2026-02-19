# db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

POC_DBT_URL = os.getenv("POC_DBT_URL")

if not POC_DBT_URL:
    raise RuntimeError("POC_DBT_URL is not set in .env")

# Create SQLAlchemy engine
engine = create_engine(
    POC_DBT_URL,
    pool_pre_ping=True,
    future=True
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True
)