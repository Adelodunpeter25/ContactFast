"""
Pydantic schemas for data validation.

Defines request/response models for contact forms, domain statistics,
and analytics data with proper type validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# Contact form schemas
class ContactForm(BaseModel):
    to: EmailStr
    website_name: str
    website_url: str
    name: str
    email: EmailStr
    subject: str
    message: str


# Info/Analytics schemas
class DomainStats(BaseModel):
    domain: str
    website_name: str
    website_url: str
    recipient_email: str
    verified: bool
    created_at: datetime
    last_submission_at: Optional[datetime]
    submission_count: int


class AnalyticsSummary(BaseModel):
    total_domains: int
    total_submissions: int
    verified_domains: int
    active_domains_last_30_days: int
    top_domains: list[DomainStats]


class DomainActivity(BaseModel):
    domain: str
    website_name: str
    submissions_today: int
    submissions_this_week: int
    submissions_this_month: int
    last_submission_at: Optional[datetime]
