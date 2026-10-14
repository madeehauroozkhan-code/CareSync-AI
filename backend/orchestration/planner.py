"""
backend/orchestration/planner.py
----------------------------------
PlannerOrchestrator: the central coordination authority for the backend.

As defined in BACKEND_BLUEPRINT.md §10 and AGENT_BIBLE.md (Planner Agent):
  - Receives incoming workflow objectives
  - Builds execution plans
  - Coordinates specialized agents via LangGraph
  - Maintains shared context
  - Handles failure recovery

This is the single orchestration entry point for all healthcare workflows.
AI agent implementation is Phase 2; this module provides the coordination
infrastructure and contract.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.core.exceptions import OrchestrationError
from backend.core.logging import get_logger
from backend.orchestration.state import WorkflowState, create_initial_state
from backend.shared.events.event_bus import EventBus
from backend.shared.events.event_types import EventType
from backend.shared.memory.context_manager import ContextManager
from backend.shared.memory.state_manager import StateManager, WorkflowStatus

logger = get_logger(__name__)


class PlannerOrchestrator:
    """
    Central orchestration authority for the AI Healthcare Coordination Platform.

    Responsibilities:
      - Accept incoming healthcare requests
      - Initialize workflow state via LangGraph
      - Coordinate agent execution sequence
      - Maintain shared context consistency
      - Handle failures and recovery
      - Emit lifecycle events to the EventBus

    One PlannerOrchestrator instance handles one request at a time.
    Create a new instance per request (or inject via FastAPI Depends).
    """

    def __init__(self) -> None:
        self._context_manager = ContextManager()
        self._state_manager = StateManager()
        self._event_bus = EventBus.get_instance()

    async def orchestrate(
        self,
        raw_input: str,
        session_id: Optional[str] = None,
        *,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        input_modality: str = "text",
        location: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete healthcare workflow from raw input to response.

        Args:
            raw_input: Raw user input (text, voice transcript, etc.)
            session_id: Existing session to continue, or None to create new.
            user_id: Optional authenticated user ID.
            request_id: HTTP request correlation ID for distributed tracing.
            input_modality: How the input was provided (text/voice/image/document).
            location: Optional user location for hospital recommendations.
            metadata: Optional additional context metadata.

        Returns:
            Dict containing workflow result:
              - workflow_id: str
              - session_id: str
              - response: str
              - workflow_status: str
              - metadata: dict

        Raises:
            OrchestrationError: If the workflow fails unrecoverably.
        """
        import time
        start_time = time.time()
        
        workflow_id = str(uuid.uuid4())
        correlation_id = request_id or workflow_id

        # Create or reuse session
        if session_id is None:
            session_id = self._context_manager.create_session(user_id=user_id, metadata=metadata)

        logger.info(
            "Orchestration started",
            workflow_id=workflow_id,
            session_id=session_id,
            user_id=user_id,
            correlation_id=correlation_id,
            modality=input_modality,
        )

        # Initialize workflow state
        self._state_manager.initialize(workflow_id)

        # Publish start event
        await self._event_bus.publish(
            EventType.WORKFLOW_STARTED,
            {
                "workflow_id": workflow_id,
                "session_id": session_id,
                "user_id": user_id,
                "modality": input_modality,
            },
            correlation_id=request_id,
        )

        try:
            # Build initial LangGraph state
            initial_state = create_initial_state(
                workflow_id=workflow_id,
                session_id=session_id,
                raw_input=raw_input,
                user_id=user_id,
                request_id=request_id,
                input_modality=input_modality,
                location=location,
                metadata=metadata,
            )

            # Transition state machine
            self._state_manager.transition(workflow_id, WorkflowStatus.CONTEXT_LOADING)

            # Execute the LangGraph orchestration graph
            result_state = await self._execute_graph(initial_state, workflow_id)

            # Transition to completed
            self._state_manager.transition(workflow_id, WorkflowStatus.COMPLETED)

            # Finalize session context
            self._context_manager.set_workflow_status(session_id, "completed")

            # Publish completion event
            await self._event_bus.publish(
                EventType.WORKFLOW_COMPLETED,
                {
                    "workflow_id": workflow_id,
                    "session_id": session_id,
                    "status": "completed",
                },
                correlation_id=request_id,
            )

            response = self._format_response(result_state, workflow_id, session_id)
            exec_ms = (time.time() - start_time) * 1000
            logger.info(
                "Orchestration completed",
                workflow_id=workflow_id,
                session_id=session_id,
                status="completed",
                execution_time_ms=exec_ms,
                correlation_id=correlation_id
            )
            return response

        except OrchestrationError:
            raise

        except Exception as exc:
            logger.exception(
                "Orchestration failed with unhandled exception",
                workflow_id=workflow_id,
                session_id=session_id,
                exc_info=exc,
            )

            # Publish failure event
            await self._event_bus.publish(
                EventType.WORKFLOW_FAILED,
                {
                    "workflow_id": workflow_id,
                    "session_id": session_id,
                    "error": str(exc),
                },
                correlation_id=request_id,
            )

            try:
                self._state_manager.transition(
                    workflow_id,
                    WorkflowStatus.FAILED,
                    reason=str(exc),
                )
            except Exception:
                pass

            raise OrchestrationError(
                f"Workflow {workflow_id} failed: {exc}",
                workflow_id=workflow_id,
            ) from exc

    async def _execute_graph(
        self,
        initial_state: WorkflowState,
        workflow_id: str,
    ) -> WorkflowState:
        """
        Execute the LangGraph healthcare orchestration graph.

        Returns the final workflow state after all nodes have executed.
        """
        from backend.orchestration.graph import get_compiled_graph

        self._state_manager.transition(workflow_id, WorkflowStatus.PLANNING)

        graph = get_compiled_graph()
        config = {"configurable": {"thread_id": workflow_id}}

        import time
        start_graph = time.time()
        try:
            final_state = await graph.ainvoke(initial_state, config=config)
            graph_ms = (time.time() - start_graph) * 1000
            logger.info("LangGraph execution finished", workflow_id=workflow_id, graph_latency_ms=graph_ms)
            return final_state

        except Exception as exc:
            graph_ms = (time.time() - start_graph) * 1000
            logger.error("LangGraph execution failed", workflow_id=workflow_id, graph_latency_ms=graph_ms, exc_info=exc)
            raise OrchestrationError(
                f"LangGraph graph execution failed: {exc}",
                workflow_id=workflow_id,
            ) from exc

    def _format_response(
        self,
        state: WorkflowState,
        workflow_id: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Format the final workflow state into the API response payload.
        """
        return {
            "workflow_id": workflow_id,
            "session_id": session_id,
            "status": state.get("workflow_status", "completed"),
            "response": state.get("response_text", ""),
            "response_language": state.get("response_language", "en"),
            "urgency_level": state.get("urgency_level"),
            "emergency_detected": state.get("emergency_detected", False),
            "requires_human_review": state.get("requires_human_review", False),
            "workflow_objective": state.get("workflow_objective"),
            "selected_agents": state.get("selected_agents", []),
            "agent_results": state.get("agent_results", []),
            "intake_data": state.get("intake_data"),
            "triage_data": state.get("triage_data"),
            "knowledge_data": state.get("knowledge_data"),
            "care_coordination_data": state.get("care_coordination_data"),
            "ambulance_data": state.get("ambulance_data"),
            "followup_data": state.get("followup_data"),
            "community_data": state.get("community_data"),
            "clinical_observations": state.get("clinical_observations", []),
            "hospital_recommendations": state.get("hospital_recommendations", []),
            "care_plan": state.get("care_plan"),
            "completed_at": state.get("completed_at"),
            "metadata": state.get("metadata"),
        }
