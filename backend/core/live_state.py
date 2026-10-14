"""
backend/core/live_state.py
----------------------------
Shared in-memory state for the admin dashboard demo.

NOTE: This is intentionally simple (a Python list in memory) for the demo/
hackathon stage. It resets whenever the backend restarts, and won't work
correctly across multiple worker processes. For a real deployment, replace
this with a database table or Redis list.
"""

from typing import List, Dict, Any

MAX_CASES = 200

# The single source of truth for "recent cases" -- both /chat (writer) and
# /dashboard/* (readers) point at this same list.
recent_cases: List[Dict[str, Any]] = []


def add_case(case: Dict[str, Any]) -> None:
    """Called by the chat endpoint after every processed case."""
    recent_cases.insert(0, case)
    del recent_cases[MAX_CASES:]


def reset_cases() -> None:
    """Called by POST /dashboard/reset."""
    recent_cases.clear()
