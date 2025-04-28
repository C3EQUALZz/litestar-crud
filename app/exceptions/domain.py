from abc import ABC
from http import HTTPStatus

from app.exceptions.base import BaseAppError


class BaseDomainError(BaseAppError, ABC):
    @property
    def status(self) -> int:
        return HTTPStatus.UNPROCESSABLE_ENTITY.value


class WrongTypeError(BaseDomainError):
    @property
    def status(self) -> int:
        return HTTPStatus.INTERNAL_SERVER_ERROR.value


class EmptyFieldError(BaseDomainError):
    @property
    def status(self) -> int:
        return HTTPStatus.UNPROCESSABLE_ENTITY.value


class CantBeNumberError(BaseDomainError):
    @property
    def status(self) -> int:
        return HTTPStatus.UNPROCESSABLE_ENTITY.value
