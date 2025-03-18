from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import typing as tp


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_DB_", extra="ignore")
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
        return self


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_SERVICE_", extra="ignore")
    mode: str
    port_container: int
    port_host: int


class MinioSetting(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_MINIO_", extra="ignore")
    ROOT_USER: str
    ROOT_PASSWORD: str
    PORT_HOST_1: int
    PORT_HOST_2: int
    url: tp.Optional[str] = None

    @model_validator(mode='after')
    def set_uri(self) -> tp.Self:
        if self.url is None:
            self.url = f""
        return self


class Settings(BaseSettings):
    ai_db_settings: DBSettings = DBSettings()
    minio_settings: MinioSetting = MinioSetting()
    service_settings: ServiceSettings = ServiceSettings()
    all_db: tp.List[tp.Dict[str, tp.Union[str, int, bool]]] = [
        {
            "name": ai_db_settings.name,
            "url": ai_db_settings.url,
            "echo": ai_db_settings.echo,
            "pool_size": ai_db_settings.pool_size,
            "max_overflow": ai_db_settings.max_overflow
        }
    ]


settings = Settings()
