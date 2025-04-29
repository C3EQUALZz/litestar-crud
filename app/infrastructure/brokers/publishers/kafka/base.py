from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.infrastructure.brokers.publishers.base import BaseMessageBrokerPublisher


class BaseKafkaMessageBrokerPublisher(BaseMessageBrokerPublisher, ABC):
    @abstractmethod
    async def send_message(self, topic: str, value: BaseModel) -> None:
        raise NotImplementedError
