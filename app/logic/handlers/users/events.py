from app.infrastructure.brokers.schemas.users import UserCreateSchema, UserDeleteSchema, UserUpdateSchema
from app.logic.events.users import UserCreateEvent, UserDeleteEvent, UserUpdateEvent
from app.logic.handlers.users.base import UsersEventHandler


class UserDeleteEventHandler(UsersEventHandler):
    async def __call__(self, event: UserDeleteEvent) -> None:
        topic: str = self._factory.get_topic(self.__class__)

        await self._broker.send_message(
            topic=topic,
            value=UserDeleteSchema(oid=event.user_oid),
        )


class UserCreateEventHandler(UsersEventHandler):
    async def __call__(self, event: UserCreateEvent) -> None:
        topic: str = self._factory.get_topic(self.__class__)

        await self._broker.send_message(
            topic=topic,
            value=UserCreateSchema(oid=event.oid, name=event.name, surname=event.surname),
        )


class UserUpdateEventHandler(UsersEventHandler):
    async def __call__(self, event: UserUpdateEvent) -> None:
        topic: str = self._factory.get_topic(self.__class__)

        await self._broker.send_message(
            topic=topic,
            value=UserUpdateSchema(oid=event.oid, name=event.name, surname=event.surname),
        )
