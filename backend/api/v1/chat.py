from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

from backend.core import live_state
from backend.core.ws_manager import ws_manager
from backend.orchestration.planner import PlannerOrchestrator
from backend.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["chat"])

# Using a single orchestrator instance for the router
orchestrator = PlannerOrchestrator()


class ChatRequest(BaseModel):
    message: str
    lat: float
    lng: float
    age: Optional[int] = None
    disaster_mode: bool = False
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    state: Dict[str, Any]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main endpoint for citizen chat.
    Invokes the LangGraph orchestrated workflow.
    """
    # Create a new session if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Run the workflow
    try:
        formatted_response = await orchestrator.orchestrate(
            raw_input=request.message,
            session_id=session_id,
            location={"lat": request.lat, "lng": request.lng},
            metadata={"age": request.age, "disaster_mode": request.disaster_mode}
        )
        
        reply = formatted_response.get("response", "I'm sorry, I couldn't process your request.")
        
        # ---- Store + broadcast case for dashboard Live Feed ----
        import time as _time
        intake = formatted_response.get("intake_data") or {}
        triage = formatted_response.get("triage_data") or {}
        
        raw_symptoms = intake.get("symptoms", [])
        raw_urgency = formatted_response.get("urgency_level") or triage.get("urgency", "unknown")

        # CaseList.jsx expects location_name, symptom_tags, epoch timestamp,
        # and Title-cased urgency ("Critical"/"Urgent"/"Routine").
        case_record = {
            "case_id": session_id,
            "timestamp": _time.time(),                        # epoch seconds
            "region": "Patna",
            "location_name": "Patna, Bihar",                  # CaseList reads this
            "lat": request.lat,
            "lng": request.lng,
            "symptoms": raw_symptoms,
            "symptom_tags": raw_symptoms,                     # CaseList reads this
            "urgency": raw_urgency.capitalize() if raw_urgency else "Unknown",
        }
        live_state.add_case(case_record)

        # Convert agent_results to LiveAgentTrace.jsx format
        # Backend sends: {agent_name, status, execution_time_ms}
        # Dashboard expects: {icon, agent, message, detail}
        agent_icons = {
            "intake": "📋", "triage": "🩺", "knowledge": "📚",
            "care_coordination": "🏥", "ambulance": "🚑", "community_response": "👥",
            "public_health": "📊", "followup": "📞", "explainability": "💡",
        }
        raw_trace = formatted_response.get("agent_results", [])
        dashboard_trace = []
        for step in raw_trace:
            name = step.get("agent_name", "unknown")
            status = step.get("status", "unknown")
            ms = step.get("execution_time_ms", 0)
            icon = agent_icons.get(name, "⚙️")
            msg = f"{status} in {ms:.0f}ms" if status == "completed" else f"FAILED: {step.get('error', '')}"
            dashboard_trace.append({
                "icon": icon,
                "agent": name,
                "message": msg,
                "detail": f"Execution time: {ms:.0f}ms" if status == "completed" else step.get("error", ""),
            })

        await ws_manager.broadcast({
            "event": "case_processed",
            "case": case_record,
            "agent_trace": dashboard_trace,
        })
        # ----------------------------------------------------------------
        
        return ChatResponse(
            session_id=session_id,
            reply=reply,
            state=formatted_response
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            session_id=session_id,
            reply="An internal error occurred. Please try again later.",
            state={}
        )
