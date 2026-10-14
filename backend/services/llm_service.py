"""
llm_service.py
-----------------
Unified LLM abstraction for the AI Sahayak backend.

Provides:
  1. `generate_response()` — legacy sync function used by old orchestrator
  2. `LLMService` class — async service with `.client`, `.translate()`,
     `.generate_json()`, `.generate_text()` used by new modular agents

Supports Gemini, OpenAI, and Groq (OpenAI-compatible endpoint).
Gracefully degrades: when no API key is configured, `.client` is None and
all agent code falls back to rule-based logic automatically.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from backend.config.settings import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GROQ_MODEL,
)
from backend.core.logging import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────
# Legacy sync API (used by old orchestrator pipeline)
# ──────────────────────────────────────────────────────────────────


def generate_response(prompt: str, system_prompt: str = "") -> str:
    """
    Sends a prompt to the configured LLM provider and returns the text
    response. Returns a clear error string instead of raising, so a missing
    API key never crashes the demo.
    """
    if LLM_PROVIDER == "gemini":
        return _call_gemini(prompt, system_prompt)
    elif LLM_PROVIDER == "openai":
        return _call_openai(prompt, system_prompt)
    else:
        return "[LLM_PROVIDER not configured -- using rule-based agent logic instead]"


def _call_gemini(prompt: str, system_prompt: str) -> str:
    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"[Gemini call failed: {e}]"


def _call_openai(prompt: str, system_prompt: str) -> str:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        return f"[OpenAI call failed: {e}]"


# ──────────────────────────────────────────────────────────────────
# Helper: robust JSON extraction from LLM text output
# ──────────────────────────────────────────────────────────────────


def _extract_json(text: str) -> str:
    """
    Strips markdown code fences and grabs the first {...} block, since
    LLMs sometimes add a sentence before/after the JSON even when told
    not to. Falls back to the raw text if no braces are found.
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


# ──────────────────────────────────────────────────────────────────
# New async LLMService class (used by modular agents)
# ──────────────────────────────────────────────────────────────────


class LLMService:
    """
    Async LLM service providing translate(), generate_json(), and
    generate_text() for agents. Supports "gemini", "openai", and "groq"
    (Groq uses the OpenAI-compatible client with a different base_url).

    If no API key is configured, self.client is None and agents should
    fall back to their rule-based logic.
    """

    def __init__(self) -> None:
        self.client: Optional[Any] = None
        self.provider: str = LLM_PROVIDER
        self.model: str = GROQ_MODEL if LLM_PROVIDER == "groq" else "gpt-4o-mini"

        if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
            try:
                import google.generativeai as genai

                genai.configure(api_key=GEMINI_API_KEY)
                self.client = genai.GenerativeModel("gemini-2.0-flash")
            except Exception:
                self.client = None

        elif LLM_PROVIDER == "openai" and OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(api_key=OPENAI_API_KEY, max_retries=0, timeout=10.0)
            except Exception:
                self.client = None

        elif LLM_PROVIDER == "groq" and GROQ_API_KEY:
            try:
                # Groq exposes an OpenAI-compatible API -- same SDK, different base_url.
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1",
                    max_retries=0,
                    timeout=10.0
                )
            except Exception:
                self.client = None

    async def translate(self, text: str, from_lang: str, to_lang: str) -> str:
        """Translate text between languages using LLM."""
        if self.client is None:
            return text  # No-op fallback

        prompt = f"Translate the following from {from_lang} to {to_lang}. Return ONLY the translation, nothing else:\n\n{text}"

        try:
            if self.provider == "gemini":
                response = self.client.generate_content(prompt)
                return response.text.strip()
            elif self.provider in ("openai", "groq"):
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content.strip()
        except Exception:
            return text  # Fallback: return original

        return text

    async def generate_json(
        self, prompt: str, system_prompt: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Generate a JSON response from the LLM. Returns parsed dict or None."""
        if self.client is None:
            return None

        raw_text = ""
        try:
            if self.provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{prompt}\n\nRespond with valid JSON only." if system_prompt else f"{prompt}\n\nRespond with valid JSON only."
                response = self.client.generate_content(full_prompt)
                raw_text = response.text.strip()
                return json.loads(_extract_json(raw_text))

            elif self.provider in ("openai", "groq"):
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                )
                raw_text = response.choices[0].message.content.strip()
                return json.loads(_extract_json(raw_text))

        except Exception as e:
            logger.warning(
                "generate_json failed to parse LLM output",
                error=str(e),
                raw_response=raw_text[:500],
            )
            return None

        return None

    async def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a plain text response from the LLM."""
        if self.client is None:
            return ""

        try:
            if self.provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self.client.generate_content(full_prompt)
                return response.text.strip()
            elif self.provider in ("openai", "groq"):
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM text generation failed: {e}")
            return ""

        return ""


# Module-level singleton — agents import this directly
llm_service = LLMService()
