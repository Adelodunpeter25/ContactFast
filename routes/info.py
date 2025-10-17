from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, desc
from database import SessionLocal, VerifiedDomain
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/info/analytics", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Analytics dashboard showing all stats in HTML format"""
    db = SessionLocal()
    
    try:
        # Quick stats
        total_domains = db.query(VerifiedDomain).count()
        total_submissions = db.query(func.sum(VerifiedDomain.submission_count)).scalar() or 0
        verified_domains = db.query(VerifiedDomain).filter(VerifiedDomain.verified == True).count()
        
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        active_last_24h = db.query(VerifiedDomain).filter(
            VerifiedDomain.last_submission_at >= twenty_four_hours_ago
        ).count()
        
        active_last_7d = db.query(VerifiedDomain).filter(
            VerifiedDomain.last_submission_at >= seven_days_ago
        ).count()
        
        # Top domains
        top_domains = db.query(VerifiedDomain).order_by(
            desc(VerifiedDomain.submission_count)
        ).limit(10).all()
        
        # Recent activity - show domains with recent submissions
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        recent_domains = db.query(VerifiedDomain).filter(
            VerifiedDomain.last_submission_at >= month_ago
        ).order_by(desc(VerifiedDomain.last_submission_at)).limit(10).all()
        
        recent_activity = []
        for domain in recent_domains:
            # Show actual activity based on when last submission occurred
            has_activity_today = domain.last_submission_at and domain.last_submission_at >= today_start
            has_activity_week = domain.last_submission_at and domain.last_submission_at >= week_ago
            has_activity_month = domain.last_submission_at and domain.last_submission_at >= month_ago
            
            recent_activity.append({
                'domain': domain.domain,
                'website_name': domain.website_name,
                'submission_count': domain.submission_count,
                'submissions_today': '✓' if has_activity_today else '-',
                'submissions_this_week': '✓' if has_activity_week else '-',
                'submissions_this_month': '✓' if has_activity_month else '-',
                'last_submission_at': domain.last_submission_at
            })
        
        # Rate limit stats (domains hitting limits)
        high_volume_domains = db.query(VerifiedDomain).filter(
            VerifiedDomain.submission_count >= 50
        ).count()
        
        # Potential rate limited domains (>5 submissions in last hour estimate)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_active = db.query(VerifiedDomain).filter(
            VerifiedDomain.last_submission_at >= one_hour_ago
        ).count()
        
        # Email recipients data
        email_recipients = db.query(
            VerifiedDomain.recipient_email,
            func.count(VerifiedDomain.domain).label('domain_count'),
            func.sum(VerifiedDomain.submission_count).label('total_emails')
        ).group_by(VerifiedDomain.recipient_email).order_by(
            desc('total_emails')
        ).limit(10).all()
        
        stats = {
            'total_domains': total_domains,
            'total_submissions': total_submissions,
            'verified_domains': verified_domains,
            'active_last_24h': active_last_24h,
            'active_last_7d': active_last_7d,
            'average_submissions_per_domain': round(total_submissions / total_domains, 2) if total_domains > 0 else 0,
            'high_volume_domains': high_volume_domains,
            'recent_active_domains': recent_active
        }
        
        return templates.TemplateResponse("analytics.html", {
            "request": request,
            "stats": stats,
            "top_domains": top_domains,
            "recent_activity": recent_activity,
            "email_recipients": email_recipients
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load analytics: {str(e)}")
    finally:
        db.close()