import os
from pathlib import Path

from authlib.jose import JsonWebKey, RSAKey
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
        return self


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_SERVICE_", extra="ignore")
    name: str
    host: str
    mode: str
    port_container: int
    port_host: int


class MinioSetting(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_MINIO_", extra="ignore")
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


class JwtSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_SERVICE_", extra="ignore")
    private_key_filename: str
    public_key_filename: str
    __private_key: JsonWebKey = None
    __public_key: JsonWebKey = None
    __rsa_key: RSAKey = None
    __static_folder: str = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../static"))

    @property
    def private_key(self) -> RSAKey:
        if self.__private_key is None:
            self.__private_key: RSAKey = JsonWebKey.import_key(Path(self.__static_folder + "/" + self.private_key_filename).read_text(), {'kty': 'RSA'})
        return self.__private_key

    @property
    def public_key(self) -> RSAKey:
        if self.__public_key is None:
            self.__public_key: RSAKey = JsonWebKey.import_key(Path(self.__static_folder + "/" + self.public_key_filename).read_text(), {'kty': 'RSA'})
        return self.__public_key


class Settings(BaseSettings):
    auth_db_settings: DBSettings = DBSettings()
    minio_settings: MinioSetting = MinioSetting()
    service_settings: ServiceSettings = ServiceSettings()
    jwt_settings: JwtSettings = JwtSettings()
    all_db: tp.List[tp.Dict[str, tp.Union[str, int, bool]]] = [
        {
            "name": auth_db_settings.name,
            "url": auth_db_settings.url,
            "echo": auth_db_settings.echo,
            "pool_size": auth_db_settings.pool_size,
            "max_overflow": auth_db_settings.max_overflow
        }
    ]


settings = Settings()
