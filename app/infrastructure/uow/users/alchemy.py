from typing import TYPE_CHECKING, Self

from app.infrastructure.repositories.users.alchemy import SQLAlchemyUsersRepository
from app.infrastructure.uow.base import SQLAlchemyAbstractUnitOfWork
from app.infrastructure.uow.users.base import UsersUnitOfWork

if TYPE_CHECKING:
    from app.infrastructure.repositories.users.base import UsersRepository


class SQLAlchemyUsersUnitOfWork(SQLAlchemyAbstractUnitOfWork, UsersUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.users: UsersRepository = SQLAlchemyUsersRepository(session=self._session)
        return uow
