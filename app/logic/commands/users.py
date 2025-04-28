from dataclasses import dataclass

from app.logic.commands.base import AbstractCommand


@dataclass(frozen=True)
class CreateUserCommand(AbstractCommand):
    surname: str
    name: str
    password: str


@dataclass(frozen=True)
class UpdateUserCommand(AbstractCommand):
    oid: str
    surname: str
    name: str
    password: str


@dataclass(frozen=True)
class DeleteUserCommand(AbstractCommand):
    oid: str
