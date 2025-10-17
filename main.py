from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routes.contact import router as contact_router
from routes.info import router as info_router
from routes.info import router as info_router

app = FastAPI(title="ContactFast")

# Allow all origins since users can embed from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "ContactFast",
        "description": "A FastAPI-based contact form API that requires zero setup",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "submit": "/submit",
        }
    }

# Include routers
app.include_router(contact_router)
app.include_router(info_router)