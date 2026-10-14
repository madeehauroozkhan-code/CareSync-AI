"""
backend/api/v1/router.py
--------------------------
Central API v1 router that aggregates all sub-routers.

All v1 endpoints are prefixed with /api/v1 in main.py.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.api.v1.health import router as health_router
from backend.api.v1.chat import router as chat_router
from backend.api.v1.dashboard import router as dashboard_router
from backend.api.v1.emergency import router as emergency_router

# Create the v1 router
api_v1_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(emergency_router)

# Future routers will be included here as they are implemented:
# from backend.api.v1.auth import router as auth_router
# api_v1_router.include_router(chat_router)
# api_v1_router.include_router(auth_router)
# api_v1_router.include_router(sessions_router)
# api_v1_router.include_router(appointments_router)
