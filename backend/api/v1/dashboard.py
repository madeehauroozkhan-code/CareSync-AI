from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
from backend.agents.public_health_intelligence.agent import PublicHealthAgent, PublicHealthInput
from backend.core.logging import get_logger
from backend.core.ws_manager import ws_manager

logger = get_logger(__name__)

router = APIRouter(tags=["dashboard"])

from backend.core import live_state

public_health_agent = PublicHealthAgent()

@router.get("/dashboard/cases")
async def get_dashboard_cases():
    """Returns recent case history for the admin/NGO dashboard."""
    return {"cases": live_state.recent_cases}


@router.get("/dashboard/outbreaks")
async def get_outbreak_alerts():
    """Runs the Public Health Intelligence Agent against recorded case history."""
    try:
        input_data = PublicHealthInput(
            cases=live_state.recent_cases,
            cluster_threshold=2,  # Low threshold for demo
        )
        result = await public_health_agent.analyze(input_data)
        return {"outbreaks": result.model_dump()}
    except Exception as e:
        logger.error(f"Error in outbreak detection: {e}")
        return {"error": str(e)}


@router.get("/dashboard/hospitals")
async def get_dashboard_hospitals():
    """Returns hospital occupancy data loaded from data/mock_hospitals.json."""
    from backend.main import HOSPITALS  # loaded once at startup
    return {"hospitals": HOSPITALS}


@router.get("/dashboard/volunteers")
async def get_dashboard_volunteers():
    """Returns volunteer roster loaded from data/mock_volunteers.json."""
    from backend.main import VOLUNTEERS  # loaded once at startup
    return {"volunteers": VOLUNTEERS}


@router.post("/dashboard/reset")
async def reset_dashboard():
    """Clears in-memory demo state and notifies connected dashboards."""
    live_state.reset_cases()
    await ws_manager.broadcast({"event": "dashboard_reset"})
    return {"status": "reset"}


@router.websocket("/dashboard/ws/live-feed")
async def live_feed_ws(websocket: WebSocket):
    """
    Push channel for the admin dashboard. Broadcasts a "case_processed"
    event (see backend/core/ws_manager.py) whenever /api/v1/chat finishes
    processing a new case, and a "dashboard_reset" event on reset.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from the client, just keep the
            # connection open and detect disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
