"""
backend/infrastructure/rabbitmq/consumer.py
--------------------------------------------
Base consumer class for RabbitMQ queue consumers.

Provides a reusable pattern for declaring queues, binding routing keys,
setting prefetch counts, and dispatching incoming messages to handler methods.

Concrete consumers extend BaseConsumer and implement on_message().
"""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class BaseConsumer(ABC):
    """
    Abstract base class for all RabbitMQ message consumers.

    Subclass this and implement on_message() to handle incoming events.

    Example:
        class WorkflowConsumer(BaseConsumer):
            queue_name = "workflow.events"
            routing_keys = ["workflow.*"]

            async def on_message(self, event_type: str, payload: dict):
                logger.info("Handling workflow event", event_type=event_type)
    """

    queue_name: str = "default"
    routing_keys: list[str] = ["#"]
    durable: bool = True

    async def start(self) -> None:
        """
        Start consuming messages. Called by the background task runner.
        """
        from backend.infrastructure.rabbitmq.client import get_channel, is_connected

        if not is_connected():
            logger.warning(
                "RabbitMQ not connected; consumer not started",
                queue=self.queue_name,
            )
            return

        logger.info("Starting consumer", queue=self.queue_name, routing_keys=self.routing_keys)

        async with get_channel() as channel:
            await channel.set_qos(prefetch_count=settings.rabbitmq_prefetch_count)

            exchange = await channel.get_exchange(settings.rabbitmq_exchange)
            queue = await channel.declare_queue(
                self.queue_name,
                durable=self.durable,
            )

            for routing_key in self.routing_keys:
                await queue.bind(exchange, routing_key=routing_key)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        await self._dispatch(message)

    async def _dispatch(self, message: Any) -> None:
        """Parse the message envelope and call on_message()."""
        try:
            body = json.loads(message.body.decode("utf-8"))
            event_type = body.get("event_type", "unknown")
            payload = body.get("payload", {})
            correlation_id = body.get("correlation_id")

            logger.debug(
                "Message received",
                queue=self.queue_name,
                event_type=event_type,
                correlation_id=correlation_id,
            )

            await self.on_message(event_type=event_type, payload=payload)

        except json.JSONDecodeError as exc:
            logger.error("Failed to decode RabbitMQ message body", exc_info=exc)
        except Exception as exc:
            logger.exception("Consumer message handler raised an exception", exc_info=exc)
            raise  # Re-raise so aio-pika can nack/retry the message

    @abstractmethod
    async def on_message(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Handle an incoming message.

        Args:
            event_type: String identifier of the event type.
            payload: Deserialized event payload dict.
        """
        ...
