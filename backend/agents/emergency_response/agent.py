"""
Emergency Response Agent
=========================
Watches incoming case volume per region in real time. When a hospital is 
trending toward overload, it PROACTIVELY redirects new incoming cases to 
nearby hospitals with capacity, BEFORE the overload actually happens.

Owner: Backend Dev
"""

from typing import Optional
from pydantic import BaseModel
from pathlib import Path
import json


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class EmergencyInput(BaseModel):
    """Current system state for emergency monitoring."""
    hospital_statuses: list[dict] = []  # [{id, name, occupied_beds, total_beds, incoming_cases_last_hour}]
    active_cases_by_region: dict = {}   # {"region_name": case_count}
    disaster_event: Optional[dict] = None  # {"type": "flood", "region": "...", "severity": "high"}


class RedistributionAction(BaseModel):
    """A single redistribution decision."""
    from_hospital_id: str
    from_hospital_name: str
    to_hospital_id: str
    to_hospital_name: str
    reason: str
    cases_to_redirect: int


class EmergencyOutput(BaseModel):
    """Emergency response decisions."""
    alert_level: str = "normal"        # "normal", "elevated", "critical"
    overloading_hospitals: list[dict] = []  # Hospitals trending toward overload
    redistributions: list[RedistributionAction] = []
    reasons: list[str] = []
    dashboard_message: str = ""


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class EmergencyResponseAgent:
    """
    Emergency Response Agent — predictive redistribution.
    """

    def __init__(self):
        self.warning_threshold = 0.80   # 80% capacity triggers a warning
        self.redirect_threshold = 0.90  # 90% capacity triggers redistribution

    def _load_hospitals(self) -> list[dict]:
        """Load hospital data from mock JSON file."""
        try:
            base_dir = Path(__file__).parent.parent.parent
            data_path = base_dir / "data" / "mock_hospitals.json"
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    async def monitor(self, input_data: EmergencyInput) -> EmergencyOutput:
        """
        Monitor hospital loads and trigger redistributions.
        """
        hospitals = input_data.hospital_statuses
        if not hospitals:
            hospitals = self._load_hospitals()

        alert_level = "normal"
        overloading = []
        redistributions = []
        reasons = []

        # 1. Identify overloaded hospitals
        safe_hospitals = []
        for hosp in hospitals:
            # Check occupancy
            total = hosp.get("total_beds", 100)
            occupied = hosp.get("occupied_beds", 0)
            incoming = hosp.get("incoming_cases_last_hour", 0)
            
            occupancy_pct = occupied / total if total > 0 else 1.0
            
            # Predictive trend (assuming incoming cases consume beds)
            predicted_occupancy = (occupied + incoming) / total if total > 0 else 1.0

            if predicted_occupancy >= self.redirect_threshold:
                overloading.append(hosp)
                reasons.append(f"CRITICAL: {hosp['name']} is trending to >90% capacity (currently {occupancy_pct*100:.0f}%, {incoming} incoming)")
                alert_level = "critical"
            elif occupancy_pct >= self.warning_threshold:
                reasons.append(f"WARNING: {hosp['name']} is at {occupancy_pct*100:.0f}% capacity")
                if alert_level == "normal":
                    alert_level = "elevated"
            else:
                safe_hospitals.append(hosp)

        # 2. Trigger redistributions if critical
        if overloading and safe_hospitals:
            # Sort safe hospitals by most available beds
            safe_hospitals.sort(
                key=lambda x: (x.get("total_beds", 100) - x.get("occupied_beds", 0)), 
                reverse=True
            )
            
            for overload_hosp in overloading:
                # Decide how many cases to redirect to bring it below 90%
                total = overload_hosp.get("total_beds", 100)
                occupied = overload_hosp.get("occupied_beds", 0)
                incoming = overload_hosp.get("incoming_cases_last_hour", 5)
                
                target_beds = int(total * self.warning_threshold) # Aim to bring down to 80%
                excess_cases = max(0, (occupied + incoming) - target_beds)
                
                if excess_cases > 0:
                    cases_left = excess_cases
                    for safe in safe_hospitals:
                        if cases_left <= 0:
                            break
                        
                        safe_total = safe.get("total_beds", 100)
                        safe_occupied = safe.get("occupied_beds", 0)
                        safe_avail = max(0, safe_total - safe_occupied - int(safe_total * 0.1)) # Keep 10% buffer
                        
                        if safe_avail > 0:
                            redirect_amount = min(cases_left, safe_avail)
                            redistributions.append(RedistributionAction(
                                from_hospital_id=overload_hosp["id"],
                                from_hospital_name=overload_hosp["name"],
                                to_hospital_id=safe["id"],
                                to_hospital_name=safe["name"],
                                reason=f"Preventing overload at {overload_hosp['name']}",
                                cases_to_redirect=redirect_amount
                            ))
                            cases_left -= redirect_amount
                            safe["occupied_beds"] = safe_occupied + redirect_amount

        # 3. Handle disaster surge override
        if input_data.disaster_event:
            alert_level = "critical"
            d_type = input_data.disaster_event.get("type", "unknown event")
            d_region = input_data.disaster_event.get("region", "unknown region")
            reasons.insert(0, f"SURGE PROTOCOL ACTIVATED: {d_type.upper()} in {d_region}")

        # 4. Generate dashboard message
        msg = f"System Status: {alert_level.upper()}."
        if redistributions:
            msg += f" {len(redistributions)} active redirection protocols in effect to balance load."
        elif overloading:
            msg += " Hospitals nearing capacity, monitoring closely."
        else:
            msg += " All hospital loads are balanced."

        return EmergencyOutput(
            alert_level=alert_level,
            overloading_hospitals=overloading,
            redistributions=redistributions,
            reasons=reasons,
            dashboard_message=msg,
        )

    async def simulate_disaster(self, disaster_type: str, region: str, case_count: int) -> EmergencyOutput:
        """
        Simulate a disaster event for demo purposes.
        Generates N cases and shows the redistribution response.
        """
        hospitals = self._load_hospitals()
        if not hospitals:
            return EmergencyOutput(dashboard_message="No hospital data for simulation.")
            
        # Simulate surge at nearest hospital (Hospital ID 1 for demo purposes)
        hospitals[0]["incoming_cases_last_hour"] = case_count
        
        input_data = EmergencyInput(
            hospital_statuses=hospitals,
            disaster_event={"type": disaster_type, "region": region, "severity": "critical"}
        )
        
        return await self.monitor(input_data)
