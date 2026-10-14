# Follow-up & Recovery Agent

**Owner:** Frontend Dev  
**Tier:** 2 (simplified — basic timer-triggered check-in)

## Responsibility
24 hours after referral, checks in with the patient (WhatsApp/SMS): Did they reach the facility? Did they recover? Do they need another visit? Closes the full patient lifecycle.

## Input Contract (from Care Coordination Agent)
```json
{
  "case_id": 42,
  "patient_phone": "+919876543210",
  "patient_name": "Ramesh",
  "hospital_name": "City Heart Hospital",
  "urgency": "critical",
  "referred_at": "2025-01-15T10:30:00Z",
  "followup_delay_hours": 24
}
```

## Output Contract
```json
{
  "case_id": 42,
  "followup_scheduled": true,
  "scheduled_at": "2025-01-16T10:30:00Z",
  "message_sent": true,
  "channel": "whatsapp",
  "check_result": {
    "case_id": 42,
    "reached_facility": true,
    "received_treatment": true,
    "current_condition": "better",
    "needs_another_visit": false,
    "patient_response_raw": "THEEK"
  },
  "reasons": ["24-hour follow-up completed — patient reports feeling better"]
}
```

## Downstream Consumers
- **Dashboard** — case lifecycle tracking
- **Triage Agent** — re-triggered if patient condition worsened
