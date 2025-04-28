from typing import override

from app.domain.values.base import BaseValueObject
from app.exceptions.domain import CantBeNumberError, EmptyFieldError, WrongTypeError


class UserName(BaseValueObject[str]):
    value: str

    @override
    def validate(self) -> None:
        if not isinstance(self.value, str):
            raise WrongTypeError(f"You provided wrong type to value object: {self.value} please use type: str")

        if self.value.isspace() or not self.value:
            raise EmptyFieldError(f"Value {self.value} is empty, please provide info")

        if self.value.isdigit():
            raise CantBeNumberError(f"Value {self.value} is empty, please provide info")

    @override
    def as_generic_type(self) -> str:
        return str(self.value)


class UserSurname(UserName): ...
