from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
import resend
import os
import hashlib
import secrets
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

load_dotenv()

from database import SessionLocal, VerifiedForm

# Load email templates
template_path = Path(__file__).parent / "templates" / "email_template.html"
EMAIL_TEMPLATE = template_path.read_text()

activation_template_path = Path(__file__).parent / "templates" / "activation_template.html"
ACTIVATION_TEMPLATE = activation_template_path.read_text()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
BASE_URL = os.getenv("BASE_URL")

resend.api_key = RESEND_API_KEY

app = FastAPI(title="Zero-Setup Contact Form API")

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

def generate_form_hash(recipient_email: str, origin: str) -> str:
    return hashlib.sha256(f"{recipient_email}{origin}".encode()).hexdigest()

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
    return {"status": "healthy", "message": "Zero-Setup Contact Form API"}

@app.post("/submit")
async def submit_form(request: Request, form: ContactForm):
    origin = request.headers.get("origin", "unknown")
    client_ip = request.client.host
    
    # Rate limiting
    if not check_rate_limit(f"ip_{client_ip}", 5, 60):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    # Generate form hash
    form_hash = generate_form_hash(form.to, origin)
    
    # Check database
    db = SessionLocal()
    try:
        verified_form = db.query(VerifiedForm).filter_by(form_hash=form_hash).first()
        
        if not verified_form:
            # First time submission - send activation email
            activation_token = secrets.token_urlsafe(32)
            
            # Check activation rate limit
            if not check_rate_limit(f"activation_{form.to}", 3, 1440):  # 3 per day
                raise HTTPException(status_code=429, detail="Too many activation requests for this email.")
            
            # Create new form entry
            new_form = VerifiedForm(
                form_hash=form_hash,
                recipient_email=form.to,
                origin_domain=origin,
                website_name=form.website_name,
                website_url=form.website_url,
                verified=False,
                activation_token=activation_token
            )
            db.add(new_form)
            db.commit()
            
            # Send activation email
            activation_url = f"{BASE_URL}/activate/{activation_token}"
            activation_html = ACTIVATION_TEMPLATE.format(
                website_name=form.website_name,
                website_url=form.website_url,
                recipient_email=form.to,
                activation_url=activation_url
            )
            
            params = {
                "from": FROM_EMAIL,
                "to": [form.to],
                "subject": f"Activate Contact Form for {form.website_name}",
                "html": activation_html
            }
            resend.Emails.send(params)
            
            return {
                "message": "Activation required",
                "detail": f"A confirmation email has been sent to {form.to}. Please check your inbox and click the activation link."
            }
        
        if not verified_form.verified:
            return {
                "message": "Pending activation",
                "detail": f"This form is awaiting activation. Please check {form.to} for the activation email."
            }
        
        # Form is verified - check rate limit
        if not check_rate_limit(f"form_{form_hash}", 10, 60):
            raise HTTPException(status_code=429, detail="Too many submissions. Please try again later.")
        
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
        verified_form.last_submission_at = datetime.utcnow()
        verified_form.submission_count += 1
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

@app.get("/activate/{token}")
async def activate_form(token: str):
    db = SessionLocal()
    try:
        verified_form = db.query(VerifiedForm).filter_by(activation_token=token).first()
        
        if not verified_form:
            return HTMLResponse(content="""
                <html>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1>❌ Invalid Activation Link</h1>
                        <p>This activation link is invalid or has expired.</p>
                    </body>
                </html>
            """, status_code=404)
        
        if verified_form.verified:
            return HTMLResponse(content=f"""
                <html>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1>✅ Already Activated</h1>
                        <p>Contact form for <strong>{verified_form.website_name}</strong> is already active.</p>
                        <p>You'll receive submissions at: {verified_form.recipient_email}</p>
                    </body>
                </html>
            """)
        
        # Activate the form
        verified_form.verified = True
        db.commit()
        
        return HTMLResponse(content=f"""
            <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>🎉 Contact Form Activated!</h1>
                    <p>Your contact form for <strong>{verified_form.website_name}</strong> is now active.</p>
                    <p>You'll receive submissions at: {verified_form.recipient_email}</p>
                    <p style="color: #666; margin-top: 30px;">You can close this window.</p>
                </body>
            </html>
        """)
        
    finally:
        db.close()
