"""
backend/shared/events/event_types.py
--------------------------------------
Platform-wide event type definitions for the AI Healthcare Coordination Platform.

Events are the language through which the ecosystem coordinates itself,
as defined in AGENT_BIBLE.md (Event Driven Communication).

Each EventType carries:
  - value:       Canonical string identifier
  - routing_key: RabbitMQ topic routing key (category.subcategory)
  - description: Human-readable documentation

Naming convention: CATEGORY_SUBCATEGORY (snake_case)
Routing key convention: category.subcategory (lowercase, dot-separated)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class EventMeta:
    """Metadata associated with each event type."""
    routing_key: str
    description: str


class EventType(str, Enum):
    """
    Canonical platform event types.

    The string value is the stable event identifier used in messages.
    """

    # ── Workflow Events ──────────────────────────────────────────
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_RECOVERING = "workflow.recovering"

    # ── Context Events ───────────────────────────────────────────
    CONTEXT_INITIALIZED = "context.initialized"
    CONTEXT_UPDATED = "context.updated"
    CONTEXT_CLEARED = "context.cleared"

    # ── Planner Events ───────────────────────────────────────────
    PLAN_CREATED = "plan.created"
    PLAN_UPDATED = "plan.updated"
    PLAN_COMPLETED = "plan.completed"
    PLAN_FAILED = "plan.failed"

    # ── Agent Events ─────────────────────────────────────────────
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_ESCALATING = "agent.escalating"

    # ── Triage / Clinical Events ─────────────────────────────────
    TRIAGE_COMPLETED = "clinical.triage_completed"
    URGENCY_ASSESSED = "clinical.urgency_assessed"
    DEPARTMENT_RECOMMENDED = "clinical.department_recommended"

    # ── Coordination Events ──────────────────────────────────────
    APPOINTMENT_REQUESTED = "coordination.appointment_requested"
    APPOINTMENT_CONFIRMED = "coordination.appointment_confirmed"
    APPOINTMENT_CANCELLED = "coordination.appointment_cancelled"
    CARE_PLAN_GENERATED = "coordination.care_plan_generated"

    # ── Emergency Events ─────────────────────────────────────────
    EMERGENCY_DETECTED = "emergency.detected"
    EMERGENCY_ESCALATED = "emergency.escalated"
    AMBULANCE_DISPATCHED = "emergency.ambulance_dispatched"

    # ── Knowledge Events ─────────────────────────────────────────
    KNOWLEDGE_RETRIEVED = "knowledge.retrieved"
    KNOWLEDGE_INDEXED = "knowledge.indexed"

    # ── Communication Events ─────────────────────────────────────
    NOTIFICATION_SENT = "communication.notification_sent"
    SMS_SENT = "communication.sms_sent"
    FOLLOWUP_SCHEDULED = "communication.followup_scheduled"

    # ── Human-in-the-Loop Events ─────────────────────────────────
    HUMAN_REVIEW_REQUIRED = "human.review_required"
    HUMAN_INTERVENTION = "human.intervention"
    HUMAN_APPROVED = "human.approved"

    # ── Session Events ───────────────────────────────────────────
    SESSION_CREATED = "session.created"
    SESSION_FINALIZED = "session.finalized"

    # ── System Events ────────────────────────────────────────────
    SYSTEM_HEALTH_CHECK = "system.health_check"
    SYSTEM_ERROR = "system.error"
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"

    @property
    def routing_key(self) -> str:
        """Return the RabbitMQ routing key for this event type."""
        return self.value  # value IS the routing key by convention

    @property
    def category(self) -> str:
        """Return the top-level category of this event (prefix before first '.')."""
        return self.value.split(".")[0]

    @classmethod
    def from_routing_key(cls, routing_key: str) -> "EventType | None":
        """Look up an EventType by its routing key."""
        for member in cls:
            if member.value == routing_key:
                return member
        return None
