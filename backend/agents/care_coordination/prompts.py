"""
Care Coordination Agent — Prompt Templates
============================================
Prompts for generating human-readable explanations of hospital selection.
"""

CARE_EXPLANATION_PROMPT = """
You are a healthcare coordinator explaining why a specific hospital was 
recommended for a patient.

Patient symptoms: {symptoms}
Urgency: {urgency}

Hospital selected: {hospital_name}
Score: {score}/100

Score breakdown:
- Proximity: {proximity_score} (distance: {distance_km} km, ETA: {eta_minutes} min)
- Bed capacity: {capacity_score} ({available_beds}/{total_beds} beds available)
- Specialization match: {specialization_score}
- Wait time: {wait_time_score} (avg: {avg_wait_minutes} min)
- ICU availability: {icu_score} ({icu_beds} ICU beds free)

Other hospitals considered:
{other_hospitals}

Generate a clear, brief explanation in both English and Hindi for why this 
hospital was chosen over others. Use checkmarks (✔) for strengths and 
crosses (✘) for why others were not selected.

Format:
Hospital [Name] selected because:
✔ [strength 1]
✔ [strength 2]
✘ [why other hospital was not chosen]
"""

AMBULANCE_DISPATCH_MESSAGE = """
🚑 Ambulance dispatched!
- From: {hospital_name}
- To: Patient location ({lat}, {lng})
- Estimated arrival: {eta_minutes} minutes
- Case urgency: {urgency}
"""
