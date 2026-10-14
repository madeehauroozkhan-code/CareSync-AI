"""
Community Response Agent — Prompt Templates
=============================================
Notification message templates for volunteers.
"""

VOLUNTEER_NOTIFICATION_SMS = """
🚨 AI Sahayak — Emergency Alert
{disaster_type} in {region}

Your help is needed as a {volunteer_type}.
Location: {region} ({distance_km} km from you)

Please respond YES if you can help.
Contact: {emergency_contact}
"""

VOLUNTEER_NOTIFICATION_WHATSAPP = """
🚨 *AI Sahayak — Emergency Alert*

*{disaster_type}* reported in *{region}*
Severity: {severity}

Your skills as a *{volunteer_type}* are needed.
📍 Location: {region} ({distance_km} km away)

Reply *YES* to confirm your availability.
Reply *NO* if you cannot help at this time.

_Thank you for being a community hero!_ 🙏
"""

DISTRICT_OFFICER_ALERT = """
📋 AI Sahayak — District Alert Report

Event: {disaster_type} in {region}
Severity: {severity}
Time: {timestamp}

Community Response:
- Volunteers notified: {total_notified}
- Blood donors: {blood_donors_count}
- Drivers: {drivers_count}
- Medical volunteers: {medical_count}
- NGO workers: {ngo_count}

Hospitals affected: {hospitals_affected}
Redistribution active: {redistribution_active}
"""
