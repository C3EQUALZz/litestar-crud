from dataclasses import dataclass

from app.domain.entities.base import BaseEntity
from app.domain.values.user import UserName, UserSurname


@dataclass(eq=False)
class UserEntity(BaseEntity):
    name: UserName
    surname: UserSurname
    password: bytes
