from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timedelta
from urllib.parse import urlparse
from pathlib import Path
import resend
import os
import re

from core.database import SessionLocal, VerifiedDomain
from core.schemas import ContactForm

router = APIRouter()

# Load email template
template_path = Path(__file__).parent.parent / "templates" / "email_template.html"
EMAIL_TEMPLATE = template_path.read_text()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

resend.api_key = RESEND_API_KEY

# Rate limiting storage
rate_limit_store = {}

# Disposable email domains
DISPOSABLE_DOMAINS = {
    'tempmail.com', 'guerrillamail.com', '10minutemail.com', 'throwaway.email',
    'mailinator.com', 'trashmail.com', 'fakeinbox.com', 'yopmail.com',
    'temp-mail.org', 'getnada.com', 'maildrop.cc', 'sharklasers.com',
    'mintemail.com', 'emailondeck.com', 'mohmal.com', 'mytemp.email',
    'dispostable.com', 'throwawaymail.com', 'tempinbox.com', 'guerrillamailblock.com',
    'spamgourmet.com', 'mailnesia.com', 'mailcatch.com', 'mailnator.com',
    'getairmail.com', 'harakirimail.com', 'anonymousemail.me', 'deadaddress.com',
    'emailsensei.com', 'mailexpire.com', 'tempr.email', 'tempmail.net',
    'disposablemail.com', 'burnermail.io', 'guerrillamail.net', 'guerrillamail.org',
    'guerrillamail.biz', 'spam4.me', 'grr.la', 'guerrillamail.de',
    'trbvm.com', 'mailforspam.com', 'spambox.us', 'incognitomail.org',
    'tmailinator.com', 'spamfree24.org', 'spamfree24.com', 'spamfree24.eu',
    'spamfree24.net', 'spamfree24.info', 'spamfree24.de', 'wegwerfmail.de',
    'wegwerfmail.net', 'wegwerfmail.org', 'trashmail.net', 'trashmail.org',
    'trashmail.me', 'trashmail.de', 'trashmail.at', 'trashmail.fr',
    'trashmail.ws', 'trash-mail.com', 'trash-mail.de', 'trash-mail.at',
    'trash-mail.cf', 'trash-mail.ga', 'trash-mail.gq', 'trash-mail.ml',
    'trash-mail.tk', 'mailtemp.info', 'mailtemp.net', 'mailtemp.org',
    'tempmail.de', 'tempmail.eu', 'tempmail.us', 'tempmail.it',
    'tempmail.fr', 'tempmail.co', 'tempmail.ninja', 'tempmail.plus',
    'tempmail.email', 'tempmail.io', 'tempmail.dev', 'tempmail.top'
}



def extract_domain(website_url: str) -> str:
    """Extract domain from website URL"""
    try:
        parsed = urlparse(website_url)
        return parsed.netloc or parsed.path
    except:
        return website_url

def check_rate_limit(key: str, limit: int, window_minutes: int) -> bool:
    now = datetime.utcnow()
    if key not in rate_limit_store:
        rate_limit_store[key] = []
    
    # Remove old entries
    rate_limit_store[key] = [
        timestamp for timestamp in rate_limit_store[key]
        if now - timestamp < timedelta(minutes=window_minutes)
    ]
    
    if len(rate_limit_store[key]) >= limit:
        return False
    
    rate_limit_store[key].append(now)
    return True

def is_disposable_email(email: str) -> bool:
    """Check if email is from a disposable domain"""
    domain = email.split('@')[-1].lower()
    return domain in DISPOSABLE_DOMAINS

def is_spam_content(message: str, subject: str = "") -> bool:
    """Detect spam patterns in message content"""
    text = (message + " " + subject).lower()
    
    # Spam keywords
    spam_keywords = [
        'viagra', 'cialis', 'casino', 'lottery', 'prize', 'winner',
        'click here', 'buy now', 'limited time', 'act now', 'free money'
    ]
    
    for keyword in spam_keywords:
        if keyword in text:
            return True
    
    # Multiple URLs (more than 3)
    url_count = len(re.findall(r'http[s]?://', text))
    if url_count > 3:
        return True
    
    # Excessive repeated characters
    if re.search(r'(.)\1{10,}', text):
        return True
    
    # All caps message (more than 70% uppercase)
    if len(message) > 20:
        upper_ratio = sum(1 for c in message if c.isupper()) / len(message)
        if upper_ratio > 0.7:
            return True
    
    return False

@router.post("/submit")
async def submit_form(request: Request, form: ContactForm):
    client_ip = request.client.host
    db = SessionLocal()
    
    try:
        # Rate limiting by IP
        if not check_rate_limit(f"ip_{client_ip}", 5, 60):
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
        
        # Spam prevention checks
        if is_disposable_email(form.email):
            raise HTTPException(status_code=400, detail="Disposable email addresses are not allowed")
        
        if is_disposable_email(form.to):
            raise HTTPException(status_code=400, detail="Invalid recipient email")
        
        if is_spam_content(form.message, form.subject):
            raise HTTPException(status_code=400, detail="Message flagged as spam")
        
        # Extract domain
        domain = extract_domain(form.website_url)
        if not domain:
            raise HTTPException(status_code=400, detail="Invalid website URL")
        
        # Rate limiting by domain (10 per hour)
        if not check_rate_limit(f"domain_{domain}", 10, 60):
            raise HTTPException(status_code=429, detail="Domain rate limit exceeded. Please try again later.")
        
        verified_domain = db.query(VerifiedDomain).filter_by(domain=domain).first()
        
        if not verified_domain:
            # First time submission - auto-verify and send both emails
            new_domain = VerifiedDomain(
                domain=domain,
                recipient_email=form.to,
                website_name=form.website_name,
                website_url=form.website_url,
                verified=True,
                submission_count=1,
                last_submission_at=datetime.utcnow()
            )
            db.add(new_domain)
            db.commit()
            
            # Send the contact form submission
            email_html = EMAIL_TEMPLATE.format(
                name=form.name,
                email=form.email,
                subject=form.subject,
                message=form.message
            )
            
            params = {
                "from": FROM_EMAIL,
                "to": [form.to],
                "subject": f"New message from {form.website_name} - {form.subject}",
                "html": email_html
            }
            
            try:
                response = resend.Emails.send(params)
            except Exception as email_error:
                db.rollback()
                raise HTTPException(status_code=500, detail="Failed to send email. Please try again later.")
            
            # Send verification notification
            verification_html = f"""
            <html>
                <body style="font-family: Arial; padding: 20px;">
                    <h2>🎉 ContactFast Auto-Verification Complete!</h2>
                    <p>Great news! We detected this is your first message using ContactFast from domain <strong>{domain}</strong>.</p>
                    <p>Your domain is now verified and all future messages from this domain will be delivered instantly.</p>
                    <p>Website: {form.website_name}<br>Domain: {domain}</p>
                </body>
            </html>
            """
            
            verification_params = {
                "from": FROM_EMAIL,
                "to": [form.to],
                "subject": f"ContactFast: {domain} Auto-Verified ✅",
                "html": verification_html
            }
            
            try:
                resend.Emails.send(verification_params)
            except:
                pass  # Don't fail if verification email fails
            
            return {
                "message": "Form submitted successfully! Domain auto-verified.",
                "domain": domain,
                "resend_response": response
            }
        
        # Send submission email
        email_html = EMAIL_TEMPLATE.format(
            name=form.name,
            email=form.email,
            subject=form.subject,
            message=form.message
        )
        
        params = {
            "from": FROM_EMAIL,
            "to": [form.to],
            "subject": f"New message from {form.website_name} - {form.subject}",
            "html": email_html
        }
        
        try:
            response = resend.Emails.send(params)
        except Exception as email_error:
            raise HTTPException(status_code=500, detail="Failed to send email. Please try again later.")
        
        # Update stats
        verified_domain.last_submission_at = datetime.utcnow()
        verified_domain.submission_count += 1
        db.commit()
        
        return {
            "message": "Form submitted successfully!",
            "resend_response": response
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")
    finally:
        db.close()
