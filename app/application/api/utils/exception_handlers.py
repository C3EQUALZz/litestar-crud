import logging
from typing import Final

from litestar import MediaType, Request, Response

from app.exceptions.base import BaseAppError

logger: Final[logging.Logger] = logging.getLogger(__name__)


def internal_server_error_handler(request: Request, exc: Exception) -> Response:
    logger.error("Server error: %s", exc)

    return Response(
        media_type=MediaType.TEXT,
        content=f"server error: {exc}",
        status_code=500,
    )


def application_error_handler(request: Request, exc: BaseAppError) -> Response:
    logger.error("Application error: %s", exc)

    if exc.headers is None:
        return Response(
            media_type=MediaType.TEXT,
            content=exc.message,
            status_code=exc.status,
        )

    return Response(
        media_type=MediaType.TEXT,
        content=exc.message,
        status_code=exc.status,
        headers=exc.headers,
    )
