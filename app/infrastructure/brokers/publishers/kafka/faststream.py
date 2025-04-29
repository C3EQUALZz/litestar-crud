import logging
from collections.abc import Mapping
from typing import Final, override

from faststream.kafka import KafkaBroker
from faststream.kafka.publisher.asyncapi import AsyncAPIBatchPublisher, AsyncAPIDefaultPublisher
from pydantic import BaseModel

from app.exceptions.infrastructure import UnknownTopicError
from app.infrastructure.brokers.publishers.kafka.base import BaseKafkaMessageBrokerPublisher

logger: Final[logging.Logger] = logging.getLogger(__name__)


class FastStreamKafkaMessageBroker(BaseKafkaMessageBrokerPublisher):
    def __init__(
        self, broker: KafkaBroker, producers: Mapping[str, AsyncAPIDefaultPublisher | AsyncAPIBatchPublisher]
    ) -> None:
        self._broker: KafkaBroker = broker
        self._producers: Mapping[str, AsyncAPIDefaultPublisher | AsyncAPIBatchPublisher] = producers

    @override
    async def start(self) -> None:
        logger.info("Kafka message broker started.")
        await self._broker.start()

    @override
    async def send_message(self, topic: str, value: BaseModel) -> None:
        if (producer := self._producers.get(topic)) is None:
            raise UnknownTopicError(f"Unknown topic {topic}, please configure in IOC")

        logger.info("Sending message %s to topic %s", value, topic)

        await producer.publish(value)

    @override
    async def stop(self) -> None:
        logger.info("Kafka message broker stopped.")
        await self._broker.close()
