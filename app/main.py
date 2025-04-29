from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from dishka.integrations.faststream import setup_dishka as setup_faststream_dishka
from dishka.integrations.litestar import setup_dishka as setup_litestar_dishka
from faststream import FastStream
from faststream.kafka import KafkaBroker
from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.orm import clear_mappers

from app.application.api.utils.docs import router as docs_faststream_router
from app.application.api.utils.exception_handlers import application_error_handler, internal_server_error_handler
from app.application.api.v1.users.handlers import UserController
from app.exceptions.base import BaseAppError
from app.infrastructure.adapters.alchemy.orm import start_mappers
from app.logic.container import get_container
from app.settings.logger.config import setup_logging

if TYPE_CHECKING:
    from dishka import AsyncContainer


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    container: AsyncContainer = get_container()
    kafka_faststream_broker: KafkaBroker = await container.get(KafkaBroker)

    faststream_app: FastStream = FastStream(kafka_faststream_broker)
    await faststream_app.start()

    start_mappers()

    setup_logging()
    setup_faststream_dishka(container, faststream_app, auto_inject=True)

    yield

    await faststream_app.stop()
    await container.close()
    clear_mappers()


def create_app() -> Litestar:
    container: AsyncContainer = get_container()
    litestar_app: Litestar = Litestar(
        route_handlers=[UserController, docs_faststream_router],
        lifespan=[lifespan],
        openapi_config=OpenAPIConfig(
            title="Users service API",
            description="This is the description of users service API",
            version="0.1.0",
            path="/docs",
        ),
        exception_handlers={
            HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error_handler,
            BaseAppError: application_error_handler,
        },
    )

    setup_litestar_dishka(container=container, app=litestar_app)

    return litestar_app
