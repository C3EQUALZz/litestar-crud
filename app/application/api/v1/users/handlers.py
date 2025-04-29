from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, delete, get, post, put
from litestar.openapi.spec import Example
from litestar.params import Body, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.application.api.v1.users.schemas import CreateUserSchemaRequest, UpdateUserSchemaRequest, UserSchemaResponse
from app.infrastructure.uow.users.base import UsersUnitOfWork
from app.logic.commands.users import CreateUserCommand, DeleteUserCommand, UpdateUserCommand
from app.logic.message_bus import MessageBus
from app.logic.views.users import UsersViews

if TYPE_CHECKING:
    from app.domain.entities.user import UserEntity


class UserController(Controller):
    path = "/user"
    tags = ["users"]  # noqa: RUF012

    @post(
        path="/",
        description="HTTP handler for creating new user",
        status_code=HTTP_201_CREATED,
    )
    @inject
    async def create_user(
        self,
        data: Annotated[CreateUserSchemaRequest, Body(title="Create User", description="Create a new user.")],
        message_bus: FromDishka[MessageBus],
    ) -> UserSchemaResponse:
        """
        Handler for creating new user
        :param data: schema for creating new user
        :param message_bus: MessageBus taken from IoC
        :return: schema that represents the user
        """
        await message_bus.handle(
            CreateUserCommand(
                surname=data.surname,
                name=data.name,
                password=data.password,
            )
        )

        return UserSchemaResponse.from_entity(message_bus.command_result)

    @get(path="/{user_id:uuid}", description="HTTP handler for getting user by his id", status_code=HTTP_200_OK)
    @inject
    async def get_user(
        self,
        user_id: Annotated[UUID, Body(description="user ID", title="user ID")],
        users_uow: FromDishka[UsersUnitOfWork],
    ) -> UserSchemaResponse:
        """
        Handler for getting user by his id.
        :param user_id: UUID of the provided user
        :param users_uow: UsersUnitOfWork taken from IoC
        :return: schema that represents the user
        """
        view: UsersViews = UsersViews(users_uow)
        user: UserEntity = await view.get_user_by_id(str(user_id))
        return UserSchemaResponse.from_entity(user)

    @delete(
        path="/{user_id:uuid}",
        description="HTTP handler for deleting user by provided id in system",
        status_code=HTTP_204_NO_CONTENT,
    )
    @inject
    async def delete_user(
        self,
        user_id: Annotated[UUID, Body(description="user ID", title="user ID")],
        message_bus: FromDishka[MessageBus],
    ) -> None:
        """
        Handler for deleting user
        :param user_id: UUID of user which client must provide
        :param message_bus: MessageBus class from IoC
        :return: None
        """
        await message_bus.handle(DeleteUserCommand(oid=str(user_id)))

        return message_bus.command_result

    @put(
        path="/{user_id:uuid}",
        description="HTTP handler for updating user by provided id in system",
        status_code=HTTP_200_OK,
    )
    @inject
    async def update_user(
        self,
        user_id: Annotated[UUID, Body(description="user ID", title="user ID")],
        data: Annotated[UpdateUserSchemaRequest, Body(title="Update User", description="Update a user.")],
        message_bus: FromDishka[MessageBus],
    ) -> UserSchemaResponse:
        """
        Handler for updating user
        :param user_id: UUID of user which client must provide
        :param data: body that user must provide
        :param message_bus: MessageBus class from IoC
        :return: schema that represents the user
        """
        await message_bus.handle(
            UpdateUserCommand(
                oid=str(user_id),
                surname=data.surname,
                name=data.name,
                password=data.password,
            )
        )

        return UserSchemaResponse.from_entity(message_bus.command_result)

    @get(path="/", description="HTTP handler for getting users with pagination", status_code=HTTP_200_OK)
    @inject
    async def get_users(
        self,
        page_number: Annotated[
            int,
            Parameter(
                default=1,
                ge=1,
                title="page number",
                description="Page number for pagination",
                examples=[Example(value=1)],
            ),
        ],
        page_size: Annotated[
            int,
            Parameter(
                default=1, ge=1, title="page size", description="Page size for pagination", examples=[Example(value=1)]
            ),
        ],
        users_uow: FromDishka[UsersUnitOfWork],
    ) -> list[UserSchemaResponse]:
        """
        Handler for getting users with pagination
        :param users_uow: UsersUnitOfWork taken from IoC
        :param page_number: number of the page
        :param page_size: size of the page
        :return: list of schemas that represents the users
        """
        view: UsersViews = UsersViews(users_uow)
        users: list[UserEntity] = await view.get_all_users(page_number=page_number, page_size=page_size)
        return [UserSchemaResponse.from_entity(user) for user in users]
