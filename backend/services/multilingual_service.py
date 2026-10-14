"""
multilingual_service.py
-----------------------
Service for handling translation and language detection.
Uses the core LLM service to seamlessly bridge the gap between regional 
languages (Hindi, Hinglish, etc.) and the core English reasoning engine.

Owner: Backend Dev
"""

import json
from typing import Optional
from backend.services.llm_service import llm_service
from backend.services.prompt_manager import prompt_manager
from backend.core.logging import get_logger

logger = get_logger(__name__)


async def detect_language(text: str) -> str:
    """
    Detects the ISO language code of the input text (e.g., 'en', 'hi').
    """
    if not llm_service.client or not text.strip():
        return "en"

    prompt = prompt_manager.get_language_detection_prompt(text)
    
    try:
        lang_code = await llm_service.generate_text(prompt)
        lang_code = lang_code.strip().lower()
        if len(lang_code) > 2:
            # Fallback if LLM gets wordy
            if "hindi" in lang_code: return "hi"
            if "bengali" in lang_code: return "bn"
            if "marathi" in lang_code: return "mr"
            if "telugu" in lang_code: return "te"
            if "tamil" in lang_code: return "ta"
            if "gujarati" in lang_code: return "gu"
            if "urdu" in lang_code: return "ur"
            if "kannada" in lang_code: return "kn"
            if "odia" in lang_code: return "or"
            if "malayalam" in lang_code: return "ml"
            if "punjabi" in lang_code: return "pa"
            return "en"
        return lang_code
    except Exception as e:
        logger.warning(f"Language detection failed: {e}. Defaulting to 'en'.")
        return "en"


async def translate_to_english(text: str) -> str:
    """
    Translates any regional language (or Hinglish) into clear English.
    """
    if not llm_service.client or not text.strip():
        return text
        
    system_prompt = "Translate the following text to clear, professional English. If it is already in English, simply return the original text. Preserve all medical or descriptive nuances."
    
    try:
        translated = await llm_service.generate_text(text, system_prompt)
        return translated.strip()
    except Exception as e:
        logger.warning(f"Translation to English failed: {e}. Returning original.")
        return text


async def translate_from_english(text: str, target_lang_code: str) -> str:
    """
    Translates system English responses into the citizen's target language.
    """
    if target_lang_code == "en" or not llm_service.client or not text.strip():
        return text
        
    system_prompt = f"Translate the following text into the language with ISO code '{target_lang_code}'. Ensure the tone is empathetic, clear, and easy for a layperson to understand. Do not lose medical accuracy."
    
    try:
        translated = await llm_service.generate_text(text, system_prompt)
        if not translated:
            logger.warning("Translation returned empty string. Returning original.")
            return text
        return translated.strip()
    except Exception as e:
        logger.warning(f"Translation from English failed: {e}. Returning original.")
        return text

