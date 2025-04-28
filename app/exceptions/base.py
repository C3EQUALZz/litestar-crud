from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass(eq=False)
class BaseAppError(Exception, ABC):
    """
    Base error class from each layer must be inherited.
    For example, I have several layers according to DDD:
    - application
    - domain
    - logic
    - infrastructure
    """

    message: str

    @property
    @abstractmethod
    def status(self) -> int:
        """
        HTTP status code of exception.
        :return: number of HTTP status code. For example, 404, 500 and etc.
        """
        raise NotImplementedError

    @property
    def headers(self) -> dict[str, str] | None:
        """
        Headers for exception.
        For example, you can write here information about bearer token and etc.
        :return: dictionary of headers
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """
        :return: The error message left by the developer
        """
        return self.message
