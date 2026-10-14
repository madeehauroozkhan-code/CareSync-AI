"""
backend/shared/memory/state_manager.py
----------------------------------------
StateManager: controls workflow state transitions for the LangGraph orchestration.

Manages the discrete workflow states that a healthcare coordination session
can occupy, ensuring deterministic, observable, and auditable state progression
as defined in BACKEND_BLUEPRINT.md §16.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.core.exceptions import OrchestrationError
from backend.core.logging import get_logger
from backend.shared.memory.shared_memory import SharedMemory

logger = get_logger(__name__)


class WorkflowStatus(str, Enum):
    """
    All possible states in the healthcare coordination workflow lifecycle.
    Transitions are validated against the allowed_transitions map.
    """
    INITIALIZED = "initialized"
    CONTEXT_LOADING = "context_loading"
    PLANNING = "planning"
    AGENT_COORDINATION = "agent_coordination"
    AWAITING_HUMAN = "awaiting_human"
    ESCALATING = "escalating"
    COMPOSING_RESPONSE = "composing_response"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERING = "recovering"


# Valid state machine transitions
_ALLOWED_TRANSITIONS: Dict[WorkflowStatus, List[WorkflowStatus]] = {
    WorkflowStatus.INITIALIZED: [WorkflowStatus.CONTEXT_LOADING, WorkflowStatus.FAILED],
    WorkflowStatus.CONTEXT_LOADING: [WorkflowStatus.PLANNING, WorkflowStatus.FAILED],
    WorkflowStatus.PLANNING: [
        WorkflowStatus.AGENT_COORDINATION,
        WorkflowStatus.ESCALATING,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
    ],
    WorkflowStatus.AGENT_COORDINATION: [
        WorkflowStatus.PLANNING,        # Re-plan based on new agent output
        WorkflowStatus.COMPOSING_RESPONSE,
        WorkflowStatus.AWAITING_HUMAN,
        WorkflowStatus.ESCALATING,
        WorkflowStatus.FAILED,
    ],
    WorkflowStatus.AWAITING_HUMAN: [
        WorkflowStatus.AGENT_COORDINATION,
        WorkflowStatus.COMPOSING_RESPONSE,
        WorkflowStatus.ESCALATING,
        WorkflowStatus.FAILED,
    ],
    WorkflowStatus.ESCALATING: [
        WorkflowStatus.COMPOSING_RESPONSE,
        WorkflowStatus.AWAITING_HUMAN,
        WorkflowStatus.FAILED,
    ],
    WorkflowStatus.COMPOSING_RESPONSE: [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED],
    WorkflowStatus.COMPLETED: [],   # Terminal state
    WorkflowStatus.FAILED: [WorkflowStatus.RECOVERING],
    WorkflowStatus.RECOVERING: [
        WorkflowStatus.PLANNING,
        WorkflowStatus.FAILED,
    ],
}

_STATE_KEY = "workflow_state"
_STATE_HISTORY_KEY = "workflow_state_history"


class StateManager:
    """
    Manages workflow state transitions with validation and history tracking.

    State is persisted in Redis via SharedMemory so it survives across
    async boundaries within the same request lifecycle.
    """

    def __init__(self) -> None:
        self._memory = SharedMemory()

    def initialize(self, workflow_id: str) -> WorkflowStatus:
        """
        Initialize workflow state to INITIALIZED.
        Clears any prior state for this workflow_id.

        Returns:
            WorkflowStatus.INITIALIZED
        """
        state = WorkflowStatus.INITIALIZED
        self._save_state(workflow_id, state)
        self._save_history(workflow_id, [])
        logger.info("Workflow state initialized", workflow_id=workflow_id)
        return state

    def get_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """
        Return the current workflow status.

        Returns:
            WorkflowStatus enum value, or None if no state is found.
        """
        raw = self._memory.get_context("state", f"{workflow_id}:{_STATE_KEY}")
        if raw is None:
            return None
        try:
            return WorkflowStatus(raw)
        except ValueError:
            logger.warning("Unknown workflow status value in state", value=raw)
            return None

    def transition(
        self,
        workflow_id: str,
        new_status: WorkflowStatus,
        reason: Optional[str] = None,
    ) -> WorkflowStatus:
        """
        Transition the workflow to a new state.

        Args:
            workflow_id: Target workflow identifier.
            new_status: Desired new WorkflowStatus.
            reason: Optional human-readable reason for the transition.

        Returns:
            The new WorkflowStatus after transition.

        Raises:
            OrchestrationError: If the transition is not permitted.
        """
        current = self.get_status(workflow_id)
        if current is None:
            raise OrchestrationError(
                f"Workflow '{workflow_id}' has no current state. Call initialize() first.",
                workflow_id=workflow_id,
            )

        allowed = _ALLOWED_TRANSITIONS.get(current, [])
        if new_status not in allowed:
            raise OrchestrationError(
                f"Invalid workflow transition: {current.value} → {new_status.value}.",
                workflow_id=workflow_id,
                metadata={
                    "current_status": current.value,
                    "requested_status": new_status.value,
                    "allowed_transitions": [s.value for s in allowed],
                },
            )

        # Record transition in history before saving new state
        self._append_history(workflow_id, current, new_status, reason)
        self._save_state(workflow_id, new_status)

        logger.info(
            "Workflow state transitioned",
            workflow_id=workflow_id,
            from_status=current.value,
            to_status=new_status.value,
            reason=reason,
        )
        return new_status

    def get_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Return the full state transition history for a workflow."""
        return self._memory.get_context("state", f"{workflow_id}:{_STATE_HISTORY_KEY}") or []

    # ── Internal Helpers ──────────────────────────────────────────

    def _save_state(self, workflow_id: str, status: WorkflowStatus) -> None:
        self._memory.set_context("state", f"{workflow_id}:{_STATE_KEY}", status.value)

    def _save_history(self, workflow_id: str, history: List) -> None:
        self._memory.set_context("state", f"{workflow_id}:{_STATE_HISTORY_KEY}", history)

    def _append_history(
        self,
        workflow_id: str,
        from_status: WorkflowStatus,
        to_status: WorkflowStatus,
        reason: Optional[str],
    ) -> None:
        history = self.get_history(workflow_id)
        history.append({
            "from": from_status.value,
            "to": to_status.value,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "reason": reason,
        })
        self._save_history(workflow_id, history)
