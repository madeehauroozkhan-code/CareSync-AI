"""
backend/orchestration/state.py
--------------------------------
LangGraph workflow state schema for the AI Healthcare Coordination Platform.

The WorkflowState TypedDict defines the complete state object that flows
through the LangGraph StateGraph. Every node reads from and writes to this
shared state — it is the runtime representation of the Shared Memory concept
for in-flight workflows.

State schema design principles (from BACKEND_BLUEPRINT.md):
  - Context continuity across all agents
  - Progressive enrichment as workflow advances
  - Traceable decision history
  - Safe recovery via checkpointing
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict


class ConversationTurn(TypedDict):
    """A single turn in the conversation history."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str


class ClinicalObservation(TypedDict):
    """A clinical observation recorded by a specialized agent."""
    observation_type: str
    content: Any
    source_agent: str
    confidence: float
    timestamp: str


class WorkflowDecision(TypedDict):
    """A decision point recorded during workflow execution."""
    decision_type: str
    decision: Any
    rationale: str
    agent: str
    timestamp: str


class AgentResult(TypedDict):
    """Output from a specialized agent execution."""
    agent_name: str
    status: Literal["completed", "failed", "skipped"]
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time_ms: Optional[float]


class WorkflowState(TypedDict, total=False):
    """
    Complete LangGraph workflow state for a healthcare coordination request.

    This state object flows through every node in the StateGraph.
    Nodes may read any field and MUST only write to fields within their
    designated responsibility (as per the BACKEND_BLUEPRINT service boundary rules).

    Fields are grouped by lifecycle stage for readability.
    total=False means all fields are optional (supports partial updates per node).
    """

    # ── Identity ──────────────────────────────────────────────────
    workflow_id: str
    session_id: str
    user_id: Optional[str]
    request_id: Optional[str]

    # ── Request Information ───────────────────────────────────────
    raw_input: str
    input_language: Optional[str]
    input_modality: Literal["text", "voice", "image", "document"]
    normalized_input: Optional[str]

    # ── Context ───────────────────────────────────────────────────
    conversation_history: Annotated[List[ConversationTurn], operator.add]
    user_profile: Optional[Dict[str, Any]]
    location: Optional[Dict[str, Any]]  # {lat, lng, city, state}

    # ── Planning ──────────────────────────────────────────────────
    workflow_objective: Optional[str]
    selected_agents: List[str]
    execution_plan: Optional[Dict[str, Any]]
    plan_iteration: int

    # ── Clinical Intelligence ─────────────────────────────────────
    clinical_observations: Annotated[List[ClinicalObservation], operator.add]
    urgency_level: Optional[Literal["low", "moderate", "high", "critical", "emergency"]]
    recommended_department: Optional[str]
    symptom_tags: List[str]

    # ── Agent Coordination ────────────────────────────────────────
    agent_results: Annotated[List[AgentResult], operator.add]
    current_agent: Optional[str]
    intake_data: Optional[Dict[str, Any]]
    triage_data: Optional[Dict[str, Any]]
    knowledge_data: Optional[Dict[str, Any]]
    care_coordination_data: Optional[Dict[str, Any]]
    ambulance_data: Optional[Dict[str, Any]]
    followup_data: Optional[Dict[str, Any]]
    community_data: Optional[Dict[str, Any]]

    # ── Knowledge Retrieval ───────────────────────────────────────
    retrieved_knowledge: Annotated[List[Dict[str, Any]], operator.add]

    # ── Care Coordination ─────────────────────────────────────────
    hospital_recommendations: List[Dict[str, Any]]
    appointment_request: Optional[Dict[str, Any]]
    care_plan: Optional[Dict[str, Any]]

    # ── Emergency ─────────────────────────────────────────────────
    emergency_detected: bool
    emergency_type: Optional[str]
    escalation_status: Optional[str]

    # ── Decisions & History ───────────────────────────────────────
    decisions: Annotated[List[WorkflowDecision], operator.add]
    workflow_status: str
    error: Optional[str]
    error_agent: Optional[str]
    retry_count: int

    # ── Response Composition ──────────────────────────────────────
    response_text: Optional[str]
    response_language: Optional[str]
    response_metadata: Optional[Dict[str, Any]]
    requires_human_review: bool

    # ── Timing & Metadata ─────────────────────────────────────────
    started_at: Optional[str]
    completed_at: Optional[str]
    metadata: Optional[Dict[str, Any]]


def create_initial_state(
    workflow_id: str,
    session_id: str,
    raw_input: str,
    *,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    input_modality: str = "text",
    location: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[ConversationTurn]] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> WorkflowState:
    """
    Create a fresh WorkflowState with sensible defaults.

    Args:
        workflow_id: Unique identifier for this workflow execution.
        session_id: The session this workflow belongs to.
        raw_input: The raw user input (text, transcript, etc.).
        user_id: Optional authenticated user ID.
        request_id: Optional HTTP request correlation ID.
        input_modality: How the input was provided (text/voice/image/document).
        location: Optional user location dict.
        conversation_history: Prior conversation turns from the session.
        user_profile: Optional user profile from Firestore.
        metadata: Optional additional metadata.

    Returns:
        WorkflowState with all list/counter fields initialised to safe defaults.
    """
    from datetime import datetime, timezone

    return WorkflowState(
        workflow_id=workflow_id,
        session_id=session_id,
        user_id=user_id,
        request_id=request_id,
        raw_input=raw_input,
        input_language=None,
        input_modality=input_modality,
        normalized_input=None,
        conversation_history=conversation_history or [],
        user_profile=user_profile,
        location=location,
        workflow_objective=None,
        selected_agents=[],
        execution_plan=None,
        plan_iteration=0,
        clinical_observations=[],
        urgency_level=None,
        recommended_department=None,
        symptom_tags=[],
        agent_results=[],
        current_agent=None,
        retrieved_knowledge=[],
        hospital_recommendations=[],
        appointment_request=None,
        care_plan=None,
        emergency_detected=False,
        emergency_type=None,
        escalation_status=None,
        decisions=[],
        workflow_status="initialized",
        error=None,
        error_agent=None,
        retry_count=0,
        response_text=None,
        response_language=None,
        response_metadata=None,
        requires_human_review=False,
        started_at=datetime.now(tz=timezone.utc).isoformat(),
        completed_at=None,
        metadata=metadata,
    )
