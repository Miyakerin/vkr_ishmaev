from authlib.jose import RSAKey
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
    name: str
    host: str
    mode: str
    port_container: int
    port_host: int


class AuthServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_SERVICE_", extra="ignore")
    name: str
    host: str
    mode: str
    port_container: int
    port_host: int
    url: tp.Optional[str] = None

    @model_validator(mode='after')
    def set_uri(self) -> tp.Self:
        if self.url is None:
            if self.host == "localhost":
                self.url = f"http://{self.host}:{self.port_host}"
            else:
                self.url = f"http://{self.host}:{self.port_container}"
        return self


class MinioSetting(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_MINIO_", extra="ignore")
    name: str
    host: str
    access_key: str
    secret_key: str
    port_host_1: int
    port_container_1: int
    url: tp.Optional[str] = None

    @model_validator(mode='after')
    def set_uri(self) -> tp.Self:
        if self.url is None:
            self.url = f"http://{self.host}:{self.port_host_1}"
        else:
            self.url = f"http://{self.host}:{self.port_container_1}"
        return self


class OpenAISetting(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_OPENAI_", extra="ignore")
    auth_key: str
    completions_url: str = "https://api.openai.com/v1/chat/completions"


class GigachatSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_GIGACHAT_", extra="ignore")
    scope: str
    auth_key: str
    auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    models_list_url: str = "https://gigachat.devices.sberbank.ru/api/v1/models"
    completions_url: str = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    file_upload_url: str = "https://gigachat.devices.sberbank.ru/api/v1/files"
    access_token: tp.Optional[str] = None
    key: tp.Optional[str] = None


class DeepSeekSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_DEEPSEEK_", extra="ignore")
    auth_key: str
    completions_url: str = "https://api.deepseek.com/chat/completions"


class APISettings(BaseSettings):
    openai: OpenAISetting = OpenAISetting()
    deepseek: DeepSeekSettings = DeepSeekSettings()
    gigachat: GigachatSettings = GigachatSettings()


class Settings(BaseSettings):
    ai_db_settings: DBSettings = DBSettings()
    minio_settings: MinioSetting = MinioSetting()
    service_settings: ServiceSettings = ServiceSettings()
    auth_service_settings: AuthServiceSettings = AuthServiceSettings()
    api_settings: APISettings = APISettings()
    auth_key: tp.Optional[RSAKey] = None
    all_db: tp.List[tp.Dict[str, tp.Union[str, int, bool]]] = [
        {
            "name": ai_db_settings.name,
            "url": ai_db_settings.url,
            "echo": ai_db_settings.echo,
            "pool_size": ai_db_settings.pool_size,
            "max_overflow": ai_db_settings.max_overflow
        }
    ]
    all_s3: tp.List[tp.Dict[str, tp.Union[str, int, bool]]] = [
        {
            "name": minio_settings.name,
            "s3_uri": minio_settings.url,
            "s3_access_key": minio_settings.access_key,
            "s3_secret_key": minio_settings.secret_key
        }
    ]


settings = Settings()
