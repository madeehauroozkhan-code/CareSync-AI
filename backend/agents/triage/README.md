# Clinical Triage Agent

**Owner:** Frontend Dev

## Responsibility
Classifies urgency as **Critical / Urgent / Routine**, attaches a **confidence score**, and always explains its reasoning. Never names a disease or diagnoses — urgency classification only.

## Input Contract (from Intake Agent)
```json
{
  "symptoms": ["chest pain", "breathing difficulty"],
  "duration": "30 minutes",
  "age": 45,
  "gender": "male"
}
```

## Output Contract
```json
{
  "urgency": "critical",
  "confidence": 0.95,
  "reasons": [
    "Chest pain reported",
    "Breathing difficulty is a red-flag symptom",
    "Age 45+ increases cardiac risk"
  ],
  "home_care_advice": null,
  "needs_hospital": true
}
```

| Field | Type | Description |
|---|---|---|
| urgency | string | "critical", "urgent", or "routine" |
| confidence | float | 0.0 to 1.0 |
| reasons | string[] | Human-readable reasons for the classification |
| home_care_advice | string/null | Safe advice (only for routine cases) |
| needs_hospital | bool | True for critical/urgent |

## Downstream Consumers
- **If critical/urgent →** Care Coordination Agent
- **If routine →** Response shown directly to citizen (home-care advice)
