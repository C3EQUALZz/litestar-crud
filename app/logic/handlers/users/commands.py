from app.domain.entities.user import UserEntity
from app.domain.values.user import Password, UserName, UserSurname
from app.exceptions.infrastructure import UserNotFoundError
from app.infrastructure.security.hashing import hash_password
from app.infrastructure.services.users import UsersService
from app.logic.commands.users import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from app.logic.events.users import UserCreateEvent, UserDeleteEvent, UserUpdateEvent
from app.logic.handlers.users.base import UsersCommandHandler


class CreateUserCommandHandler(UsersCommandHandler[CreateUserCommand]):
    async def __call__(self, command: CreateUserCommand) -> UserEntity:
        """
        Handler for creating a new user.
        """
        async with self._uow as uow:
            user_service: UsersService = UsersService(uow=uow)

            new_user: UserEntity = UserEntity(
                name=UserName(command.name),
                surname=UserSurname(command.surname),
                password=Password(hash_password(command.password)),
            )

            added_user: UserEntity = await user_service.add(new_user)

            self._event_buffer.add(
                UserCreateEvent(
                    oid=added_user.oid,
                    name=added_user.name.as_generic_type(),
                    surname=added_user.surname.as_generic_type(),
                )
            )

            return added_user


class UpdateUserCommandHandler(UsersCommandHandler[UpdateUserCommand]):
    async def __call__(self, command: UpdateUserCommand) -> UserEntity:
        """
        Updates a user, if user with provided credentials exist, and updates event signaling that
        operation was successfully executed. In other case raises BookNotExistsException.
        :param command: command to execute which must be linked in app/logic/handlers/__init__
        :return: domain entity of the updated book
        """
        async with self._uow as uow:
            user_service: UsersService = UsersService(uow=uow)

            if not await user_service.check_existence(oid=command.oid):
                raise UserNotFoundError(command.oid)

            user: UserEntity = await user_service.get_by_id(command.oid)

            updated_user: UserEntity = UserEntity(
                oid=user.oid,
                name=UserName(command.name),
                surname=UserSurname(command.surname),
                password=Password(hash_password(command.password)),
                created_at=user.created_at,
            )

            updated_user: UserEntity = await user_service.update(updated_user)

            self._event_buffer.add(
                UserUpdateEvent(
                    oid=updated_user.oid,
                    name=updated_user.name.as_generic_type(),
                    surname=updated_user.surname.as_generic_type(),
                )
            )

            return updated_user


class DeleteUserCommandHandler(UsersCommandHandler[DeleteUserCommand]):
    async def __call__(self, command: UpdateUserCommand) -> None:
        async with self._uow as uow:
            user_service: UsersService = UsersService(uow=uow)

            if not await user_service.check_existence(oid=command.oid):
                raise UserNotFoundError(f"Couldn't find user {command.oid}")

            deleted_user: None = await user_service.delete(oid=command.oid)

            self._event_buffer.add(
                UserDeleteEvent(
                    user_oid=command.oid,
                )
            )

            return deleted_user
