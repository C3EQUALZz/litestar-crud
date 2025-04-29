from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.infrastructure.brokers.publishers.base import BaseMessageBrokerPublisher


class BaseRabbitMessageBrokerPublisher(BaseMessageBrokerPublisher, ABC):
    @abstractmethod
    async def send_message(self, queue: str, exchange: str, value: BaseModel) -> None:
        raise NotImplementedError
