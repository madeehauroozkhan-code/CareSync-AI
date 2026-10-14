"""
main.py
---------
FastAPI application entry point.

Exposes the endpoints the frontend (chat UI + admin dashboard) will call.
Integrates both the legacy synchronous orchestration and the new modular 
async architecture.
"""

import json
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# --- New Modular Architecture Imports ---
from backend.core.config import settings
from backend.core.logging import get_logger, configure_logging
from backend.core.middleware import (
    ErrorHandlerMiddleware,
    LoggingMiddleware,
    RequestIDMiddleware,
)
from backend.api.v1.router import api_v1_router

# Infrastructure clients
from backend.infrastructure.firebase.client import initialize_firebase, shutdown_firebase
from backend.infrastructure.redis.client import initialize_redis, close_redis
from backend.infrastructure.rabbitmq.client import initialize_rabbitmq, close_rabbitmq
from backend.infrastructure.qdrant.client import initialize_qdrant, close_qdrant

# --- Legacy Orchestration Imports ---
# Migrated to /api/v1 routes and LangGraph orchestrated planner

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Lifespan Manager (Startup / Shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured logging
    configure_logging()
    logger.info("Starting AI Sahayak backend...")

    # Initialize infrastructure
    initialize_firebase()
    initialize_redis()
    await initialize_rabbitmq()
    initialize_qdrant()

    yield  # Application runs

    # Teardown infrastructure
    logger.info("Shutting down AI Sahayak backend...")
    await close_rabbitmq()
    close_qdrant()
    close_redis()
    shutdown_firebase()

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Sahayak API",
    lifespan=lifespan,
    version="0.1.0",
)

# Middleware (Order matters: RequestID -> Logging -> ErrorHandler -> CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(ErrorHandlerMiddleware)
# app.add_middleware(LoggingMiddleware)
# app.add_middleware(RequestIDMiddleware)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# Mount the new modular v1 API router
app.include_router(api_v1_router)

# ---------------------------------------------------------------------------
# Data Loading (Graceful fallback)
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"

def load_json_safe(filepath: Path) -> list:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Data file not found: {filepath.name}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in data file: {filepath.name}")
        return []

HOSPITALS = load_json_safe(DATA_DIR / "mock_hospitals.json")
VOLUNTEERS = load_json_safe(DATA_DIR / "mock_volunteers.json")

@app.get("/")
def root():
    return {"status": "AI Sahayak API is running", "message": "Please use /api/v1 for all endpoints."}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True, access_log=False)

# Trigger reload for .env

# Final reload after dependencies

# Trigger reload
