"""
Clinical Triage Agent
======================
Classifies urgency as Critical / Urgent / Routine, attaches a confidence
score, and always explains its reasoning. 

IMPORTANT: Never names a disease or diagnoses — urgency classification only.

Owner: Frontend Dev
"""

from typing import Optional
from pydantic import BaseModel
from backend.services.llm_service import llm_service


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class TriageInput(BaseModel):
    """Structured data from the Intake Agent."""
    symptoms: list[str] = []
    duration: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class TriageOutput(BaseModel):
    """Triage classification result."""
    urgency: str = "routine"            # "critical", "urgent", "routine"
    confidence: float = 0.0            # 0.0 to 1.0
    reasons: list[str] = []            # ["chest pain detected", "breathing difficulty"]
    home_care_advice: Optional[str] = None  # Only for routine cases
    needs_hospital: bool = False       # True for critical/urgent
    recommended_specialization: Optional[str] = None  # e.g. "cardiology"


# ---------------------------------------------------------------------------
# Critical Symptom Keywords (Rule-based fallback)
# ---------------------------------------------------------------------------

CRITICAL_KEYWORDS = {
    "chest pain": "cardiology",
    "breathing difficulty": "pulmonology",
    "cannot breathe": "pulmonology",
    "unconscious": "emergency",
    "loss of consciousness": "emergency",
    "seizure": "neurology",
    "severe bleeding": "surgery",
    "heart attack": "cardiology",
    "heart failure": "cardiology",
    "stroke": "neurology",
    "choking": "emergency",
    "not breathing": "emergency",
    "severe burn": "surgery",
    "poisoning": "emergency",
    "snake bite": "emergency",
    "snakebite": "emergency",
    "electric shock": "emergency",
    "head injury": "neurology",
    "drowning": "emergency",
    "vomiting blood": "gastroenterology",
    "severe trauma": "emergency",
}

URGENT_KEYWORDS = {
    "high fever": "general_medicine",
    "dengue": "general_medicine",
    "malaria": "general_medicine",
    "fracture": "orthopedics",
    "deep wound": "surgery",
    "severe headache": "neurology",
    "fainting": "general_medicine",
    "allergic reaction": "general_medicine",
    "dehydration": "general_medicine",
    "persistent vomiting": "gastroenterology",
    "abdominal pain": "gastroenterology",
    "bleeding": "surgery",
    "dizziness": "general_medicine",
    "burn": "surgery",
    "dog bite": "emergency",
}

HOME_CARE_ADVICE = {
    "fever": "Rest well, stay hydrated (drink plenty of water, ORS). Apply a damp cloth on the forehead. If fever persists beyond 3 days or goes above 103°F, visit a doctor immediately.",
    "headache": "Rest in a quiet, dark room. Stay hydrated. If headache is severe, sudden, or persists beyond 24 hours, see a doctor.",
    "cough": "Stay hydrated, use steam inhalation. Avoid cold drinks. If cough persists beyond a week or you cough blood, see a doctor.",
    "body pain": "Rest and stay hydrated. Light stretching may help. If pain is severe or persists beyond 3 days, consult a doctor.",
    "weakness": "Eat nutritious food, stay hydrated, get adequate rest. If weakness persists or worsens, see a doctor.",
    "rash": "Keep the area clean and dry. Avoid scratching. If rash spreads rapidly or is accompanied by fever, see a doctor.",
    "diarrhea": "Drink ORS solution frequently. Eat light food (khichdi, bananas). If diarrhea persists beyond 2 days or contains blood, see a doctor immediately.",
    "general discomfort": "Rest well, stay hydrated, and eat nutritious food. If symptoms worsen or new symptoms appear, please see a doctor.",
}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class TriageAgent:
    """
    Clinical Triage Agent — classifies urgency and provides reasoning.
    
    Strategy (as per README):
    1. First, use rule-based keyword matching as a reliable baseline
    2. Then, optionally use LLM for more nuanced understanding
    3. The output contract stays the same either way
    """

    def __init__(self):
        self.llm = llm_service

    async def process(self, input_data: TriageInput) -> TriageOutput:
        """
        Classify urgency of the patient's condition.
        """
        # Step 1: Rule-based triage (fast, reliable)
        urgency, confidence, reasons, specialization = self._rule_based_triage(input_data.symptoms)

        # Step 2: Adjust for age (elderly and children are higher risk)
        if input_data.age:
            if input_data.age < 5 or input_data.age > 70:
                if urgency == "routine":
                    urgency = "urgent"
                    confidence = max(confidence, 0.75)
                    reasons.append(f"Age factor: {'child under 5' if input_data.age < 5 else 'elderly patient'} — elevated risk")
                elif urgency == "urgent":
                    confidence = min(confidence + 0.1, 1.0)
                    reasons.append(f"Age factor increases urgency confidence")

        # Step 3: LLM enhancement (if available and symptoms are ambiguous)
        if self.llm.client and confidence < 0.7 and len(input_data.symptoms) > 0:
            llm_urgency, llm_confidence, llm_reasons, llm_spec = await self._llm_enhanced_triage(input_data)
            if llm_confidence > confidence:
                urgency = llm_urgency
                confidence = llm_confidence
                reasons = llm_reasons
                if llm_spec:
                    specialization = llm_spec

        # Step 4: Generate home-care advice for routine cases
        home_care = None
        needs_hospital = urgency in ("critical", "urgent")
        
        if urgency == "routine":
            home_care = self._generate_home_care(input_data.symptoms)

        return TriageOutput(
            urgency=urgency,
            confidence=round(confidence, 2),
            reasons=reasons,
            home_care_advice=home_care,
            needs_hospital=needs_hospital,
            recommended_specialization=specialization,
        )

    def _rule_based_triage(self, symptoms: list[str]) -> tuple[str, float, list[str], Optional[str]]:
        """
        Rule-based triage using keyword matching.
        Returns: (urgency, confidence, reasons, specialization)
        """
        symptoms_lower = [s.lower() for s in symptoms]
        reasons = []
        specialization = None

        # Check for critical symptoms
        for symptom in symptoms_lower:
            for keyword, spec in CRITICAL_KEYWORDS.items():
                if keyword in symptom:
                    reasons.append(f"Critical symptom detected: {symptom}")
                    specialization = spec
                    # Multiple critical symptoms = higher confidence
                    critical_count = sum(1 for s in symptoms_lower 
                                       for k in CRITICAL_KEYWORDS if k in s)
                    confidence = min(0.85 + (critical_count - 1) * 0.05, 0.98)
                    return "critical", confidence, reasons, specialization

        # Check for urgent symptoms
        for symptom in symptoms_lower:
            for keyword, spec in URGENT_KEYWORDS.items():
                if keyword in symptom:
                    reasons.append(f"Urgent symptom detected: {symptom}")
                    if not specialization:
                        specialization = spec
        
        if reasons:
            urgent_count = len(reasons)
            confidence = min(0.70 + (urgent_count - 1) * 0.05, 0.90)
            return "urgent", confidence, reasons, specialization

        # Default: routine
        reasons.append("No critical or urgent symptoms detected")
        if symptoms_lower and symptoms_lower != ["unknown"]:
            reasons.append(f"Reported symptoms: {', '.join(symptoms)}")
        # CRITICAL FIX: Set confidence to 0.40 so that _llm_enhanced_triage is triggered for unmatched symptoms!
        return "routine", 0.40, reasons, "general_medicine"

    async def _llm_enhanced_triage(self, input_data: TriageInput) -> tuple[str, float, list[str], Optional[str]]:
        """
        LLM-enhanced triage for more nuanced understanding.
        """
        system_prompt = """You are a medical urgency classifier. You NEVER diagnose diseases.
You classify urgency ONLY as: "critical", "urgent", or "routine".

Return JSON:
{
    "urgency": "critical|urgent|routine",
    "confidence": 0.0-1.0,
    "reasons": ["reason1", "reason2"],
    "specialization": "cardiology|neurology|general_medicine|..."
}

Rules:
- Chest pain + breathing issues = CRITICAL
- High fever for 3+ days = URGENT
- Mild symptoms with short duration = ROUTINE
- Never suggest medicine names or dosages"""

        prompt = f"""Patient symptoms: {input_data.symptoms}
Duration: {input_data.duration or 'not specified'}
Age: {input_data.age or 'not specified'}
Gender: {input_data.gender or 'not specified'}"""

        data = await self.llm.generate_json(prompt, system_prompt)
        
        if data and "urgency" in data:
            return (
                data["urgency"],
                data.get("confidence", 0.7),
                data.get("reasons", ["LLM classification"]),
                data.get("specialization"),
            )
        
        return "routine", 0.5, ["Unable to classify with LLM"], "general_medicine"

    def _generate_home_care(self, symptoms: list[str]) -> str:
        """Generate safe home-care advice for routine cases."""
        advice_parts = []
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for key, advice in HOME_CARE_ADVICE.items():
                if key in symptom_lower:
                    advice_parts.append(advice)
                    break
        
        if not advice_parts:
            advice_parts.append(HOME_CARE_ADVICE["general discomfort"])
        
        return " ".join(advice_parts)
