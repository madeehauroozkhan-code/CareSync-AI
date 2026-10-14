"""
backend/infrastructure/rabbitmq/publisher.py
---------------------------------------------
RabbitMQ event publisher for the AI Healthcare Coordination Platform.

Publishes structured events to the platform exchange using topic routing keys.
All events are JSON-encoded and marked as persistent (delivery_mode=2)
so they survive broker restarts.

When RabbitMQ is unavailable, publish silently no-ops and returns False
so callers degrade gracefully.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.shared.events.event_types import EventType

logger = get_logger(__name__)


class EventPublisher:
    """
    Publishes platform events to the configured RabbitMQ exchange.

    Routing key convention: <category>.<event_name>
    e.g., "workflow.started", "agent.completed", "emergency.escalated"
    """

    async def publish(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        *,
        routing_key: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> bool:
        """
        Publish a single event to RabbitMQ.

        Args:
            event_type: The EventType enum value identifying this event.
            payload: Event payload dict (must be JSON-serialisable).
            routing_key: Override routing key (defaults to event_type.routing_key).
            correlation_id: Optional correlation ID for distributed tracing.

        Returns:
            True if the event was published, False if RabbitMQ is unavailable.
        """
        from backend.infrastructure.rabbitmq.client import get_channel, is_connected

        if not is_connected():
            logger.debug(
                "RabbitMQ unavailable; event not published",
                event_type=event_type.value,
            )
            return False

        effective_routing_key = routing_key or event_type.routing_key
        event_id = str(uuid.uuid4())
        envelope = {
            "event_id": event_id,
            "event_type": event_type.value,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "correlation_id": correlation_id or event_id,
            "payload": payload,
        }

        try:
            import aio_pika

            message = aio_pika.Message(
                body=json.dumps(envelope).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                correlation_id=correlation_id or event_id,
                message_id=event_id,
            )

            async with get_channel() as channel:
                exchange = await channel.get_exchange(settings.rabbitmq_exchange)
                await exchange.publish(message, routing_key=effective_routing_key)

            logger.debug(
                "Event published",
                event_type=event_type.value,
                routing_key=effective_routing_key,
                event_id=event_id,
            )
            return True

        except Exception as exc:
            logger.warning(
                "Failed to publish event",
                event_type=event_type.value,
                routing_key=effective_routing_key,
                exc_info=exc,
            )
            return False
