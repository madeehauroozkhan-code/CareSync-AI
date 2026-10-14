from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
import time, random
from backend.agents.emergency_response.agent import EmergencyResponseAgent, EmergencyInput
from backend.agents.public_health_intelligence.agent import PublicHealthAgent, PublicHealthInput
from backend.core.logging import get_logger
from backend.core import live_state
from backend.core.ws_manager import ws_manager

logger = get_logger(__name__)

router = APIRouter(tags=["emergency"])

emergency_agent = EmergencyResponseAgent()
public_health_agent = PublicHealthAgent()


class SimulateDisasterRequest(BaseModel):
    num_cases: int = 20
    disaster_type: str = "flood"
    region: str = "Patna"


@router.post("/emergency/simulate")
async def simulate_disaster(request: SimulateDisasterRequest):
    """
    Triggers the 'disaster surge' demo: generates a burst of Critical cases
    around a fixed location to observe the Emergency Response Agent's redistribution.
    Now also updates live_state and broadcasts via WebSocket.
    """
    try:
        result = await emergency_agent.simulate_disaster(
            disaster_type=request.disaster_type,
            region=request.region,
            case_count=request.num_cases,
        )

        # Generate synthetic cases and push them to live dashboard
        disaster_symptoms = {
            "flood": ["drowning risk", "waterborne infection", "hypothermia", "skin infection"],
            "earthquake": ["crush injury", "fracture", "head trauma", "internal bleeding"],
            "cyclone": ["flying debris injury", "fracture", "respiratory distress"],
            "fire": ["severe burns", "smoke inhalation", "respiratory failure"],
        }
        symptoms_pool = disaster_symptoms.get(request.disaster_type, ["trauma", "injury"])

        for i in range(request.num_cases):
            case = {
                "case_id": f"disaster_{request.disaster_type}_{int(time.time())}_{i}",
                "timestamp": time.time(),
                "region": request.region,
                "location_name": f"{request.region}, Bihar",
                "lat": 25.59 + random.uniform(-0.05, 0.05),
                "lng": 85.13 + random.uniform(-0.05, 0.05),
                "symptoms": random.sample(symptoms_pool, min(2, len(symptoms_pool))),
                "symptom_tags": random.sample(symptoms_pool, min(2, len(symptoms_pool))),
                "urgency": random.choice(["Critical", "Urgent", "Critical"]),
            }
            live_state.add_case(case)
            await ws_manager.broadcast({
                "event": "case_processed",
                "case": case,
                "agent_trace": [
                    {"icon": "🚨", "agent": "emergency_response", "message": f"Disaster case #{i+1} — {request.disaster_type}", "detail": f"Region: {request.region}"},
                    {"icon": "🏥", "agent": "care_coordination", "message": "Routing to nearest available hospital", "detail": "Auto-dispatched"},
                ],
            })

        return {
            "num_cases_simulated": request.num_cases,
            "disaster_type": request.disaster_type,
            "emergency_response": result.model_dump(),
        }
    except Exception as e:
        logger.error(f"Error simulating disaster: {e}")
        return {"error": str(e)}


class SimulateOutbreakRequest(BaseModel):
    num_cases: int = 15
    region: str = "Patna"


@router.post("/emergency/simulate-outbreak")
async def simulate_outbreak(request: SimulateOutbreakRequest):
    """
    Generates a burst of similar-symptom cases (fever cluster) in one region
    and runs them through the Public Health Intelligence Agent.
    Now also updates live_state and broadcasts via WebSocket.
    """
    try:
        outbreak_symptoms = ["high fever", "body pain", "headache", "fatigue", "rash"]
        synthetic_cases = []
        for i in range(request.num_cases):
            case = {
                "case_id": f"outbreak_sim_{int(time.time())}_{i}",
                "timestamp": time.time(),
                "region": request.region,
                "location_name": f"{request.region}, Bihar",
                "lat": 25.61 + (i * 0.001),
                "lng": 85.14 + (i * 0.001),
                "symptoms": random.sample(outbreak_symptoms, 3),
                "symptom_tags": random.sample(outbreak_symptoms, 3),
                "urgency": random.choice(["Urgent", "Urgent", "Critical"]),
            }
            synthetic_cases.append(case)
            live_state.add_case(case)
            await ws_manager.broadcast({
                "event": "case_processed",
                "case": case,
                "agent_trace": [
                    {"icon": "📊", "agent": "public_health", "message": f"Outbreak case #{i+1} detected", "detail": f"Symptoms: {', '.join(case['symptoms'])}"},
                ],
            })

        input_data = PublicHealthInput(cases=synthetic_cases, cluster_threshold=2)
        result = await public_health_agent.analyze(input_data)
        return {
            "num_cases_simulated": request.num_cases,
            "region": request.region,
            "outbreak_analysis": result.model_dump(),
        }
    except Exception as e:
        logger.error(f"Error simulating outbreak: {e}")
        return {"error": str(e)}
