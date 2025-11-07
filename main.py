"""
ContactFast - Zero-setup contact form API.

A FastAPI application that provides contact form submission endpoints
without requiring user signup or configuration. Features auto-verification,
spam protection, and multi-tenant support.
"""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.contact import router as contact_router
from routes.info import router as info_router

load_dotenv()

app = FastAPI(
    title="ContactFast",
    description="A zero-setup contact form API that requires no signup or configuration. Just copy-paste the form code snippet and you are done!",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow all origins since users can embed from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contact_router)
app.include_router(info_router)
