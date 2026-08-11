from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_level: str = "INFO"
    redact_online_url: str = "https://api.brighter.ai/"
    redact_url_default: str = "http://127.0.0.1:8787/"
    base_timeout: int = 60

    @field_validator("log_level")
    @classmethod
    def log_level_must_be_upper_case(cls, value: str) -> str:
        return value.upper()

    @field_validator("redact_online_url", "redact_url_default")
    @classmethod
    def _must_be_valid_url(cls, value: str) -> str:
        AnyUrl(value)  # raises if not a valid URL
        return value
