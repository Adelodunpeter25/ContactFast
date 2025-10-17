from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import SessionLocal, VerifiedDomain
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

# Response models
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
    top_domains: List[DomainStats]

class DomainActivity(BaseModel):
    domain: str
    website_name: str
    submissions_today: int
    submissions_this_week: int
    submissions_this_month: int
    last_submission_at: Optional[datetime]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/info/analytics", response_model=AnalyticsSummary)
async def get_analytics_summary(limit: int = Query(10, ge=1, le=50, description="Number of top domains to return")):
    """
    Get overall analytics summary including:
    - Total domains and submissions
    - Verified domains count
    - Active domains in last 30 days
    - Top domains by submission count
    """
    db = next(get_db())
    
    try:
        # Get basic counts
        total_domains = db.query(VerifiedDomain).count()
        total_submissions = db.query(func.sum(VerifiedDomain.submission_count)).scalar() or 0
        verified_domains = db.query(VerifiedDomain).filter(VerifiedDomain.verified == True).count()
        
        # Active domains in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_domains_last_30_days = db.query(VerifiedDomain).filter(
            VerifiedDomain.last_submission_at >= thirty_days_ago
        ).count()
        
        # Top domains by submission count
        top_domains_query = db.query(VerifiedDomain).order_by(
            desc(VerifiedDomain.submission_count)
        ).limit(limit)
        
        top_domains = [
            DomainStats(
                domain=domain.domain,
                website_name=domain.website_name,
                website_url=domain.website_url,
                recipient_email=domain.recipient_email,
                verified=domain.verified,
                created_at=domain.created_at,
                last_submission_at=domain.last_submission_at,
                submission_count=domain.submission_count
            )
            for domain in top_domains_query.all()
        ]
        
        return AnalyticsSummary(
            total_domains=total_domains,
            total_submissions=total_submissions,
            verified_domains=verified_domains,
            active_domains_last_30_days=active_domains_last_30_days,
            top_domains=top_domains
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")
    finally:
        db.close()

@router.get("/info/domain/{domain}", response_model=DomainStats)
async def get_domain_info(domain: str):
    """
    Get detailed information about a specific domain including:
    - Domain verification status
    - Submission statistics
    - Last activity timestamp
    """
    db = next(get_db())
    
    try:
        domain_record = db.query(VerifiedDomain).filter(VerifiedDomain.domain == domain).first()
        
        if not domain_record:
            raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
        
        return DomainStats(
            domain=domain_record.domain,
            website_name=domain_record.website_name,
            website_url=domain_record.website_url,
            recipient_email=domain_record.recipient_email,
            verified=domain_record.verified,
            created_at=domain_record.created_at,
            last_submission_at=domain_record.last_submission_at,
            submission_count=domain_record.submission_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch domain info: {str(e)}")
    finally:
        db.close()

@router.get("/info/domains", response_model=List[DomainStats])
async def get_all_domains(
    verified_only: bool = Query(False, description="Return only verified domains"),
    active_only: bool = Query(False, description="Return only domains with submissions in last 30 days"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of domains to return"),
    offset: int = Query(0, ge=0, description="Number of domains to skip")
):
    """
    Get list of all domains with their statistics.
    Supports filtering by verification status and recent activity.
    """
    db = next(get_db())
    
    try:
        query = db.query(VerifiedDomain)
        
        # Apply filters
        if verified_only:
            query = query.filter(VerifiedDomain.verified == True)
        
        if active_only:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            query = query.filter(VerifiedDomain.last_submission_at >= thirty_days_ago)
        
        # Order by submission count (most active first)
        query = query.order_by(desc(VerifiedDomain.submission_count))
        
        # Apply pagination
        domains = query.offset(offset).limit(limit).all()
        
        return [
            DomainStats(
                domain=domain.domain,
                website_name=domain.website_name,
                website_url=domain.website_url,
                recipient_email=domain.recipient_email,
                verified=domain.verified,
                created_at=domain.created_at,
                last_submission_at=domain.last_submission_at,
                submission_count=domain.submission_count
            )
            for domain in domains
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch domains: {str(e)}")
    finally:
        db.close()

@router.get("/info/activity", response_model=List[DomainActivity])
async def get_domain_activity(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(20, ge=1, le=100, description="Number of domains to return")
):
    """
    Get domain activity analysis showing submission patterns over time.
    Returns domains sorted by recent activity.
    """
    db = next(get_db())
    
    try:
        # Calculate date thresholds
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Get domains with recent activity
        domains = db.query(VerifiedDomain).filter(
            VerifiedDomain.last_submission_at >= (now - timedelta(days=days))
        ).order_by(desc(VerifiedDomain.last_submission_at)).limit(limit).all()
        
        activity_list = []
        
        for domain in domains:
            # For this simplified version, we'll estimate daily/weekly/monthly submissions
            # based on total submissions and time since creation
            # In a real implementation, you'd want a separate submissions table with timestamps
            
            days_since_creation = (now - domain.created_at).days or 1
            avg_daily_submissions = domain.submission_count / days_since_creation
            
            # Estimate recent activity (this is simplified - ideally you'd have detailed logs)
            submissions_today = int(avg_daily_submissions) if domain.last_submission_at and domain.last_submission_at >= today_start else 0
            submissions_this_week = int(avg_daily_submissions * 7) if domain.last_submission_at and domain.last_submission_at >= week_ago else 0
            submissions_this_month = int(avg_daily_submissions * 30) if domain.last_submission_at and domain.last_submission_at >= month_ago else 0
            
            activity_list.append(DomainActivity(
                domain=domain.domain,
                website_name=domain.website_name,
                submissions_today=submissions_today,
                submissions_this_week=submissions_this_week,
                submissions_this_month=submissions_this_month,
                last_submission_at=domain.last_submission_at
            ))
        
        return activity_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch activity data: {str(e)}")
    finally:
        db.close()

@router.get("/info/stats")
async def get_quick_stats():
    """
    Get quick statistics for dashboard display.
    Returns basic metrics without detailed data.
    """
    db = next(get_db())
    
    try:
        # Basic counts
        total_domains = db.query(VerifiedDomain).count()
        total_submissions = db.query(func.sum(VerifiedDomain.submission_count)).scalar() or 0
        verified_domains = db.query(VerifiedDomain).filter(VerifiedDomain.verified == True).count()
        
        # Recent activity
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        active_last_24h = db.query(VerifiedDomain).filter(
            VerifiedDomain.last_submission_at >= twenty_four_hours_ago
        ).count()
        
        active_last_7d = db.query(VerifiedDomain).filter(
            VerifiedDomain.last_submission_at >= seven_days_ago
        ).count()
        
        # Most active domain
        most_active_domain = db.query(VerifiedDomain).order_by(
            desc(VerifiedDomain.submission_count)
        ).first()
        
        return {
            "total_domains": total_domains,
            "total_submissions": total_submissions,
            "verified_domains": verified_domains,
            "active_last_24h": active_last_24h,
            "active_last_7d": active_last_7d,
            "most_active_domain": {
                "domain": most_active_domain.domain,
                "website_name": most_active_domain.website_name,
                "submission_count": most_active_domain.submission_count
            } if most_active_domain else None,
            "average_submissions_per_domain": round(total_submissions / total_domains, 2) if total_domains > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch quick stats: {str(e)}")
    finally:
        db.close()