"""
settings.py
-------------
Centralized configuration. Reads from environment variables so real API
keys never get hardcoded or committed to git. Copy .env.example to .env
and fill in real values before running with live integrations.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)
except ImportError:
    # python-dotenv is optional; if it's not installed, we just rely on
    # whatever is already in the environment (fine for most demo setups).
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# --- LLM provider (used once you upgrade Intake/Triage from keyword-based
# to LLM-based reasoning) ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none")  # "gemini" | "openai" | "groq" | "none"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# --- Maps / geolocation ---
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# --- Notifications ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "")

# --- Firebase (simulated hospital status) ---
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "")

# --- App-level constants ---
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
