from abc import ABC
from typing import TYPE_CHECKING

from app.infrastructure.brokers.factory import EventHandlerTopicFactory
from app.infrastructure.brokers.publishers.kafka.base import BaseKafkaMessageBrokerPublisher
from app.infrastructure.uow.users.base import UsersUnitOfWork
from app.logic.event_buffer import EventBuffer
from app.logic.handlers.base import AbstractCommandHandler, AbstractEventHandler
from app.logic.types.handlers import CT, ET

if TYPE_CHECKING:
    from app.infrastructure.brokers.publishers.base import BaseMessageBrokerPublisher


class UsersEventHandler(AbstractEventHandler[ET], ABC):
    """
    Abstract event handler class, from which every users event handler should be inherited from.
    """

    def __init__(
        self,
        event_buffer: EventBuffer,
        users_uow: UsersUnitOfWork,
        kafka_broker: BaseKafkaMessageBrokerPublisher,
        event_handler_and_topic_factory: EventHandlerTopicFactory,
    ) -> None:
        self._event_buffer: EventBuffer = event_buffer
        self._uow: UsersUnitOfWork = users_uow
        self._broker: BaseMessageBrokerPublisher = kafka_broker
        self._factory: EventHandlerTopicFactory = event_handler_and_topic_factory


class UsersCommandHandler(AbstractCommandHandler[CT], ABC):
    """
    Abstract command handler class, from which every users command handler should be inherited from.
    """

    def __init__(self, event_buffer: EventBuffer, users_uow: UsersUnitOfWork) -> None:
        self._uow: UsersUnitOfWork = users_uow
        self._event_buffer: EventBuffer = event_buffer
