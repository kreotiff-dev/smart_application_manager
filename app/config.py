from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Config(BaseSettings):
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_username: str
    rabbitmq_password: str
    rabbitmq_vhost: str
    rabbitmq_exchange: str
    rabbitmq_approval_routing_key: str
    card_generation_url: str
    log_level: LogLevel = LogLevel.DEBUG

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_urls()

    def validate_urls(self):
        if not self.card_generation_url.startswith(("http://", "https://")):
            raise ValueError("card_generation_url must start with http:// or https://")
