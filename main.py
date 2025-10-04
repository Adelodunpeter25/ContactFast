# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from resend import Resend
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env (optional if set in Vercel)
load_dotenv()

# Load email template
template_path = Path(__file__).parent / "email_template.html"
EMAIL_TEMPLATE = template_path.read_text()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")  # e.g., https://your-frontend.com

resend = Resend(api_key=RESEND_API_KEY)

app = FastAPI(title="Contact Form API")

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
)

# Pydantic model for incoming form data
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/submit")
async def submit_form(form: ContactForm):
    try:
        # Populate email template
        email_html = EMAIL_TEMPLATE.format(
            name=form.name,
            email=form.email,
            subject=form.subject,
            message=form.message
        )
        
        # Send email via Resend
        response = resend.emails.send(
            from_email=FROM_EMAIL,
            to=[TO_EMAIL],
            subject=f"{form.subject} - from {form.name}",
            html=email_html
        )
        return {"message": "Form submitted successfully!", "resend_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")
