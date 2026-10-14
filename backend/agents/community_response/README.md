# Community Response Agent

**Owner:** Backend Dev  
**Tier:** 2 (simplified version for demo)

## Responsibility
During a disaster-scale event, notifies nearby NGO volunteers, blood donors, local drivers/boat owners, and the district officer liaison using a simple location-based matching list.

## Input Contract (from Emergency Response Agent)
```json
{
  "disaster_type": "flood",
  "region": "Patna East",
  "latitude": 25.594,
  "longitude": 85.137,
  "severity": "high",
  "needs": ["blood_donors", "local_driver", "ngo_worker"],
  "radius_km": 25.0
}
```

## Output Contract
```json
{
  "volunteers_notified": [
    {
      "volunteer_id": 1,
      "name": "Rajesh Kumar",
      "volunteer_type": "local_driver",
      "distance_km": 5.2,
      "phone": "+919876543210",
      "notified": true,
      "notification_channel": "whatsapp"
    }
  ],
  "total_notified": 6,
  "notification_summary": "6 volunteers notified (2 drivers, 2 blood donors, 2 NGO workers)",
  "reasons": ["Flood event in Patna East — activating nearby community resources"]
}
```

## Downstream Consumers
- **Dashboard** — shows activated volunteers on the map
