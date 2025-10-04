from sqlalchemy import create_engine, Column, String, Boolean, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class VerifiedForm(Base):
    __tablename__ = "verified_forms"
    
    form_hash = Column(String, primary_key=True)
    recipient_email = Column(String, nullable=False)
    origin_domain = Column(String, nullable=False)
    website_name = Column(String, nullable=False)
    website_url = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    activation_token = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_submission_at = Column(DateTime, nullable=True)
    submission_count = Column(Integer, default=0)

engine = create_engine("sqlite:///./contact_forms.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
