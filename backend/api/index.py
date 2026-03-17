"""Vercel serverless entry point for FastAPI backend."""
import sys
import os

# Add the backend root to the path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.api import API
from fastapi.middleware.cors import CORSMiddleware

app = API().app

# CORS — allow frontend origins
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
