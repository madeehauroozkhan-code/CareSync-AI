"""
Follow-up & Recovery Agent
============================
24 hours after referral, checks in with the patient (WhatsApp/SMS):
Did they reach the facility? Did they recover? Do they need another visit?
Closes the full patient lifecycle.

Owner: Frontend Dev
Tier: 2 (simplified version — basic timer-triggered check-in)
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from backend.services.sms_service import send_message

# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class FollowupInput(BaseModel):
    """Case data for scheduling follow-up."""
    case_id: str
    patient_phone: Optional[str] = None
    patient_name: Optional[str] = None
    hospital_name: Optional[str] = None
    urgency: str = "routine"
    referred_at: Optional[datetime] = None
    followup_delay_hours: int = 24     # Default: follow up after 24 hours


class FollowupCheckResult(BaseModel):
    """Result of a follow-up check-in."""
    case_id: str
    reached_facility: Optional[bool] = None
    received_treatment: Optional[bool] = None
    current_condition: Optional[str] = None  # "better", "same", "worse"
    needs_another_visit: bool = False
    patient_response_raw: Optional[str] = None


class FollowupOutput(BaseModel):
    """Follow-up scheduling/execution result."""
    case_id: str
    followup_scheduled: bool = False
    scheduled_at: Optional[datetime] = None
    message_sent: bool = False
    channel: str = ""                  # "whatsapp", "sms"
    check_result: Optional[FollowupCheckResult] = None
    reasons: list[str] = []


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class FollowupAgent:
    """
    Follow-up & Recovery Agent — closes the patient lifecycle loop.
    
    For the demo: schedules a timer and sends a simulated follow-up
    message. In production, this would integrate with WhatsApp Business API.
    """

    def __init__(self):
        pass

    async def schedule_followup(self, input_data: FollowupInput) -> FollowupOutput:
        """
        Schedule a follow-up check-in for a patient.
        """
        if not input_data.patient_phone:
            return FollowupOutput(
                case_id=input_data.case_id,
                followup_scheduled=False,
                reasons=["No patient phone number provided."]
            )

        referred_at = input_data.referred_at or datetime.utcnow()
        scheduled_at = referred_at + timedelta(hours=input_data.followup_delay_hours)
        
        # In a real system, we would insert a job into Celery or Redis here.
        # For this implementation, we log the scheduled time.

        return FollowupOutput(
            case_id=input_data.case_id,
            followup_scheduled=True,
            scheduled_at=scheduled_at,
            reasons=[f"Follow-up scheduled for {scheduled_at.isoformat()}"]
        )

    async def execute_followup(self, input_data: FollowupInput) -> FollowupOutput:
        """
        Execute the actual follow-up check-in immediately.
        """
        if not input_data.patient_phone:
            return FollowupOutput(
                case_id=input_data.case_id,
                message_sent=False,
                reasons=["Missing patient phone number for check-in."]
            )

        name = input_data.patient_name or "Patient"
        hosp = input_data.hospital_name or "the healthcare facility"

        sent = await self._send_checkin_message(
            phone=input_data.patient_phone,
            patient_name=name,
            hospital_name=hosp
        )

        return FollowupOutput(
            case_id=input_data.case_id,
            message_sent=sent,
            channel="whatsapp",
            reasons=[f"Check-in message sent to {name} regarding {hosp} visit."] if sent else ["Failed to send check-in message."]
        )

    async def _send_checkin_message(self, phone: str, patient_name: str, hospital_name: str) -> bool:
        """Send the follow-up check-in message."""
        message = (
            f"Hello {patient_name}, this is AI Sahayak checking in. "
            f"Were you able to receive care at {hospital_name}? "
            f"Please reply YES if you were treated, or NO if you need further assistance."
        )
        
        result = send_message(phone, message, channel="whatsapp")
        return result.get("status") in ["sent", "simulated"]

    def _parse_patient_response(self, case_id: str, response: str) -> FollowupCheckResult:
        """Parse the patient's response to the check-in."""
        resp_lower = response.lower()
        
        needs_visit = False
        reached = True
        condition = "unknown"
        
        if "no" in resp_lower or "didn't" in resp_lower or "did not" in resp_lower:
            reached = False
            needs_visit = True
        
        if "worse" in resp_lower or "pain" in resp_lower:
            condition = "worse"
            needs_visit = True
        elif "better" in resp_lower or "good" in resp_lower or "okay" in resp_lower:
            condition = "better"

        return FollowupCheckResult(
            case_id=case_id,
            reached_facility=reached,
            received_treatment=reached,
            current_condition=condition,
            needs_another_visit=needs_visit,
            patient_response_raw=response
        )
