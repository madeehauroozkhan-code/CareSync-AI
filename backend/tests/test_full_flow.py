import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.orchestration.planner import PlannerOrchestrator
from backend.core.logging import get_logger

logger = get_logger(__name__)

def safe_print(label, val):
    if val is None:
        print(f"{label}: None")
    elif isinstance(val, str):
        print(f"{label}: {val.encode('ascii', 'replace').decode('ascii')}")
    else:
        print(f"{label}: {val}")

async def main():
    print("Initializing Planner Orchestrator...")
    orchestrator = PlannerOrchestrator()
    
    print("\n--- TEST 1: Chest Pain (Triage + Care Coordination) ---")
    try:
        result = await orchestrator.orchestrate(
            raw_input="I am having severe chest pain and left arm numbness.",
            location={"lat": 25.60, "lng": 85.13}
        )
        safe_print("Workflow Status", result.get("status"))
        safe_print("Response", result.get("response"))
        safe_print("Selected Agents", result.get("selected_agents"))
        safe_print("Emergency Detected", result.get("emergency_detected"))
        print("Hospital Recommendations:", [h.get("hospital_name") for h in result.get("hospital_recommendations", [])])
    except Exception as e:
        print("TEST 1 FAILED:", e)

    print("\n--- TEST 2: General Knowledge ---")
    try:
        result = await orchestrator.orchestrate(
            raw_input="What are the symptoms of Dengue?",
            location={"lat": 25.60, "lng": 85.13}
        )
        safe_print("Workflow Status", result.get("status"))
        safe_print("Response", result.get("response"))
        safe_print("Selected Agents", result.get("selected_agents"))
    except Exception as e:
        print("TEST 2 FAILED:", e)

    print("\n--- TEST 3: Disaster Mode ---")
    try:
        result = await orchestrator.orchestrate(
            raw_input="There is a massive flood here, people are drowning, we need help immediately!",
            location={"lat": 25.61, "lng": 85.13},
            metadata={"disaster_mode": True}
        )
        safe_print("Workflow Status", result.get("status"))
        safe_print("Response", result.get("response"))
        safe_print("Selected Agents", result.get("selected_agents"))
        safe_print("Emergency Detected", result.get("emergency_detected"))
    except Exception as e:
        print("TEST 3 FAILED:", e)

if __name__ == "__main__":
    asyncio.run(main())
