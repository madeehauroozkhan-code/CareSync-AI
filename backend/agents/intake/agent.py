"""
Citizen Intake Agent
=====================
Understands symptoms via voice/text in any language; converts free-form 
conversation into structured data (symptoms, duration, age, location).

Owner: Frontend Dev
"""

from typing import Optional
from pydantic import BaseModel
from backend.services.llm_service import llm_service


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class IntakeInput(BaseModel):
    """Raw input from the citizen."""
    text: Optional[str] = None          # Text input (may be in any language)
    audio_base64: Optional[str] = None  # Base64-encoded audio for voice input
    language: str = "hi"                # ISO language code (default: Hindi)
    latitude: Optional[float] = None    # User's GPS location
    longitude: Optional[float] = None


class IntakeOutput(BaseModel):
    """Structured data extracted from the citizen's input."""
    symptoms: list[str] = []            # ["chest pain", "breathing difficulty"]
    duration: Optional[str] = None      # "30 minutes", "2 days"
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[dict] = None     # {"lat": 25.594, "lng": 85.137}
    raw_text_translated: Optional[str] = None  # Translated to English
    confidence: float = 0.0            # How confident the extraction is (0-1)
    reasons: list[str] = []            # Extraction rationale


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class IntakeAgent:
    """
    Citizen Intake Agent — converts free-form voice/text input into
    structured symptom data for downstream agents.
    """

    def __init__(self):
        self.llm = llm_service

    async def process(self, input_data: IntakeInput) -> IntakeOutput:
        """
        Process citizen input and extract structured data.
        """
        text = input_data.text or ""
        
        if not text:
            return IntakeOutput(
                symptoms=["unknown"],
                confidence=0.0,
                location={"lat": input_data.latitude, "lng": input_data.longitude}
                    if input_data.latitude else None,
            )

        # Step 1: Translate if not English
        translated = text
        if input_data.language != "en" and self.llm.client:
            translated = await self.llm.translate(text, input_data.language, "en")
        
        # Step 2: Use LLM to extract structured data
        if self.llm.client:
            result = await self._llm_extract(translated, text)
        else:
            result = self._keyword_extract(translated)

        # Step 3: Attach location
        if input_data.latitude and input_data.longitude:
            result.location = {"lat": input_data.latitude, "lng": input_data.longitude}
        
        result.raw_text_translated = translated
        return result

    async def _llm_extract(self, translated_text: str, original_text: str) -> IntakeOutput:
        """Use LLM to extract structured symptom data."""
        system_prompt = """You are a medical intake system. Extract structured data from the patient's description.
Return a JSON object with these fields:
- symptoms: list of symptom strings in English (e.g. ["chest pain", "breathing difficulty"])
- duration: how long the symptoms have lasted (e.g. "2 days", "30 minutes")
- age: patient's age as integer if mentioned, null otherwise
- gender: patient's gender if mentioned, null otherwise
- confidence: float 0-1 indicating how confident you are in the extraction

IMPORTANT: Extract symptoms only. Do NOT diagnose or name diseases."""

        prompt = f"Patient says: \"{translated_text}\"\nOriginal: \"{original_text}\""
        
        data = await self.llm.generate_json(prompt, system_prompt)
        
        if data:
            return IntakeOutput(
                symptoms=data.get("symptoms", ["unknown"]),
                duration=data.get("duration"),
                age=data.get("age"),
                gender=data.get("gender"),
                confidence=data.get("confidence", 0.7),
            )
        
        # Fallback to keyword extraction
        return self._keyword_extract(translated_text)

    def _keyword_extract(self, text: str) -> IntakeOutput:
        """Fallback: simple keyword-based symptom extraction."""
        text_lower = text.lower()
        
        symptom_map = {
            "chest pain": ["chest pain", "seene me dard", "chhati me dard", "chest"],
            "breathing difficulty": ["breathing difficulty", "saans", "breath", "breathing problem"],
            "fever": ["fever", "bukhaar", "bukhar", "temperature"],
            "headache": ["headache", "sir dard", "sar dard", "head pain"],
            "vomiting": ["vomiting", "ulti", "vomit"],
            "cough": ["cough", "khansi", "khaansi"],
            "body pain": ["body pain", "badan dard", "body ache"],
            "diarrhea": ["diarrhea", "dast", "loose motion"],
            "abdominal pain": ["abdominal pain", "pet dard", "pet me dard", "stomach pain"],
            "weakness": ["weakness", "kamzori", "weak"],
            "dizziness": ["dizziness", "chakkar", "dizzy"],
            "bleeding": ["bleeding", "khoon", "blood"],
            "fracture": ["fracture", "haddi tooti", "bone broken"],
            "unconscious": ["unconscious", "behosh", "hosh nahi"],
            "seizure": ["seizure", "mirgi", "fits"],
            "burn": ["burn", "jala", "jalaa"],
            "rash": ["rash", "daane", "skin"],
            "swelling": ["swelling", "sujan", "sooj"],
            "severe trauma": ["accident", "durghatna", "ghayal", "injured", "disaster", "mass casualty"],
        }
        
        found_symptoms = []
        for symptom, keywords in symptom_map.items():
            for kw in keywords:
                if kw in text_lower:
                    found_symptoms.append(symptom)
                    break
        
        if not found_symptoms:
            found_symptoms = ["general discomfort"]
        
        # Try to extract duration
        duration = None
        import re
        dur_match = re.search(r'(\d+)\s*(din|day|hour|ghanta|minute|week|hafta|month|mahina)', text_lower)
        if dur_match:
            num = dur_match.group(1)
            unit_map = {"din": "days", "day": "days", "hour": "hours", "ghanta": "hours",
                       "minute": "minutes", "week": "weeks", "hafta": "weeks",
                       "month": "months", "mahina": "months"}
            unit = unit_map.get(dur_match.group(2), dur_match.group(2))
            duration = f"{num} {unit}"

        return IntakeOutput(
            symptoms=found_symptoms,
            duration=duration,
            confidence=0.6,
        )
