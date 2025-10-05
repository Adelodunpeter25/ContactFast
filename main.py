from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import resend
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse

load_dotenv()

from database import SessionLocal, VerifiedDomain

# Load email templates
template_path = Path(__file__).parent / "templates" / "email_template.html"
EMAIL_TEMPLATE = template_path.read_text()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
BASE_URL = os.getenv("BASE_URL")

resend.api_key = RESEND_API_KEY

app = FastAPI(title="ContactFast")

# Allow all origins since users can embed from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting storage (in-memory for simplicity)
rate_limit_store = {}

class ContactForm(BaseModel):
    to: EmailStr
    website_name: str
    website_url: str
    name: str
    email: EmailStr
    subject: str
    message: str

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

@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "ContactFast API"}

@app.post("/submit")
async def submit_form(request: Request, form: ContactForm):
    client_ip = request.client.host
    
    # Rate limiting by IP
    if not check_rate_limit(f"ip_{client_ip}", 5, 60):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    # Extract domain
    domain = extract_domain(form.website_url)
    
    # Rate limiting by domain (10 per hour)
    if not check_rate_limit(f"domain_{domain}", 10, 60):
        raise HTTPException(status_code=429, detail="Domain rate limit exceeded. Please try again later.")
    
    # Check database
    db = SessionLocal()
    try:
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
            response = resend.Emails.send(params)
            
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
            resend.Emails.send(verification_params)
            
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
        response = resend.Emails.send(params)
        
        # Update stats
        verified_domain.last_submission_at = datetime.utcnow()
        verified_domain.submission_count += 1
        db.commit()
        
        return {
            "message": "Form submitted successfully!",
            "resend_response": response
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        db.close()