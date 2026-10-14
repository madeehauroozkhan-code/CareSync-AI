"""
Care Coordination Agent
========================
Chooses the best hospital AND ambulance using the weighted scoring model — 
not just the nearest one. This is the core differentiator of the project.

Owner: Backend Dev
"""

import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from backend.services.scoring_service import rank_hospitals


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class CareCoordinationInput(BaseModel):
    """Input from the Triage Agent + patient location."""
    symptoms: list[str] = []
    urgency: str = "routine"           # "critical", "urgent", "routine"
    required_specialization: Optional[str] = None  # e.g. "cardiology"
    patient_location: dict = {}        # {"lat": 25.594, "lng": 85.137}
    age: Optional[int] = None


class HospitalScore(BaseModel):
    """Score breakdown for a single hospital."""
    hospital_id: str
    hospital_name: str
    hospital_lat: float = 0.0
    hospital_lng: float = 0.0
    total_score: float                 # 0 to 100
    proximity_score: float
    capacity_score: float
    specialization_score: float
    wait_time_score: float
    icu_score: float
    distance_km: float
    eta_minutes: int
    free_beds: int = 0
    icu_beds_available: int = 0
    has_specialization: bool = False
    reasons: list[str] = []            # Why this hospital was scored this way


class CareCoordinationOutput(BaseModel):
    """Ranked hospital recommendations with explanations."""
    recommended_hospital: Optional[HospitalScore] = None  # Top pick
    all_scores: list[HospitalScore] = []  # All hospitals ranked
    ambulance_dispatched: bool = False
    ambulance_eta_minutes: Optional[int] = None
    explanation: str = ""              # Human-readable summary of why
    confidence: float = 0.9            # Confidence of the routing decision
    reasons: list[str] = []            # List of structured reasons


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class CareCoordinationAgent:
    """
    Care Coordination Agent — the brain of hospital selection.
    """

    def __init__(self):
        self.hospitals = self._load_mock_hospitals()

    def _load_mock_hospitals(self) -> list[dict]:
        """Load hospital data from mock JSON file."""
        try:
            # Resolve path relative to project root
            base_dir = Path(__file__).parent.parent.parent
            data_path = base_dir / "data" / "mock_hospitals.json"
            
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading mock hospitals: {e}")
            return []

    async def process(self, input_data: CareCoordinationInput) -> CareCoordinationOutput:
        """
        Score all nearby hospitals and pick the best match.
        """
        if not self.hospitals:
            return CareCoordinationOutput(
                explanation="No hospital data available in the system."
            )

        # Default location to Patna if missing
        lat = input_data.patient_location.get("lat", 25.61)
        lng = input_data.patient_location.get("lng", 85.14)
        
        is_critical = (input_data.urgency == "critical")

        # 1. Rank hospitals using the Scoring Service
        ranked_list = rank_hospitals(
            hospitals=self.hospitals,
            patient_lat=lat,
            patient_lng=lng,
            required_specialization=input_data.required_specialization,
            is_critical=is_critical,
        )

        if not ranked_list:
            return CareCoordinationOutput(
                explanation="No suitable hospitals found within range."
            )

        # Convert dictionaries back to HospitalScore models
        all_scores = [HospitalScore(**h) for h in ranked_list]
        top_hospital = all_scores[0]

        # 2. Ambulance dispatch logic
        ambulance_dispatched = False
        ambulance_eta = None
        if input_data.urgency in ("critical", "urgent"):
            ambulance_dispatched = True
            # Rough ETA calculation: Ambulance gets there in half the ETA time 
            # (as it only needs to travel one way to patient first, but we simulate it)
            ambulance_eta = max(5, int(top_hospital.eta_minutes * 0.6))

        # 3. Generate human-readable explanation
        explanation = self._generate_explanation(top_hospital, is_critical, ambulance_dispatched)

        return CareCoordinationOutput(
            recommended_hospital=top_hospital,
            all_scores=all_scores,
            ambulance_dispatched=ambulance_dispatched,
            ambulance_eta_minutes=ambulance_eta,
            explanation=explanation,
            confidence=0.9,
            reasons=top_hospital.reasons
        )

    def _generate_explanation(self, top_hospital: HospitalScore, is_critical: bool, ambulance_dispatched: bool) -> str:
        """Generate a clear, human-readable summary for the dashboard/user."""
        reasons_text = ", ".join([r.strip("✔✘ ") for r in top_hospital.reasons if "✔" in r])
        
        text = f"{top_hospital.hospital_name} is the best match with a score of {top_hospital.total_score:.1f}/100. "
        if reasons_text:
            text += f"Selected because: {reasons_text.lower()}. "
            
        if ambulance_dispatched:
            text += f"Ambulance dispatched (ETA ~{top_hospital.eta_minutes} mins)."
        else:
            text += "Please proceed to this facility."
            
        return text
