import logging
from functools import lru_cache
from typing import Final, cast

from dishka import AsyncContainer, Provider, Scope, from_context, make_async_container, provide
from faststream.kafka import KafkaBroker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.brokers.factory import EventHandlerTopicFactory
from app.infrastructure.brokers.publishers.kafka.base import BaseKafkaMessageBrokerPublisher
from app.infrastructure.brokers.publishers.kafka.faststream import FastStreamKafkaMessageBroker
from app.infrastructure.uow.users.alchemy import SQLAlchemyUsersUnitOfWork
from app.infrastructure.uow.users.base import UsersUnitOfWork
from app.logic.bootstrap import Bootstrap
from app.logic.commands.users import CreateUserCommand, DeleteUserCommand, UpdateUserCommand
from app.logic.event_buffer import EventBuffer
from app.logic.events.users import UserCreateEvent, UserDeleteEvent, UserUpdateEvent
from app.logic.handlers.users.commands import (
    CreateUserCommandHandler,
    DeleteUserCommandHandler,
    UpdateUserCommandHandler,
)
from app.logic.handlers.users.events import UserCreateEventHandler, UserDeleteEventHandler, UserUpdateEventHandler
from app.logic.message_bus import MessageBus
from app.logic.types.handlers import CommandHandlerMapping, EventHandlerMapping
from app.settings.configs.app import Settings, get_settings

logger: Final[logging.Logger] = logging.getLogger(__name__)


class HandlerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_mapping_and_command_handlers(self) -> CommandHandlerMapping:
        """
        Here you have to link commands and command handlers for future inject in Bootstrap
        """
        return cast(
            "CommandHandlerMapping",
            {
                CreateUserCommand: CreateUserCommandHandler,
                UpdateUserCommand: UpdateUserCommandHandler,
                DeleteUserCommand: DeleteUserCommandHandler,
            },
        )

    @provide(scope=Scope.APP)
    async def get_mapping_event_and_event_handlers(self) -> EventHandlerMapping:
        """
        Here you have to link events and event handlers for future inject in Bootstrap
        """
        return cast(
            "EventHandlerMapping",
            {
                UserCreateEvent: [UserCreateEventHandler],
                UserDeleteEvent: [UserDeleteEventHandler],
                UserUpdateEvent: [UserUpdateEventHandler],
            },
        )


class BrokerProvider(Provider):
    settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_mapping_events_and_topic(self, settings: Settings) -> EventHandlerTopicFactory:
        return EventHandlerTopicFactory(
            mapping={
                UserCreateEventHandler: settings.broker_kafka.user_create_topic,
                UserDeleteEventHandler: settings.broker_kafka.user_delete_topic,
                UserUpdateEventHandler: settings.broker_kafka.user_update_topic,
            }
        )

    @provide(scope=Scope.APP)
    async def get_faststream_kafka_broker(self, settings: Settings) -> KafkaBroker:
        return KafkaBroker(bootstrap_servers=str(settings.broker_kafka.url))

    @provide(scope=Scope.APP)
    async def get_producer(
        self,
        settings: Settings,
        faststream_kafka_broker: KafkaBroker,
    ) -> BaseKafkaMessageBrokerPublisher:
        return FastStreamKafkaMessageBroker(
            broker=faststream_kafka_broker,
            producers={
                settings.broker_kafka.user_create_topic: faststream_kafka_broker.publisher(
                    settings.broker_kafka.user_create_topic
                ),
                settings.broker_kafka.user_update_topic: faststream_kafka_broker.publisher(
                    settings.broker_kafka.user_update_topic
                ),
                settings.broker_kafka.user_delete_topic: faststream_kafka_broker.publisher(
                    settings.broker_kafka.user_delete_topic
                ),
            },
        )


class AppProvider(Provider):
    settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_users_uow(self, session_maker: async_sessionmaker[AsyncSession]) -> UsersUnitOfWork:
        return SQLAlchemyUsersUnitOfWork(session_factory=session_maker)

    @provide(scope=Scope.APP)
    async def get_event_buffer(self) -> EventBuffer:
        return EventBuffer()

    @provide(scope=Scope.APP)
    async def get_bootstrap(
        self,
        events: EventHandlerMapping,
        commands: CommandHandlerMapping,
        kafka_broker: BaseKafkaMessageBrokerPublisher,
        event_handler_and_topic_factory: EventHandlerTopicFactory,
        user_uow: UsersUnitOfWork,
        event_buffer: EventBuffer,
    ) -> Bootstrap:
        return Bootstrap(
            event_buffer=event_buffer,
            events_handlers_for_injection=events,
            commands_handlers_for_injection=commands,
            dependencies={
                "users_uow": user_uow,
                "kafka_broker": kafka_broker,
                "event_handler_and_topic_factory": event_handler_and_topic_factory,
            },
        )

    @provide(scope=Scope.APP)
    async def get_message_bus(self, bootstrap: Bootstrap) -> MessageBus:
        return await bootstrap.get_messagebus()


class DatabaseProvider(Provider):
    settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_engine_client(self, settings: Settings) -> AsyncEngine:
        engine: AsyncEngine = create_async_engine(
            url=settings.database.url,
            pool_pre_ping=settings.alchemy.pool_pre_ping,
            pool_recycle=settings.alchemy.pool_recycle,
            echo=settings.alchemy.echo,
        )

        logger.info("Successfully connected to database")

        return engine

    @provide(scope=Scope.APP)
    async def get_session_maker(self, engine: AsyncEngine, settings: Settings) -> async_sessionmaker[AsyncSession]:
        session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=engine,
            autoflush=settings.alchemy.auto_flush,
            expire_on_commit=settings.alchemy.expire_on_commit,
        )

        return session_maker


@lru_cache(maxsize=1)
def get_container() -> AsyncContainer:
    return make_async_container(
        HandlerProvider(),
        BrokerProvider(),
        AppProvider(),
        DatabaseProvider(),
        context={Settings: get_settings()},
    )
