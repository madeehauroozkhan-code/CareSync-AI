# Public Health Intelligence Agent

**Owner:** Backend Dev

## Responsibility
Continuously scans anonymized case data for symptom clusters by location/time. When a cluster crosses a threshold, it predicts the likely next-affected area and recommends specific actions (extra stock, vaccination camp, mobile clinic).

## Input Contract
```json
{
  "cases": [
    {
      "symptoms": ["high fever", "body pain"],
      "region": "Village X",
      "latitude": 25.6,
      "longitude": 85.1,
      "timestamp": "2025-01-15T10:30:00Z",
      "age_group": "30-45"
    }
  ],
  "time_window_hours": 72,
  "cluster_threshold": 10
}
```

## Output Contract
```json
{
  "clusters_detected": [
    {
      "region": "Village X",
      "latitude": 25.6,
      "longitude": 85.1,
      "dominant_symptoms": ["high fever", "body pain"],
      "case_count": 45,
      "time_span_hours": 48,
      "confidence": 0.88,
      "possible_condition": "Possible dengue"
    }
  ],
  "predicted_next_regions": [
    {
      "region": "Village Y",
      "risk_level": "high",
      "reasons": ["15km from Village X", "Connected by water source"]
    }
  ],
  "recommended_actions": [
    "Increase platelet/testing stock in Village X",
    "Deploy mobile clinic to Village X",
    "Alert PHCs in Village Y"
  ],
  "village_risk_map": [
    {"region": "Village X", "lat": 25.6, "lng": 85.1, "risk_level": "critical"},
    {"region": "Village Y", "lat": 25.65, "lng": 85.15, "risk_level": "high"},
    {"region": "Village Z", "lat": 25.55, "lng": 85.05, "risk_level": "safe"}
  ],
  "alert_message": "🟠 Possible dengue cluster in Village X...",
  "reasons": ["45 of 52 recent cases report high fever + body pain"]
}
```

## Downstream Consumers
- **Government Dashboard** — Village Health Risk heatmap
- **Community Response Agent** — may be triggered for severe outbreaks
