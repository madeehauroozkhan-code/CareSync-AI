"""
backend/shared/events/event_bus.py
------------------------------------
In-process EventBus for the AI Healthcare Coordination Platform.

Provides a lightweight publish/subscribe mechanism for synchronous
in-process event handling. For cross-service events, the EventBus
bridges to RabbitMQ via the EventPublisher.

Architecture:
  - In-process: synchronous/async handlers registered with subscribe()
  - Cross-process: async bridge to RabbitMQ via EventPublisher

The EventBus follows a singleton pattern per process to ensure
all components share the same event registry.

Usage:
    bus = EventBus.get_instance()

    # Subscribe
    @bus.subscribe(EventType.TRIAGE_COMPLETED)
    async def handle_triage(payload: dict):
        ...

    # Publish
    await bus.publish(EventType.TRIAGE_COMPLETED, {"urgency": "high"})
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional

from backend.core.logging import get_logger
from backend.shared.events.event_types import EventType

logger = get_logger(__name__)

# Type alias for event handlers
EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]


class EventBus:
    """
    Singleton in-process event bus with optional RabbitMQ bridge.

    Thread-safe for single-process async applications (asyncio).
    """

    _instance: Optional["EventBus"] = None

    def __init__(self) -> None:
        # Maps EventType → list of registered async handlers
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._enabled: bool = True

    @classmethod
    def get_instance(cls) -> "EventBus":
        """Return the singleton EventBus instance."""
        if cls._instance is None:
            cls._instance = cls()
            logger.info("EventBus singleton created")
        return cls._instance

    # ── Subscription ──────────────────────────────────────────────

    def subscribe(
        self,
        event_type: EventType,
    ) -> Callable[[EventHandler], EventHandler]:
        """
        Decorator to register an async handler for an event type.

        Usage:
            @bus.subscribe(EventType.TRIAGE_COMPLETED)
            async def handle_triage(payload: dict):
                ...
        """
        def decorator(handler: EventHandler) -> EventHandler:
            self._handlers[event_type].append(handler)
            logger.debug(
                "EventBus handler registered",
                event_type=event_type.value,
                handler=handler.__name__,
            )
            return handler

        return decorator

    def register(self, event_type: EventType, handler: EventHandler) -> None:
        """Programmatically register an async handler for an event type."""
        self._handlers[event_type].append(handler)
        logger.debug(
            "EventBus handler registered (programmatic)",
            event_type=event_type.value,
            handler=handler.__name__,
        )

    def unregister(self, event_type: EventType, handler: EventHandler) -> bool:
        """
        Remove a previously registered handler.

        Returns:
            True if the handler was found and removed.
        """
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    # ── Publishing ────────────────────────────────────────────────

    async def publish(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        *,
        correlation_id: Optional[str] = None,
        bridge_to_rabbitmq: bool = True,
    ) -> None:
        """
        Publish an event to all registered in-process handlers and
        optionally bridge to RabbitMQ for cross-service propagation.

        Args:
            event_type: The event to publish.
            payload: Event payload dict.
            correlation_id: Optional tracing correlation ID.
            bridge_to_rabbitmq: If True, also publishes to RabbitMQ exchange.
        """
        if not self._enabled:
            return

        envelope = {
            "event_type": event_type.value,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "payload": payload,
        }

        # ── In-process handlers ──────────────────────────────────
        handlers = self._handlers.get(event_type, [])
        if handlers:
            logger.debug(
                "EventBus dispatching to handlers",
                event_type=event_type.value,
                handler_count=len(handlers),
            )
            tasks = [
                self._invoke_handler(handler, envelope)
                for handler in handlers
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

        # ── RabbitMQ bridge ──────────────────────────────────────
        if bridge_to_rabbitmq:
            try:
                from backend.infrastructure.rabbitmq.publisher import EventPublisher

                publisher = EventPublisher()
                await publisher.publish(
                    event_type=event_type,
                    payload=payload,
                    correlation_id=correlation_id,
                )
            except Exception as exc:
                # RabbitMQ bridge failure should not stop in-process flow
                logger.debug("EventBus RabbitMQ bridge failed", event_type=event_type.value, exc_info=exc)

    async def _invoke_handler(
        self,
        handler: EventHandler,
        envelope: Dict[str, Any],
    ) -> None:
        """Invoke a single event handler, catching and logging exceptions."""
        try:
            await handler(envelope)
        except Exception as exc:
            logger.error(
                "EventBus handler raised an exception",
                handler=handler.__name__,
                event_type=envelope.get("event_type"),
                exc_info=exc,
            )

    def publish_sync(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        *,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Synchronous convenience wrapper for publishing from non-async contexts.
        Uses asyncio.get_event_loop() — prefer the async version whenever possible.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.publish(event_type, payload, correlation_id=correlation_id))
            else:
                loop.run_until_complete(self.publish(event_type, payload, correlation_id=correlation_id))
        except Exception as exc:
            logger.warning("EventBus sync publish failed", event_type=event_type.value, exc_info=exc)

    # ── Management ────────────────────────────────────────────────

    def disable(self) -> None:
        """Disable all event dispatching (useful in tests)."""
        self._enabled = False

    def enable(self) -> None:
        """Re-enable event dispatching."""
        self._enabled = True

    def clear_handlers(self) -> None:
        """Remove all registered handlers (useful in tests)."""
        self._handlers.clear()

    def handler_count(self, event_type: Optional[EventType] = None) -> int:
        """Return the number of registered handlers (total or per event type)."""
        if event_type is not None:
            return len(self._handlers.get(event_type, []))
        return sum(len(h) for h in self._handlers.values())
