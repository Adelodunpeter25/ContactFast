# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import resend
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env
load_dotenv()

# Load email template for recieving contact form data
template_path = Path(__file__).parent / "email_template.html"
EMAIL_TEMPLATE = template_path.read_text()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")  # e.g., https://your-frontend.com

resend.api_key = RESEND_API_KEY

app = FastAPI(title="Contact Form Submission API")

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://adelodunpeter.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for incoming form data
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

@app.get("/")
async def health_check():
    return {"contact api status": "healthy"}

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
        params = {
            "from": FROM_EMAIL,
            "to": [TO_EMAIL],
            "subject": f"{form.subject} - from {form.name}",
            "html": email_html
        }
        response = resend.Emails.send(params)
        return {"message": "Form submitted successfully!", "resend_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")