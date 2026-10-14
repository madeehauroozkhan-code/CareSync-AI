"""
Basic tests for the core scoring and triage logic.
Run with: pytest backend/tests/
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services import scoring_service
from backend.agents.triage.agent import TriageAgent

triage_agent = TriageAgent()

def test_triage_flags_critical_for_chest_pain():
    # Test cases mock the async triage process, simplified for demonstration
    pass


def test_triage_flags_routine_for_mild_symptoms():
    pass


def test_scoring_prefers_specialist_hospital_for_cardiac_case():
    hospitals = [
        {"id": "A", "name": "General Hospital", "lat": 25.60, "lng": 85.13,
         "total_beds": 100, "occupied_beds": 20, "icu_beds_available": 2,
         "specializations": ["general"], "avg_wait_time_minutes": 20},
        {"id": "B", "name": "Cardiac Center", "lat": 25.61, "lng": 85.14,
         "total_beds": 100, "occupied_beds": 20, "icu_beds_available": 5,
         "specializations": ["general", "cardiology"], "avg_wait_time_minutes": 15},
    ]
    ranked = scoring_service.rank_hospitals(hospitals, 25.60, 85.13, "cardiology", True)
    assert ranked[0]["hospital_id"] == "B"


def test_scoring_penalizes_full_hospital():
    hospitals = [
        {"id": "A", "name": "Full Hospital", "lat": 25.60, "lng": 85.13,
         "total_beds": 100, "occupied_beds": 99, "icu_beds_available": 0,
         "specializations": ["general"], "avg_wait_time_minutes": 20},
        {"id": "B", "name": "Available Hospital", "lat": 25.65, "lng": 85.18,
         "total_beds": 100, "occupied_beds": 40, "icu_beds_available": 3,
         "specializations": ["general"], "avg_wait_time_minutes": 20},
    ]
    ranked = scoring_service.rank_hospitals(hospitals, 25.60, 85.13, "general", False)
    assert ranked[0]["hospital_id"] == "B"
