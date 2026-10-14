# Emergency Response Agent

**Owner:** Backend Dev

## Responsibility
Watches incoming case volume per region in real time. When a hospital is trending toward overload, it **proactively** redirects new incoming cases to nearby hospitals with capacity, **before** the overload actually happens.

## Key Thresholds
- **80% occupancy** → Warning alert on dashboard
- **90% occupancy** → Active redistribution begins

## Input Contract
```json
{
  "hospital_statuses": [
    {
      "id": 1,
      "name": "District Hospital A",
      "occupied_beds": 85,
      "total_beds": 100,
      "incoming_cases_last_hour": 12
    }
  ],
  "active_cases_by_region": {
    "Patna East": 45,
    "Patna West": 12
  },
  "disaster_event": {
    "type": "flood",
    "region": "Patna East",
    "severity": "high"
  }
}
```

## Output Contract
```json
{
  "alert_level": "critical",
  "overloading_hospitals": [
    {"id": 1, "name": "District Hospital A", "occupancy_pct": 85, "predicted_full_in_minutes": 45}
  ],
  "redistributions": [
    {
      "from_hospital_id": 1,
      "from_hospital_name": "District Hospital A",
      "to_hospital_id": 2,
      "to_hospital_name": "City Medical Center",
      "reason": "Hospital A at 85% and trending up — redirecting to Hospital B at 40%",
      "cases_to_redirect": 8
    }
  ],
  "reasons": ["Hospital A trending to full capacity in ~45 min"],
  "dashboard_message": "⚠️ OVERLOAD WARNING — ..."
}
```

## Downstream Consumers
- **Dashboard** — live redistribution visualization on map
- **Community Response Agent** — triggered during disaster events
- **Care Coordination Agent** — updated routing priorities
