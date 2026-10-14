"""
Public Health Intelligence Agent — Prompt Templates
=====================================================
Templates for outbreak alerts and recommendations.
"""

OUTBREAK_ALERT_TEMPLATE = """
🟠 POSSIBLE OUTBREAK DETECTED
Region: {region}
Dominant symptoms: {symptoms}
Cases detected: {case_count} in {time_span} hours
Confidence: {confidence}%

Predicted next-affected: {predicted_regions}

Recommended actions:
{actions}
"""

RISK_LEVEL_DESCRIPTIONS = {
    "safe": "🟢 Safe — No significant symptom clusters detected",
    "medium": "🟡 Medium — Small cluster detected, monitoring needed",
    "high": "🟠 High — Significant cluster, active measures recommended",
    "critical": "🔴 Critical — Large outbreak, immediate intervention required",
}

RECOMMENDATION_TEMPLATES = {
    "fever_cluster": [
        "Increase testing/diagnostic supply stock in {region}",
        "Deploy mobile diagnostic clinic to {region}",
        "Alert PHCs in surrounding villages",
        "Begin door-to-door symptom screening",
    ],
    "respiratory_cluster": [
        "Distribute masks and sanitizers in {region}",
        "Set up temporary isolation facility",
        "Alert district health officer",
        "Begin contact tracing in {region}",
    ],
    "waterborne_cluster": [
        "Test water sources in {region}",
        "Distribute ORS and clean water supplies",
        "Deploy water purification units",
        "Issue public advisory on water safety",
    ],
    "default": [
        "Increase monitoring in {region}",
        "Alert local healthcare facilities",
        "Prepare additional medical supplies",
        "Coordinate with district health authorities",
    ],
}
