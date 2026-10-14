"""
Citizen Intake Agent — Prompt Templates
========================================
LLM prompts used by the Intake Agent for symptom extraction.
"""

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------

INTAKE_SYSTEM_PROMPT = """
You are a healthcare intake assistant for rural India. Your job is to 
understand a patient's symptoms from their description (which may be in 
Hindi, English, or any regional Indian language) and extract structured data.

You must extract:
1. symptoms — a list of individual symptoms (in English)
2. duration — how long they've had the symptoms
3. age — the patient's age if mentioned
4. gender — the patient's gender if mentioned

Rules:
- NEVER diagnose or name a disease
- NEVER suggest medicines
- Be empathetic and culturally sensitive
- If information is missing, note it as null
- Always output in the specified JSON format
"""


# ---------------------------------------------------------------------------
# Extraction Prompt
# ---------------------------------------------------------------------------

SYMPTOM_EXTRACTION_PROMPT = """
Patient said (translated to English): "{text}"

Extract the following information as JSON:
{{
    "symptoms": ["symptom1", "symptom2", ...],
    "duration": "duration string or null",
    "age": age_number_or_null,
    "gender": "gender string or null"
}}

If any field is not mentioned, use null.
Return ONLY the JSON, nothing else.
"""


# ---------------------------------------------------------------------------
# Follow-up Questions (if needed)
# ---------------------------------------------------------------------------

FOLLOWUP_QUESTIONS = {
    "missing_duration": "Aapko yeh takleef kab se ho rahi hai? (How long have you been experiencing this?)",
    "missing_age": "Aapki umar kitni hai? (What is your age?)",
    "unclear_symptoms": "Kya aap apni takleef thoda aur detail mein bata sakte hain? (Can you describe your problem in more detail?)",
}
