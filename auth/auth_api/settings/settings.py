from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, BaseSettings


class FlaskSettings(BaseModel):
    debug: bool
    testing: bool
    secret_key: str
    requests_from_ip_per_minute: int


class AlchemySettings(BaseModel):
    database_uri: str
    track_modifications: bool


class RedisSettings(BaseModel):
    host: str
    port: int


class JaegerSettings(BaseModel):
    host: str
    port: int


class JWTTokenSettings(BaseModel):
    expires: int


class JWTSettings(BaseModel):
    identity_claim: str
    secret_key: str
    access: JWTTokenSettings
    refresh: JWTTokenSettings


class OAuthProviderSettings(BaseModel):
    id: str
    secret: str
    redirect_uri: str
    authorize_url: str
    base_url: str
    scope: str


class OAuthSettings(BaseModel):
    yandex: OAuthProviderSettings
    google: OAuthProviderSettings
    vk: OAuthProviderSettings


class Settings(BaseSettings):
    flask: FlaskSettings
    alchemy: AlchemySettings
    redis: RedisSettings
    jaeger: JaegerSettings
    jwt: JWTSettings
    oauth: OAuthSettings

    class Config:
        env_nested_delimiter = "__"
        case_sensitive = False

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """Переопределение старшинства источников настроек."""
            return (
                init_settings,
                env_settings,
                yaml_settings_source,
                file_secret_settings,
            )


def yaml_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """Возвращает настройки из файла settings.yaml."""
    settings_path = Path(__file__).parent / "settings.yaml"
    with settings_path.open("r", encoding="utf-8") as f:
        yaml_settings = yaml.load(f, Loader=yaml.Loader)
    return yaml_settings
