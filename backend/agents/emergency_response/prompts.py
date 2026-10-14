"""
Emergency Response Agent — Prompt Templates
=============================================
Templates for dashboard alerts and redistribution notifications.
"""

OVERLOAD_WARNING_TEMPLATE = """
⚠️ OVERLOAD WARNING — {hospital_name}
Current occupancy: {occupancy_pct}% ({occupied}/{total} beds)
Incoming cases (last hour): {incoming_count}
Predicted time to full capacity: {time_to_full} minutes

Action: New cases in this region will be redirected to nearby hospitals.
"""

REDISTRIBUTION_ALERT_TEMPLATE = """
🔄 REDISTRIBUTION ACTIVE
{from_hospital} → {to_hospital}
Reason: {reason}
Cases redirected: {case_count}
{to_hospital} current capacity: {to_occupancy}%
"""

DISASTER_ALERT_TEMPLATE = """
🚨 DISASTER EVENT — {disaster_type} in {region}
Severity: {severity}
Estimated cases: {estimated_cases}
Hospitals in affected area: {hospital_count}

Surge Protocol:
- All non-critical cases being redirected
- Community Response Agent activated
- Emergency capacity being assessed
"""
