# db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()
FINANCE_DB_URL = os.getenv("FINANCE_DB_URL")

if not FINANCE_DB_URL:
    raise RuntimeError("FINANCE_DB_URL is not set in .env")

# Create SQLAlchemy engine
engine = create_engine(
    FINANCE_DB_URL,
    pool_pre_ping=True,   # avoids stale connections
    future=True
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True
)
