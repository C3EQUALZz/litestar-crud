from typing import TYPE_CHECKING, Any, override

from sqlalchemy import Result, Row, RowMapping, delete, insert, select, update

from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.base import SQLAlchemyAbstractRepository
from app.infrastructure.repositories.users.base import UsersRepository

if TYPE_CHECKING:
    from collections.abc import Sequence


class SQLAlchemyUsersRepository(SQLAlchemyAbstractRepository, UsersRepository):
    @override
    async def get_by_fullname(self, surname: str, name: str) -> UserEntity | None:
        result: Result = await self._session.execute(select(UserEntity).filter_by(surname=surname, name=name))

        return result.scalar_one_or_none()

    @override
    async def add(self, model: UserEntity) -> UserEntity:
        result: Result = await self._session.execute(
            insert(UserEntity).values(**await model.to_dict(save_classes_value_objects=True)).returning(UserEntity)
        )

        return result.scalar_one()

    @override
    async def get(self, oid: str) -> UserEntity | None:
        result: Result = await self._session.execute(select(UserEntity).filter_by(oid=oid))

        return result.scalar_one_or_none()

    @override
    async def update(self, oid: str, model: UserEntity) -> UserEntity:
        result: Result = await self._session.execute(
            update(UserEntity)
            .filter_by(oid=oid)
            .values(**await model.to_dict(exclude={"oid"}, save_classes_value_objects=True))
            .returning(UserEntity)
        )

        return result.scalar_one()

    @override
    async def delete(self, oid: str) -> None:
        await self._session.execute(delete(UserEntity).filter_by(oid=oid))

    @override
    async def list(self, start: int | None = None, limit: int | None = None) -> list[UserEntity]:
        if start is None and limit is None:
            result: Result = await self._session.execute(select(UserEntity))
        else:
            result: Result = await self._session.execute(select(UserEntity).offset(start).limit(limit))

        trading_result_entities: Sequence[Row | RowMapping | Any] = result.scalars().all()

        assert isinstance(trading_result_entities, list)

        for entity in trading_result_entities:
            assert isinstance(entity, UserEntity)

        return trading_result_entities
