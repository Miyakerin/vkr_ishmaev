from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import typing as tp


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_DB_", extra="ignore")
    host: str = "localhost"
    password: str
    user: str
    name: str
    port_container: int
    port_host: int
    driver: str
    url: tp.Optional[str] = None
    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 20

    @model_validator(mode='after')
    def set_uri(self) -> tp.Self:
        if self.url is None:
            if self.host == "localhost":
                self.url = f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port_host}/{self.name}"
            else:
                self.url = f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port_container}/{self.name}"
        print(self.url)
        return self


class RabbitSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RABBIT_", extra="ignore")
    password: str
    user: str
    host: str
    port_host_1: int
    port_host_2: int
    port_container_1: int
    port_container_2: int
    url: tp.Optional[str] = None

    @model_validator(mode='after')
    def set_uri(self) -> tp.Self:
        if self.url is None:
            if self.host == "localhost":
                self.url = f"amqp://{self.user}:{self.password}@{self.host}:{self.port_host_2}/vhost"
            else:
                self.url = f"amqp://{self.user}:{self.password}@{self.host}:{self.port_container_2}/vhost"
        print(self.url)
        return self


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_SERVICE_", extra="ignore")
    mode: str
    port_container: int
    port_host: int


class Settings(BaseSettings):
    auth_db_settings: DBSettings = DBSettings()
    rabbit_settings: RabbitSettings = RabbitSettings()
    service_settings: ServiceSettings = ServiceSettings()



settings = Settings()
