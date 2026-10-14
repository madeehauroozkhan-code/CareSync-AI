"""
backend/shared/memory/context_manager.py
-----------------------------------------
ContextManager: manages the lifecycle of session-level context within
the AI Healthcare Coordination Platform.

Responsible for:
  - Initializing new session contexts
  - Loading existing session contexts
  - Enriching context as agents contribute information
  - Finalizing sessions upon completion

Backed by SharedMemory; all state is stored in Redis with Firestore
persistence for long-term cases.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.core.logging import get_logger
from backend.shared.memory.shared_memory import SharedMemory
from backend.infrastructure.firebase.client import get_firebase_app
from firebase_admin import firestore

logger = get_logger(__name__)

# Context keys — centralised to avoid magic strings
CTX_USER_ID = "user_id"
CTX_SESSION_ID = "session_id"
CTX_STARTED_AT = "started_at"
CTX_LAST_UPDATED = "last_updated"
CTX_CONVERSATION_HISTORY = "conversation_history"
CTX_CLINICAL_OBSERVATIONS = "clinical_observations"
CTX_WORKFLOW_STATUS = "workflow_status"
CTX_ACTIVE_AGENTS = "active_agents"
CTX_DECISIONS = "decisions"
CTX_METADATA = "metadata"


class ContextManager:
    """
    Manages the session context lifecycle for multi-agent collaboration.

    The context is the shared operational understanding of a healthcare
    interaction — it evolves incrementally as the workflow progresses.
    """

    def __init__(self) -> None:
        self._memory = SharedMemory()
        self._db = None
        
    @property
    def db(self):
        if self._db is None and get_firebase_app():
            self._db = firestore.client()
        return self._db

    # ── Lifecycle ─────────────────────────────────────────────────

    def create_session(
        self,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Initialize a new session context.

        Args:
            user_id: Optional user identifier to associate with the session.
            metadata: Optional additional metadata (e.g., device, language).

        Returns:
            New session_id (UUID4).
        """
        session_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc).isoformat()

        self._memory.set_context(session_id, CTX_SESSION_ID, session_id)
        self._memory.set_context(session_id, CTX_STARTED_AT, now)
        self._memory.set_context(session_id, CTX_LAST_UPDATED, now)
        self._memory.set_context(session_id, CTX_CONVERSATION_HISTORY, [])
        self._memory.set_context(session_id, CTX_CLINICAL_OBSERVATIONS, [])
        self._memory.set_context(session_id, CTX_WORKFLOW_STATUS, "initialized")
        self._memory.set_context(session_id, CTX_ACTIVE_AGENTS, [])
        self._memory.set_context(session_id, CTX_DECISIONS, [])

        if user_id:
            self._memory.set_context(session_id, CTX_USER_ID, user_id)
        if metadata:
            self._memory.set_context(session_id, CTX_METADATA, metadata)

        logger.info("Session context created", session_id=session_id, user_id=user_id)
        return session_id

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve the full context for a session.

        Returns:
            Dict of all context keys, or empty dict if session doesn't exist.
        """
        return self._memory.get_full_session_context(session_id)

    def finalize_session(self, session_id: str) -> bool:
        """
        Mark a session as completed and persist to Firestore for long-term storage.
        """
        self._update_field(session_id, CTX_WORKFLOW_STATUS, "completed")
        logger.info("Session finalized", session_id=session_id)
        
        # Persist to Firestore
        self._persist_to_firestore(session_id)
        
        # Clean up short-term memory
        self._memory.clear_session(session_id)
        
        return True

    # ── Context Enrichment ────────────────────────────────────────

    def add_conversation_turn(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> bool:
        """
        Append a conversation turn to the session history.

        Args:
            session_id: Target session.
            role: "user" | "assistant" | "system"
            content: Message content.
        """
        history: List[Dict[str, Any]] = self._memory.get_context(session_id, CTX_CONVERSATION_HISTORY) or []
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        })
        success = self._memory.set_context(session_id, CTX_CONVERSATION_HISTORY, history)
        self._touch(session_id)
        return success

    def add_clinical_observation(
        self,
        session_id: str,
        observation: Dict[str, Any],
        source_agent: str,
    ) -> bool:
        """
        Record a clinical observation contributed by an agent.

        Args:
            session_id: Target session.
            observation: Structured clinical finding dict.
            source_agent: Name of the contributing agent.
        """
        observations: List[Dict[str, Any]] = (
            self._memory.get_context(session_id, CTX_CLINICAL_OBSERVATIONS) or []
        )
        observations.append({
            **observation,
            "source_agent": source_agent,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        })
        success = self._memory.set_context(session_id, CTX_CLINICAL_OBSERVATIONS, observations)
        self._touch(session_id)
        return success

    def record_decision(
        self,
        session_id: str,
        decision: Dict[str, Any],
        agent: str,
    ) -> bool:
        """
        Record a decision made by an agent within the workflow.
        """
        decisions: List[Dict[str, Any]] = self._memory.get_context(session_id, CTX_DECISIONS) or []
        decisions.append({
            **decision,
            "agent": agent,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        })
        success = self._memory.set_context(session_id, CTX_DECISIONS, decisions)
        self._touch(session_id)
        return success

    def set_workflow_status(self, session_id: str, status: str) -> bool:
        """
        Update the workflow status for a session.

        Status values: initialized | planning | in_progress | awaiting_human | completed | failed
        """
        success = self._update_field(session_id, CTX_WORKFLOW_STATUS, status)
        if success:
            logger.info("Workflow status updated", session_id=session_id, status=status)
        return success

    # ── Internal Helpers ──────────────────────────────────────────

    def _touch(self, session_id: str) -> None:
        """Update the last_updated timestamp."""
        self._memory.set_context(
            session_id,
            CTX_LAST_UPDATED,
            datetime.now(tz=timezone.utc).isoformat(),
        )

    def _update_field(self, session_id: str, key: str, value: Any) -> bool:
        """Set a single context field and touch the session."""
        success = self._memory.set_context(session_id, key, value)
        self._touch(session_id)
        return success

    def _persist_to_firestore(self, session_id: str) -> None:
        """Saves the entire session context to Firestore."""
        if not self.db:
            logger.warning("Firestore not initialized; skipping persistence for session", session_id=session_id)
            return
            
        try:
            full_context = self.get_context(session_id)
            if full_context:
                self.db.collection('sessions').document(session_id).set(full_context, merge=True)
                logger.info("Session persisted to Firestore", session_id=session_id)
        except Exception as e:
            logger.error("Failed to persist session to Firestore", session_id=session_id, error=str(e))

    async def summarize_history(self, session_id: str, max_turns: int = 20) -> bool:
        """
        Compress conversation history when it exceeds max_turns.
        Summarizes older turns into a single system message to keep context window manageable.
        """
        history: List[Dict[str, Any]] = self._memory.get_context(session_id, CTX_CONVERSATION_HISTORY) or []
        
        if len(history) <= max_turns:
            return False  # No summarization needed
        
        # Split: older turns to summarize, recent turns to keep
        older_turns = history[:-max_turns]
        recent_turns = history[-max_turns:]
        
        # Build summary using LLM if available
        from backend.services.llm_service import llm_service
        
        older_text = "\n".join([f"{t.get('role', 'unknown')}: {t.get('content', '')}" for t in older_turns])
        
        summary_text = f"[Summary of {len(older_turns)} earlier messages]"
        if llm_service.client:
            try:
                summary_text = await llm_service.generate_text(
                    f"Summarize the following conversation in 2-3 sentences, preserving key medical details:\n\n{older_text}",
                    "You are a clinical conversation summarizer. Be concise and preserve all medically relevant information."
                )
            except Exception as e:
                logger.warning(f"History summarization failed: {e}")
        
        # Replace history with summary + recent
        compressed = [{"role": "system", "content": summary_text, "timestamp": datetime.now(tz=timezone.utc).isoformat()}]
        compressed.extend(recent_turns)
        
        self._memory.set_context(session_id, CTX_CONVERSATION_HISTORY, compressed)
        self._touch(session_id)
        logger.info("Conversation history summarized", session_id=session_id, original_turns=len(history), compressed_turns=len(compressed))
        return True

    def get_patient_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve past session summaries for a user from Firestore.
        Enables long-term memory across sessions.
        """
        if not self.db or not user_id:
            return []
        
        try:
            sessions_ref = self.db.collection('sessions').where('user_id', '==', user_id).order_by('started_at', direction='DESCENDING').limit(10)
            docs = sessions_ref.stream()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                history.append({
                    "session_id": data.get("session_id"),
                    "started_at": data.get("started_at"),
                    "workflow_status": data.get("workflow_status"),
                    "clinical_observations": data.get("clinical_observations", []),
                    "decisions": data.get("decisions", []),
                    "hospital_recommendations": data.get("hospital_recommendations", []),
                    "emergency_history": data.get("emergency_detected", False)
                })
            return history
        except Exception as e:
            logger.warning(f"Failed to retrieve patient history: {e}")
            return []

