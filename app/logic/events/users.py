from dataclasses import dataclass

from app.logic.events.base import AbstractEvent


@dataclass(frozen=True)
class UserCreateEvent(AbstractEvent):
    oid: str
    surname: str
    name: str


@dataclass(frozen=True)
class UserDeleteEvent(AbstractEvent):
    user_oid: str


@dataclass(frozen=True)
class UserUpdateEvent(AbstractEvent):
    oid: str
    surname: str
    name: str
