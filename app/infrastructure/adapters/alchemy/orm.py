from sqlalchemy import Column, DateTime, MetaData, Table
from sqlalchemy.orm import registry
from sqlalchemy.sql import func

from app.infrastructure.adapters.alchemy.type_decorators import (
    PasswordTypeDecorator,
    StringUUID,
    UserNameTypeDecorator,
    UserSurnameTypeDecorator,
)

metadata: MetaData = MetaData()
mapper_registry: registry = registry(metadata=metadata)

users_table: Table = Table(
    "users",
    metadata,
    Column("id", StringUUID(), primary_key=True, key="oid"),
    Column("surname", UserSurnameTypeDecorator(100)),
    Column("name", UserNameTypeDecorator(100), nullable=False),
    Column("password", PasswordTypeDecorator(100), nullable=False),
    Column("created_at", DateTime(timezone=True), default=func.now()),
    Column("updated_at", DateTime(timezone=True), default=func.now(), onupdate=func.now()),
)


def start_mappers() -> None:
    """
    Map all domain models to ORM models, for purpose of using domain models directly during work with the database,
    according to DDD.
    """
    from app.domain.entities.user import UserEntity

    mapper_registry.map_imperatively(
        class_=UserEntity,
        local_table=users_table,
        properties={
            "oid": users_table.c.oid,
        },
    )
