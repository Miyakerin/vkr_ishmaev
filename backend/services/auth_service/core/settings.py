from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import typing as tp

load_dotenv(".env", override=False)


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_DB_", extra="ignore")
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
            self.url = f"{self.driver}://{self.user}:{self.password}@{self.name}:{self.port_container}/{self.name}"
        return self


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_SERVICE_", extra="ignore")
    port_container: int
    port_host: int


class Settings(BaseSettings):
    auth_db_settings: DBSettings = DBSettings()
    service_settings: ServiceSettings = ServiceSettings()


settings = Settings()
