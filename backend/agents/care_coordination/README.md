# Care Coordination Agent

**Owner:** Backend Dev

## Responsibility
Chooses the best hospital **and** ambulance using a weighted scoring model — not just the nearest one. This is the project's core differentiator.

## Scoring Formula
```
Hospital Score (0-100) =
    (0.25 × Proximity Score)
  + (0.25 × Bed Capacity Score)
  + (0.25 × Specialization Match Score)
  + (0.15 × Wait Time Score)
  + (0.10 × ICU Availability Score)   ← only weighted for Critical cases
```

## Input Contract (from Triage Agent + patient location)
```json
{
  "symptoms": ["chest pain", "breathing difficulty"],
  "urgency": "critical",
  "required_specialization": "cardiology",
  "patient_location": {"lat": 25.594, "lng": 85.137},
  "age": 45
}
```

## Output Contract
```json
{
  "recommended_hospital": {
    "hospital_id": 3,
    "hospital_name": "City Heart Hospital",
    "total_score": 87.5,
    "proximity_score": 70,
    "capacity_score": 90,
    "specialization_score": 100,
    "wait_time_score": 80,
    "icu_score": 95,
    "distance_km": 8.2,
    "eta_minutes": 14,
    "reasons": [
      "Cardiologist available (patient reported chest pain)",
      "ICU beds available (3)",
      "ETA ~14 min"
    ]
  },
  "all_scores": [ ... ],
  "ambulance_dispatched": true,
  "ambulance_eta_minutes": 14,
  "explanation": "Hospital C selected because: ..."
}
```

## Downstream Consumers
- **Frontend** — displays hospital recommendation with explanation
- **Emergency Response Agent** — monitors case volume per hospital
- **Follow-up Agent** — schedules post-referral check-in
