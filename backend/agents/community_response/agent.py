"""
Community Response Agent
=========================
During a disaster-scale event, notifies nearby NGO volunteers, blood donors,
local drivers/boat owners, and the district officer liaison using a simple
location-based matching list.

Owner: Backend Dev
Tier: 2 (simplified version)
"""

from typing import Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class CommunityInput(BaseModel):
    """Trigger from Emergency Response Agent."""
    disaster_type: str = ""            # "flood", "earthquake", "mass_casualty"
    region: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    severity: str = "medium"           # "low", "medium", "high", "critical"
    needs: list[str] = []              # ["blood_donors", "drivers", "medical_volunteers"]
    radius_km: float = 25.0            # How far to search for volunteers


class ActivatedVolunteer(BaseModel):
    """A volunteer that has been notified."""
    volunteer_id: str
    name: str
    volunteer_type: str
    distance_km: float
    phone: Optional[str] = None
    notified: bool = False
    notification_channel: str = ""     # "sms", "whatsapp", "app"


class CommunityOutput(BaseModel):
    """Community response activation results."""
    volunteers_notified: list[ActivatedVolunteer] = []
    total_notified: int = 0
    notification_summary: str = ""
    reasons: list[str] = []


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
import json
from pathlib import Path
import math
from backend.services.sms_service import send_message

class CommunityResponseAgent:
    """
    Community Response Agent — activates community resources during emergencies.
    
    For the hackathon demo, this uses a mock volunteer list. Notifications
    can be real (via Twilio) or simulated (logged to dashboard).
    """

    def __init__(self):
        # Load volunteer data
        self.volunteers = self._load_volunteers()

    def _load_volunteers(self) -> list[dict]:
        try:
            base_dir = Path(__file__).parent.parent.parent
            data_path = base_dir / "data" / "mock_volunteers.json"
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    async def activate(self, input_data: CommunityInput) -> CommunityOutput:
        """
        Activate community resources based on the emergency.
        """
        reasons = []
        if not self.volunteers:
            return CommunityOutput(
                notification_summary="Failed to load volunteer data. No volunteers activated.",
                reasons=["Volunteer database unavailable."]
            )

        # 1. Filter volunteers by type
        type_filtered = self._filter_by_type(self.volunteers, input_data.needs)
        reasons.append(f"Found {len(type_filtered)} volunteers matching needs: {', '.join(input_data.needs) if input_data.needs else 'any'}")

        # 2. Filter volunteers by proximity and calculate distance
        nearby_volunteers = self._filter_by_proximity(
            type_filtered, input_data.latitude, input_data.longitude, input_data.radius_km
        )
        reasons.append(f"Found {len(nearby_volunteers)} volunteers within {input_data.radius_km}km.")

        # 3. Sort by distance
        nearby_volunteers.sort(key=lambda x: x["distance_km"])

        # 4. Notify volunteers
        notified_list = []
        for vol in nearby_volunteers:
            success = await self._send_notification(vol, input_data.model_dump())
            if success:
                notified_list.append(
                    ActivatedVolunteer(
                        volunteer_id=vol["id"],
                        name=vol["name"],
                        volunteer_type=vol["type"],
                        distance_km=vol["distance_km"],
                        phone=vol.get("phone"),
                        notified=True,
                        notification_channel="whatsapp"
                    )
                )

        summary = f"Activated {len(notified_list)} community responders for {input_data.disaster_type}."
        
        return CommunityOutput(
            volunteers_notified=notified_list,
            total_notified=len(notified_list),
            notification_summary=summary,
            reasons=reasons
        )

    def _filter_by_proximity(self, volunteers: list[dict], lat: float, lng: float, radius_km: float) -> list[dict]:
        """Filter volunteers within the specified radius."""
        nearby = []
        for v in volunteers:
            v_lat = v.get("latitude")
            v_lng = v.get("longitude")
            if v_lat is None or v_lng is None:
                continue
                
            dist = self._haversine(lat, lng, v_lat, v_lng)
            if dist <= radius_km:
                v_copy = v.copy()
                v_copy["distance_km"] = round(dist, 2)
                nearby.append(v_copy)
        return nearby

    def _filter_by_type(self, volunteers: list[dict], needs: list[str]) -> list[dict]:
        """Filter volunteers by type matching the emergency needs."""
        if not needs:
            return volunteers
        needs_lower = [n.lower() for n in needs]
        return [v for v in volunteers if v.get("type", "").lower() in needs_lower]

    async def _send_notification(self, volunteer: dict, disaster_info: dict) -> bool:
        """Send notification to a volunteer. Returns True if successful."""
        phone = volunteer.get("phone")
        if not phone:
            return False
            
        disaster_type = disaster_info.get("disaster_type", "emergency")
        region = disaster_info.get("region", "your area")
        
        message = (
            f"URGENT: AI Sahayak Alert.\n"
            f"A {disaster_type} has occurred in {region}.\n"
            f"Your skills ({volunteer.get('type')}) are needed immediately. "
            f"Please respond to coordination center if available."
        )
        
        result = send_message(phone, message, channel="whatsapp")
        return result.get("status") in ["sent", "simulated"]

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on the earth in km."""
        R = 6371.0 # Radius of the earth in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dLon / 2) * math.sin(dLon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
