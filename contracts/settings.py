from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class CoralogixSettings(BaseSettings):
    api_url: str
    api_key: str

    model_config = SettingsConfigDict(
        env_prefix='CORALOGIX_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

class PrometheusSettings(BaseSettings):
    url: str

    model_config = SettingsConfigDict(
        env_prefix='PROMETHEUS_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

class AzureOpenAISettings(BaseSettings):
    deployment_name: str
    api_version: str
    api_base: str
    api_key: str
    temperature: float = 0.0

    model_config = SettingsConfigDict(
        env_prefix='AZURE_OPENAI_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

class Settings(BaseSettings):
    coralogix: Optional[CoralogixSettings] = None
    prometheus: Optional[PrometheusSettings] = None
    azure_openai: Optional[AzureOpenAISettings] = None
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coralogix = CoralogixSettings()
        self.prometheus = PrometheusSettings()
        self.azure_openai = AzureOpenAISettings()

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
