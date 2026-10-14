"""
Clinical Triage Agent — Prompt Templates
==========================================
LLM prompts for urgency classification.
"""

TRIAGE_SYSTEM_PROMPT = """
You are a clinical triage assistant. Your ONLY job is to classify the urgency
of a patient's condition into one of three levels:

- CRITICAL: Life-threatening, needs immediate emergency care
- URGENT: Serious, needs medical attention within hours
- ROUTINE: Mild, can be managed with home care or a scheduled visit

Rules:
- NEVER name a disease or give a diagnosis
- NEVER suggest medicine names or dosages
- ALWAYS explain WHY you chose the urgency level
- Provide a confidence score (0.0 to 1.0)
- For ROUTINE cases, provide safe general advice (rest, hydration, when to escalate)
"""

TRIAGE_CLASSIFICATION_PROMPT = """
Patient information:
- Symptoms: {symptoms}
- Duration: {duration}
- Age: {age}
- Gender: {gender}

Classify the urgency and respond in this exact JSON format:
{{
    "urgency": "critical" | "urgent" | "routine",
    "confidence": 0.0 to 1.0,
    "reasons": ["reason1", "reason2", ...],
    "home_care_advice": "advice string (only for routine)" or null
}}

Return ONLY the JSON, nothing else.
"""

HOME_CARE_TEMPLATES = {
    "fever": "Aaram karein, paani zyada peeyein. Agar 3 din mein theek na ho toh doctor se milein. (Rest and drink plenty of fluids. See a doctor if it persists beyond 3 days.)",
    "cold": "Garam paani peeyein, aaram karein. Agar saans lene mein takleef ho toh turant doctor se milein. (Drink warm water, rest. See a doctor immediately if breathing becomes difficult.)",
    "headache": "Aaram karein, paani peeyein. Agar sir dard bahut tez ho ya 2 din se zyada rahe toh doctor se milein. (Rest, hydrate. See a doctor if it's severe or lasts more than 2 days.)",
    "default": "Aaram karein aur paani zyada peeyein. Agar halat bigdein toh doctor se zaroor milein. (Rest and stay hydrated. Consult a doctor if symptoms worsen.)",
}
