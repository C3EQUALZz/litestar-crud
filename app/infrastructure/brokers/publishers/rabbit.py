import logging
from collections.abc import Mapping
from typing import override

from faststream.rabbit import RabbitBroker
from faststream.rabbit.publisher.asyncapi import AsyncAPIPublisher
from pydantic import BaseModel

from app.exceptions.infrastructure import UnknownTopicError
from app.infrastructure.brokers.publishers.base import BaseMessageBrokerPublisher

logger = logging.getLogger(__name__)


class FastStreamRabbitMessageBroker(BaseMessageBrokerPublisher):
    def __init__(self, broker: RabbitBroker, producers: Mapping[str, AsyncAPIPublisher]) -> None:
        self._broker: RabbitBroker = broker
        self._producers: Mapping[str, AsyncAPIPublisher] = producers

    @override
    async def start(self) -> None:
        logger.info("Rabbit message broker started.")
        await self._broker.start()

    @override
    async def send_message(self, topic: str, value: BaseModel) -> None:
        if (producer := self._producers.get(topic)) is None:
            raise UnknownTopicError(f"Unknown topic {topic}, please configure in IOC")

        logger.info("Sending message %s to topic %s", value, topic)

        await producer.publish(value)

    @override
    async def stop(self) -> None:
        logger.info("Rabbit message broker stopped.")
        await self._broker.close()
