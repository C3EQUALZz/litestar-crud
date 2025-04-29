from abc import ABC
from functools import lru_cache
from pathlib import Path

from pydantic import Field, KafkaDsn, model_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class CommonSettings(BaseSettings, ABC):
    """
    Base class for each setting. If you add new technologies, please add new class and inherit from BaseSettings.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


class DatabaseSettings(CommonSettings):
    """
    Settings for connection to database.
    Some settings are optional, because sqlite doesn't take them.
    """

    host: str | None = Field(alias="DATABASE_HOST", default=None)
    port: int | None = Field(alias="DATABASE_PORT_NETWORK", default=None)
    user: str | None = Field(alias="DATABASE_USER", default=None)
    password: str | None = Field(alias="DATABASE_PASSWORD", default=None)
    name: str = Field(alias="DATABASE_NAME")
    dialect: str = Field(alias="DATABASE_DIALECT")
    driver: str = Field(alias="DATABASE_DRIVER")

    @property
    def url(self) -> str:
        if self.dialect == "sqlite":
            return f"{self.dialect}+{self.driver}:///{self.name}"

        return f"{self.dialect}+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class SQLAlchemySettings(CommonSettings):
    """
    Check in docs alchemy settings
    """

    pool_pre_ping: bool = Field(alias="DATABASE_POOL_PRE_PING")
    pool_recycle: int = Field(alias="DATABASE_POOL_RECYCLE")
    echo: bool = Field(alias="DATABASE_ECHO")
    auto_flush: bool = Field(alias="DATABASE_AUTO_FLUSH")
    expire_on_commit: bool = Field(alias="DATABASE_EXPIRE_ON_COMMIT")


class BrokerKafkaSettings(CommonSettings):
    """
    Kafka settings for broker.
    """

    host: str = Field(alias="BROKER_HOST")
    port: int = Field(alias="BROKER_PORT_NETWORK")

    user_create_topic: str = Field(
        default="user-create-topic",
        alias="USER_CREATE_TOPIC",
    )

    user_update_topic: str = Field(
        default="user-update-topic",
        alias="USER_UPDATE_TOPIC",
    )

    user_delete_topic: str = Field(
        default="user-delete-topic",
        alias="USER_DELETE_TOPIC",
    )

    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"

    @model_validator(mode="after")
    def validate_url(self) -> "BrokerKafkaSettings":
        """Валидация формата Kafka DSN"""
        try:
            KafkaDsn(f"kafka://{self.host}:{self.port}")
            return self
        except ValueError as e:
            raise ValueError(f"Invalid Kafka URL: {self.url}") from e


class Settings(CommonSettings):
    """
    Settings class which encapsulates logic of settings from other classes.
    In application, you must use this class.
    """

    database: DatabaseSettings = DatabaseSettings()
    alchemy: SQLAlchemySettings = SQLAlchemySettings()
    broker_kafka: BrokerKafkaSettings = BrokerKafkaSettings()


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()
