import uuid
from typing import Annotated, Self

from pydantic import UUID4, AfterValidator, BaseModel, Field

from app.domain.entities.user import UserEntity


class UserSchemaResponse(BaseModel):
    oid: UUID4 | Annotated[str, AfterValidator(lambda x: uuid.UUID(x, version=4))] = Field(
        ..., description="UUID of the user"
    )

    name: str = Field(min_length=1, max_length=40, description="Name of the user")
    surname: str = Field(min_length=1, max_length=40, description="Surname of the user")

    @classmethod
    def from_entity(cls, entity: UserEntity) -> Self:
        return cls(
            surname=entity.surname.as_generic_type(),
            name=entity.name.as_generic_type(),
            oid=entity.oid,
        )


class CreateUserSchemaRequest(BaseModel):
    surname: str = Field(min_length=2, max_length=40, description="Surname of user")
    name: str = Field(min_length=2, max_length=40, description="Name of user")
    password: str = Field(min_length=8, max_length=50, description="Password of user")


class UpdateUserSchemaRequest(CreateUserSchemaRequest): ...
