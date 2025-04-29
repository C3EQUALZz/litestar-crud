import uuid
from typing import override

from sqlalchemy import UUID, Dialect, LargeBinary, String, TypeDecorator

from app.domain.values.user import Password, UserName, UserSurname
from app.exceptions.infrastructure import ConvertingError


class StringUUID(TypeDecorator):
    """Кастомный тип для преобразования UUID в строку при загрузке и строки в UUID при сохранении."""

    impl = UUID(as_uuid=True)
    cache_ok = True

    @override
    def process_bind_param(self, value: str, dialect) -> uuid.UUID:
        if isinstance(value, str):
            return uuid.UUID(value)
        raise ConvertingError(f"{self.__class__.__name__}, method: process_bind_param, value: {value}")

    @override
    def process_result_value(self, value: UUID, dialect) -> str:
        if value:
            return str(value)
        raise ConvertingError(f"{self.__class__.__name__}, method: process_result_value, value: {value}")


class UserNameTypeDecorator(TypeDecorator):
    impl = String
    cache_ok = True

    @override
    def process_bind_param(self, value: UserName, dialect: Dialect) -> str:
        if value is not None:
            return value.as_generic_type()
        raise ConvertingError(f"{self.__class__.__name__}, method: process_bind_param, value: {value}")

    @override
    def process_result_value(self, value: str, dialect: Dialect) -> UserName:
        if value is not None:
            return UserName(value)
        raise ConvertingError(f"{self.__class__.__name__}, method: process_result_value, value: {value}")


class UserSurnameTypeDecorator(TypeDecorator):
    impl = String
    cache_ok = True

    @override
    def process_bind_param(self, value: UserSurname, dialect: Dialect) -> str:
        if value is not None:
            return value.as_generic_type()
        raise ConvertingError(f"{self.__class__.__name__}, method: process_bind_param, value: {value}")

    @override
    def process_result_value(self, value: str, dialect: Dialect) -> UserSurname:
        if value is not None:
            return UserSurname(value)
        raise ConvertingError(f"{self.__class__.__name__}, method: process_result_value, value: {value}")


class PasswordTypeDecorator(TypeDecorator):
    impl = LargeBinary
    cache_ok = True

    @override
    def process_bind_param(self, value: Password, dialect: Dialect) -> bytes:
        if value is not None:
            return value.as_generic_type()
        raise ConvertingError(f"{self.__class__.__name__}, method: process_bind_param, value: {value}")

    @override
    def process_result_value(self, column: bytes, dialect: Dialect) -> Password:
        if column is not None:
            return Password(column)
        raise ConvertingError(f"{self.__class__.__name__}, method: process_result_value, column: {column}")
