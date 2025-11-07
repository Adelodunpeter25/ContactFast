"""
Database configuration and models.

SQLAlchemy setup with PostgreSQL backend for storing verified domains
and tracking submission statistics.
"""

from sqlalchemy import create_engine, Column, String, Boolean, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class VerifiedDomain(Base):
    __tablename__ = "verified_domains"
    
    domain = Column(String, primary_key=True)
    recipient_email = Column(String, nullable=False)
    website_name = Column(String, nullable=False)
    website_url = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_submission_at = Column(DateTime, nullable=True)
    submission_count = Column(Integer, default=0)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Convert postgres:// to postgresql+pg8000://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
