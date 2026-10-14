"""
Ambulance Dispatch Agent
=========================
Identifies the nearest available ambulance to the patient's location and calculates ETA
to the scene and then to the target hospital.

Owner: Backend Dev
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.services.maps_service import get_distance_and_eta
from backend.core.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class AmbulanceInput(BaseModel):
    """Input for ambulance dispatch."""
    patient_lat: float
    patient_lng: float
    target_hospital_id: str
    target_hospital_name: str
    target_hospital_lat: float
    target_hospital_lng: float
    urgency: str = "urgent"


class AmbulanceDetails(BaseModel):
    id: str
    vehicle_no: str
    type: str  # "ALS", "BLS"
    current_lat: float
    current_lng: float


class AmbulanceOutput(BaseModel):
    """Dispatch decision output."""
    dispatched: bool = False
    ambulance: Optional[AmbulanceDetails] = None
    eta_to_patient_mins: Optional[int] = None
    eta_to_hospital_mins: Optional[int] = None
    total_eta_mins: Optional[int] = None
    status_message: str = ""
    confidence: float = 0.95
    reasons: list[str] = []


# ---------------------------------------------------------------------------
# Mock Data (In real life, this would come from a tracking DB)
# ---------------------------------------------------------------------------
MOCK_AMBULANCES = [
    {"id": "amb_001", "vehicle_no": "BR-01-AB-1234", "type": "ALS", "lat": 25.6000, "lng": 85.1200, "status": "available"},
    {"id": "amb_002", "vehicle_no": "BR-01-XY-9876", "type": "BLS", "lat": 25.6200, "lng": 85.1500, "status": "available"},
    {"id": "amb_003", "vehicle_no": "BR-01-PQ-4567", "type": "ALS", "lat": 25.5900, "lng": 85.1350, "status": "available"},
]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class AmbulanceAgent:
    """
    Ambulance Dispatch Agent — locates nearest ambulance and calculates routing ETAs.
    """

    def __init__(self):
        pass

    async def dispatch(self, input_data: AmbulanceInput) -> AmbulanceOutput:
        """
        Find the nearest available ambulance, calculate ETA to patient, and then ETA to hospital.
        Prefers ALS for critical cases and nearest for urgent cases.
        """
        if input_data.urgency == "routine":
            return AmbulanceOutput(
                dispatched=False,
                status_message="Ambulance not required for routine cases. Please arrange personal transport.",
                confidence=1.0,
                reasons=["Case urgency is routine"]
            )

        candidates = []

        for amb in MOCK_AMBULANCES:
            if amb["status"] != "available":
                continue

            _, eta = get_distance_and_eta(
                amb["lat"], amb["lng"],
                input_data.patient_lat, input_data.patient_lng
            )

            # Scoring: lower is better
            # Base score is ETA
            score = eta

            # For critical cases, strongly prefer ALS ambulances
            if input_data.urgency == "critical":
                if amb["type"] == "BLS":
                    score += 15  # Heavy penalty for BLS in critical
                else:
                    score -= 5   # Bonus for ALS in critical
            
            candidates.append({"amb": amb, "eta": eta, "score": score})

        if not candidates:
            return AmbulanceOutput(
                dispatched=False,
                status_message="No ambulances currently available in your area. Proceed to hospital immediately.",
                confidence=1.0,
                reasons=["No ambulances available in mock list"]
            )

        # Select the best candidate by score
        candidates.sort(key=lambda c: c["score"])
        best = candidates[0]
        best_amb = best["amb"]
        shortest_eta_to_patient = best["eta"]

        # Calculate ETA from patient to hospital
        _, eta_to_hospital = get_distance_and_eta(
            input_data.patient_lat, input_data.patient_lng,
            input_data.target_hospital_lat, input_data.target_hospital_lng
        )

        on_scene_time = 5  # minutes
        total_eta = shortest_eta_to_patient + on_scene_time + eta_to_hospital

        # Build rationale
        rationale = (
            f"Selected {best_amb['type']} ambulance {best_amb['vehicle_no']} "
            f"because it is the {'nearest ALS unit' if best_amb['type'] == 'ALS' else 'nearest available unit'} "
            f"with an ETA of ~{shortest_eta_to_patient} min to the patient. "
            f"Total transport time to {input_data.target_hospital_name}: ~{total_eta} min."
        )

        return AmbulanceOutput(
            dispatched=True,
            ambulance=AmbulanceDetails(
                id=best_amb["id"],
                vehicle_no=best_amb["vehicle_no"],
                type=best_amb["type"],
                current_lat=best_amb["lat"],
                current_lng=best_amb["lng"]
            ),
            eta_to_patient_mins=shortest_eta_to_patient,
            eta_to_hospital_mins=eta_to_hospital,
            total_eta_mins=total_eta,
            status_message=f"Ambulance {best_amb['vehicle_no']} ({best_amb['type']}) dispatched. ETA: ~{shortest_eta_to_patient} min. {rationale}",
            confidence=0.9,
            reasons=[rationale]
        )

