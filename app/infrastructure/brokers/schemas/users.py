from pydantic import BaseModel, Field

from app.infrastructure.brokers.schemas.base import StringUUID


class UserDeleteSchema(BaseModel):
    oid: StringUUID


class UserCreateSchema(BaseModel):
    oid: StringUUID
    name: str = Field(..., description="Name of user for broker")
    surname: str = Field(..., description="Surname of user for broker")


class UserUpdateSchema(UserCreateSchema): ...
